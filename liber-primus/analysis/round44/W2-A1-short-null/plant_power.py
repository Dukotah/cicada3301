"""R44 / W2-A1 step 2 — GLUE PLANT + POWER measurement (PREREG §2 Q1, §3) -> plant_power.json.

Gate: the L=120 held-out-English plant through the cell's OWN grid must clear the cell's own
L=120 bar of record (and is cross-reported vs bars_v3 free@120).  No real read without it.
Power per node: fraction of 300 held-out EN (and 300 LATIN) windows whose grid-max pmax
clears the bar of record.  EN power < 0.5 at a node => streams at that node are measured-only.
"""
import json

import numpy as np

import shortnull as S

rng = np.random.default_rng(S.SEED)
pan = S.panel()
bars = {int(k): v["bar_of_record"]
        for k, v in json.load(open("short_null.json"))["nodes"].items()}

out = {"bars": bars, "power_floor": S.POWER_FLOOR, "n_windows": 300, "nodes": {}}

# ---- the glue plant (single, pre-registered): first held-out EN window at L=120
plant_x = S.english_windows(120, 1, np.random.default_rng(S.SEED + 1))[0]
pm, r, X, meta = S.grid_pmax(plant_x, pan)
i = int(pm.argmax())
identity_ok = bool((X[meta.index(dict(dir="fwd", a=1, s=0))] == plant_x).all())
plant = {"L": 120, "pmax": round(float(pm[i]), 4), "bar": bars[120],
         "best_map": meta[i], "identity_cell_intact": identity_ok,
         "passed": bool(pm[i] >= bars[120] and identity_ok)}
out["glue_plant_L120"] = plant
print("GLUE PLANT:", plant, flush=True)

# ---- power curves
for L in S.L_NODES:
    node = {}
    for lang, latin in (("EN", False), ("LA", True)):
        W = S.english_windows(L, 300, rng, latin=latin)
        hits = 0
        best = -99.0
        for w in W:
            pm, _, _, _ = S.grid_pmax(w, pan)
            m = float(pm.max())
            best = max(best, m)
            hits += int(m >= bars[L])
        node[lang] = {"power": round(hits / 300.0, 4), "best_pmax": round(best, 3)}
    node["verdict_capable"] = bool(node["EN"]["power"] >= S.POWER_FLOOR)
    out["nodes"][str(L)] = node
    print(L, node, flush=True)

json.dump(out, open("plant_power.json", "w"), indent=1)
print("all_passed(glue):", plant["passed"])
