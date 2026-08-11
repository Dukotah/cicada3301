"""Track SKELETON — is the cleartext consistent with English PLUS interrupters?

LP2's mean rune-word length is 4.43 against ~4.1 for English-in-futhorc. That gap
has an obvious candidate explanation: a null interrupter adds one rune to its
word, and LP2 carries 458 F runes over 2,928 words. The right comparison is
therefore not raw English but English with F-insertions simulated at the observed
rate -- otherwise the cipher's own padding is mistaken for a plaintext anomaly.

Also reports what fraction of F would have to be null for the distributions to
agree, which is an independent estimate of the null-interrupter count. That
number is interesting on its own: the community has never had a way to estimate
it for the unsolved pages, because the usual method (does the decode read?)
requires the key.
"""
import os, sys, re, math, random, collections, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import RUNE_TO_IDX

MULTI = ('ING', 'EA', 'IA', 'IO', 'AE', 'OE', 'NG', 'EO', 'TH')


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
    a = np.sort(np.asarray(a)); b = np.sort(np.asarray(b))
    vs = np.union1d(a, b)
    fa = np.searchsorted(a, vs, 'right') / len(a)
    fb = np.searchsorted(b, vs, 'right') / len(b)
    return float(np.abs(fa - fb).max())


def lp2():
    txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'),
               encoding='utf-8').read()
    words, cur, cf, F = [], 0, 0, 0
    for seg in txt.split('%')[:55]:
        for ch in seg:
            if ch in RUNE_TO_IDX:
                cur += 1
                if ch == 'ᚠ':
                    cf += 1
            elif ch in '-.':                    # '/' is a line wrap
                if cur:
                    words.append((cur, cf)); F += cf
                cur = cf = 0
        if cur:
            words.append((cur, cf)); F += cf
            cur = cf = 0
    return words, F


def main():
    w, F = lp2()
    obs = [a for a, _ in w]
    n = len(obs)
    print('LP2 unsolved: %d words, %d F runes, mean length %.3f'
          % (n, F, np.mean(obs)))

    ref_text = open(os.path.join(ROOT, 'data', 'moby.txt'),
                    encoding='utf-8', errors='ignore').read()
    eng = [enc(x) for x in re.findall(r"[A-Za-z']+", ref_text)]
    eng = [x for x in eng if x][:200000]
    print('English-in-futhorc reference: %d words, mean %.3f'
          % (len(eng), np.mean(eng)))

    rng = np.random.default_rng(3301)
    print('\n%-8s %-10s %-10s %-10s' % ('null F', 'ins/word', 'KS', 'verdict'))
    crit = 1.36 * math.sqrt(1/n + 1/len(eng))
    best = None
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        nulls = F * frac
        rate = nulls / n                       # mean inserted runes per word
        sim = []
        for _ in range(6):
            base = rng.choice(eng, n, replace=False)
            add = rng.poisson(rate, n)
            sim.append(base + add)
        sim = np.concatenate(sim)
        k = ks(obs, sim)
        tag = 'consistent' if k < crit else 'DIFFERENT'
        print('%-8.0f %-10.3f %-10.4f %-10s (crit %.4f)'
              % (nulls, rate, k, tag, crit))
        if best is None or k < best[0]:
            best = (k, frac, nulls)
    print('\nclosest fit: %.0f null interrupters (%.0f%% of the 458 F runes), KS %.4f'
          % (best[2], 100*best[1], best[0]))
    print('mean-length gap accounted for: LP2 %.3f vs English %.3f = %+.3f runes/word;'
          % (np.mean(obs), np.mean(eng), np.mean(obs) - np.mean(eng)))
    print('all 458 F as nulls would supply %+.3f runes/word.' % (F / n))
    json.dump(dict(n_words=n, F=F, lp2_mean=float(np.mean(obs)),
                   eng_mean=float(np.mean(eng)), crit=crit,
                   best_frac=best[1], best_ks=best[0]),
              open(os.path.join(HERE, 'interrupter_null.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
