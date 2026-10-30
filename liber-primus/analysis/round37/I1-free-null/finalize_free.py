"""Round 37 / I1 finalize: fit nulls, control table, bars.  python finalize_free.py -> null_free.json control_free.json fit_free.json"""
import json, math, os, sys, collections
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "round34", "I1-v3-null"))
import fit as R34FIT            # tailfit, bar_from, ols (R34 machinery)
ALPHA = 0.01
NS = (1e3, 1e5, 1e6)

def load_null():
    cells = collections.defaultdict(dict)
    for l in open(os.path.join(HERE, "null_free_stream.jsonl")):
        r = json.loads(l); cells[r["L"]][r["i0"]] = r["pm"]
    out = {}
    for L, d in cells.items():
        v = []
        for i0 in sorted(d): v.extend(d[i0])
        out[L] = v
    return out

def main():
    nulls = load_null(); res = {}
    Ls = sorted(nulls)
    for L in Ls:
        v = nulls[L]; f = R34FIT.tailfit(v)
        f["bars"] = {"%g" % N: R34FIT.bar_from(f, N, ALPHA) for N in NS}
        f["gpd_bar_1e6"] = R34FIT.gpd_bar(f, 1e6, ALPHA)
        f["sens"] = {str(q): {k: R34FIT.tailfit(v, q)[k] for k in ("u", "beta", "mu")} for q in (0.85, 0.95)}
        f["draws"] = len(v); f["bars_se_beta"] = {"%g" % N: f["beta_se"] * (math.log(N / -math.log1p(-ALPHA))) for N in NS}
        f["q90"] = f["u"]; f["q999"] = float(np.quantile(v, .999)); f["min"] = float(np.min(v))
        res[str(L)] = f
    # exponent of beta(L) and the mu(L) trend over the L>=240 cells and over all
    pts = [(L, res[str(L)]["beta"], res[str(L)]["mu"]) for L in Ls]
    a, b, sa, sb, n = R34FIT.ols(np.array([p[0] for p in pts], float), np.array([p[1] for p in pts]))
    ex = {"beta_exponent": b, "beta_exponent_se": sb, "ln_a": a, "n_points": n, "Ls": Ls}
    # mu linear in ln L
    A = np.vstack([np.ones(len(pts)), np.log([p[0] for p in pts])]).T
    co = np.linalg.lstsq(A, np.array([p[2] for p in pts]), rcond=None)[0]
    ex["mu_vs_lnL"] = {"intercept": float(co[0]), "slope_per_lnL": float(co[1])}
    json.dump({"panel": "panel-r36 (12 registers)", "decoder": "beam_v3 free panel_max beam_w400 lam_u4", "alpha": ALPHA, "cells": res, "trend": ex,
               "draws_raw": {str(L): nulls[L] for L in Ls}}, open(os.path.join(HERE, "null_free.json"), "w"))
    json.dump({"fit": {k: {kk: vv for kk, vv in v.items() if kk != "sens"} for k, v in res.items()}, "trend": ex}, open(os.path.join(HERE, "fit_free.json"), "w"), indent=1)
    # control
    ctl = collections.defaultdict(lambda: collections.defaultdict(list))
    for l in open(os.path.join(HERE, "control_free_stream.jsonl")):
        r = json.loads(l); ctl[r["L"]][r["register"]].append((r["seed"], r["pmax"], r["rec"]))
    C = {}
    for L, regs in sorted(ctl.items()):
        if str(L) not in res: continue
        bar = res[str(L)]["bars"]["1e+06"]
        rows = {}
        for reg, lst in regs.items():
            pm = np.array([x[1] for x in lst])
            rows[reg] = {"n": len(lst), "pass": int((pm >= bar).sum()), "median_pmax": float(np.median(pm)), "min_pmax": float(pm.min()),
                         "median_rec": float(np.median([x[2] for x in lst])), "ok_19of20": bool(len(lst) >= 20 and (pm >= bar).sum() >= 19),
                         "n_lt_20": len(lst) < 20}
        C[str(L)] = {"bar_N1e6": bar, "bar_N1e5": res[str(L)]["bars"]["100000"], "registers": rows}
    json.dump(C, open(os.path.join(HERE, "control_free.json"), "w"), indent=1)
    for L in Ls:
        f = res[str(L)]; print("L=%d n=%d med=%.2f p99=%.2f max=%.2f u=%.2f beta=%.3f(%.3f) mu=%.2f xi=%.2f bars %s" % (L, f["draws"], f["p50"], f["p99"], f["emp_max"], f["u"], f["beta"], f["beta_se"], f["mu"], f["xi_gpd_moments"], {k: round(x, 2) for k, x in f["bars"].items()}))
    print(ex)
    for L, c in C.items():
        print("control L=%s bar1e6=%.2f" % (L, c["bar_N1e6"]))
        for reg, r in c["registers"].items(): print("  %-13s %d/%d med %.2f min %.2f rec %.2f" % (reg, r["pass"], r["n"], r["median_pmax"], r["min_pmax"], r["median_rec"]))

if __name__ == "__main__": main()
