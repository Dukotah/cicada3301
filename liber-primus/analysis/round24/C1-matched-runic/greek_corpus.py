"""Round 24 / C1 — build a romanized-Greek corpus for the positive control.

No clean Greek plaintext file exists in the repo; the Greek that IS here sits as polytonic
fragments inside mostly-English books. This module extracts every run of >=2 Greek letters from
those files and romanizes it with a standard scholarly transliteration, producing a Greek-language
(Latin-script) stream that then goes through detectors.text_to_runes exactly like Latin.

The point is a LANGUAGE control (Greek phonotactics under a Latin-script rendering), not a claim
about how Cicada would have rendered Greek. It reproduces L7-A's register axis for a language the
English quadgram scorer has never seen.

Run: PYTHONUTF8=1 python3 greek_corpus.py   # prints letter count + a sample
"""
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# Greek-bearing source files in the repo (verified to hold >500 Greek letters each).
SOURCES = [
    "analysis/skeleton/corpus/book_of_enoch.txt",
    "analysis/foundation/iamblichus_pythagoras_raw.txt",
    "analysis/skeleton/corpus/homer_iliad.txt",
    "data/keys/armada19/schopenhauer_world_will.txt",
    "data/keys/campaign13/mathscience_whewell_inductive_sciences.txt",
    "analysis/skeleton/corpus/homer_iliad.txt",
]

# Standard scholarly romanization (lowercased, accents stripped). Maps into the A-Z alphabet the
# rune folder understands; digraphs (th, ch, ps) are kept because detectors.text_to_runes handles
# multi-letter runes and TH exists as a rune (index 2).
_GK = {
    "α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e", "ζ": "z", "η": "e",
    "θ": "th", "ι": "i", "κ": "c", "λ": "l", "μ": "m", "ν": "n", "ξ": "x",
    "ο": "o", "π": "p", "ρ": "r", "σ": "s", "ς": "s", "τ": "t", "υ": "u",
    "φ": "f", "χ": "ch", "ψ": "ps", "ω": "o",
}


def _strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def romanized_greek():
    """Return a single romanized-Greek string (lowercase Latin letters + spaces)."""
    words = []
    for rel in SOURCES:
        p = os.path.join(LP, rel)
        if not os.path.exists(p):
            continue
        t = _strip_accents(open(p, encoding="utf-8", errors="ignore").read()).lower()
        for w in re.findall(r"[α-ω]+", t):
            if len(w) >= 2:
                words.append("".join(_GK.get(ch, "") for ch in w))
    return " ".join(w for w in words if w)


if __name__ == "__main__":
    g = romanized_greek()
    letters = re.sub(r"[^a-z]", "", g)
    print(f"romanized greek letters: {len(letters):,}")
    print("sample:", g[:200])
