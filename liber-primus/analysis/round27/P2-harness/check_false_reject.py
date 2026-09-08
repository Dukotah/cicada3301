#!/usr/bin/env python3
"""Check 3 -- THE broken-magnet guard (false-reject audit against the Python reference).

Samples N (default 100,000) uniform-random seeds (frozen RNG seed 27002 => reproducible),
scores every one with the PYTHON reference pipeline (cached to py_scores.jsonl -- this
half runs without the binary), then scores the same seeds with the C engine and requires:

  G1 (hard gate)   every seed with python pmax >= HARD_GATE (claim_bar - 1.5 =
                   5.883520294328688) is C-flagged (C pmax >= 5.0). false-reject rate
                   MUST be 0. (Expected count above 5.8835 in 100k nulls is ~0.3, so:)
  G2 (cand parity) every seed with python pmax >= CAND_BAR (5.0) is C-flagged too --
                   ~7 expected in 100k, this is where the gate gets real teeth.
  G3 (top-100)     the top-100 python-scored seeds all appear in C output with
                   |pmax diff| <= 1e-9.
  G4 (global)      max |pmax diff| over all N seeds <= 1e-9 (reported either way).

Exit: 0 PASS, 1 FAIL, 2 BLOCKED-ON-BINARY (python cache is still built/verified).
"""
import argparse
import json
import os
import random
import sys

import engine
import pyref

HERE = os.path.dirname(os.path.abspath(__file__))
ABS_TOL = 1e-9
SAMPLE_RNG_SEED = 27002


def sample_seeds(n):
    rng = random.Random(SAMPLE_RNG_SEED)
    return [rng.randrange(0, 2 ** 32) for _ in range(n)]


def load_cache(path, seeds):
    if not os.path.exists(path):
        return None
    rows = {}
    with open(path) as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                o = json.loads(ln)
                rows[int(o["seed"])] = float(o["pmax"])
    if [s for s in seeds if s not in rows]:
        return None  # incomplete/mismatched cache -> rebuild
    return [(s, rows[s]) for s in seeds]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100_000)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--cache", default=os.path.join(HERE, "py_scores.jsonl"))
    args = ap.parse_args()

    seeds = sample_seeds(args.n)
    print("check_false_reject: %d seeds (sample RNG seed %d)" % (args.n, SAMPLE_RNG_SEED))

    py = load_cache(args.cache, seeds)
    if py is None:
        print("scoring with the PYTHON reference (%d workers)..." % args.workers)
        py = pyref.score_many(seeds, workers=args.workers)
        tmp = args.cache + ".tmp"
        with open(tmp, "w") as f:
            for s, p in py:
                f.write(json.dumps({"seed": s, "pmax": repr(p)}) + "\n")
        os.replace(tmp, args.cache)
        print("python cache written: %s" % args.cache)
    else:
        print("python cache loaded: %s" % args.cache)

    pmap = dict(py)
    above_hard = [s for s, p in py if p >= pyref.HARD_GATE]
    above_cand = [s for s, p in py if p >= pyref.CAND_BAR]
    top100 = sorted(py, key=lambda t: -t[1])[:100]
    print("python side: max pmax %.6f @ seed %d | >=HARD_GATE(%.4f): %d | >=CAND_BAR(5.0): %d"
          % (top100[0][1], top100[0][0], pyref.HARD_GATE, len(above_hard), len(above_cand)))

    try:
        rows = engine.score_seeds(seeds, full=False, timeout=7200)
    except engine.Blocked as e:
        engine.blocked_exit("%s -- python cache is built and sane; C comparison awaits "
                            "the binary" % e)

    cmap = {int(r["seed"]): float(r["pmax"]) for r in rows}
    fails = []

    # G1 + G2: no python-flaggable seed may be missed by the C screen
    fr = 0
    for s in above_cand:  # superset of above_hard
        cp = cmap.get(s)
        if cp is None or cp < pyref.CAND_BAR:
            fr += 1
            hard = " [ABOVE HARD GATE]" if s in set(above_hard) else ""
            fails.append("false-reject seed %d: py %.6f but C %r%s" % (s, pmap[s], cp, hard))
    n_flaggable = max(len(above_cand), 1)
    print("measured false-reject rate: %d/%d = %.6f (MUST be 0)"
          % (fr, len(above_cand), fr / n_flaggable))

    # G3: top-100 value match
    worst_top = 0.0
    for s, p in top100:
        d = abs(cmap.get(s, -1e18) - p)
        worst_top = max(worst_top, d)
        if d > ABS_TOL:
            fails.append("top-100 seed %d: py %r vs C %r (|d|=%.3g)" % (s, p, cmap.get(s), d))
    print("top-100 max |pmax diff|: %.3g (tol %.0e)" % (worst_top, ABS_TOL))

    # G4: global agreement
    worst = max(abs(cmap[s] - p) for s, p in py)
    print("global  max |pmax diff| over %d seeds: %.3g" % (args.n, worst))
    if worst > ABS_TOL:
        fails.append("global max |pmax diff| %.3g > %.0e" % (worst, ABS_TOL))

    if fails:
        for m in fails[:20]:
            print("  FAIL:", m)
        print("FAIL: %d violations -- the C screen can lose a true seed. DO NOT LAUNCH."
              % len(fails))
        return 1
    print("PASS: false-reject rate 0; top-100 and global scores match within %.0e" % ABS_TOL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
