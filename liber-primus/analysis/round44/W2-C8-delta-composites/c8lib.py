"""R44 / W2-C8 shared glue — delta-stream composite decoders (k>=7) + panel/bars plumbing.

Everything pre-registered in PREREG.md (hash-stamped in run.log before first execution).
Pure python3 + numpy, no network.  Construction space: PREREG section 2, frozen.
"""
import heapq
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (os.path.join(LP, "src"), os.path.join(LP, "analysis"),
          os.path.join(LP, "analysis", "round11"),
          os.path.join(LP, "analysis", "round19", "I2"),
          os.path.join(LP, "analysis", "round34", "I1-v3-null")):
    if p not in sys.path:
        sys.path.insert(0, p)

import adjudicate as A                      # noqa: E402
import lib_numchannel as nc                 # noqa: E402
from lp import gematria as gp               # noqa: E402

N = 29
KS = tuple(range(7, 14))                                    # k = 7..13 (hinted constants)
ORIENTS = ("fwd", "rev")
COMPOSITE_CELLS = ((1, 1), (1, 28), (28, 1), (28, 28), (0, 1), (0, 28))   # negation-closed
WINDOW_FS = ("prod", "max", "min")
SIGNS = (-1, 1)
SEEDS = tuple(range(N))                                     # eq0..eq28 all-equal probe
N_BAR = 1_500_000
BARS = {120: 15.5204, 240: 20.8883, 400: 21.9469, 729: 25.1583}   # bars_v3(1.5e6, L, "free")
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))

# ct-affine grid: a in 0..28, b in 1..28 (PREREG section 2; negation-closed, sign -1 WLOG)
AFF_A = np.repeat(np.arange(N), N - 1)                      # (812,)
AFF_B = np.tile(np.arange(1, N), N)                         # (812,)
N_AFF = AFF_A.size                                          # 812


def lbar(n):
    """Largest bar node <= n, clamped to 120 below (PREREG section 4)."""
    for node in (729, 400, 240, 120):
        if n >= node:
            return node
    return 120


def bar_for(n):
    return BARS[lbar(n)]


# ------------------------------------------------------------------ decoders (vectorised)
def decode_ct_affine(C, k):
    """All 812 (a,b) ct-affine decodes of C at lag pair (1,k).  Returns (812, L-k) scored
    region [k:].  Seedless: key for i>=k depends only on ciphertext (PREREG section 2)."""
    C = np.asarray(C, dtype=np.int64)
    s1 = C[k - 1:-1]                                        # C[i-1] for i=k..L-1
    sk = C[:len(C) - k]                                     # C[i-k]
    K = (AFF_A[:, None] * s1[None, :] + AFF_B[:, None] * sk[None, :]) % N
    return (C[None, k:] - K) % N


def _win_f(W, f):
    """f over (B, k) windows -> (B,) key values."""
    if f == "prod":
        acc = np.ones(W.shape[0], dtype=np.int64)
        for j in range(W.shape[1]):
            acc = acc * W[:, j] % N
        return acc
    return (W.max(axis=1) if f == "max" else W.min(axis=1)) % N


def decode_ct_window(C, k):
    """The 6 ct-window decodes (3 f x 2 sign) of C.  Returns (6, L-k) + labels."""
    C = np.asarray(C, dtype=np.int64)
    W = np.lib.stride_tricks.sliding_window_view(C, k)[:len(C) - k]   # window for i = j+k
    rows, labels = [], []
    for f in WINDOW_FS:
        K = _win_f(W, f)
        for sign in SIGNS:
            rows.append((C[k:] + sign * K) % N)
            labels.append((f, sign))
    return np.stack(rows), labels


def decode_ptmix(C, k):
    """ALL pt/mix rows of one stream at one k in ONE sequential pass, vectorised across
    configs.  Width = 2 src x (6 affine cells + 3 f x 2 sign) x 29 seeds = 696.

    Returns (P[:, k:], labels) with labels[(w)] = (family, src, cell_or_fsign, seed).
    Seed convention (R12-C1): K_i = seed for i < k; score region [k:]."""
    C = np.asarray(C, dtype=np.int64)
    L = len(C)
    labels = []
    for src in ("pt", "mix"):
        for a, b in COMPOSITE_CELLS:
            for sv in SEEDS:
                labels.append(("aff", src, (a, b), sv))
        for f in WINDOW_FS:
            for sign in SIGNS:
                for sv in SEEDS:
                    labels.append(("win", src, (f, sign), sv))
    Wd = len(labels)                                        # 696
    half = Wd // 2                                          # pt rows first, then mix
    aff_n = len(COMPOSITE_CELLS) * N                        # 174 affine rows per src
    aA = np.array([lab[2][0] for lab in labels[:aff_n]])    # per-src affine a (repeats)
    aB = np.array([lab[2][1] for lab in labels[:aff_n]])
    sgn = np.array([lab[2][1] for lab in labels[aff_n:half]])      # window signs per src
    fs = [lab[2][0] for lab in labels[aff_n:half]]
    seeds = np.array([lab[3] for lab in labels], dtype=np.int64)

    P = np.empty((Wd, L), dtype=np.int64)
    S = np.empty((Wd, L), dtype=np.int64)                   # the source stream per row
    for i in range(L):
        if i < k:
            K = seeds
        else:
            K = np.empty(Wd, dtype=np.int64)
            for off in (0, half):                           # 0 = pt block, half = mix block
                s1 = S[off:off + half, i - 1]
                skk = S[off:off + half, i - k]
                K[off:off + aff_n] = (aA * s1[:aff_n] + aB * skk[:aff_n]) % N
                Wn = S[off + aff_n:off + half, i - k:i]     # (174, k) window rows
                kv = np.empty(half - aff_n, dtype=np.int64)
                for fi, f in enumerate(WINDOW_FS):          # 58-row f blocks (2 sign x 29)
                    sl = slice(fi * 2 * N, (fi + 1) * 2 * N)
                    kv[sl] = _win_f(Wn[sl], f)
                K[off + aff_n:off + half] = (-sgn * kv) % N  # fold sign into subtraction
        P[:, i] = (C[i] - K) % N
        S[:half, i] = P[:half, i]                           # pt source
        S[half:, i] = (C[i] + P[half:, i]) % N              # mix source
    return P[:, k:], labels


# ------------------------------------------------------------------ enciphering (plants)
def encipher_ct_affine(Pt, k, a, b):
    C = []
    for i, p in enumerate(Pt):
        K = 0 if i < k else (a * C[i - 1] + b * C[i - k]) % N
        C.append((p + K) % N)
    return C


def encipher_ct_window(Pt, k, f, sign):
    C = []
    for i, p in enumerate(Pt):
        K = 0 if i < k else int(_win_f(np.array([C[i - k:i]], dtype=np.int64), f)[0])
        C.append((p - sign * K) % N)
    return C


def encipher_ptmix(Pt, k, fam, src, cell, seed):
    """fam='aff' cell=(a,b): p = c - K  ->  c = p + K.   fam='win' cell=(f,sign):
    p = c + sign*K  ->  c = p - sign*K.   K from the pt/mix history of the TRUE streams."""
    C = []
    for i, p in enumerate(Pt):
        if i < k:
            K = seed
        else:
            hist = (Pt[i - k:i] if src == "pt"
                    else [(C[j] + Pt[j]) % N for j in range(i - k, i)])
            if fam == "aff":
                a, b = cell
                K = (a * hist[-1] + b * hist[0]) % N
            else:
                f, sign = cell
                K = int(_win_f(np.array([hist], dtype=np.int64), f)[0])
        if fam == "aff":
            C.append((p + K) % N)
        else:
            f, sign = cell
            C.append((p - sign * K) % N)
    return C


# ------------------------------------------------------------------ scoring plumbing
def ioc_rows(X):
    """Vectorised decrypt IoC*N per row of (B, n)."""
    B, n = X.shape
    off = (np.arange(B, dtype=np.int64)[:, None] * N + X).ravel()
    c = np.bincount(off, minlength=B * N).reshape(B, N).astype(np.float64)
    return N * (c * (c - 1.0)).sum(axis=1) / (n * (n - 1.0))


def sweep_stream(C, stream_id, sink):
    """Run the FULL per-stream enumeration (PREREG section 2 table: 21,196 rows) on one
    stream and feed every row to `sink(meta, pmax, pmax_ne, pcon, preg, ioc, decode)`.
    This is the single code path both the plants and the real targets go through."""
    C = np.asarray(C, dtype=np.int64)
    for orient in ORIENTS:
        Co = C if orient == "fwd" else C[::-1].copy()
        for k in KS:
            n = len(Co) - k
            if n < 3:
                continue
            Xa = decode_ct_affine(Co, k)
            Xw, wlab = decode_ct_window(Co, k)
            Xp, plab = decode_ptmix(Co, k)
            X = np.concatenate([Xa, Xw, Xp], axis=0)
            meta = ([("ctaff", "ct", (int(a), int(b)), None)
                     for a, b in zip(AFF_A, AFF_B)]
                    + [("ctwin", "ct", lab, None) for lab in wlab]
                    + [(("aff" == lab[0]) and "pmaff" or "pmwin",
                        lab[1], lab[2], lab[3]) for lab in plab])
            r = A.adjudicate_batch(X, pan=PAN)
            ioc = ioc_rows(X)
            sink(stream_id, orient, k, n, meta, r, ioc, X)


def make_topsink(top_n=200, bar_fn=bar_for):
    """Returns (sink, state).  Tracks global top-N by pmax + every bar-crosser, and counts."""
    state = {"heap": [], "crossers": [], "n_rows": 0, "best": None, "uid": 0,
             "n_rows_primary": 0, "n_rows_diag": 0}

    def sink(stream_id, orient, k, n, meta, r, ioc, X):
        pm = r["pmax"]
        bar = bar_fn(n)
        state["n_rows"] += len(meta)
        state["n_rows_primary" if n >= 120 else "n_rows_diag"] += len(meta)
        order = np.argsort(pm)[-5:]            # only the top few per batch can matter
        for j in order:
            row = dict(stream=stream_id, orient=orient, k=k, n=int(n),
                       family=meta[j][0], src=meta[j][1], cell=meta[j][2],
                       seed=meta[j][3], pmax=float(pm[j]), preg=int(r["preg"][j]),
                       pmax_ne=float(r["pmax_ne"][j]), pcon=float(r["pcon"][j]),
                       ioc=float(ioc[j]), bar=bar)
            state["uid"] += 1
            item = (row["pmax"], state["uid"], row, X[j].copy())
            if len(state["heap"]) < top_n:
                heapq.heappush(state["heap"], item)
            elif item[0] > state["heap"][0][0]:
                heapq.heapreplace(state["heap"], item)
            if state["best"] is None or row["pmax"] > state["best"]["pmax"]:
                state["best"] = row
        for j in np.nonzero(pm >= bar)[0]:
            full = A.adjudicate(X[int(j)], pan=PAN)
            if not full["degenerate"] and full["pmax"] >= bar:
                state["crossers"].append(dict(
                    stream=stream_id, orient=orient, k=k, n=int(n),
                    family=meta[j][0], src=meta[j][1], cell=meta[j][2],
                    seed=meta[j][3], bar=bar, row=full,
                    translit=gp.indices_to_translit(X[int(j)][:80].tolist())))
    return sink, state


def top_rows(state):
    out = []
    for pm, _u, row, dec in sorted(state["heap"], key=lambda t: -t[0]):
        rr = dict(row)
        rr["translit60"] = gp.indices_to_translit(dec[:60].tolist())
        out.append(rr)
    return out


# ------------------------------------------------------------------ plant plaintexts
def _encode_text(path, n_runes):
    txt = open(path, encoding="utf-8", errors="ignore").read().upper()
    import re
    out = []
    for w in re.findall(r"[A-Z]+", txt):
        try:
            out += gp.keyword_to_indices(w)
        except (ValueError, KeyError):
            continue
        if len(out) >= n_runes:
            break
    assert len(out) >= n_runes, (path, len(out))
    return out[:n_runes]


def english_plain(n_runes=2000):
    return _encode_text(os.path.join(LP, "data", "kjv.txt"), n_runes)


def latin_plain(n_runes=2000):
    return _encode_text(os.path.join(LP, "analysis", "latin", "latin_28233.txt"), n_runes)
