"""Bars + powers from out_gate_<tag>.json (gates.py rule: bar = max(empirical, GPD) wrong-key 1-1e-3 quantile of pmax)."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "round32", "I2-multiregister-readjudication"))
import power as P
TAG = sys.argv[1] if len(sys.argv) > 1 else "v1"
o = json.load(open(os.path.join(HERE, f"out_gate_{TAG}.json")))
REGS = o["registers"]
r32 = json.load(open(os.path.join(HERE, "..", "..", "round32", "I2-multiregister-readjudication", "gate_proof.json")))
def bar(pm): return float(max(np.quantile(pm, 1 - 1e-3), P.gpd_quantile(pm, 1e-3) if P.gpd_quantile(pm, 1e-3) == P.gpd_quantile(pm, 1e-3) else -9))
res = {"tag": TAG, "bars": {}, "cells": {}, "null_n": {}}
for L in (120, 240):
    z = np.array(o["null"][f"wk{L}"]["z"]); res["null_n"][str(L)] = len(z)
    res["bars"][str(L)] = {"pmax9": bar(z[:, :9].max(1)), "pmax12": bar(z.max(1))}
    for reg in REGS:
        rows = o["plant"].get(f"{reg}|{L}")
        if not rows: continue
        Z = np.array([r["z"] for r in rows])
        p12 = float((Z.max(1) >= res["bars"][str(L)]["pmax12"]).mean())
        p9 = float((Z[:, :9].max(1) >= res["bars"][str(L)]["pmax9"]).mean())
        c = {"pow12": p12, "pow9_same_draws": p9, "median_z_own": float(np.median(Z[:, REGS.index(reg)])),
             "median_pmax": float(np.median(Z.max(1))), "median_recovery": float(np.median([r["rec"] for r in rows])),
             "argmax_mode": REGS[int(np.bincount(Z.argmax(1)).argmax())]}
        if reg in r32["cells"][str(L)]["registers"]:
            c["pow_r32_recorded"] = r32["cells"][str(L)]["registers"][reg]["pow_pmax"]
            c["delta_vs_r32"] = round(p12 - c["pow_r32_recorded"], 4)
        res["cells"][f"{reg}|{L}"] = c
# null shift (shuffled LP2, L=120)
s = np.array(o["null"]["sh120"]["z"]); w = np.array(o["null"]["wk120"]["z"])
def dist(v): return {"n": int(len(v)), "mean": float(v.mean()), "sd": float(v.std(ddof=1)), **{f"q{q}": float(np.quantile(v, q)) for q in (0.5, 0.9, 0.99, 0.999)}, "max": float(v.max()), "emp_bar_1e-3": float(np.quantile(v, 0.999)), "gpd_bar_1e-3": float(P.gpd_quantile(v, 1e-3))}
res["null_shift_L120"] = {"shuffled_LP2": {"pmax9": dist(s[:, :9].max(1)), "pmax12": dist(s.max(1))},
                          "realLP2_wrongkey": {"pmax9": dist(w[:, :9].max(1)), "pmax12": dist(w.max(1))},
                          "argmax_register_share_shuffled12": {REGS[i]: float((s.argmax(1) == i).mean()) for i in range(len(REGS))}}
# gate verdicts
for L in ("120", "240"):
    ok = {}
    for reg in REGS:
        c = res["cells"].get(f"{reg}|{L}")
        if not c: continue
        if "pow_r32_recorded" in c: ok[reg] = c["delta_vs_r32"] >= -0.02
        else: ok[reg] = c["pow12"] >= 0.90
    res.setdefault("gate", {})[L] = ok
json.dump(res, open(os.path.join(HERE, f"analysis_{TAG}.json"), "w"), indent=1)
print("bars", json.dumps(res["bars"]))
for L in ("120", "240"):
    print("L", L)
    for reg in REGS:
        c = res["cells"].get(f"{reg}|{L}")
        if c: print(f"  {reg:13s} pow12={c['pow12']:.3f} pow9={c['pow9_same_draws']:.3f} r32={c.get('pow_r32_recorded','-')} zown={c['median_z_own']:.1f} rec={c['median_recovery']:.3f} {'OK' if res['gate'][L][reg] else 'FAIL'}")
for k in ("shuffled_LP2", "realLP2_wrongkey"):
    for m in ("pmax9", "pmax12"):
        d = res["null_shift_L120"][k][m]; print(k, m, {a: round(d[a], 3) for a in ("mean", "sd", "q0.99", "q0.999", "max", "gpd_bar_1e-3")})
