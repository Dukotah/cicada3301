#!/usr/bin/env python3
"""
ROUND 19 / LANE G3 — Python 2.7 `random.seed(<string>)` generator.

A byte-exact Python-3 reimplementation of CPython **2.7**'s seeding + Mersenne
Twister, so that a 2026 sweep can produce the rune streams a 2012 author's
`python2.7` script would actually have produced.

WHY THIS FILE EXISTS
--------------------
Python 2 and Python 3 seed MT19937 from a string by completely different routes:

    Python 2.7   Modules/_randommodule.c : random_seed()
                 -> not int/long?  n = (unsigned long) PyObject_Hash(arg)
                 -> split n into 32-bit chunks (from the right)
                 -> init_by_array(key, keyused)
                 => a `str` collapses to ONE `long`: <= 2 key words on amd64,
                    exactly 1 key word on i386.

    Python 3.x   Lib/random.py : Random.seed(a, version=2)
                 -> a = int.from_bytes(a.encode() + sha512(a.encode()).digest(), 'big')
                 -> super().seed(a) -> init_by_array over >= 18 key words
                 => >= 576 bits of key material, and (3.3+) a randomised
                    `hash()` that never enters the path at all.

`liber-primus/analysis/seed_sweep/string_seeds.py` (Round 8) ran the Python-3
path. `liber-primus/analysis/round13/B04/ks.py` contains no Mersenne Twister at
all. So the Python-2 string-seed path is unswept ground.

Source of truth (verbatim algorithms, cited in RESULTS.md):
  * CPython 2.7  Modules/_randommodule.c   random_seed, init_genrand,
                 init_by_array, genrand_int32, random_random, random_getrandbits,
                 random_jumpahead
  * CPython 2.7  Objects/stringobject.c    string_hash
  * CPython 2.7  Objects/object.c          _Py_HashDouble
  * CPython 2.7  Lib/random.py             Random.seed, randrange, randint,
                 choice, shuffle

Validated against real CPython 2.7.3 (Ubuntu 12.04 package, GCC 4.6.3) and real
CPython 2.7.18 — see `validation.json`.

This module SCORES NOTHING. It emits keystreams. Round 19 Phase 0 owns the
decoder (I1) and the adjudicator (I2); lane G3 holds at the scoring boundary.

CLI
---
    python3 gen_py27.py --selftest
    python3 gen_py27.py --vectors  out.json  [--n 64]
    python3 gen_py27.py --emit  --seed CICADA3301 --mode random29 --n 40
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys

# ---------------------------------------------------------------- MT19937 core
# Verbatim from CPython 2.7 Modules/_randommodule.c (which is verbatim Nishimura
# & Matsumoto 2002 with the globals moved into a struct).

_N = 624
_M = 397
_MATRIX_A = 0x9908B0DF
_UPPER_MASK = 0x80000000
_LOWER_MASK = 0x7FFFFFFF
_MASK32 = 0xFFFFFFFF


class MT19937:
    """CPython 2.7's `_random.Random` state machine."""

    __slots__ = ("mt", "index")

    def __init__(self):
        self.mt = [0] * _N
        self.index = _N + 1

    # ---- init_genrand(unsigned long s)
    def init_genrand(self, s: int) -> None:
        mt = self.mt
        mt[0] = s & _MASK32
        for i in range(1, _N):
            mt[i] = (1812433253 * (mt[i - 1] ^ (mt[i - 1] >> 30)) + i) & _MASK32
        self.index = _N

    # ---- init_by_array(unsigned long init_key[], unsigned long key_length)
    def init_by_array(self, init_key) -> None:
        self.init_genrand(19650218)
        mt = self.mt
        klen = len(init_key)
        i, j = 1, 0
        k = _N if _N > klen else klen
        while k:
            mt[i] = (
                (mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1664525)) + init_key[j] + j
            ) & _MASK32
            i += 1
            j += 1
            if i >= _N:
                mt[0] = mt[_N - 1]
                i = 1
            if j >= klen:
                j = 0
            k -= 1
        k = _N - 1
        while k:
            mt[i] = (
                (mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1566083941)) - i
            ) & _MASK32
            i += 1
            if i >= _N:
                mt[0] = mt[_N - 1]
                i = 1
            k -= 1
        mt[0] = 0x80000000
        self.index = _N

    # ---- genrand_int32(void)
    def genrand_uint32(self) -> int:
        mt = self.mt
        if self.index >= _N:
            for kk in range(_N - _M):
                y = (mt[kk] & _UPPER_MASK) | (mt[kk + 1] & _LOWER_MASK)
                mt[kk] = mt[kk + _M] ^ (y >> 1) ^ (_MATRIX_A if y & 1 else 0)
            for kk in range(_N - _M, _N - 1):
                y = (mt[kk] & _UPPER_MASK) | (mt[kk + 1] & _LOWER_MASK)
                mt[kk] = mt[kk + (_M - _N)] ^ (y >> 1) ^ (_MATRIX_A if y & 1 else 0)
            y = (mt[_N - 1] & _UPPER_MASK) | (mt[0] & _LOWER_MASK)
            mt[_N - 1] = mt[_M - 1] ^ (y >> 1) ^ (_MATRIX_A if y & 1 else 0)
            self.index = 0
        y = mt[self.index]
        self.index += 1
        y ^= y >> 11
        y ^= (y << 7) & 0x9D2C5680
        y ^= (y << 15) & 0xEFC60000
        y ^= y >> 18
        return y & _MASK32

    # ---- random_random(): genrand_res53
    def random(self) -> float:
        a = self.genrand_uint32() >> 5
        b = self.genrand_uint32() >> 6
        return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0)

    # ---- random_getrandbits(k)
    def getrandbits(self, k: int) -> int:
        if k <= 0:
            raise ValueError("number of bits must be greater than zero")
        nbytes = ((k - 1) // 32 + 1) * 4
        out = bytearray(nbytes)
        i = 0
        kk = k
        while i < nbytes:
            r = self.genrand_uint32()
            if kk < 32:
                r >>= 32 - kk
            out[i + 0] = r & 0xFF
            out[i + 1] = (r >> 8) & 0xFF
            out[i + 2] = (r >> 16) & 0xFF
            out[i + 3] = (r >> 24) & 0xFF
            i += 4
            kk -= 32
        return int.from_bytes(bytes(out), "little")

    # ---- random_getstate(): note EVERY element is a Python `long`
    # (`PyLong_FromUnsignedLong`), so its repr() carries an 'L' suffix in 2.x.
    # This matters: Lib/random.py's jumpahead() hashes repr(self.getstate()).
    def py2_getstate_repr(self, version: int = 3) -> str:
        return "(%d, (%s), None)" % (
            version, ", ".join("%dL" % w for w in (list(self.mt) + [self.index])))

    # ---- _random.Random.jumpahead(n)  — the C level [Python 2 ONLY]
    def jumpahead_core(self, n: int, issue14591: bool = True) -> None:
        mt = self.mt
        for i in range(_N - 1, 1, -1):
            j = n % i
            mt[i], mt[j] = mt[j], mt[i]
        if issue14591:
            nonzero = 0
            for i in range(1, _N):
                mt[i] = (mt[i] + i + 1) & _MASK32
                nonzero |= mt[i]
            if nonzero:
                mt[0] = (mt[0] + 1) & _MASK32
            else:
                mt[0] = 0x80000000
        else:
            # pre-issue-14591 (<= 2.7.3): no explicit 32-bit mask, mt[0] included
            for i in range(_N):
                mt[i] = (mt[i] + i + 1) & _MASK32
        self.index = _N

    # ---- random.Random.jumpahead(n) — the *Python* level (Lib/random.py 2.7)
    def jumpahead(self, n: int, issue14591: bool = True,
                  n_is_long: bool = False, version: int = 3) -> None:
        """Lib/random.py (2.7):

            s = repr(n) + repr(self.getstate())
            n = int(_hashlib.new('sha512', s).hexdigest(), 16)
            super(Random, self).jumpahead(n)

        i.e. the **repr of the entire 625-word MT state** is SHA-512'd and the
        digest becomes the shuffle index. Note `repr` of each state word carries
        a trailing `L` (they are `PyLong_FromUnsignedLong` objects).
        This wrapper does not exist in Python 3 — `jumpahead` was removed.
        """
        s = ("%dL" % n if n_is_long else "%d" % n) + self.py2_getstate_repr(version)
        big = int(hashlib.sha512(s.encode("latin-1")).hexdigest(), 16)
        self.jumpahead_core(big, issue14591=issue14591)


# ------------------------------------------------- CPython 2.7 hash() functions

def py2_str_hash(s: bytes, wordsize: int = 64) -> int:
    """CPython 2.7 Objects/stringobject.c : string_hash().

    Returns the *signed* `long` value the interpreter would return, with
    `_Py_HashSecret.prefix == suffix == 0` (the default: hash randomisation is
    off in 2.7 unless `-R` or `PYTHONHASHSEED` is set).

    `wordsize` is `8 * sizeof(long)`: 64 on amd64, 32 on i386.
    """
    mod = 1 << wordsize
    half = 1 << (wordsize - 1)
    n = len(s)
    if n == 0:
        return 0
    x = 0                      # _Py_HashSecret.prefix
    x ^= s[0] << 7
    x &= mod - 1
    for c in s:
        x = ((1000003 * x) & (mod - 1)) ^ c
    x ^= n & (mod - 1)
    x &= mod - 1               # ^ _Py_HashSecret.suffix (== 0)
    signed = x - mod if x >= half else x
    if signed == -1:
        signed = -2
    return signed


def py2_float_hash(v: float, wordsize: int = 64) -> int:
    """CPython 2.7 Objects/object.c : _Py_HashDouble()."""
    mod = 1 << wordsize
    half = 1 << (wordsize - 1)
    long_max = half - 1

    if v != v or v in (float("inf"), float("-inf")):
        # 2.7: inf -> 314159, -inf -> -271828, nan -> 0
        if v != v:
            return 0
        return 314159 if v > 0 else -271828

    fractpart, intpart = math.modf(v)
    if fractpart == 0.0:
        if intpart > long_max / 2 or -intpart > long_max / 2:
            return py2_long_hash(int(intpart), wordsize)
        x = int(intpart)
    else:
        m, expo = math.frexp(v)
        m *= 2147483648.0                       # 2**31
        hipart = int(m)                         # C truncation toward zero
        m = (m - float(hipart)) * 2147483648.0
        x = hipart + int(m) + (expo << 15)
    x &= mod - 1
    signed = x - mod if x >= half else x
    if signed == -1:
        signed = -2
    return signed


def py2_long_hash(v: int, wordsize: int = 64) -> int:
    """CPython 2.7 Objects/longobject.c : long_hash() (needed only by float)."""
    mod = 1 << wordsize
    half = 1 << (wordsize - 1)
    sign = 1
    if v < 0:
        sign = -1
        v = -v
    x = 0
    # 15-bit digits, high to low, with the documented rotate
    digits = []
    t = v
    if t == 0:
        digits = [0]
    while t:
        digits.append(t & 0x7FFF)
        t >>= 15
    for d in reversed(digits):
        x = ((x << 15) & (mod - 1)) | ((x >> (wordsize - 15)) & 0x7FFF)
        x = (x + d) & (mod - 1)
    x = (x * sign) & (mod - 1)
    signed = x - mod if x >= half else x
    if signed == -1:
        signed = -2
    return signed


# --------------------------------------------------------- random_seed dispatch

def _chunks32(n: int):
    """`random_seed`'s 'split n into 32-bit chunks, from the right'."""
    key = []
    while n:
        key.append(n & 0xFFFFFFFF)
        n >>= 32
    if not key:
        key = [0]
    return key


def py27_seed(arg, wordsize: int = 64) -> MT19937:
    """CPython 2.7 `random.seed(arg)` -> a freshly seeded MT19937.

    * int / long  -> abs(arg)                     (identical to Python 3)
    * anything else -> (unsigned long) hash(arg)  (**the Python-2-only path**)
    """
    r = MT19937()
    if isinstance(arg, bool):
        raise TypeError("bool seed is ambiguous; pass an int")
    if isinstance(arg, int):
        n = abs(arg)
    elif isinstance(arg, float):
        h = py2_float_hash(arg, wordsize)
        n = h & ((1 << wordsize) - 1)
    elif isinstance(arg, (bytes, bytearray)):
        h = py2_str_hash(bytes(arg), wordsize)
        n = h & ((1 << wordsize) - 1)
    elif isinstance(arg, str):
        # a Python-2 `str` literal is bytes; latin-1 keeps 1 char == 1 byte
        h = py2_str_hash(arg.encode("latin-1"), wordsize)
        n = h & ((1 << wordsize) - 1)
    elif arg is None:
        raise ValueError("seed(None) is time/urandom seeded — not reproducible")
    else:
        raise TypeError("unsupported seed type %r" % type(arg))
    r.init_by_array(_chunks32(n))
    return r


# ------------------------------------------------------- era-idiomatic reducers
#
# MEASURED FACT (validation V5, real 2.7.3): in Python 2.7
#     randrange(29) == randint(0,28) == choice(range(29)) == int(random()*29)
# are the SAME computation. Lib/random.py's randrange uses
#     `_int(self.random() * istart)` whenever width < 2**53,
# and randint delegates to randrange, and choice is `seq[int(random()*len)]`.
# In Python 3 they are NOT the same (Py3 randrange uses _randbelow ->
# getrandbits with rejection). So a Py3 sweep that listed 'randrange', 'randint'
# and 'choice' as three modes was testing ONE Py3 mode; under Py2 those three
# collapse onto the `random29` mode below.

N_RUNES = 29


def ks_random29(r: MT19937, n: int, k: int = N_RUNES):
    """int(random()*29)  ==  randrange(29) == randint(0,28) == choice(pool).

    Consumes exactly 2 MT words per rune. No rejection.
    """
    return [int(r.random() * k) for _ in range(n)]


def ks_getrandbits5_mod(r: MT19937, n: int, k: int = N_RUNES):
    """getrandbits(5) % 29 — the lazy fold. 1 MT word per rune, biased."""
    return [r.getrandbits(5) % k for _ in range(n)]


def ks_getrandbits5_reject(r: MT19937, n: int, k: int = N_RUNES):
    """getrandbits(5), rejecting 29..31 — the careful fold. Variable draws."""
    out = []
    while len(out) < n:
        v = r.getrandbits(5)
        if v < k:
            out.append(v)
    return out


def ks_shuffle29(r: MT19937, n: int, k: int = N_RUNES):
    """repeated `random.shuffle(range(29))` blocks (Lib/random.py 2.7).

        for i in reversed(xrange(1, len(x))):
            j = int(random() * (i+1)); x[i], x[j] = x[j], x[i]
    """
    out = []
    while len(out) < n:
        pool = list(range(k))
        for i in range(len(pool) - 1, 0, -1):
            j = int(r.random() * (i + 1))
            pool[i], pool[j] = pool[j], pool[i]
        out.extend(pool)
    return out[:n]


REDUCERS = {
    "random29": ks_random29,               # == randrange/randint/choice in 2.7
    "grb5_mod": ks_getrandbits5_mod,
    "grb5_rej": ks_getrandbits5_reject,
    "shuffle29": ks_shuffle29,
}
REDUCER_NAMES = list(REDUCERS)


# --------------------------------------------------------- keystream interface

def keystream(seed, mode: str = "random29", n: int = 260, wordsize: int = 64,
              jump: int | None = None, issue14591: bool = True, k: int = N_RUNES):
    """The one call Phase 2 (S1) uses.

    Parameters
    ----------
    seed       : bytes | str | int | float   — a B-04 dictionary entry, as-is
    mode       : one of REDUCER_NAMES
    n          : number of rune indices to emit
    wordsize   : 64 (amd64 python2.7) or 32 (i386 python2.7)
    jump       : if not None, call Python 2's `jumpahead(jump)` after seeding
    issue14591 : jumpahead variant; True = 2.7.4+, False = pre-14591 (<= 2.7.3)

    Returns a list of ints in [0, k).
    """
    r = py27_seed(seed, wordsize=wordsize)
    if jump is not None:
        r.jumpahead(jump, issue14591=issue14591)
    return REDUCERS[mode](r, n, k)


def py3_keystream(seed, mode: str = "random29", n: int = 260, k: int = N_RUNES):
    """The Python-3 stream for the SAME literal — the thing already swept.

    Present only so that "Py2 != Py3" is a measurement in this repo rather than
    an assertion (validation gate V6).
    """
    import random as _pyrandom

    r = _pyrandom.Random()
    r.seed(seed)
    if mode == "random29":
        return [int(r.random() * k) for _ in range(n)]
    if mode == "grb5_mod":
        return [r.getrandbits(5) % k for _ in range(n)]
    if mode == "grb5_rej":
        out = []
        while len(out) < n:
            v = r.getrandbits(5)
            if v < k:
                out.append(v)
        return out
    if mode == "shuffle29":
        out = []
        while len(out) < n:
            pool = list(range(k))
            r.shuffle(pool)
            out.extend(pool)
        return out[:n]
    raise ValueError(mode)


# ------------------------------------------------------------------- self-test

_SELFTEST_VECTORS = {
    # (seed, mode, wordsize) -> first 16 rune indices, captured from REAL CPython
    # 2.7.3 (Ubuntu 12.04 package python2.7_2.7.3-0ubuntu3.19_amd64, GCC 4.6.3)
    # and reproduced identically by real CPython 2.7.18. Full gate: validation.json.
    ('CICADA3301', 'random29', 64): [0, 17, 2, 22, 9, 22, 27, 11, 10, 13, 27, 11, 28, 5, 26, 22],
    ('CICADA3301', 'grb5_rej', 64): [1, 28, 18, 23, 2, 25, 24, 10, 10, 25, 2, 21, 12, 16, 11, 20],
    ('3301', 'random29', 64): [15, 27, 17, 1, 24, 8, 12, 11, 25, 27, 13, 2, 28, 19, 14, 22],
    ('3301', 'grb5_rej', 64): [17, 26, 16, 19, 26, 1, 11, 27, 3, 9, 14, 13, 0, 12, 8, 27],
    ('DIVINITY', 'random29', 64): [8, 25, 16, 5, 22, 11, 8, 3, 3, 6, 5, 1, 8, 3, 16, 6],
    ('DIVINITY', 'grb5_rej', 64): [9, 11, 28, 18, 18, 6, 28, 24, 6, 12, 9, 18, 4, 20, 3, 17],
    ('THE PRIMES ARE SACRED', 'random29', 64): [13, 8, 19, 27, 28, 24, 26, 25, 11, 21, 4, 17, 17, 27, 10, 14],
    ('THE PRIMES ARE SACRED', 'grb5_rej', 64): [14, 5, 9, 1, 21, 24, 5, 6, 26, 10, 27, 28, 1, 12, 1, 23],
    ('cicada3301', 'random29', 64): [3, 26, 27, 26, 5, 20, 0, 7, 16, 5, 22, 26, 14, 24, 4, 19],
    ('cicada3301', 'grb5_rej', 64): [3, 8, 28, 17, 28, 4, 6, 25, 22, 24, 1, 25, 8, 2, 18, 13],
    ('an end', 'random29', 64): [21, 1, 1, 9, 2, 10, 19, 18, 21, 0, 20, 21, 21, 6, 22, 1],
    ('an end', 'grb5_rej', 64): [23, 6, 1, 26, 1, 13, 10, 3, 24, 11, 28, 21, 27, 20, 19, 23],
    ('ky2khlqdf7qdznac', 'random29', 64): [24, 9, 8, 28, 9, 3, 5, 10, 4, 19, 25, 10, 0, 20, 8, 24],
    ('ky2khlqdf7qdznac', 'grb5_rej', 64): [26, 10, 10, 0, 9, 15, 7, 10, 18, 4, 20, 5, 27, 11, 21, 5],
}


def _selftest() -> int:
    ok = True
    # structural: MT19937 reference vector, init_genrand(5489) first outputs
    r = MT19937()
    r.init_genrand(5489)
    got = [r.genrand_uint32() for _ in range(5)]
    ref = [3499211612, 581869302, 3890346734, 3586334585, 545404204]
    print("MT init_genrand(5489)  :", "PASS" if got == ref else "FAIL %r" % got)
    ok &= got == ref

    # init_by_array([0x123,0x234,0x345,0x456]) -- the mt19937ar test key.
    # Reference values MEASURED from real CPython 2.7.3 (which carries mt19937ar
    # verbatim): seed the int whose 32-bit chunks are that key and read
    # getrandbits(32).  An earlier hand-transcribed literal for element 3 was
    # wrong; this one is measured, not remembered.
    r = MT19937()
    r.init_by_array([0x123, 0x234, 0x345, 0x456])
    got = [r.genrand_uint32() for _ in range(5)]
    ref = [1067595299, 955945823, 477289528, 4107218783, 4228976476]
    print("MT init_by_array(ref)  :", "PASS" if got == ref else "FAIL %r" % got)
    ok &= got == ref

    # known Python 2 hashes (deterministic, hash randomisation off)
    cases64 = {
        b"": 0,
        b"a": 12416037344,
        b"CICADA3301": 8810433306790406628,   # real 2.7.3 amd64
    }
    for s, want in cases64.items():
        h = py2_str_hash(s, 64)
        if want is not None:
            print("py2_str_hash(%r,64)" % s, "PASS" if h == want else "FAIL %d" % h)
            ok &= h == want

    if _SELFTEST_VECTORS:
        for key, ref in _SELFTEST_VECTORS.items():
            seed, mode, ws = key
            got = keystream(seed, mode, len(ref), wordsize=ws)
            print("vector %-24r %-10s ws%d :" % (seed, mode, ws),
                  "PASS" if got == ref else "FAIL")
            ok &= got == ref
    else:
        print("(no pinned 2.7 vectors compiled in; run validate_py27.py)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--seed", default="CICADA3301")
    ap.add_argument("--mode", default="random29", choices=REDUCER_NAMES)
    ap.add_argument("--wordsize", type=int, default=64, choices=(32, 64))
    ap.add_argument("--jump", type=int, default=None)
    ap.add_argument("--n", type=int, default=40)
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.emit:
        ks = keystream(a.seed, a.mode, a.n, wordsize=a.wordsize, jump=a.jump)
        print(json.dumps(ks))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
