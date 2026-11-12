"""R44 / W2-C5 shared glue — powered per-page doublet-rate stationarity test.

ONE code path used identically by the plant gate and the real run (R42 X1 rule).
Registered in PREREG.md (sha256-stamped in run.log before first execution).
"""
import math
import os
import sys

import numpy as np
from scipy.stats import binom

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(LP, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from lp import gematria as gp  # noqa: E402

N = 29
ALPHA_FAMILY = 0.01
N_TESTS = 3
BAR_PER_TEST = ALPHA_FAMILY / N_TESTS          # 0.0033333...
BAR_PAGE = ALPHA_FAMILY / 55                   # 1.818e-4, Bonferroni over 55 pages
D_REAL = 10_000
D_PLANT = 2_000
R_PLANT = 400
FLAGGED = [19, 24, 27, 29, 44]                 # 0-based U-stream segments (B3-pinned)
Q_UNIF = 1.0 / N


# ------------------------------------------------------------------ census (D-01 object)
def real_pages():
    """55 unsolved segments as lists of rune indices (12,956 runes total)."""
    txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    kept = [s for s in txt.split("%") if gp.runes_to_indices(s)]
    assert len(kept) == 57, len(kept)
    pages = []
    for s in kept[:-2]:
        pages.append([gp.RUNE_TO_IDX[ch] for ch in s if ch in gp.RUNE_TO_IDX])
    assert sum(len(p) for p in pages) == 12_956
    assert len(pages) == 55
    return pages


def page_counts(pages):
    """(c, m): per-page doublet counts and per-page within-page adjacent-pair counts.
    Doublet = adjacent equal pair, counted within a page only (cross-page joins excluded)."""
    c = np.empty(len(pages), dtype=np.int64)
    m = np.empty(len(pages), dtype=np.int64)
    for i, pg in enumerate(pages):
        a = np.asarray(pg, dtype=np.int64)
        m[i] = len(a) - 1
        c[i] = int(np.count_nonzero(a[1:] == a[:-1]))
    return c, m


# ------------------------------------------------------------------ registered statistics
def g_stat(c, m, r):
    """Binomial LRT: saturated per-page rates vs common rate r."""
    c = c.astype(float)
    m = m.astype(float)
    e = m * r
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = np.where(c > 0, c * np.log(c / e), 0.0)
        t2 = np.where(m - c > 0, (m - c) * np.log((m - c) / (m - e)), 0.0)
    return float(2.0 * (t1 + t2).sum())


def tarone_z(c, m, r):
    c = c.astype(float)
    m = m.astype(float)
    s = (((c - m * r) ** 2) / (r * (1.0 - r))).sum()
    return float((s - m.sum()) / math.sqrt(2.0 * (m * (m - 1.0)).sum()))


def page_pvals(c, m, r):
    """Exact binomial upper tails P(Bin(m_i, r) >= c_i)."""
    return binom.sf(c - 1, m, r)


def stats_triple(c, m):
    r = c.sum() / m.sum()
    pv = page_pvals(c, m, r)
    return g_stat(c, m, r), tarone_z(c, m, r), float(pv.min()), r, pv


# ------------------------------------------------------------------ bootstrap null (vectorised)
def null_table(m, r0, D, rng):
    """Draw D parametric-bootstrap replicates of (G, Z, minp) under H0 at rate r0,
    refitting r per draw (same estimator as the observed statistics)."""
    m = m.astype(np.int64)
    C = rng.binomial(m[None, :], r0, size=(D, len(m))).astype(float)
    M = m.astype(float)[None, :]
    rhat = C.sum(axis=1, keepdims=True) / M.sum()
    rhat = np.clip(rhat, 1e-12, 1 - 1e-12)
    E = M * rhat
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = np.where(C > 0, C * np.log(C / E), 0.0)
        t2 = np.where(M - C > 0, (M - C) * np.log((M - C) / (M - E)), 0.0)
    G = 2.0 * (t1 + t2).sum(axis=1)
    S = (((C - E) ** 2) / (rhat * (1.0 - rhat))).sum(axis=1)
    Z = (S - M.sum()) / np.sqrt(2.0 * (M * (M - 1.0)).sum())
    PV = binom.sf(C - 1.0, M.astype(np.int64), rhat)
    return G, Z, PV.min(axis=1)


def addone_upper(null, obs):
    null = np.asarray(null, dtype=float)
    return float((1 + (null >= obs).sum()) / (len(null) + 1))


def addone_lowtail(null, obs):
    """Upper significance for a LOW observed value (min-p: smaller = more extreme)."""
    null = np.asarray(null, dtype=float)
    return float((1 + (null <= obs).sum()) / (len(null) + 1))


def addone_two(null, obs):
    null = np.asarray(null, dtype=float)
    lo = (1 + (null <= obs).sum()) / (len(null) + 1)
    hi = (1 + (null >= obs).sum()) / (len(null) + 1)
    return float(min(1.0, 2.0 * min(lo, hi)))


def test_pvalues(c, m, D, rng):
    """The full registered procedure on one dataset: three bootstrap p-values.
    T1 G upper; T2 Tarone two-sided; T3 min-p low-tail (family-wise)."""
    G, Z, minp, r0, pv = stats_triple(c, m)
    nG, nZ, nM = null_table(m, r0, D, rng)
    return {
        "r_hat": r0,
        "G": G, "p_G": addone_upper(nG, G),
        "Z": Z, "p_Z": addone_two(nZ, Z),
        "minp": minp, "p_minp": addone_lowtail(nM, minp),
        "page_pvals": pv,
    }


def fired(res):
    return (res["p_G"] <= BAR_PER_TEST or res["p_Z"] <= BAR_PER_TEST
            or res["p_minp"] <= BAR_PER_TEST)


# ------------------------------------------------------------------ plant generator
R_GLOBAL = 86.0 / 12_901.0                     # real within-page doublet rate (R12-D2: 0.667%)
K_UNFILTERED = Q_UNIF / R_GLOBAL               # p_keep = 1 on the elevated pages (= 5.173)


def p_keep_of_rate(r, q=Q_UNIF):
    """Invert r = q*p/(1 - q*(1-p)) for the rejection-filter keep probability."""
    return r * (1.0 - q) / (q * (1.0 - r))


def sample_filtered_page(n, r, rng):
    """Exact emitted-chain sampler of a flat rejection filter over a uniform base:
    x_t = x_{t-1} w.p. r, else uniform over the other 28 symbols.
    Vectorised: non-repeat steps add a uniform offset in 1..28 (mod 29); repeats add 0."""
    if n <= 0:
        return np.empty(0, dtype=np.int64)
    d = rng.integers(1, N, size=n - 1)
    d[rng.random(n - 1) < r] = 0
    x0 = rng.integers(0, N)
    return (x0 + np.concatenate([[0], np.cumsum(d)])) % N


def plant_book(page_lens, elev_pages, k, rng):
    """Synthetic book with the REAL page lengths; elevated pages at rate k*R_GLOBAL."""
    relev = k * R_GLOBAL
    assert relev <= Q_UNIF + 1e-12, "k beyond the unfiltered ceiling"
    pages = []
    for i, L in enumerate(page_lens):
        r = relev if i in elev_pages else R_GLOBAL
        pages.append(sample_filtered_page(L, r, rng).tolist())
    return pages
