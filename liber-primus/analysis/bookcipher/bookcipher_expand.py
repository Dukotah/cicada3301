"""EXPANDED book-cipher extraction over Cicada-adjacent esoterica NEVER tested
as book ciphers: Liber AL (Book of the Law), Kybalion, Blake's Marriage of
Heaven and Hell, Ars Goetia (Lesser Key of Solomon), Thunder Perfect Mind,
Gospel of Thomas (Nag Hammadi).

Assignment lane: novel_cipher. Prior book-cipher only tried KJV/Mabinogion/
Milton/Blake(complete)/Agrippa (all null, additive AND pointer). This adds the
above texts and MORE pointer schemes: word-index, line-index, page-index
selection driven by the rune stream.

Rune stream drives SELECTION from book B. Schemes:
  L1  cumulative LETTER skip by (rune_index+1); read B.letters[pos]
  L2  cumulative LETTER skip by rune PRIME value
  W1  cumulative WORD skip by (rune_index+1); output whole WORD (classic book code)
  W2  cumulative WORD skip by rune PRIME value; output whole WORD
  WA  ABSOLUTE word index = grouped base-29 pairs -> words[pos]  (word-index pointer)
  LN  LINE-index pointer: grouped triples -> line number -> first letter of line
  PG  PAGE-index pointer: grouped -> (page,line,word) -> word (needs pagination approx)
Each x book x {forward, reversed} x start offsets. Score English quadgram.
A real decode reads English (~ -2.2 letters / better than -4 = signal).
"""
import os, sys, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
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
    # strip gutenberg boilerplate if present
    a = re.split(r"\*\*\* ?START.*?\*\*\*", t, flags=re.S)
    t = a[1] if len(a) > 1 else t
    t = re.split(r"\*\*\* ?END", t, flags=re.S)[0]
    letters = re.sub(r"[^A-Z]", "", t.upper())
    words = [w.upper() for w in re.findall(r"[A-Za-z]+", t) if 1 < len(w) < 15]
    lines = [ln for ln in re.split(r"[.;:\n]", t) if len(re.sub(r"[^A-Za-z]","",ln)) > 3]
    return letters, words, lines

def score_letters(s):
    return SC.score_norm(s[:4000])

R = runes()
print(f"{len(R)} unsolved runes; expanded book-cipher pointer schemes\n")

BOOKS = ["liber_al.txt", "kybalion.txt", "blake_mhh.txt", "goetia_g.txt",
         "thunder.txt", "thomas_gnosis.txt"]

best = (-99.0, None)
results = []

for bf in BOOKS:
    try:
        letters, words, lines = load_book(bf)
    except Exception as e:
        print(f"  skip {bf}: {e}"); continue
    Ln, Wn, LNn = len(letters), len(words), len(lines)
    if Ln < 3000:
        print(f"  skip {bf}: too short ({Ln})"); continue
    bbest = (-99.0, None)
    for rev in (False, True):
        rr = R[::-1] if rev else R
        steps_idx = (rr + 1)
        steps_prime = np.array([P[i] for i in rr])
        for off in (0, 1, 1000, 12345):
            for lbl, steps in (("L1", steps_idx), ("L2", steps_prime)):
                pos = (off + np.cumsum(steps)) % Ln
                out = "".join(letters[p] for p in pos[:4000])
                s = score_letters(out)
                if s > bbest[0]: bbest = (s, dict(book=bf, scheme=lbl, rev=rev, off=off, head=out[:60]))
            for wbl, steps in (("W1", steps_idx), ("W2", steps_prime)):
                pos = (off + np.cumsum(steps)) % Wn
                out = "".join(words[p] for p in pos[:800])
                s = score_letters(out)
                if s > bbest[0]: bbest = (s, dict(book=bf, scheme=wbl, rev=rev, off=off, head=out[:60]))
        # WA: absolute word-index from base-29 pairs
        pairs = rr[:len(rr)//2*2].reshape(-1,2)
        widx = (pairs[:,0]*N + pairs[:,1]) % Wn
        out = "".join(words[p] for p in widx[:800]); s = score_letters(out)
        if s > bbest[0]: bbest = (s, dict(book=bf, scheme="WA", rev=rev, off=0, head=out[:60]))
        # WA3: base-29 triples for larger index range
        tri = rr[:len(rr)//3*3].reshape(-1,3)
        widx3 = (tri[:,0]*N*N + tri[:,1]*N + tri[:,2]) % Wn
        out = "".join(words[p] for p in widx3[:800]); s = score_letters(out)
        if s > bbest[0]: bbest = (s, dict(book=bf, scheme="WA3", rev=rev, off=0, head=out[:60]))
        # LN: line-index pointer -> first letter of chosen line
        lidx = (pairs[:,0]*N + pairs[:,1]) % LNn
        out = "".join(re.sub(r"[^A-Za-z]","",lines[p])[:1].upper() or "X" for p in lidx[:4000]); s = score_letters(out)
        if s > bbest[0]: bbest = (s, dict(book=bf, scheme="LN-firstletter", rev=rev, off=0, head=out[:60]))
        # G: grouped base-29 pairs -> absolute letter position
        gpos = (pairs[:,0]*N + pairs[:,1]) % Ln
        out = "".join(letters[p] for p in gpos[:4000]); s = score_letters(out)
        if s > bbest[0]: bbest = (s, dict(book=bf, scheme="G-letter", rev=rev, off=0, head=out[:60]))
    results.append(bbest)
    if bbest[0] > best[0]: best = bbest
    print(f"  {bf:20s} Ln={Ln:7d} Wn={Wn:6d} best={bbest[0]:.3f} {bbest[1]['scheme']:14s} head={bbest[1]['head'][:34]!r}")

print("\n" + "="*60)
print(f"OVERALL BEST: {best[0]:.3f}  (English letters ~ -2.2; noise < -4; HIT threshold beats -5.2 WITH readable English)")
print("  ", best[1])
if best[0] > -3.2:
    print("\n  *** ABOVE ENGLISH-NOISE FLOOR -- BOOK-CIPHER LEAD, VERIFY ***")
else:
    print("\n  NULL: no natural pointer scheme into these esoterica yields English.")
