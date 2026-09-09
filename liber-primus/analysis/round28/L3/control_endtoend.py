#!/usr/bin/env python3
"""Round 28 / L3 — END-TO-END planted-control power measurement.

The sweep drops a seed unless stage-A (beam L=120 screen on the ciphertext) reaches
SCREEN_BAR=5.0; controls.json validated stage-B only. This measures the FULL path —
plant cipher -> stage-A screen (must clear 5.0) -> stage-B hitfn20 (must HIT with
recovery >= 0.90) — for 10 planted dictionary words per (reducer x relation) cell.
Required: >= 0.90 end-to-end recovery per cell (PREREG Q1). Writes control_e2e.json.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sweep28 as S  # noqa  (reuses the exact sweep code paths)

PLANTS = ["THE PRIMES ARE SACRED", "DIVINITY", "CICADA3301", "an end",
          "INSTAR EMERGENCE", "patience", "circumference", "2013-01-04",
          "ky2khlqdf7qdznac", "liber primus"]

CELLS = [("random29", "pair"), ("random29", "exact"), ("grb5_mod", "pair"),
         ("grb5_rej", "pair"), ("shuffle29", "pair")]


def main():
    import skipdecode as sk
    eng = sk.eng_to_idx(open(os.path.join(S.LP, "data", "keys", "self_reliance.txt"),
                             encoding="utf-8", errors="ignore").read())[5000:5000 + S.L_HIT]
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "screen_bar": S.SCREEN_BAR,
           "n_plants_per_cell": len(PLANTS), "cells": []}
    all_ok = True
    for mode, preset in CELLS:
        n_pass = 0
        rows = []
        for w in PLANTS:
            K = S.keystream(w, mode, S.L_HIT * 6 + 64)
            if preset == "pair":
                C = S.encipher_skip_by_two(eng, K)
            else:
                C, _s, _u = sk.encipher_keyskip(eng, K, sign=-1, supp=0.83, seed=777)
                C = list(C)[:S.L_HIT]
            # stage A exactly as the sweep runs it, but on the plant cipher
            import driftbeam as DB
            import adjudicate as AD
            Ka = S.keystream(w, mode, S.L_SCREEN * 6 + 64)
            d = DB.beam_decode(C[:S.L_SCREEN], Ka, sign=-1, o=0,
                               beam_w=S.SCREEN_BEAM_W, **DB.PRESETS[preset])
            a_pm = float(AD.adjudicate(d["plain_idx"], translit=d.get("translit"))["pmax"])
            screen_ok = a_pm >= S.SCREEN_BAR
            gate_ok = False
            if screen_ok:
                import hitfn20 as H
                dec = H.HitDecode(C=C[:S.L_HIT], K=K, o=0, preset=preset,
                                  n_round_adjudicated=S.N_ADJ_BAR,
                                  truth_idx=eng[:len(C[:S.L_HIT])])
                v = H.evaluate(dec)
                gate_ok = bool(v.hit) and v.recovery >= 0.90
            ok = screen_ok and gate_ok
            n_pass += ok
            rows.append({"w": w, "stage_a_pmax": round(a_pm, 3),
                         "screen_ok": screen_ok, "end_to_end": ok})
        rec = n_pass / len(PLANTS)
        cell_ok = rec >= 0.90
        all_ok &= cell_ok
        out["cells"].append({"cell": "%s x %s" % (mode, preset),
                             "end_to_end_recovery": rec, "pass": cell_ok,
                             "min_stage_a_pmax": min(r["stage_a_pmax"] for r in rows),
                             "plants": rows})
        print(json.dumps(out["cells"][-1]["cell"]), rec,
              "min_stageA", out["cells"][-1]["min_stage_a_pmax"])
    out["all_pass"] = all_ok
    json.dump(out, open(os.path.join(HERE, "control_e2e.json"), "w"), indent=1)
    print("E2E CONTROLS:", "ALL PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
