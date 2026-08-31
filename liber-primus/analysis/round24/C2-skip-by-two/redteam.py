#!/usr/bin/env python3
"""C2 RED-TEAM (R6, mandatory) -- FP ceiling under the skip_by_two (pair) decoder.

Refute-by-default. Recompute the false-positive rate of the C2 gate under the SAME
pair decoder used by the sweep, on the SAME unsolved ciphertext, with WRONG keys
(seed-3301 order-matched null): words NOT in the prior, drawn by random.Random(3301),
each seeding Py2.7 MT init_by_array([w]) -> random29 stream. Measure:

  1. how many wrong pair keys clear the Stage-A screen bar (5.0),
  2. how many of those clear the full three-clause hitfn20 gate at the pair claim bar,
  3. the wrong-key pmax distribution (max, p99) vs the claim bar 7.384.

Expected-FP over the real slice = P(wrong clears full gate) * N_screened. Pre-reg
expectation: < 1 over the whole slice. Any sweep survivor must be refuted against
this ceiling before any oracle flag stands.

    python3 redteam.py --n 4000 --out redteam.json
"""
import argparse, json, os, random, sys, time

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

PRESET = "pair"
L_SCREEN, L_HIT = 120, 240
SCREEN_BAR, SCREEN_BEAM_W = 5.0, 64
U = list(nc.unsolved())
C_SCREEN, C_HIT = U[:L_SCREEN], U[:L_HIT]


def word_stream(w, n):
    r = G.MT19937()
    r.init_by_array([w] if w else [0])
    return G.REDUCERS["random29"](r, n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--out", default=os.path.join(HERE, "redteam.json"))
    args = ap.parse_args()

    prior = json.load(open(os.path.join(LP, "analysis", "round20", "P3", "seedprior20.json")))
    prior_words = {int(e["seed"]) & 0xFFFFFFFF for e in prior["order"]}

    rng = random.Random(3301)          # order-matched wrong-key null, seed 3301
    t0 = time.time()
    pmaxes = []
    screen_pass = 0
    full_pass = 0
    passers = []
    tested = 0
    while tested < args.n:
        w = rng.randrange(0, 2 ** 32)
        if w in prior_words:
            continue
        tested += 1
        K = word_stream(w, L_SCREEN * 6 + 64)
        d = DB.beam_decode(C_SCREEN, K, sign=-1, o=0, beam_w=SCREEN_BEAM_W, **DB.PRESETS[PRESET])
        a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
        pm = float(a["pmax"])
        pmaxes.append(pm)
        if pm >= SCREEN_BAR:
            screen_pass += 1
            dec = H.HitDecode(C=C_HIT, K=word_stream(w, L_HIT * 6 + 64), o=0,
                              preset=PRESET, n_round_adjudicated=10 ** 6)
            v = H.evaluate(dec)
            if v.hit:
                full_pass += 1
                passers.append(dict(w=w, pmax=round(v.pmax, 3), rec=round(v.recovery, 4),
                                    heldout=round(v.heldout_recovery, 4)))

    pmaxes.sort()
    n = len(pmaxes)
    p99 = pmaxes[int(0.99 * n)] if n else None
    bar_ref = H.PM.panelmax_bar(PRESET, 10 ** 6, 0.01)
    p_screen = screen_pass / tested
    p_full = full_pass / tested

    out = {
        "lane": "round24/C2-skip-by-two/redteam (R6)",
        "decoder": "pair (keyskip2) -- SAME as sweep",
        "null": "seed-3301 wrong-key: random.Random(3301) 32-bit words not in prior; Py2.7 MT init_by_array; random29",
        "n_wrong_keys_tested": tested,
        "screen_bar": SCREEN_BAR,
        "wrong_clearing_screen": screen_pass, "p_clear_screen": p_screen,
        "wrong_clearing_full_gate": full_pass, "p_clear_full_gate": p_full,
        "pmax_max": round(max(pmaxes), 3) if pmaxes else None,
        "pmax_p99": round(p99, 3) if p99 is not None else None,
        "pmax_median": round(pmaxes[n // 2], 3) if n else None,
        "claim_bar_pair_1e6": round(bar_ref, 3),
        "wrong_keys_clearing_claim_bar": sum(1 for x in pmaxes if x >= bar_ref),
        "passers": passers,
        "elapsed_s": round(time.time() - t0, 1),
    }
    with open(args.out, "w") as f:
        f.write(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main()
