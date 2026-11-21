"""R44 / W2-C1 — the six-statistic order/identity battery (PREREG 5a).

seed-3301 nulls, 10,000 draws each, mirroring R22-D. Survivor iff any p < 0.01/6.
"""
import zlib

import numpy as np

NDRAW = 10000
SEED = 3301


def _spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    d = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / d) if d > 0 else 0.0


def S1_presence_gaps(present_pages, n_pages=56, rng=None):
    """Variance of gaps between consecutive motif-bearing pages vs uniform placement."""
    rng = rng or np.random.default_rng(SEED)
    pp = sorted(present_pages)
    obs = float(np.var(np.diff(pp))) if len(pp) > 2 else 0.0
    cnt = 0
    for _ in range(NDRAW):
        s = np.sort(rng.choice(n_pages, size=len(pp), replace=False))
        if np.var(np.diff(s)) >= obs:
            cnt += 1
    return (cnt + 1) / (NDRAW + 1)


def S2_spearman_count(V, rng=None):
    rng = rng or np.random.default_rng(SEED)
    V = np.asarray(V, dtype=float)
    idx = np.arange(len(V), dtype=float)
    obs = abs(_spearman(V, idx))
    cnt = 0
    for _ in range(NDRAW):
        if abs(_spearman(rng.permutation(V), idx)) >= obs:
            cnt += 1
    return (cnt + 1) / (NDRAW + 1)


def _zlib_p(tokens, rng):
    toks = list(tokens)
    vocab = {t: i for i, t in enumerate(dict.fromkeys(toks))}
    arr = bytes(vocab[t] for t in toks)
    obs = len(zlib.compress(arr, 9))
    a = np.frombuffer(arr, dtype=np.uint8).copy()
    cnt = 0
    for _ in range(NDRAW):
        rng.shuffle(a)
        if len(zlib.compress(a.tobytes(), 9)) <= obs:
            cnt += 1
    return (cnt + 1) / (NDRAW + 1)


def S3_zlib_type(T, rng=None):
    return _zlib_p(T, rng or np.random.default_rng(SEED))


def S4_zlib_orient(O, rng=None):
    return _zlib_p(O, rng or np.random.default_rng(SEED))


def S5_prime_counts(V, rng=None):
    rng = rng or np.random.default_rng(SEED)
    nz = [v for v in V if v > 0]
    PR = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    obs = sum(1 for v in nz if v in PR)
    mx = max(nz)
    cnt = 0
    for _ in range(NDRAW):
        d = rng.integers(1, mx + 1, size=len(nz))
        if sum(1 for v in d if int(v) in PR) >= obs:
            cnt += 1
    return (cnt + 1) / (NDRAW + 1)


def S6_centroid_y(pairs, rng=None):
    """pairs: (page, centroid_y) per motif; |spearman| of y vs page over motifs."""
    rng = rng or np.random.default_rng(SEED)
    pg = np.asarray([p for p, y in pairs], dtype=float)
    ys = np.asarray([y for p, y in pairs], dtype=float)
    obs = abs(_spearman(ys, pg))
    cnt = 0
    for _ in range(NDRAW):
        if abs(_spearman(rng.permutation(ys), pg)) >= obs:
            cnt += 1
    return (cnt + 1) / (NDRAW + 1)
