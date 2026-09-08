#!/usr/bin/env python3
"""Check 2 -- planted-seed drill (SPEC V2 + the live-sweep half of V3's spirit).

Part A (needs binary): grind27 --mode self-test must decode the FROZEN planted stage-A
construct (vectors.json["planted_stage_a"], seed 777) and flag it as a candidate with
pmax = 17.93115850976196 (+-1e-9).

Part B (needs binary): plant a FRESH construct at an arbitrary mid-space seed
(default 3141592653), enciphered by the same skip_by_two recipe, and run a LIVE
micro-sweep of a few million seeds with the plant mid-band. The planted seed MUST land
in candidates.jsonl with pmax matching the Python reference (+-1e-9). This is the
anti-broken-magnet drill run through the REAL sweep path (threads, banding, candidate
emission), not a special-cased scorer.

Python-side pre-verification (runs without the binary): builds the fresh plant, scores
it with the Python reference, and requires pmax >= CAND_BAR + 1.0 -- proving the drill
itself is well-posed before the C engine is judged against it.

Exit: 0 PASS, 1 FAIL, 2 BLOCKED-ON-BINARY (after the Python pre-check).
"""
import argparse
import json
import os
import sys
import tempfile

import engine
import pyref

ABS_TOL = 1e-9
DRILL_SEED_DEFAULT = 3141592653          # arbitrary mid-space u32
HALF_BAND_DEFAULT = 1_500_000            # sweep = 3M seeds, plant mid-band


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drill-seed", type=int, default=DRILL_SEED_DEFAULT)
    ap.add_argument("--half-band", type=int, default=HALF_BAND_DEFAULT)
    ap.add_argument("--threads", type=int, default=6)
    args = ap.parse_args()

    vecs = pyref.vectors()

    # ---- Python pre-check: fresh plant is well-posed ---------------------------
    w = args.drill_seed & 0xFFFFFFFF
    plant = pyref.build_plant(w)
    cipher120 = plant["cipher_idx"][:120]
    ref = pyref.stage_a_full(w, cipher=cipher120)
    print("drill plant: seed %d, python stage-A pmax %r (CAND_BAR %.1f)"
          % (w, ref["pmax"], pyref.CAND_BAR))
    if ref["pmax"] < pyref.CAND_BAR + 1.0:
        print("FAIL: drill is ill-posed -- planted construct only scores %r under the "
              "PYTHON reference; pick another drill seed / fix the plant recipe before "
              "judging the C engine." % ref["pmax"])
        return 1
    print("  python pre-check OK (margin over CAND_BAR: %.2f)" % (ref["pmax"] - pyref.CAND_BAR))

    # ---- Part A: frozen self-test ---------------------------------------------
    try:
        rc, st, raw = engine.self_test()
    except engine.Blocked as e:
        engine.blocked_exit("%s -- python pre-check of the fresh plant PASSED; "
                            "parts A and B await the binary" % e)
    ok_a = True
    want = float(vecs["planted_stage_a"]["pmax"])
    if st is None:
        print("FAIL A: self-test emitted no JSON line; raw stdout:\n%s" % raw[-1000:])
        ok_a = False
    else:
        d = abs(float(st.get("pmax", -1e9)) - want)
        cand = bool(st.get("candidate"))
        print("self-test: rc=%d pmax=%r (want %r, |d|=%.3g) candidate=%s"
              % (rc, st.get("pmax"), want, d, cand))
        if rc != 0 or not cand:
            print("FAIL A: planted seed 777 NOT flagged as candidate")
            ok_a = False
        if d > ABS_TOL:
            print("FAIL A: self-test pmax off by %.3g (tol %.0e)" % (d, ABS_TOL))
            ok_a = False
    if ok_a:
        print("PASS A: frozen planted screen flagged, pmax matches")

    # ---- Part B: live micro-sweep with plant mid-band --------------------------
    lo = max(0, w - args.half_band)
    hi = min(2 ** 32, w + args.half_band)
    td = tempfile.mkdtemp(prefix="p2drill.")
    cands_path = os.path.join(td, "candidates.jsonl")
    print("live micro-sweep: band [%d, %d) = %d seeds, %d threads, plant mid-band"
          % (lo, hi, hi - lo, args.threads))
    summary, cands = engine.sweep(lo, hi, cands_path, threads=args.threads,
                                  cipher_idx=cipher120)
    print("  sweep summary: %s" % json.dumps(summary))
    print("  candidates emitted: %d" % len(cands))
    hit = [c for c in cands if int(c.get("seed", -1)) == w]
    ok_b = True
    if not hit:
        print("FAIL B: planted seed %d NOT in candidates.jsonl -- the sweep path can "
              "throw away a true seed (broken magnet). DO NOT LAUNCH." % w)
        ok_b = False
    else:
        d = abs(float(hit[0]["pmax"]) - ref["pmax"])
        print("  planted seed found: pmax %r vs python %r (|d|=%.3g)"
              % (hit[0]["pmax"], ref["pmax"], d))
        if d > ABS_TOL:
            print("FAIL B: candidate pmax off by %.3g (tol %.0e)" % (d, ABS_TOL))
            ok_b = False
    if ok_b:
        print("PASS B: planted seed landed in candidates.jsonl with matching pmax")

    return 0 if (ok_a and ok_b) else 1


if __name__ == "__main__":
    sys.exit(main())
