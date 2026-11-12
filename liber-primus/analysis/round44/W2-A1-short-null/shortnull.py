"""R44 / W2-A1 shared glue: the short-stream reading grid + canon + panel (PREREG §3).

ONE grid function used identically by the null build, the plants, and the real reads —
the R42 X1 plant-through-own-glue rule depends on this file being the single code path.
"""
import os
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

N = gp.N
SEED = 3301
L_NODES = (13, 26, 30, 40, 120)
N_BUDGET = 600          # PREREG §3: bars fixed at this real-decode budget
ALPHA = 0.01
POWER_FLOOR = 0.5       # PREREG §3: verdict requires EN power >= this at the node


def panel():
    return A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))


def canon():
    txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    c = np.asarray(gp.runes_to_indices(txt), dtype=np.int64)
    assert len(c) == 13136, len(c)
    return c


def grid(x):
    """The FIXED 116-map reading grid (PREREG §3): {fwd, rev} x affine a in {1,28}, s in 0..28.
    x: (L,) rune indices -> (116, L) decode block + meta list."""
    rows, meta = [], []
    for dname, v in (("fwd", np.asarray(x, dtype=np.int64)),
                     ("rev", np.asarray(x, dtype=np.int64)[::-1])):
        for a in (1, N - 1):
            for s in range(N):
                rows.append((a * v + s) % N)
                meta.append(dict(dir=dname, a=int(a), s=int(s)))
    return np.stack(rows), meta


def grid_pmax(x, pan):
    """All 116 pmax values for one stream, plus argmax meta."""
    X, meta = grid(x)
    r = A.adjudicate_batch(X, pan=pan)
    return r["pmax"], r, X, meta


def pot_fit(vals):
    """bars_v3's model refit: exponential POT above the empirical 90th percentile.
    Returns (u, p_u, beta, n_exceed)."""
    v = np.asarray(vals, dtype=np.float64)
    u = float(np.quantile(v, 0.90))
    exc = v[v > u] - u
    return u, float((v > u).mean()), float(exc.mean()), int(len(exc))


def pot_bar(u, p_u, beta, Nreal=N_BUDGET, alpha=ALPHA):
    import math
    mu = u + beta * math.log(p_u)
    return mu + beta * math.log(Nreal / -math.log1p(-alpha))


def english_windows(L, n_win, rng, path=None, latin=False):
    """Held-out plant windows: second half of the corpus file (the panel build's reserved
    plant half), word-encoded via gematria, contiguous L-rune windows."""
    if path is None:
        path = (os.path.join(LP, "analysis", "latin", "latin_28233.txt") if latin
                else os.path.join(LP, "data", "keys", "self_reliance.txt"))
    raw = open(path, encoding="utf-8", errors="ignore").read()
    raw = raw[len(raw) // 2:]                     # held-out half
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
    starts = rng.integers(0, len(s) - L, size=n_win)
    return np.stack([s[a:a + L] for a in starts])
