"""I3 / Round 19 — G-HONEST. Re-derive the bar each past sweep SHOULD have used at its own
trial count, segment length and beam width, and tabulate it against the bar it actually used.

L7-C already suspected that some sweeps were compared against a fixed -5.5 out of habit.
This lane can now answer it quantitatively, because it has measured (mu, beta) at the
geometries the sweeps actually ran at, rather than at the single geometry
`benchmark/null.py` was calibrated on.

Every fact in SWEEPS below is cited to a file and a JSON key. Nothing here is inferred from
prose.

    python3 ghonest.py        # -> out_ghonest.json, and a printed table
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import nullcurve19 as NC          # noqa: E402

A_CLAIM = 0.01
A_ESC = 0.05

# ---------------------------------------------------------------------------------------
# The record. n_enum = candidates enumerated; n_adj = decodes actually scored on the
# score_norm scale (the statistic the bar is a bar for).
# ---------------------------------------------------------------------------------------
SWEEPS = [
    dict(id="R13-B04-A", n_enum=1_385_600, n_adj=1_385_600, L=120, bw=400, ms=3,
         bar_used=-5.5, best=-6.185272398068207, tf_called=False, tf_n=None, tf_value=None,
         bar_rule="fixed -5.5 (PREREG s5: max(-5.5, null_max+0.5) with null_max=-6.826, floor binds)",
         cite="round13/B04/results_A.json {n_decodes,best_score,bar}; sweep.py:31 BAR=-5.5; harness.py:28-31"),
    dict(id="R13-B04-B", n_enum=1_290_240, n_adj=1_290_240, L=120, bw=400, ms=3,
         bar_used=-5.5, best=-6.129256156699389, tf_called=False, tf_n=None, tf_value=None,
         bar_rule="fixed -5.5", cite="round13/B04/results_B.json"),
    dict(id="R13-B04-C", n_enum=3_548_160, n_adj=3_548_160, L=100, bw=400, ms=3,
         bar_used=-5.5, best=-5.8852781358815305, tf_called=False, tf_n=None, tf_value=None,
         bar_rule="fixed -5.5 (per-page segments, L=min(100, page))",
         cite="round13/B04/results_C.json; harness.page_segments(L=PAGE_L=100)"),
    dict(id="R13-B04-D1", n_enum=150, n_adj=150, L=262, bw=400, ms=3,
         bar_used=-5.5, best=-6.653807964146638, tf_called=False, tf_n=None, tf_value=None,
         bar_rule="fixed -5.5 (full page 0)", cite="round13/B04/results_D.json[0]"),
    dict(id="R13-B04-D2", n_enum=150, n_adj=150, L=12956, bw=400, ms=3,
         bar_used=-5.5, best=-7.2387875104087245, tf_called=False, tf_n=None, tf_value=None,
         bar_rule="fixed -5.5 (full unsolved stream)", cite="round13/B04/results_D.json[1]"),
    dict(id="R16-KDF-A", n_enum=692_064, n_adj=692_064, L=120, bw=400, ms=3,
         bar_used=-5.5, best=-6.259433075138837, tf_called=False, tf_n=None, tf_value=None,
         bar_rule="max(-5.5, null_max+0.5), null_max=-6.7731 -> floor binds",
         cite="round16/KDF/results_A.json; round15/KDF/sweep.py:262"),
    dict(id="R16-PRNG", n_enum=52_556, n_adj=52_556, L=120, bw=400, ms=3,
         bar_used=-5.5, best=-6.347015698641356, tf_called=False, tf_n=None, tf_value=None,
         bar_rule="max(-5.5, null_max+0.5), null_max=-6.7091 -> floor binds",
         cite="round16/prng/results.json; prng_sweep.py:631"),
    dict(id="R17-P0-primary-ms3", n_enum=2_900_403_446, n_adj=5_554, L=400, bw=120, ms=3,
         bar_used=-5.5, best=-6.768547353763123, tf_called=True,
         tf_n=2_900_403_446, tf_value=-5.338550793999656,
         bar_rule="max(-5.5, null_max+0.5) per variant; threshold_for quoted at OFFSETS and at beams",
         cite="round17/P0_dense/results.json passes.primary_ms3; lib_padsweep.py:46,200"),
    dict(id="R17-P0-nibbles-ms3", n_enum=1_011_416_288, n_adj=1_042, L=400, bw=120, ms=3,
         bar_used=-5.5, best=-6.822498259552346, tf_called=True,
         tf_n=1_011_416_288, tf_value=-5.414929415869157,
         bar_rule="max(-5.5, null_max+0.5)", cite="round17/P0_dense/results.json passes.nibbles_ms3"),
    dict(id="R17-P0-ms8", n_enum=2_900_237_574, n_adj=3_869, L=400, bw=120, ms=8,
         bar_used=-5.5, best=-6.768547353763123, tf_called=True,
         tf_n=2_900_237_574, tf_value=-5.3385549403414005,
         bar_rule="max(-5.5, null_max+0.5)", cite="round17/P0_dense/results.json passes.max_skip_8"),
    dict(id="R17-P1-bitcoin", n_enum=1_389_182_016, n_adj=17_920, L=400, bw=120, ms=3,
         bar_used=-5.5, best=-6.801690421150176, tf_called=True,
         tf_n=1_389_182_016, tf_value=-5.391920563403858,
         bar_rule="max(-5.5, null_max+0.5) per variant per skip budget",
         cite="round17/P1_blockchain/results.json {n_offsets_total,best_overall,threshold_for_n_trials}; "
              "sweep.py:300 passes n_offsets_total; n_adj = 224 configs x 2 skip budgets x <=40"),
    dict(id="R17-P2-beacons", n_enum=3_464_597_548, n_adj=3_839, L=400, bw=120, ms=3,
         bar_used=-5.5, best=-6.810640700106527, tf_called=True,
         tf_n=3_464_597_548, tf_value=-5.3256641632154516,
         bar_rule="max(-5.5, null_max+0.5) per config",
         cite="round17/P2_beacons/results.json {coverage_total.beam_escalations, extreme_value_check}"),
    dict(id="R17-P3-tables", n_enum=2_466_258_498, n_adj=26_400, L=40, bw=120, ms=3,
         bar_used=-5.5, best=-6.419656065216985, tf_called=True,
         tf_n=2_466_258_498, tf_value=-5.3503064966353024,
         bar_rule="max(-5.5, null_max+0.5); nulls measured only for pad-bests",
         note="the BEST was scored on a 40-rune head, not 400; heads ranged 30..400",
         cite="round17/P3_tables/results.json; sweep.py:207-215 head_for(), :340 threshold_for(n_offsets)"),
    dict(id="R17-P3-tables-ms8", n_enum=3_291_058_250, n_adj=25_080, L=31, bw=120, ms=8,
         bar_used=-5.5, best=-5.679002000077624, tf_called=True,
         tf_n=3_291_058_250, tf_value=-5.329389743084673,
         bar_rule="max(-5.5, null_max+0.5); own ms8 null_max -6.088",
         note="R17's headline near-miss. Scored on a 31-rune head window.",
         cite="round17/P3_tables/results_ms8.json"),
]


# ---------------------------------------------------------------------------------------
def curve(L, bw):
    """(mu, beta, provenance) at a geometry, from measured cells where they exist.

    Where a cell does not exist, interpolate/extrapolate along the measured beta ~ 1/sqrt(L)
    law, anchoring on the nearest measured cell at the SAME beam width. Every such value is
    labelled so no reader mistakes it for a measurement.
    """
    cells = NC.calib()["cells"]
    exact = cells.get(f"EN_QUAD|keyskip1|L{L}|bw{bw}")
    if exact is None and bw == 400:
        exact = cells.get(f"EN_QUAD|keyskip1|L{L}")
    if exact is not None:
        return exact["mu"], exact["beta"], f"measured (M={exact['M']:,})"
    same_bw = []
    for k, v in cells.items():
        if v.get("register") != "EN_QUAD" or v.get("mode") != "keyskip1":
            continue
        vbw = v.get("beam_w", 400)
        if vbw != bw:
            continue
        same_bw.append(v)
    if not same_bw:
        return None, None, "NO MEASURED CELL AT THIS BEAM WIDTH"
    if len(same_bw) >= 2:
        # regress mu and log(beta) on 1/sqrt(L)
        xs = [1.0 / math.sqrt(v["L"]) for v in same_bw]
        mus = [v["mu"] for v in same_bw]
        lbs = [math.log(v["beta"]) for v in same_bw]
        n = len(xs)
        mx = sum(xs) / n
        sxx = sum((x - mx) ** 2 for x in xs) or 1e-12
        bmu = sum((x - mx) * (y - sum(mus) / n) for x, y in zip(xs, mus)) / sxx
        amu = sum(mus) / n - bmu * mx
        bb = sum((x - mx) * (y - sum(lbs) / n) for x, y in zip(xs, lbs)) / sxx
        ab = sum(lbs) / n - bb * mx
        x = 1.0 / math.sqrt(L)
        return (amu + bmu * x, math.exp(ab + bb * x),
                f"EXTRAPOLATED from {len(same_bw)} cells at bw={bw} via beta~1/sqrt(L)")
    v = same_bw[0]
    return (v["mu"], v["beta"] * math.sqrt(v["L"] / L),
            f"EXTRAPOLATED from L={v['L']} at bw={bw} via beta~1/sqrt(L)")


def main():
    rows = []
    for s in SWEEPS:
        mu, beta, prov = curve(s["L"], s["bw"])
        r = dict(s)
        r["mu"], r["beta"], r["curve_provenance"] = mu, beta, prov
        if mu is None:
            rows.append(r)
            continue
        r["bar_correct_claim"] = NC._fw(s["n_adj"], mu, beta, A_CLAIM)
        r["bar_correct_escalate"] = NC._fw(s["n_adj"], mu, beta, A_ESC)
        r["bar_at_n_enumerated"] = NC._fw(s["n_enum"], mu, beta, A_CLAIM)
        r["legacy_threshold_for_n_adj"] = NC.threshold_for(s["n_adj"])
        r["legacy_threshold_for_n_enum"] = NC.threshold_for(s["n_enum"])
        d = s["bar_used"] - r["bar_correct_claim"]
        r["discrepancy"] = d
        r["direction"] = ("STRICTER than needed (costs power)" if d > 0.02 else
                          "LOOSER than needed (false-positive risk)" if d < -0.02 else
                          "correct to within 0.02")
        r["verdict_used"] = "HIT" if s["best"] >= s["bar_used"] else "NOISE"
        r["verdict_correct"] = "HIT" if s["best"] >= r["bar_correct_claim"] else "NOISE"
        r["verdict_flips"] = r["verdict_used"] != r["verdict_correct"]
        r["margin_to_correct_bar"] = s["best"] - r["bar_correct_claim"]
        rows.append(r)
    out = {"alpha_claim": A_CLAIM, "alpha_escalate": A_ESC, "rows": rows,
           "n_verdicts_flipped": sum(1 for r in rows if r.get("verdict_flips")),
           "note": ("bar_used is what the sweep compared against; bar_correct_claim is the "
                    "family-wise bar at that sweep's OWN adjudicated decode count, segment "
                    "length and beam width, from this lane's measured null curves.")}
    json.dump(out, open(os.path.join(HERE, "out_ghonest.json"), "w", encoding="utf-8"),
              indent=1, default=float)

    hdr = (f"{'sweep':22s} {'N_enum':>15s} {'N_adj':>9s} {'L':>5s} {'bw':>4s} "
           f"{'used':>7s} {'correct':>8s} {'delta':>7s} {'best':>8s} {'flip':>5s}  provenance")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        if r.get("bar_correct_claim") is None:
            print(f"{r['id']:22s} {'-':>15s} {'':>9s} {r['L']:5d} {r['bw']:4d}  NO CELL")
            continue
        print(f"{r['id']:22s} {r['n_enum']:>15,} {r['n_adj']:>9,} {r['L']:5d} {r['bw']:4d} "
              f"{r['bar_used']:7.3f} {r['bar_correct_claim']:8.3f} {r['discrepancy']:7.3f} "
              f"{r['best']:8.3f} {str(r['verdict_flips']):>5s}  {r['curve_provenance']}")
    print(f"\nverdicts flipped: {out['n_verdicts_flipped']} / {len(rows)}")
    return out


if __name__ == "__main__":
    main()
