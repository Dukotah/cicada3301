"""R45 / T1 — PREREG Addendum 1 (EXPLORATORY): E0 / E1 / E2 -> addendum.json."""
import itertools
import json
import math
import time

import numpy as np

import t1lib as L

D = L.load()
S = L.Struct(D)
T = S.T
ev = D["ev"]
t0 = time.time()
rng = np.random.default_rng(45003)
NEV = L.NEV
MEAN = NEV / T


def s1s3(e):
    e = np.sort(e)
    h = L.hmm_ll_all(L.emissions(L.bin_counts(e, S), S))
    return L.ac1(np.diff(e).astype(float)), float(h.max() - h[0])


# ---------------- E2 two-state switching model
COMBOS = list(itertools.product((1.5, 2, 3, 4, 6, 10), (0.3, 0.5, 0.7), (2, 4, 8, 16, 32)))
RLO = np.array([MEAN / (p * r + (1 - p)) for r, p, d in COMBOS])
RHI = np.array([r for r, p, d in COMBOS]) * RLO
PI = np.array([p for r, p, d in COMBOS])
DW = np.array([d for r, p, d in COMBOS], float)


def e2_lrt(e):
    k = L.bin_counts(np.sort(e), S)
    n = S.bin_len
    # switching: leave current state w.p. 1/d, go to stationary draw
    q = 1.0 / DW
    a = np.stack([1 - PI, PI], axis=1)            # (C,2) stationary init
    tot = np.zeros(len(COMBOS))
    lr = np.stack([np.log(RLO), np.log(RHI)], 1)
    rr = np.stack([RLO, RHI], 1)
    for b in range(S.nbin):
        if b > 0:
            stay = (1 - q)[:, None] * a
            a = stay + (q * a.sum(1))[:, None] * np.stack([1 - PI, PI], 1)
        em = k[b] * lr - rr * n[b]
        mx = em.max(1, keepdims=True)
        a = a * np.exp(em - mx)
        c = a.sum(1)
        tot += np.log(c) + mx[:, 0]
        a = a / c[:, None]
    l0 = L.ll0(e, T)
    j = int(np.argmax(tot))
    return float(tot[j] - l0), COMBOS[j]


def sim_e2(rng, rho=4.0, pi=0.5, dwell=12):
    rlo = 1.0
    st = rng.random() < pi
    lam = np.empty(S.nbin)
    for b in range(S.nbin):
        if b > 0 and rng.random() < 1.0 / dwell:
            st = rng.random() < pi
        lam[b] = rho if st else 1.0
    return L.draw_weighted(np.repeat(lam, L.BIN)[:T], rng)


out = {"label": "EXPLORATORY (PREREG Addendum 1) - cannot change any registered verdict"}

# ---------------- E0 descriptive: contributions to T7
g = np.diff(ev).astype(float)
x, y = g[:-1], g[1:]
cx, cy = x - x.mean(), y - y.mean()
den = math.sqrt((cx ** 2).sum() * (cy ** 2).sum())
contrib = cx * cy / den
order = np.argsort(-np.abs(contrib))
out["E0_top_contributions"] = [{"site_i": int(ev[i]), "gap_i": int(x[i]), "gap_i+1": int(y[i]),
                                "share_of_r": float(contrib[i])} for i in order[:10]]
out["E0_r_total"] = float(contrib.sum())
out["E0_r_from_top5"] = float(contrib[order[:5]].sum())
out["E0_r_without_top5"] = float(contrib.sum() - contrib[order[:5]].sum())
print("E0", out["E0_r_total"], out["E0_r_from_top5"], flush=True)

# ---------------- E2 real + null + plant
obs_e2, comb = e2_lrt(ev)
null_e2 = []
for j in range(2000):
    null_e2.append(e2_lrt(L.sim("M0", S, rng))[0])
null_e2 = np.array(null_e2)
p_e2 = float((1 + (null_e2 >= obs_e2).sum()) / 2001)
crit = np.quantile(null_e2, 0.99)
pl = np.array([e2_lrt(sim_e2(rng))[0] for _ in range(500)])
out["E2"] = {"obs_LRT": obs_e2, "best_combo_rho_pi_dwellbins": comb, "p": p_e2,
             "null_q99": float(crit), "plant_power_at_0.01": float(np.mean(pl > crit))}
print("E2", out["E2"], "%.0fs" % (time.time() - t0), flush=True)

# ---------------- E1 discordance
s1o, s3o = s1s3(ev)
out["E1_obs"] = {"S1": s1o, "S3": s3o}


def joint(gen, n):
    hit_s1 = hit = 0
    s3zero = 0
    for _ in range(n):
        a, b = s1s3(gen())
        hit_s1 += a >= 0.380
        s3zero += b <= 1e-9
        hit += (a >= 0.380) and (b <= 1e-9)
    return {"n": n, "P_S1_ge_obs": hit_s1 / n, "P_S3_zero": s3zero / n, "P_joint": hit / n}


E1 = {"M0": joint(lambda: L.sim("M0", S, rng), 10000)}
print("E1 M0", E1["M0"], "%.0fs" % (time.time() - t0), flush=True)
for m in ("M1a", "M1c", "M2"):
    for sl in (0.5, 0.8):
        E1["%s@%s" % (m, sl)] = joint(lambda: L.sim(m, S, rng, sl=sl), 500)
        print("E1", m, sl, E1["%s@%s" % (m, sl)], "%.0fs" % (time.time() - t0), flush=True)
E1["E2plant"] = joint(lambda: sim_e2(rng), 500)
p0 = max(E1["M0"]["P_joint"], 0.5 / 10000)
for k, v in E1.items():
    v["LR_vs_M0_joint"] = v["P_joint"] / p0 if k != "M0" else 1.0
out["E1"] = E1
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open("addendum.json", "w"), indent=1, default=float)
print("DONE %.0fs" % (time.time() - t0), flush=True)
