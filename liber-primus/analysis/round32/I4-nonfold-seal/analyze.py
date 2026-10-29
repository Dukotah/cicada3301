"""analyze.py -- ROC / catch-x-false-reject for the non-fold seal designs, from cached feat_*.json.
Designs frozen in PREREG.md. Tuning split = tune_*, held-out = held_* (+spread for register axis).
All statistics are oracle-free; truth labels are used only to score catch / false-reject."""
import json
import math
import os
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
N = 240
EN_FAMILY = ("EN_MODERN", "EN_KJV")
HEADS = [24, 32, 48, 60, 80, 96, 120, 144, 168, 192, 216]
TAUS = [0.80, 0.85, 0.90, 0.95, 0.98, 1.00]
TAU_N = [0.90, 0.92, 0.94, 0.96, 0.98, 1.00]
KS = [2, 3, 4, 5, 6, 7, 8]


def load(n):
    return json.load(open(os.path.join(HERE, f"feat_{n}.json")))


D = {n: load(n) for n in ("tune_nv", "tune_en", "held_nv", "held_en", "spread")}


def bounds(n, k):
    k = max(2, min(k, n))
    base, rem = divmod(n, k)
    s = 0
    out = []
    for i in range(k):
        ln = base + (1 if i < rem else 0)
        out.append((s, s + ln))
        s += ln
    return out


def cutv(c, h):
    return c["cut_rec"].get(str(h))


def fold_stat(c, k, rule="min"):
    r = [cutv(c, hi) for lo, hi in bounds(N, k) if N - hi >= 3]
    r = [x for x in r if x is not None]
    if not r:
        return 0.0
    return min(r) if rule == "min" else sum(r) / len(r)


def multihead(c, h0):
    r = [cutv(c, h) for h in HEADS if h >= h0]
    r = [x for x in r if x is not None]
    return min(r) if r else 0.0


def pick(pop, label, streams=None):
    return [c for c in D[pop]["cases"] if c["label"] == label and (streams is None or c["stream"] in streams)]


SETS = {
    "H_t": pick("tune_nv", "halluc"), "G_t": pick("tune_en", "genuine"),
    "H_h": pick("held_nv", "halluc"), "G_h": pick("held_en", "genuine"),
    "R_t": pick("tune_nv", "genuine"),                 # EN_NOVOWEL correct-key genuine, tuning side
    "R_nv_h": pick("held_nv", "genuine"),
    "R_sp_h": pick("spread", "genuine"),
}
SETS["R_h"] = SETS["R_nv_h"] + SETS["R_sp_h"]          # pooled register-spread genuine, held-out


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - r) / d, 3), round((c + r) / d, 3)]


def rates(acc, H, G, R):
    caught = sum(1 for c in H if not acc(c))
    rej = sum(1 for c in G if not acc(c))
    rr = sum(1 for c in R if not acc(c))
    return {"catch": caught, "catch_n": len(H), "catch_rate": round(caught / len(H), 3) if H else None,
            "fr": rej, "fr_n": len(G), "fr_rate": round(rej / len(G), 3) if G else None,
            "reg_fr": rr, "reg_n": len(R), "reg_fr_rate": round(rr / len(R), 3) if R else None}


def evalcell(acc):
    return {"tuning": rates(acc, SETS["H_t"], SETS["G_t"], SETS["R_t"]),
            "heldout": rates(acc, SETS["H_h"], SETS["G_h"], SETS["R_h"])}


def is_en(c):
    return c["feat"]["preg_name"] in EN_FAMILY


# ---------------------------------------------------------------- designs: {cell: (acc, params)}
def design_fold_control():
    return {f"fold_k{k}_min_tau{t}": ((lambda c, k=k, t=t: fold_stat(c, k, "min") >= t), {"k": k, "tau": t})
            for k in KS for t in TAUS}


def design_D1():
    return {f"cut_h{h}_tau{t}": ((lambda c, h=h, t=t: (cutv(c, h) or 0.0) >= t), {"head": h, "tau": t})
            for h in HEADS for t in TAUS}


def design_D1b():
    return {f"multihead_h0{h0}_tau{t}": ((lambda c, h0=h0, t=t: multihead(c, h0) >= t), {"h0": h0, "tau": t})
            for h0 in HEADS for t in TAUS}


def design_D2():
    return {f"perreg_k{k}_tauN{tn}": ((lambda c, k=k, tn=tn: fold_stat(c, k, "min") >= (0.90 if is_en(c) else tn)),
                                      {"k": k, "tau_N": tn})
            for k in KS for tn in TAU_N}


# ---------------------------------------------------------------- D3 learned gate
def fvec(c, aware):
    f = c["feat"]
    v = []
    for k in (3, 4, 5, 6, 7, 8):
        v += [fold_stat(c, k, "min"), fold_stat(c, k, "mean")]
    v += [cutv(c, 60) or 0, cutv(c, 120) or 0, cutv(c, 176) or 0]
    v += [c["cons"]["ms8"], c["cons"]["pair"], c["cons"]["bw100"]]
    v += [c["headp"]["64"], c["headp"]["120"], c["headp"]["180"]]
    v += [f["pmax"], f["ioc"], f["mds"], f["h2"], f["zl"], c["n_skips"], c["n_unexpl"], c["beam_score"]]
    if aware:
        v += [1.0 if is_en(c) else 0.0, f["en"], f["pmax_ne"], f["pcon"]] + list(f["z"])
    return np.array(v, float)


def fit_lr(X, y, lam, iters=40):
    n, d = X.shape
    w = np.zeros(d + 1)
    Xb = np.hstack([X, np.ones((n, 1))])
    reg = lam * np.eye(d + 1)
    reg[-1, -1] = 0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(Xb @ w, -30, 30)))
        g = Xb.T @ (p - y) + reg @ w
        Hm = Xb.T @ (Xb * (p * (1 - p))[:, None]) + reg + 1e-6 * np.eye(d + 1)
        w = w - np.linalg.solve(Hm, g)
    return w


def predict(w, X):
    return 1 / (1 + np.exp(-np.clip(np.hstack([X, np.ones((len(X), 1))]) @ w, -30, 30)))


def run_D3(aware):
    tr = SETS["H_t"] + SETS["G_t"]
    y = np.array([0.0] * len(SETS["H_t"]) + [1.0] * len(SETS["G_t"]))   # 1 = genuine (accept)
    X = np.array([fvec(c, aware) for c in tr])
    mu = X.mean(0)
    sd = X.std(0) + 1e-9
    Z = (X - mu) / sd
    best = None
    for lam in (0.01, 0.1, 1.0, 10.0, 100.0):
        loo = np.zeros(len(y))
        for i in range(len(y)):
            m = np.arange(len(y)) != i
            w = fit_lr(Z[m], y[m], lam)
            loo[i] = predict(w, Z[i:i + 1])[0]
        ll = -np.mean(y * np.log(loo + 1e-9) + (1 - y) * np.log(1 - loo + 1e-9))
        if best is None or ll < best[0]:
            best = (ll, lam, loo)
    ll, lam, loo = best
    w = fit_lr(Z, y, lam)
    sel = None
    for thr in sorted(set(np.round(np.concatenate([loo, [0.0, 1.0]]), 6))):
        fr = float(np.mean(loo[y == 1] < thr))
        cr = float(np.mean(loo[y == 0] < thr))
        if fr <= 0.10 and (sel is None or cr > sel[1] + 1e-12):
            sel = (float(thr), cr, fr)
    thr = sel[0] if sel else 0.5
    cache = {}

    def sc(c):
        k = id(c)
        if k not in cache:
            cache[k] = float(predict(w, ((fvec(c, aware) - mu) / sd)[None, :])[0])
        return cache[k]

    grid = sorted(set([round(x, 3) for x in np.linspace(0.02, 0.98, 49)] + [round(thr, 6)]))
    cells = {f"lr_thr{t}": ((lambda c, t=t: sc(c) >= t), {"thr": t}) for t in grid}
    meta = {"lambda": lam, "loo_logloss": round(float(ll), 4), "loo_thr": thr,
            "loo_tuning_catch": round(sel[1], 3) if sel else None,
            "loo_tuning_fr": round(sel[2], 3) if sel else None, "n_features": int(X.shape[1])}
    return cells, meta, f"lr_thr{round(thr, 6)}"


# ---------------------------------------------------------------- sweep / freeze
def sweep(cells):
    return {n: dict(params=p, **evalcell(a)) for n, (a, p) in cells.items()}


def freeze(res, frozen_name=None):
    """Pre-stated rule: max tuning catch s.t. tuning FR<=0.10; ties -> lower tuning FR, then enumeration order."""
    if frozen_name is not None:
        return frozen_name, len(res), sum(1 for r in res.values() if r["tuning"]["fr_rate"] <= 0.10)
    elig = [(n, r) for n, r in res.items() if r["tuning"]["fr_rate"] <= 0.10]
    if not elig:
        return None, len(res), 0
    order = {n: i for i, n in enumerate(res)}
    n, _ = sorted(elig, key=lambda x: (-x[1]["tuning"]["catch_rate"], x[1]["tuning"]["fr_rate"], order[x[0]]))[0]
    return n, len(res), len(elig)


def hindsight(res):
    el = [(r["heldout"]["catch_rate"], n) for n, r in res.items() if r["heldout"]["fr_rate"] <= 0.10]
    return max(el) if el else None


def main():
    out = {"bar": D["tune_nv"]["bar"], "set_sizes": {k: len(v) for k, v in SETS.items()},
           "n_draws": {n: D[n]["n_draws"] for n in D},
           "labels": {n: {f"{s}/{l}": v for (s, l), v in Counter((c["stream"], c["label"]) for c in D[n]["cases"]).items()}
                      for n in D}}
    res = {}
    frozen_override = {}
    res["CTRL_fold_k_min"] = sweep(design_fold_control())
    res["D1_longhead_cut"] = sweep(design_D1())
    res["D1b_multihead_AND"] = sweep(design_D1b())
    res["D2_perregister_fold_bar"] = sweep(design_D2())
    out["d3_meta"] = {}
    cellsb = None
    for aware, nm in ((False, "D3a_learned_register_blind"), (True, "D3b_learned_register_aware")):
        cells, meta, thrname = run_D3(aware)
        res[nm] = sweep(cells)
        out["d3_meta"][nm] = dict(meta, frozen_by_loo=thrname)
        frozen_override[nm] = thrname
        if not aware:
            cellsb = cells
    # D4 hybrids (enumerated conjunctions)
    c4 = {}
    for k in (4, 5, 6):
        for tn in (0.96, 1.0):
            for h in (96, 120, 144):
                for t in (0.90, 0.95, 1.00):
                    c4[f"hyb_perreg_k{k}_tauN{tn}_AND_cut{h}_{t}"] = (
                        (lambda c, k=k, tn=tn, h=h, t=t: fold_stat(c, k, "min") >= (0.90 if is_en(c) else tn)
                         and (cutv(c, h) or 0) >= t), {"k": k, "tau_N": tn, "head": h, "tau": t})
    res["D4_hybrid_perreg_AND_longhead"] = sweep(c4)
    thr_names = {float(n.split("thr")[1]): n for n in cellsb}
    c4b = {}
    for t in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
        near = thr_names[min(thr_names, key=lambda z: abs(z - t))]
        f = cellsb[near][0]
        for k in (4, 5, 6):
            c4b[f"hyb_LRblind_thr{t}_AND_fold{k}min0.90"] = (
                (lambda c, f=f, k=k: f(c) and fold_stat(c, k, "min") >= 0.90), {"thr": t, "k": k})
    res["D4b_learned_blind_AND_fold"] = sweep(c4b)

    summary = {}
    for name, r in res.items():
        fn, ncells, nel = freeze(r, frozen_override.get(name))
        e = {"n_cells": ncells, "n_cells_tuning_FR_ok": nel, "frozen": fn}
        if fn:
            t, h = r[fn]["tuning"], r[fn]["heldout"]
            e.update(frozen_tuning=t, frozen_heldout=h,
                     heldout_catch_wilson95=wilson(h["catch"], h["catch_n"]),
                     heldout_fr_wilson95=wilson(h["fr"], h["fr_n"]),
                     heldout_regspread_fr_wilson95=wilson(h["reg_fr"], h["reg_n"]))
            e["comparable_pass"] = bool(t["catch_rate"] >= 0.90 and t["fr_rate"] <= 0.10
                                        and h["catch_rate"] >= 0.90 and h["fr_rate"] <= 0.10)
            e["strict_pass"] = bool(e["comparable_pass"] and h["reg_fr_rate"] is not None
                                    and h["reg_fr_rate"] <= 0.10)
        hs = hindsight(r)
        e["hindsight_best_heldout_catch_at_FR_le_0.10"] = (
            {"catch_rate": hs[0], "cell": hs[1], "heldout": r[hs[1]]["heldout"]} if hs else None)
        summary[name] = e
    out["summary"] = summary
    nonctrl = {n: e for n, e in summary.items() if not n.startswith("CTRL")}
    out["SEAL_PASS"] = any(e.get("strict_pass") for e in nonctrl.values())
    out["SEAL_PASS_L1_COMPARABLE"] = any(e.get("comparable_pass") for e in nonctrl.values())
    out["cells"] = res
    json.dump(out, open(os.path.join(HERE, "catch_surface.json"), "w"), indent=1, default=float)
    print(out["set_sizes"], out["n_draws"])
    print(out["labels"])
    for n, e in summary.items():
        if e["frozen"]:
            t, h = e["frozen_tuning"], e["frozen_heldout"]
            print(f"{n:32s} {e['frozen']:44s} tune {t['catch_rate']}/{t['fr_rate']} (reg {t['reg_fr_rate']})"
                  f"  held {h['catch_rate']}/{h['fr_rate']} reg_fr {h['reg_fr_rate']} n={h['reg_n']}"
                  f" cmp={e['comparable_pass']} strict={e['strict_pass']}")
        else:
            print(n, "no tuning cell with FR<=0.10")
        hs = e["hindsight_best_heldout_catch_at_FR_le_0.10"]
        print("      hindsight:", hs and (hs["catch_rate"], hs["cell"], hs["heldout"]["reg_fr_rate"]))
    print("SEAL_PASS", out["SEAL_PASS"], "comparable", out["SEAL_PASS_L1_COMPARABLE"])


if __name__ == "__main__":
    main()
