"""B6 run 5 — adjudicate the single cell that tripped the pre-registered gate.

run_lang.py's page-scale sweep produced exactly one PASS: EN|L4 (English trigram LM,
periodic key of length 4), best -1.5876 on page 49, z=+8.16 against a 10-replicate
shuffled null.  Page 49 is the SHORTEST page in the corpus (66 runes = 16.5 runes per
key slot), so the suspicion is search noise / extreme-value overfitting rather than
signal: with only 3 random restarts per page, real and null are not sampling the same
depth of the optimisation landscape.

This script re-runs the contested cells with a 20x larger and IDENTICAL restart budget
for real and null, so the comparison is between optima rather than between lucky starts.
It also adds a DOUBLET-MATCHED null (soft anti-repeat, p_keep tuned to the observed
0.66% doublet rate) so that the one known non-random property of LP2 is charged to the
null instead of showing up as a hit.
"""
import json
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detectors as D
import run_lang as RL

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(90210)
CELLS = [("EN", 4), ("DE", 2), ("DE", 6), ("LA", 3)]
RESTARTS = 60
NREP = 12


def doublet_suppressed(n, rng, pkeep=0.18):
    x = np.empty(n, dtype=np.int64)
    x[0] = rng.integers(D.N)
    for i in range(1, n):
        v = int(rng.integers(D.N))
        while v == x[i - 1] and rng.random() > pkeep:
            v = int(rng.integers(D.N))
        x[i] = v
    return x


def best_over_pages(lm, pgs, L):
    bs, bp, bk = -1e9, None, None
    for p, c in pgs:
        s, k = RL.hill_climb(lm, c, L, restarts=RESTARTS, sweeps=5)
        if s > bs:
            bs, bp, bk = s, p, k
    return bs, bp, bk


def main():
    pages, stream = D.load_unsolved()
    lms, _ = RL.build_lms()
    out = {}
    t0 = time.time()
    for lk, L in CELLS:
        lm = lms[lk]
        real, rp, rk = best_over_pages(lm, pages, L)
        sh, ds = [], []
        for r in range(NREP):
            sh.append(best_over_pages(lm, [(p, RNG.permutation(c))
                                           for p, c in pages], L)[0])
            ds.append(best_over_pages(lm, [(p, doublet_suppressed(len(c), RNG))
                                           for p, c in pages], L)[0])
        sh, ds = np.array(sh), np.array(ds)
        out["%s|L%d" % (lk, L)] = {
            "real": real, "page": rp, "key": [int(v) for v in rk],
            "restarts": RESTARTS,
            "shuffle_null": {"mean": float(sh.mean()), "sd": float(sh.std(ddof=1)),
                             "max": float(sh.max()),
                             "z": float((real - sh.mean()) / sh.std(ddof=1))},
            "doublet_matched_null": {
                "mean": float(ds.mean()), "sd": float(ds.std(ddof=1)),
                "max": float(ds.max()),
                "z": float((real - ds.mean()) / ds.std(ddof=1))},
        }
        v = out["%s|L%d" % (lk, L)]
        print("%s|L%d real=%.4f p%d  shuffle z=%+.2f (max %.4f)  "
              "doublet-matched z=%+.2f (max %.4f)  [%.0fs]" %
              (lk, L, real, rp, v["shuffle_null"]["z"], v["shuffle_null"]["max"],
               v["doublet_matched_null"]["z"], v["doublet_matched_null"]["max"],
               time.time() - t0), flush=True)
    json.dump(out, open(os.path.join(HERE, "verify_pass.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
