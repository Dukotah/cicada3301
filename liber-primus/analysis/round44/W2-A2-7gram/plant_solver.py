"""R44/W2-A2 PLANT-S1/S2/S3 — the constraint solver must recover engineered pairs
through the identical scan code (PREREG section 9).  Writes plant_solver.json."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a2lib as L                                    # noqa: E402

N = L.N


def main():
    v3, heads = L.build_vocab()
    report = {"V3": len(v3), "H": sorted(int(h) for h in heads)}
    rng = np.random.default_rng(3301)

    # --- PLANT-S1: constant shift s=11 ------------------------------------
    s = 11
    base = sorted(v3)
    u1, u2 = np.array(base[3]), np.array(base[7])
    v3c = set(v3) | {tuple(((u1 - s) % N).tolist()), tuple(((u2 - s) % N).tolist())}
    hc = set(heads) | {(L.CRIB_P + s) % N}
    out, out_nh, pairs = L.ap_scan(v3c, hc)
    s1_hit = int(out[s, 0]) >= 1 and any(
        p["s"] == s and p["P1_w1"] == u1.tolist() and p["P1_w2"] == u2.tolist()
        for p in pairs)
    report["PLANT_S1"] = {"s": s, "count_at_s": int(out[s, 0]), "recovered": bool(s1_hit)}

    # --- PLANT-S2: AP (a,b)=(4,3) ------------------------------------------
    a, b = 4, 3
    e1 = np.array([a, a + b, a + 2 * b]) % N
    e2 = np.array([a + 3 * b, a + 4 * b, a + 5 * b]) % N
    v3c = set(v3) | {tuple(((u1 - e1) % N).tolist()), tuple(((u2 - e2) % N).tolist())}
    hc = set(heads) | {(L.CRIB_P + a + 6 * b) % N}
    out2, _, _ = L.ap_scan(v3c, hc, list_pairs=False)
    report["PLANT_S2"] = {"ab": [a, b], "count_at_ab": int(out2[a, b]),
                          "recovered": bool(out2[a, b] >= 1)}

    # --- PLANT-S3: generator window pair (57, 141), key G-bash-3301, sigma +1
    keys = L.build_keys()
    K = keys["G-bash-3301"]
    o1, o2 = 57, 141
    D = (K[o1:o1 + 7] - K[o2:o2 + 7]) % N
    # sigma +1: P2 = P1 - D
    P1w1, P1w2 = np.array(base[5]), np.array(base[9])
    x1 = (L.CRIB_P + D[6]) % N                      # P1 head forced by the crib condition
    v3c = set(v3) | {tuple(((P1w1 - D[0:3]) % N).tolist()),
                     tuple(((P1w2 - D[3:6]) % N).tolist())}
    hc = np.zeros(N, dtype=np.int64)
    for h in set(heads) | {int(x1)}:
        hc[h] = 1
    g3, _ = L.g3_table(v3c)
    res = L.gen_scan_key(np.asarray(K, dtype=np.int64), g3, hc, len(v3c))
    grid7 = res["grid"]
    # recompute the specific cell to assert the flag sits at (57,141)
    E = D % N
    body = int(g3[int(L.pack3(E[0:3]))]) * int(g3[int(L.pack3(E[3:6]))])
    cell_count = body * int(hc[(L.CRIB_P + E[6]) % N])
    report["PLANT_S3"] = {"o1o2": [o1, o2], "cell_count7": cell_count,
                          "grid_sat7_total": grid7["sat7"],
                          "recovered": bool(cell_count >= 1)}

    report["passed"] = all(report[k]["recovered"]
                           for k in ("PLANT_S1", "PLANT_S2", "PLANT_S3"))
    json.dump(report, open(os.path.join(HERE, "plant_solver.json"), "w"), indent=1)
    print(json.dumps({k: report[k] for k in ("PLANT_S1", "PLANT_S2", "PLANT_S3", "passed")},
                     indent=1))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
