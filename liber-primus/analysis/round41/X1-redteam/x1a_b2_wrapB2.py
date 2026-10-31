"""Compare B2's own heads_off wrapper (imported unchanged) with an independent generator on fresh seeds."""
import os, sys, json, random, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import numpy as np
sp = importlib.util.spec_from_file_location("b2sweep", os.path.join(LP, "analysis", "round40", "B2-offsets", "sweep.py")); B = importlib.util.module_from_spec(sp); sys.modules["b2sweep"] = B; sp.loader.exec_module(B)
M64 = (1 << 64) - 1
def my_raws(seed, n):
    s = seed & M64; out = []
    while len(out) < n:
        if s == 0: s = 123459876
        h, l = divmod(s, 127773); s = (16807 * l - 2836 * h) & M64; out.append(s & 32767)
    return out
rng = random.Random(777); seeds = np.array([(rng.choice(B.S.PREF) << 20) | rng.randrange(1 << 20) for _ in range(300)], dtype=np.uint64)
res = {}
for off, sg in B.CELLS:
    B.CUR.update(off=off, sign=sg); H = B.heads_off(seeds, 28, "bash4.2"); bad = 0
    for i, s in enumerate(seeds):
        r = [x % 29 for x in my_raws(int(s), 28 + off)][off:]
        r = r if sg < 0 else [(29 - x) % 29 for x in r]
        bad += r != H[:, i].tolist()
    res["o%d_s%s" % (off, "p" if sg > 0 else "m")] = {"seeds": 300, "values": 300 * 28, "mismatch_seeds": int(bad)}
json.dump(res, open(os.path.join(HERE, "x1a_b2_wrapB2.json"), "w"), indent=1); print(json.dumps(res))
