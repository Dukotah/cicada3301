"""R44 / W2-C6 shared glue: short-PAGE instrument (PREREG §3).

ONE code path shared by the null build, the plants, and the real reads (R42 X1 rule).
Extends W2-A1's glue with: the page table, the unsolved-prefix WIN-U family, the EN rune
unigram (training half), and the FIXED classical attack (exhaust k<=3 + unigram beam k=4..8).
"""
import math
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

N = 29
SEED = 3301
ALPHA = 0.01
L_NODES = (66, 76, 85, 92, 95)
N_DIRECT = 600            # PREREG §3: direct-read bar budget
N_CL = 160000             # PREREG §3: classical bar budget (actual 157,532)
POWER_FLOOR = 0.5
UNSOLVED_END = 12956      # canon pages 0..54

# PREREG §3/§5: stored per-page bests + lane Ns (copied verbatim pre-execution)
LANES = {
    "P2-p15-grid":      {"N_page": 12184,   "N_lane": 670120,
                         "best": {49: 4.794, 50: 4.471, 54: 4.389}, "lane_bar": 12.956},
    "P4-blob-pads":     {"N_page": 92160,   "N_lane": 5068800,
                         "best": {49: 4.964, 50: 4.783, 54: 5.748}, "lane_bar": 14.034},
    "R1-key-resets":    {"N_page": 2000000, "N_lane": 2000000,
                         "best": {49: 4.890, 50: 4.678, 54: 4.791}, "lane_bar": 15.674},
    "W2-A4-chained":    {"N_page": 50000,   "N_lane": 50000,
                         "best": {49: 4.433, 50: 3.585, 54: 3.301}, "lane_bar": 13.708},
}

# classical attack shape (PREREG §3): full exhaust k<=3; beam B per k for k>=4
BEAM_B = {4: 4, 5: 4, 6: 4, 7: 3, 8: 3}
KS = (1, 2, 3, 4, 5, 6, 7, 8)


def panel():
    return A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))


def canon():
    txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    c = np.asarray(gp.runes_to_indices(txt), dtype=np.int64)
    assert len(c) == 13136, len(c)
    return c


def pages():
    """Per-page (start, length) from the canon page breaks ('%')."""
    txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    lens = [len(gp.runes_to_indices(p)) for p in txt.split("%")]
    starts = np.concatenate([[0], np.cumsum(lens)[:-1]]).astype(int)
    tab = {i: (int(starts[i]), int(lens[i])) for i in range(len(lens))}
    assert tab[49] == (12048, 66) and tab[54] == (12880, 76) and tab[50] == (12114, 92)
    assert tab[55][1] == 85 and tab[56][1] == 95 and tab[55][0] == UNSOLVED_END
    return tab


def grid(x):
    """The FIXED 116-map grid: {fwd, rev} x affine a in {1,28}, s in 0..28 (W2-A1 path)."""
    rows, meta = [], []
    for dname, v in (("fwd", np.asarray(x, dtype=np.int64)),
                     ("rev", np.asarray(x, dtype=np.int64)[::-1])):
        for a in (1, N - 1):
            for s in range(N):
                rows.append((a * v + s) % N)
                meta.append(dict(dir=dname, a=int(a), s=int(s)))
    return np.stack(rows), meta


def grid_pmax(x, pan):
    X, meta = grid(x)
    r = A.adjudicate_batch(X, pan=pan)
    return r["pmax"], r, X, meta


def pot_fit(vals):
    """bars_v3 refit (W2-A1 code path): exponential POT above the empirical 90th pct."""
    v = np.asarray(vals, dtype=np.float64)
    u = float(np.quantile(v, 0.90))
    exc = v[v > u] - u
    return u, float((v > u).mean()), float(exc.mean()), int(len(exc))


def pot_bar(u, p_u, beta, Nreal, alpha=ALPHA):
    mu = u + beta * math.log(p_u)
    return mu + beta * math.log(Nreal / -math.log1p(-alpha))


def corpus_stream(latin=False, held_out=True):
    """EN/LA rune-index stream. held_out=True -> second half (plants, as W2-A1);
    held_out=False -> FIRST half (unigram training; PREREG §3)."""
    path = (os.path.join(LP, "analysis", "latin", "latin_28233.txt") if latin
            else os.path.join(LP, "data", "keys", "self_reliance.txt"))
    raw = open(path, encoding="utf-8", errors="ignore").read()
    raw = raw[len(raw) // 2:] if held_out else raw[:len(raw) // 2]
    out = []
    for w in raw.split():
        w = "".join(ch for ch in w.upper() if ch.isalpha())
        if not w:
            continue
        try:
            out.extend(gp.keyword_to_indices(w))
        except Exception:
            pass
    return np.asarray(out, dtype=np.int64)


def windows(stream, L, n_win, rng):
    starts = rng.integers(0, len(stream) - L, size=n_win)
    return np.stack([stream[a:a + L] for a in starts])


def en_unigram_logq():
    """EN rune unigram log-probs from the TRAINING half, add-0.5 smoothing (PREREG §3)."""
    s = corpus_stream(latin=False, held_out=False)
    cnt = np.bincount(s, minlength=N).astype(np.float64) + 0.5
    return np.log(cnt / cnt.sum())


# ---------------------------------------------------------------- classical attack
def column_topB(v, k, B, logq):
    """v: (L,) already direction-applied ciphertext AFTER multiplying by a.
    Returns (k, B) array: top-B shifts per column by column unigram log-likelihood."""
    tops = np.empty((k, B), dtype=np.int64)
    for j in range(k):
        col = v[j::k]
        # score[s] = sum_i logq[(col_i + s) % 29]
        sc = np.array([logq[(col + s) % N].sum() for s in range(N)])
        tops[j] = np.argsort(sc)[::-1][:B]
    return tops


def attack_candidates(c, logq):
    """The FULL fixed attack on one 66-rune ciphertext. Yields (config_meta, decode_block)
    where decode_block is (n_cand, L). Identical path for null ATTSEL, plants, real read."""
    c = np.asarray(c, dtype=np.int64)
    for dname, w in (("fwd", c), ("rev", c[::-1])):
        for a in (1, N - 1):
            v = (a * w) % N
            L = len(v)
            pos = np.arange(L)
            for k in KS:
                if k <= 3:
                    # full exhaust of s in Z29^k
                    gridk = np.indices((N,) * k).reshape(k, -1).T  # (29^k, k)
                else:
                    B = BEAM_B[k]
                    tops = column_topB(v, k, B, logq)
                    mesh = np.meshgrid(*[tops[j] for j in range(k)], indexing="ij")
                    gridk = np.stack([m.ravel() for m in mesh], axis=1)  # (B^k, k)
                svec = gridk[:, pos % k]                     # (n_cand, L)
                dec = (v[None, :] + svec) % N
                yield dict(dir=dname, a=int(a), k=int(k), n=len(dec), keys=gridk), dec


def attack_total():
    return 4 * (29 + 29**2 + 29**3 + sum(BEAM_B[k] ** k for k in range(4, 9)))
