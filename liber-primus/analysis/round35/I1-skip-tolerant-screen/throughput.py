import sys, os, json, time
import numpy as np
sys.dont_write_bytecode = True
LANE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(LANE, "..", "..", "round32", "B1-bash-random"))
from common import *
sys.path.insert(0, LANE); import pf_v4
pf_v3 = pf_v4.pf_v3
LMT = AD.panel().LMT.astype(np.float32)
C = np.array(U[:24], dtype=np.int8)
N = 1 << 18
seeds = np.array([(1325376000 & ~((1 << 20) - 1)) + i * 37 for i in range(N)], dtype=np.uint64)
def timeit(f, reps=2):
    best = 1e9
    for _ in range(reps):
        t = time.time(); f(); best = min(best, time.time() - t)
    return N / best
out = {"seeds": N, "variant": "bash4.2", "single_process": True}
r3 = timeit(lambda: pf_v3.prefilter_mask(seeds, "bash4.2", C, LMT, m=20))
out["pf_v3_m20_heads_per_s"] = r3
cfgs = {}
base = dict(pf_v4.FROZEN)
for (m, k, rel) in [(20, 1, "keyskip1"), (24, 1, "keyskip1"), (20, 2, "keyskip1"), (24, 2, "keyskip1"), (24, 2, "keyskip2"), (24, 1, "both"), (20, 2, "both"), (24, 2, "both")]:
    pf_v4.FROZEN.update(base); pf_v4.FROZEN["k"] = k
    rate = timeit(lambda: pf_v4.prefilter_mask(seeds, "bash4.2", C, LMT, m=m, rel=rel), reps=1)
    cfgs["m%d_k%d_%s" % (m, k, rel)] = {"heads_per_s": rate, "cost_vs_pf_v3_m20": r3 / rate}
out["pf_v4"] = cfgs
out["frozen_op_cost_vs_pf_v3"] = cfgs["m24_k2_both"]["cost_vs_pf_v3_m20"]
out["orbit_minutes_155M_seeds_frozen"] = 155189248 / cfgs["m24_k2_both"]["heads_per_s"] / 60
out["target_le_3x_met_for_frozen"] = bool(out["frozen_op_cost_vs_pf_v3"] <= 3)
json.dump(out, open(os.path.join(LANE, "throughput.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
