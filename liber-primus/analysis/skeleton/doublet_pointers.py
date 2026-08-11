"""Short shot — the residual doublets as POINTERS rather than as structure.

Round 5 (LEDGER/DEAD_ENDS) tested the surviving doublets for digraphic parity,
doubled-rune identity and inter-doublet gap distribution -- i.e. as *cipher
structure*, and killed all three. Nobody has tested them as a *payload*: an
83-element list of positions is exactly the shape of a book-cipher index, and
Cicada's own solved pages are the obvious book.

Tests (each scored against an explicit null):
  1. the doubled rune values read as a message
  2. inter-doublet gaps read as letters (1..26 / mod 26 / mod 29)
  3. gaps as word indices into the solved LP1 English (book cipher)
  4. positions as word indices into the LP2 cleartext skeleton
  5. positions/gaps vs primes, totients, Fibonacci
  6. the runes immediately following each doublet, in order
"""
import os, sys, json, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import IDX_TO_TRANS, RUNE_TO_IDX

N = 29
ct = np.frombuffer(open(os.path.join(ROOT, 'analysis', 'seed_sweep', 'ct.bin'),
                        'rb').read(), np.uint8).astype(int)
ng = np.fromfile(os.path.join(ROOT, 'analysis', 'seed_sweep', 'ngram.bin'),
                 np.float32)

SOLVED = """WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT
AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY
YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR
CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF SOME WISDOM THE
PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW
THIS A KOAN DURING A LESSON THE MASTER EXPLAINED THE I THE I IS THE VOICE OF THE
CIRCUMFERENCE HE SAID WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER
SAID IT IS A VOICE INSIDE YOUR HEAD I DO NOT HAVE A VOICE IN MY HEAD THOUGHT THE
STUDENT AND HE RAISED HIS HAND TO TELL THE MASTER THE MASTER STOPPED THE STUDENT AND
SAID THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD IS THE I AND THE STUDENTS
WERE ENLIGHTENED AN INSTRUCTION QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF
FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS KNOW THIS AN END WITHIN THE DEEP WEB THERE
EXISTS A PAGE THAT HASHES TO IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE
PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES
FIND THE DIVINITY WITHIN AND EMERGE""".split()


def score_runes(seq):
    if len(seq) < 8:
        return -99.0
    a = np.asarray(seq, np.int32) % N
    idx = ((a[:-3]*N + a[1:-2])*N + a[2:-1])*N + a[3:]
    return float(ng[idx].mean())


def show(seq):
    return ''.join(IDX_TO_TRANS[int(v) % N] for v in seq)


def latin(seq, mod=26):
    return ''.join(chr(ord('A') + (int(v) % mod)) for v in seq)


def main():
    pos = [i for i in range(1, len(ct)) if ct[i] == ct[i-1]]
    vals = [ct[i] for i in pos]
    gaps = [pos[i] - pos[i-1] for i in range(1, len(pos))]
    print('residual doublets: %d   positions %d..%d' % (len(pos), pos[0], pos[-1]))
    print('gaps: n=%d min %d max %d mean %.1f' %
          (len(gaps), min(gaps), max(gaps), np.mean(gaps)))

    out = {}
    rng = np.random.default_rng(3301)

    def report(name, seq, text=None):
        s = score_runes(seq)
        out[name] = dict(score=s, head=(text or show(seq))[:70])
        print('%-38s score %8.4f  %s' % (name, s, (text or show(seq))[:56]))
        return s

    # 1. the doubled runes themselves
    report('1 doubled rune values', vals)
    print('   as latin: %s' % show(vals))

    # 2. gaps as letters
    report('2a gaps mod 29', [g % 29 for g in gaps])
    print('   gaps mod 26 -> %s' % latin(gaps)[:70])
    print('   gaps-1 mod 26 -> %s' % latin([g-1 for g in gaps])[:70])

    # 3. gaps as word indices into the solved LP1 English
    for base, tag in ((0, '0-based'), (1, '1-based')):
        w = [SOLVED[(g - base) % len(SOLVED)] for g in gaps]
        print('3 gaps as word index (%s): %s' % (tag, ' '.join(w[:14])))
    # cumulative gaps too (a real book cipher indexes cumulatively)
    cum = np.cumsum(gaps)
    w = [SOLVED[c % len(SOLVED)] for c in cum]
    print('3 cumulative gaps as word index: %s' % ' '.join(w[:14]))

    # 4. positions as word indices into LP2's own cleartext word skeleton
    txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'),
               encoding='utf-8').read()
    words, cur = [], []
    for ch in txt.split('%')[0] if False else txt:
        if ch in RUNE_TO_IDX:
            cur.append(RUNE_TO_IDX[ch])
        elif ch in '-./%\n':
            if cur:
                words.append(cur); cur = []
    firsts = [w[0] for w in words]
    report('4 first rune of the pos-indexed word',
           [firsts[p % len(firsts)] for p in pos])

    # 5. number-theoretic identity of positions and gaps
    def primes_upto(n):
        s = np.ones(n+1, bool); s[:2] = False
        for i in range(2, int(n**0.5)+1):
            if s[i]:
                s[i*i::i] = False
        return np.flatnonzero(s)
    pr = set(primes_upto(20000).tolist())
    print('5 positions that are prime: %d/%d (chance ~%.1f)' %
          (sum(1 for p in pos if p in pr), len(pos),
           len(pos) * len([1 for x in range(1, 13000) if x in pr]) / 13000))
    print('  gaps that are prime: %d/%d' % (sum(1 for g in gaps if g in pr), len(gaps)))
    fib = set()
    a, b = 1, 2
    while a < 20000:
        fib.add(a); a, b = b, a+b
    print('  gaps that are Fibonacci: %d/%d' % (sum(1 for g in gaps if g in fib), len(gaps)))

    # 6. the runes following each doublet
    report('6 rune after each doublet', [ct[p+1] for p in pos if p+1 < len(ct)])
    report('6b rune before each doublet', [ct[p-2] for p in pos if p >= 2])

    # null calibration: same statistics on random position sets
    nulls = []
    for _ in range(2000):
        q = np.sort(rng.choice(len(ct)-1, len(pos), replace=False)) + 1
        nulls.append(score_runes([ct[i] for i in q]))
    nulls = np.array(nulls)
    print('\nnull (random position sets of the same size): mean %.4f sd %.4f max %.4f'
          % (nulls.mean(), nulls.std(), nulls.max()))
    print('English-class threshold for this length is about -12.0;')
    print('best observed across all readings: %.4f'
          % max(v['score'] for v in out.values()))
    json.dump(dict(n_doublets=len(pos), positions=pos, gaps=gaps, readings=out,
                   null_mean=float(nulls.mean()), null_sd=float(nulls.std()),
                   null_max=float(nulls.max())),
              open(os.path.join(HERE, 'doublet_pointer_results.json'), 'w'), indent=1)
    print('wrote doublet_pointer_results.json')


if __name__ == '__main__':
    main()
