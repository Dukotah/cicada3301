import sys, os, json, random, time
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "..", "..")
B1 = os.path.join(R, "round32", "B1-bash-random")
sys.path.insert(0, B1)
from common import *
HERE = os.path.dirname(os.path.abspath(__file__))  # common.py rebinds HERE
sys.path.insert(0, os.path.join(R, "round35", "I1-skip-tolerant-screen"))
import pf_v4
pf_v3 = pf_v4.pf_v3
LMT = AD.panel().LMT.astype(np.float32); REG = list(AD.panel().registers)
F = pf_v4.FROZEN
out = {"frozen": F}
rng = random.Random(777)   # independent of lane's 3301
SEC = [(1325376000 >> 20), (1401580800 >> 20)]
def bseeds(n): return np.array([(rng.randrange(SEC[0], SEC[1] + 1) << 20) | rng.randrange(1 << 20) for _ in range(n)], dtype=np.uint64)
# (B) k=0 == pf_v3 on 1000 heads
Cr = np.array(U[:24], dtype=np.int8)
sd = bseeds(1000); K = pf_v4.heads(sd, 24, "bash4.2")
P = (Cr[:20, None] - K[:20]) % 29
a = pf_v3.lse_stat(P, LMT)
R0 = pf_v4.dp_regs(Cr, K, LMT, 0, 1, 0.0, ms=(20,))
b = pf_v4.lse_from_regs(R0[20], 20)
out["k0_vs_pfv3_1000"] = {"max_abs_diff": float(np.abs(a - b).max()), "n": 1000}
# (C) fresh held-out FPR, bash LP64, 2^16 fresh seeds
sd = bseeds(1 << 16)
m = pf_v4.prefilter_mask(sd, "bash4.2", Cr, LMT, m=24, rel="both")
out["fresh_fpr_bash_LP64_2p16"] = {"n": 1 << 16, "pass": int(m.sum()), "fpr": float(m.mean())}
sd2 = bseeds(1 << 16)
m2 = pf_v4.prefilter_mask(sd2, "bash4.2_i32", Cr, LMT, m=24, rel="both")
out["fresh_fpr_bash_ILP32_2p16"] = {"n": 1 << 16, "pass": int(m2.sum()), "fpr": float(m2.mean())}
# (A) 300 plants, EN_NOVOWEL & EN_HALFVOWEL natural, keyskip2 (own encipherer: common.enc_pair)
TH = np.load(os.path.join(LP, "analysis/round32/I2-multiregister-readjudication/models/testhalves.npz"))
def plant_pass(reg, N, a_rel):
    txt = TH[reg].astype(np.int64); sds = bseeds(N); Kf = pf_v4.heads(sds, 70, "bash4.2")
    hits_both = []; wskip = []; hit_k0 = []
    for i in range(N):
        st = rng.randrange(0, len(txt) - 40); Pp = [int(x) for x in txt[st:st + 30]]
        Kk = Kf[:, i].tolist()
        if a_rel == 2: Cc = enc_pair(Pp, Kk, seed=991 + i)
        else: Cc = sk.encipher_keyskip(Pp, Kk, sign=-1, supp=0.83, seed=991 + i)[0]
        # independent skip detection: decode with plain key offset 0 and see if head recovers
        naive = [(Cc[t] + Kk[t]) % 29 for t in range(24)]  # sign -1 decode p=c-k? use (c - k)
        naive = [(Cc[t] - Kk[t]) % 29 for t in range(24)]
        wskip.append(naive[:24] != Pp[:24])
        Cn = np.array(Cc[:24], dtype=np.int8)
        hit = False
        for a in (1, 2):
            s = pf_v4.lse_v4(Cn, Kf[:24 + 2 * 2, i:i + 1].astype(np.int8), LMT, F["k"], a, F["pen_a%d" % a], ms=(24,))[24][0]
            hit |= bool(s > F["thr"]["a%d" % a])
        hits_both.append(hit)
        s0 = pf_v3.lse_stat(((Cn[:20, None] - Kf[:20, i:i + 1]) % 29).astype(np.int8), LMT)[0]
        hit_k0.append(bool(s0 > pf_v3.FROZEN[20]))
    h = np.array(hits_both); w = np.array(wskip); h0 = np.array(hit_k0)
    return {"n": N, "power_pf_v4_frozen": float(h.mean()), "power_pf_v3": float(h0.mean()), "frac_head_differs_from_naive": float(w.mean()),
            "power_v4_withskip": float(h[w].mean()) if w.any() else None, "power_v4_skipfree": float(h[~w].mean()) if (~w).any() else None,
            "power_v3_withskip": float(h0[w].mean()) if w.any() else None, "n_withskip": int(w.sum())}
t0 = time.time()
out["plants_keyskip2"] = {}
for reg in ("EN_NOVOWEL", "EN_HALFVOWEL"):
    out["plants_keyskip2"][reg] = plant_pass(reg, 300, 2); print(reg, out["plants_keyskip2"][reg], round(time.time() - t0), flush=True)
json.dump(out, open(os.path.join(HERE, "rerun_i1.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "frozen"}, indent=1))
