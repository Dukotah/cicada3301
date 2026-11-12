"""R44 / W2-B3 step 0 — null build -> nulls.json.

F1 (binding, matched): 1,000 site_matched_shuffle draws (PREREG Addendum 1) of the unsolved stream (target 86) and of the
full canon (target 89); per draw the IDENTICAL glue extracts sites, builds the 4 channels,
runs the 116-map grid; pmax pooled per channel.  F2 (SEL conservatism cross-check, W2-A1
family): 1,000 sorted uniform canon selections at each real channel L, same grid.  Bar of
record per channel = max(F1 POT bar, F2 POT bar) at N=928, alpha=0.01 (PREREG).  Battery
null: the 7 statistics over the same 1,000 U draws.  Only surrogates are scored here.
"""
import json
import random as pyrandom
import time

import numpy as np

import b3lib as B

D = B.D_NULL
pan = B.panel()
t0 = time.time()

xU, pgU = B.stream_pages("U")
xC, pgC = B.stream_pages("C")
nU, nC = len(xU), len(xC)

# real channel lengths (pinned census: 86/89 sites)
REAL_L = {"dblvals_U": 86, "gapsmod29_U": 85, "posmod29_U": 86, "pagecounts_U": 55,
          "dblvals_C": 89, "gapsmod29_C": 88, "posmod29_C": 89, "pagecounts_C": 57}

f1 = {k: [] for k in REAL_L}
batt = {k: [] for k in ("T1_ks", "T2_gapcv2", "T3_chi2_mod29", "T4_chi2_mod60",
                        "T6_dispersion", "T7_gap_ac1")}
vcs = []

for j in range(D):
    for tag, x, pg, npg, tgt in (("U", xU, pgU, B.N_PAGES_U, 86), ("C", xC, pgC, 57, 89)):
        y = B.site_matched_shuffle(x, pyrandom.Random(B.SEED + 10000 * (tag == "C") + j), target=tgt)
        ch, p, g, cnt = B.channels(y, pg, npg)
        for cname in ("dblvals", "gapsmod29", "posmod29", "pagecounts"):
            s = ch[cname]
            if len(s) < 3:
                continue
            pm, _, _, _ = B.grid_pmax(s, pan)
            f1[cname + "_" + tag].extend(pm.tolist())
        if tag == "U":
            st = B.battery_stats(y, pg, npg, len(x))
            for k in batt:
                batt[k].append(st[k])
            vcs.append(st["T5_valuecounts"])
    if (j + 1) % 100 == 0:
        print("F1 draw", j + 1, "of", D, "%.1fs" % (time.time() - t0), flush=True)

# T5: chi2 of each draw's value-count vector against the null mean vector
VC = np.stack(vcs).astype(float)
vc_mean = VC.mean(axis=0)
t5_null = (((VC - vc_mean) ** 2) / np.maximum(vc_mean, 1e-9)).sum(axis=1)

# F2 SEL family at each real L
rng = np.random.default_rng(B.SEED + 5)
f2 = {}
for L in sorted(set(REAL_L.values())):
    pm_all = np.empty(D * 116)
    for i in range(D):
        posn = np.sort(rng.choice(nC, size=L, replace=False))
        pm, _, _, _ = B.grid_pmax(xC[posn], pan)
        pm_all[i * 116:(i + 1) * 116] = pm
    f2[L] = pm_all
    print("F2 SEL L =", L, "done %.1fs" % (time.time() - t0), flush=True)

bars = {}
for k, L in REAL_L.items():
    u1, p1, b1, n1 = B.pot_fit(f1[k])
    bar1 = B.pot_bar(u1, p1, b1)
    u2, p2, b2, n2 = B.pot_fit(f2[L])
    bar2 = B.pot_bar(u2, p2, b2)
    bars[k] = {"L": L, "n_null_F1": len(f1[k]),
               "F1": {"u": round(u1, 4), "p_u": round(p1, 5), "beta": round(b1, 5),
                      "n_exceed": n1, "bar": round(bar1, 4),
                      "emp_max": round(float(np.max(f1[k])), 4)},
               "F2_SEL": {"u": round(u2, 4), "p_u": round(p2, 5), "beta": round(b2, 5),
                          "n_exceed": n2, "bar": round(bar2, 4),
                          "emp_max": round(float(np.max(f2[L])), 4)},
               "bar_of_record": round(max(bar1, bar2), 4)}
    print(k, bars[k]["bar_of_record"], flush=True)

out = {"seed": B.SEED, "D": D, "N_budget": B.N_BUDGET, "alpha": B.ALPHA,
       "bars": bars,
       "battery_null_U": {**{k: [float(v) for v in a] for k, a in batt.items()},
                          "T5_chi2": [float(v) for v in t5_null],
                          "vc_mean": [float(v) for v in vc_mean]},
       "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open("nulls.json", "w"), indent=1)
print("DONE", {k: v["bar_of_record"] for k, v in bars.items()}, out["elapsed_s"], flush=True)
