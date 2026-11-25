"""Shared helpers for the heavy-lift checkers C7-C10 (CHALLENGES.md, "Heavy lifts").

Seeds, keystreams, English text -> rune sentences, the English reference score, the panel-R36 incumbent,
and power-at-fixed-FPR. Everything is built from code the repo already trusts (benchmark/plant.py,
campaign18_skip/skipdecode.py, src/lp); nothing about the cipher is re-implemented.

Sealing: every checker draws fresh plants from --seed. With no --seed a 64-bit seed comes from os.urandom
and is printed, so any run can be reproduced. Credit is decided on a seed the maintainers choose at review
(sha256 posted first, seed revealed with the verdict), plus held-out text for C8-C10.
"""
import hashlib
import math
import os
import random
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402  (sets sys.path for lp / benchmark / skipdecode)
import skipdecode as sk  # noqa: E402
import plant as PL  # noqa: E402
from lp import gematria as gp  # noqa: E402
from lp import score as _score  # noqa: E402

N = C.N
Q = _score.default()
RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
RUNE_IDX = {r: i for i, r in enumerate(RUNES)}
GP_TOKENS = [gp.IDX_TO_TRANS[i] for i in range(N)]          # F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA
LP2_PAGE = 236                                             # 12,956 / 55 = 235.6
EXACT_SUPP = PL.EXACT_SUPP                                 # filter strength that reproduces LP2's 0.664 % doublets
PANEL_PATH = os.path.join(C.LP, "data", "panels", "panel-r36.npz")
PANEL_SHA = "a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c"
PANEL_REGISTERS = ("EN_MODERN", "EN_KJV", "LP1_REAL", "LATIN", "OE", "DE", "CY", "EN_HALFVOWEL",
                   "EN_NOVOWEL", "GREEK", "HEBREW", "NORSE")

# English dev texts (committed). Held-out text replaces these at review.
DEV_ENGLISH = ("data/keys/self_reliance.txt", "data/keys/armada19/mill_on_liberty.txt",
               "data/keys/armada18/emerson_essays_first_series.txt", "data/keys/armada19/shelley_frankenstein.txt")


# ------------------------------------------------------------------ seeds
def resolve_seed(seed):
    """--seed value, or 64 fresh random bits. Returned so the caller prints it."""
    return int.from_bytes(os.urandom(8), "big") if seed is None else int(seed)


def seed_digest(seed):
    return hashlib.sha256(str(seed).encode()).hexdigest()[:16]


def sha_key(seed_bytes, length):
    """SHA-256 counter-mode keystream mod 29: benchmark/plant.py ks_sha256_ctr (the derived-key gate family)."""
    return PL.ks_sha256_ctr(seed=seed_bytes, length=length)


def rand_key(rng, length):
    return sha_key(rng.getrandbits(128).to_bytes(16, "big"), length)


# ------------------------------------------------------------------ text
def repo_path(p):
    return p if os.path.isabs(p) else os.path.join(C.ROOT, p) if p.startswith("liber-primus") or p.startswith(
        "challenges") else os.path.join(C.LP, p)


def strip_gutenberg(t):
    s, e = t.find("*** START OF"), t.find("*** END OF")
    if s >= 0:
        s = t.find("\n", s) + 1
        t = t[s:e if e > s else None]
    return t


def read_text(path):
    b = open(repo_path(path), "rb").read()
    t = b.decode("utf-8", errors="replace")
    if t.count("�") > 0.01 * max(1, len(t)):
        t = b.decode("latin-1")
    return strip_gutenberg(t)


_FOLD = {"þ": "th", "ð": "th", "æ": "ae", "œ": "oe", "ø": "oe", "ß": "ss"}


def fold_latin(t):
    """Latin-alphabet text -> plain A-Z letters (umlauts/accents stripped, þ/ð -> th, æ -> ae)."""
    t = "".join(_FOLD.get(ch, ch) for ch in t.lower())
    t = unicodedata.normalize("NFD", t)
    return "".join(ch for ch in t if not unicodedata.combining(ch))


def latin_text_to_idx(path):
    """A Latin-alphabet text file as one rune stream (GP greedy, letters only; skipdecode.eng_to_idx)."""
    return sk.eng_to_idx(re.sub(r"[^a-z]", "", fold_latin(read_text(path))))


def english_sentences(paths=DEV_ENGLISH):
    """Sentences as lists of words, each word a list of rune indices (skipdecode.eng_to_idx per word)."""
    out = []
    for p in paths:
        cur = []
        for m in re.finditer(r"[A-Za-z]+(?:'[A-Za-z]+)*|[.!?]", read_text(p)):
            g = m.group()
            if g in ".!?":
                if cur:
                    out.append(cur)
                    cur = []
                continue
            r = sk.eng_to_idx(g.replace("'", ""))
            if r:
                cur.append(r)
        if cur:
            out.append(cur)
    return out


def english_stream(paths=DEV_ENGLISH):
    return [x for s in english_sentences(paths) for w in s for x in w]


def lp2_stream():
    """The 12,956-rune unsolved stream as a plain list (no numpy)."""
    out = []
    for s in C.canon_segments()[:55]:
        out.extend(gp.runes_to_indices(s))
    assert len(out) == 12956
    return out


# ------------------------------------------------------------------ scorers
def english_score(idx):
    """The repo's English reference: per-quadgram log-probability of the transliteration (lp.score)."""
    return Q.score_norm(sk.idx_to_trans(list(idx)))


_PAN = None


def panel_pmax(idx):
    """Incumbent: max z over the 12 registers of panel-R36 (round32/I2 adjudicate.Panel). Needs numpy."""
    global _PAN
    import numpy as np
    if _PAN is None:
        got = hashlib.sha256(open(PANEL_PATH, "rb").read()).hexdigest()
        assert got == PANEL_SHA, "panel-r36.npz sha256 mismatch"
        sys.path.insert(0, os.path.join(C.LP, "analysis", "round32", "I2-multiregister-readjudication"))
        import adjudicate as AD
        _PAN = AD.Panel(PANEL_PATH)
    x = np.asarray(idx, dtype=np.int64)
    mu, sd, _, _ = _PAN.cal(len(x))
    return float(((_PAN.raw(x) - mu) / sd).max())


# ------------------------------------------------------------------ power
def threshold(neg, fpr):
    """Score a positive must EXCEED so that at most `fpr` of `neg` does (same rule as C2)."""
    v = sorted(neg)
    return v[min(len(v) - 1, int((1 - fpr) * len(v)))]


def power(pos, neg, fpr):
    t = threshold(neg, fpr)
    return sum(1 for s in pos if s > t) / len(pos), t


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    a = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - a) / d, 3), round((c + a) / d, 3))


def to_runes(idx):
    return "".join(RUNES[i] for i in idx)


def banner(name, seed, extra=""):
    print(f"{name}   seed={seed} (sha256[:16] {seed_digest(seed)}){'   ' + extra if extra else ''}")
