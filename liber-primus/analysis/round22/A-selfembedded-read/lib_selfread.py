"""Round 22 Lane A — self-embedded read (roadmap X2).

Search space: the already-SOLVED plaintext (5 rig-reproduced pages of
liber-primus/SOLVED-PAGES.json), concatenated in book order. We DO NOT touch the
ciphertext or the number/value channel here (those were Round 11: N1-N5, S1-S2).

Two representations are provided, both defensible:
  (a) LETTER stream  -- the verified transliteration characters a reader actually reads
                        (this is what validate.py reproduces and trusts).
  (b) RUNE-INDEX stream -- the transliteration greedily re-parsed into Gematria rune
                        indices (longest-match-first). Doctrine mechanics R5 asks us to
                        score on rune indices where possible; greedy parse can merge a
                        true rune boundary, so counts undercount slightly (~1.5%), which
                        is recorded as a coverage caveat, not hidden.

Selection functions (the enumerable set, frozen in PREREG.md):
  1. every-k-th element, k in [2,K_MAX], offset o in [0,k-1]
  2. column reads of a width-w fold  (== every-w with offset c -> subsumed by (1))
  3. main-diagonal reads of a width-w fold, w in [2,W_MAX]
  4. reverse of every selection
Acrostic (first/last per line/page/word): the concat transliteration has no reliable
line breaks; page acrostics (5 runes) are too short for the quadgram scorer and are read
by eye. Word-first acrostic is included where SOLVED-PAGES word spacing is reconstructable.

Recognizer: src/lp/score.py Quadgram.score_norm  (~ -2.2 English, < -4 noise).
Null: same selection applied to order-shuffled source, seed 3301 (built in run_sweep.py).
"""
import os, sys, json, math, gzip, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp, score as _score

SOLVED = os.path.join(LP, "SOLVED-PAGES.json")

# frozen sweep bounds (PREREG)
K_MAX = 40          # every-k for k in [2,40]
W_MAX = 60          # fold widths for diagonal reads

_ALPHA = re.compile(r"[^A-Z]")


def load_solved_translit():
    """Return list of (page_label, uppercase_transliteration_string) in book order."""
    d = json.load(open(SOLVED))
    return [(p["page_label"], p["plaintext_transliteration"].upper()) for p in d["pages"]]


def concat_letters():
    """Concatenated LETTER stream (A-Z only) of all solved pages, book order."""
    s = "".join(t for _, t in load_solved_translit())
    return _ALPHA.sub("", s)


def _greedy_translit_to_indices(t):
    """Greedy longest-first parse of a transliteration into rune indices."""
    t = t.upper()
    out = []
    i = 0
    n = len(t)
    while i < n:
        matched = False
        for trans, idx in gp._TRANS_SORTED:
            if trans and t.startswith(trans, i):
                out.append(idx)
                i += len(trans)
                matched = True
                break
        if not matched:
            i += 1
    return out


def concat_rune_indices():
    """Concatenated RUNE-INDEX stream (greedy parse) of all solved pages, book order."""
    out = []
    for _, t in load_solved_translit():
        out += _greedy_translit_to_indices(t)
    return out


# ---------------------------------------------------------------- selection funcs

def sel_every_k(seq, k, offset):
    return seq[offset::k]


def sel_diagonal(seq, w):
    """Fold seq into rows of width w; read the main diagonal (row r, col r)."""
    out = []
    r = 0
    while True:
        pos = r * w + r
        if pos >= len(seq):
            break
        out.append(seq[pos])
        r += 1
    return out


def sel_antidiagonal(seq, w):
    """Fold into rows of width w; read the anti-diagonal (row r, col w-1-r)."""
    out = []
    r = 0
    nrows = (len(seq) + w - 1) // w
    while r < w and r < nrows:
        pos = r * w + (w - 1 - r)
        if pos < len(seq):
            out.append(seq[pos])
        r += 1
    return out


def enumerate_selections(seq, k_max=K_MAX, w_max=W_MAX, include_reverse=True):
    """Yield (descriptor, selected_subsequence) over the frozen function set.

    seq is either a LETTER string or a list of rune indices; selection is
    index-based so it works for both."""
    # 1. every-k with all offsets
    for k in range(2, k_max + 1):
        for o in range(k):
            sub = sel_every_k(seq, k, o)
            if len(sub) >= 4:
                yield (f"everyk_k{k}_o{o}", sub)
    # 3. diagonals / anti-diagonals of width-w folds
    for w in range(2, w_max + 1):
        d = sel_diagonal(seq, w)
        if len(d) >= 4:
            yield (f"diag_w{w}", d)
        a = sel_antidiagonal(seq, w)
        if len(a) >= 4:
            yield (f"antidiag_w{w}", a)
    # 5. reverses (of the whole stream, then every-k over the reversed stream)
    if include_reverse:
        rev = seq[::-1]
        for k in range(2, k_max + 1):
            for o in range(k):
                sub = sel_every_k(rev, k, o)
                if len(sub) >= 4:
                    yield (f"rev_everyk_k{k}_o{o}", sub)


# ---------------------------------------------------------------- scoring / stats

_SCORER = None


def scorer():
    global _SCORER
    if _SCORER is None:
        _SCORER = _score.default()
    return _SCORER


def to_letters(sub):
    """Coerce a selected subsequence (letters OR rune indices) to an A-Z string."""
    if sub and isinstance(sub[0], int):
        return _ALPHA.sub("", gp.indices_to_translit(sub))
    return _ALPHA.sub("", "".join(sub))


def english_score(sub):
    return scorer().score_norm(to_letters(sub))


# language-agnostic secondary stats (doctrine R3)

def ioc_times_n(sub):
    """Index of coincidence * N on the selected symbols (letters or indices)."""
    if not sub:
        return 0.0
    if isinstance(sub[0], int):
        syms = sub
    else:
        syms = list("".join(sub))
    n = len(syms)
    if n < 2:
        return 0.0
    c = Counter(syms)
    num = sum(v * (v - 1) for v in c.values())
    return (num / (n * (n - 1))) * len(set(syms))


def min_distinct_32(sub):
    """Minimum number of distinct symbols over any 32-symbol window."""
    if isinstance(sub[0], int):
        syms = sub
    else:
        syms = list("".join(sub))
    if len(syms) <= 32:
        return len(set(syms))
    m = 999
    for i in range(len(syms) - 32 + 1):
        m = min(m, len(set(syms[i:i + 32])))
    return m


def base32_fraction(sub):
    """Fraction of chars that are valid base32 (A-Z2-7) -- catches a sparse pointer."""
    s = to_letters(sub)
    if not s:
        return 0.0
    b32 = sum(1 for ch in s if ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
    return b32 / len(s)


def gzip_ratio(sub):
    """Compressed/raw length; low = structured/repetitive."""
    s = to_letters(sub).encode()
    if not s:
        return 1.0
    return len(gzip.compress(s, 9)) / max(1, len(s))


def full_stats(sub):
    return {
        "len": len(sub),
        "score_norm": round(english_score(sub), 4),
        "ioc_n": round(ioc_times_n(sub), 4),
        "min_distinct_32": min_distinct_32(sub),
        "base32_frac": round(base32_fraction(sub), 4),
        "gzip_ratio": round(gzip_ratio(sub), 4),
    }
