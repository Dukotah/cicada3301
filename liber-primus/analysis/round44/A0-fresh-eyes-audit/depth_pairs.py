"""Fresh-eyes audit, part 5: position-aligned page pairs (the classical depth test, length-normalised).

For every pair of unsolved pages at offset 0, D_i = (a_i - b_i) mod 29. If two pages share key values
position by position, D is the difference of two plaintext symbols and is not uniform. The chi-square
splits into a symmetric (cosine) and an antisymmetric (sine) half; a difference of two draws from one
distribution lives entirely in the symmetric half. Output: depth_pairs.json.
"""
import itertools
import json
import math
import os

import numpy as np

import lp2

HERE = os.path.dirname(os.path.abspath(__file__))
PI = [np.array(p) for p in lp2.idx(lp2.unsolved())]


def stats(a, b, off=0):
    n = min(len(a), len(b) - off)
    D = (a[:n] - b[off:off + n]) % 29
    cnt = np.bincount(D, minlength=29)
    chi = float(((cnt - n / 29) ** 2 / (n / 29)).sum())
    w = np.arange(1, 15)[:, None]
    z = np.exp(2j * np.pi * w * D[None, :] / 29).mean(axis=1)
    sd = math.sqrt(0.5 / n)
    return {"n": int(n), "chi2_28df": chi, "sym_chi2_14df": float((z.real ** 2).sum() / sd ** 2),
            "antisym_chi2_14df": float((z.imag ** 2).sum() / sd ** 2), "kappa": float(cnt[0] / n),
            "counts": [int(x) for x in cnt], "re": [float(x) for x in z.real]}


rows = []
for i, j in itertools.combinations(range(55), 2):
    if min(len(PI[i]), len(PI[j])) >= 100:
        s = stats(PI[i], PI[j]); rows.append({"pair": [i, j], **{k: s[k] for k in ("n", "chi2_28df", "sym_chi2_14df", "antisym_chi2_14df", "kappa")}})
top = sorted(rows, key=lambda r: -r["chi2_28df"])
out = {"pairs_tested": len(rows), "mean_chi2": float(np.mean([r["chi2_28df"] for r in rows])),
       "mean_sym": float(np.mean([r["sym_chi2_14df"] for r in rows])), "mean_antisym": float(np.mean([r["antisym_chi2_14df"] for r in rows])),
       "top_by_chi2": top[:6], "top_by_sym": sorted(rows, key=lambda r: -r["sym_chi2_14df"])[:6]}
s = stats(PI[28], PI[42])
out["pair_28_42"] = s
out["pair_28_42"]["offsets"] = {str(o): (stats(PI[28], PI[42], o) if o >= 0 else stats(PI[42], PI[28], -o))["sym_chi2_14df"] for o in range(-4, 5)}
D = (PI[28][:269] - PI[42][:269]) % 29
S = {0, 2, 3, 5, 6, 27, 26, 24, 23}
out["pair_28_42"]["share_of_d_in_0_2_3_5_6_per_45_runes"] = [float(np.mean([d in S for d in D[k:k + 45]])) for k in range(0, 269, 45)]
rng = np.random.default_rng(7); b = PI[42].copy(); ge = 0; T = 20000
for _ in range(T):
    rng.shuffle(b)
    ge += stats(PI[28], b)["chi2_28df"] >= s["chi2_28df"]
out["pair_28_42"]["permutation_p_chi2"] = ge / T
out["family_wise"] = {"chi2_tail_p": 4.8e-6, "x_pairs": 4.8e-6 * len(rows),
                      "note": "a-priori statistic over the offset-0 pairs; the reader who found it scanned 331,908 pair x offset cells, "
                              "where 1.6 cells this extreme are expected on the unfolded statistic"}
json.dump(out, open(os.path.join(HERE, "depth_pairs.json"), "w"), indent=1)
print("pairs", len(rows), "mean chi2 %.1f (28)  mean sym %.1f / antisym %.1f (14 each)" % (out["mean_chi2"], out["mean_sym"], out["mean_antisym"]))
print("top by chi2:", [(r["pair"], round(r["chi2_28df"], 1)) for r in top[:5]])
print("top by symmetric part:", [(r["pair"], round(r["sym_chi2_14df"], 1)) for r in out["top_by_sym"][:5]])
print("(28,42): chi2 %.1f  sym %.1f  antisym %.1f  kappa %.4f  perm p %.5f" % (s["chi2_28df"], s["sym_chi2_14df"], s["antisym_chi2_14df"], s["kappa"], out["pair_28_42"]["permutation_p_chi2"]))
print("   by offset -4..4:", {k: round(v, 1) for k, v in out["pair_28_42"]["offsets"].items()})
