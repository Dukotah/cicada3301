#!/usr/bin/env python3
"""L3 SWEEP — Py2.7 init_by_array word space across the 3 uncovered reducers + amd64 2-word map,
prior-ordered, two-stage. Reuses the S-G3 sweep pattern verbatim; the only change is that the
reducer and the key-word map are per-config, and we loop the 4 configs S-G3 never covered.

For each config (reducer, map):
  Stage A (cheap, every screened word): keyskip1 beam (exact preset, bw64) on the first L=120
    runes of the canonical unsolved ciphertext -> pmax. pmax >= SCREEN_BAR promotes.
  Stage B (survivors only): full L=240 adjudication + hitfn20.is_hit -> SWEEPROW/3 row.
Any is_hit==True is a HIT by the round's own definition.

Seed order (P3b prior-weighted, doctrine R4): 433 prior words -> top-64 +-512 neigh -> dense-from-0.
Time-boxed per config. Reports per config: exact words screened, fraction of 2^32, survivors,
hits, words/sec, extrapolated full-2^32 core-days.

    python3 sweep.py --seconds-per-config 240 --procs 6
"""
import argparse, json, os, sys, time
from multiprocessing import Process, Queue

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
_PATHS = [os.path.abspath(os.path.join(HERE, p)) for p in
          ("../../round19/I1", "../../round19/I2", "../../round19/I3", "../../round20/P3",
           "../../round19/G3", "../../campaign18_skip", "../../../src", "../../round11",
           "../../round20/HITFN")]
for ap in _PATHS:
    if ap not in sys.path:
        sys.path.insert(0, ap)

L_SCREEN = 120
L_HIT = 240
SCREEN_BAR = 5.0            # frozen (PREREG): << 7.634 claim bar; plant clears ~28, wrong <=3.2
SCREEN_BEAM_W = 64
NEIGH = 512
TOPN = 64

# config-id -> (reducer mode, "i386"|"amd64"). i386 -> init_by_array([w]); amd64 -> [lo, hi].
CONFIGS = [
    ("grb5_mod_i386",  "grb5_mod",  "i386"),
    ("grb5_rej_i386",  "grb5_rej",  "i386"),
    ("shuffle29_i386", "shuffle29", "i386"),
    ("random29_amd64", "random29",  "amd64"),
]

# module-level state set per worker per config
G = DB = AD = H = None
C_SCREEN = C_HIT = None
PMbar = None
CUR_MODE = None
CUR_MAP = None


def _worker_import():
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


def _keywords(w):
    if CUR_MAP == "amd64":
        # amd64 str-hash is a 64-bit long -> up to 2 key words. Fold w into a full 64-bit long
        # deterministically so the 2-word init path is genuinely exercised across the sweep.
        n64 = (w * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        return [n64 & 0xFFFFFFFF, (n64 >> 32) & 0xFFFFFFFF]
    return [w] if w else [0]


def word_stream(w, n=L_HIT * 6 + 64):
    r = G.MT19937()
    r.init_by_array(_keywords(w))
    return G.REDUCERS[CUR_MODE](r, n)


def stage_a(w):
    K = word_stream(w, n=L_SCREEN * 6 + 64)
    d = DB.beam_decode(C_SCREEN, K, sign=-1, o=0, beam_w=SCREEN_BEAM_W, **DB.PRESETS["exact"])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return float(a["pmax"])


def stage_b(w):
    K = word_stream(w, n=L_HIT * 6 + 64)
    dec = H.HitDecode(C=C_HIT, K=K, o=0, preset="exact", n_round_adjudicated=10 ** 6)
    v = H.evaluate(dec)
    return dict(w=w, hit=v.hit, pmax=round(v.pmax, 3), bar=round(v.bar, 3),
                recovery=round(v.recovery, 4), heldout=round(v.heldout_recovery, 4),
                preg=v.preg_name, score=round(v.score, 3), clears=v.clears_null)


def worker(wid, mode, mapname, chunks_q, res_q):
    global CUR_MODE, CUR_MAP
    CUR_MODE, CUR_MAP = mode, mapname
    _worker_import()
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


def build_word_order():
    prior = json.load(open(os.path.join(HERE, "..", "..", "round20", "P3", "seedprior20.json")))
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


def run_config(cfg_id, mode, mapname, seconds, procs, chunk, dense_n, jsonl_fh):
    t0 = time.time()
    prior_order, seen = build_word_order()
    n_prior = len(prior_order)

    chunks_q = Queue(maxsize=procs * 4)
    res_q = Queue()
    ps = [Process(target=worker, args=(i, mode, mapname, chunks_q, res_q)) for i in range(procs)]
    for p in ps:
        p.start()

    def all_words():
        for w in prior_order:
            yield w
        for w in dense_gen(seen, 0, dense_n):
            yield w

    fed = 0
    for ch in chunker(all_words(), chunk):
        if time.time() - t0 > seconds:
            break
        chunks_q.put(ch)
        fed += len(ch)
    for _ in ps:
        chunks_q.put(None)

    results = [res_q.get() for _ in ps]
    for p in ps:
        p.join()

    screened = sum(r["screened"] for r in results)
    survivors = [s for r in results for s in r["survivors"]]
    hits = [h for r in results for h in r["hits"]]
    dt = time.time() - t0

    frac = screened / float(2 ** 32)
    rate = screened / dt if dt > 0 else 0
    full_cost_core_days = (2 ** 32) / (rate * procs) / 86400 if rate > 0 else None

    for s in survivors:
        jsonl_fh.write(json.dumps(dict(config=cfg_id, **s)) + "\n")

    return {
        "config": cfg_id, "reducer": mode, "map": mapname,
        "words_screened": screened,
        "fraction_of_2pow32": frac,
        "fraction_pct": round(100 * frac, 6),
        "survivors_stage_b": len(survivors),
        "hits": len(hits),
        "hit_rows": hits[:20],
        "top_survivors_by_pmax": sorted(survivors, key=lambda s: -s["pmax"])[:10],
        "seconds": round(dt, 1),
        "words_per_sec_total": round(rate, 1),
        "procs": procs,
        "extrapolated_full_2pow32_core_days": round(full_cost_core_days, 1) if full_cost_core_days else None,
        "prior_words_all_screened": screened >= n_prior,
        "n_prior_words": n_prior,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds-per-config", type=int, default=240)
    ap.add_argument("--procs", type=int, default=6)
    ap.add_argument("--chunk", type=int, default=2000)
    ap.add_argument("--dense-n", type=int, default=200_000_000)
    ap.add_argument("--jsonl", default=os.path.join(HERE, "reducers_sweep.jsonl"))
    a = ap.parse_args()

    bar = None
    header = {
        "v": "SWEEPROW/3", "lane": "round21/L3-py27-reducers-plus-64bit-map",
        "generator": "Py2.7 init_by_array(words) reducers grb5_mod/grb5_rej/shuffle29 + amd64 2-word random29 map",
        "decoder": "I1 driftbeam keyskip1 (exact) Stage-A screen bw64 L120 + full L240 gate",
        "hit_fn": "round20/HITFN is_hit (pmax>=7.634 AND recovery>=0.90 AND heldout>=0.90)",
        "screen_bar_pmax": SCREEN_BAR, "claim_bar_pmax": 7.6342,
        "seed_order": f"P3b prior 433 + top{TOPN}+-{NEIGH} neigh then dense from 0",
        "configs": [c[0] for c in CONFIGS],
        "note": "S-G3 (round20) covered only random29/i386-1word; this lane covers the 3 other reducers + amd64 2-word map.",
    }
    jf = open(a.jsonl, "w")
    jf.write(json.dumps(header) + "\n")

    per_config = []
    for cfg_id, mode, mapname in CONFIGS:
        r = run_config(cfg_id, mode, mapname, a.seconds_per_config, a.procs,
                       a.chunk, a.dense_n, jf)
        per_config.append(r)
        print(json.dumps({k: r[k] for k in ("config", "words_screened", "fraction_pct",
              "survivors_stage_b", "hits", "words_per_sec_total",
              "extrapolated_full_2pow32_core_days")}, default=float))
    jf.close()

    total_screened = sum(r["words_screened"] for r in per_config)
    total_hits = sum(r["hits"] for r in per_config)
    out = {"header": header, "per_config": per_config,
           "total_words_screened": total_screened, "total_hits": total_hits,
           "any_hit": total_hits > 0}
    json.dump(out, open(os.path.join(HERE, "out_reducers.json"), "w"), indent=1, default=float)
    print("\nTOTAL screened=%d hits=%d" % (total_screened, total_hits))


if __name__ == "__main__":
    main()
