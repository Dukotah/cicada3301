"""FRONT C1 -- unbounded multi-rune-history ciphertext/plaintext feedback.

A self-keying (autokey-class) cipher: the key symbol used to decode position i
is a function f of the last k already-known runes (plaintext and/or ciphertext,
and/or their gematria primes). Because the key is derived from already-recovered
material, decoding proceeds strictly LEFT-TO-RIGHT with a seed of length k.

This is a class the OTP proof does NOT bound: Round 11 N1 tested only a SINGLE
running-sum feedback. Here we test genuine k-history feedback for k in 2..6 and a
small basis of natural f, sign +/-, forward + reversed stream, per-segment vs
continuous, with plaintext-history, ciphertext-history, and mixed source.

Decode relation (mod N=29):   p_i = (c_i + sign * k_i) mod N
where k_i = f( history )  and history = last k of the chosen SOURCE stream.

- CT-autokey  : history = ciphertext runes (known up front) -> can decode all at once
- PT-autokey  : history = recovered plaintext runes         -> true left-to-right
- MIX-autokey : history = last k of (ct XOR-ish combined pt)

POSITIVE CONTROL REQUIRED and gated before any real result is trusted.
"""
import os, sys, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "round11"))

from lp import gematria as gp          # noqa
from lp import score as _score         # noqa
import lib_numchannel as nc            # noqa

N = gp.N
Q = _score.default()
PRIMES = gp.PRIMES

# small prime table for "prime-of-sum" f (indexable well beyond needed range)
def _sieve(limit):
    s = [True] * (limit + 1)
    s[0] = s[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if s[i]:
            for j in range(i * i, limit + 1, i):
                s[j] = False
    return [i for i, v in enumerate(s) if v]
_PRIMES_LIST = _sieve(20000)   # >> 6*109

# ---------------------------------------------------------------- f basis
# Each f takes a list of runic INDICES (the k-history, most-recent last) and a
# list of their PRIMES, and returns a key index in 0..N-1.

def f_sum(idx_hist, prime_hist):
    return sum(idx_hist) % N

def f_gemsum(idx_hist, prime_hist):
    return sum(prime_hist) % N

def f_xor(idx_hist, prime_hist):
    x = 0
    for i in idx_hist:
        x ^= i
    return x % N

def f_prime_of_sum(idx_hist, prime_hist):
    # prime indexed by the sum of history indices -> reduce mod N
    s = sum(idx_hist)
    return _PRIMES_LIST[s % len(_PRIMES_LIST)] % N

def f_prime_of_gemsum(idx_hist, prime_hist):
    s = sum(prime_hist)
    return _PRIMES_LIST[s % len(_PRIMES_LIST)] % N

def f_lastdiff(idx_hist, prime_hist):
    # difference of last two history symbols (Beaufort-ish 2-history)
    if len(idx_hist) >= 2:
        return (idx_hist[-1] - idx_hist[-2]) % N
    return idx_hist[-1] % N

def f_alt_sum(idx_hist, prime_hist):
    # alternating signed sum
    s = 0
    for j, i in enumerate(idx_hist):
        s += i if j % 2 == 0 else -i
    return s % N

F_BASIS = {
    "sum": f_sum,
    "gemsum": f_gemsum,
    "xor": f_xor,
    "prime_of_sum": f_prime_of_sum,
    "prime_of_gemsum": f_prime_of_gemsum,
    "lastdiff": f_lastdiff,
    "alt_sum": f_alt_sum,
}

# ---------------------------------------------------------- source selectors
# SOURCE decides which stream the history is drawn from.
#   "ct" : ciphertext runes  (known -> decode deterministically all at once)
#   "pt" : recovered plaintext runes (true autokey, left-to-right)
#   "mix": (c_i + p_i) mod N of the history positions
SOURCES = ("ct", "pt", "mix")


def _prime_hist(idx_hist):
    return [PRIMES[i] for i in idx_hist]


def decode(C, f, k, seed, source="ct", sign=-1):
    """Decode ciphertext indices C with k-history feedback.

    seed: list of k SEED KEY INDICES used for the first k positions (before enough
          history exists). For a fair positive control the same seed is used to
          encipher. We keep the seed small (k values in 0..N-1).
    """
    P = []
    Cn = list(C)
    for i in range(len(Cn)):
        if i < k:
            ki = seed[i] % N
        else:
            if source == "ct":
                hist = Cn[i - k:i]
            elif source == "pt":
                hist = P[i - k:i]
            else:  # mix
                hist = [(Cn[j] + P[j]) % N for j in range(i - k, i)]
            ki = f(hist, _prime_hist(hist))
        p = (Cn[i] + sign * ki) % N
        P.append(p)
    return P


def encipher(P, f, k, seed, source="ct", sign=-1):
    """Inverse of decode: produce ciphertext C so that decode(C,...) == P.

    Relation: p_i = (c_i + sign*k_i) mod N  ->  c_i = (p_i - sign*k_i) mod N.
    For source in {ct, mix} the key depends on ciphertext history so we must
    build c_i left-to-right (each c_i needs earlier c's, which we already have).
    For source == pt the key depends on recovered plaintext = the true P, easy.
    """
    C = []
    for i in range(len(P)):
        if i < k:
            ki = seed[i] % N
        else:
            if source == "ct":
                hist = C[i - k:i]
            elif source == "pt":
                hist = P[i - k:i]
            else:
                hist = [(C[j] + P[j]) % N for j in range(i - k, i)]
            ki = f(hist, _prime_hist(hist))
        c = (P[i] - sign * ki) % N
        C.append(c)
    return C


def idx_to_trans(idxs):
    return "".join(gp.IDX_TO_TRANS[i % N] for i in idxs)


def score_norm(idxs):
    return Q.score_norm(idx_to_trans(idxs))
