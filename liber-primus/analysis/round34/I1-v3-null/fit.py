"""Round 34 / I1: cells + Gumbel(POT) fit + exponent.  python fit.py  -> null_cells.json, fit.json"""
import json, math, os, sys, collections
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
R32_EXP, R32_SE = -0.55, 0.04

def load():
    cells = collections.defaultdict(list)
    seen = set()
    for line in open(os.path.join(HERE, "null_stream.jsonl")):
        r = json.loads(line)
        key = (r["family"], r["source"], r["L"], r["rel"])
        if (key, r["i0"]) in seen:
            continue
        seen.add((key, r["i0"]))
        cells[key].extend(r["pm"])
    return cells

def tailfit(v, q=0.90):
    a = np.sort(np.asarray(v, float)); n = len(a)
    u = float(np.quantile(a, q)); exc = a[a > u] - u; k = len(exc)
    beta = float(exc.mean()); pu = k / n
    # GPD shape by moments (xi = 0.5*(1 - m^2/s^2)); xi~0 <=> exponential (Gumbel-max) tail
    xi = 0.5 * (1 - exc.mean() ** 2 / exc.var(ddof=1)) if k > 5 else float("nan")
    sig = float(exc.mean() * (1 - xi)) if xi == xi else float("nan")
    return {"gpd_sigma": sig, "n": n, "k": k, "u": u, "p_u": pu, "beta": beta, "beta_se": beta / math.sqrt(k), "mu": u + beta * math.log(pu),
            "xi_gpd_moments": float(xi), "emp_max": float(a[-1]), "p99": float(np.quantile(a, .99)), "p50": float(np.quantile(a, .5)),
            "mean": float(a.mean())}

def gpd_bar(f, N, alpha=0.01):
    xi, sg = f["xi_gpd_moments"], f["gpd_sigma"]
    t = N * f["p_u"] / -math.log1p(-alpha)
    return f["u"] + sg / xi * (t ** xi - 1) if abs(xi) > 1e-6 else f["u"] + sg * math.log(t)

def bar_from(f, N, alpha=0.01, beta=None):
    b = f["beta"] if beta is None else beta
    mu = f["u"] + b * math.log(f["p_u"])
    return mu + b * math.log(N / -math.log1p(-alpha))

def ols(L, b):
    x, y = np.log(L), np.log(b); n = len(x)
    A = np.vstack([np.ones(n), x]).T
    coef = np.linalg.lstsq(A, y, rcond=None)[0]
    r = y - A @ coef
    if n > 2:
        s2 = r @ r / (n - 2); se = np.sqrt(np.diag(s2 * np.linalg.inv(A.T @ A)))
    else:
        se = np.array([float("nan")] * 2)
    return float(coef[0]), float(coef[1]), float(se[0]), float(se[1]), n

def main():
    cells = load()
    out_cells = {}; fits = {}
    for key, v in sorted(cells.items()):
        fam, src, L, rel = key
        name = "%s|%s|L%d|%s" % (fam, src, L, rel)
        f = tailfit(v)
        f["sens"] = {str(q): {k: tailfit(v, q)[k] for k in ("u", "beta", "mu")} for q in (0.85, 0.95)}
        f["gpd_bar_N2e5"] = gpd_bar(f, 2e5); f["gumbel_bar_N2e5"] = bar_from(f, 2e5)
        f["gumbel_median_max_at_n"] = bar_from(f, f["n"], alpha=0.5); out_cells[name] = {"family": fam, "source": src, "L": L, "rel": rel, **f}
    json.dump(out_cells, open(os.path.join(HERE, "null_cells.json"), "w"), indent=1)
    # groups for exponent: (family, rel) with lp2 as one series; register as pooled-over-registers sample and per register
    groups = collections.defaultdict(dict)
    for key, v in cells.items():
        fam, src, L, rel = key
        if fam == "lp2":
            groups[("lp2", rel)].setdefault(L, []).extend(v)
        else:
            groups[("register", rel)].setdefault(L, []).extend(v)
    res = {}
    for (fam, rel), byL in sorted(groups.items()):
        if rel == "free":
            continue
        Ls = sorted(byL)
        per = {L: tailfit(byL[L]) for L in Ls}
        L_ = np.array(Ls, float); be = np.array([per[L]["beta"] for L in Ls])
        a, b, sa, sb, n = ols(L_, be)
        e = {"nodes": {str(L): per[L] for L in Ls}, "exponent": b, "exponent_se": sb, "ln_a": a, "n_points": n,
             "dof": n - 2, "beta_at_120": math.exp(a + b * math.log(120))}
        if len(Ls) >= 4 and 400 in Ls:
            k = [i for i, L in enumerate(Ls) if L != 400]
            a3, b3, _, s3, n3 = ols(L_[k], be[k]); e["fit_without_L400"] = {"exponent": b3, "exponent_se": s3, "ln_a": a3}
        # difference vs R32 I3
        comb = math.sqrt(sb ** 2 + R32_SE ** 2) if sb == sb else float("nan")
        e["vs_R32_I3"] = {"r32_exponent": R32_EXP, "r32_se": R32_SE, "diff": b - R32_EXP, "n_se_combined": (b - R32_EXP) / comb if comb == comb else None,
                          "n_se_v3_only": (b - R32_EXP) / sb if sb == sb else None}
        e["Q5_fires_combined"] = bool(comb == comb and abs(b - R32_EXP) / comb > 3)
        # per-point weighted version using beta SEs (log-scale se = beta_se/beta)
        w = np.array([(per[L]["beta"] / per[L]["beta_se"]) ** 2 for L in Ls])
        x = np.log(L_); y = np.log(be); W = np.diag(w); A = np.vstack([np.ones(len(x)), x]).T
        cov = np.linalg.inv(A.T @ W @ A); co = cov @ A.T @ W @ y
        e["wls_exponent"] = float(co[1]); e["wls_exponent_se_sampling"] = float(math.sqrt(cov[1, 1]))
        res["%s|%s" % (fam, rel)] = e
    # per-register series (register family)
    perreg = {}
    for rel in ("keyskip1", "keyskip2"):
        for src in ("EN_NOVOWEL", "LATIN", "OE", "DE"):
            pts = sorted((k[2], tailfit(v)) for k, v in cells.items() if k[0] == "register" and k[1] == src and k[3] == rel)
            if len(pts) >= 3:
                a, b, sa, sb, n = ols(np.array([p[0] for p in pts], float), np.array([p[1]["beta"] for p in pts]))
                perreg["%s|%s" % (src, rel)] = {"exponent": b, "exponent_se": sb, "Ls": [p[0] for p in pts], "ln_a": a}
    # per-cell register fits for bars (max over registers)
    regcell = {}
    for key, v in cells.items():
        if key[0] == "register":
            regcell["%s|L%d|%s" % (key[1], key[2], key[3])] = tailfit(v)
    free = {str(k[2]): tailfit(v) for k, v in cells.items() if k[3] == "free"}
    json.dump({"method": "POT exponential tail above empirical 90th pct; mu=u+beta ln p_u; bar=mu+beta ln(N/-ln(1-alpha))",
               "series": res, "per_register_exponent": perreg, "register_cells": regcell, "free": free,
               "r32_i3_exponent": [R32_EXP, R32_SE]}, open(os.path.join(HERE, "fit.json"), "w"), indent=1)
    for k, e in res.items():
        print(k, "exp %.3f +- %.3f" % (e["exponent"], e["exponent_se"]), "nse %s" % e["vs_R32_I3"]["n_se_combined"], "Q5", e["Q5_fires_combined"])
    for n, c in out_cells.items():
        print(n, c["n"], "max %.3f p99 %.3f beta %.3f(+-%.3f) mu %.3f xi %.2f" % (c["emp_max"], c["p99"], c["beta"], c["beta_se"], c["mu"], c["xi_gpd_moments"]))

if __name__ == "__main__":
    main()
