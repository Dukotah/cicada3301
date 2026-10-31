"""R41 I1 fit: null_stream.jsonl -> null_survivor12.json, fit.json.  python fit.py"""
import json, math, os, sys, collections, importlib.util
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", ".."))
sp = importlib.util.spec_from_file_location("fit34", os.path.join(AN, "round34", "I1-v3-null", "fit.py")); FIT = importlib.util.module_from_spec(sp); sp.loader.exec_module(FIT)
FAM = ("bash4.2", "bash4.2_i32", "mt_scale", "mt_mod", "php_scale", "php_mod"); RELS = ("keyskip1", "keyskip2")
NS = (69017, 1e5, 131786, 1e6, 1e9)
A = -math.log1p(-0.01)


def bar(f, N): return f["u"] + f["beta"] * math.log(f["p_u"]) + f["beta"] * math.log(N / A)


def tail(v, boots=0, rng=None):
    v = np.asarray(v, float)
    f = FIT.tailfit(v); f["mu"] = float(f["u"] + f["beta"] * math.log(f["p_u"]))
    f["bars"] = {"N=%g" % N: round(bar(f, N), 4) for N in NS}
    f["q90"], f["q99"], f["q999"] = [float(np.quantile(v, q)) for q in (.9, .99, .999)]
    f["median_pmax"] = float(np.median(v))
    try:
        f["gpd_bars_sensitivity"] = {"N=%g" % N: round(FIT.gpd_bar(f, N), 4) for N in NS}
    except Exception:
        f["gpd_bars_sensitivity"] = None
    if boots:
        bb = {N: [] for N in NS}
        for _ in range(boots):
            g = FIT.tailfit(v[rng.integers(0, len(v), len(v))])
            for N in NS: bb[N].append(bar(g, N))
        f["bar_se"] = {"N=%g" % N: round(float(np.std(bb[N], ddof=1)), 4) for N in NS}
    return f


def real_store_rows():
    out = {}

    def add(name, path):
        d = out.setdefault(name, {r: [] for r in RELS})
        with open(path) as f:
            f.readline()
            for l in f:
                r = json.loads(l)
                if r[1] != 120: continue
                k = r[0]; rel = k.rsplit("|", 1)[1] if "|" in k else k.rsplit(":", 1)[1]
                if rel in d: d[rel].append(r[3])
    add("R37-I2", os.path.join(AN, "round37", "I2-pfv4-12reg", "sweep_rows.jsonl"))
    add("R40-B1", os.path.join(AN, "round40", "B1-bash-versions", "sweep_rows.jsonl"))
    for g in ("B04", "KDF", "R17PAD", "COSPAD"): add("R40-B3:" + g, os.path.join(AN, "round40", "B3-english-era-grids", "rows_%s.jsonl" % g))
    return out


def ks2(a, b):
    a = np.sort(a); b = np.sort(b); x = np.concatenate([a, b])
    d = np.abs(np.searchsorted(a, x, side="right") / len(a) - np.searchsorted(b, x, side="right") / len(b)).max()
    n = len(a) * len(b) / (len(a) + len(b)); lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * d
    p = 2 * sum((-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam) for k in range(1, 100)); return float(d), float(min(max(p, 0), 1))


def main():
    rng = np.random.default_rng(41)
    rows = [json.loads(l) for l in open(os.path.join(HERE, "null_stream.jsonl"))]
    p240 = os.path.join(HERE, "null_stream240.jsonl")
    if os.path.exists(p240):
        ex = {(r["fam"], r["seed"]): r for r in map(json.loads, open(p240))}
        for r in rows:
            e = ex.get((r["fam"], r["seed"]))
            if e: r["keyskip1_240"], r["keyskip2_240"] = e["keyskip1_240"], e["keyskip2_240"]
    seen = set(); ded = []
    for r in rows:
        k = (r["fam"], r["seed"])
        if k in seen: continue
        seen.add(k); ded.append(r)
    n_raw = len(rows); rows = ded          # distinct wrong keys (draws are with replacement; 1.6 % repeats are one key)
    null12 = json.load(open(os.path.join(AN, "round36", "B1-orbit-12reg", "null12.json")))["cells"]
    out = {"n_survivor_draws_raw": n_raw, "n_survivors": len(rows), "per_family_survivors": dict(collections.Counter(r["fam"] for r in rows)), "cells": {}, "per_family": {}, "heterogeneity": {}}
    pop = {}
    for L, suf in ((120, ""), (240, "_240")):
        for rel in RELS:
            sel = [r for r in rows if rel + suf in r]
            v = np.array([r[rel + suf][0] for r in sel])
            f = tail(v, boots=200, rng=rng)
            f["degenerate_share"] = float(np.mean([(r[rel + suf][2] <= 6 or r[rel + suf][3] >= 4.24) for r in sel]))
            pop[(L, rel)] = (sel, v)
            n12 = null12["L%d|%s" % (L, rel)]
            f["null12"] = {"mu": n12["mu"], "beta": n12["beta"], "bars": n12["bars"], "p50": n12["p50"], "p99": n12["p99"],
                           "bar_N131786": n12["mu"] + n12["beta"] * math.log(131786 / A), "bar_N1e9": n12["mu"] + n12["beta"] * math.log(1e9 / A)}
            out["cells"]["L%d|%s" % (L, rel)] = f
            for fam in FAM:
                vv = np.array([r[rel + suf][0] for r in sel if r["fam"] == fam])
                if len(vv) >= 200:
                    out["per_family"]["L%d|%s|%s" % (L, rel, fam)] = dict(tail(vv), n_fam=len(vv))
            het = {}
            for fam in FAM:
                a = np.array([r[rel + suf][0] for r in sel if r["fam"] == fam]); b = np.array([r[rel + suf][0] for r in sel if r["fam"] != fam])
                if len(a) >= 200:
                    d, p = ks2(a, b); het[fam] = {"n": len(a), "ks_D_vs_rest": round(d, 4), "ks_p": round(p, 4)}
            bars = {fam: out["per_family"]["L%d|%s|%s" % (L, rel, fam)]["bars"]["N=1e+06"] for fam in FAM if "L%d|%s|%s" % (L, rel, fam) in out["per_family"]}
            het["bar1e6_by_family"] = bars; het["bar1e6_spread_max_minus_min"] = round(max(bars.values()) - min(bars.values()), 4)
            het["max_family_bar1e6"] = max(bars, key=bars.get); het["pooled_bar1e6"] = f["bars"]["N=1e+06"]
            out["heterogeneity"]["L%d|%s" % (L, rel)] = het
    stores = real_store_rows(); real = {"per_store": {}, "pooled": {}, "pooled_R37_only": {}}
    for st, d in stores.items():
        real["per_store"][st] = {rel: {"n": len(v), "max": max(v), "median": float(np.median(v)), "q99": float(np.quantile(v, .99))} for rel, v in d.items()}
    for rel in RELS:
        pooled = np.array([x for d in stores.values() for x in d[rel]]); r37 = np.array(stores["R37-I2"][rel])
        for key, a in (("pooled", pooled), ("pooled_R37_only", r37)):
            g = tail(a, boots=100, rng=rng); g["max"] = float(a.max()); g["n_rows"] = len(a); real[key][rel] = g
    out["real_stores"] = real
    q1a = {}
    for rel in RELS:
        refit = out["cells"]["L120|" + rel]; tgt = real["pooled"][rel]; t37 = real["pooled_R37_only"][rel]
        b_ref = refit["bars"]["N=131786"]; b_t = tgt["bars"]["N=131786"]; b_t37 = t37["bars"]["N=131786"]
        q1a[rel] = {"refit_bar_N131786": b_ref, "refit_bar_se": refit["bar_se"]["N=131786"], "target_pooled_real_POT_bar_N131786": b_t, "target_se": tgt["bar_se"]["N=131786"],
                    "target_R37_only_bar_N131786": b_t37, "refit_minus_pooled": round(b_ref - b_t, 4), "refit_minus_R37only": round(b_ref - b_t37, 4),
                    "PASS_pooled": bool(b_ref >= b_t), "PASS_R37only": bool(b_ref >= b_t37)}
    out["Q1a"] = q1a
    q5a = {}
    for rel in RELS:
        f = out["cells"]["L120|" + rel]
        for st, d in stores.items():
            v = d[rel]; N = len(v); loc = f["mu"] + f["beta"] * math.log(N); sd = 1.2825 * f["beta"]
            q5a["%s|%s" % (st, rel)] = {"N": N, "obs_max": max(v), "fit_mean_of_max": round(loc + 0.5772 * f["beta"], 4), "fit_sd_of_max": round(sd, 4),
                                        "z_obs_minus_fit": round((max(v) - (loc + 0.5772 * f["beta"])) / sd, 3)}
        sel, v = pop[(120, rel)]; n = len(v); chk = {}
        for q in (.99, .999, .9997):
            x = float(np.quantile(v, q)); exp_n = n * f["p_u"] * math.exp(-(x - f["u"]) / f["beta"]); obs_n = int((v >= x).sum())
            chk["q%g" % q] = {"x": round(x, 3), "observed": obs_n, "fit_expected": round(exp_n, 2), "z_poisson": round((obs_n - exp_n) / math.sqrt(max(exp_n, 1e-9)), 2)}
        f["tail_count_check"] = chk
    out["Q5_realstore_max_vs_fit"] = q5a
    # ---- bar of record: Q5 fired in the CONSERVATIVE direction (see RESULTS): the record at L=120 is the higher of the null Gumbel refit and the
    # pooled real-sweep-survivor POT line (both fitted on the survivor population); at L=240 (no real-sweep rows exist) the Gumbel refit.
    rec = {}
    for rel in RELS:
        a = out["cells"]["L120|" + rel]; b = real["pooled"][rel]
        lines = {"refit": (a["mu"], a["beta"]), "pooled_real": (b["mu"], b["beta"])}
        pick = {}
        for N in NS:
            vals = {k: m + be * math.log(N / A) for k, (m, be) in lines.items()}
            pick["N=%g" % N] = {"refit": round(vals["refit"], 4), "pooled_real": round(vals["pooled_real"], 4), "record": round(max(vals.values()), 4), "from": max(vals, key=vals.get)}
        rec["L120|" + rel] = pick
        c = out["cells"]["L240|" + rel]
        rec["L240|" + rel] = {"N=%g" % N: {"refit": round(bar(c, N), 4), "record": round(bar(c, N), 4), "from": "refit (no real L=240 survivor rows exist)"} for N in NS}
    out["bar_of_record"] = rec
    json.dump(out, open(os.path.join(HERE, "fit.json"), "w"), indent=1, default=float)
    comp = {"population": "wrong-key seeds, six generator families, real LP2 head, pf_v4_12 frozen survivors, beam_v3 panel_max panel-R36",
            "n_survivors": len(rows), "per_family_survivors": out["per_family_survivors"],
            "cells": {k: {kk: v[kk] for kk in ("n", "k", "u", "p_u", "beta", "mu", "beta_se", "xi_gpd_moments", "gpd_sigma", "median_pmax", "q90", "q99", "q999", "emp_max", "bars", "bar_se", "gpd_bars_sensitivity")} for k, v in out["cells"].items()}, "bar_of_record": rec,
            "pooled_real_line_L120": {rel: {"mu": real["pooled"][rel]["mu"], "beta": real["pooled"][rel]["beta"], "n_rows": real["pooled"][rel]["n_rows"]} for rel in RELS},
            "record_rule": "L=120: max(null Gumbel refit, pooled real-sweep survivor POT line); L=240: Gumbel refit"}
    json.dump(comp, open(os.path.join(HERE, "null_survivor12.json"), "w"), indent=1, default=float)
    print(json.dumps({"n": len(rows), "Q1a": q1a, "cells": {k: (v["mu"], v["beta"], v["bars"], v["bar_se"]) for k, v in out["cells"].items()}}, indent=1, default=float))


if __name__ == "__main__": main()
