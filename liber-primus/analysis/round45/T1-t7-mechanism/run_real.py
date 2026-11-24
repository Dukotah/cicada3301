"""R45 / T1 step 2 — real-data fits, Stage-B parametric bootstrap, held-out, change-point
coincidence, descriptives -> results.json.  Requires plants.json (gate) from run_plants.py."""
import json
import math
import os
import time

import numpy as np

import t1lib as L

np.seterr(divide="ignore")
P = json.load(open("plants.json"))
D = L.load()
S = L.Struct(D)
T = S.T
ev = D["ev"]
t0 = time.time()
rng = np.random.default_rng(45002)
out = {"gate": P["gate"]}

# ------------------------------------------------------------------ 1. real fit + detection p-values
R = L.fit_all(ev, S, keep_detail=True)
fmu, fsd = np.array(P["fano_null_mu"]), np.array(P["fano_null_sd"])
R["S4"] = float(np.max((np.array(R["fano"]) - fmu) / fsd))
NS = {s: np.array(v) for s, v in P["null"].items()}
pv = {s: (L.addone_two if s in ("S1", "S2") else L.addone_upper)(NS[s], R[s]) for s in NS}
out["detection"] = {"obs": {s: R[s] for s in NS}, "fano_raw": dict(zip(map(str, L.FANO_W), R["fano"])),
                    "p": pv, "D_null": P["D_null"],
                    "S3_confirmed_p_le_0.01": bool(pv["S3"] <= 0.01),
                    "S3_verdict_capable": bool(P["gate"]["pass"])}
print("detection", out["detection"]["obs"], pv, flush=True)

bmin = min(R["bic"].values())
w = {m: math.exp(-0.5 * (R["bic"][m] - bmin)) for m in L.MODELS}
ws = sum(w.values())
out["models"] = {m: {"logL": R["L"][m], "k": R["k"][m], "BIC": R["bic"][m],
                     "dBIC": R["bic"][m] - bmin, "BIC_weight": w[m] / ws} for m in L.MODELS}
out["best_bic"] = R["choice"]
out["params"] = R["par"]
out["m1c_by_K"] = [{"K": K, "logL": R["m1c_all"][K][0], "cps": R["m1c_all"][K][1],
                    "BIC": -2 * R["m1c_all"][K][0] + (2 * K + 1) * L.LN_NEV} for K in range(0, L.KMAX + 1)]
out["hmm_ll_by_sigma"] = dict(zip(map(str, L.SIGMAS.tolist()), R["hmm_ll"]))
print("BIC", {m: round(v["dBIC"], 2) for m, v in out["models"].items()}, flush=True)

# ------------------------------------------------------------------ 2. Stage B parametric bootstrap
par = R["par"]
cnt_ch = np.histogram(ev, bins=S.e_chap)[0] / np.diff(S.e_chap)
cnt_se = np.histogram(ev, bins=S.e_sect)[0] / np.diff(S.e_sect)
cps = par["M1c_cps"]
e1c = np.array([0] + cps + [T])
r1c = np.histogram(ev, bins=e1c)[0] / np.diff(e1c)
spec = {"M0": None, "M1a": cnt_ch, "M1b": cnt_se, "M1c": (cps, r1c), "M2": par["M2_sigma"],
        "M3a": par["M3a"][1], "M3b": par["M3b"][1], "M4": par["M4"][0]}
NB = 200
conf = {}
stageB = {}
for m in L.MODELS:
    rows = []
    for j in range(NB):
        e = L.sim(m, S, rng, par=spec[m]) if m != "M0" else L.sim("M0", S, rng)
        r = L.fit_all(e, S)
        rows.append((r["choice"], r["S1"], r["S3"]))
    conf[m] = {mm: sum(x[0] == mm for x in rows) for mm in L.MODELS}
    s1 = np.array([x[1] for x in rows])
    s3 = np.array([x[2] for x in rows])
    stageB[m] = {"choice_counts": conf[m],
                 "S1_quantiles_5_50_95": np.quantile(s1, [0.05, 0.5, 0.95]).tolist(),
                 "S1_frac_ge_obs": float(np.mean(s1 >= R["S1"])),
                 "S3_power_at_0.01": float(np.mean([L.addone_upper(NS["S3"], v) <= 0.01 for v in s3])),
                 "S1_power_at_0.01": float(np.mean([L.addone_two(NS["S1"], v) <= 0.01 for v in s1]))}
    print("StageB", m, conf[m], stageB[m]["S1_quantiles_5_50_95"], "%.0fs" % (time.time() - t0), flush=True)
C = np.array([[conf[a][b] for b in L.MODELS] for a in L.MODELS], float)
recall = {m: C[i, i] / C[i].sum() for i, m in enumerate(L.MODELS)}
precision = {m: (C[i, i] / C[:, i].sum() if C[:, i].sum() > 0 else float("nan")) for i, m in enumerate(L.MODELS)}
out["stageB"] = {"n_per_row": NB, "spec": {k: (np.asarray(v).tolist() if not isinstance(v, tuple)
                                                else [v[0], v[1].tolist()]) for k, v in spec.items()},
                 "rows": stageB, "confusion_rows_planted_cols_chosen": C.tolist(), "order": L.MODELS,
                 "recall": recall, "precision_uniform_prior": precision}

# family-level confusion (heterogeneity families)
FAM = {"M0": "stationary", "M1a": "sessions-structural", "M1b": "sessions-structural",
       "M1c": "sessions-free", "M2": "smooth-drift", "M3a": "covariate", "M3b": "covariate",
       "M4": "renewal"}
fams = sorted(set(FAM.values()))
CF = np.zeros((len(fams), len(fams)))
for i, a in enumerate(L.MODELS):
    for j, b in enumerate(L.MODELS):
        CF[fams.index(FAM[a]), fams.index(FAM[b])] += C[i, j]
out["stageB"]["family_confusion"] = {"order": fams, "matrix": CF.tolist()}

# ------------------------------------------------------------------ 3. verdict per PREREG threshold 3
best = R["choice"]
srt = sorted(L.MODELS, key=lambda m: R["bic"][m])
runner = srt[1]
verdict = {}
for m in L.MODELS:
    d = R["bic"][m] - bmin
    if m == best and recall[m] >= 0.5 and precision[m] >= 0.6:
        v = "favoured"
        if R["bic"][runner] - bmin >= 6 and precision[m] >= 0.8:
            v = "decisive"
    elif d >= 10 and recall[m] >= 0.5:
        v = "disfavoured"
    else:
        v = "not separable at n=86"
    verdict[m] = v
out["verdict_per_model"] = verdict
print("verdicts", verdict, flush=True)

# M4 exclusion rule (threshold 5)
m4q = {k: P["plants"][k]["S1_q"][2] for k in P["plants"] if k.startswith("M4@")}
out["M4_exclusion"] = {"stageA_S1_q95": m4q, "stageB_S1_q95": stageB["M4"]["S1_quantiles_5_50_95"][2],
                       "excluded": bool(all(v < 0.380 for v in m4q.values()) and
                                        stageB["M4"]["S1_quantiles_5_50_95"][2] < 0.380)}

# ------------------------------------------------------------------ 4. held-out (2-fold, interleaved 500-pair blocks)
tt = np.arange(T)
SH = 100.0  # pseudo-exposure shrinkage for piecewise rates (held-out only)


def last_event_dist(evs):
    idx = np.searchsorted(evs, tt, side="left") - 1
    return np.where(idx >= 0, tt - evs[np.maximum(idx, 0)], tt + 1).astype(float)


DIST = last_event_dist(ev)


def ll_region(lam, mask):
    e = ev[mask[ev]]
    return float(np.log(lam[e]).sum() - lam[mask].sum())


def pw_lam(edges, train):
    k = np.histogram(ev[train[ev]], bins=edges)[0]
    cw = np.concatenate([[0], np.cumsum(train)])
    n = cw[edges[1:]] - cw[edges[:-1]]
    r0 = train[ev].sum() / train.sum()
    rate = (k + SH * r0) / (n + SH)
    return rate[L.piece_index(edges, T)]


def gamma_haz(d, k, th):
    from scipy.special import gammaincc
    lf = L._gamma_logpdf(d, k, th)
    sf = np.maximum(gammaincc(k, d / th), 1e-300)
    return np.exp(lf) / sf


heldout = {m: 0.0 for m in L.MODELS}
for f in (0, 1):
    test = ((tt // 500) % 2) == f
    train = ~test
    r0 = train[ev].sum() / train.sum()
    heldout["M0"] += ll_region(np.full(T, r0), test)
    heldout["M1a"] += ll_region(pw_lam(S.e_chap, train), test)
    heldout["M1b"] += ll_region(pw_lam(S.e_sect, train), test)
    c = L.m1c_fit(ev, S, w=train)
    Kb = int(np.argmin([-2 * c[K][0] + (2 * K + 1) * L.LN_NEV for K in range(0, L.KMAX + 1)]))
    heldout["M1c"] += ll_region(pw_lam(np.array([0] + c[Kb][1] + [T]), train), test)
    binmask = np.array([(((b * L.BIN) // 500) % 2) != f for b in range(S.nbin)], float)
    E = L.emissions(L.bin_counts(ev, S), S, mask=binmask)
    si = int(np.argmax(L.hmm_ll_all(E)))
    mlam, _ = L.hmm_smooth(E, si)
    heldout["M2"] += ll_region(np.repeat(mlam, L.BIN)[:T], test)
    for m, z in (("M3a", S.z3), ("M3b", S.z4)):
        _, a, b = L.m3_fit(ev, z, w=train)
        heldout[m] += ll_region(np.exp(a + b * z), test)
    best4 = (-np.inf, None)
    mg = T / len(ev)
    for k in L.KAP:
        for sc in L.SCF:
            th = mg / k * sc
            h = gamma_haz(DIST, k, th)
            v = ll_region(h, train)
            if v > best4[0]:
                best4 = (v, h)
    heldout["M4"] += ll_region(best4[1], test)
hb = max(heldout.values())
out["heldout"] = {"scheme": "2-fold, interleaved 500-pair blocks; piecewise rates shrunk with 100 pseudo-pairs at the train rate; M2 = HMM smoothing over masked bins; M4 = conditional-intensity gamma hazard",
                  "logL_test": heldout, "delta_vs_best": {m: v - hb for m, v in heldout.items()},
                  "delta_vs_M0": {m: v - heldout["M0"] for m, v in heldout.items()}}
print("heldout", {m: round(v - heldout["M0"], 2) for m, v in heldout.items()}, flush=True)

# ------------------------------------------------------------------ 5. where do the rate changes fall?
cps = par["M1c_cps"]
ps = D["page_starts"]
SETS = {"chapter_ends": list(S.e_chap[1:-1]), "section_ends": list(S.e_sect[1:-1]),
        "page_starts": list(S.e_page[1:-1]), "ten_dot_page_starts": [ps[36], ps[38], ps[49]]}
grid_in = S.grid[1:-1]


def mdist(pts, B):
    B = np.asarray(B)
    return float(np.mean([np.min(np.abs(B - p)) for p in pts]))


coinc = {}
for name, B in SETS.items():
    obs = mdist(cps, B)
    Barr = np.asarray(B)
    nd = np.array([np.mean(np.min(np.abs(Barr[None, :] - rng.choice(grid_in, len(cps), replace=False)[:, None]), axis=1))
                   for _ in range(10000)])
    p = float((1 + (nd <= obs).sum()) / 10001)
    coinc[name] = {"obs_mean_dist": obs, "null_median": float(np.median(nd)), "p_lower": p,
                   "fires_at_0.0025": bool(p <= 0.0025),
                   "per_cp_nearest": [[int(c), int(Barr[np.argmin(np.abs(Barr - c))])] for c in cps]}
out["changepoint_coincidence"] = {"K": len(cps), "cps": cps,
                                  "segment_rates_per_1000": (r1c * 1000).tolist(),
                                  "segment_counts": np.histogram(ev, bins=e1c)[0].tolist(),
                                  "sets": coinc}
print("coincidence", {k: (v["obs_mean_dist"], v["p_lower"]) for k, v in coinc.items()}, flush=True)

# ------------------------------------------------------------------ 6. descriptives
desc = {}
desc["chapter_rates_per_1000"] = [[int(a), int(b), int(k), round(1000 * k / (b - a), 2)] for a, b, k in
                                   zip(S.e_chap[:-1], S.e_chap[1:], np.histogram(ev, bins=S.e_chap)[0])]
desc["section_rates_per_1000"] = [[int(a), int(b), int(k), round(1000 * k / (b - a), 2)] for a, b, k in
                                   zip(S.e_sect[:-1], S.e_sect[1:], np.histogram(ev, bins=S.e_sect)[0])]
sig_i = par["M2_si"]
E = L.emissions(L.bin_counts(ev, S), S)
mlam, mlog = L.hmm_smooth(E, max(sig_i, 1))
desc["M2_profile_sigma_used"] = float(L.SIGMAS[max(sig_i, 1)])
desc["M2_posterior_mean_rate_per_1000_every_250"] = [round(1000 * float(mlam[i]), 2) for i in range(0, S.nbin, 10)]
gm = len(ev) / T
low = mlam < 0.6 * gm
runs = []
i = 0
while i < S.nbin:
    if low[i]:
        j = i
        while j < S.nbin and low[j]:
            j += 1
        runs.append([i * L.BIN, min(j * L.BIN, T), round(1000 * float(mlam[i:j].min()), 2)])
        i = j
    else:
        i += 1
desc["M2_low_rate_regions_lt_0.6x_mean"] = runs
g = np.diff(ev)
big = np.argsort(-g)[:6]
desc["largest_gaps"] = [[int(ev[i]), int(ev[i + 1]), int(g[i])] for i in big]
# approximate dot-diamond positions (descriptive only)
cen = json.load(open(os.path.join(L.LP, "analysis", "round44", "P1-red-ink", "census.json")))
dia = []
pl = np.diff(np.append(ps, 12956))
for b in cen["blocks"]:
    if b.get("n_dots") in (10, 13):
        img = int(b["img"])
        if img == 50 or img > 55:
            continue
        sg = img if img < 50 else img - 1
        yc = 0.5 * (b["bbox"][2] + b["bbox"][3])
        fr = min(max((yc - 687) / (2900 - 687), 0), 1)
        dia.append({"n_dots": b["n_dots"], "img": img, "segment": sg, "approx_rune": int(ps[sg] + fr * pl[sg])})
desc["dot_diamonds_approx"] = dia
desc["ten_dot_pages"] = {str(sg): {"start": int(ps[sg]), "len": int(pl[sg]),
                                   "doublets": int(((ev >= ps[sg]) & (ev < ps[sg] + pl[sg])).sum())}
                         for sg in (36, 38, 49)}
desc["numbered_list_region_8805_9229"] = int(((ev >= 8805) & (ev < 9229)).sum())
desc["note_solved_pages"] = "AN END / PARABLE (segments 55-56) are outside the 12,956-rune unsolved stream; the only solved-adjacent position is the stream end (12,956)."
out["descriptive"] = desc
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open("results.json", "w"), indent=1, default=float)
print("DONE %.0fs" % (time.time() - t0))
