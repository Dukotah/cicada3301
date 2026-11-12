"""R44 / W2-B3 step 2 — THE REAL READS -> results.json.

8 real channel streams x 116 maps vs the nulls.json bars of record (N=928, alpha=0.01),
plus the 7-statistic uniformity battery on U86 (family alpha 0.01, Bonferroni /7).
Gate order honoured: nulls.py and plant_gate.py have both run (run.log).
"""
import json
import sys
import time

import numpy as np

import b3lib as B

sys.path.insert(0, B.os.path.join(B.LP, "analysis", "round34", "I1-v3-null"))
from bars_v3 import bar_v3  # noqa: E402

pan = B.panel()
t0 = time.time()
nulls = json.load(open("nulls.json"))
bars = nulls["bars"]
nb = nulls["battery_null_U"]
plants = json.load(open("plants.json"))

POWER = {"dblvals_U": plants["classes"]["PLANT-V"]["power"],
         "gapsmod29_U": plants["classes"]["PLANT-G"]["power"],
         "posmod29_U": plants["classes"]["PLANT-P"]["power"],
         "pagecounts_U": plants["classes"]["PLANT-C"]["power"]}
POWER.update({k.replace("_U", "_C"): v for k, v in POWER.items()})  # same construction/L+3

out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "N_real": 0, "channels": {}, "battery": {},
       "bars_v3_free_120_N928_crosscheck_nonbinding": round(bar_v3(B.N_BUDGET, 120, "free"), 4)}

TRANS = ["F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J", "EO", "P", "X", "S",
         "T", "B", "E", "M", "L", "NG", "OE", "D", "A", "AE", "Y", "IA", "EA"]

crossers = []
for tag in ("U", "C"):
    x, pg = B.stream_pages(tag)
    npg = B.N_PAGES_U if tag == "U" else 57
    ch, p, g, cnt = B.channels(x, pg, npg)
    if tag == "U":
        real_sites = {"positions_first_rune": p.tolist(), "gaps": g.tolist(),
                      "doubled_values": ch["dblvals"].tolist(),
                      "doubled_translit": "".join(TRANS[v] for v in ch["dblvals"]),
                      "pagecounts": cnt.tolist()}
    for cname in ("dblvals", "gapsmod29", "posmod29", "pagecounts"):
        key = cname + "_" + tag
        s = ch[cname]
        pm_best, meta, full, deg = B.best_reading(s, pan)
        out["N_real"] += 116
        bar = bars[key]["bar_of_record"]
        row = {"L": int(len(s)), "best_pmax": round(pm_best, 4), "bar": bar,
               "best_map": meta, "degenerate_stream": deg,
               "power_at_L": POWER[key],
               "best_full": {k: (round(v, 4) if isinstance(v, float) else v)
                             for k, v in full.items() if k in
                             ("n", "en", "pmax", "preg", "pmax_ne", "pcon", "ioc",
                              "mds", "h2", "zl", "degenerate")},
               "crosses": bool((not deg) and pm_best >= bar)}
        if row["crosses"]:
            crossers.append(key)
        if deg:
            row["verdict"] = "measured-only (degenerate stream, R38 guard)"
        elif row["crosses"]:
            row["verdict"] = "FLAGGED-FOR-ORACLE"
        elif POWER[key] >= B.POWER_FLOOR:
            row["verdict"] = "NEGATIVE at measured power %.2f" % POWER[key]
        else:
            row["verdict"] = "measured-only (power %.2f < %.2f)" % (POWER[key], B.POWER_FLOOR)
        out["channels"][key] = row
        print(key, row["best_pmax"], "vs", bar, row["verdict"], flush=True)

out["real_sites_U86"] = real_sites

# ---------------- battery on U86
xU, pgU = B.stream_pages("U")
st = B.battery_stats(xU, pgU, B.N_PAGES_U, len(xU))
vc_mean = np.asarray(nb["vc_mean"], dtype=float)
t5 = float(((np.asarray(st["T5_valuecounts"], dtype=float) - vc_mean) ** 2
            / np.maximum(vc_mean, 1e-9)).sum())
tests = {
    "T1_ks": (st["T1_ks"], B.addone_upper(nb["T1_ks"], st["T1_ks"]), "one-sided"),
    "T2_gapcv2": (st["T2_gapcv2"], B.addone_two(nb["T2_gapcv2"], st["T2_gapcv2"]), "two-sided"),
    "T3_chi2_mod29": (st["T3_chi2_mod29"],
                      B.addone_upper(nb["T3_chi2_mod29"], st["T3_chi2_mod29"]), "one-sided"),
    "T4_chi2_mod60": (st["T4_chi2_mod60"],
                      B.addone_upper(nb["T4_chi2_mod60"], st["T4_chi2_mod60"]), "one-sided"),
    "T5_valuecount_chi2": (t5, B.addone_upper(nb["T5_chi2"], t5), "one-sided"),
    "T6_dispersion": (st["T6_dispersion"],
                      B.addone_two(nb["T6_dispersion"], st["T6_dispersion"]), "two-sided"),
    "T7_gap_ac1": (st["T7_gap_ac1"], B.addone_two(nb["T7_gap_ac1"], st["T7_gap_ac1"]), "two-sided"),
}
fired = {k: v for k, v in tests.items() if v[1] <= B.BATT_ALPHA}
out["battery"] = {"alpha_per_test": B.BATT_ALPHA, "D": nulls["D"],
                  "power_T1_from_PLANT_G": plants["classes"]["PLANT-G"]["battery_T1_fire_rate"],
                  "tests": {k: {"stat": round(v[0], 5), "p": round(v[1], 6), "side": v[2]}
                            for k, v in tests.items()},
                  "fired": sorted(fired),
                  "verdict": ("D-01-RESIDUE-STRUCTURED (LOUD FLAG)" if fired
                              else "UNIFORM — D-01 Bernoulli-slip model HARDENS")}
out["crossers"] = crossers
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open("results.json", "w"), indent=1)
print("BATTERY", out["battery"]["verdict"],
      {k: out["battery"]["tests"][k]["p"] for k in out["battery"]["tests"]}, flush=True)
print("CROSSERS", crossers, "N_real", out["N_real"], flush=True)
