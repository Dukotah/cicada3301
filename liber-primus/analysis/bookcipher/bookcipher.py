"""RED TEAM front #2: is it a BOOK CIPHER, not a keyed cipher?

If the runes are POINTERS into an external book (a confirmed Cicada M.O. -- the
2012 puzzle used book codes into Agrippa/the Mabinogion), the stream looks
exactly this flat, no key ever breaks it, and it's solvable only WITH the book.
Not excluded by the doublet argument (that was about ADDITIVE keys; selection is
different). Test the natural pointer schemes against Cicada's known books.

Schemes (rune stream drives selection from book B):
  L1  cumulative LETTER skip by (rune_index+1); read B.letters[pos % Ln]
  L2  cumulative LETTER skip by rune PRIME value
  W1  cumulative WORD skip by (rune_index+1); output whole word (classic book code)
  W2  cumulative WORD skip by rune PRIME value
  G   grouped base-29 pairs -> absolute letter position
Each x book x {forward, reversed rune stream} x a few start offsets.
Score with the English quadgram model; a real decode reads as English (~-2.2).
Reproduce: PYTHONUTF8=1 python analysis/bookcipher/bookcipher.py
"""
import os, sys, re
import numpy as np
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp
from lp import score as _score

N = 29
P = gp.PRIMES
SC = _score.default()

def runes():
    segs = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read().split("%")
    ix = [i for s in segs[:-2] for i in gp.runes_to_indices(s)]
    return np.array(ix)

def load_book(fn):
    t = open(os.path.join(HERE, "books", fn), encoding="utf-8", errors="ignore").read()
    a = re.split(r"\*\*\* ?START.*?\*\*\*", t, flags=re.S)
    t = a[1] if len(a) > 1 else t
    t = re.split(r"\*\*\* ?END", t, flags=re.S)[0]
    letters = re.sub(r"[^A-Z]", "", t.upper())
    words = re.findall(r"[A-Za-z]+", t)
    return letters, [w.upper() for w in words if 1 < len(w) < 15]

R = runes()
print(f"{len(R)} unsolved runes; testing book-cipher pointer schemes\n")
BOOKS = ["kjv.txt", "mabinogion.txt", "miltonPL.txt", "blake.txt", "agrippa.txt"]
best = (-99, None)

def score_letters(s):
    return SC.score_norm(s[:4000])  # 4k chars is plenty to judge English-ness

for bf in BOOKS:
    try:
        letters, words = load_book(bf)
    except Exception as e:
        continue
    Ln, Wn = len(letters), len(words)
    if Ln < 5000:
        continue
    for rev in (False, True):
        rr = R[::-1] if rev else R
        steps_idx = (rr + 1)
        steps_prime = np.array([P[i] for i in rr])
        for off in (0, 1000, 12345):
            # L1 / L2 : letter selection
            for lbl, steps in (("L1", steps_idx), ("L2", steps_prime)):
                pos = (off + np.cumsum(steps)) % Ln
                out = "".join(letters[p] for p in pos[:4000])
                s = score_letters(out)
                if s > best[0]:
                    best = (s, dict(book=bf, scheme=lbl, rev=rev, off=off, head=out[:60]))
            # W1 / W2 : word selection (classic book code) -> concatenate words
            for wbl, steps in (("W1", steps_idx), ("W2", steps_prime)):
                pos = (off + np.cumsum(steps)) % Wn
                out = "".join(words[p] for p in pos[:800])
                s = score_letters(out)
                if s > best[0]:
                    best = (s, dict(book=bf, scheme=wbl, rev=rev, off=off, head=out[:60]))
        # G : grouped base-29 pairs -> absolute position
        pairs = rr[:len(rr) // 2 * 2].reshape(-1, 2)
        pos = (pairs[:, 0] * N + pairs[:, 1]) % Ln
        out = "".join(letters[p] for p in pos[:4000])
        s = score_letters(out)
        if s > best[0]:
            best = (s, dict(book=bf, scheme="G", rev=rev, off=0, head=out[:60]))
    print(f"  tested {bf} (Ln={Ln}, Wn={Wn})")

print("\n" + "=" * 55)
print(f"BEST book-cipher decode: {best[0]:.3f}  (English ~ -2.2, noise < -4)")
print("  ", best[1])
if best[0] > -3.2:
    print("\n  *** ABOVE NOISE — BOOK-CIPHER LEAD, VERIFY ***")
else:
    print("\n  Null: no natural pointer scheme into Cicada's known books yields")
    print("  English. (DOF is large; this tests the natural family, not all schemes.)")
