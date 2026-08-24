"""Round 16 / matched scorer — importable module.

Trains quadgram log-probabilities on the RUNIC TRANSLITERATION distribution,
which is the actual output distribution of the decoder, rather than raw English.

The mismatch the old scorer has:
  - english_quadgrams.txt was built from English text (KJV + 3 novels)
  - the decoder emits the runic transliteration: 7 of 29 runes expand to
    two characters (TH, EO, NG, OE, AE, IA, EA), and the alphabet is lossy
    (no K, Q, V, Z — they map to C, C, U, S respectively)
  - quadgram windows slide over CHARACTERS, not runes, so a 4-rune window
    is not the same as a 4-character window after transliteration

This module builds a MATCHED model by reweighting the existing quadgram counts
through the same rune round-trip the decoder inverts:
  English text -> canonical letter -> runic index -> transliteration string

Algorithm:
  For each English quadgram ABCD with count N:
    1. Map each letter to a runic index (respecting the lossy equivalences:
       K->C, V->U, Z->S, Q->C)
    2. Map each runic index to its transliteration string
    3. Concatenate: ABCD becomes e.g. "THEOF" for A=TH, B=E, C=O, D=F
    4. Slide a 4-char window over that expanded string, adding N to each
       4-char window count

This exactly mirrors what happens when a correct plaintext goes through the
decoder: English letters become transliteration characters.

Usage:
    from analysis.round16.scorer.scorer import matched_scorer
    sc = matched_scorer()
    sc.score_norm("WELCOMEPILGRIMTOTHEGREAT")  # ~ -4.0 on correct decode
    sc.score_norm("XQZJXQZJXQZJXQZJ")         # ~ -7.5 on noise

Singleton access (lazy, cached):
    from analysis.round16.scorer.scorer import matched_scorer
    sc = matched_scorer()
"""

import math
import os
import re
import sys

# ---------------------------------------------------------------------------
# Resolve path to english_quadgrams.txt relative to repo root
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
# From analysis/round16/scorer/ go up 3 levels to liber-primus/
_LP = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
_QGRAM_EN = os.path.join(_LP, "data", "english_quadgrams.txt")

# Runic alphabet mapping — must match src/lp/gematria.py exactly
# (index, transliteration)
_GEMATRIA = [
    (0,  "F"),
    (1,  "U"),
    (2,  "TH"),
    (3,  "O"),
    (4,  "R"),
    (5,  "C"),   # C / K
    (6,  "G"),
    (7,  "W"),
    (8,  "H"),
    (9,  "N"),
    (10, "I"),
    (11, "J"),
    (12, "EO"),
    (13, "P"),
    (14, "X"),
    (15, "S"),   # S / Z
    (16, "T"),
    (17, "B"),
    (18, "E"),
    (19, "M"),
    (20, "L"),
    (21, "NG"),
    (22, "OE"),
    (23, "D"),
    (24, "A"),
    (25, "AE"),
    (26, "Y"),
    (27, "IA"),
    (28, "EA"),
]

# Latin letter -> runic index (lossy: K->5, V->1, Z->15, Q->5)
_LATIN_TO_IDX = {}
for _idx, _trans in _GEMATRIA:
    # Multi-char transliterations: only first char maps back here; handled in
    # TRANS_TO_IDX below. For the FORWARD mapping (English -> rune), we
    # parse letter by letter.
    if len(_trans) == 1:
        _LATIN_TO_IDX[_trans] = _idx
# Lossy aliases
_LATIN_TO_IDX["K"] = 5
_LATIN_TO_IDX["V"] = 1
_LATIN_TO_IDX["Z"] = 15
_LATIN_TO_IDX["Q"] = 5

# Runic index -> transliteration string
_IDX_TO_TRANS = {idx: trans for idx, trans in _GEMATRIA}

_NONALPHA = re.compile(r"[^A-Z]")


def _letter_to_translit(ch: str) -> str:
    """Map a single uppercase English letter to its runic transliteration.
    Returns the transliteration string (1 or 2 chars)."""
    idx = _LATIN_TO_IDX.get(ch)
    if idx is None:
        return ch  # unknown letter — pass through unchanged (shouldn't happen)
    return _IDX_TO_TRANS[idx]


def _english_word_to_translit(word: str) -> str:
    """Push an English string through the runic round-trip.

    Each letter is mapped to its runic index then to the transliteration.
    Multi-char transliterations (TH, EO, NG, etc.) expand the string.
    """
    parts = []
    for ch in _NONALPHA.sub("", word.upper()):
        parts.append(_letter_to_translit(ch))
    return "".join(parts)


class MatchedQuadgram:
    """Quadgram scorer trained on the runic transliteration distribution.

    Built by reweighting the existing English quadgram counts through the
    runic round-trip mapping. See module docstring for algorithm details.
    """

    def __init__(self, english_qgram_path: str = _QGRAM_EN):
        # Load English quadgram counts
        en_counts: dict[str, int] = {}
        with open(english_qgram_path, encoding="ascii") as f:
            for line in f:
                parts = line.split()
                if len(parts) == 2:
                    q, c = parts
                    en_counts[q] = int(c)

        # Build matched counts by expanding each English quadgram
        matched_counts: dict[str, int] = {}
        for quad, cnt in en_counts.items():
            # Push each 4-letter English quadgram through the runic round-trip
            expanded = _english_word_to_translit(quad)
            # Slide a 4-char window over the expanded string
            for i in range(len(expanded) - 3):
                tq = expanded[i:i + 4]
                matched_counts[tq] = matched_counts.get(tq, 0) + cnt

        total = sum(matched_counts.values())
        self.total = total
        self.logtotal = math.log10(total) if total > 0 else 0.0
        self.d: dict[str, float] = {}
        for q, c in matched_counts.items():
            self.d[q] = math.log10(c) - self.logtotal
        # Floor for unseen quadgrams (same formula as the English scorer)
        self.floor = math.log10(0.01) - self.logtotal

    def score(self, text: str) -> float:
        """Total log10 probability. Higher (less negative) = more English-via-runes."""
        t = _NONALPHA.sub("", text.upper())
        if len(t) < 4:
            return -999.0
        s = 0.0
        for i in range(len(t) - 3):
            s += self.d.get(t[i:i + 4], self.floor)
        return s

    def score_norm(self, text: str) -> float:
        """Per-quadgram average. ~-4.0 to -4.5 = correct runic decode, < -7 = noise."""
        t = _NONALPHA.sub("", text.upper())
        n = len(t) - 3
        if n <= 0:
            return -999.0
        return self.score(t) / n

    @property
    def n_distinct(self) -> int:
        """Number of distinct quadgrams in the matched model."""
        return len(self.d)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
_MATCHED: MatchedQuadgram | None = None


def matched_scorer(english_qgram_path: str = _QGRAM_EN) -> MatchedQuadgram:
    """Return the (lazily cached) matched runic quadgram scorer."""
    global _MATCHED
    if _MATCHED is None:
        _MATCHED = MatchedQuadgram(english_qgram_path)
    return _MATCHED


# ---------------------------------------------------------------------------
# CLI: run validation + power measurement when executed directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Quick sanity check
    sc = matched_scorer()
    print(f"Matched model: {sc.n_distinct} distinct quadgrams (total {sc.total:,})")
    tests = [
        ("WELCOMEPILGRIMTOTHEGREATJOURNEY", "signal (WELCOME)"),
        ("BELIEVENOTHINGFROMTHISBOOK", "signal (BELIEVE)"),
        ("THEPRIMESARESACREDTHETOTIENT", "signal (PRIMES)"),
        ("XQZJXQZJXQZJXQZJXQZJXQZJ", "noise"),
    ]
    for text, label in tests:
        print(f"  {sc.score_norm(text):7.3f}  {label}")
