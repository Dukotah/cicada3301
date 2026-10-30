"""P1: bars + per-register power from out_gate_r36.json -> gate_proof_r36.json (rule: bar = max(empirical, GPD) wrong-key 1-1e-3 quantile of 12-panel pmax;
power = fraction of 24 planted-correct-key decodes with pmax >= bar; required >= 0.90 per register at L=120 and L=240). Printed beside I1's carried-panel numbers."""
import json, os, sys
sys.dont_write_bytecode = True
import numpy as np
LANE = os.path.dirname(os.path.abspath(__file__))
R32 = os.path.abspath(os.path.join(LANE, "..", "..", "round32", "I2-multiregister-readjudication")); I1 = os.path.join(LANE, "..", "I1-new-registers")
sys.path.insert(0, R32); import power as P
o = json.load(open(os.path.join(LANE, "out_gate_r36.json"))); REGS = o["registers"]
r32 = json.load(open(os.path.join(R32, "gate_proof.json")))["cells"]
i1 = json.load(open(os.path.join(I1, "analysis_v1.json")))
def bar(pm):
    g = P.gpd_quantile(pm, 1e-3); e = float(np.quantile(pm, 1 - 1e-3)); return float(max(e, g if g == g else -9))
res = {"panel": "panel-R36 (from-disk build, build1/panel12.npz)", "protocol": "I1 run_gate.py (Round 32 power.py plant_trial verbatim), 24 reps, nproc=1, reduced pre-registered null 4000(L120)/2000(L240)/2000 shuffled",
       "null_n": {}, "bars_pmax12": {}, "cells": {}, "gate_pass": {}, "required": 0.90}
for L in (120, 240):
    z = np.array(o["null"][f"wk{L}"]["z"]); res["null_n"][str(L)] = len(z); res["bars_pmax12"][str(L)] = bar(z.max(1))
    for reg in REGS:
        rows = o["plant"].get(f"{reg}|{L}")
        Z = np.array([r["z"] for r in rows]); k = int((Z.max(1) >= res["bars_pmax12"][str(L)]).sum())
        c = {"hits": k, "n": len(rows), "power": k / len(rows), "median_z_own": float(np.median(Z[:, REGS.index(reg)])), "min_pmax": float(Z.max(1).min()),
             "median_recovery": float(np.median([r["rec"] for r in rows])), "own_register_is_argmax_share": float((Z.argmax(1) == REGS.index(reg)).mean()),
             "i1_carried_panel_power": i1["cells"][f"{reg}|{L}"]["pow12"]}
        if reg in r32[str(L)]["registers"]: c["round32_power"] = r32[str(L)]["registers"][reg]["pow_pmax"]
        c["pass"] = c["power"] >= 0.90; res["cells"][f"{reg}|{L}"] = c; res["gate_pass"][f"{reg}|{L}"] = c["pass"]
res["i1_carried_bars_pmax12"] = i1["bars"]
res["all_12_registers_pass_at_both_lengths"] = all(res["gate_pass"].values())
s = np.array(o["null"]["sh120"]["z"]); w = np.array(o["null"]["wk120"]["z"])
res["null_L120_pmax12"] = {"wrongkey_realLP2": {"mean": float(w.max(1).mean()), "sd": float(w.max(1).std(ddof=1)), "q0.999": float(np.quantile(w.max(1), .999))},
                           "shuffledLP2": {"mean": float(s.max(1).mean()), "sd": float(s.max(1).std(ddof=1)), "q0.999": float(np.quantile(s.max(1), .999))}}
json.dump(res, open(os.path.join(LANE, "gate_proof_r36.json"), "w"), indent=1)
print("bars", res["bars_pmax12"], "| I1 carried", {k: round(v["pmax12"], 3) for k, v in i1["bars"].items()})
for L in (120, 240):
    print("L", L)
    for reg in REGS:
        c = res["cells"][f"{reg}|{L}"]
        print(f"  {reg:13s} {c['hits']:2d}/{c['n']} pow={c['power']:.3f}  R32={c.get('round32_power','-')}  I1carried={c['i1_carried_panel_power']:.3f}  zown={c['median_z_own']:.1f} minpmax={c['min_pmax']:.1f} {'PASS' if c['pass'] else 'FAIL'}")
print("ALL PASS:", res["all_12_registers_pass_at_both_lengths"])
