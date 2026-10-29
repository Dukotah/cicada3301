"""Prefilter v2: panel trigram LLR (max over 9 registers) on the first m decoded runes (before any skip is applied)."""
import sys, json, random, numpy as np
from common import *
import pf
rng = random.Random(3301)
PREF = list(range(1325376000 >> 20, (1401580800 >> 20) + 1))
def rand_seeds(n):
    return np.array([(rng.choice(PREF) << 20) | rng.randrange(1 << 20) for _ in range(n)], dtype=np.uint64)
pan = AD.panel(); LMT = pan.LMT.astype(np.float32)
MS = (10, 14, 18, 24)
C = np.array(U[:max(MS)], dtype=np.int8)[:, None]
out = {"ms": MS, "null": {}, "power": {}}
cor = corpora()
for v in VARIANTS:
    sd_ = rand_seeds(1 << 19); K = pf.heads(sd_, max(MS), v)
    out["null"][v] = {}; norm = {}
    for m in MS:
        S = pf.tri_stat((C[:m] - K[:m]) % 29, LMT)
        mu, sdv = S.mean(0), S.std(0); norm[m] = (mu, sdv)
        mx = ((S - mu) / sdv).max(1)
        out["null"][v][m] = {"q": {q: float(np.quantile(mx, float(q))) for q in ("0.99", "0.999", "0.9999")}}
    for rel, enc in (("keyskip2", enc_pair), ("keyskip1", enc_exact)):
        for reg, txt in cor.items():
            seeds = rand_seeds(400); Cs = []
            for i, s in enumerate(seeds):
                st = rng.randrange(0, len(txt) - 130)
                Cs.append(enc(txt[st:st + 120], ks(int(s), v), seed=i + 1)[:max(MS)])
            Cs = np.array(Cs, dtype=np.int8).T; Kp = pf.heads(seeds, max(MS), v)
            for m in MS:
                S = pf.tri_stat((Cs[:m] - Kp[:m]) % 29, LMT, *norm[m]).max(1)
                out["power"].setdefault(v, {}).setdefault(rel, {}).setdefault(reg, {})[m] = {q: round(float((S > out["null"][v][m]["q"][q]).mean()), 3) for q in ("0.99", "0.999", "0.9999")}
            print(v, rel, reg, {m: out["power"][v][rel][reg][m]["0.999"] for m in MS}, flush=True)
json.dump(out, open("prefilter_power2.json", "w"), indent=1)
