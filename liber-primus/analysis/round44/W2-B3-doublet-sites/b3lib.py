"""R44 / W2-B3 shared glue — doublet-site census, channel builders, grid, nulls, battery.

ONE code path used identically by plants, nulls and the real reads (R42 X1 rule).
Everything pre-registered in PREREG.md (sha-stamped in run.log before first execution).
"""
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

from lp import gematria as gp  # noqa: E402
import adjudicate as A  # noqa: E402

N = gp.N                       # 29
SEED = 3301
N_BUDGET = 928                 # PREREG: 8 streams x 116 maps, bars fixed at this
ALPHA = 0.01
POWER_FLOOR = 0.5
D_NULL = 1000
BATT_ALPHA = ALPHA / 7.0       # 0.001428... Bonferroni over the 7 battery tests
N_PAGES_U = 55


def panel():
    return A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))


def canon_segments():
    txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    kept = [s for s in txt.split("%") if gp.runes_to_indices(s)]
    assert len(kept) == 57, len(kept)
    return kept


def stream_pages(which):
    """which='U' -> unsolved segments 0..54 (12,956 runes, the D-01 object);
    which='C' -> all 57 segments (13,136 runes).  Returns (x, page) int64 arrays."""
    kept = canon_segments()
    segs = kept[:-2] if which == "U" else kept
    stream, page = [], []
    for pg, s in enumerate(segs):
        for ch in s:
            if ch in gp.RUNE_TO_IDX:
                stream.append(gp.RUNE_TO_IDX[ch])
                page.append(pg)
    x = np.asarray(stream, dtype=np.int64)
    p = np.asarray(page, dtype=np.int64)
    assert len(x) == (12956 if which == "U" else 13136), len(x)
    return x, p


def sites(x):
    """Site positions = global 0-based index of the FIRST rune of each adjacent equal pair."""
    return np.flatnonzero(x[1:] == x[:-1])


def channels(x, page, n_pages):
    """The four pre-registered channel streams from one raw rune stream."""
    p = sites(x)
    v = x[p]                                            # doubled values, site order
    g = np.diff(p)                                      # gaps
    cnt = np.bincount(page[p], minlength=n_pages)[:n_pages]
    return {
        "dblvals": v,
        "gapsmod29": g % N,
        "posmod29": p % N,
        "pagecounts": cnt % N,
    }, p, g, cnt


# ------------------------------------------------------------------ 116-map grid (W2-A1 shape)
def grid(x):
    rows, meta = [], []
    for dname, vv in (("fwd", np.asarray(x, dtype=np.int64)),
                      ("rev", np.asarray(x, dtype=np.int64)[::-1])):
        for a in (1, N - 1):
            for s in range(N):
                rows.append((a * vv + s) % N)
                meta.append(dict(dir=dname, a=int(a), s=int(s)))
    return np.stack(rows), meta


def grid_pmax(x, pan):
    X, meta = grid(x)
    r = A.adjudicate_batch(X, pan=pan)
    return r["pmax"], r, X, meta


def stream_degenerate(x):
    """mds and IoC are invariant under the 116 affine/reversal maps, so degeneracy
    (R38 guard) is a property of the STREAM; one call decides all 116 readings."""
    x = np.asarray(x, dtype=np.int64)
    return bool(A.is_degenerate(A.min_distinct(x), A.ioc_n(x)))


def best_reading(x, pan):
    """Best-of-116 for one stream: (best pmax, argmax meta, full adjudicate record,
    stream-level degenerate flag)."""
    pm, r, X, meta = grid_pmax(x, pan)
    j = int(np.argmax(pm))
    full = A.adjudicate(X[j], pan=pan)
    return float(pm[j]), meta[j], full, stream_degenerate(x)


# ------------------------------------------------------------------ dfshuffle (round41 lib, verbatim)
def dfshuffle(seq, rng, target):
    """histogram-preserving shuffle repaired to <= target adjacent equal pairs."""
    x = list(seq)
    rng.shuffle(x)
    n = len(x)
    bad = [i for i in range(n - 1) if x[i] == x[i + 1]]
    cnt = len(bad)
    for i in bad:
        if cnt <= target:
            break
        if x[i] != x[i + 1]:
            continue
        for _ in range(40):
            j = rng.randrange(2, n - 2)
            if abs(j - i) < 3:
                continue
            a, b = x[i + 1], x[j]
            if b != x[i] and b != x[i + 2] and a != x[j - 1] and a != x[j + 1] and a != b:
                x[i + 1], x[j] = b, a
                cnt -= 1
                break
    return np.asarray(x, dtype=np.int64)


def site_matched_shuffle(x, rng, target, max_passes=200000):
    """PREREG Addendum 1 surrogate: histogram-preserving shuffle with EXACTLY `target`
    adjacent equal pairs whose positions carry no order bias — repairs are chosen
    UNIFORMLY AT RANDOM among current bad pairs, with a full recount per repair.
    rng: python random.Random."""
    while True:
        y = list(x)
        rng.shuffle(y)
        n = len(y)
        bad = [i for i in range(n - 1) if y[i] == y[i + 1]]
        passes = 0
        while len(bad) > target and passes < max_passes:
            passes += 1
            i = bad[rng.randrange(len(bad))]
            for _ in range(60):
                j = rng.randrange(2, n - 2)
                if abs(j - i) < 3:
                    continue
                a, b = y[i + 1], y[j]
                right = y[i + 2] if i + 2 < n else None
                if (b != y[i] and b != right and a != y[j - 1]
                        and a != y[j + 1] and a != b):
                    y[i + 1], y[j] = b, a
                    break
            lo = max(0, min(i, j) - 2)
            hi = min(n - 1, max(i, j) + 2)
            bad = [k for k in bad if not (lo <= k <= hi) and y[k] == y[k + 1]] + \
                  [k for k in range(lo, hi) if y[k] == y[k + 1]]
            bad = sorted(set(bad))
        arr = np.asarray(y, dtype=np.int64)
        if len(sites(arr)) == target:
            return arr


def zero_doublet_base(x, rng):
    """A doublet-free histogram-preserving shuffle of x (plant base)."""
    return site_matched_shuffle(x, rng, target=0)


# ------------------------------------------------------------------ POT bar (bars_v3 model, W2-A1 code shape)
def pot_fit(vals):
    v = np.asarray(vals, dtype=np.float64)
    u = float(np.quantile(v, 0.90))
    exc = v[v > u] - u
    return u, float((v > u).mean()), float(exc.mean()), int(len(exc))


def pot_bar(u, p_u, beta, Nreal=N_BUDGET, alpha=ALPHA):
    mu = u + beta * math.log(p_u)
    return mu + beta * math.log(Nreal / -math.log1p(-alpha))


# ------------------------------------------------------------------ battery statistics (PREREG T1-T7)
def ks_uniform(pos, n_total):
    u = np.sort(pos / float(n_total))
    k = len(u)
    i = np.arange(1, k + 1)
    return float(max(np.max(i / k - u), np.max(u - (i - 1) / k)))


def battery_stats(x, page, n_pages, n_total):
    p = sites(x)
    v = x[p]
    g = np.diff(p).astype(float)
    cnt = np.bincount(page[p], minlength=n_pages)[:n_pages].astype(float)
    # T6: binomial dispersion of per-page counts around one fitted rate (D-01 test 6 statistic)
    mm = np.bincount(page[:-1][page[:-1] == page[1:]], minlength=n_pages)[:n_pages].astype(float)
    phat = cnt.sum() / mm.sum()
    var = mm * phat * (1 - phat)
    keep = var > 0
    disp = float((((cnt - mm * phat) ** 2 / var)[keep]).sum() / (keep.sum() - 1))
    vc = np.bincount(v, minlength=N).astype(float)
    ac = 0.0
    if len(g) > 2 and g.std() > 0:
        ac = float(np.corrcoef(g[:-1], g[1:])[0, 1])
    return {
        "T1_ks": ks_uniform(p, n_total),
        "T2_gapcv2": float(g.var() / g.mean() ** 2),
        "T3_chi2_mod29": _chi2_uniform(p % 29, 29),
        "T4_chi2_mod60": _chi2_uniform(p % 60, 60),
        "T5_valuecounts": vc,          # vector; chi2 vs null mean computed by caller
        "T6_dispersion": disp,
        "T7_gap_ac1": ac,
    }


def _chi2_uniform(vals, k):
    c = np.bincount(vals, minlength=k).astype(float)
    e = c.sum() / k
    return float(((c - e) ** 2 / e).sum())


def addone_upper(null, obs):
    null = np.asarray(null, dtype=float)
    return float((1 + (null >= obs).sum()) / (len(null) + 1))


def addone_two(null, obs):
    null = np.asarray(null, dtype=float)
    lo = (1 + (null <= obs).sum()) / (len(null) + 1)
    hi = (1 + (null >= obs).sum()) / (len(null) + 1)
    return float(min(1.0, 2.0 * min(lo, hi)))


# ------------------------------------------------------------------ held-out English plant windows (W2-A1 code)
_EN_CACHE = None


def english_windows(L, n_win, rng):
    global _EN_CACHE
    if _EN_CACHE is not None:
        s = _EN_CACHE
        starts = rng.integers(0, len(s) - L, size=n_win)
        return np.stack([s[a:a + L] for a in starts])
    path = os.path.join(LP, "data", "keys", "self_reliance.txt")
    raw = open(path, encoding="utf-8", errors="ignore").read()
    raw = raw[len(raw) // 2:]                     # the panel build's reserved plant half
    out = []
    for w in raw.split():
        w = "".join(ch for ch in w.upper() if ch.isalpha())
        if not w:
            continue
        try:
            out.extend(gp.keyword_to_indices(w))
        except Exception:
            pass
    s = np.asarray(out, dtype=np.int64)
    _EN_CACHE = s
    starts = rng.integers(0, len(s) - L, size=n_win)
    return np.stack([s[a:a + L] for a in starts])


# ------------------------------------------------------------------ plant injectors (through the SAME glue)
def inject_value_sites(base, positions, values):
    """Set base[p]=base[p+1]=values[j] at each position; positions must be >=1 apart by 3
    and interior.  Returns the modified stream; caller re-extracts via sites()."""
    y = base.copy()
    for p, v in zip(positions, values):
        y[p] = v
        y[p + 1] = v
        # keep neighbours from accidentally extending/creating doublets
        if p - 1 >= 0 and y[p - 1] == v:
            y[p - 1] = (v + 1) % N
            if p - 2 >= 0 and y[p - 2] == y[p - 1]:
                y[p - 1] = (v + 2) % N
        if p + 2 < len(y) and y[p + 2] == v:
            y[p + 2] = (v + 1) % N
            if p + 3 < len(y) and y[p + 3] == y[p + 2]:
                y[p + 2] = (v + 2) % N
    return y


def random_positions(n_sites, n_total, rng, min_gap=5):
    """Uniform-ish site positions with a minimum separation (interior)."""
    while True:
        p = np.sort(rng.choice(np.arange(5, n_total - 5), size=n_sites, replace=False))
        if np.all(np.diff(p) >= min_gap):
            return p


def positions_from_gaps(gaps, start=10):
    p = start + np.concatenate([[0], np.cumsum(gaps)])
    return p.astype(np.int64)
