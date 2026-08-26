"""I3 / Round 19 — turn `calib19.json` + `out_*.json` into the tables RESULTS.md publishes,
and evaluate every pre-registered gate.

    python3 summary.py            # prints markdown, writes out_summary.json
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import nullcurve19 as NC          # noqa: E402

A = NC.ALPHA_ROUND19


def cells():
    return NC.calib()["cells"]


def bar(c, n, alpha=A):
    return NC._fw(n, c["mu"], c["beta"], alpha)


def g(c, key="gcal_a01"):
    r = c.get(key, {})
    per = r.get("per_block", {})
    gate = [v for v in per.values() if v["gating"]]
    worst = max((abs(v["ratio"] - 1) for v in gate), default=float("nan"))
    sign = ""
    if gate:
        w = max(gate, key=lambda v: abs(v["ratio"] - 1))
        sign = "conservative" if w["ratio"] < 1 else "ANTI-conservative"
    return r.get("passed"), worst, sign, len(gate)


def scaling_law():
    """beta ~ L^-p and mu(L), fitted across the measured (L, bw=400) EN_QUAD cells."""
    pts = []
    for k, c in cells().items():
        if c.get("register") == "EN_QUAD" and c.get("mode") == "keyskip1" \
                and c.get("beam_w", 400) == 400 and "|bw" not in k:
            pts.append((c["L"], c["mu"], c["beta"], c["M"]))
    pts.sort()
    out = {"points": [{"L": L, "mu": m, "beta": b, "M": M} for L, m, b, M in pts]}
    if len(pts) >= 2:
        xs = [math.log(p[0]) for p in pts]
        ys = [math.log(p[2]) for p in pts]
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        sxx = sum((x - mx) ** 2 for x in xs)
        p_exp = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
        out["beta_exponent"] = p_exp        # beta ~ L^p_exp ; 1/sqrt(L) would be -0.5
        out["beta_at_L120_implied"] = math.exp(my + p_exp * (math.log(120) - mx))
    # beam_w=120 family
    pts2 = sorted((c["L"], c["mu"], c["beta"], c["M"]) for k, c in cells().items()
                  if c.get("register") == "EN_QUAD" and c.get("beam_w") == 120)
    out["points_bw120"] = [{"L": L, "mu": m, "beta": b, "M": M} for L, m, b, M in pts2]
    if len(pts2) >= 2:
        xs = [math.log(p[0]) for p in pts2]
        ys = [math.log(p[2]) for p in pts2]
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        sxx = sum((x - mx) ** 2 for x in xs)
        out["beta_exponent_bw120"] = sum((x - mx) * (y - my)
                                         for x, y in zip(xs, ys)) / sxx
    return out


def legacy_check():
    """The repo's published constants vs this lane's 1e6-sample measurement at L=120."""
    c = cells().get("EN_QUAD|keyskip1|L120")
    if not c:
        return None
    rows = []
    for n in (10 ** 6, 10 ** 8, 3.13e8, 10 ** 9, 10 ** 10, 1.7058157809e10):
        rows.append({"N": n,
                     "legacy_threshold_for": NC.threshold_for(n),
                     "legacy_uncapped": NC._fw(n, NC.DEFAULT_MU, NC.DEFAULT_BETA, A),
                     "measured_uncapped": NC._fw(n, c["mu"], c["beta"], A),
                     "delta_measured_minus_legacy":
                         NC._fw(n, c["mu"], c["beta"], A)
                         - NC._fw(n, NC.DEFAULT_MU, NC.DEFAULT_BETA, A)})
    return {"published_mu": NC.DEFAULT_MU, "published_beta": NC.DEFAULT_BETA,
            "measured_mu": c["mu"], "measured_beta": c["beta"], "M": c["M"],
            "beta_rel_error_of_published": (NC.DEFAULT_BETA - c["beta"]) / c["beta"],
            "mu_abs_error_of_published": NC.DEFAULT_MU - c["mu"],
            "rows": rows}


def mode_curve():
    p = os.path.join(HERE, "out_modes.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    base = cells().get("EN_QUAD|keyskip1|L120")
    rows = []
    for r in d.get("curve", []):
        row = dict(r)
        if base:
            row["shift_mu_vs_keyskip1"] = r["mu"] - base["mu"]
            row["bar_shift_1e6"] = (NC._fw(1e6, r["mu"], r["beta"], A)
                                    - NC._fw(1e6, base["mu"], base["beta"], A))
        rows.append(row)
    if base:
        rows.insert(0, {"mode": "keyskip1", "lam": float("inf"), "mu": base["mu"],
                        "beta": base["beta"], "mean": base["single_mean"],
                        "realised_drift": None, "shift_mu_vs_keyskip1": 0.0,
                        "bar_shift_1e6": 0.0, "M": base["M"],
                        "bar_1e6_a01": NC._fw(1e6, base["mu"], base["beta"], A)})
    return rows


def i1_curve():
    rows = []
    base = None
    for k, c in cells().items():
        if not k.startswith("I19:"):
            continue
        rows.append({"cell": k, "instrument": c.get("instrument"),
                     "statistic": c.get("statistic_name"), "L": c["L"], "M": c["M"],
                     "mu": c["mu"], "beta": c["beta"],
                     "bar_1e4": bar(c, 1e4), "bar_1e6": bar(c, 1e6),
                     "bar_1e6_escalate": bar(c, 1e6, NC.ALPHA_ESCALATE),
                     "single_max": c["single_max"], "status": c["status"],
                     "gcal": g(c)[0], "gcal_worst_dev": g(c)[1], "gcal_sign": g(c)[2],
                     "gev_xi": (c["gev"] or {}).get("xi"),
                     "gumbel_rejected": (c["gev"] or {}).get("gumbel_rejected"),
                     "preset": c.get("preset")})
    rows.sort(key=lambda r: (r["statistic"] or "", r["instrument"] or ""))
    return rows


def gate_verdicts():
    v = {}
    cs = cells()
    # G-CAL
    published = [(k, c) for k, c in cs.items() if c.get("M", 0) >= 1_000_000]
    gc = [(k, *g(c)) for k, c in published]
    v["G-CAL"] = {
        "cells_at_M_ge_1e6": len(published),
        "passed_cells": sum(1 for r in gc if r[1]),
        "failed_cells": [r[0] for r in gc if not r[1]],
        "worst_deviation": max((r[2] for r in gc), default=None),
        "all_failures_conservative": all(r[3] == "conservative" for r in gc if not r[1]),
        "provisional_cells": sorted(k for k, c in cs.items() if c.get("M", 0) < 1_000_000),
    }
    v["G-CAL"]["verdict"] = ("PASSED" if v["G-CAL"]["passed_cells"] == len(published)
                             else "PARTIAL")
    # G-CAL-X
    ex = []
    for k, c in cs.items():
        for b, r in (c.get("extrapolation_check") or {}).items():
            ex.append((k, b, r["residual_gumbel_sd"], r["within_1sd"]))
    v["G-CAL-X"] = {"n_checks": len(ex), "n_within_1sd": sum(1 for e in ex if e[3]),
                    "worst": max(ex, key=lambda e: abs(e[2]), default=None),
                    "verdict": "PASSED" if ex and all(e[3] for e in ex) else
                               ("PARTIAL" if ex else "NOT RUN")}
    # GEV shape (PREREG H1)
    gv = [(k, (c["gev"] or {}).get("xi"), (c["gev"] or {}).get("gumbel_rejected"))
          for k, c in cs.items() if c.get("gev")]
    v["GEV"] = {"n": len(gv), "n_gumbel_rejected": sum(1 for r in gv if r[2]),
                "xi_range": [min((r[1] for r in gv), default=None),
                             max((r[1] for r in gv), default=None)],
                "all_negative": all((r[1] or 0) < 0 for r in gv)}
    return v


def md(x, nd=4):
    return "—" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def main():
    out = {"scaling_law": scaling_law(), "legacy_check": legacy_check(),
           "mode_curve": mode_curve(), "i1_cells": i1_curve(),
           "gates": gate_verdicts()}
    p = os.path.join(HERE, "out_registers_L120.json")
    if os.path.exists(p):
        out["panel_L120"] = json.load(open(p, encoding="utf-8")).get("panel")
    p = os.path.join(HERE, "out_i2panel_L120.json")
    if os.path.exists(p):
        out["i2_panel_L120"] = json.load(open(p, encoding="utf-8")).get("panel")
    json.dump(out, open(os.path.join(HERE, "out_summary.json"), "w", encoding="utf-8"),
              indent=1, default=float)

    lc = out["legacy_check"]
    if lc:
        print("### legacy L=120 cell vs benchmark/null.py")
        print(f"published mu={lc['published_mu']} beta={lc['published_beta']}")
        print(f"measured  mu={lc['measured_mu']:.4f} beta={lc['measured_beta']:.5f} "
              f"(M={lc['M']:,})")
        print(f"published beta is {100*lc['beta_rel_error_of_published']:+.1f} % vs measured; "
              f"mu off by {lc['mu_abs_error_of_published']:+.4f}")
        print(f"| N | legacy threshold_for | legacy uncapped | measured | delta |")
        print("|---|---|---|---|---|")
        for r in lc["rows"]:
            print(f"| {r['N']:,.0f} | {r['legacy_threshold_for']:.4f} | "
                  f"{r['legacy_uncapped']:.4f} | {r['measured_uncapped']:.4f} | "
                  f"{r['delta_measured_minus_legacy']:+.4f} |")
    sl = out["scaling_law"]
    print("\n### beta(L) scaling, beam_w=400")
    for pt in sl["points"]:
        print(f"  L={pt['L']:5d}  mu={pt['mu']:8.4f}  beta={pt['beta']:.5f}  M={pt['M']:,}")
    if "beta_exponent" in sl:
        print(f"  fitted beta ~ L^{sl['beta_exponent']:.3f}  (1/sqrt(L) would be -0.500)")
    if sl.get("points_bw120"):
        print("### beta(L) scaling, beam_w=120 (R17's setting)")
        for pt in sl["points_bw120"]:
            print(f"  L={pt['L']:5d}  mu={pt['mu']:8.4f}  beta={pt['beta']:.5f}  M={pt['M']:,}")
        if "beta_exponent_bw120" in sl:
            print(f"  fitted beta ~ L^{sl['beta_exponent_bw120']:.3f}")
    mc = out["mode_curve"]
    if mc:
        print("\n### decoder-mode (permissiveness) curve, EN_QUAD, L=120")
        print("| mode | lam | realised drift | mu | beta | null mean | bar@1e6 | shift vs keyskip1 | M |")
        print("|---|---|---|---|---|---|---|---|---|")
        for r in mc:
            print(f"| {r['mode']} | {r['lam']} | {md(r.get('realised_drift'))} | "
                  f"{r['mu']:.4f} | {r['beta']:.5f} | {r['mean']:.4f} | "
                  f"{r['bar_1e6_a01']:.4f} | {md(r.get('bar_shift_1e6'),3)} | {r['M']:,} |")
    if out["i1_cells"]:
        print("\n### the actual Round-19 instrument (I1 x I2)")
        print("| cell | L | M | mu | beta | bar@1e4 | bar@1e6 | observed null max | status |")
        print("|---|---|---|---|---|---|---|---|---|")
        for r in out["i1_cells"]:
            print(f"| {r['cell']} | {r['L']} | {r['M']:,} | {r['mu']:.4f} | {r['beta']:.5f} | "
                  f"{r['bar_1e4']:.4f} | {r['bar_1e6']:.4f} | {r['single_max']:.4f} | "
                  f"{r['status']} |")
    print("\n### gates")
    print(json.dumps(out["gates"], indent=1, default=str))
    return out


if __name__ == "__main__":
    main()
