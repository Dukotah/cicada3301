"""Fresh-eyes audit, part 1: recompute the foundation statistics from the raw transcription.

Nothing here imports the repo rig. Output: foundation.json. Every number the audit quotes about
doublets, lags, periodicity and position effects comes from this file.
"""
import collections
import json
import math
import os

import numpy as np

import lp2

HERE = os.path.dirname(os.path.abspath(__file__))
P = lp2.unsolved()
PI = lp2.idx(P)
U = [x for p in PI for x in p]
N = len(U)
out = {"n_runes": N, "n_pages": len(P)}


def z_eq(eq, tot):
    return (eq - tot / 29) / math.sqrt(tot * (1 / 29) * (28 / 29))


# ---- 1. doublets by boundary class, page, section
cat, catn, dbl = collections.Counter(), collections.Counter(), []
g = 0
for pi, p in enumerate(P):
    for k, r in enumerate(p):
        if k > 0:
            pre = r["pre"]
            c = ("sentence" if "." in pre else "word" if "-" in pre else "line-wrap inside a word" if "/" in pre
                 else "inside a word")
            catn[c] += 1
            if r["i"] == p[k - 1]["i"]:
                cat[c] += 1
                dbl.append(g)
        g += 1
pairs = sum(catn.values())
out["doublets"] = {"count": len(dbl), "within_page_pairs": pairs, "rate": len(dbl) / pairs,
                   "cross_page": sum(a[-1] == b[0] for a, b in zip(PI, PI[1:])),
                   "by_boundary": {c: {"pairs": catn[c], "doublets": cat[c], "keep_ratio": cat[c] / (catn[c] / 29)}
                                   for c in catn},
                   "triples": sum(1 for p in PI for k in range(2, len(p)) if p[k] == p[k - 1] == p[k - 2])}
per_page = [sum(a == b for a, b in zip(p, p[1:])) for p in PI]
exp = [(len(p) - 1) * len(dbl) / pairs for p in PI]
out["doublets"]["per_page_chi2"] = sum((o - e) ** 2 / e for o, e in zip(per_page, exp))
out["doublets"]["per_page_df"] = len(P) - 1
gaps = sorted(b - a for a, b in zip(dbl, dbl[1:]))
out["doublets"]["smallest_gaps"] = gaps[:6]

# sections split on the '$' / paragraph marks of the transcription
txt = open(lp2.KRIS, encoding="utf-8").read()
secs, cur = [], []
for ch in txt:
    if ch in lp2.R2I:
        cur.append(lp2.R2I[ch])
    elif ch in "$§":
        secs.append(cur); cur = []
secs = [s for s in secs if s][:8]
out["sections"] = [{"runes": len(s), "doublets": sum(a == b for a, b in zip(s, s[1:])),
                    "keep_ratio": sum(a == b for a, b in zip(s, s[1:])) / (len(s) / 29),
                    "ioc_x29": 29 * sum(v * (v - 1) for v in collections.Counter(s).values()) / (len(s) * (len(s) - 1))}
                   for s in secs]

# in-word position of the second rune of each doublet (0 = the pair straddles a word boundary)
wpos, base, g = collections.Counter(), collections.Counter(), 0
for p in P:
    w = 0
    for k, r in enumerate(p):
        if k > 0:
            w = 0 if lp2.word_start(r, k) else w + 1
            base[min(w, 8)] += 1
            if r["i"] == p[k - 1]["i"]:
                wpos[min(w, 8)] += 1
out["doublets"]["in_word_position"] = {str(k): {"pairs": base[k], "doublets": wpos[k]} for k in sorted(base)}

# ---- 2. monogram, delta, bigram
mc = collections.Counter(U)
out["monogram_chi2_28df"] = sum((mc[i] - N / 29) ** 2 / (N / 29) for i in range(29))
dc = collections.Counter((p[k] - p[k - 1]) % 29 for p in PI for k in range(1, len(p)))
e = (pairs - dc[0]) / 28
out["nonzero_delta_chi2_27df"] = sum((dc[d] - e) ** 2 / e for d in range(1, 29))
big = collections.Counter((p[k - 1], p[k]) for p in PI for k in range(1, len(p)))
row, col = collections.Counter(), collections.Counter()
for (a, b), n in big.items():
    if a != b:
        row[a] += n; col[b] += n
ra, cb = {a: 1.0 for a in range(29)}, {b: 1.0 for b in range(29)}
for _ in range(200):
    for a in range(29):
        ra[a] = row[a] / sum(cb[b] for b in range(29) if b != a)
    for b in range(29):
        cb[b] = col[b] / sum(ra[a] for a in range(29) if a != b)
chi = sum((big.get((a, b), 0) - ra[a] * cb[b]) ** 2 / (ra[a] * cb[b]) for a in range(29) for b in range(29) if a != b)
df = 29 * 29 - 29 - 57
out["bigram_offdiag"] = {"chi2": chi, "df": df, "z": (chi - df) / math.sqrt(2 * df)}

# ---- 3. every lag, rigid, on the flat stream; then a drift-smeared periodicity statistic
A = np.array(U)
zs = np.zeros(N)
for lag in range(1, N - 500):
    zs[lag] = z_eq(int((A[lag:] == A[:-lag]).sum()), N - lag)
m = np.arange(N); sel = (m >= 2) & (m < N - 500)
out["lag_scan_rigid"] = {"lags": int(sel.sum()), "mean_z": float(zs[sel].mean()), "sd_z": float(zs[sel].std()),
                         "max_z": float(zs[sel].max()), "argmax": int(m[sel][zs[sel].argmax()]),
                         "z_at_6395": float(zs[6395]), "z_at_1279": float(zs[1279])}


def smeared(Lp, lam):
    """Matched filter for a key of period Lp when each rejection consumes one key draw (rate lam per rune)."""
    mu = lam * Lp
    ms = np.arange(0, int(mu + 8 * math.sqrt(mu + 1)) + 2)
    w = np.exp(ms * math.log(mu) - mu - np.array([math.lgamma(x + 1) for x in ms]))
    ok = Lp - ms >= 2
    return float((w[ok] * zs[Lp - ms[ok]]).sum() / math.sqrt((w[ok] ** 2).sum()))


for lam in (0.0288, 0.0576):
    t = np.array([smeared(Lp, lam) for Lp in range(3, N - 600)])
    out[f"lag_scan_drift_smeared_lam{lam}"] = {"sd": float(t.std()), "max": float(t.max()), "argmax_period": int(t.argmax()) + 3}

# ---- 4. position tests on the doublet sites
def sieve(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return s


PR = sieve(N + 2)
out["doublet_sites_vs_prime_positions"] = {"touching_a_prime_1based": sum(1 for i in dbl if PR[i + 1] or PR[i]),
                                           "of": len(dbl), "base_rate": 0.238}
res = {}
for mod in range(2, 41):
    c = collections.Counter(i % mod for i in dbl)
    x = sum((c.get(r, 0) - len(dbl) / mod) ** 2 / (len(dbl) / mod) for r in range(mod))
    res[mod] = (x - (mod - 1)) / math.sqrt(2 * (mod - 1))
out["doublet_position_residue_max_z_mod2to40"] = max(res.values())

# ---- 5. two-dimensional avoidance, and the line-initial rune distribution
lines = []
for p in P:
    L, cur = [], []
    for k, r in enumerate(p):
        if k > 0 and "/" in r["pre"]:
            L.append(cur); cur = []
        cur.append(r["i"])
    L.append(cur); lines.append(L)
eq = tot = 0
for L in lines:
    for a, b in zip(L, L[1:]):
        for k in range(min(len(a), len(b))):
            tot += 1; eq += a[k] == b[k]
out["vertical_same_column"] = {"equal": eq, "pairs": tot, "z": z_eq(eq, tot)}
first = collections.Counter(l[0] for L in lines for l in L)
nl = sum(first.values())
out["line_initial"] = {"lines": nl, "chi2_28df": sum((first.get(i, 0) - nl / 29) ** 2 / (nl / 29) for i in range(29)),
                       "note": "glyph-width size bias, already measured and explained in round18/L4-forcing"}

json.dump(out, open(os.path.join(HERE, "foundation.json"), "w"), indent=1)
d = out["doublets"]
print(f"runes {N}  doublets {d['count']}/{d['within_page_pairs']} = {100 * d['rate']:.3f}%  cross-page {d['cross_page']}  triples {d['triples']}")
for c, v in d["by_boundary"].items():
    print(f"   {c:26s} pairs {v['pairs']:5d} doublets {v['doublets']:2d} keep {v['keep_ratio']:.3f}")
print("per-page chi2 %.1f / %d   monogram chi2 %.1f / 28   nonzero-delta chi2 %.1f / 27   bigram z %+.2f"
      % (d["per_page_chi2"], d["per_page_df"], out["monogram_chi2_28df"], out["nonzero_delta_chi2_27df"], out["bigram_offdiag"]["z"]))
print("sections keep ratio:", [round(s["keep_ratio"], 2) for s in out["sections"]])
print("rigid lag scan:", out["lag_scan_rigid"])
print("drift-smeared:", out["lag_scan_drift_smeared_lam0.0288"], out["lag_scan_drift_smeared_lam0.0576"])
print("vertical:", out["vertical_same_column"], " line-initial chi2 %.1f" % out["line_initial"]["chi2_28df"])
