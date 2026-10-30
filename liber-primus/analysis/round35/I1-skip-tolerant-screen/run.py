import sys, os, json, random, time
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
B1 = os.path.join(HERE, "..", "..", "round32", "B1-bash-random"); B2 = os.path.join(HERE, "..", "..", "round32", "B2-php-mtrand")
sys.path.insert(0, B1)
from common import *
HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util as iu
s = iu.spec_from_file_location("php_mt", os.path.join(B2, "php_mt.py")); PM = iu.module_from_spec(s); sys.modules["php_mt"] = PM; s.loader.exec_module(PM)
sys.path.insert(0, HERE); import pf_v4
LMT = AD.panel().LMT.astype(np.float32)
REG = list(AD.panel().registers)
KL = 28; MS = (20, 24)
C = np.array(U[:24], dtype=np.int8)
rng = random.Random(3301); nrng = np.random.default_rng(3301)
SEC = [(1325376000 >> 20), (1401580800 >> 20)]
def bseeds(n): return np.array([(rng.randrange(SEC[0], SEC[1] + 1) << 20) | rng.randrange(1 << 20) for _ in range(n)], dtype=np.uint64)
NG = 1 << 17
GENS = ["bash4.2", "bash4.2_i32", "php_mt_scale", "php_mt_mod", "php_php_scale", "php_php_mod"]
def gen_heads(name, n):
    if name.startswith("bash"): return pf_v4.heads(bseeds(n), KL, name)
    tw, rd = name.split("_")[1:]
    sd = nrng.integers(0, 1 << 32, size=n, dtype=np.uint64)
    return PM.reduce_heads(PM.heads_all(sd, KL)[tw], rd)
t0 = time.time()
NK = {g: gen_heads(g, NG) for g in GENS}
print("null heads", round(time.time() - t0), flush=True)
NKall = np.concatenate([NK[g] for g in GENS], 1)
gid = np.repeat(np.arange(6), NG); half = np.tile((np.arange(NG) >= NG // 2), 6)   # half B = True

TH = np.load(os.path.join(LP, "analysis/round32/I2-multiregister-readjudication/models/testhalves.npz"))
cor = {k: TH[k].astype(np.int64) for k in REG}
NPL = 2000
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
PL = {}
for a, enc in ((1, enc1), (2, enc2)):
    Cs, Ks, ri, ii, fs, dbs = [], [], [], [], [], []
    for r, reg in enumerate(REG):
        txt = cor[reg]; N = NPL
        sd = bseeds(N); Kf = pf_v4.heads(sd, 70, "bash4.2")
        for i in range(N):
            st = rng.randrange(0, len(txt) - 40); P = [int(x) for x in txt[st:st + 30]]
            Cc, used = enc(P, Kf[:, i].tolist(), 7919 * a + 131 * r + i + 1)
            Cs.append(Cc[:24]); Ks.append(Kf[:KL, i]); ri.append(r); ii.append(i)
            fs.append(next((t for t in range(24) if used[t] != t), 99))
            dbs.append(next((t for t in range(1, 24) if Cc[t] == Cc[t - 1]), 99))
    PL[a] = dict(C=np.array(Cs, dtype=np.int8), K=np.array(Ks, dtype=np.int8).T, r=np.array(ri), i=np.array(ii), f=np.array(fs), dbl=np.array(dbs))
print("plants", round(time.time() - t0), flush=True)

def dp_regs_cols(Cc, K, k, a, pen):
    pl = pen / pf_v4.LN10; mmax = max(MS)
    st = [(b, c) for b in range(k + 1) for c in range(b, k + 1)]
    D = [[((Cc[t].astype(np.int32) - K[t + a * s].astype(np.int32)) % 29) for s in range(k + 1)] for t in range(mmax)]
    V = {(b, c): LMT[D[0][0] * 841 + D[1][b] * 29 + D[2][c]] - np.float32(pl * c) for (b, c) in st}
    out = {}
    for t in range(1, mmax - 2):
        Vn = {}
        for (b, c) in st:
            best = None
            for a_ in range(b + 1):
                x = V[(a_, b)] + LMT[D[t][a_] * 841 + D[t + 1][b] * 29 + D[t + 2][c]]
                best = x if best is None else np.maximum(best, x)
            Vn[(b, c)] = best - np.float32(pl * (c - b))
        V = Vn
        if t + 3 in MS:
            f = None
            for v in V.values(): f = v if f is None else np.maximum(f, v)
            out[t + 3] = f.astype(np.float64)
    return out
def plant_scores(a_plant, k, a, pen):
    R = dp_regs_cols(PL[a_plant]['C'].T, PL[a_plant]['K'], k, a, pen)
    return {m: pf_v4.lse_from_regs(R[m], m) for m in MS}

FPRS = [3e-4, 1e-3, 3e-3, 1e-2]
BAR = np.array([0.90] * 9); BAR[REG.index("EN_NOVOWEL")] = 0.85
PENS = [0, 1, 2, 3]
cal = ~half
res = {}
for a in (1, 2):
    for k in (1, 2):
        for pen in PENS:
            nr = pf_v4.dp_regs(C, NKall, LMT, k, a, pen, MS)
            ns = {m: pf_v4.lse_from_regs(nr[m], m) for m in MS}
            res[(a, k, pen)] = dict(ns=ns, ps=plant_scores(a, k, a, pen))
        print("done a,k", a, k, round(time.time() - t0), flush=True)
base = {}
for a in (1, 2):
    nr = pf_v4.dp_regs(C, NKall, LMT, 0, a, 0.0, MS); ns = {m: pf_v4.lse_from_regs(nr[m], m) for m in MS}
    base[a] = dict(ns=ns, ps=plant_scores(a, 0, a, 0.0))

def thr_at(ns, fpr, mask): return float(np.quantile(ns[mask], 1 - fpr))
def ratio(pw): return float(np.min(pw / BAR))
calpl = {a: PL[a]['i'] < NPL // 2 for a in (1, 2)}
hopl = {a: ~calpl[a] for a in (1, 2)}
chosen = {}
for a in (1, 2):
    for k in (1, 2):
        for m in MS:
            best = None
            for pen in PENS:
                R = res[(a, k, pen)]
                thr = thr_at(R['ns'][m], 1e-3, cal)
                hit = R['ps'][m] > thr
                pw = np.array([hit[(PL[a]['r'] == r) & calpl[a]].mean() for r in range(9)])
                rt = ratio(pw)
                if best is None or rt > best[0] + 1e-9: best = (rt, pen)
            chosen[(a, k, m)] = best[1]

def evaluate(a, k, m, pen, fpr):
    R = res[(a, k, pen)] if k > 0 else base[a]
    thr = thr_at(R['ns'][m], fpr, cal)
    nsb = R['ns'][m] > thr
    P = PL[a]; hit = R['ps'][m] > thr
    f = P['f']; dbl = P['dbl']
    out = dict(thr=thr, fpr_heldout=float(nsb[half].mean()), fpr_heldout_per_gen={GENS[g]: float(nsb[half & (gid == g)].mean()) for g in range(6)}, fpr_calib=float(nsb[cal].mean()))
    for nm, sel in (('natural', hopl[a]), ('skip_free', hopl[a] & (f >= m)), ('with_skip', hopl[a] & (f < m)), ('natural_no_cipher_doublet', hopl[a] & (dbl >= m))):
        out[nm] = {REG[r]: (float(hit[(P['r'] == r) & sel].mean()) if ((P['r'] == r) & sel).any() else None) for r in range(9)}
        out[nm + '_n'] = {REG[r]: int(((P['r'] == r) & sel).sum()) for r in range(9)}
    out['frac_with_skip'] = float((f[hopl[a]] < m).mean())
    pw = np.array([out['natural'][REG[r]] for r in range(9)])
    out['ratio_min'] = ratio(pw); out['bar_met'] = bool((pw >= BAR).all())
    return out
roc = {}
for a in (1, 2):
    for k in (0, 1, 2):
        for m in MS:
            pen = chosen.get((a, k, m), 0)
            roc["a%d|k%d|m%d" % (a, k, m)] = dict(pen=pen, curves={str(f): evaluate(a, k, m, pen, f) for f in FPRS})
json.dump(roc, open(os.path.join(HERE, "roc_matched.json"), "w"), indent=1)

both = {}
for k in (1, 2):
    for m in MS:
        for f in FPRS:
            e = {}; nulls_ = []; thrs = {}
            for a in (1, 2):
                pen = chosen[(a, k, m)]; thrs[a] = thr_at(res[(a, k, pen)]['ns'][m], f / 2, cal)
                nulls_.append(res[(a, k, pen)]['ns'][m] > thrs[a])
            nb = nulls_[0] | nulls_[1]
            for a_plant in (1, 2):
                hits = []
                for a in (1, 2):
                    pen = chosen[(a, k, m)]
                    ps = res[(a, k, pen)]['ps'][m] if a == a_plant else plant_scores(a_plant, k, a, pen)[m]
                    hits.append(ps > thrs[a])
                hit = hits[0] | hits[1]; P = PL[a_plant]; fq = P['f']
                e['plants_keyskip%d' % a_plant] = {nm: {REG[r]: float(hit[(P['r'] == r) & sel].mean()) for r in range(9)}
                    for nm, sel in (('natural', hopl[a_plant]), ('skip_free', hopl[a_plant] & (fq >= m)), ('with_skip', hopl[a_plant] & (fq < m)))}
            e['thr'] = {"a1": thrs[1], "a2": thrs[2]}
            e['fpr_heldout'] = float(nb[half].mean()); e['fpr_heldout_per_gen'] = {GENS[g]: float(nb[half & (gid == g)].mean()) for g in range(6)}
            pw = np.array([min(e['plants_keyskip1']['natural'][REG[r]], e['plants_keyskip2']['natural'][REG[r]]) for r in range(9)])
            e['ratio_min'] = ratio(pw); e['bar_met'] = bool((pw >= BAR).all()); e['min_power_over_relations'] = {REG[r]: float(pw[r]) for r in range(9)}
            both["k%d|m%d|%s" % (k, m, f)] = e
json.dump(both, open(os.path.join(HERE, "roc_both.json"), "w"), indent=1)
json.dump({"chosen_pen": {"a%d|k%d|m%d" % kk: v for kk, v in chosen.items()}}, open(os.path.join(HERE, "chosen_pen.json"), "w"), indent=1)
print("ROC matched-relation (ratio_min = min power/bar; fpr held-out)")
for key, v in roc.items():
    print(key, "pen", v['pen'], {f: (round(c['ratio_min'], 3), round(c['fpr_heldout'], 5)) for f, c in v['curves'].items()})
print("BOTH (OR of a1,a2 at FPR/2 each)")
for key, v in both.items(): print(key, round(v['ratio_min'], 3), v['bar_met'], round(v['fpr_heldout'], 5))
print("elapsed", round(time.time() - t0))
