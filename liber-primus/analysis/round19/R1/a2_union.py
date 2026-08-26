"""R1 / sub-attack A, supplement — the CONSTRAINED route.

ADDENDUM 1 records that my first `union` model de-duplicated admissible key advances by
magnitude, so an even advance inherited the strict `exact` constraint and never got the looser
`by2` one. `union2` fixes that: every even advance is admissible under EITHER constraint.

This script also scans the drift penalty lambda more finely, because sub-attack A's main run
showed lambda=2.0 restores skip_by_two recovery to 0.98 while the null is still inflated.
"""
import json, os, random, statistics as st, time
from multiprocessing import Pool
import r1_lib as R
from a_permissive import correct_arm, null_arm, L_MAIN, NREP, NULL_N

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIGS = [
    ("union2/ms2", "union2", 2, 0.0),
    ("union2/ms3", "union2", 3, 0.0),
    ("union2/ms4", "union2", 4, 0.0),
    ("freepen3.0/ms3", "freepen", 3, 3.0),
    ("freepen6.0/ms3", "freepen", 3, 6.0),
    ("freepen10.0/ms3", "freepen", 3, 10.0),
]

def main():
    out = {"meta": {"started": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "note": "union2 = corrected union (ADDENDUM 1); lambda scan continued"},
           "frontier": []}
    with Pool(6) as pool:
        for (label, model, ms, lam) in CONFIGS:
            t0 = time.time()
            row = {"label": label, "model": model, "max_skip": ms, "lam": lam,
                   "mean_branching": R.mean_branching(model, ms)}
            for plant in ("keyskip", "skip2", "drift"):
                row[plant] = correct_arm(model, ms, lam, L_MAIN, plant, nrep=NREP)
            row["null"] = null_arm(model, ms, lam, L_MAIN, n=NULL_N, pool=pool)
            nb6 = row["null"].get("bar_1e+06")
            row["sec"] = time.time() - t0
            row["sep_keyskip_vs_bar1e6"] = row["keyskip"]["median_score"] - nb6
            row["sep_skip2_vs_bar1e6"] = row["skip2"]["median_score"] - nb6
            row["sep_drift_vs_bar1e6"] = row["drift"]["median_score"] - nb6
            row["passes_Ai_a"] = (row["skip2"]["median_score"] >= -5.5
                                  and row["skip2"]["median_recovery"] >= 0.80)
            row["passes_Ai_b"] = row["sep_skip2_vs_bar1e6"] >= 0.30
            out["frontier"].append(row)
            print(f"  {label:18s} branch {row['mean_branching']:5.3f} | "
                  f"keyskip {row['keyskip']['median_score']:7.3f} "
                  f"skip2 {row['skip2']['median_score']:7.3f}(rec {row['skip2']['median_recovery']:.2f}) "
                  f"drift {row['drift']['median_score']:7.3f} | null mean "
                  f"{row['null']['mean']:7.3f} max {row['null']['max']:7.3f} "
                  f"bar1e6 {nb6:7.3f} | A-i(a) {row['passes_Ai_a']} A-i(b) {row['passes_Ai_b']}"
                  f" | {row['sec']:.0f}s", flush=True)
    out["meta"]["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(out, open(os.path.join(HERE, "out_a2.json"), "w"), indent=1)
    print("wrote out_a2.json")

if __name__ == "__main__":
    main()
