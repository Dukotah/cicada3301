"""Independent loader for the canonical LP2 stream, with the cleartext structure the rig's loader drops.

Written for the Round 44 fresh-eyes audit. It does NOT import the repo rig: it parses
data/krisyotam_runes.txt directly and checks the result against the pinned SHA-256 in PROBLEM.json,
so every audit statistic is computed on a stream that provably equals the canonical one.

Separators in the source file: '-' word, '.' sentence, '/' line end, '%' page, '&' paragraph,
'$' section, digits = literal numerals on the page.
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KRIS = os.path.join(LP, "data", "krisyotam_runes.txt")
RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
TR = ["F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J", "EO", "P", "X", "S", "T", "B", "E",
      "M", "L", "NG", "OE", "D", "A", "AE", "Y", "IA", "EA"]
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89,
          97, 101, 103, 107, 109]
R2I = {r: i for i, r in enumerate(RUNES)}
CANON_SHA = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
N_UNSOLVED_PAGES = 55


def load_all():
    """All 57 %-segments. Each rune is a dict: i (index 0..28), pre (separators before it), line."""
    txt = open(KRIS, encoding="utf-8").read()
    pages = []
    for seg in txt.split("%"):
        runes, seps, line = [], "", 0
        for ch in seg:
            if ch in R2I:
                runes.append({"i": R2I[ch], "pre": seps, "line": line})
                seps = ""
            else:
                seps += ch
                if ch == "/":
                    line += 1
        if runes:
            pages.append(runes)
    return pages


def unsolved():
    """The 55 unsolved pages (segments 0-54), hash-checked against the canonical stream."""
    pages = load_all()[:N_UNSOLVED_PAGES]
    flat = [r["i"] for p in pages for r in p]
    h = hashlib.sha256(",".join(map(str, flat)).encode()).hexdigest()
    assert len(flat) == 12956 and h == CANON_SHA, "loader does not reproduce the canonical stream"
    return pages


def idx(pages):
    return [[r["i"] for r in p] for p in pages]


def word_start(r, k):
    """True if rune r (k-th on its page) starts a word."""
    return k == 0 or ("-" in r["pre"]) or ("." in r["pre"])


def words(pages):
    """Words in reading order as lists of rune indices (a page break is a word break)."""
    out = []
    for p in pages:
        cur = []
        for k, r in enumerate(p):
            if word_start(r, k) and cur:
                out.append(cur)
                cur = []
            cur.append(r["i"])
        if cur:
            out.append(cur)
    return out


if __name__ == "__main__":
    P = unsolved()
    W = words(P)
    print("pages", len(P), "runes", sum(len(p) for p in P), "words", len(W),
          "mean word length %.4f" % (sum(map(len, W)) / len(W)), "one-rune words", sum(len(w) == 1 for w in W))
