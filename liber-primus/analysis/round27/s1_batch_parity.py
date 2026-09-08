#!/usr/bin/env python3
"""Round 27 — S1 lane-end batch parity re-score (K4 discharge) + histogram sanity.

Scope (honest scaling, per closeout protocol):
  * ALL S1 flags with C pmax >= HARD_GATE = claim_bar - 1.5 = 5.883520294328688
    (the zone where a C-side false-reject could hide a true key), plus
  * a uniform random sample of 2,000 of the remaining S1 flags (fixed RNG seed 27).

Every selected seed is re-scored with the Python R25 reference (runner.stage_a,
verbatim via P2-harness/pyref.py) and compared to the C screen pmax recorded in
run/candidates.jsonl. Any |C - Python| > 1e-6 = K4 kill (parity void).

Also: sums run/hist_S1.u64 (6 workers x 2600 bins of 0.01 over [0,26)) — total must be
exactly 2^32, and the >= cand_bar(5.0) tail must equal the S1 candidate count and sit
inside the K2 window [0.2x, 5x] of the Gumbel prediction 6.95e-5/seed.

Read-only w.r.t. the running sweep. Single-threaded; run under nice -n 15.
Output: JSON to stdout (recorded in S1-CLOSEOUT.md).
"""
import json
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P2 = os.path.join(HERE, "P2-harness")
if P2 not in sys.path:
    sys.path.insert(0, P2)

import pyref                        # noqa: E402  imports the R25 pipeline VERBATIM
from pyref import runner            # noqa: E402

CAND_PATH = os.path.join(HERE, "P1-engine", "run", "candidates.jsonl")
HIST_PATH = os.path.join(HERE, "P1-engine", "run", "hist_S1.u64")
CLAIM_BAR = 7.3835202943286884
HARD_GATE = CLAIM_BAR - 1.5         # 5.8835202943286884
PARITY_TOL = 1e-6
SAMPLE_N = 2000
RNG_SEED = 27
GUMBEL_RATE = 6.95e-5               # expected flags/seed at cand_bar 5.0 (PREREG)
LANE_SPACE = 2 ** 32


def main():
    # ---- select the re-score set from the S1 flags
    hi, lo = [], []
    with open(CAND_PATH) as f:
        for line in f:
            r = json.loads(line)
            if r.get("lane") != "S1":
                continue
            (hi if r["pmax"] >= HARD_GATE else lo).append((r["seed"], r["pmax"]))
    sample = random.Random(RNG_SEED).sample(lo, SAMPLE_N)
    todo = hi + sample

    # ---- Python re-score, single process (sweep S2 owns the cores)
    max_delta, argmax = 0.0, None
    py_over_claim = []
    for i, (seed, c_pmax) in enumerate(todo):
        py = runner.stage_a(seed)
        d = abs(py - c_pmax)
        if d > max_delta:
            max_delta, argmax = d, seed
        if py >= CLAIM_BAR:
            py_over_claim.append({"seed": seed, "py_pmax": py, "c_pmax": c_pmax})
        if (i + 1) % 1000 == 0:
            print("  rescored %d/%d (max_delta %r)" % (i + 1, len(todo), max_delta),
                  file=sys.stderr)

    # ---- histogram sanity
    with open(HIST_PATH, "rb") as f:
        raw = f.read()
    bins = struct.unpack("<%dQ" % (len(raw) // 8), raw)
    nw = len(bins) // 2600
    tot = [0] * 2600
    for w in range(nw):
        for b in range(2600):
            tot[b] += bins[w * 2600 + b]
    hist_total = sum(tot)
    tail_ge_5 = sum(tot[500:])       # bins of 0.01 over [0,26): bin 500 = pmax 5.00
    tail_ge_claim = sum(tot[739:])   # 7.39 <= first full bin above the claim bar
    exp_flags = GUMBEL_RATE * LANE_SPACE

    out = {
        "lane": "S1",
        "n_s1_flags_total": len(hi) + len(lo),
        "hard_gate": HARD_GATE,
        "n_rescored_hard_gate": len(hi),
        "n_rescored_random_sample": len(sample),
        "rng_seed": RNG_SEED,
        "n_rescored_total": len(todo),
        "max_abs_delta": repr(max_delta),
        "max_abs_delta_seed": argmax,
        "k4_parity_ok": max_delta <= PARITY_TOL,
        "python_pmax_over_claim_bar": py_over_claim,
        "hist": {
            "workers": nw,
            "total_seeds": hist_total,
            "total_is_2pow32": hist_total == LANE_SPACE,
            "tail_ge_cand_bar_5.0": tail_ge_5,
            "tail_matches_flag_count": tail_ge_5 == len(hi) + len(lo),
            "tail_ge_7.39": tail_ge_claim,
            "gumbel_expected_flags": exp_flags,
            "flag_rate_x_gumbel": tail_ge_5 / exp_flags,
            "k2_window": [0.2, 5.0],
        },
    }
    print(json.dumps(out, indent=1))
    return 0 if out["k4_parity_ok"] else 4


if __name__ == "__main__":
    sys.exit(main())
