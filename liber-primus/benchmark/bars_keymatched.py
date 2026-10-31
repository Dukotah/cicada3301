"""Round 39 T1: the standing KEY-MATCHED null for ciphertext-derived key families (the I2-R38 recipe, generic).

A family whose key is a function of the ciphertext (X4 prime/totient maps, N4/N5 cells, ...) must be nulled by
shuffling the ciphertext and RE-DERIVING the key from each shuffle: a bar from a fixed-key null is too low
(R38 I2: transferred 5.6-5.7 vs key-matched 6.994 at L=120).

    bar_keymatched(derive_key_fn, decode_fn, L, N, draws, seed=3301, stream=..., alpha=0.01)

per draw j: S = doublet-matched shuffle of `stream` (Random(seed+j)); members = derive_key_fn(S); for each member,
decode_fn(member, L) -> iterable of decodes (rune-index sequences; one per window/relation); each decode is
adjudicated, degenerate decodes (mds <= 6 or IoC*N >= 4.24) are DROPPED, the draw's value is the max pmax over the
rest (the family max).  The bar is the empirical (1-alpha) quantile of the draws' family maxima when N equals the
null's family size (N0 = non-degenerate rows per draw); for N != N0 a Gumbel fit (moments) shifted by beta*ln(N/N0).

`bar_from_maxima(maxima, N, N0, alpha)` is the pure part (no decoding); `family_maxima_from_rows(path, rel)` reads a
stored R38 `null_rows_L*.jsonl` so the X4 bar reproduces without re-decoding.
"""
import json, math, os, random, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))

DOUBLET_TARGET = 86            # LP2 adjacent-equal-pair level (R37 C3 / R38 I2)
_EULER = 0.5772156649015329


def is_degenerate(mds, ioc_n):
    return bool(mds <= 6 or ioc_n >= 4.24)


def dfshuffle(seq, rng, target=DOUBLET_TARGET):
    """histogram-preserving shuffle repaired to <= `target` adjacent equal pairs (as round37/C3 rescore.py)."""
    x = list(seq); rng.shuffle(x); n = len(x)
    bad = [i for i in range(n - 1) if x[i] == x[i + 1]]; cnt = len(bad)
    for i in bad:
        if cnt <= target: break
        if x[i] != x[i + 1]: continue
        for _ in range(40):
            j = rng.randrange(2, n - 2)
            if abs(j - i) < 3: continue
            a, b = x[i + 1], x[j]
            if b != x[i] and b != x[i + 2] and a != x[j - 1] and a != x[j + 1] and a != b:
                x[i + 1], x[j] = b, a; cnt -= 1; break
    return x


def gumbel_params(maxima):
    m = np.asarray(maxima, float); beta = m.std(ddof=1) * math.sqrt(6) / math.pi
    return m.mean() - _EULER * beta, beta


def bar_from_maxima(maxima, N=None, N0=None, alpha=0.01):
    """Empirical (1-alpha) quantile when N is None or == N0; else Gumbel(moments) shifted by beta*ln(N/N0)."""
    m = np.asarray(maxima, float)
    if N is None or N0 is None or N == N0:
        return float(np.quantile(m, 1 - alpha))
    mu, beta = gumbel_params(m)
    return float(mu + beta * math.log(N / N0) - beta * math.log(-math.log1p(-alpha)))


def draw_family_max(stream, derive_key_fn, decode_fn, L, j, seed=3301, pan=None, adjudicate_fn=None):
    """One shuffle's family max over non-degenerate decodes -> (max or None, n_nondegenerate, n_degenerate)."""
    if adjudicate_fn is None:
        import adjudicate as AD
        adjudicate_fn = lambda x: AD.adjudicate(x, pan=pan)
    S = dfshuffle(stream, random.Random(seed + j))
    best, nd, dg = None, 0, 0
    for member in derive_key_fn(S):
        for plain in decode_fn(member, L):
            a = adjudicate_fn(plain)
            if is_degenerate(a["mds"], a["ioc"]):
                dg += 1; continue
            nd += 1
            if best is None or a["pmax"] > best: best = float(a["pmax"])
    return best, nd, dg


def bar_keymatched(derive_key_fn, decode_fn, L, N, draws, seed=3301, stream=None, alpha=0.01, pan=None,
                   adjudicate_fn=None, with_maxima=False):
    """The key-matched family-wise bar at N (see module doc).  `stream` = the LP2 stream (required)."""
    if stream is None:
        raise ValueError("stream (the LP2 rune-index stream to shuffle) is required")
    maxima, n0 = [], None
    for j in range(draws):
        b, nd, _ = draw_family_max(stream, derive_key_fn, decode_fn, L, j, seed, pan, adjudicate_fn)
        if b is not None: maxima.append(b)
        n0 = nd if n0 is None else n0
    if not maxima:
        raise RuntimeError("every decode of every draw was degenerate")
    bar = bar_from_maxima(maxima, N, n0, alpha)
    return (bar, maxima, n0) if with_maxima else bar


def family_maxima_from_rows(path, rel):
    """Stored R38 I2 `null_rows_L*.jsonl` -> per-shuffle family max over non-degenerate rows of relation `rel`.
    rows are [cfg, start, rel, pmax, mds, ioc*N]."""
    out = []
    for line in open(path, encoding="utf-8"):
        rows = [r for r in json.loads(line)["rows"] if r[2] == rel and not is_degenerate(r[4], r[5])]
        if rows: out.append(max(r[3] for r in rows))
    return out
