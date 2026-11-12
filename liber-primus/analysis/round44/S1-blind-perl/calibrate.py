"""Lane S1 calibration: throughput, the null on random (non-Perl) keys, and plant power through the C kernel.

No Perl seed is evaluated against the real ciphertext here. Output: calibration.json.
"""
import json
import os
import random
import sys
import tempfile
import time

import common as cm

N_NULL = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
out = {}
C0 = cm.build()
rng = random.Random(44_001)
T = cm.plant_texts()


def pct(hist, q):
    tot = sum(hist); acc = 0
    for v in range(len(hist) - 1, -1, -1):
        acc += hist[v]
        if acc > q * tot:
            return v + 1                   # smallest threshold with pass rate <= q
    return 0


for L1 in (64, 80, 96):
    t0 = time.time()
    _, H = cm.run_kernel("rnd", 0, N_NULL, cm.PAGE0, L1, 10 ** 6, 120, 10 ** 6, 262, hist=True)
    dt = time.time() - t0
    thr = [pct(H[m], 0.03) for m in range(4)]
    out[f"L1={L1}"] = {"seconds_per_million_seeds": dt / (N_NULL / 1e6), "T1_3pct_by_mode": thr,
                       "T1_ioc_x29": [cm.ioc29(t, L1) for t in thr],
                       "null_mean_ioc_x29": [cm.ioc29(sum(v * h for v, h in enumerate(H[m])) / sum(H[m]), L1) for m in range(4)]}
    print(f"L1={L1}: {dt / (N_NULL / 1e6):.2f} s per 1e6 seeds (4 modes)  T1(3%) ssq {thr} = IoCx29 {[round(x, 3) for x in out[f'L1={L1}']['T1_ioc_x29']]}", flush=True)

# plants through the kernel: every stage statistic for the TRUE mode
plants = []
with tempfile.TemporaryDirectory() as td:
    kf, cf = os.path.join(td, "k.txt"), os.path.join(td, "c.txt")
    for tname, stream in T.items():
        for variant in cm.VARIANTS:
            for cons, q in (("keyskip1", 1), ("skip_by_two", 2), ("coin_from_key", 2)):
                for sign in (+1, -1):
                    for rep in range(6):
                        K = [rng.randrange(cm.N) for _ in range(420)]
                        Cp, info = cm.make_plant(rng, stream, variant, cons, K, L=262, sign=sign)
                        open(kf, "w").write(" ".join(map(str, K))); open(cf, "w").write(" ".join(map(str, Cp)))
                        row = {"text": tname, "variant": variant, "construction": cons, "sign": sign}
                        mode = (0 if sign == +1 else 2) + (q - 1)
                        for L1 in (64, 80, 96):
                            recs, _ = cm.run_kernel("file:" + kf, 0, 1, cf, L1, 0, 120, 0, 262)
                            r = [x for x in recs if x[1] == mode][0]
                            row[f"v1_L{L1}"] = r[2]; row["v2"] = r[3]; row["v3"] = r[4]
                        plants.append(row)
out["plants"] = plants
for L1 in (64, 80, 96):
    thr = out[f"L1={L1}"]["T1_3pct_by_mode"]
    ok = sum(1 for p in plants if p[f"v1_L{L1}"] >= thr[(0 if p["sign"] == 1 else 2) + (0 if p["construction"] == "keyskip1" else 1)])
    out[f"L1={L1}"]["plant_pass_at_T1"] = ok / len(plants)
    print(f"L1={L1}: plants passing the 3% null threshold: {ok}/{len(plants)} = {ok / len(plants):.3f}")
v2 = sorted(cm.ioc29(p["v2"], 120) for p in plants); v3 = sorted(cm.ioc29(p["v3"], 262) for p in plants)
print("plants IoCx29 at L=120: min %.3f  1%% %.3f  5%% %.3f  median %.3f" % (v2[0], v2[len(v2) // 100], v2[len(v2) // 20], v2[len(v2) // 2]))
print("plants IoCx29 at L=262: min %.3f  1%% %.3f  5%% %.3f  median %.3f" % (v3[0], v3[len(v3) // 100], v3[len(v3) // 20], v3[len(v3) // 2]))
out["plant_ioc_L120"] = {"min": v2[0], "p01": v2[len(v2) // 100], "p05": v2[len(v2) // 20], "median": v2[len(v2) // 2]}
out["plant_ioc_L262"] = {"min": v3[0], "p01": v3[len(v3) // 100], "p05": v3[len(v3) // 20], "median": v3[len(v3) // 2]}
json.dump(out, open(os.path.join(cm.HERE, "calibration.json"), "w"), indent=1)
