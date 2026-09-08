#!/usr/bin/env python3
"""Check 4 -- R25 best-word reproduction. Seed 2149309687 must reproduce
pmax 6.825835461843649 ("6.826", the R25 global best) in BOTH engines.

Python half runs without the binary. Exit: 0 PASS, 1 FAIL, 2 BLOCKED-ON-BINARY.
"""
import sys

import engine
import pyref

SEED = 2149309687
WANT = 6.825835461843649       # vectors.json seed_vectors + R25 RESULTS-parked.md
ABS_TOL = 1e-9


def main():
    ref = pyref.stage_a_full(SEED)
    print("python: seed %d pmax %r (want %r)" % (SEED, ref["pmax"], WANT))
    if abs(ref["pmax"] - WANT) > 1e-12 or round(ref["pmax"], 3) != 6.826:
        print("FAIL: PYTHON no longer reproduces the R25 best word -- pipeline drifted.")
        return 1
    print("  python reproduction OK (rounds to 6.826)")

    try:
        rows = engine.score_seeds([SEED], full=False)
    except engine.Blocked as e:
        engine.blocked_exit("%s -- python half PASSED" % e)

    cp = float(rows[0]["pmax"])
    d = abs(cp - WANT)
    print("C engine: pmax %r (|d|=%.3g, tol %.0e)" % (cp, d, ABS_TOL))
    if d > ABS_TOL or round(cp, 3) != 6.826:
        print("FAIL: C engine does not reproduce R25 best word.")
        return 1
    print("PASS: both engines reproduce pmax 6.826 at seed %d" % SEED)
    return 0


if __name__ == "__main__":
    sys.exit(main())
