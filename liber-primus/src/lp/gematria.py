"""Gematria Primus — the Cicada 3301 Liber Primus runic alphabet.

29 runes (Anglo-Saxon futhorc subset). Each rune maps to:
  - an index 0..28 (its position; this is the value used for Vigenere shifts)
  - a Latin transliteration (some are multi-letter: TH, EO, NG, OE, AE, IA, EA)
  - a prime number (2,3,5,... the 29th prime 109) — "the primes are sacred"

This table is the single source of truth for the whole rig. Every cipher
operates on indices 0..28; transliteration is only for human-readable output.

NOTE on direction/keys: nothing here assumes a cipher direction. The cipher
modules implement add/subtract both ways; the validation gate (tests/) decides
which is correct by reproducing known solved pages. Do not hard-code lore here.
"""

# (index, rune, transliteration, prime)
GEMATRIA = [
    (0,  "ᚠ", "F",   2),
    (1,  "ᚢ", "U",   3),    # U / V
    (2,  "ᚦ", "TH",  5),
    (3,  "ᚩ", "O",   7),
    (4,  "ᚱ", "R",   11),
    (5,  "ᚳ", "C",   13),   # C / K
    (6,  "ᚷ", "G",   17),
    (7,  "ᚹ", "W",   19),
    (8,  "ᚻ", "H",   23),
    (9,  "ᚾ", "N",   29),
    (10, "ᛁ", "I",   31),
    (11, "ᛄ", "J",   37),
    (12, "ᛇ", "EO",  41),
    (13, "ᛈ", "P",   43),
    (14, "ᛉ", "X",   47),
    (15, "ᛋ", "S",   53),   # S / Z
    (16, "ᛏ", "T",   59),
    (17, "ᛒ", "B",   61),
    (18, "ᛖ", "E",   67),
    (19, "ᛗ", "M",   71),
    (20, "ᛚ", "L",   73),
    (21, "ᛝ", "NG",  79),   # NG / ING
    (22, "ᛟ", "OE",  83),
    (23, "ᛞ", "D",   89),
    (24, "ᚪ", "A",   97),
    (25, "ᚫ", "AE",  101),
    (26, "ᚣ", "Y",   103),
    (27, "ᛡ", "IA",  107),  # IA / IO
    (28, "ᛠ", "EA",  109),
]

N = len(GEMATRIA)  # 29

RUNES        = [r for (_, r, _, _) in GEMATRIA]
TRANSLIT     = [t for (_, _, t, _) in GEMATRIA]
PRIMES       = [p for (_, _, _, p) in GEMATRIA]

RUNE_TO_IDX  = {r: i for (i, r, _, _) in GEMATRIA}
IDX_TO_RUNE  = {i: r for (i, r, _, _) in GEMATRIA}
IDX_TO_TRANS = {i: t for (i, _, t, _) in GEMATRIA}
RUNE_TO_TRANS = {r: t for (_, r, t, _) in GEMATRIA}
RUNE_TO_PRIME = {r: p for (_, r, _, p) in GEMATRIA}
PRIME_TO_IDX  = {p: i for (i, _, _, p) in GEMATRIA}

# Transliteration -> index, longest-first so multi-letter runes win when parsing
# Latin keywords into rune indices (e.g. "DIVINITY", "CIRCUMFERENCE").
_TRANS_SORTED = sorted(((t, i) for i, _, t, _ in GEMATRIA), key=lambda x: -len(x[0]))

INTERRUPTER = "ᚠ"  # the F rune; on some pages acts as a null/interrupter


def is_rune(ch: str) -> bool:
    return ch in RUNE_TO_IDX


def runes_to_indices(text: str):
    """Extract rune indices from arbitrary text, ignoring non-runes."""
    return [RUNE_TO_IDX[c] for c in text if c in RUNE_TO_IDX]


def indices_to_runes(idxs) -> str:
    return "".join(IDX_TO_RUNE[i % N] for i in idxs)


def indices_to_translit(idxs, sep: str = "") -> str:
    return sep.join(IDX_TO_TRANS[i % N] for i in idxs)


def runes_to_translit(text: str, sep: str = "") -> str:
    """Human-readable transliteration; non-runes pass through unchanged
    (so word separators '•' and line breaks survive if you want them)."""
    out = []
    for c in text:
        out.append(RUNE_TO_TRANS[c] if c in RUNE_TO_TRANS else c)
    return sep.join(out) if sep else "".join(out)


def keyword_to_indices(word: str):
    """Parse a Latin keyword (e.g. 'DIVINITY') into Gematria Primus indices,
    matching multi-letter runes greedily (TH, EO, NG, OE, AE, IA, EA)."""
    s = word.upper().replace(" ", "")
    out, i = [], 0
    while i < len(s):
        for t, idx in _TRANS_SORTED:
            if s.startswith(t, i):
                out.append(idx)
                i += len(t)
                break
        else:
            # Unknown letter — try common Latin aliases for shared runes
            alias = {"V": 1, "K": 5, "Z": 15, "Q": 5}.get(s[i])
            if alias is None:
                raise ValueError(f"cannot map letter {s[i]!r} in {word!r}")
            out.append(alias)
            i += 1
    return out


if __name__ == "__main__":
    assert N == 29
    assert PRIMES[0] == 2 and PRIMES[-1] == 109
    print("Gematria Primus OK:", N, "runes")
    print("DIVINITY ->", keyword_to_indices("DIVINITY"))
    print("indices  ->", indices_to_translit(keyword_to_indices("DIVINITY"), "-"))
