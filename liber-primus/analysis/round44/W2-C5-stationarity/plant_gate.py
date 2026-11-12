"""R44 / W2-C5 plant gate — specificity + power curve, BEFORE any real-data run.

Plant = synthetic book, real page lengths, pages 19/24/27/29/44 at k * R_GLOBAL
(k = 5.173 == unfiltered, the literal A4-H10 mechanism). Every replicate runs the
FULL registered procedure (census -> stats -> own D=2,000 bootstrap -> decision rule).
"""
import json
import time

import numpy as np

import c5lib as C


def main():
    t0 = time.time()
    rng = np.random.default_rng(3301)
    real = C.real_pages()
    c_real, m_real = C.page_counts(real)
    page_lens = [len(p) for p in real]
    elev = set(C.FLAGGED)

    ks = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, round(C.K_UNFILTERED, 4)]
    out = {
        "date": "2026-11-09",
        "seed": 3301,
        "R": C.R_PLANT,
        "D_plant": C.D_PLANT,
        "bar_per_test": C.BAR_PER_TEST,
        "r_global": C.R_GLOBAL,
        "p_keep_global": C.p_keep_of_rate(C.R_GLOBAL),
        "k_unfiltered": C.K_UNFILTERED,
        "elevated_pages": sorted(elev),
        "curve": [],
    }

    for k in ks:
        fires = 0
        per_test = {"G": 0, "Z": 0, "minp": 0}
        mean_elev_count = 0.0
        for rep in range(C.R_PLANT):
            book = C.plant_book(page_lens, elev, min(k, C.K_UNFILTERED), rng)
            c, m = C.page_counts(book)
            res = C.test_pvalues(c, m, C.D_PLANT, rng)
            if C.fired(res):
                fires += 1
            per_test["G"] += res["p_G"] <= C.BAR_PER_TEST
            per_test["Z"] += res["p_Z"] <= C.BAR_PER_TEST
            per_test["minp"] += res["p_minp"] <= C.BAR_PER_TEST
            mean_elev_count += c[sorted(elev)].sum()
        row = {
            "k": k,
            "power_any": fires / C.R_PLANT,
            "power_G": per_test["G"] / C.R_PLANT,
            "power_Z": per_test["Z"] / C.R_PLANT,
            "power_minp": per_test["minp"] / C.R_PLANT,
            "mean_doublets_on_5_elev_pages": mean_elev_count / C.R_PLANT,
        }
        out["curve"].append(row)
        print(f"k={k:<6} power_any={row['power_any']:.3f} "
              f"(G {row['power_G']:.3f} / Z {row['power_Z']:.3f} / minp {row['power_minp']:.3f}) "
              f"elev-page doublets ~{row['mean_doublets_on_5_elev_pages']:.1f}", flush=True)

    spec = out["curve"][0]["power_any"]
    p_at_unf = out["curve"][-1]["power_any"]
    out["specificity_false_fire_rate_k1"] = spec
    out["gate_power_at_unfiltered"] = p_at_unf
    out["gate_pass"] = bool(p_at_unf >= 0.8 and spec <= 0.03)
    mde80 = next((r["k"] for r in out["curve"][1:] if r["power_any"] >= 0.8), None)
    mde50 = next((r["k"] for r in out["curve"][1:] if r["power_any"] >= 0.5), None)
    out["mde_k_power80"] = mde80
    out["mde_k_power50"] = mde50
    out["elapsed_s"] = round(time.time() - t0, 1)
    with open("plants.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"GATE {'PASS' if out['gate_pass'] else 'FAIL'}: power@unfiltered={p_at_unf:.3f}, "
          f"specificity={spec:.4f}, MDE(0.8)={mde80}, MDE(0.5)={mde50}, "
          f"{out['elapsed_s']}s")


if __name__ == "__main__":
    main()
