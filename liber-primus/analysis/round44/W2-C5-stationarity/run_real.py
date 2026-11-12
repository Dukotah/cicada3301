"""R44 / W2-C5 real run — the registered three-test procedure on the canon U stream.

Pre-conditions (PREREG order of operations): plant gate PASSED (plants.json gate_pass true).
Census must reproduce R12-D2 / W2-B3 exactly or this halts.
"""
import json
import time

import numpy as np

import c5lib as C


def main():
    t0 = time.time()
    gate = json.load(open("plants.json"))
    assert gate["gate_pass"], "plant gate not passed - real run forbidden"

    pages = C.real_pages()
    c, m = C.page_counts(pages)
    # cross-checks against the pinned record
    b3 = json.load(open("../W2-B3-doublet-sites/results.json"))["real_sites_U86"]["pagecounts"]
    assert list(map(int, c)) == list(map(int, b3)), "census mismatch vs W2-B3 pinned tuple"
    assert int(c.sum()) == 86 and int(m.sum()) == 12_901

    rng = np.random.default_rng(3302)
    res = C.test_pvalues(c, m, C.D_REAL, rng)

    pv = res.pop("page_pvals")
    flagged = {int(i): {"count": int(c[i]), "pairs": int(m[i]),
                        "rate": float(c[i] / m[i]),
                        "exact_p": float(pv[i]),
                        "bonf55_p": float(min(1.0, pv[i] * 55)),
                        "fires_at_bar": bool(pv[i] <= C.BAR_PAGE)}
               for i in C.FLAGGED}

    out = {
        "date": "2026-11-09",
        "seed": 3302,
        "D": C.D_REAL,
        "bar_per_test": C.BAR_PER_TEST,
        "bar_page_bonf55": C.BAR_PAGE,
        "census": {"n_runes": 12_956, "pages": 55, "doublets_within_page": int(c.sum()),
                   "within_page_pairs": int(m.sum()), "r_hat": res["r_hat"]},
        "tests": {
            "T1_G": {"stat": res["G"], "p": res["p_G"], "fired": bool(res["p_G"] <= C.BAR_PER_TEST)},
            "T2_tarone_Z": {"stat": res["Z"], "p": res["p_Z"], "fired": bool(res["p_Z"] <= C.BAR_PER_TEST)},
            "T3_minp": {"stat": res["minp"], "p": res["p_minp"], "fired": bool(res["p_minp"] <= C.BAR_PER_TEST)},
        },
        "any_fired": bool(res["p_G"] <= C.BAR_PER_TEST or res["p_Z"] <= C.BAR_PER_TEST
                          or res["p_minp"] <= C.BAR_PER_TEST),
        "flagged_pages": flagged,
        "per_page": {"counts": list(map(int, c)), "pairs": list(map(int, m)),
                     "exact_upper_p": [float(x) for x in pv]},
        "power_context_from_plants": {
            "power_at_unfiltered_k5.173": gate["gate_power_at_unfiltered"],
            "power_curve": [(r["k"], r["power_any"]) for r in gate["curve"]],
            "mde_k_power80": gate["mde_k_power80"],
            "mde_k_power50": gate["mde_k_power50"],
        },
        "elapsed_s": round(time.time() - t0, 1),
    }
    with open("results.json", "w") as f:
        json.dump(out, f, indent=1)

    print(f"T1 G={res['G']:.2f} p={res['p_G']:.4f} | T2 Z={res['Z']:.3f} p={res['p_Z']:.4f} | "
          f"T3 minp={res['minp']:.5f} family-p={res['p_minp']:.4f} | bar {C.BAR_PER_TEST:.5f} | "
          f"ANY FIRED: {out['any_fired']}")
    for i, d in flagged.items():
        print(f"  page {i}: {d['count']}/{d['pairs']} ({100*d['rate']:.2f}%) exact p={d['exact_p']:.4f} "
              f"bonf55={d['bonf55_p']:.3f} fires={d['fires_at_bar']}")


if __name__ == "__main__":
    main()
