"""Round 11 — the NUMBER CHANNEL instrument (Phase 0).

The whole round follows one literal reading of the signed hints ("the primes are
sacred", "either the words or their numbers", "their numbers are the direction"):
every rune carries a PRIME value, and reduction mod 29 throws its magnitude away.
This module exposes the value channel — prime magnitudes, prime indices, totients,
prime gaps, digit planes — and a shared scorer + null so every Phase-1/2 lens is
measured the same way against the same size-matched surrogate.

Trust anchor: PHASE0-GATE.py must pass (reproduces the 12,956-rune unsolved stream
AND decrypts the solved AN END page via the prime-totient keystream) before any lens
result here is trustworthy. Pure stdlib + the project's own rig.
"""
import os, sys, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))

from lp import gematria as gp, ciphers, score, stats   # noqa: E402
from run_stats import load_pages                        # noqa: E402

N = gp.N                       # 29
PRIMES = gp.PRIMES             # first 29 primes, indexed by rune index (F=idx0=2)
INTERRUPTER_IDX = gp.RUNE_TO_IDX[gp.INTERRUPTER]   # 0  (the F rune)

# ----------------------------------------------------------------- loaders
def segments():
    """All 57 page-segments as lists of rune indices. [:-2]=unsolved 0-54,
    [-2]=AN END (solved, totient keystream), [-1]=PARABLE (plaintext)."""
    return load_pages()

def unsolved():
    """The 12,956-rune unsolved LP2 stream (pages 0-54), flattened."""
    return [i for p in load_pages()[:-2] for i in p]

def anend():
    return load_pages()[-2]

# ------------------------------------------------- value-channel views
# Each takes a list of rune indices and returns a list of INTEGERS in Z
# (NOT reduced mod 29 unless you ask). This is the space our exclusion
# proofs never touched.
def v_prime(idxs):        return [PRIMES[i] for i in idxs]
def v_prime_index(idxs):  return [i + 1 for i in idxs]        # 2 is the 1st prime
def v_totient(idxs):      return [PRIMES[i] - 1 for i in idxs]  # phi(prime)=p-1

def _is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True

def _next_prime(p):
    q = p + 1
    while not _is_prime(q):
        q += 1
    return q

_GAP = {p: _next_prime(p) - p for p in PRIMES}
def v_prime_gap(idxs):    return [_GAP[PRIMES[i]] for i in idxs]

def digit_plane(values, base=10, place=0):
    """Extract one digit place from an integer stream (units place=0)."""
    return [(v // (base ** place)) % base for v in values]

def cumulative(values, mod=None):
    """Running sum of a value stream; optionally reduced mod `mod`."""
    out, s = [], 0
    for v in values:
        s += v
        out.append(s % mod if mod else s)
    return out

# --------------------------------------------------------- cipher helpers
def apply_keystream(idxs, ks, sign=-1):
    """Decrypt (sign=-1) or encrypt (sign=+1) mod 29 with a keystream of ints."""
    return [(c + sign * ks[i]) % N for i, c in enumerate(idxs)]

# ------------------------------------------------------------- scoring
_SC = score.default()
def eng_norm(idxs):
    """Per-quadgram English score of the transliteration. ~-2.2 English, <-4 noise."""
    return _SC.score_norm("".join(gp.IDX_TO_TRANS[i % N] for i in idxs))

def eng_norm_text(s):
    return _SC.score_norm(s)

def summary(idxs):
    return stats.summary(idxs)

# --------------------------------------------------------------- null
def shuffled(seq, seed=3301):
    """Order-destroying, histogram-preserving surrogate (the pre-registered null)."""
    r = random.Random(seed)
    s = list(seq)
    r.shuffle(s)
    return s

def null_band(score_fn, seq, n=200, seed0=3301):
    """Distribution of score_fn over n shuffles; returns (mean, max, all)."""
    vals = []
    for k in range(n):
        vals.append(score_fn(shuffled(seq, seed0 + k)))
    return sum(vals) / len(vals), max(vals), vals
