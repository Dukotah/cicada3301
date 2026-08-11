"""Track SKELETON — distributional tests on the cleartext channel.

Companion to wordlen_search.py (which asks WHICH text). This asks the weaker but
cheaper question: does the cleartext skeleton look like natural-language prose at
all? Word boundaries are unenciphered, so this is measurable without any key.

Two tests:
  1. word-length distribution of LP2 vs English-in-futhorc (KS)
  2. clause-position structure: in real prose, clause-edge words have a different
     length profile than clause-interior words. A pad or a filler has none.

CRITICAL PARSING NOTE. `/` is a LINE WRAP, not a word separator: 458 of the 604
line breaks fall mid-word (e.g. ...-I / AEHXTHP-...). Splitting words at `/`
shatters 458 words into 916 fragments and manufactures a huge false excess of
short words. Only `-` (word), `.` (title mark) and `%` (page) end a word.

IMPORTANT scoping note. An earlier quick pass measured these over the whole
krisyotam file, which includes the two SOLVED LP2 pages (AN END, PARABLE) -- real
English. Restricted correctly to the 55 unsolved pages the clause-edge effect is
NOT significant. Recorded here so the earlier number is not propagated.

The reference English is the solved LP1 prose typed out as plaintext.
data/keys/solved_plaintext.txt is NOT usable for this -- it is PGP-signed message
bodies with hex digest blobs, whose "words" are hex chunks.
"""
import os, sys, re, math, random, collections, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import RUNE_TO_IDX

MULTI = ('ING', 'EA', 'IA', 'IO', 'AE', 'OE', 'NG', 'EO', 'TH')

SOLVED_LP1 = """WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS
IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE
ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE
YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY
ULTIMATELY YOU WILL DISCOVER AN END TO SELF
SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED
ALL THINGS SHOULD BE ENCRYPTED KNOW THIS
A KOAN DURING A LESSON THE MASTER EXPLAINED THE I
THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID
WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID
IT IS A VOICE INSIDE YOUR HEAD
I DO NOT HAVE A VOICE IN MY HEAD THOUGHT THE STUDENT
AND HE RAISED HIS HAND TO TELL THE MASTER
THE MASTER STOPPED THE STUDENT AND SAID
THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD IS THE I
AND THE STUDENTS WERE ENLIGHTENED AN INSTRUCTION
QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH
IMPOSE NOTHING ON OTHERS KNOW THIS
AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO
IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE
PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE
WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE"""


def enc(w):
    w = w.upper(); i = n = 0
    while i < len(w):
        for m in MULTI:
            if w.startswith(m, i):
                i += len(m); n += 1
                break
        else:
            if 'A' <= w[i] <= 'Z':
                n += 1
            i += 1
    return n


def ks(a, b):
    a = sorted(a); b = sorted(b); d = 0.0
    for v in sorted(set(a) | set(b)):
        d = max(d, abs(sum(1 for x in a if x <= v)/len(a)
                       - sum(1 for x in b if x <= v)/len(b)))
    return d


def main():
    txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'),
               encoding='utf-8').read()
    segs = txt.split('%')[:55]                      # UNSOLVED pages only
    words, bnd, cur = [], [], 0
    for seg in segs:
        for ch in seg:
            if ch in RUNE_TO_IDX:
                cur += 1
            elif ch in '-.':          # '/' is a LINE WRAP, not a word boundary
                if cur:
                    words.append(cur); bnd.append(ch); cur = 0
        if cur:
            words.append(cur); bnd.append('%'); cur = 0
    n = len(words)

    sol = [enc(w) for w in SOLVED_LP1.split() if enc(w)]
    refs = {'solved LP1 English': sol}
    for f in ('pride.txt', 'moby.txt', 'kjv.txt'):
        p = os.path.join(ROOT, 'data', f)
        if os.path.exists(p):
            t = open(p, encoding='utf-8', errors='ignore').read()
            refs[f] = [enc(w) for w in re.findall(r"[A-Za-z']+", t)][:20000]

    print('LP2 unsolved: %d words, mean %.3f' % (n, sum(words)/n))
    out = {'n_words': n, 'mean': sum(words)/n, 'ks': {}}
    for name, r in refs.items():
        r = [x for x in r if x]
        crit = 1.36 * math.sqrt(1/n + 1/len(r))
        k = ks(words, r)
        verdict = 'indistinguishable' if k < crit else 'distinguishable'
        print('  KS(LP2, %-20s) = %.4f   crit@.05 %.4f  n_ref %5d  -> %s'
              % (name, k, crit, len(r), verdict))
        out['ks'][name] = dict(ks=k, crit=crit, n=len(r), verdict=verdict)

    c = collections.Counter(words)
    print('  LP2 1-rune-word share %.3f  vs English prose ~0.042'
          % (c[1]/n))
    out['len1_share'] = c[1]/n

    # clause position -- '.' and '%' end a clause; '/' is a line wrap, not a break
    first, last, inter = [], [], []
    for i, (w, b) in enumerate(zip(words, bnd)):
        pe = (i == 0) or bnd[i-1] in '.%'
        te = b in '.%'
        (first if pe else (last if te else inter)).append(w)
    m = lambda x: sum(x)/len(x)
    print('\nclause position: FIRST %.3f (n=%d)  LAST %.3f (n=%d)  INTERIOR %.3f (n=%d)'
          % (m(first), len(first), m(last), len(last), m(inter), len(inter)))
    random.seed(3301)
    out['clause'] = {}
    for nm, grp in (('last', last), ('first', first)):
        obs = m(grp) - m(inter)
        pool = grp + inter
        k = len(grp)
        cnt = 0
        for _ in range(20000):
            random.shuffle(pool)
            if abs(m(pool[:k]) - m(pool[k:])) >= abs(obs):
                cnt += 1
        p = cnt/20000
        print('  %-5s vs interior: %+.3f runes  permutation p = %.4f  -> %s'
              % (nm, obs, p, 'significant' if p < 0.05 else 'NOT significant'))
        out['clause'][nm] = dict(diff=obs, p=p)
    json.dump(out, open(os.path.join(HERE, 'cleartext_profile.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
