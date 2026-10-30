import sys, os, json, random, time, math
import numpy as np
sys.dont_write_bytecode = True
LANE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(LANE, "..", "..")
B1 = os.path.join(R, "round32", "B1-bash-random"); B2 = os.path.join(R, "round32", "B2-php-mtrand")
sys.path.insert(0, B1)
from common import *          # rebinds HERE; never write via HERE
import importlib.util as iu
s = iu.spec_from_file_location("php_mt", os.path.join(B2, "php_mt.py")); PM = iu.module_from_spec(s); sys.modules["php_mt"] = PM; s.loader.exec_module(PM)
sys.path.insert(0, os.path.join(R, "round35", "I1-skip-tolerant-screen")); import pf_v4
F = pf_v4.FROZEN; assert F["m"] == 24 and F["k"] == 2
LMT = AD.panel().LMT.astype(np.float32)
REGS = ["EN_MODERN", "EN_NOVOWEL", "EN_HALFVOWEL", "LATIN"]
TH = np.load(os.path.join(LP, "analysis/round32/I2-multiregister-readjudication/models/testhalves.npz"))
rng = random.Random(3601); nrng = np.random.default_rng(3601)
SEC = [(1325376000 >> 20), (1401580800 >> 20)]
def bseeds(n): return np.array([(rng.randrange(SEC[0], SEC[1] + 1) << 20) | rng.randrange(1 << 20) for _ in range(n)], dtype=np.uint64)
GENS = ["bash4.2", "bash4.2_i32", "php_mt_scale", "php_mt_mod", "php_php_scale", "php_php_mod"]
def heads(g, n, L):
    if g.startswith("bash"): return pf_v4.heads(bseeds(n), L, g)
    tw, rd = g.split("_")[1:]
    sd = nrng.integers(0, 1 << 32, size=n, dtype=np.uint64)
    return PM.reduce_heads(PM.heads_all(sd, L)[tw], rd)
def enc2(P, K, seed):
    r = random.Random(seed); Cc, used, j, cp = [], [], 0, None
    for p in P:
        while True:
            c = (p + K[j]) % 29
            if cp is not None and c == cp and r.random() < 0.83: j += 2; continue
            break
        Cc.append(c); used.append(j); j += 1; cp = c
    return Cc, used
def enc1(P, K, seed):
    Cc, _, used = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=seed)
    return list(Cc), used
def dp_cols(Cc, K, k, a, pen, m=24):
    pl = pen / pf_v4.LN10
    st = [(b, c) for b in range(k + 1) for c in range(b, k + 1)]
    D = [[((Cc[t].astype(np.int32) - K[t + a * s].astype(np.int32)) % 29) for s in range(k + 1)] for t in range(m)]
    V = {(b, c): LMT[D[0][0] * 841 + D[1][b] * 29 + D[2][c]] - np.float32(pl * c) for (b, c) in st}
    for t in range(1, m - 2):
        Vn = {}
        for (b, c) in st:
            best = None
            for a_ in range(b + 1):
                x = V[(a_, b)] + LMT[D[t][a_] * 841 + D[t + 1][b] * 29 + D[t + 2][c]]
                best = x if best is None else np.maximum(best, x)
            Vn[(b, c)] = best - np.float32(pl * (c - b))
        V = Vn
    f = None
    for v in V.values(): f = v if f is None else np.maximum(f, v)
    return pf_v4.lse_from_regs(f.astype(np.float64), m)
def hit_or(Cc, K):
    h = np.zeros(Cc.shape[1], bool)
    for a in (1, 2):
        h |= dp_cols(Cc, K, F["k"], a, F["pen_a%d" % a]) > F["thr"]["a%d" % a]
    return h
def wilson(x, n, z=1.96):
    if n == 0: return [None, None]
    p = x / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]
def stat(h):
    n = int(len(h)); x = int(h.sum()); return dict(n=n, hits=x, power=(x / n if n else None), wilson95=wilson(x, n))
N = 500; t0 = time.time(); power = {}
for g in GENS:
    power[g] = {}
    for rel, enc in (("keyskip1", enc1), ("keyskip2", enc2)):
        power[g][rel] = {}
        for ri, reg in enumerate(REGS):
            txt = TH[reg].astype(np.int64)
            Kf = heads(g, N, 70); Cs, fs = [], []
            for i in range(N):
                st = rng.randrange(0, len(txt) - 40); P = [int(x) for x in txt[st:st + 30]]
                Cc, used = enc(P, Kf[:, i].tolist(), 100003 * ri + 17 * i + (1 if rel == "keyskip1" else 2) + GENS.index(g) * 7919)
                Cs.append(Cc[:24]); fs.append(next((t for t in range(24) if used[t] != t), 99))
            h = hit_or(np.array(Cs, dtype=np.int8).T, Kf[:28]); f = np.array(fs)
            power[g][rel][reg] = dict(natural=stat(h), skip_free=stat(h[f >= 24]), with_skip=stat(h[f < 24]), frac_with_skip=float((f < 24).mean()))
        print(g, rel, round(time.time() - t0), {r: round(v["natural"]["power"], 3) for r, v in power[g][rel].items()}, flush=True)
json.dump(dict(frozen=F, plants_per_cell=N, power=power), open(os.path.join(LANE, "power_by_generator.json"), "w"), indent=1)
Cr = np.array(U[:24], dtype=np.int8)[:, None]
fpr = {}
NF = 1 << 16
for g in GENS:
    Kh = heads(g, NF, 28); hit = np.zeros(NF, bool)
    for i0 in range(0, NF, 16384):
        Kc = Kh[:, i0:i0 + 16384]
        for a in (1, 2):
            Cb = np.repeat(Cr, Kc.shape[1], 1)
            hit[i0:i0 + 16384] |= dp_cols(Cb, Kc, F["k"], a, F["pen_a%d" % a]) > F["thr"]["a%d" % a]
    fpr[g] = dict(n=NF, pass_=int(hit.sum()), fpr=float(hit.mean()), wilson95=wilson(int(hit.sum()), NF))
    print("FPR", g, fpr[g], flush=True)
json.dump(fpr, open(os.path.join(LANE, "fpr_by_generator.json"), "w"), indent=1)
print("elapsed", round(time.time() - t0))
