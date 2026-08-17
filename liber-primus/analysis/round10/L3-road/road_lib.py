"""L3-ROAD shared library: data loading, encoding, scoring.

Round 10, lane L3 ("their meaning is the road").
Writes nothing outside analysis/round10/L3-road/.
"""
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))   # -> liber-primus/
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp.gematria import GEMATRIA, PRIMES, IDX_TO_TRANS, RUNE_TO_IDX  # noqa: E402

N = 29
PRIME = np.array(PRIMES, dtype=np.int64)

# --------------------------------------------------------------- 4-gram model
_NG = None


def ngram():
    """Seed-sweep rune 4-gram log-prob table (29^4 float32).

    Scale note: this is the STREAM-scale scorer used by the seed sweep and by
    Round 9's DIRECTION track. English-class is about -11 to -12; random is
    about -16. It is NOT the page-scale (-4.2/-7.3) scorer.
    """
    global _NG
    if _NG is None:
        _NG = np.fromfile(os.path.join(ROOT, "analysis", "seed_sweep", "ngram.bin"),
                          np.float32)
        assert _NG.size == N ** 4
    return _NG


def score(seq):
    """Mean 4-gram log-prob of a rune-index sequence. -99 if too short."""
    a = np.asarray(seq, np.int64)
    if a.size < 24:
        return -99.0
    ng = ngram()
    idx = ((a[:-3] * N + a[1:-2]) * N + a[2:-1]) * N + a[3:]
    return float(ng[idx].mean())


def show(seq, k=90):
    return "".join(IDX_TO_TRANS[int(v) % N] for v in np.asarray(seq)[:k])


# ------------------------------------------------------------- English -> runes
_MULTI = [("ING", 21), ("EA", 28), ("IA", 27), ("IO", 27), ("AE", 25),
          ("OE", 22), ("NG", 21), ("EO", 12), ("TH", 2)]
_SINGLE = {t: i for (i, r, t, p) in GEMATRIA if len(t) == 1}
_SINGLE.update({"V": 1, "K": 5, "Z": 15, "Q": 5})


def eng_to_runes(s):
    """Greedy longest-match English -> rune indices (repo-standard encoder;
    verified by Round 9 against PARABLE's 20 word lengths)."""
    s = s.upper()
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if not ("A" <= c <= "Z"):
            i += 1
            continue
        for m, idx in _MULTI:
            if s.startswith(m, i):
                out.append(idx)
                i += len(m)
                break
        else:
            j = _SINGLE.get(c)
            if j is not None:
                out.append(j)
            i += 1
    return out


def eng_words_to_runes(s):
    """Same encoder, but returns a list of per-WORD rune-index lists."""
    return [w for w in (eng_to_runes(t) for t in re.split(r"[^A-Za-z]+", s)) if w]


# --------------------------------------------------------------------- LP2 data
_RUNE_RE = re.compile(r"[ᚠ-᛿]")


def lp2_words():
    """Unsolved LP2 segments 0-54 as a list of per-word rune-index lists.

    PARSE RULE (mandated by research/DEAD_ENDS.md:412): '/' is a LINE WRAP, not
    a word separator - 458 of 604 line breaks fall mid-word. Words are split on
    '-' and '.' (and the paragraph/section marks '&' '$'), never on '/'.
    Validated: 2928 words / 12956 runes / mean 4.4249 - the repo's recorded
    corrected-parse numbers.
    """
    raw = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"),
               encoding="utf-8").read()
    segs = [s for s in raw.split("%") if _RUNE_RE.search(s)][:-2]  # drop AN END, PARABLE
    pages = []
    for s in segs:
        s = s.replace("/", "").replace("\n", "")
        ws = [[RUNE_TO_IDX[c] for c in w] for w in re.split(r"[^ᚠ-᛿]+", s) if w]
        pages.append(ws)
    return pages


def lp2_solved():
    """(an_end_words, parable_words) - the two solved LP2 segments, same parse."""
    raw = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"),
               encoding="utf-8").read()
    segs = [s for s in raw.split("%") if _RUNE_RE.search(s)][-2:]
    out = []
    for s in segs:
        s = s.replace("/", "").replace("\n", "")
        out.append([[RUNE_TO_IDX[c] for c in w]
                    for w in re.split(r"[^ᚠ-᛿]+", s) if w])
    return out[0], out[1]


def wsum(words):
    """Gematria-Primus prime sum of each word."""
    return np.array([int(PRIME[np.asarray(w)].sum()) for w in words], dtype=np.int64)


# ---------------------------------------------------------------------- primes
def sieve(n):
    s = np.ones(n + 1, dtype=bool)
    s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return s


_S = sieve(4_000_000)


def is_prime(x):
    x = np.asarray(x)
    out = np.zeros(x.shape, dtype=bool)
    ok = (x >= 0) & (x < _S.size)
    out[ok] = _S[x[ok]]
    return out


def is_emirp(x):
    """Prime whose decimal reversal is a different prime (Cicada's own marker
    in the published per-sentence gematria sums of the solved pages)."""
    x = np.asarray(x)
    rev = np.array([int(str(int(v))[::-1]) for v in x])
    return is_prime(x) & is_prime(rev) & (rev != x)
