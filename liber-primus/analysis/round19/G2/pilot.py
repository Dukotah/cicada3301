"""ROUND 19 / LANE G2 -- PLUMBING PILOT.  *** NOT A RESULT. ***

READ THIS FIRST
---------------
This script proves that validated G2 keystreams flow end-to-end through I1/I3's
decoder and I2's adjudicator and come out as well-formed SWEEPROWs, and it
measures how long each stage takes.  **It is not a sweep and its scores are not
findings.**  Phase 0's gates (I1 power envelope, I2 register panel, I3
recalibrated thresholds) have not published PASS verdicts, and doctrine forbids
scoring a key space with an unvalidated instrument -- that is the specific
mistake Round 19 exists to correct.

Accordingly:
  * the decode budget is hard-capped at PILOT_CAP = 10,000 decodes;
  * every output file is stamped `"is_result": false` and
    `"scores_are_not_findings": true`;
  * no score is compared to any threshold, no candidate is escalated, and no
    best-of is reported as a bound;
  * the seeds are a fixed arbitrary block, chosen for reproducibility, NOT the
    high-prior band -- so nothing here can be mistaken for coverage of it.

What it DOES report is the only thing Phase 2 needs from G2 right now: real
per-stage timings on this box, so `READY.md`'s wall-clock is measured rather
than guessed.

Run:  python3 pilot.py
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R19 = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (os.path.join(ROOT, "src"),
          os.path.join(ROOT, "analysis"),
          os.path.join(ROOT, "analysis", "round11"),
          os.path.join(ROOT, "analysis", "campaign18_skip"),
          os.path.join(R19, "I1"), os.path.join(R19, "I2"), os.path.join(R19, "I3"),
          HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import lib_numchannel as nc     # noqa: E402
import gen_perl as G            # noqa: E402

PILOT_CAP = 10_000
N = 29
MAX_SKIP = 3

# A deliberately ARBITRARY seed block. Not S0, not S1, not the era band --
# picking a high-prior band here would let a plumbing run masquerade as coverage.
PILOT_SEED_BASE = 700_000_000
SEEDS_PER_CELL = 625
ORIENTATIONS = [(sign, atb, drc)
                for sign in (-1, +1)
                for atb in (False, True)
                for drc in ("fwd", "rev")]          # 8


def build_batch(red, seeds, L, orientation):
    """(C, K) arrays for one (reduction, orientation) cell."""
    sign, atb, drc = orientation
    KL = L * (2 * MAX_SKIP + 2) + 64
    C0 = np.asarray(nc.unsolved()[:L], dtype=np.int64)
    if atb:
        C0 = (N - 1) - C0
    C = np.tile(C0, (len(seeds), 1))
    K = np.empty((len(seeds), KL), dtype=np.int64)
    for i, s in enumerate(seeds):
        ks = G.make_ks(red, s, KL)
        K[i] = ks[::-1] if drc == "rev" else ks
    return C, K, sign


def main():
    import vecbeam                      # I3
    import adjudicate as ADJ            # I2
    import driftbeam                    # I1  (imported to pin the version used)

    out = {
        "lane": "round19/G2",
        "artifact": "PLUMBING PILOT",
        "is_result": False,
        "scores_are_not_findings": True,
        "why": ("Phase 0 gates (I1 power envelope, I2 panel, I3 thresholds) have not "
                "published PASS. Doctrine forbids scoring a key space with an "
                "unvalidated instrument. This run measures timings and proves the "
                "SWEEPROW plumbing, nothing else."),
        "pilot_cap": PILOT_CAP,
        "seed_block": {"base": PILOT_SEED_BASE, "per_cell": SEEDS_PER_CELL,
                       "note": "arbitrary, NOT the high-prior band, so this cannot be "
                               "mistaken for coverage"},
        "generator_validated_by": "round19/G2/validation.json (gates A/B/C PASS)",
        "cells": [],
    }

    n_decodes = 0
    rows = []

    # (reduction, L, decoder mode).  L=31 is the candidate SCREEN tier, L=120 the
    # escalation tier; they are timed separately because their costs differ by
    # more than an order of magnitude and READY.md needs both.
    plan = [("r29", 31, "keyskip1"),
            ("r29", 120, "keyskip1"),
            ("r29", 120, "skip_by_two"),
            ("r29_nodup", 120, "keyskip1")]
    per_cell = PILOT_CAP // len(plan)          # 2500
    nseed = per_cell // len(ORIENTATIONS)      # 312 seeds x 8 orientations

    for red, L, mode in plan:
        t_gen = t_dec = t_adj = t_adjb = 0.0
        cell_n = 0
        for oi, orientation in enumerate(ORIENTATIONS):
            seeds = [PILOT_SEED_BASE + oi * 1_000_000 + i for i in range(nseed)]

            t0 = time.time()
            C, K, sign = build_batch(red, seeds, L, orientation)
            t_gen += time.time() - t0

            t0 = time.time()
            r = vecbeam.batch_decode(C, K, sign=sign, beam_w=400,
                                     max_skip=MAX_SKIP, mode=mode, want_plain=True)
            t_dec += time.time() - t0

            # I2 fast path: panel only, vectorised over the block.
            t0 = time.time()
            ADJ.adjudicate_batch(r["plain"])
            t_adjb += time.time() - t0

            # I2 full path: the complete SWEEPROW, one call per decode.
            t0 = time.time()
            for i in range(len(seeds)):
                res = ADJ.adjudicate(r["plain"][i])
                kid = (f"perl514|{red}|seed={seeds[i]}|sign={sign}|"
                       f"atb={int(orientation[1])}|dir={orientation[2]}|off=0|"
                       f"L={L}|mode={mode}")
                rows.append(ADJ.to_row(res, kid))
            t_adj += time.time() - t0

            cell_n += len(seeds)

        n_decodes += cell_n
        tot = t_gen + t_dec + t_adj
        out["cells"].append({
            "reduction": red, "L": L, "mode": mode, "n_decodes": cell_n,
            "orientations": len(ORIENTATIONS),
            "gen_s": round(t_gen, 3), "decode_s": round(t_dec, 3),
            "adjudicate_full_s": round(t_adj, 3),
            "adjudicate_batch_panel_only_s": round(t_adjb, 3),
            "gen_per_s": round(cell_n / t_gen, 1),
            "decode_per_s": round(cell_n / t_dec, 1),
            "adjudicate_full_per_s": round(cell_n / t_adj, 1),
            "adjudicate_batch_per_s": round(cell_n / t_adjb, 1),
            "end_to_end_per_s": round(cell_n / tot, 1),
            "end_to_end_per_s_batch_adj": round(cell_n / (t_gen + t_dec + t_adjb), 1),
        })
        print(f"  {red:10s} L={L:3d} {mode:12s} n={cell_n:5d}  "
              f"gen {cell_n/t_gen:8.0f}/s  dec {cell_n/t_dec:8.1f}/s  "
              f"adjFULL {cell_n/t_adj:7.1f}/s  adjBATCH {cell_n/t_adjb:9.0f}/s  "
              f"=> e2e {cell_n/tot:7.1f}/s (batch {cell_n/(t_gen+t_dec+t_adjb):8.1f}/s)")

    # SWEEPROW validation -- doctrine R3 is CI-enforced, so prove compliance here.
    hdr = ADJ.header("round19-G2-PILOT",
                     lane="G2", is_result=False,
                     generator="perl514_drand48",
                     generator_validation="round19/G2/validation.json")
    bad = 0
    for row in rows:
        try:
            ADJ.validate_row(row, hdr)
        except ADJ.RowError as e:
            bad += 1
            if bad == 1:
                print("  ROW ERROR:", e)

    out["timings"] = {"n_decodes": n_decodes, "per_cell": out["cells"],
                      "cores_detected": os.cpu_count()}
    out["sweeprow"] = {"rows_emitted": len(rows), "rows_failing_validate_row": bad,
                       "schema": hdr.get("v"), "fields": hdr.get("fields")}

    with open(os.path.join(HERE, "pilot.json"), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(HERE, "pilot_rows.jsonl"), "w") as f:
        f.write(json.dumps({"HEADER": hdr, "is_result": False}) + "\n")
        for row in rows:
            f.write(json.dumps(row) + "\n")

    print("=" * 74)
    print("ROUND 19 / G2 -- PLUMBING PILOT   *** NOT A RESULT ***")
    print("=" * 74)
    print(f"  decodes {n_decodes:,} (cap {PILOT_CAP:,}), cores {os.cpu_count()}")
    print(f"  SWEEPROWs emitted {len(rows)}, failing validate_row: {bad}")
    print("\n  No score in pilot_rows.jsonl was compared to a threshold, and none")
    print("  may be cited as coverage, a bound, or a negative.")


if __name__ == "__main__":
    main()
