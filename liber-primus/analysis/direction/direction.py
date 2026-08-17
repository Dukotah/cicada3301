"""Track DIRECTION — "their numbers are the direction".

Licensed by a SIGNED 3301 statement rather than by speculation. The 2016 message
(OpenPGP 7A35090F, 2016-01-01, recovered by outguess from the tweet image) reads:

    Liber Primus is the way.  Its words are the map, their
    meaning is the road, and their numbers are the direction.

Three parts: words = map, meaning = road, NUMBERS = direction. The repo has
attacked the numbers as KEYSTREAM (prime/totient/Fibonacci -- all dead, and dead
by mechanism since any additive stream lands in the measured normal doublet band)
and as history-dependent prime transforms (`analysis/seek_primes.py`). It has
never attacked them as what the word "direction" actually says: a rule for WHERE
TO GO NEXT.

That is a different mechanism, not another key. It supposes the pages are mostly
filler and the message sits at COMPUTED POSITIONS, unenciphered. Nothing measured
so far excludes it:
  - flat IoC is exactly what filler gives;
  - Round 6's SIEVE-W hunted for readable *contiguous* windows with a sliding
    detector, so a non-contiguous, position-computed message is invisible to it;
  - it needs no key, so the one-time-pad verdict does not apply.

Families tested (all deterministic, all key-free):
  A  self-indexing walk : p <- p + f(c[p])       f = index, index+1, gematria
                          prime, prime mod 29, prime-1 (totient), reversed index
  B  cumulative walk    : p <- p + (running sum of f(c)) mod L
  C  sign walk          : each rune's parity/threshold picks forward or back by a
                          fixed stride
  D  numeric sieve      : read positions selected by a number-theoretic predicate
                          (prime index, totient, Fibonacci, squares, 3301-related)

Every reading is scored with the same rune 4-gram model used by the seed sweep,
against a null built by running the identical families on a shuffled ciphertext.
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import PRIMES, IDX_TO_TRANS

N = 29
SS = os.path.join(ROOT, 'analysis', 'seed_sweep')
ct = np.frombuffer(open(os.path.join(SS, 'ct.bin'), 'rb').read(), np.uint8).astype(int)
ng = np.fromfile(os.path.join(SS, 'ngram.bin'), np.float32)
L = len(ct)
PRIME = np.array(PRIMES)


def score(seq):
    if len(seq) < 24:
        return -99.0
    a = np.asarray(seq, np.int32)
    idx = ((a[:-3]*N + a[1:-2])*N + a[2:-1])*N + a[3:]
    return float(ng[idx].mean())


def show(seq, k=60):
    return ''.join(IDX_TO_TRANS[int(v)] for v in seq[:k])


# ------------------------------------------------------------- step functions
STEPS = {
    'idx':        lambda v: v,
    'idx+1':      lambda v: v + 1,
    'prime':      lambda v: int(PRIME[v]),
    'prime%29':   lambda v: int(PRIME[v]) % N,
    'totient':    lambda v: int(PRIME[v]) - 1,
    'revidx':     lambda v: N - v,
    'idx*2+1':    lambda v: 2*v + 1,
    'primesum%L': lambda v: int(PRIME[v]),
}


def walk(stream, step, start, maxlen=400, back=False, skipF=True):
    """family A: p <- p +/- f(c[p]); collect the runes landed on"""
    out, seen, p = [], set(), start
    sgn = -1 if back else 1
    while len(out) < maxlen:
        if p in seen:
            break
        seen.add(p)
        v = int(stream[p])
        if not (skipF and v == 0):
            out.append(v)
        d = step(v)
        if d == 0:
            d = 1
        p = (p + sgn * d) % len(stream)
    return out


def cumwalk(stream, step, start, maxlen=400, skipF=True):
    """family B: p advances by the running sum of f over runes visited"""
    out, seen, p, acc = [], set(), start, 0
    while len(out) < maxlen:
        if p in seen:
            break
        seen.add(p)
        v = int(stream[p])
        if not (skipF and v == 0):
            out.append(v)
        acc += step(v)
        if acc % len(stream) == 0:
            acc += 1
        p = (start + acc) % len(stream)
    return out


def signwalk(stream, stride, start, maxlen=400, mode='parity'):
    """family C: each rune chooses a direction, the stride is fixed"""
    out, seen, p = [], set(), start
    while len(out) < maxlen:
        if p in seen:
            break
        seen.add(p)
        v = int(stream[p])
        out.append(v)
        if mode == 'parity':
            d = stride if (v % 2 == 0) else -stride
        else:
            d = stride if v < N // 2 else -stride
        p = (p + d) % len(stream)
    return out


def sieves(stream):
    """family D: positions chosen by a number-theoretic predicate"""
    n = len(stream)
    out = {}
    s = np.ones(n, bool); s[:2] = False
    for i in range(2, int(n**0.5)+1):
        if s[i]:
            s[i*i::i] = False
    pr = np.flatnonzero(s)
    out['prime positions'] = stream[pr]
    out['prime-index runes'] = stream[pr[pr < n]]
    fib = []
    a, b = 1, 2
    while a < n:
        fib.append(a); a, b = b, a+b
    out['fibonacci positions'] = stream[np.array(fib)]
    sq = np.array([i*i for i in range(1, int(n**0.5)+1)])
    out['square positions'] = stream[sq[sq < n]]
    for k in (3, 7, 11, 29, 33, 301, 3301 % n, 133, 331):
        if 0 < k < n:
            out['every %d-th' % k] = stream[::k]
    # cumulative gematria sum crossing a prime
    cs = np.cumsum(PRIME[stream])
    out['cumsum-prime hits'] = stream[np.flatnonzero(np.isin(cs % 3301, [0, 1, 2]))] \
        if n else np.array([])
    return out


def run_all(stream, label, report):
    best = (-99.0, '')
    n = 0
    for sname, f in STEPS.items():
        for start in range(0, 64):
            for back in (False, True):
                for skipF in (True, False):
                    s = walk(stream, f, start, back=back, skipF=skipF)
                    sc = score(s); n += 1
                    if sc > best[0]:
                        best = (sc, 'A walk %s start=%d back=%d skipF=%d' %
                                (sname, start, back, skipF), s)
        for start in range(0, 32):
            s = cumwalk(stream, f, start)
            sc = score(s); n += 1
            if sc > best[0]:
                best = (sc, 'B cumwalk %s start=%d' % (sname, start), s)
    for stride in (1, 2, 3, 5, 7, 11, 13, 29, 33, 133, 331):
        for start in range(0, 16):
            for mode in ('parity', 'half'):
                s = signwalk(stream, stride, start, mode=mode)
                sc = score(s); n += 1
                if sc > best[0]:
                    best = (sc, 'C sign stride=%d start=%d %s' % (stride, start, mode), s)
    for k, v in sieves(stream).items():
        sc = score(v); n += 1
        if sc > best[0]:
            best = (sc, 'D sieve %s' % k, v)
    report[label] = dict(readings=n, best=best[0], how=best[1])
    print('%-10s readings %6d   best %8.4f   %s' % (label, n, best[0], best[1]))
    if len(best) > 2:
        print('           %s' % show(best[2]))
    return best


def main():
    rep = {}
    print('ciphertext %d runes\n' % L)
    real = run_all(ct, 'REAL', rep)

    rng = np.random.default_rng(3301)
    nulls = []
    for t in range(6):
        sh = ct.copy()
        rng.shuffle(sh)
        b = run_all(sh, 'null-%d' % t, rep)
        nulls.append(b[0])
    nulls = np.array(nulls)
    print('\nnull best-of-family: mean %.4f  sd %.4f  max %.4f'
          % (nulls.mean(), nulls.std(), nulls.max()))
    print('REAL best %.4f  ->  z = %.2f' %
          (real[0], (real[0] - nulls.mean()) / (nulls.std() + 1e-9)))
    print('English-class at this length is about -11 to -12.')
    rep['summary'] = dict(real_best=real[0], null_mean=float(nulls.mean()),
                          null_sd=float(nulls.std()), null_max=float(nulls.max()))
    json.dump(rep, open(os.path.join(HERE, 'direction_results.json'), 'w'), indent=1)
    print('\nwrote direction_results.json')


if __name__ == '__main__':
    main()
