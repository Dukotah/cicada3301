"""ROUND 19 / G4 — timing bench for the Phase-2 full-enumeration route.

Measures, on this box, the two costs READY.md quotes:
  (a) building the reduced master cycle (uint8, one symbol per phase), and
  (b) one rigid sliding-window prefilter pass over it.

Both are measured on a 2^24-phase slice and extrapolated to the full 2^31-2, with the
slice size and the extrapolation factor reported so the number can be checked.

    python3 bench_master.py
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis", os.path.join("analysis", "round11")):
    sys.path.insert(0, os.path.join(ROOT, p))
sys.path.insert(0, HERE)

import lib_numchannel as nc            # noqa: E402
import gen_tex as gt                   # noqa: E402

N = 29
SLICE = 1 << 24                        # 16 777 216 phases
FULL = gt.M31 - 1                      # 2 147 483 646
W = 32                                 # prefilter window (runes before the first key skip)


def build_slice(a=gt.PGF_A, total=SLICE, lanes=1 << 16):
    per = total // lanes
    step = pow(a, per, gt.M31)
    starts = np.empty(lanes, dtype=np.int64)
    z = 1
    for i in range(lanes):
        starts[i] = z
        z = (z * step) % gt.M31
    cur = starts
    block = np.empty((lanes, per), dtype=np.int64)
    for t in range(per):
        cur = (a * cur) % gt.M31
        block[:, t] = cur
    return (block % N).astype(np.uint8).ravel()


def main():
    res = {"lane": "round19/G4", "bench": "Phase-2 full-enumeration route",
           "slice_phases": SLICE, "full_phases": FULL,
           "extrapolation_factor": FULL / SLICE, "window": W}

    t0 = time.time()
    M = build_slice()
    t_build = time.time() - t0
    res["build"] = {"slice_s": round(t_build, 2),
                    "full_s_est": round(t_build * FULL / SLICE, 1),
                    "full_bytes": FULL,
                    "full_gib": round(FULL / 2**30, 2),
                    "distinct_symbols": int(len(np.unique(M)))}

    # rigid prefilter: s(p) = sum_i LUT[C_i][M[p+i]] over a W-rune window.
    # 29x29 LUT of per-position unigram log-probabilities of the rigid plaintext.
    C = np.asarray(nc.unsolved()[:W], dtype=np.int64)
    counts = np.bincount(np.asarray(nc.solved_plain() if hasattr(nc, "solved_plain")
                                    else nc.unsolved(), dtype=np.int64), minlength=N) + 1.0
    logf = np.log(counts / counts.sum()).astype(np.float32)
    LUT = np.empty((N, N), dtype=np.float32)
    for c in range(N):
        for k in range(N):
            LUT[c, k] = logf[(c - k) % N]

    t0 = time.time()
    nph = len(M) - W
    acc = np.zeros(nph, dtype=np.float32)
    for i in range(W):
        acc += LUT[int(C[i])][M[i:i + nph]]
    t_scan = time.time() - t0
    res["prefilter_pass"] = {
        "slice_s": round(t_scan, 2),
        "full_s_est": round(t_scan * FULL / SLICE, 1),
        "note": ("one pass = one (stream family x sign x direction x atbash x c) cell; "
                 "Phase 2 needs 8 cells per stream family"),
        "cells_per_stream_family": 8,
        "full_all_cells_s_est": round(t_scan * FULL / SLICE * 8, 1),
    }

    # what a 1e-3 cut leaves for the beam
    for frac in (1e-2, 1e-3, 1e-4):
        res.setdefault("cut_sizes", {})[f"{frac:g}"] = int(FULL * frac)

    json.dump(res, open(os.path.join(HERE, "bench_master.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
