import sys, os, json, random, time
import numpy as np
sys.dont_write_bytecode = True
MYDIR = os.path.dirname(os.path.abspath(__file__)); HERE = MYDIR
B1 = os.path.join(HERE, "..", "..", "round32", "B1-bash-random"); B2 = os.path.join(HERE, "..", "..", "round32", "B2-php-mtrand")
sys.path.insert(0, B1)
from common import *
HERE = MYDIR
import pf as PF1
import importlib.util as iu
s = iu.spec_from_file_location("php_mt", os.path.join(B2, "php_mt.py")); PM = iu.module_from_spec(s); sys.modules["php_mt"] = PM; s.loader.exec_module(PM)
sys.path.insert(0, HERE); import pf_v3
LMT = AD.panel().LMT.astype(np.float32)
MS = (16, 20, 24); MM = 24
C = np.array(U[:MM], dtype=np.int8)[:, None]
NG = 1 << 18
rng = random.Random(3301); nrng = np.random.default_rng(3301)
SEC = [(1325376000 >> 20), (1401580800 >> 20)]
def bseeds(n): return np.array([(rng.randrange(SEC[0], SEC[1] + 1) << 20) | rng.randrange(1 << 20) for _ in range(n)], dtype=np.uint64)
def gen_heads(name, n):
    if name.startswith("bash"):
        return PF1.heads(bseeds(n), MM, name)
    tw, rd = name.split("_")[1:]
    sd = nrng.integers(0, 1 << 32, size=n, dtype=np.uint64)
    return PM.reduce_heads(PM.heads_all(sd, MM)[tw], rd)
GENS = ["bash4.2", "bash4.2_i32", "php_mt_scale", "php_mt_mod", "php_php_scale", "php_php_mod"]
LNK = np.log(29.0)
def accs(Pfull):
    P = Pfull.astype(np.int32); out = {}; acc = np.zeros((P.shape[1], 9), np.float32)
    for t in range(MM - 2):
        acc += LMT[P[t] * 841 + P[t + 1] * 29 + P[t + 2]]
        if t + 3 in MS: out[t + 3] = acc.copy()
    return out
def accs_chunks(K=None, Pfull=None):
    res = {m: [] for m in MS}
    n = (K if K is not None else Pfull).shape[1]
    for i in range(0, n, 65536):
        P = ((C - K[:, i:i + 65536]) % 29) if K is not None else Pfull[:, i:i + 65536]
        a = accs(P)
        for m in MS: res[m].append(a[m])
    return {m: np.concatenate(res[m]) for m in MS}
t0 = time.time()
null = {}
for g in GENS:
    null[g] = accs_chunks(K=gen_heads(g, NG)); print("null", g, round(time.time() - t0), flush=True)
REG = list(AD.panel().registers)
TH = np.load(os.path.join(LP, "analysis/round32/I2-multiregister-readjudication/models/testhalves.npz"))
cor = {k: TH[k].astype(np.int64) for k in REG}
NPL = 400
plant_ns = {}
for reg, txt in cor.items():
    st = [rng.randrange(0, len(txt) - 200) for _ in range(NPL)]
    Pf = np.array([txt[s:s + MM] for s in st], dtype=np.int8).T
    plant_ns[reg] = accs_chunks(Pfull=Pf)
plant_sk = {}
for reg, txt in cor.items():
    cols = []
    for rel, enc in (("keyskip2", enc_pair), ("keyskip1", enc_exact)):
        for i in range(100):
            s0 = rng.randrange(0, len(txt) - 200); sd = int(bseeds(1)[0]); K = ks(sd, "bash4.2", 80)
            Cc = enc(list(map(int, txt[s0:s0 + 60])), K, seed=i + 1)
            cols.append((np.array(Cc[:MM], dtype=np.int8) - np.array(K[:MM], dtype=np.int8)) % 29)
    plant_sk[reg] = accs_chunks(Pfull=np.array(cols, dtype=np.int8).T)
print("plants", round(time.time() - t0), flush=True)

PS = np.array([0.5, 0.9, 0.99, 0.999, 0.9999, 0.99995])
YS = -np.log10(1 - PS)
def stats(a, m, mu, sdv, qx):
    z = (a - mu) / sdv
    llr = a.astype(np.float64) * pf_v3.LN10 + (m - 2) * LNK
    mx = llr.max(1); lse = mx + np.log(np.exp(llr - mx[:, None]).sum(1))
    pq = np.max(np.stack([np.interp(z[:, r], qx[r], YS) for r in range(9)], 1), 1) + 1e-3 * z.max(1)
    return {"zmax": z.max(1), "llrmax": mx, "lse": lse, "pq": pq}
roc = {}; norm = {}
FPRS = [3e-4, 1e-3, 3e-3, 1e-2]
for m in MS:
    cal = np.concatenate([null[g][m][: NG // 2] for g in GENS])
    mu, sdv = cal.mean(0), cal.std(0); z = (cal - mu) / sdv
    qx = [np.maximum.accumulate(np.quantile(z[:, r], PS) + 1e-6 * np.arange(len(PS))) for r in range(9)]
    sc = stats(cal, m, mu, sdv, qx)
    ev = {g: stats(null[g][m][NG // 2:], m, mu, sdv, qx) for g in GENS}
    pl_n = {r: stats(plant_ns[r][m], m, mu, sdv, qx) for r in REG}
    pl_s = {r: stats(plant_sk[r][m], m, mu, sdv, qx) for r in REG}
    roc[m] = {}
    for st in ("zmax", "llrmax", "lse", "pq", "OR"):
        roc[m][st] = {}
        for f in FPRS:
            if st == "OR":
                t1 = np.quantile(sc["zmax"], 1 - f / 2); t2 = np.quantile(sc["lse"], 1 - f / 2)
                fn = lambda d, t1=t1, t2=t2: (d["zmax"] > t1) | (d["lse"] > t2)
                thr = [float(t1), float(t2)]
            else:
                t = float(np.quantile(sc[st], 1 - f)); fn = (lambda d, t=t, st=st: d[st] > t); thr = t
            roc[m][st][str(f)] = {"thr": thr, "fpr_heldout": float(np.mean(np.concatenate([fn(ev[g]) for g in GENS]))),
                                  "fpr_by_gen": {g: float(fn(ev[g]).mean()) for g in GENS},
                                  "power_noskip": {r: round(float(fn(pl_n[r]).mean()), 3) for r in REG},
                                  "power_withskip": {r: round(float(fn(pl_s[r]).mean()), 3) for r in REG}}
    norm[m] = {"mu": mu.tolist(), "sd": sdv.tolist()}
    print("m", m, {st: (roc[m][st]["0.001"]["power_noskip"]["EN_NOVOWEL"], min(v for k, v in roc[m][st]["0.001"]["power_noskip"].items() if k != "EN_NOVOWEL")) for st in roc[m]}, flush=True)
json.dump({"n_null_per_gen": NG, "n_plants_noskip": NPL, "n_plants_withskip": 200, "roc": roc}, open(os.path.join(MYDIR, "roc.json"), "w"), indent=1)
json.dump(norm, open(os.path.join(MYDIR, "_norm.json"), "w"))
print("done", round(time.time() - t0))
