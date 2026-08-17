"""Lane B6 — language-agnostic and non-English-prose detectors over rune streams.

Symbol space: rune indices 0..28 (Gematria Primus order).

Detectors D1-D4, D7 are invariant under ANY monoalphabetic substitution of the
29 symbols (hence under all 29 shifts, Atbash, and any alphabet reordering) and
under reversal. D5/D6 operate on a specific decode.
"""
import io
import json
import lzma
import os
import re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
LP = os.path.join(REPO, "liber-primus")

N = 29
TRANSLIT = ["F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J", "EO", "P",
            "X", "S", "T", "B", "E", "M", "L", "NG", "OE", "D", "A", "AE", "Y",
            "IA", "EA"]


# ---------------------------------------------------------------- data loading

def load_unsolved():
    """Return (per_page list of np.int8 arrays, concatenated stream)."""
    d = json.load(io.open(os.path.join(LP, "dataset", "liber_primus.json"),
                          encoding="utf-8"))
    pages = []
    for p in d["pages"]:
        if p["page"] > 55:
            continue
        idx = p.get("indices")
        if idx is None:
            continue
        pages.append((p["page"], np.array(idx, dtype=np.int64)))
    stream = np.concatenate([a for _, a in pages])
    return pages, stream


# ------------------------------------------------- D1-D4, D7: language-agnostic

def _windows(x, w, step=1):
    n = len(x)
    if n < w:
        return np.empty((0, w), dtype=x.dtype)
    starts = np.arange(0, n - w + 1, step)
    return x[starts[:, None] + np.arange(w)[None, :]]


def _symbol_cum(x):
    """cum[s, i] = count of symbol s in x[:i]; shape (N, len(x)+1)."""
    n = len(x)
    oh = np.zeros((N, n), dtype=np.int32)
    oh[x, np.arange(n)] = 1
    return np.concatenate([np.zeros((N, 1), dtype=np.int32),
                           np.cumsum(oh, axis=1)], axis=1)


def _window_counts(x, w, step=1):
    """(n_windows, N) symbol counts, via cumulative sums (fast)."""
    n = len(x)
    if n < w:
        return np.zeros((0, N), dtype=np.int32)
    cum = _symbol_cum(x)
    starts = np.arange(0, n - w + 1, step)
    return (cum[:, starts + w] - cum[:, starts]).T


def d1_distinct(x, w, step=1):
    """Alphabet restriction: LOW distinct count = restricted alphabet.
    Returned as (E_random - k) so that HIGH = more structured."""
    C = _window_counts(x, w, step)
    if len(C) == 0:
        return np.array([])
    k = (C > 0).sum(axis=1)
    exp = N * (1.0 - ((N - 1.0) / N) ** w)
    return exp - k


def d2_ioc(x, w, step=1):
    """Windowed index of coincidence x 29. HIGH = structured."""
    C = _window_counts(x, w, step).astype(np.int64)
    if len(C) == 0:
        return np.array([])
    num = (C * (C - 1)).sum(axis=1).astype(float)
    return num / (w * (w - 1)) * N


def d3_repeat(x, w, step=1):
    """Repeated-bigram pair count inside window (sliding, O(n))."""
    n = len(x)
    if n < w:
        return np.array([])
    big = (x[:-1] * N + x[1:]).tolist()
    bw = w - 1
    nb = len(big)
    cnt = {}
    pairs = 0
    out = []
    for i in range(nb):
        c = cnt.get(big[i], 0)
        pairs += c
        cnt[big[i]] = c + 1
        if i >= bw:
            j = i - bw
            cnt[big[j]] -= 1
            pairs -= cnt[big[j]]
        if i >= bw - 1:
            out.append(pairs)
    out = np.array(out, dtype=float)
    return out[::step] if step > 1 else out


def d4_compress(x, w, step=1):
    """lzma-compressed size of the window, negated (HIGH = compressible)."""
    n = len(x)
    if n < w:
        return np.array([])
    starts = np.arange(0, n - w + 1, step)
    out = np.zeros(len(starts))
    xb = bytes(bytearray(x.tolist()))
    for j, s in enumerate(starts):
        out[j] = -len(lzma.compress(xb[s:s + w], preset=6))
    return out


def d7_subalpha(x, w, step=1, k=16):
    """Base-N shape: mass of the window inside its own top-k symbols."""
    C = _window_counts(x, w, step)
    if len(C) == 0:
        return np.array([])
    C = np.sort(C, axis=1)
    return C[:, -k:].sum(axis=1).astype(float)


AGNOSTIC = {
    "D1_distinct": d1_distinct,
    "D2_ioc": d2_ioc,
    "D3_repeat": d3_repeat,
    "D4_compress": d4_compress,
    "D7_sub16": lambda x, w, step=1: d7_subalpha(x, w, step, k=16),
    "D7_sub10": lambda x, w, step=1: d7_subalpha(x, w, step, k=10),
}


# ------------------------------------------------------- D5: rune-space LMs

# Reverse transliteration: text -> rune indices, greedy longest match.
_DIGRAPHS = sorted([(t, i) for i, t in enumerate(TRANSLIT)],
                   key=lambda p: -len(p[0]))

# extra orthographic folds per language, applied before matching
_FOLD_COMMON = {
    "K": "C", "Q": "C", "V": "U", "Z": "S", "Ç": "C",
}
_FOLD_DE = {"Ä": "AE", "Ö": "OE", "Ü": "U", "ß": "S"}
_FOLD_OE = {"Þ": "TH", "Ð": "TH", "Æ": "AE", "Ȝ": "G"}
_FOLD_CY = {"Ŵ": "W", "Ŷ": "Y", "Â": "A", "Ê": "E", "Î": "I", "Ô": "O", "Û": "U"}
_FOLD_LA = {"Æ": "AE", "Œ": "OE", "J": "I", "Ā": "A", "Ē": "E", "Ī": "I",
            "Ō": "O", "Ū": "U"}


def text_to_runes(text, lang="EN"):
    t = text.upper()
    folds = dict(_FOLD_COMMON)
    if lang == "DE":
        folds.update(_FOLD_DE)
    elif lang == "OE":
        folds.update(_FOLD_OE)
    elif lang == "CY":
        folds.update(_FOLD_CY)
    elif lang == "LA":
        folds.update(_FOLD_LA)
    # language-specific folds win over the common J->? etc.
    for a, b in folds.items():
        t = t.replace(a, b)
    t = re.sub(r"[^A-Z]", " ", t)
    out = []
    i = 0
    L = len(t)
    while i < L:
        c = t[i]
        if c == " ":
            i += 1
            continue
        hit = None
        for tr, idx in _DIGRAPHS:
            if t.startswith(tr, i):
                hit = (tr, idx)
                break
        if hit:
            out.append(hit[1])
            i += len(hit[0])
        else:
            i += 1
    return np.array(out, dtype=np.int64)


def build_trigram(runes, alpha=0.5):
    """log10 conditional trigram model over rune indices."""
    cnt = np.full((N, N, N), alpha, dtype=np.float64)
    if len(runes) >= 3:
        a, b, c = runes[:-2], runes[1:-1], runes[2:]
        np.add.at(cnt, (a, b, c), 1.0)
    lm = np.log10(cnt / cnt.sum(axis=2, keepdims=True))
    return lm


def score_trigram(lm, x):
    if len(x) < 3:
        return -99.0
    return float(lm[x[:-2], x[1:-1], x[2:]].mean())


def score_trigram_windows(lm, x, w, step=1):
    """Per-window mean log10 trigram score."""
    n = len(x)
    if n < w:
        return np.array([])
    v = lm[x[:-2], x[1:-1], x[2:]]          # len n-2
    cs = np.concatenate([[0.0], np.cumsum(v)])
    starts = np.arange(0, n - w + 1, step)
    m = w - 2
    return (cs[starts + m] - cs[starts]) / m


# ---------------------------------------------------- D6: token / crib detector

TOKEN_CLASSES = {
    "net": ["ONION", "HTTP", "WWW", "TOR", "DOTCOM", "COM", "ORG", "NET",
            "URL", "LINK", "ADDRESS", "SERVICE", "HIDDEN"],
    "crypto": ["PGP", "BEGIN", "PUBLIC", "PRIVATE", "KEY", "SIGNATURE",
               "BLOCK", "MESSAGE", "HASH", "PRIME", "CIPHER"],
    "digits": ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN",
               "EIGHT", "NINE", "TEN"],
    "geo": ["NORTH", "SOUTH", "EAST", "WEST", "DEGREE", "DEGREES", "MINUTE",
            "SECOND", "LATITUDE", "LONGITUDE", "COORDINATE"],
}


def runes_to_translit(x):
    return "".join(TRANSLIT[i] for i in x)


def d6_tokens(x):
    s = runes_to_translit(x)
    out = {}
    for cls, toks in TOKEN_CLASSES.items():
        c = 0
        for t in toks:
            c += s.count(t)
        out[cls] = c
    return out
