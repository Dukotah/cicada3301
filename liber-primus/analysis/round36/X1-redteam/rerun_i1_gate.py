"""X1 re-run: GREEK and NORSE plant cells at L=120 under panel-R36 (P1 build1). reps 0-7 (lane seeds) and 100-107 (fresh)."""
import os, sys, json, hashlib
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); R36 = os.path.abspath(os.path.join(HERE, ".."))
R32 = os.path.abspath(os.path.join(R36, "..", "round32", "I2-multiregister-readjudication")); sys.path.insert(0, R32)
import power as P
AJ = P.AJ
pp = os.path.join(R36, "P1-panel-r36", "build1", "panel12.npz"); tp = os.path.join(R36, "P1-panel-r36", "build1", "testhalves12.npz")
sha = hashlib.sha256(open(pp, "rb").read()).hexdigest()
pan = AJ.Panel(pp); AJ._PANEL = pan
d = np.load(tp)
lane = json.load(open(os.path.join(R36, "P1-panel-r36", "out_gate_r36.json")))
bar = json.load(open(os.path.join(R36, "P1-panel-r36", "gate_proof_r36.json")))["bars_pmax12"]["120"]
res = {"panel_sha256": sha, "bar_L120": bar, "cells": {}}
for reg in ("GREEK", "NORSE"):
    T = d[reg].astype(np.int64); i = pan.registers.index(reg)
    rows = {}
    for rep in list(range(8)) + list(range(100, 108)):
        r = P.plant_trial(T, 120, rep, pan)
        rows[rep] = {"z": [round(float(v), 4) for v in r["z"]], "pmax": float(max(r["z"])), "rec": r["recovery"]}
    lz = lane["plant"][reg + "|120"]
    same = [bool(np.allclose(rows[k]["z"], lz[k]["z"], atol=1e-3)) for k in range(8)]
    fresh = [rows[k]["pmax"] >= bar for k in range(100, 108)]
    lane8 = [max(x["z"]) >= bar for x in lz[:8]]
    res["cells"][reg] = {"lane_reps0_7_reproduced_z": same, "lane_hits_first8": sum(lane8), "rerun_hits_reps0_7": sum(rows[k]["pmax"] >= bar for k in range(8)),
        "fresh_reps100_107_hits": sum(fresh), "fresh_min_pmax": min(rows[k]["pmax"] for k in range(100, 108)), "rows": rows,
        "own_is_argmax_fresh": sum(int(np.argmax(rows[k]["z"]) == i) for k in range(100, 108))}
    print(reg, {k: v for k, v in res["cells"][reg].items() if k != "rows"}, flush=True)
json.dump(res, open(os.path.join(HERE, "rerun_i1_gate.json"), "w"))
