"""R45 / T1 — PREREG Addendum 2, E0b fragility (DESCRIPTIVE) -> fragility.json."""
import json
import numpy as np
import t1lib as L

D = L.load(); ev = D["ev"]; T = D["T"]
null = np.array(json.load(open("plants.json"))["null"]["S1"])
def p(v): return L.addone_two(null, v)
rows = []
evs = set(ev.tolist())
for t in range(0, T, 5):
    if t in evs or (t - 1) in evs or (t + 1) in evs:
        continue
    e = np.sort(np.append(ev, t))
    r = L.ac1(np.diff(e).astype(float))
    rows.append((t, r))
rows = np.array(rows)
i = int(np.argmin(rows[:, 1]))
breakers = rows[[p(v) > 0.01 for v in rows[:, 1]]]
def runs(pos):
    out = []
    for t in pos:
        if out and t - out[-1][1] <= 5: out[-1][1] = int(t)
        else: out.append([int(t), int(t)])
    return out
res = {"label": "DESCRIPTIVE (Addendum 2)", "obs_T7": L.ac1(np.diff(ev).astype(float)),
       "min_T7_after_one_insertion": float(rows[i, 1]), "at_pair": int(rows[i, 0]),
       "p_of_min": p(rows[i, 1]),
       "n_positions_tested": int(len(rows)),
       "n_positions_where_one_insert_pushes_p_above_0.01": int(len(breakers)),
       "breaker_intervals": runs(breakers[:, 0].astype(int).tolist())}
json.dump(res, open("fragility.json", "w"), indent=1)
print(json.dumps(res))
