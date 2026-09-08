#!/usr/bin/env python3
"""Check 5 -- throughput bench. Measures aggregate seeds/s of the C engine's REAL sweep
path (live LP2 C_SCREEN, 6 threads) over >= 60 s of wall clock and computes the ETA for
one full 2^32 lane. SPEC section 7: target >= 30k seeds/s aggregate (<= ~40 h);
kill-condition K1 fires below 2,000 seeds/s/core (= 12k aggregate on 6 threads).

Exit: 0 PASS (>= target), 1 FAIL (below K1), 2 BLOCKED-ON-BINARY.
A rate between K1 and target exits 0 but prints PROFILE-BEFORE-LAUNCH.
"""
import argparse
import json
import os
import sys
import tempfile
import time

import engine

CAL_BAND = 200_000                 # calibration band size
MIN_WALL = 60.0                    # measured run must span >= 60 s
BAND_BASE = 100_000_000            # arbitrary live band start (real C_SCREEN)
TARGET_AGG = 30_000.0              # SPEC section 7 conservative target
K1_PER_CORE = 2_000.0              # PREREG kill-condition


def timed_sweep(start, size, threads, td):
    out = os.path.join(td, "cands_%d.jsonl" % start)
    t0 = time.time()
    summary, cands = engine.sweep(start, start + size, out, threads=threads)
    wall = time.time() - t0
    return wall, summary, cands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", type=int, default=6)
    ap.add_argument("--min-wall", type=float, default=MIN_WALL)
    ap.add_argument("--cal-band", type=int, default=CAL_BAND,
                    help="calibration band size (only lower for smoke tests)")
    args = ap.parse_args()
    cal_band = args.cal_band

    try:
        engine.find_binary(), engine.find_lm()
    except engine.Blocked as e:
        engine.blocked_exit(str(e))

    with tempfile.TemporaryDirectory(prefix="p2bench.") as td:
        # calibration burst to size the real run
        wall, _, _ = timed_sweep(BAND_BASE, cal_band, args.threads, td)
        rate0 = cal_band / wall
        print("calibration: %d seeds in %.1fs -> %.0f seeds/s aggregate" %
              (cal_band, wall, rate0))
        size = max(cal_band, int(rate0 * args.min_wall * 1.3))
        print("measured run: band [%d, %d) (%d seeds, %d threads)"
              % (BAND_BASE + cal_band, BAND_BASE + cal_band + size, size, args.threads))
        wall, summary, cands = timed_sweep(BAND_BASE + cal_band, size, args.threads, td)

    rate = size / wall
    per_core = rate / args.threads
    eta_h = 2 ** 32 / rate / 3600.0
    report = {
        "seeds": size, "wall_s": round(wall, 1), "threads": args.threads,
        "seeds_per_s_aggregate": round(rate, 1), "seeds_per_s_per_core": round(per_core, 1),
        "eta_full_2pow32_hours": round(eta_h, 2),
        "candidates_in_band": len(cands),
        "engine_summary": summary,
    }
    print(json.dumps(report, indent=1))

    if wall < args.min_wall * 0.9:
        print("WARN: measured window %.1fs < %.0fs -- calibration underestimated; "
              "rerun bench.py" % (wall, args.min_wall))
    if per_core < K1_PER_CORE:
        print("FAIL: %.0f seeds/s/core < K1 kill-condition %.0f -- profile before any "
              "launch (PREREG K1)." % (per_core, K1_PER_CORE))
        return 1
    if rate < TARGET_AGG:
        print("PROFILE-BEFORE-LAUNCH: above K1 but below the %.0f/s aggregate target; "
              "ETA %.1f h" % (TARGET_AGG, eta_h))
    else:
        print("PASS: %.0f seeds/s aggregate; full 2^32 lane ETA %.1f h" % (rate, eta_h))
    return 0


if __name__ == "__main__":
    sys.exit(main())
