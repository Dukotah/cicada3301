"""I2 / adjudication of this lane's OWN pre-registered gates.

Reads out_null.json, out_power.json, out_speed.json and emits out_gates.json plus the
markdown tables that go into RESULTS.md.  Thresholds are read from PREREG.md's constants,
never recomputed from the results.

    python3 gates.py
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# --- pre-registered constants (PREREG.md s3).  DO NOT EDIT after seeing results. -------
G_POWER_MIN = 0.90
G_LP1_MIN_EN = -4.5
G_SPEED_MAX_RATIO = 3.0
ALPHA_REF = 1e-3
LEGACY_BAR = -5.5
LENGTHS = [120, 240, 400]
REGISTERS = ["EN_MODERN", "EN_KJV", "LP1_REAL", "LATIN", "OE", "DE", "CY",
             "EN_HALFVOWEL", "EN_NOVOWEL"]

# L7-A's published numbers, for the before/after column (round18/L7-redteam/RESULTS.md A.1)
L7A = {"EN_MODERN": (-4.22, 1.00), "EN_KJV": (-4.11, 1.00), "LP1_REAL": (-4.33, 1.00),
       "LATIN": (-5.58, 0.33), "OE": (-5.39, 0.58), "DE": (-5.52, 0.42),
       "CY": (-6.58, 0.00), "EN_HALFVOWEL": (-5.62, 0.33), "EN_NOVOWEL": (-7.60, 0.00)}


def load(name):
    p = os.path.join(HERE, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


# --------------------------------------------------------------------------------------
# SUPPLEMENTARY (not a gate): the far tail.
#
# alpha_ref = 1e-3 is the PRE-REGISTERED per-decode false-positive rate and the gates are
# adjudicated there and nowhere else.  But a real Phase 2 sweep performs 10^6 - 10^9
# decodes, so its FAMILY-WISE bar sits at alpha/N, i.e. a per-decode FP of 1e-9 or worse.
# That is exactly why the repo's fixed -5.5 English bar is so much stricter than a 1e-3
# bar would be.  These numbers are reported so Phase 2 and I3 have the operating point
# they will actually use.  They are EXTRAPOLATIONS and are labelled as such.
# --------------------------------------------------------------------------------------
def gpd_from_quantiles(q99, q999, q9999, pu=0.01):
    """Recover (u, sigma, xi) of a Generalized Pareto tail from three stored quantiles.

    The raw null draws are not persisted (only summaries are), so the tail is refitted
    from q(0.99) as the threshold u and the two higher quantiles as constraints:
        q(1-a) = u + sigma/xi * ((a/pu)^-xi - 1)
    """
    u = float(q99)
    a1, a2 = 1e-3, 1e-4
    r1, r2 = a1 / pu, a2 / pu
    y1, y2 = float(q999) - u, float(q9999) - u
    if y1 <= 0 or y2 <= y1:
        return None
    target = y2 / y1

    def f(xi):
        if abs(xi) < 1e-9:
            return np.log(1 / r2) / np.log(1 / r1)
        return (r2 ** -xi - 1.0) / (r1 ** -xi - 1.0)

    lo, hi = -0.99, 2.0
    if not (min(f(lo), f(hi)) <= target <= max(f(lo), f(hi))):
        return None
    for _ in range(200):                       # bisection; f is monotone in xi
        mid = 0.5 * (lo + hi)
        if (f(mid) - target) * (f(lo) - target) <= 0:
            hi = mid
        else:
            lo = mid
    xi = 0.5 * (lo + hi)
    sig = y1 * xi / (r1 ** -xi - 1.0) if abs(xi) > 1e-9 else y1 / np.log(1 / r1)
    return {"u": u, "sigma": float(sig), "xi": float(xi), "pu": pu}


def gpd_q(par, alpha):
    if par is None:
        return float("nan")
    r = alpha / par["pu"]
    if abs(par["xi"]) < 1e-9:
        return par["u"] + par["sigma"] * (-np.log(r))
    return par["u"] + par["sigma"] / par["xi"] * (r ** -par["xi"] - 1.0)


def k_eff_ci(nl):
    """k_eff with a Poisson interval, because I3 is going to cite this number.

    k_eff = P(pmax > t) / P(z_EN > t) measured on the SAME random-rune null.  The numerator
    is fixed by construction (t is that null's own q-quantile); the denominator is a count
    of exceedances, so its uncertainty is Poisson in that count.
    """
    n = nl["random_rune"]["en"]["n"]
    out = {"random_rune_n": n}
    for q, ent in nl["k_eff_by_quantile"].items():
        p_en = ent["P_zEN_gt_t"]
        c = p_en * n
        if c <= 0:
            out[q] = {"k_eff": None, "exceedances": 0,
                      "note": "no z_EN exceedance at this depth; k_eff unbounded below n"}
            continue
        lo_c, hi_c = max(c - 1.96 * np.sqrt(c), 0.5), c + 1.96 * np.sqrt(c)
        out[q] = {"k_eff": ent["k_eff"], "exceedances": int(round(c)),
                  "k_eff_ci95": [ent["P_pmax_gt_t"] / (hi_c / n),
                                 ent["P_pmax_gt_t"] / (lo_c / n)],
                  "t": ent["t"]}
    return out


def far_tail(nulls, power_rows, alphas=(1e-6, 1e-9)):
    out = {"note": ("SUPPLEMENTARY, not a gate.  Thresholds extrapolated with a "
                    "Generalized Pareto tail refitted from the stored q99/q999/q9999 of "
                    "each null, because the raw draws are summarised rather than kept.  "
                    "Treat as order-of-magnitude, not as a calibrated bar — that is I3's "
                    "deliverable."),
           "per_length": {}}
    for L in LENGTHS:
        nl = nulls["lengths"][str(L)]
        ent = {}
        for src in ("wrongkey", "random_rune"):
            for stat in ("en", "pmax", "pcon"):
                q = nl[src][stat]["q"]
                par = gpd_from_quantiles(q["0.99"], q["0.999"], q["0.9999"])
                ent[f"{src}_{stat}_gpd_params"] = par
                for a in alphas:
                    ent[f"{src}_{stat}_t_at_{a:g}"] = gpd_q(par, a)
        rows = []
        for r in power_rows:
            if r["L"] != L:
                continue
            rows.append(r)
        ent["power_at_far_tail"] = {}
        for a in alphas:
            t_en = ent[f"wrongkey_en_t_at_{a:g}"]
            t_p = ent[f"wrongkey_pmax_t_at_{a:g}"]
            ent["power_at_far_tail"][f"{a:g}"] = {
                "t_en": t_en, "t_pmax": t_p,
                "per_register": {r["register"]: {
                    "power_en": float(np.mean([v >= t_en for v in r["_en_vals"]])),
                    "power_pmax": float(np.mean([v >= t_p for v in r["_pmax_vals"]])),
                } for r in rows}}
        out["per_length"][str(L)] = ent
    return out


def main():
    nulls, power, speed = load("out_null.json"), load("out_power.json"), load("out_speed.json")
    missing = [n for n, v in (("out_null.json", nulls), ("out_power.json", power),
                              ("out_speed.json", speed)) if v is None]
    if missing:
        print("MISSING:", missing)
        sys.exit(1)
    out = {"lane": "round19/I2", "alpha_ref": ALPHA_REF, "gates": {}}

    # ------------------------------------------------------------------ G-POWER
    # Powers are RECOMPUTED here from the stored per-replicate rows against the FINAL
    # measured thresholds, so the power grid and the null run do not have to be run in
    # lockstep and the published numbers can never disagree with out_null.json.
    cells = power["cells"]
    raw = {}
    for r in power.get("rows", []):
        raw.setdefault((r["register"], r["L"]), []).append(r)
    rows, fails = [], []
    for reg in REGISTERS:
        for L in LENGTHS:
            rr = raw.get((reg, L), [])
            c = cells.get(f"{reg}|{L}")
            if not rr or c is None:
                fails.append((reg, L, "MISSING CELL"))
                continue
            th = nulls["lengths"][str(L)]["thresholds_at_alpha_ref"]
            t_en, t_p, t_pc = th["t_en"], th["t_pmax"], th["t_pcon"]
            env = [x["en"] for x in rr]
            pmv = [x["pmax"] for x in rr]
            pcv = [x["pcon"] for x in rr]
            pw = float(np.mean([v >= t_p for v in pmv]))
            rows.append({"register": reg, "L": L, "n": len(rr),
                         "_en_vals": env, "_pmax_vals": pmv,
                         "bars": {"t_en": t_en, "t_pmax": t_p, "t_pcon": t_pc},
                         "median_en": float(np.median(env)),
                         "power_legacy_bar": float(np.mean([v >= LEGACY_BAR for v in env])),
                         "power_en_matchedFP": float(np.mean([v >= t_en for v in env])),
                         "median_pmax": float(np.median(pmv)),
                         "power_pmax": pw,
                         "median_pcon": float(np.median(pcv)),
                         "power_pcon": float(np.mean([v >= t_pc for v in pcv])),
                         "median_z_own": c["median_z_own_model"],
                         "recovery": c["median_recovery"],
                         "median_ioc": c["median_ioc"], "median_mds": c["median_mds"],
                         "median_h2": c["median_h2"], "median_zl": c["median_zl"],
                         "argmax_register": c["argmax_register_mode"]})
            if pw < G_POWER_MIN:
                fails.append((reg, L, pw))
    out["gates"]["G-POWER"] = {
        "rule": f"power(pmax >= t_pmax at alpha_ref={ALPHA_REF}) >= {G_POWER_MIN} for every "
                f"register at every L in {LENGTHS}",
        "verdict": "PASSED" if not fails else "FAILED",
        "failing_cells": [{"register": r, "L": L, "power": p} for r, L, p in fails],
        "min_power_over_all_cells": min((r["power_pmax"] for r in rows), default=None),
        "worst_cell": min(rows, key=lambda r: r["power_pmax"]) if rows else None,
        "table": rows,
    }

    # ------------------------------------------------------------------ G-FP
    fp = {"rule": ("at matched per-decode FP alpha_ref, panel power >= single-scorer power "
                   "for every register at every L"),
          "per_length": {}, "regressions": []}
    for L in LENGTHS:
        nl = nulls["lengths"][str(L)]
        th = nl["thresholds_at_alpha_ref"]
        fp["per_length"][str(L)] = {
            "t_en": th["t_en"], "t_pmax": th["t_pmax"], "t_pcon": th["t_pcon"],
            "t_en_empirical": th["en_wrongkey_empirical"], "t_en_gpd": th["en_wrongkey_gpd"],
            "t_pmax_empirical": th["pmax_wrongkey_empirical"],
            "t_pmax_gpd": th["pmax_wrongkey_gpd"],
            "wrongkey_n": nl["wrongkey"]["en"]["n"],
            "random_rune_n": nl["random_rune"]["en"]["n"],
            "k_eff": nl["k_eff"], "k_eff_by_quantile": nl["k_eff_by_quantile"],
            "k_eff_with_poisson_ci": k_eff_ci(nl),
            "legacy_bar_fp_rate_wrongkey": th["legacy_bar_fp_rate_wrongkey"],
            "beam_inflation_pmax_mean": (nl["wrongkey"]["pmax"]["mean"]
                                         - nl["random_rune"]["pmax"]["mean"]),
            "beam_inflation_en_mean": (nl["wrongkey"]["en"]["mean"]
                                       - nl["random_rune"]["en"]["mean"]),
        }
    for r in rows:
        if r["power_pmax"] < r["power_en_matchedFP"] - 1e-9:
            fp["regressions"].append({"register": r["register"], "L": r["L"],
                                      "power_panel": r["power_pmax"],
                                      "power_single_scorer": r["power_en_matchedFP"]})
    fp["verdict"] = "PASSED" if not fp["regressions"] else "FAILED"
    out["gates"]["G-FP"] = fp

    # ------------------------------------------------------------------ G-LP1
    lp1 = {"rule": f"LP1_REAL median legacy score_norm >= {G_LP1_MIN_EN} and 100% of "
                   f"replicates clear the legacy bar {LEGACY_BAR}, at every L",
           "per_length": {}}
    ok = True
    for L in LENGTHS:
        c = cells.get(f"LP1_REAL|{L}")
        if c is None:
            ok = False
            lp1["per_length"][str(L)] = {"error": "MISSING"}
            continue
        good = c["median_en"] >= G_LP1_MIN_EN and c["power_legacy_bar"] >= 1.0
        ok = ok and good
        lp1["per_length"][str(L)] = {
            "median_en": c["median_en"], "power_legacy_bar": c["power_legacy_bar"],
            "median_pmax": c["median_pmax"], "power_pmax": c["power_pmax_matchedFP"],
            "n": c["n"], "held_out": "leave-one-page-out", "ok": good}
    lp1["verdict"] = "PASSED" if ok else "FAILED"
    out["gates"]["G-LP1"] = lp1

    # ------------------------------------------------------------------ G-SPEED
    out["gates"]["G-SPEED"] = speed["gate_G_SPEED"] | {
        "per_length": {k: {"us_adjudicate": v["us_adjudicate_full"],
                           "us_score_norm": v["us_score_norm_only"],
                           "ratio": v["ratio_vs_score_norm"],
                           "us_batch_panel_only": v["us_adjudicate_batch_panel_only_per_row"]}
                       for k, v in speed["lengths"].items()}}

    # ------------------------------------------------------------------ markdown
    md = []
    md.append("| register | L | legacy `en` (L7-A) | legacy power | **panel `pmax`** | "
              "**panel power** | `pcon` | `pcon` power | own-model z | recovery |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for reg in REGISTERS:
        for L in LENGTHS:
            r = next((x for x in rows if x["register"] == reg and x["L"] == L), None)
            if not r:
                continue
            l7 = L7A[reg]
            md.append(f"| `{reg}` | {L} | {r['median_en']:.2f} _(L7-A {l7[0]:.2f})_ | "
                      f"{r['power_legacy_bar']:.2f} _(L7-A {l7[1]:.2f})_ | "
                      f"**{r['median_pmax']:.1f}** | **{r['power_pmax']:.2f}** | "
                      f"{r['median_pcon']:.1f} | {r['power_pcon']:.2f} | "
                      f"{r['median_z_own']:.1f} | {r['recovery']:.0%} |")
    out["markdown_power_table"] = "\n".join(md)

    # --- how well does each R3 language-agnostic statistic actually separate? -----------
    # PREREG s2.2 committed to persisting BOTH h2 and zl and REPORTING the measured
    # separation of both rather than asserting which is better.  This is that measurement.
    DIRECTION = {"ioc": +1, "mds": -1, "h2": +1, "zl": -1}   # +1: structured = larger
    agn = {}
    for L in LENGTHS:
        nl = nulls["lengths"][str(L)]["wrongkey"]
        ent = {}
        for stat, sgn in DIRECTION.items():
            mu, sd = nl[stat]["mean"], nl[stat]["sd"]
            per = {}
            for reg in REGISTERS:
                c = cells.get(f"{reg}|{L}")
                if not c:
                    continue
                v = c[f"median_{stat}"]
                per[reg] = {"plant_median": v, "z_vs_null": sgn * (v - mu) / sd if sd else None}
            ent[stat] = {"null_mean": mu, "null_sd": sd, "direction":
                         "higher = more structured" if sgn > 0 else
                         "lower = more structured",
                         "per_register": per,
                         "min_abs_z_over_registers": min(
                             (abs(p["z_vs_null"]) for p in per.values()
                              if p["z_vs_null"] is not None), default=None)}
        agn[str(L)] = ent
    out["agnostic_statistic_separation"] = agn
    out["supplementary_far_tail"] = far_tail(nulls, rows)
    for r in rows:                                     # drop the raw vectors before dump
        r.pop("_en_vals", None)
        r.pop("_pmax_vals", None)

    json.dump(out, open(os.path.join(HERE, "out_gates.json"), "w"), indent=1)
    print("=" * 78)
    for g, v in out["gates"].items():
        print(f"{g:10s} {v['verdict']}")
    print("=" * 78)
    print(out["markdown_power_table"])
    print("\nk_eff by length:",
          {L: round(fp["per_length"][str(L)]["k_eff"], 2) for L in LENGTHS})
    print("wrote out_gates.json")


if __name__ == "__main__":
    main()
