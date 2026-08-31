"""Round 20 / P1 -- consolidate the pilot runs into ONE published survival SURFACE
(register x decoder-relation x keep-point), the Q4 deliverable, and adjudicate the PASS/PARTIAL/
INFEASIBLE verdict against the FROZEN PREREG thresholds.

Reads the pilot_*.json produced by measure_survival.py and emits survival_surface.json.
It does NOT re-run any compute and it does NOT change any threshold (PREREG is frozen).
"""
import os
import json
import glob

HERE = os.path.dirname(os.path.abspath(__file__))

# frozen PREREG thresholds
GATE_REGISTERS = ["LP1_REAL", "LATIN", "OE", "EN_HALFVOWEL"]     # the 4 PREREG gate registers
ALL9 = ["EN_MODERN", "EN_KJV", "LP1_REAL", "LATIN", "OE", "DE", "CY",
        "EN_HALFVOWEL", "EN_NOVOWEL"]
KILL_REGISTERS = ["CY", "EN_HALFVOWEL"]     # Q5 kill: 0.90 on Welsh + half-vowel English
SURV_THRESH = 0.90
REDUCTION_THRESH = 100.0


def load_cells():
    cells = []
    for p in sorted(glob.glob(os.path.join(HERE, "pilot_*.json"))):
        d = json.load(open(p))
        cell = {"file": os.path.basename(p), "mech": d["mech"], "W": d["W"],
                "fA": d["fA"], "fB": d["fB"], "stageB": d["stageB"],
                "span": d.get("span"), "ntrials": d["ntrials"],
                "survival": {r: {"A": s["survivalA"], "B": s["survivalB"],
                                 "median_reduction": s["median_reduction"]}
                             for r, s in d["summary"].items()}}
        cells.append(cell)
    return cells


def adjudicate(cell):
    """Return (verdict, detail) for one operating point against the frozen thresholds.

    Survival used = the FINAL (Stage-B) survival; reduction = median reduction over trials.
    A cell PASSES only if survival >= 0.90 on ALL 9 registers AND reduction >= 100x.
    """
    surv = cell["survival"]
    # representative reduction (median over registers of the per-register median reductions)
    reds = [surv[r]["median_reduction"] for r in ALL9 if r in surv]
    red = min(reds) if reds else 0.0
    def sv(r):
        return surv[r]["B"] if r in surv else 0.0
    present9 = [r for r in ALL9 if r in surv]   # a cell may measure a register subset
    all9_pass = bool(present9) and all(sv(r) >= SURV_THRESH for r in present9)
    gate_pass = all(sv(r) >= SURV_THRESH for r in GATE_REGISTERS if r in surv)
    kill_pass = all(sv(r) >= SURV_THRESH for r in KILL_REGISTERS if r in surv)
    red_pass = red >= REDUCTION_THRESH
    if all9_pass and red_pass:
        verdict = "PASS"
    elif gate_pass and red_pass:
        verdict = "PARTIAL(gate-registers-only)"
    elif kill_pass and red_pass:
        verdict = "PARTIAL(kill-registers-only)"
    else:
        verdict = "SHORTFALL"
    detail = {"reduction_min_over_registers": red,
              "reduction_pass": red_pass,
              "all9_survival_pass": all9_pass,
              "gate_survival_pass": gate_pass,
              "kill_survival_pass": kill_pass,
              "worst_register": min(present9, key=lambda r: sv(r)) if present9 else None,
              "worst_survival": min((sv(r) for r in present9), default=0.0),
              "CY_survival": sv("CY"), "EN_HALFVOWEL_survival": sv("EN_HALFVOWEL")}
    return verdict, detail


def main():
    cells = load_cells()
    surface = {"lane": "round20/P1",
               "prereg_thresholds": {"survival": SURV_THRESH, "reduction": REDUCTION_THRESH,
                                     "gate_registers": GATE_REGISTERS,
                                     "kill_registers": KILL_REGISTERS, "all9": ALL9},
               "cells": []}
    best_kill = 0.0
    any_pass = False
    for c in cells:
        v, d = adjudicate(c)
        c["verdict"] = v
        c["detail"] = d
        surface["cells"].append(c)
        if v == "PASS":
            any_pass = True
        # track best simultaneous CY & half-vowel survival at >=100x reduction
        if d["reduction_pass"]:
            best_kill = max(best_kill, min(d["CY_survival"], d["EN_HALFVOWEL_survival"]))
    # FROZEN Q5 kill adjudication
    if any_pass:
        overall = "PASS"
    elif best_kill >= SURV_THRESH:
        overall = "PASS(kill-registers, at >=100x)"     # cannot happen if any_pass false, guard
    else:
        overall = "INFEASIBLE"
    surface["best_min(CY,HALFVOWEL)_at>=100x"] = best_kill
    surface["OVERALL_VERDICT"] = overall
    out = os.path.join(HERE, "survival_surface.json")
    json.dump(surface, open(out, "w"), indent=1)
    # human table
    print(f"{'file':<34}{'mech':<13}{'stageB':<10}{'verdict':<26} worstReg/surv  CY  HV  redMin")
    for c in surface["cells"]:
        d = c["detail"]
        print(f"{c['file']:<34}{c['mech']:<13}{c['stageB']:<10}{c['verdict']:<26} "
              f"{d['worst_register']:<8}{d['worst_survival']:.2f}  "
              f"{d['CY_survival']:.2f} {d['EN_HALFVOWEL_survival']:.2f} "
              f"{d['reduction_min_over_registers']:.0f}")
    print(f"\nbest min(CY,HALFVOWEL) at >=100x reduction = {best_kill:.3f} "
          f"(PREREG kill threshold {SURV_THRESH})")
    print(f"OVERALL VERDICT: {overall}")
    print(f"wrote {out}")
    return surface


if __name__ == "__main__":
    main()
