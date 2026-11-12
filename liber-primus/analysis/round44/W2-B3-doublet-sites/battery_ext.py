"""R44 / W2-B3 step 3 — PREREG Addendum 2: extended battery null (D=10,000) -> battery_ext.json.

Battery statistics only; no panel scoring; statistics, alpha and decision rule unchanged.
Fresh disjoint seed block.  Also: non-registered descriptive context for T7 (Spearman ac1,
leave-one-pair-out Pearson sensitivity, block-rate profile).
"""
import json
import random as pyrandom
import time

import numpy as np

import b3lib as B

D = 10000
t0 = time.time()
xU, pgU = B.stream_pages("U")
nU = len(xU)
obs = B.battery_stats(xU, pgU, B.N_PAGES_U, nU)

keys = ("T1_ks", "T2_gapcv2", "T3_chi2_mod29", "T4_chi2_mod60", "T6_dispersion", "T7_gap_ac1")
null = {k: np.empty(D) for k in keys}
vcs = np.empty((D, B.N))
for j in range(D):
    y = B.site_matched_shuffle(xU, pyrandom.Random(B.SEED + 200000 + j), target=86)
    st = B.battery_stats(y, pgU, B.N_PAGES_U, nU)
    for k in keys:
        null[k][j] = st[k]
    vcs[j] = st["T5_valuecounts"]
    if (j + 1) % 1000 == 0:
        print("draw", j + 1, "%.0fs" % (time.time() - t0), flush=True)

vc_mean = vcs.mean(axis=0)
t5_null = (((vcs - vc_mean) ** 2) / np.maximum(vc_mean, 1e-9)).sum(axis=1)
t5_obs = float(((np.asarray(obs["T5_valuecounts"], dtype=float) - vc_mean) ** 2
                / np.maximum(vc_mean, 1e-9)).sum())

tests = {
    "T1_ks": (obs["T1_ks"], B.addone_upper(null["T1_ks"], obs["T1_ks"]), "one-sided"),
    "T2_gapcv2": (obs["T2_gapcv2"], B.addone_two(null["T2_gapcv2"], obs["T2_gapcv2"]), "two-sided"),
    "T3_chi2_mod29": (obs["T3_chi2_mod29"],
                      B.addone_upper(null["T3_chi2_mod29"], obs["T3_chi2_mod29"]), "one-sided"),
    "T4_chi2_mod60": (obs["T4_chi2_mod60"],
                      B.addone_upper(null["T4_chi2_mod60"], obs["T4_chi2_mod60"]), "one-sided"),
    "T5_valuecount_chi2": (t5_obs, B.addone_upper(t5_null, t5_obs), "one-sided"),
    "T6_dispersion": (obs["T6_dispersion"],
                      B.addone_two(null["T6_dispersion"], obs["T6_dispersion"]), "two-sided"),
    "T7_gap_ac1": (obs["T7_gap_ac1"], B.addone_two(null["T7_gap_ac1"], obs["T7_gap_ac1"]), "two-sided"),
}
fired = sorted(k for k, v in tests.items() if v[1] <= B.BATT_ALPHA)

# ---- non-registered descriptive context for T7
p = B.sites(xU)
g = np.diff(p).astype(float)


def _pearson_ac1(gg):
    return float(np.corrcoef(gg[:-1], gg[1:])[0, 1])


def _spearman_ac1(gg):
    r = np.argsort(np.argsort(gg)).astype(float)
    return float(np.corrcoef(r[:-1], r[1:])[0, 1])


loo = [_pearson_ac1(np.delete(g, [i, i + 1] if i + 1 < len(g) else [i]))
       for i in range(len(g) - 1)]
# crude per-region rate profile: doublets per 1000-rune block
blocks = np.bincount((p // 1000).astype(int))
ctx = {"pearson_ac1": _pearson_ac1(g), "spearman_ac1": _spearman_ac1(g),
       "loo_pearson_min": float(np.min(loo)), "loo_pearson_max": float(np.max(loo)),
       "gap_sorted_desc_top8": sorted(g.tolist(), reverse=True)[:8],
       "doublets_per_1000rune_block": blocks.tolist(),
       "null_T7_mean": float(null["T7_gap_ac1"].mean()),
       "null_T7_sd": float(null["T7_gap_ac1"].std()),
       "null_T7_max": float(null["T7_gap_ac1"].max()),
       "obs_T7_z_vs_null": float((obs["T7_gap_ac1"] - null["T7_gap_ac1"].mean())
                                 / null["T7_gap_ac1"].std())}

out = {"D": D, "alpha_per_test": B.BATT_ALPHA,
       "tests": {k: {"stat": round(v[0], 5), "p": round(v[1], 6), "side": v[2]}
                 for k, v in tests.items()},
       "fired": fired,
       "verdict": ("D-01-RESIDUE-STRUCTURED (LOUD FLAG)" if fired
                   else "UNIFORM — D-01 Bernoulli-slip model HARDENS"),
       "T7_descriptive_context_nonregistered": ctx,
       "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open("battery_ext.json", "w"), indent=1)
print("EXTENDED BATTERY", out["verdict"])
print({k: out["tests"][k]["p"] for k in out["tests"]})
print("ctx", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in ctx.items()})
