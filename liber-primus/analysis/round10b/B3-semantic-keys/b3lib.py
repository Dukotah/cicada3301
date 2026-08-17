"""Lane B3 shared library: orthographic orbit expander + semantic vocabulary + page loading.

The point of this module is G-a from PREREG.md: gp.keyword_to_indices() is a SINGLE greedy
longest-first parse, so every prior keyword sweep in this repo tested exactly one rune spelling
per Latin word.  The author's own demonstrated key FIRFUMFERENFE is not reachable that way.
Here we enumerate the full orthographic orbit of a Latin word:

  * the systematic C -> F substitution the author demonstrably used (all-C or no-C, plus free
    per-C choice for words with <= 3 C's),
  * K and Q, which share the C rune, therefore inherit the same C/F choice,
  * every multigraph boundary the author had free choice at:
        TH | T+H,  EO | E+O,  NG | N+G,  OE | O+E,  AE | A+E,  IA | I+A,  EA | E+A,
        ING -> NG-rune (the rune is documented "NG / ING"),  IO -> IA-rune.
"""
import os
import sys
import itertools

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))

from lp import gematria as gp, corpus, score as _score  # noqa

N = gp.N

# single-letter -> rune index (deterministic ones)
SINGLE = {
    "F": 0, "U": 1, "V": 1, "O": 3, "R": 4, "G": 6, "W": 7, "H": 8, "N": 9,
    "I": 10, "J": 11, "P": 13, "X": 14, "S": 15, "Z": 15, "T": 16, "B": 17,
    "E": 18, "M": 19, "L": 20, "D": 23, "A": 24, "Y": 26,
}
# letters that live on the C rune (5) and may be written with the F rune (0)
C_CLASS = set("CKQ")

# multigraph -> rune index.  Longest first matters for the enumerator.
MULTI = [("ING", 21), ("TH", 2), ("EO", 12), ("NG", 21), ("OE", 22),
         ("AE", 25), ("IA", 27), ("IO", 27), ("EA", 28)]

MAX_VARIANTS = 96


def _segmentations(w):
    """All token segmentations of w using the multigraph table + single letters.
    Yields lists of tokens (strings)."""
    out = []

    def rec(i, acc):
        if len(out) >= 4096:
            return
        if i == len(w):
            out.append(tuple(acc))
            return
        for m, _ in MULTI:
            if w.startswith(m, i):
                acc.append(m)
                rec(i + len(m), acc)
                acc.pop()
        acc.append(w[i])
        rec(i + 1, acc)
        acc.pop()

    rec(0, [])
    return out


def orbit(word):
    """Return the orthographic orbit of a Latin word as a sorted list of rune-index tuples."""
    w = "".join(ch for ch in word.upper() if ch.isalpha())
    if not w:
        return []
    segs = _segmentations(w)
    variants = set()
    for seg in segs:
        cpos = [j for j, tok in enumerate(seg) if tok in C_CLASS]
        if len(cpos) == 0:
            choices = [()]
        elif len(cpos) <= 3:
            choices = list(itertools.product((5, 0), repeat=len(cpos)))
        else:
            # systematic only: all-C or all-F (that is what FIRFUMFERENFE is)
            choices = [tuple([5] * len(cpos)), tuple([0] * len(cpos))]
        for ch in choices:
            idxs = []
            ci = 0
            ok = True
            for tok in seg:
                if tok in C_CLASS:
                    idxs.append(ch[ci]); ci += 1
                    continue
                mm = dict(MULTI).get(tok)
                if mm is not None:
                    idxs.append(mm)
                    continue
                s = SINGLE.get(tok)
                if s is None:
                    ok = False
                    break
                idxs.append(s)
            if ok and idxs:
                variants.add(tuple(idxs))
    v = sorted(variants)
    if len(v) > MAX_VARIANTS:
        # keep the greedy parse, the all-C and all-F systematic forms, then shortest keys first
        greedy = tuple(gp.keyword_to_indices(w)) if _safe_greedy(w) else None
        v.sort(key=lambda t: (len(t), t))
        keep = v[:MAX_VARIANTS]
        if greedy and greedy not in keep:
            keep[-1] = greedy
        v = keep
    return v


def _safe_greedy(w):
    try:
        gp.keyword_to_indices(w)
        return True
    except ValueError:
        return False


# ------------------------------------------------------------------ vocabulary
# Derived SEMANTICALLY, per the lane brief: from the author's own demonstrated sources.

# (1) the known section titles across LP1 + LP2 (the author's own chapter headings)
TITLES = [
    "WELCOME", "SOMEWISDOM", "AKOAN", "ANINSTRUCTION", "ANEND", "PARABLE",
    "AWARNING", "ANINSTAR", "THELOSSOFDIVINITY", "THELOSS", "LOSSOFDIVINITY",
    "AKOANOFTHEINSTAR", "AWISDOM", "WISDOM", "KOAN", "INSTRUCTION", "WARNING",
    "ENDOFALLTHINGS", "THEGREATJOURNEY", "THEINSTAR", "THEDIVINITY",
    "ANINSTARWITHIN", "THEEMERGENCE", "THECIRCUMFERENCE", "THEPRIMES",
    "THETOTIENTFUNCTION", "AWARNINGTOTHEPILGRIM", "APARABLE", "THEPARABLE",
]

# (2) content words drawn from the author's own plaintext (LP1 solved pages + LP2 seg 56)
#     -- the demonstrated key-selection rule is "a thematic word from the page's own meaning".
LP_PLAINTEXT_WORDS = [
    # 03.jpg WELCOME page
    "WELCOME", "PILGRIM", "GREAT", "JOURNEY", "TOWARD", "THINGS", "EASY", "TRIP",
    "PATIENCE", "DILIGENCE", "ENLIGHTENMENT", "DECEPTION", "DECEIVE", "TRUTH",
    "BOOK", "PRIMES", "SACRED", "DIVINITY", "EMERGE", "EMERGENCE", "INSTAR",
    # 05.jpg SOME WISDOM
    "TOTIENT", "FUNCTION", "ENCRYPTED", "ENCRYPT", "COMMAND", "MASTER", "STUDENT",
    "LESSON", "CIRCUMFERENCE", "VOICE", "SAID", "ASKED", "EXPLAIN", "EXPLAINED",
    # 06-09 instruction pages
    "DECIDED", "STUDY", "SHADOWS", "SHADOW", "CAVE", "REALITY", "ILLUSION",
    "CONSUME", "CONSUMPTION", "PRESERVE", "PRESERVATION", "ADHERE", "ADHERENCE",
    "OBEY", "COMMANDMENT", "MOBIUS", "TUNNEL", "TUNNELING", "SURFACE", "SHED",
    "WITHIN", "WITHOUT", "SELF", "SELFRELIANCE", "AMASS", "KNOWLEDGE",
    # LP2 seg 56 PARABLE (the one readable LP2 page -- most page-local source there is)
    "LIKE", "MUST", "OUR", "OWN", "FIND", "AND", "THE",
]

# (3) the author's published prose lexicon 2012-2014 (outside the book, period-correct)
AUTHOR_PROSE = [
    "MAYFLY", "INSTAR", "EMERGENCE", "TUNNELING", "CIRCUMFERENCE", "DIVINITY",
    "PRIMES", "PRIME", "TOTIENT", "SHADOWS", "EPIPHANY", "KOAN", "PARABLE",
    "SACRED", "PILGRIM", "PILGRIMAGE", "WISDOM", "CICADA", "LIBERPRIMUS",
    "LIBER", "PRIMUS", "GEMATRIA", "GEMATRIAPRIMUS", "RUNES", "FUTHORC",
    "ANEND", "THEEND", "ENDOFALLTHINGS", "SEEKOUT", "SEEK", "TRUTH",
    "ENLIGHTENMENT", "CONSCIOUSNESS", "SACRIFICE", "DISCOVER", "JOURNEY",
    "EMERGE", "PRESERVE", "ADHERE", "DECEPTION", "ILLUSION", "REALITY",
]

# (4) section/structure handles: the 14 red-ink heads and the &/$ ornament sections
STRUCTURE_WORDS = [
    "SECTION", "CHAPTER", "VERSE", "PAGE", "FIRST", "SECOND", "THIRD",
    "BEGINNING", "THEBEGINNING", "END", "THEEND", "OPENING", "CLOSING",
]


def vocabulary():
    seen, out = set(), []
    for grp, words in (("title", TITLES), ("plaintext", LP_PLAINTEXT_WORDS),
                       ("prose", AUTHOR_PROSE), ("structure", STRUCTURE_WORDS)):
        for w in words:
            key = w.upper()
            if key in seen:
                continue
            seen.add(key)
            out.append((grp, key))
    return out


def expanded_keys():
    """[(latin, group, tuple(rune indices)), ...] deduped by rune tuple."""
    out, seen = [], set()
    for grp, w in vocabulary():
        for t in orbit(w):
            if t in seen:
                continue
            seen.add(t)
            out.append((w, grp, t))
    return out


# ------------------------------------------------------------------ pages
KRIS = os.path.join(ROOT, "data", "krisyotam_runes.txt")


def lp2_segments():
    """[(seg_index, [rune indices]), ...] for all 57 krisyotam segments."""
    txt = open(KRIS, encoding="utf-8").read()
    segs = txt.split("%")
    out = []
    for s in segs:
        idxs = gp.runes_to_indices(s)
        if idxs:
            out.append(idxs)
    return out


def lp2_segments_raw():
    txt = open(KRIS, encoding="utf-8").read()
    return [s for s in txt.split("%") if gp.runes_to_indices(s)]


def solved_page(label):
    p = corpus.page_by_label(label)
    return gp.runes_to_indices(p["runes"]), p


def scorer():
    return _score.default()


if __name__ == "__main__":
    ks = expanded_keys()
    print(f"vocabulary words : {len(vocabulary())}")
    print(f"expanded keys    : {len(ks)}")
    circ = [k for k in ks if k[0] == "CIRCUMFERENCE"]
    print("CIRCUMFERENCE orbit:")
    for lat, grp, t in circ:
        print("   ", gp.indices_to_translit(t))
    div = [k for k in ks if k[0] == "DIVINITY"]
    print("DIVINITY orbit:", [gp.indices_to_translit(t) for _, _, t in div])
