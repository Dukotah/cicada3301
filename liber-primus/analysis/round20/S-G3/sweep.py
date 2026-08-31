#!/usr/bin/env python3
"""S-G3 SWEEP — Python 2.7 `init_by_array([w])` word space, prior-ordered, two-stage.

Stage A (cheap, every screened word): keyskip1 beam (exact preset, reduced width) on the first
L=120 runes of the canonical unsolved ciphertext -> pmax. Words with pmax >= SCREEN_BAR promote.
Stage B (survivors only): full L=240 adjudication + hitfn20.is_hit (recovery + held-out gate) ->
SWEEPROW/3 rows. Any is_hit==True is a HIT by the round's own definition.

Seed order (P3b prior-weighted, doctrine R4):
  block 0: the 433 prior words (unix seconds) themselves
  block 1: +/-NEIGH neighborhoods of the top TOPN prior words
  block 2: a contiguous dense baseline from w=0 (stated fraction), filling the time-box

Time-boxed. Reports exact words screened, fraction of 2**32, survivors, hits, extrapolated cost.

    python3 sweep.py --seconds 2100 --procs 6 --out sweep.jsonl
"""
import argparse, json, os, sys, time
from multiprocessing import Process, Queue

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
_PATHS = [os.path.abspath(os.path.join(HERE, p)) for p in
          ("../../round19/I1", "../../round19/I2", "../../round19/I3", "../../round20/P3",
           "../../round19/G3", "../../campaign18_skip", "../../../src", "../../round11",
           "../HITFN")]
for ap in _PATHS:
    if ap not in sys.path:
        sys.path.insert(0, ap)

L_SCREEN = 120
L_HIT = 240
SCREEN_BAR = 5.0            # frozen: << the 7.634 claim bar; plant clears at ~28, wrong <=4.2
SCREEN_BEAM_W = 64
NEIGH = 512
TOPN = 64
MODE = "random29"          # = randrange/randint/choice in Py2.7; the idiomatic reducer


def _worker_setup():
    global G, DB, AD, H, C_SCREEN, C_HIT, PMbar
    import gen_py27 as _G
    import driftbeam as _DB
    import adjudicate as _AD
    import hitfn20 as _H
    import lib_numchannel as nc
    G, DB, AD, H = _G, _DB, _AD, _H
    u = nc.unsolved()
    C_SCREEN = list(u[:L_SCREEN])
    C_HIT = list(u[:L_HIT])
    PMbar = H.PM.panelmax_bar("exact", 10 ** 6, 0.01)


def word_stream(w, mode=MODE, n=L_HIT * 6 + 64):
    r = G.MT19937()
    r.init_by_array([w] if w else [0])
    return G.REDUCERS[mode](r, n)


def stage_a(w):
    """Cheap screen: reduced-beam keyskip1 pmax on L=120. Returns pmax."""
    K = word_stream(w, n=L_SCREEN * 6 + 64)
    d = DB.beam_decode(C_SCREEN, K, sign=-1, o=0, beam_w=SCREEN_BEAM_W, **DB.PRESETS["exact"])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return float(a["pmax"])


def stage_b(w):
    """Full gate on a survivor. Returns (is_hit, pmax, recovery, heldout, preg, score)."""
    K = word_stream(w, n=L_HIT * 6 + 64)
    dec = H.HitDecode(C=C_HIT, K=K, o=0, preset="exact", n_round_adjudicated=10 ** 6)
    v = H.evaluate(dec)
    return dict(w=w, hit=v.hit, pmax=round(v.pmax, 3), bar=round(v.bar, 3),
                recovery=round(v.recovery, 4), heldout=round(v.heldout_recovery, 4),
                preg=v.preg_name, score=round(v.score, 3), clears=v.clears_null)


def worker(wid, chunks_q, res_q):
    _worker_setup()
    screened = 0
    survivors = []
    hits = []
    while True:
        chunk = chunks_q.get()
        if chunk is None:
            break
        for w in chunk:
            pm = stage_a(w)
            screened += 1
            if pm >= SCREEN_BAR:
                b = stage_b(w)
                survivors.append(b)
                if b["hit"]:
                    hits.append(b)
    res_q.put({"wid": wid, "screened": screened, "survivors": survivors, "hits": hits})


def build_word_order(dense_start=0, dense_n=None):
    """P3b-prior-ordered word list: prior words, then neighborhoods, then dense baseline."""
    prior = json.load(open(os.path.join(HERE, "..", "P3", "seedprior20.json")))
    seen = set()
    order = []

    def add(w):
        w &= 0xFFFFFFFF
        if w not in seen:
            seen.add(w)
            order.append(w)

    for e in prior["order"]:
        add(int(e["seed"]))
    for e in prior["order"][:TOPN]:
        s = int(e["seed"])
        for d in range(-NEIGH, NEIGH + 1):
            add(s + d)
    # dense baseline block appended lazily by the caller via a generator (not materialized here)
    return order, seen


def dense_gen(seen, start, count):
    w = start
    emitted = 0
    while emitted < count:
        if (w & 0xFFFFFFFF) not in seen:
            yield w & 0xFFFFFFFF
            emitted += 1
        w += 1


def chunker(iterable, size):
    buf = []
    for x in iterable:
        buf.append(x)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=2100)
    ap.add_argument("--procs", type=int, default=6)
    ap.add_argument("--chunk", type=int, default=2000)
    ap.add_argument("--dense-start", type=int, default=0)
    ap.add_argument("--dense-n", type=int, default=200_000_000)  # cap; time-box stops earlier
    ap.add_argument("--out", default=os.path.join(HERE, "sweep.jsonl"))
    a = ap.parse_args()

    t0 = time.time()
    prior_order, seen = build_word_order()
    n_prior = len(prior_order)

    chunks_q = Queue(maxsize=a.procs * 4)
    res_q = Queue()
    procs = [Process(target=worker, args=(i, chunks_q, res_q)) for i in range(a.procs)]
    for p in procs:
        p.start()

    # feed: prior order first, then dense baseline, until time-box.
    def all_words():
        for w in prior_order:
            yield w
        for w in dense_gen(seen, a.dense_start, a.dense_n):
            yield w

    fed = 0
    stop = False
    for ch in chunker(all_words(), a.chunk):
        if time.time() - t0 > a.seconds:
            stop = True
            break
        chunks_q.put(ch)
        fed += len(ch)
    # signal end
    for _ in procs:
        chunks_q.put(None)

    results = [res_q.get() for _ in procs]
    for p in procs:
        p.join()

    screened = sum(r["screened"] for r in results)
    survivors = [s for r in results for s in r["survivors"]]
    hits = [h for r in results for h in r["hits"]]
    dt = time.time() - t0

    # coverage + extrapolation
    frac = screened / float(2 ** 32)
    rate = screened / dt if dt > 0 else 0
    full_cost_core_days = (2 ** 32) / (rate * a.procs) / 86400 if rate > 0 else None

    header = {
        "v": "SWEEPROW/3", "lane": "round20/S-G3",
        "generator": "Py2.7 init_by_array([w]) random29 (32-bit string-seed word)",
        "decoder": "I1 driftbeam keyskip1 (exact) Stage-A screen bw64 L120 + full L240 gate",
        "hit_fn": "round20/HITFN is_hit (pmax>=7.634 AND recovery>=0.90 AND heldout>=0.90)",
        "screen_bar_pmax": SCREEN_BAR, "claim_bar_pmax": round(hits and hits[0].get("bar") or 7.634, 3),
        "seed_order": f"P3b prior {n_prior} words (433 prior + top{TOPN}+-{NEIGH} neigh) then dense from {a.dense_start}",
    }
    summary = {
        "words_screened": screened,
        "fraction_of_2pow32": frac,
        "fraction_pct": round(100 * frac, 5),
        "survivors_stage_b": len(survivors),
        "hits": len(hits),
        "hit_rows": hits[:20],
        "top_survivors_by_pmax": sorted(survivors, key=lambda s: -s["pmax"])[:15],
        "seconds": round(dt, 1),
        "words_per_sec_total": round(rate, 1),
        "procs": a.procs,
        "extrapolated_full_2pow32_core_days": round(full_cost_core_days, 1) if full_cost_core_days else None,
        "prior_words_all_screened": screened >= n_prior,
        "n_prior_words": n_prior,
    }
    with open(a.out, "w") as f:
        f.write(json.dumps(header) + "\n")
        for s in survivors:
            f.write(json.dumps(s) + "\n")
    json.dump({"header": header, "summary": summary},
              open(os.path.join(HERE, "out_sweep.json"), "w"), indent=1, default=float)
    print(json.dumps(summary, indent=1, default=float))


if __name__ == "__main__":
    main()
