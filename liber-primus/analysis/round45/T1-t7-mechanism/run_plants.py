"""R45 / T1 step 1 — M0 null (D=2000) + Stage-A plants + gate -> plants.json.
No real-data statistic is computed here (the census halt-check only verifies the event set)."""
import json
import time

import numpy as np

import t1lib as L

D = L.load()
S = L.Struct(D)
t0 = time.time()
rng = np.random.default_rng(45001)

DNULL = 2000
NPL = 200


def summ(r):
    return {"choice": r["choice"], "S1": r["S1"], "S2": r["S2"], "S3": r["S3"],
            "fano": r["fano"], "S5": r["S5"]}


null = []
for j in range(DNULL):
    null.append(summ(L.fit_all(L.sim("M0", S, rng), S)))
    if (j + 1) % 500 == 0:
        print("null", j + 1, "%.0fs" % (time.time() - t0), flush=True)

F = np.array([n["fano"] for n in null])
fmu, fsd = F.mean(axis=0), F.std(axis=0)


def s4(f):
    return float(np.max((np.asarray(f) - fmu) / fsd))


for n in null:
    n["S4"] = s4(n["fano"])
NS = {s: np.array([n[s] for n in null]) for s in ("S1", "S2", "S3", "S4", "S5")}
TWO = {"S1", "S2"}


def pvals(r):
    return {s: (L.addone_two if s in TWO else L.addone_upper)(NS[s], r[s]) for s in NS}


plants = {}
order = [("M2", 0.8), ("M1c", 0.8)] + [(m, sl) for sl in (0.5, 0.8)
                                        for m in ("M1a", "M1b", "M1c", "M2", "M3a", "M3b", "M4")
                                        if not (sl == 0.8 and m in ("M2", "M1c"))] + [("M0", None)]
kill_checked = False
for m, sl in order:
    rows = []
    for j in range(NPL):
        r = summ(L.fit_all(L.sim(m, S, rng, sl=sl), S))
        r["S4"] = s4(r["fano"])
        r["p"] = pvals(r)
        rows.append(r)
    key = "%s@%s" % (m, sl)
    pw = {a: {s: float(np.mean([x["p"][s] <= a for x in rows])) for s in NS} for a in (0.05, 0.01)}
    conf = {mm: sum(x["choice"] == mm for x in rows) for mm in L.MODELS}
    plants[key] = {"model": m, "sigma_L": sl, "n": NPL, "power": pw, "choice_counts": conf,
                   "S1_q": np.quantile([x["S1"] for x in rows], [0.05, 0.5, 0.95]).tolist(),
                   "S1_frac_ge_0.380": float(np.mean([x["S1"] >= 0.380 for x in rows]))}
    print(key, "pow@.01", pw[0.01], conf, "%.0fs" % (time.time() - t0), flush=True)
    if not kill_checked and "M2@0.8" in plants and "M1c@0.8" in plants:
        kill_checked = True
        dead = all(plants[k]["power"][0.05][s] < 0.2 for k in ("M2@0.8", "M1c@0.8") for s in NS)
        plants["_kill_check"] = {"killed": bool(dead)}
        print("Q5 kill check:", "KILL" if dead else "continue", flush=True)
        if dead:
            break

gate = {"S3_power_M2_0.8_at_0.01": plants["M2@0.8"]["power"][0.01]["S3"],
        "S3_false_fire_M0_at_0.01": plants.get("M0@None", {}).get("power", {}).get(0.01, {}).get("S3")}
gate["pass"] = bool(gate["S3_power_M2_0.8_at_0.01"] >= 0.5 and
                    gate["S3_false_fire_M0_at_0.01"] is not None and
                    gate["S3_false_fire_M0_at_0.01"] <= 0.02)
print("GATE", gate, flush=True)

json.dump({"D_null": DNULL, "n_per_plant": NPL, "seed": 45001,
           "fano_null_mu": fmu.tolist(), "fano_null_sd": fsd.tolist(),
           "null": {s: NS[s].tolist() for s in NS},
           "null_choice_counts": {mm: sum(n["choice"] == mm for n in null) for mm in L.MODELS},
           "plants": plants, "gate": gate, "elapsed_s": round(time.time() - t0, 1)},
          open("plants.json", "w"), indent=1)
print("DONE %.0fs" % (time.time() - t0))
