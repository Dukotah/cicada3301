#!/usr/bin/env python3
"""Round 28 / L4 -- K4-style batch parity: re-score grind28 C-flagged candidates
through the Python reference pipeline (runner/driftbeam/adjudicate, imported
verbatim) with the cell's generator from gen28/gen_py27.

Policy (mirrors R27 s1_batch_parity.py, RNG seed 28): for each completed lane,
re-score EVERY candidate with pmax >= claim_bar - 1.5 (the hard gate) plus 2000
uniformly sampled candidates below it. Any |C - Python| pmax disagreement > 1e-6
VOIDS the lane (PREREG Q1). Writes receipts/batch_parity_<lane>.json.

    nice -n 15 python3 stage_a28.py --run-dir <dir> [--lane NAME] [--sample 2000]

Run AFTER a queued cell completes (closeout), not during the NOW phase.
"""
import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import make_gates as MG          # noqa: brings runner/DB/AD/H + STREAMS + stage_a


def rescore(lane_cfg, seed):
    K = MG.STREAMS[lane_cfg["reducer"]](seed, MG.L_SCREEN * 6 + 64)
    _, pmax = MG.stage_a(MG.runner.C_SCREEN, K, lane_cfg["relation"],
                         lane_cfg["offset"])
    return pmax


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--plan", default=os.path.join(HERE, "queued_cells.json"))
    ap.add_argument("--lane", default=None, help="restrict to one lane")
    ap.add_argument("--sample", type=int, default=2000)
    ap.add_argument("--tol", type=float, default=1e-6)
    args = ap.parse_args()

    plan = {e["lane"]: e for e in json.load(open(args.plan))}
    cands = {}
    with open(os.path.join(args.run_dir, "candidates.jsonl")) as f:
        for line in f:
            row = json.loads(line)
            if args.lane and row["lane"] != args.lane:
                continue
            cands.setdefault(row["lane"], []).append((row["seed"], row["pmax"]))

    overall_ok = True
    for lane, rows in sorted(cands.items()):
        cfg = plan[lane]
        hard = [r for r in rows if r[1] >= cfg["claim_bar"] - 1.5]
        rest = [r for r in rows if r[1] < cfg["claim_bar"] - 1.5]
        rng = random.Random(28)
        pick = hard + (rng.sample(rest, min(args.sample, len(rest))) if rest else [])
        worst, worst_seed, n_bad = 0.0, None, 0
        for seed, cpm in pick:
            ppm = rescore(cfg, seed)
            d = abs(ppm - cpm)
            if d > worst:
                worst, worst_seed = d, seed
            if d > args.tol:
                n_bad += 1
        ok = n_bad == 0
        overall_ok &= ok
        rec = {"lane": lane, "n_candidates": len(rows), "n_hard_gate": len(hard),
               "n_rescored": len(pick), "worst_abs_delta": worst,
               "worst_seed": worst_seed, "tol": args.tol,
               "n_over_tol": n_bad, "pass": ok,
               "policy": "all >= claim-1.5 + uniform sample, RNG seed 28"}
        out = os.path.join(HERE, "receipts", f"batch_parity_{lane}.json")
        json.dump(rec, open(out, "w"), indent=1)
        print(f"{lane}: {len(pick)} re-scored ({len(hard)} hard-gate), worst |d| "
              f"{worst:.3g} -> {'PASS' if ok else 'FAIL (LANE VOID)'}")
    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
