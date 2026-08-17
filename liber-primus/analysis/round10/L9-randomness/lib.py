"""L9 — shared: stream loading, controls, and the five 29->bits mappings.

Controls are the point of this lane. ARFILT (uniform-29 pushed through the
DOCUMENTED soft anti-repeat rule) is what separates "trips because of the known
filter" from "trips for an unexplained reason".
"""
import os, sys, hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
CT_BIN = os.path.join(ROOT, 'liber-primus', 'analysis', 'seed_sweep', 'ct.bin')

N_SYM = 29
P_KEEP = 0.18714          # calibrated so p/(p+28) == measured doublet rate


def load_ct():
    """Canonical LP2 pages 0-54 rune indices. Asserts the repo's own invariants."""
    ct = np.frombuffer(open(CT_BIN, 'rb').read(), np.uint8).astype(np.int64)
    assert len(ct) == 12956, len(ct)
    assert ct.min() == 0 and ct.max() == 28
    assert int((ct == 0).sum()) == 458
    return ct


def doublet_rate(a):
    a = np.asarray(a)
    return float((a[1:] == a[:-1]).mean())


def gen_urand(n, rng):
    """Genuine uniform i.i.d. over 29 symbols."""
    return rng.integers(0, N_SYM, size=n, dtype=np.int64)


def gen_arfilt(n, rng, p_keep=P_KEEP):
    """Uniform-29 through the documented SOFT anti-repeat rewrite.

    Candidate equal to the previous OUTPUT rune is kept with probability
    p_keep, otherwise redrawn. Steady-state doublet rate = p/(p+28).
    Vectorised: oversample candidates, walk once.
    """
    out = np.empty(n, np.int64)
    # oversample: expected draws per output = 1 + (1-p)/29 ~ 1.03
    pool = rng.integers(0, N_SYM, size=int(n * 1.30) + 64, dtype=np.int64)
    keep = rng.random(size=len(pool)) < p_keep
    j = 0
    prev = -1
    for i in range(n):
        while True:
            if j >= len(pool):                       # top up (rare)
                pool = np.concatenate([pool, rng.integers(0, N_SYM, size=4096, dtype=np.int64)])
                keep = np.concatenate([keep, rng.random(size=4096) < p_keep])
            c = pool[j]; k = keep[j]; j += 1
            if c != prev or k:
                break
        out[i] = c
        prev = c
    return out


def gen_shuffle(ct, rng):
    a = ct.copy()
    rng.shuffle(a)
    return a


# ----------------------------------------------------------------- mappings
# Each returns a numpy uint8 array of BITS (0/1).

def _bits_from_int(x, nbits):
    b = np.zeros(nbits, np.uint8)
    # little work, big int -> bytes
    nby = (nbits + 7) // 8
    raw = x.to_bytes(nby, 'big')
    arr = np.unpackbits(np.frombuffer(raw, np.uint8))
    return arr[len(arr) - nbits:].astype(np.uint8)


def map_M1(a):
    """Arithmetic / exact big-integer base-29 -> base-2. Entropy preserving."""
    n = len(a)
    nbits = int(np.floor(n * np.log2(N_SYM)))
    # Horner in Python ints. Chunk to keep bigint multiplies sane.
    x = 0
    CH = 512
    pw = N_SYM ** CH
    for s in range(0, n, CH):
        blk = a[s:s + CH]
        v = 0
        for d in blk:
            v = v * N_SYM + int(d)
        x = x * (N_SYM ** len(blk)) + v
    return _bits_from_int(x, nbits)


def map_M2(a):
    """Rejection to 4 bits: keep runes 0-15 (uniform over 16), drop 16-28."""
    k = a[a < 16]
    b = ((k[:, None] >> np.arange(3, -1, -1)) & 1).astype(np.uint8)
    return b.reshape(-1)


def map_M3(a):
    """5-bit fixed width. 29 of 32 codes used -> KNOWN, DECLARED bias."""
    b = ((a[:, None] >> np.arange(4, -1, -1)) & 1).astype(np.uint8)
    return b.reshape(-1)


def map_M4(a):
    """Per-rune parity of the index. p(1) = 14/29 = 0.4828 -> KNOWN bias."""
    return (a & 1).astype(np.uint8)


_PRIMES = None
def _primes():
    global _PRIMES
    if _PRIMES is None:
        sys.path.insert(0, os.path.join(ROOT, 'liber-primus', 'src'))
        from lp.gematria import PRIMES
        _PRIMES = np.array(PRIMES, np.int64)
        assert len(_PRIMES) == 29
    return _PRIMES


def map_M5(a):
    """Gematria-prime residue: prime mod 4 >= 2 (all gematria primes are odd,
    so prime mod 2 is degenerate; mod 4 is the first informative residue)."""
    pr = _primes()
    return ((pr[a] % 4) >= 2).astype(np.uint8)


MAPS = {'M1': map_M1, 'M2': map_M2, 'M3': map_M3, 'M4': map_M4, 'M5': map_M5}
MAP_NOTE = {
    'M1': 'arithmetic base-29->2, entropy preserving, unbiased',
    'M2': 'rejection to 4 bits (runes 0-15), unbiased by construction',
    'M3': '5-bit fixed width, 29/32 codes -- BIAS DECLARED IN ADVANCE',
    'M4': 'per-rune index parity, p(1)=14/29 -- BIAS DECLARED IN ADVANCE',
    'M5': 'gematria prime mod 4 >= 2',
}


def build_streams(n_rep=20, seed=3301):
    """REAL + SHUF + n_rep x URAND + n_rep x ARFILT, all length 12956."""
    ct = load_ct()
    n = len(ct)
    rng = np.random.default_rng(seed)
    out = {'REAL': [ct], 'SHUF': [], 'URAND': [], 'ARFILT': []}
    for _ in range(n_rep):
        out['SHUF'].append(gen_shuffle(ct, rng))
        out['URAND'].append(gen_urand(n, rng))
        out['ARFILT'].append(gen_arfilt(n, rng))
    return out


if __name__ == '__main__':
    ct = load_ct()
    print('REAL   n=%d doublet=%.4f%%' % (len(ct), 100 * doublet_rate(ct)))
    rng = np.random.default_rng(1)
    u = gen_urand(len(ct), rng); f = gen_arfilt(len(ct), rng); s = gen_shuffle(ct, rng)
    print('URAND  doublet=%.4f%%' % (100 * doublet_rate(u)))
    print('ARFILT doublet=%.4f%%  (target %.4f%%)' % (100 * doublet_rate(f), 100 * doublet_rate(ct)))
    print('SHUF   doublet=%.4f%%' % (100 * doublet_rate(s)))
    for k, fn in MAPS.items():
        b = fn(ct)
        print('%s len=%7d  ones=%.5f   %s' % (k, len(b), b.mean(), MAP_NOTE[k]))
