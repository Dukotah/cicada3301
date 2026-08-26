"""Round 19 / G1 (b) -- glibc random() / rand() / *rand48.

L1's prior (round18/L1-toolchain/RESULTS.md section 6.2 **row 1, x3**, the top-ranked
family): F6/F7 -- 46/46 curated 3301 PGP messages, 2012 through 2014, carry
`Version: GnuPG v1.4.11 (GNU/Linux)`, and 1.4.11 is exactly the Ubuntu 11.04-12.04 LTS
package -- fix glibc-on-Linux as the runtime.  random()'s TYPE_3 additive-feedback
generator is what a 2012 Linux C program gets for free.

Prior coverage (read `coverage`, not `status`, per doctrine R7):
  * LEDGER B-21 / round10/L5-seed32/CENSUS.md section A: Round 8 swept glibc random()
    generators 0,1,2 over **2011-2015 unix-seconds only** (~1.26e8 of 2**32 = ~2.9%),
    plus a partial 0..2**32 extension in L5; generator 0 has **no DONE line**
    (LEDGER B-01: "the full 32-bit sweep is 2/10 complete ... gen=0 is absent").
  * CENSUS section B generators 10/11 covered drand48 via Perl and lrand48, again over
    2011-2015 unix-seconds only.
  * All of it was RIGID-decoded (B-21 coverage field), which D3 showed manufactures a
    false negative on a key-skip cipher.
So: the generator family is implemented but its seed space is ~3% covered and its
decodes were taken with a decoder now known to be wrong for this cipher.

Everything below is validated byte-for-byte against the running system glibc through
ref_glibc.c.  glibc's random() has been bit-stable since glibc 1.x (stdlib/random_r.c
is unchanged in substance from 1995 to 2.43), so today's libc is a valid reference for
2012's; that claim is itself checked in RESULTS.md section 4.
"""

M32 = (1 << 32) - 1
INT32_MAX = 0x7FFFFFFF


def _s32(x):
    x &= M32
    return x - (1 << 32) if x >> 31 else x


# --------------------------------------------------------------- random() / rand()
# glibc stdlib/random_r.c.  TYPE_0..TYPE_4 selected by the initstate() buffer size.
#   size  8 -> TYPE_0 deg  0 sep 0   (a bare LCG)
#   size 32 -> TYPE_1 deg  7 sep 3
#   size 64 -> TYPE_2 deg 15 sep 1
#   size128 -> TYPE_3 deg 31 sep 3   <-- the DEFAULT, what srandom()/rand() give you
#   size256 -> TYPE_4 deg 63 sep 1
_TYPES = {
    "initstate8":   (0, 0),
    "initstate32":  (7, 3),
    "initstate64":  (15, 1),
    "initstate128": (31, 3),
    "initstate256": (63, 1),
}
RMAX_RANDOM = INT32_MAX          # random() returns 0..2**31-1


def _srandom_state(seed, deg):
    """glibc __srandom_r: state[0] = seed (0 -> 1); then the Schrage-seeded fill."""
    seed = seed & M32
    if seed == 0:
        seed = 1
    r = [0] * deg
    r[0] = _s32(seed)
    word = r[0]
    for i in range(1, deg):
        # int32_t hi = word / 127773;  int32_t lo = word % 127773;   (C truncating div)
        hi = int(word / 127773) if word >= 0 else -int(-word // 127773)
        lo = word - hi * 127773
        word = 16807 * lo - 2836 * hi
        if word < 0:
            word += INT32_MAX
        r[i] = word
    return r


def random_seq(seed, n, variant="initstate128"):
    """The exact output of srandom(seed) followed by n calls to random().

    This is glibc __random_r's circular buffer, written literally rather than as a
    linear recurrence -- the linear form with the obvious index mapping does NOT
    reproduce it, which is precisely the sort of thing the validation gate exists to
    catch (see validate.py / validation.json).

        val = *fptr += (uint32_t) *rptr;  *result = val >> 1;
        ++fptr; if (fptr >= end) { fptr = state; ++rptr; }
        else    { ++rptr; if (rptr >= end) rptr = state; }
    """
    deg, sep = _TYPES[variant]
    if deg == 0:                                    # TYPE_0: a plain LCG, no discard
        s = seed & M32
        if s == 0:
            s = 1
        out = []
        for _ in range(n):
            s = ((s * 1103515245) + 12345) & INT32_MAX
            out.append(s)
        return out

    st = [x & M32 for x in _srandom_state(seed, deg)]
    f, rp = sep, 0
    discard = 10 * deg                              # glibc: kc *= 10; discard kc draws
    res = []
    for _ in range(discard + n):
        st[f] = (st[f] + st[rp]) & M32
        res.append(st[f] >> 1)
        f += 1
        if f >= deg:
            f = 0
            rp += 1
        else:
            rp += 1
            if rp >= deg:
                rp = 0
    return res[discard:]


def raws_random(seed, n, variant="initstate128"):
    return random_seq(seed, n, variant)


# ----------------------------------------------------------------------- *rand48
_A48 = 0x5DEECE66D
_C48 = 0xB
M48 = (1 << 48) - 1
RMAX_LRAND48 = INT32_MAX             # lrand48 returns 0..2**31-1
RMAX_MRAND48 = M32                   # mrand48 as a raw 32-bit pattern


def _srand48(seed):
    return ((seed & M32) << 16) | 0x330E


def _next48(x):
    return (_A48 * x + _C48) & M48


def lrand48_seq(seed, n):
    x = _srand48(seed)
    out = []
    for _ in range(n):
        x = _next48(x)
        out.append(x >> 17)
    return out


def mrand48_seq(seed, n):
    """Raw 32-bit pattern (x >> 16).  mrand48() returns that reinterpreted as int32;
    reductions here consume the unsigned pattern, which is the same bits."""
    x = _srand48(seed)
    out = []
    for _ in range(n):
        x = _next48(x)
        out.append((x >> 16) & M32)
    return out


def drand48_x2p53_seq(seed, n):
    """floor(drand48() * 2**53).  drand48() is exactly x / 2**48, so this is x * 32 --
    an exact integer comparison, no floating-point fuzz in the validation."""
    x = _srand48(seed)
    out = []
    for _ in range(n):
        x = _next48(x)
        out.append(x * 32)
    return out


def drand48_scaled29(seed, n):
    """`(int)(drand48() * 29)` -- the idiom a C author actually writes.  Exact:
    floor(29 * x / 2**48)."""
    x = _srand48(seed)
    out = []
    for _ in range(n):
        x = _next48(x)
        out.append((29 * x) >> 48)
    return out


# ------------------------------------------------------------------- registry
GENERATORS = {
    # name              -> (fn(seed, n), inclusive rmax)
    "glibc_random":      (lambda s, n: random_seq(s, n, "initstate128"), RMAX_RANDOM),
    "glibc_rand":        (lambda s, n: random_seq(s, n, "initstate128"), RMAX_RANDOM),
    "glibc_initstate8":  (lambda s, n: random_seq(s, n, "initstate8"), RMAX_RANDOM),
    "glibc_initstate32": (lambda s, n: random_seq(s, n, "initstate32"), RMAX_RANDOM),
    "glibc_initstate64": (lambda s, n: random_seq(s, n, "initstate64"), RMAX_RANDOM),
    "glibc_initstate256": (lambda s, n: random_seq(s, n, "initstate256"), RMAX_RANDOM),
    "lrand48":           (lrand48_seq, RMAX_LRAND48),
    "mrand48":           (mrand48_seq, RMAX_MRAND48),
    "drand48_x2p53":     (drand48_x2p53_seq, (1 << 53) - 1),
}

# glibc_rand IS glibc_random on Linux -- kept as a separate name because a sweep row
# must say which source line the author wrote, and validated separately in validate.py
# so the identity is a MEASUREMENT, not an assumption.
ERA_CORRECT = ("glibc_random", "lrand48", "drand48_x2p53")


if __name__ == "__main__":
    print("random(3301)[:8]  =", random_seq(3301, 8))
    print("lrand48(3301)[:8] =", lrand48_seq(3301, 8))
