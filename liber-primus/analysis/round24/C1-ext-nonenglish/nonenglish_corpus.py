"""Round 24 / C1-EXT — honest non-English corpus builders (Old English + Enochian).

Both are extracted from GENUINE non-English text already in the repo — NEVER from an English
translation (see PREREG red-team #1). No external downloads.

OLD ENGLISH: the bilingual Gutenberg Beowulf (round10b/.../corpora/oe_beowulf.txt) interleaves
Old English poetic lines with modern-English apparatus. We keep only lines carrying >=2 of the
OE special letters {þ ð æ Þ Ð Æ}, which uniquely mark the genuine OE poem lines and reject the
English editorial prose. ~138k letters of real Old English.

ENOCHIAN (phonetic Angelic): the phonetic renderings of the Enochian Keys in
analysis/foundation/enoch_text.txt ("Ol sonuf vaoresaji, gohu IAD Balata..."). We keep lines that
are Angelic phonetic (the 'zod'/hyphen-compound register) and reject the English translation
lines. ~9.9k letters. This register is TENTATIVE — its positive control must validate it.

Run: PYTHONUTF8=1 python3 nonenglish_corpus.py   # prints letter counts + samples
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

OE_SRC = os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext",
                      "corpora", "oe_beowulf.txt")
ENOCH_SRC = os.path.join(LP, "analysis", "foundation", "enoch_text.txt")


def old_english():
    """Genuine Old English poetic text: lines with >=2 OE special letters (þ ð æ)."""
    if not os.path.exists(OE_SRC):
        return ""
    t = open(OE_SRC, encoding="utf-8", errors="ignore").read()
    keep = []
    # English editorial prose also occasionally cites OE words; reject any line carrying >=2
    # common modern-English function words so the model stays genuinely Old English.
    ENG = re.compile(r"\b(the|and|of|to|which|that|from|with|would|best|perhaps|"
                     r"during|absence|then|takes|leave|back|for|appeals|etc|adverb)\b",
                     re.IGNORECASE)
    for line in t.split("\n"):
        if len(re.findall(r"[þðæÞÐÆ]", line)) >= 2 and len(ENG.findall(line)) < 2:
            keep.append(line.strip())
    return " ".join(keep)


def enochian():
    """Phonetic Angelic (Enochian) Key text; reject English-translation lines.

    Angelic phonetic markers: the 'zod' spelling, hyphen compounds with Angelic particles,
    and the near-absence of common English function words. English lines are dropped.
    """
    if not os.path.exists(ENOCH_SRC):
        return ""
    t = open(ENOCH_SRC, encoding="utf-8", errors="ignore").read()
    keep = []
    ENG = re.compile(r"\b(the|and|of|to|which|that|from|with|your|shall|are|is|"
                     r"be|for|unto|these|them|him|her|god)\b")
    for line in re.split(r"[\n]", t):
        s = line.strip()
        if not s:
            continue
        low = s.lower()
        angelic = ("zod" in low or "sonuf" in low or "aladi" in low or "peresaho" in low
                   or "qaa" in low or "nazpad" in low
                   or (re.search(r"\b\w+-\w+\b", s)
                       and (" ta " in low or " das " in low or " od " in low or "qo " in low)))
        if angelic and len(ENG.findall(low)) < 2:
            keep.append(s)
    return " ".join(keep)


if __name__ == "__main__":
    for name, fn in (("OLD_ENGLISH", old_english), ("ENOCHIAN", enochian)):
        txt = fn()
        letters = re.sub(r"[^A-Za-zþðæÞÐÆ]", "", txt)
        print(f"{name}: {len(letters):,} letters")
        print("  sample:", txt[:180])
