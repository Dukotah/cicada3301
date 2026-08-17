"""L5-seed32 — EMPIRICAL detection power of the seed sweep at each candidate threshold.

nullcurve.py answers "where is the null at the completed sweep's N". This answers the
other half: "how much English would a corrected threshold still catch". Together they
decide whether finishing the full-32 sweep is informative or a completeness ritual.

Method: reproduce sweep.c's scorer exactly (mean 4-gram log-prob over ngram.bin, the
same 29^4 float32 table the C sweep mmaps), transliterate the same English corpora
prep.py used, and score 40,000 random 48-rune windows. Report the fraction that clears
each threshold. A threshold's detection power = that fraction.

Conservative in the sweep's favour on two counts: (1) the C decoder takes the MAX over
up to 16 interrupter branches, which can only raise a true decode's score; (2) the
corpus that built ngram.bin is the corpus being scored, so these numbers are an upper
bound on power against unseen plaintext.

Run: python3 power.py
"""
import array, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
DATA = os.path.join(ROOT, 'data')
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import GEMATRIA          # noqa: E402

N = 29
W = 48

MULTI = [('ING', 21), ('EA', 28), ('IA', 27), ('IO', 27), ('AE', 25), ('OE', 22),
         ('NG', 21), ('EO', 12), ('TH', 2)]
SINGLE = {t: i for i, r, t, p in GEMATRIA if len(t) == 1}
SINGLE.update({'V': 1, 'K': 5, 'Z': 15, 'Q': 5})


def to_runes(s):
    s = s.upper()
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if not ('A' <= c <= 'Z'):
            i += 1
            continue
        for m, idx in MULTI:
            if s.startswith(m, i):
                out.append(idx); i += len(m); break
        else:
            if c in SINGLE:
                out.append(SINGLE[c])
            i += 1
    return out


def main():
    ng = array.array('f')
    with open(os.path.join(ROOT, 'analysis', 'seed_sweep', 'ngram.bin'), 'rb') as f:
        ng.fromfile(f, N ** 4)

    corp = []
    for f in ('kjv.txt', 'moby.txt', 'pride.txt', 'war.txt'):
        p = os.path.join(DATA, f)
        if os.path.exists(p):
            corp.append(open(p, encoding='utf-8', errors='ignore').read())
    for f in ('mabinogion.txt', 'self_reliance.txt', 'king_in_yellow.txt'):
        p = os.path.join(DATA, 'keys', f)
        if os.path.exists(p):
            corp.append(open(p, encoding='utf-8', errors='ignore').read())
    seq = to_runes('\n'.join(corp))
    print(f'corpus runes: {len(seq):,}')

    def score(w):
        s = 0.0
        for j in range(3, len(w)):
            s += ng[((w[j-3] * N + w[j-2]) * N + w[j-1]) * N + w[j]]
        return s / (len(w) - 3)

    rng = random.Random(3301)
    eng = sorted(score(seq[i:i + W]) for i in rng.sample(range(len(seq) - W), 40000))
    rnd = sorted(score([rng.randrange(N) for _ in range(W)]) for _ in range(40000))

    def pct(xs, q):
        return xs[max(0, min(len(xs) - 1, int(q * len(xs))))]

    print()
    print(f'English 48-rune windows (n={len(eng):,}): mean {sum(eng)/len(eng):+.4f}  '
          f'p1 {pct(eng,.01):+.4f}  p0.1 {pct(eng,.001):+.4f}  min {eng[0]:+.4f}')
    print(f'Uniform-random  (n={len(rnd):,}): mean {sum(rnd)/len(rnd):+.4f}  '
          f'p99.9 {pct(rnd,.999):+.4f}  max {rnd[-1]:+.4f}')
    print()
    print('DETECTION POWER — fraction of true English 48-rune windows clearing each rule')
    print(f'{"threshold":>11}  {"provenance":40s} {"power":>8}')
    print('-' * 64)
    rows = [
        (-12.5000, 'PREREG / Round 8, calibrated at N=2.5e9'),
        (-12.0629, 'FWER 5%  over a completed 10-gen sweep'),
        (-11.8156, 'FWER 1%  over a completed 10-gen sweep'),
        (-11.4655, 'FWER 0.1% over a completed 10-gen sweep'),
        (-11.2360, 'the planted-true self-test score itself'),
    ]
    for t, prov in rows:
        p = sum(1 for x in eng if x > t) / len(eng)
        print(f'{t:>11.4f}  {prov:40s} {p:>7.3%}')
    print()
    fp = sum(1 for x in rnd if x > -12.5) / len(rnd)
    print(f'per-decode false-positive rate of -12.5 on uniform random: {fp:.3e}')
    print('(x 8.59e10 decodes in a completed 10-generator sweep => expected crossings '
          f'{fp * 8.59e10:.3g}, though the sweep\'s decodes are not iid-uniform)')


if __name__ == '__main__':
    main()
