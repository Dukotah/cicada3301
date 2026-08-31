#!/usr/bin/env python3
"""C2 SWEEP -- the top-prior Py2.7-MT slice, re-decoded under the skip_by_two
(pair / keyskip2) decoder the beam cannot represent.

One-for-one with round20/S-G3/sweep.py EXCEPT the driftbeam preset is "pair"
(keyskip2, exact for enc_skip_by_two) instead of "exact" (keyskip1). Everything
frozen in PREREG.md.

Two-stage:
  Stage A  cheap pair screen (beam_w=64, L=120) -> pmax; promote pmax >= SCREEN_BAR.
  Stage B  full hitfn20.evaluate at the pair preset on survivors (recovery + held-out).

Word order (frozen): block0 the 433 prior words; block1 +/-512 nbhd of top 64;
block2 dense from w=0 filling the time-box.

    python3 sweep.py --seconds 1200 --out sweep.jsonl
"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis/round20/S-G3", "analysis/round19/I1", "analysis/round19/I2",
          "analysis/round20/P3", "analysis/round11", "analysis/campaign18_skip",
          "src", "analysis/round20/HITFN", "analysis/round19/G3"):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

import lib_numchannel as nc          # noqa
import gen_py27 as G                 # noqa
import driftbeam as DB               # noqa
import adjudicate as AD              # noqa
import hitfn20 as H                  # noqa

PRESET = "pair"                       # <-- THE ONLY DIFFERENCE vs S-G3
L_SCREEN = 120
L_HIT = 240
SCREEN_BAR = 5.0                      # frozen (= S-G3): << the 7.384 pair claim bar
SCREEN_BEAM_W = 64
NEIGH = 512
TOPN = 64
MODE = "random29"

U = list(nc.unsolved())
C_SCREEN = U[:L_SCREEN]
C_HIT = U[:L_HIT]


def word_stream(w, n):
    r = G.MT19937()
    r.init_by_array([w] if w else [0])
    return G.REDUCERS[MODE](r, n)


def stage_a(w):
    K = word_stream(w, L_SCREEN * 6 + 64)
    d = DB.beam_decode(C_SCREEN, K, sign=-1, o=0, beam_w=SCREEN_BEAM_W, **DB.PRESETS[PRESET])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return float(a["pmax"])


def stage_b(w, n_adj):
    K = word_stream(w, L_HIT * 6 + 64)
    dec = H.HitDecode(C=C_HIT, K=K, o=0, preset=PRESET, n_round_adjudicated=n_adj)
    v = H.evaluate(dec)
    return dict(w=w, hit=v.hit, pmax=round(v.pmax, 3), bar=round(v.bar, 3),
                recovery=round(v.recovery, 4), heldout=round(v.heldout_recovery, 4),
                preg=v.preg_name, score=round(v.score, 3), clears=v.clears_null,
                reason=v.reason)


def build_word_order():
    prior = json.load(open(os.path.join(LP, "analysis", "round20", "P3", "seedprior20.json")))
    seen, order = set(), []

    def add(w):
        w &= 0xFFFFFFFF
        if w not in seen:
            seen.add(w)
            order.append(w)

    for e in prior["order"]:
        add(int(e["seed"]))
    n_block0 = len(order)
    for e in prior["order"][:TOPN]:
        s = int(e["seed"])
        for dd in range(-NEIGH, NEIGH + 1):
            add(s + dd)
    n_block01 = len(order)
    return order, seen, n_block0, n_block01


def dense_gen(seen, count):
    w, made = 0, 0
    while made < count:
        if w not in seen:
            yield w
            made += 1
        w += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=1200)
    ap.add_argument("--dense", type=int, default=200000,
                    help="dense baseline words to append after prior+neighbourhood")
    ap.add_argument("--out", default=os.path.join(HERE, "sweep.jsonl"))
    args = ap.parse_args()

    t0 = time.time()
    order, seen, n_b0, n_b01 = build_word_order()
    survivors, hits = [], []
    screened = 0
    max_pmax = -1e9
    best = None

    def process(w):
        nonlocal screened, max_pmax, best
        pm = stage_a(w)
        screened += 1
        if pm > max_pmax:
            max_pmax = pm
            best = (w, pm)
        if pm >= SCREEN_BAR:
            # n_round_adjudicated is filled at the end with the true screened count;
            # use a provisional 1e6 (the reference bar) for the live decision, then
            # re-adjudicate the bar post-hoc against n_stage_b.
            b = stage_b(w, 10 ** 6)
            survivors.append(b)
            if b["hit"]:
                hits.append(b)

    # blocks 0 + 1 (always fully swept -- the actual top-prior slice)
    for w in order:
        if time.time() - t0 > args.seconds:
            break
        process(w)
    prior_and_nbhd_done = screened >= len(order)

    # block 2 dense baseline, time-boxed
    if prior_and_nbhd_done:
        for w in dense_gen(seen, args.dense):
            if time.time() - t0 > args.seconds:
                break
            process(w)

    elapsed = time.time() - t0
    n_stage_b = max(1, len(survivors))
    # re-express the family-wise bar at the true Stage-B count
    bar_at_nb = H.PM.panelmax_bar(PRESET, n_stage_b, 0.01)
    bar_ref = H.PM.panelmax_bar(PRESET, 10 ** 6, 0.01)
    # re-adjudicate each survivor's hit against the true-N bar
    for s in survivors:
        s["bar_at_n_stageb"] = round(bar_at_nb, 3)
        s["clears_at_n_stageb"] = bool(s["pmax"] >= bar_at_nb)

    out = {
        "lane": "round24/C2-skip-by-two/sweep",
        "decoder": "driftbeam mode=keyskip2 (preset 'pair') -- skip_by_two-exact; the relation the beam cannot represent (L7-B)",
        "generator": "Py2.7 MT19937 init_by_array([w]); reducer random29",
        "ciphertext": "lib_numchannel.unsolved(); screen L=120, gate L=240; sign=-1 o=0",
        "screen_bar": SCREEN_BAR, "screen_beam_w": SCREEN_BEAM_W,
        "prior_words": n_b0, "prior_plus_neigh": n_b01,
        "words_screened": screened,
        "fraction_of_2pow32": screened / 2 ** 32,
        "prior_and_nbhd_fully_swept": prior_and_nbhd_done,
        "survivors_screen": len(survivors),
        "hits_provisional_bar1e6": len(hits),
        "hits_at_n_stageb_bar": sum(1 for s in survivors if s.get("clears_at_n_stageb") and s["hit"]),
        "panelmax_bar_ref_1e6": round(bar_ref, 3),
        "panelmax_bar_at_n_stageb": round(bar_at_nb, 3),
        "n_stage_b": n_stage_b,
        "max_pmax_over_slice": round(max_pmax, 3),
        "best_word_by_pmax": best,
        "power_note": "pair decoder recovery on skip_by_two plant = 100% (control.json); beam = 25.8% (L7-B)",
        "elapsed_s": round(elapsed, 1),
        "survivors": survivors,
        "hits": hits,
    }
    with open(args.out, "w") as f:
        f.write(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("survivors", "hits")}, indent=1))
    print(f"\nwrote {args.out}")
    return out


if __name__ == "__main__":
    main()
