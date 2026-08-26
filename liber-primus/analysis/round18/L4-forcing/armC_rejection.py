"""Round 18 / L4-FORCING — Arm C: the filter's residual signature CONDITIONED ON
position-within-line. Pre-registered; the sharpest sub-test in the lane.

Why this is the sharp one. Round 17 (item D-01) established the anti-repeat filter is
machine-applied, memoryless, unscoped and single-lag, at suppression s ~ 0.8075. A
rejection sampler that also enforced a SECOND predicate at line-start positions has to
resolve a conflict whenever the wanted rune equals the previous rune. There are only two
resolutions and both are visible without any key:

  * the author let the doublet through  -> EXCESS doublets at the line boundary,
  * the author let the filter win / re-rolled upstream -> DEFICIT.

Only "indistinguishable from the within-line rate" is consistent with no second constraint.
Round 17 measured a related but much weaker thing: that 4 of the 86 doublets cross a line
boundary (a SCOPE test at n=86). It never measured the residual RATE as a function of
position-within-line, nor the full 29-bin difference channel at the boundary, which uses
all 593 boundary transitions rather than only the 4 doublets.

Every null here permutes line-initial runes AMONG THEMSELVES, which preserves the
size-biased line-initial marginal that confound_layout.py established. Using a flat null
would manufacture a false positive out of typography.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "src")))
from parse_structure import Geometry  # noqa: E402

N = 29
ALPHA_TEST = 0.001 / 21
NPERM = 200_000


def _detectable_band(n_trans, coll_p, s_base, power=0.80, alpha=ALPHA_TEST):
    """Which boundary suppression values s could this many transitions have caught?

    Returns {"alpha":..., "power":..., "detectable_if_s_below": x, "detectable_if_s_above": y}
    -- the honest statement of what Arm C rules out. y is None when even s = 1
    (a total ban on boundary doublets) is invisible at this n, which is the usual
    situation for a 0.66 % residual rate on 539 transitions.
    """
    from math import sqrt
    try:
        from scipy.stats import norm
        za, zb = float(norm.isf(alpha / 2)), float(norm.isf(1 - power))
    except Exception:
        za, zb = 4.06, 0.842
    p0 = coll_p * (1 - s_base)

    def sig(s):
        p1 = min(max(coll_p * (1 - s), 1e-9), 0.999)
        se = sqrt(p0 * (1 - p0) / n_trans + p1 * (1 - p1) / n_trans)
        return abs(p1 - p0) >= (za + zb) * se

    lo = None
    for s in np.arange(s_base, -3.0, -0.005):      # excess side (s decreasing)
        if sig(float(s)):
            lo = float(s); break
    hi = None
    for s in np.arange(s_base, 1.0001, 0.005):     # deficit side (s increasing)
        if sig(float(s)):
            hi = float(s); break
    return {"alpha": alpha, "power": power,
            "detectable_if_s_at_or_below": lo,
            "detectable_if_s_at_or_above": hi,
            "interpretation": ("Arm C at the line boundary can only see suppression outside "
                               f"[{lo if lo is not None else '-inf'}, "
                               f"{hi if hi is not None else '+inf'}]; inside that band it is "
                               "blind, and the observed value sits inside it.")}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def run(nperm=NPERM, seed=3301, verbose=True):
    rng = np.random.default_rng(seed)
    g = Geometry()
    x = np.array(g.runes)
    n = len(x)
    pil = np.array(g.pos_in_line)
    piw = np.array(g.pos_in_word)
    page = np.array(g.page_of)

    # transitions i-1 -> i, excluding page boundaries (nothing precedes a new page)
    trans = np.arange(1, n)
    trans = trans[page[trans] == page[trans - 1]]
    prev, cur = x[trans - 1], x[trans]
    dbl = (prev == cur)
    at_line0 = (pil[trans] == 0)
    at_word0 = (piw[trans] == 0)

    res = {}

    # ---------------- C1  doublet rate by within-line position bucket ----------
    def bucket_line(p):
        return np.where(p == 0, 0, np.where(p == 1, 1, np.where(p <= 4, 2, 3)))

    bl = bucket_line(pil[trans])
    tab = np.array([[dbl[bl == b].sum(), (bl == b).sum()] for b in range(4)], dtype=float)
    # expected match prob per bucket from the ACTUAL marginals of that bucket
    exp_p = []
    for b in range(4):
        m = bl == b
        pp = np.bincount(prev[m], minlength=N) / m.sum()
        pc = np.bincount(cur[m], minlength=N) / m.sum()
        exp_p.append(float((pp * pc).sum()))
    exp_p = np.array(exp_p)
    supp = 1 - (tab[:, 0] / tab[:, 1]) / exp_p
    ci = [wilson(int(tab[b, 0]), int(tab[b, 1])) for b in range(4)]

    # null: permute line-initial runes among themselves (preserves their marginal)
    init_pos = np.array(g.subsets()["A1_line_initial"])
    init_pos = init_pos[page[init_pos] == page[np.maximum(init_pos - 1, 0)]]  # has a predecessor
    ipos = np.array(g.subsets()["A1_line_initial"])
    ivals = x[ipos]
    # H0 = ONE suppression s applied everywhere. The per-bucket collision baseline
    # exp_p differs slightly (the line-initial marginal is size-biased, see
    # confound_layout.py), so the H0 expectation is n_b * exp_p_b * (1-s_pooled),
    # NOT n_b * pooled_rate. Getting this wrong is what makes a null that destroys
    # the filter and returns p = 1.0000.
    stat_obs = _g2_weighted(tab[:, 0], tab[:, 1] * exp_p)
    nullv = _alloc_null(tab[:, 0].sum(), tab[:, 1] * exp_p, rng, nperm)
    p_c1 = (1.0 + np.sum(nullv >= stat_obs)) / (1.0 + len(nullv))
    res["C1_doublet_rate_by_line_position"] = {
        "buckets": ["p=0 (crosses line break)", "p=1", "p=2..4", "p>=5"],
        "doublets": tab[:, 0].tolist(), "transitions": tab[:, 1].tolist(),
        "rate": (tab[:, 0] / tab[:, 1]).tolist(),
        "expected_indep_rate": exp_p.tolist(),
        "suppression_s": supp.tolist(),
        "rate_wilson95": ci,
        "statistic_G2": stat_obs, "p_empirical": float(p_c1),
        "verdict": "HIT" if p_c1 < ALPHA_TEST else ("SUBTHRESHOLD" if p_c1 < 0.001 else "NEGATIVE"),
    }

    # ---------------- C2  doublet rate by within-word position ----------------
    bw = np.where(piw[trans] == 0, 0, np.where(piw[trans] == 1, 1, 2))
    tab2 = np.array([[dbl[bw == b].sum(), (bw == b).sum()] for b in range(3)], dtype=float)
    exp2 = []
    for b in range(3):
        m = bw == b
        pp = np.bincount(prev[m], minlength=N) / m.sum()
        pc = np.bincount(cur[m], minlength=N) / m.sum()
        exp2.append(float((pp * pc).sum()))
    exp2 = np.array(exp2)
    g2_obs = _g2_weighted(tab2[:, 0], tab2[:, 1] * exp2)
    null2 = _alloc_null(tab2[:, 0].sum(), tab2[:, 1] * exp2, rng, nperm)
    p_c2 = (1.0 + np.sum(null2 >= g2_obs)) / (1.0 + len(null2))
    res["C2_doublet_rate_by_word_position"] = {
        "buckets": ["p=0 (crosses word break)", "p=1", "p>=2"],
        "doublets": tab2[:, 0].tolist(), "transitions": tab2[:, 1].tolist(),
        "rate": (tab2[:, 0] / tab2[:, 1]).tolist(),
        "expected_indep_rate": exp2.tolist(),
        "suppression_s": (1 - (tab2[:, 0] / tab2[:, 1]) / exp2).tolist(),
        "statistic_G2": g2_obs, "p_empirical": float(p_c2),
        "verdict": "HIT" if p_c2 < ALPHA_TEST else ("SUBTHRESHOLD" if p_c2 < 0.001 else "NEGATIVE"),
    }

    # ---------------- C3  suppression equality, line-boundary vs within --------
    k0, n0 = int(dbl[at_line0].sum()), int(at_line0.sum())
    k1, n1 = int(dbl[~at_line0].sum()), int((~at_line0).sum())
    s0 = 1 - (k0 / n0) / exp_p[0]
    p_in = np.bincount(prev[~at_line0], minlength=N) / n1
    c_in = np.bincount(cur[~at_line0], minlength=N) / n1
    e_in = float((p_in * c_in).sum())
    s1 = 1 - (k1 / n1) / e_in
    lo0, hi0 = wilson(k0, n0)
    res["C3_suppression_boundary_vs_interior"] = {
        "line_boundary": {"doublets": k0, "transitions": n0, "rate": k0 / n0,
                          "expected_indep": exp_p[0], "s": s0,
                          "s_95ci": [1 - hi0 / exp_p[0], 1 - lo0 / exp_p[0]]},
        "interior": {"doublets": k1, "transitions": n1, "rate": k1 / n1,
                     "expected_indep": e_in, "s": s1},
        "round17_reference_s": 0.8075,
        "note": ("two-sided; excess OR deficit at the boundary is evidence. "
                 "The boundary CI is the lane's power limit for Arm C."),
        "detectable_band_alpha_prereg": _detectable_band(n0, exp_p[0], s1),
        "detectable_band_alpha_0p05": _detectable_band(n0, exp_p[0], s1, alpha=0.05),
    }

    # ---------------- C4  difference channel at the boundary ------------------
    # Bins 1..28 ONLY. The d = 0 bin is the anti-repeat filter itself, a KNOWN H0
    # property, and it is adjudicated by C1/C3; leaving it in makes any permutation
    # null that reshuffles line initials produce a guaranteed false alarm.
    d_all = (cur - prev) % N
    d0 = np.bincount(d_all[at_line0], minlength=N).astype(float)[1:]
    d1 = np.bincount(d_all[~at_line0], minlength=N).astype(float)[1:]
    obs_chi = _homog_chi2(d0, d1)
    null4 = _perm_null_c4(x, trans, pil, rng, min(nperm, 50000))
    p_c4 = (1.0 + np.sum(null4 >= obs_chi)) / (1.0 + len(null4))
    res["C4_difference_channel_at_line_boundary"] = {
        "n_boundary_transitions": int(at_line0.sum()),
        "n_interior_transitions": int((~at_line0).sum()),
        "chi2_homogeneity_27df_bins_1_28": obs_chi,
        "null_mean": float(null4.mean()), "null_p95": float(np.quantile(null4, .95)),
        "p_empirical": float(p_c4), "nperm": int(len(null4)),
        "verdict": "HIT" if p_c4 < ALPHA_TEST else ("SUBTHRESHOLD" if p_c4 < 0.001 else "NEGATIVE"),
    }

    # ---------------- C5  MI(line-final, next line-initial) -------------------
    pairs = [(x[t - 1], x[t]) for t in trans[at_line0]]
    mi_obs = _mi(pairs)
    a = np.array([p for p, _ in pairs]); bvals = np.array([c for _, c in pairs])
    null5 = np.empty(min(nperm, 100000))
    for i in range(len(null5)):
        bb = rng.permutation(bvals)
        null5[i] = _mi(list(zip(a, bb)))
    p_c5 = (1.0 + np.sum(null5 >= mi_obs)) / (1.0 + len(null5))
    res["C5_MI_linefinal_to_next_lineinitial"] = {
        "n_pairs": len(pairs), "MI_bits": mi_obs,
        "null_mean_bits": float(null5.mean()), "null_p95_bits": float(np.quantile(null5, .95)),
        "p_empirical": float(p_c5), "nperm": int(len(null5)),
        "verdict": "HIT" if p_c5 < ALPHA_TEST else ("SUBTHRESHOLD" if p_c5 < 0.001 else "NEGATIVE"),
        "note": "MI is positively biased at this n; the permutation null carries the same bias.",
    }

    # ---------------- C6  full within-line doublet profile (descriptive) ------
    prof = []
    for p in range(0, int(pil[trans].max()) + 1):
        m = pil[trans] == p
        if m.sum() < 50:
            continue
        prof.append({"pos": p, "transitions": int(m.sum()), "doublets": int(dbl[m].sum()),
                     "rate": float(dbl[m].mean())})
    res["C6_profile"] = prof

    if verbose:
        for k, v in res.items():
            if k == "C6_profile":
                continue
            print(f"{k}: {v.get('verdict', '-')}  p={v.get('p_empirical', float('nan'))}")
    return res


def _c1_stat(tab):
    """G^2 for a 2 x k table of (successes, trials)."""
    k = tab[:, 0]; nn = tab[:, 1]
    p = k.sum() / nn.sum()
    g2 = 0.0
    for i in range(len(k)):
        for obs, exp in ((k[i], nn[i] * p), (nn[i] - k[i], nn[i] * (1 - p))):
            if obs > 0:
                g2 += 2 * obs * math.log(obs / exp)
    return float(g2)


def _homog_chi2(a, b):
    tot = a + b
    na, nb = a.sum(), b.sum()
    s = 0.0
    for i in range(len(a)):
        if tot[i] == 0:
            continue
        ea = tot[i] * na / (na + nb); eb = tot[i] * nb / (na + nb)
        s += (a[i] - ea) ** 2 / ea + (b[i] - eb) ** 2 / eb
    return float(s)


def _mi(pairs):
    from collections import Counter
    ca, cb, cab = Counter(), Counter(), Counter()
    for p, c in pairs:
        ca[p] += 1; cb[c] += 1; cab[(p, c)] += 1
    n = len(pairs)
    mi = 0.0
    for (p, c), v in cab.items():
        mi += (v / n) * math.log2((v / n) / ((ca[p] / n) * (cb[c] / n)))
    return mi


def _perm_null_c4(x, trans, pil, rng, nperm):
    """Permute line-initial runes among themselves, then DROP any pair that would be a
    doublet, so the null carries the same anti-repeat conditioning as the data. Bins
    1..28 only."""
    at0 = pil[trans] == 0
    prev_of_init = x[trans[at0] - 1]
    ivals = x[trans[at0]]
    dint = (x[trans[~at0]] - x[trans[~at0] - 1]) % N
    d1 = np.bincount(dint[dint != 0], minlength=N).astype(float)[1:]
    out = np.empty(nperm)
    for i in range(nperm):
        v = rng.permutation(ivals)
        d = (v - prev_of_init) % N
        d0 = np.bincount(d[d != 0], minlength=N).astype(float)[1:]
        out[i] = _homog_chi2(d0, d1)
    return out


def _g2_weighted(obs, w):
    """G^2 for counts obs_b against expectations proportional to w_b."""
    exp = w / w.sum() * obs.sum()
    return float(sum(2 * o * math.log(o / e) for o, e in zip(obs, exp) if o > 0))


def _alloc_null(total, w, rng, nperm):
    """H0: the total doublets are allocated across buckets in proportion to w."""
    nperm = int(min(nperm, 200000))
    p = np.asarray(w, dtype=float); p = p / p.sum()
    draws = rng.multinomial(int(total), p, size=nperm).astype(float)
    exp = p * total
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(draws > 0, 2 * draws * np.log(draws / exp), 0.0)
    return term.sum(axis=1)


if __name__ == "__main__":
    nperm = int(sys.argv[1]) if len(sys.argv) > 1 else NPERM
    print(f"Arm C — position-conditioned filter signature   alpha_test={ALPHA_TEST:.4g}")
    r = run(nperm=nperm)
    json.dump({"alpha_test": ALPHA_TEST, "tests": r},
              open(os.path.join(HERE, "results_armC.json"), "w"), indent=2)
    for k, v in r.items():
        print()
        print(k)
        print(json.dumps(v, indent=2)[:1400])
    print("\nwrote results_armC.json")
