"""ROUND 19 / LANE G2 -- Perl 5.14 `rand`/`srand` keystream generators.

WHAT THIS IS
------------
A byte-exact reimplementation of the pseudo-random number path that a script
running on **Perl 5.14.2 as shipped by Ubuntu 12.04 LTS** would have taken, plus
the reductions to Z_29 that a 2012-era Perl author would plausibly have written.

WHY PERL 5.14 (the prior; doctrine R4 requires a citation)
---------------------------------------------------------
`liber-primus/analysis/round18/L1-toolchain/RESULTS.md` sec.6.2 row 3 ranks
"Perl 5.14 `rand`/`srand` (drand48 under the hood)" at **x2.5**, third of eleven
families, on measured facts F6/F7: **46/46** curated 3301 PGP messages from 2012
through 2014 carry `GnuPG v1.4.11 (GNU/Linux)`, and 1.4.11 is the version Ubuntu
11.04-12.04 LTS shipped.  Perl 5.14.2 is that distribution's *system* Perl.

THE ERA QUESTION, SETTLED FROM SOURCE
-------------------------------------
This box has perl **v5.40.1**, not 5.14.  Rather than assume the behaviour is
unchanged, the 5.14.2 source tarball was fetched and read
(`https://www.cpan.org/src/5.0/perl-5.14.2.tar.gz`, md5
`3306fbaf976dcebdcd49b2ac0be00eb9`, the official upstream digest):

  * `Configure` line ~19280 --

        case "$randfunc" in
        '')  if set drand48 val -f; eval $csym; $val; then
                     dflt="drand48"
                     echo "Good, found drand48()." >&4
             elif set random val -f; ...   dflt="random"
             else                          dflt="rand"

    so on **any glibc host** -- which Ubuntu 12.04 is -- Configure picks
    `drand48` without asking.  It then sets

        drand01="drand48()" ; seedfunc="srand48" ; randbits=48 ; randseedtype=long

  * `config_h.SH` lines 2131-2134 --

        #define Drand01()        $drand01                 -> drand48()
        #define Rand_seed_t      $randseedtype            -> long
        #define seedDrand01(x)   $seedfunc((Rand_seed_t)x) -> srand48((long)x)
        #define RANDBITS         $randbits                -> 48

  * `pp.c` --

        PP(pp_rand)   value = (MAXARG < 1) ? 1.0 : POPn;
                      if (value == 0.0) value = 1.0;
                      if (!PL_srand_called) { seedDrand01((Rand_seed_t)seed()); ... }
                      value *= Drand01();

        PP(pp_srand)  const UV anum = (MAXARG < 1) ? seed() : POPu;
                      (void)seedDrand01((Rand_seed_t)anum);

So Perl 5.14.2/Ubuntu is **literally calling glibc `srand48`/`drand48`**, and
`rand(M)` is exactly `M * drand48()` evaluated in a C `double`
(`perl -V:nvtype` = `double`, `nvsize` = 8, on both the era build and this one).

Perl 5.20 replaced the libc call with Perl's own bundled drand48 so that
sequences would be identical across platforms -- the *same* algorithm.  Lane
gate B below measures that equality instead of asserting it: the installed
perl 5.40.1 `rand()` is compared, to 17 significant digits, against a C program
calling glibc `srand48`/`drand48` directly.  That is the exact function 5.14.2
called, so a pass makes the version difference immaterial for the number stream.

THE ONE REAL 5.14 -> 5.40 DIVERGENCE
------------------------------------
`pp_srand`'s handling of a *non-integer* argument changed.

    5.14.2:  const UV anum = (MAXARG < 1) ? seed() : POPu;
             -- plain SvUV numification.  srand("CICADA3301") == srand(0).

    5.40.1:  grok_number(pv, len, &anum); if (!(flags & IS_NUMBER_IN_UV))
                 { warn "Integer overflow in srand"; anum = UV_MAX; }
             -- measured on this box: srand("CICADA3301") == srand(UV_MAX),
                and srand(-1) == srand(1) (grok_number returns the magnitude).

`srand_arg_to_seed()` implements **both** rules and flags where they differ.
This affects only the *interpretation* of a hit ("the author typed
srand('CICADA3301')"), never the coverage: every one of those coerced values is
reduced mod 2**32 by `srand48` and therefore already lies inside the enumerated
seed space (see below).

WHY THE SPACE IS BOUNDED AT 2**32 -- INCLUDING THE UN-SEEDED CASE
-----------------------------------------------------------------
Two independent facts close the seed space completely:

 1. glibc `srand48_r` keeps only the low 32 bits of its argument:

        buffer->__x[2] = (unsigned short int) (seedval >> 16);
        buffer->__x[1] = (unsigned short int) (seedval & 0xffffl);
        buffer->__x[0] = 0x330e;

    Measured on this box: `srand(4294967297)` and `srand(1)` emit an identical
    stream.  So *any* srand argument -- 64-bit integer, numified string,
    negative, `time`, `time ^ $$` -- folds into 0 .. 2**32-1.

 2. The **auto-seeded** path is 32 bits too.  `util.c: Perl_seed()` in 5.14.2:

        U32 u;
        fd = PerlLIO_open(PERL_RANDOM_DEVICE, 0);   /* "/dev/urandom" */
        if (fd != -1) { PerlLIO_read(fd, (void*)&u, sizeof u); ... if (u) return u; }

    It reads **four bytes** of /dev/urandom into a `U32` and returns it.  The
    fallback (no /dev/urandom) mixes gettimeofday, getpid and two stack
    pointers, also into a `U32`.

    This is the finding that makes the lane worth running.  The single most
    idiomatic thing a 2012 scripter writes --

        perl -e 'print chr(int(rand(29))) for 1..13000'

    with **no `srand` at all** -- does not escape into an unbounded space the
    way `/dev/urandom`-as-a-pad does.  Only 32 bits of entropy ever reach the
    generator.  Unlike Java's 48-bit `setSeed` or Python's millisecond seeds
    (`round10/L5-seed32/CENSUS.md` sec.D), **this family has no residue above
    2**32 at all.**

REDUCTIONS
----------
See `REDUCTIONS` below.  The ranking is by what a 2012 Perl author actually
writes, and rank 1 is not a judgement call: `perlfunc`'s own worked example for
`rand` is `$random = int(rand(10))`, so `int(rand(29))` is *the* idiom.  Note
that `int(rand(29))` is NOT the same object as reducing the raw 48-bit state
mod 29 -- the former is a scaled truncation of the top bits, the latter reads
the low bits, and the two streams share no symbol beyond coincidence.

Run the validation:  python3 validate.py
"""

from __future__ import annotations

import os
import sys

# --------------------------------------------------------------------------
# drand48 core -- glibc-exact
# --------------------------------------------------------------------------

_A = 0x5DEECE66D
_C = 0xB
_M48 = (1 << 48) - 1
_TWO48 = float(1 << 48)

N = 29


class Drand48:
    """glibc `srand48`/`drand48`, which is what Perl 5.14.2 on Ubuntu calls.

    `x` is the 48-bit state *after* the most recent step, i.e. the value the
    matching `drand48()` call returned as `x / 2**48`.
    """

    __slots__ = ("x",)

    def __init__(self, seed: int):
        self.srand48(seed)

    def srand48(self, seed: int) -> None:
        # glibc: __x[2] = seedval >> 16; __x[1] = seedval & 0xffff; __x[0] = 0x330e
        self.x = (((seed & 0xFFFFFFFF) << 16) | 0x330E) & _M48

    def step(self) -> int:
        """Advance and return the raw 48-bit state."""
        self.x = (self.x * _A + _C) & _M48
        return self.x

    def drand48(self) -> float:
        """The C `double` that glibc `drand48()` / Perl 5.14 `Drand01()` returns.

        Exact: `x < 2**48` has at most 48 significant bits and the divisor is a
        power of two, so `x / 2**48` is representable with no rounding.
        """
        return self.step() / _TWO48


# --------------------------------------------------------------------------
# `rand(M)` and `int(rand(M))`
# --------------------------------------------------------------------------

def _int_rand_from_state(x: int, m: int) -> int:
    """`int(rand(M))` for a state `x` already advanced.

    Perl computes `value *= Drand01()` in an NV, which is a C `double` on every
    build in scope (`perl -V:nvtype` == 'double' on Debian/Ubuntu x86_64 for
    both 5.14 and 5.40).  Python floats are the same IEEE-754 binary64 with the
    same round-to-nearest-even, so `float(m) * (x / 2**48)` reproduces the C
    expression bit for bit.

    Where the product is provably exact we take the integer path instead, which
    is both faster and immune to any platform float question:  `x` carries at
    most 48 significant bits, so if `m < 2**5` (or `m` is a power of two) the
    product `m*x` needs at most 53 bits and binary64 holds it exactly, hence
    `int(m * x / 2**48) == (m * x) >> 48`.  `validate.py` asserts the identity
    against the real perl for every `m` this module uses.
    """
    if m <= 32 or (m & (m - 1)) == 0:          # exact-integer regime
        return (m * x) >> 48
    return int(float(m) * (x / _TWO48))        # must mirror the C double


def int_rand_stream(seed: int, m: int, n: int):
    """`srand(seed); int(rand(M)) x n` -- the raw draw sequence."""
    r = Drand48(seed)
    if m <= 32 or (m & (m - 1)) == 0:
        return [(m * r.step()) >> 48 for _ in range(n)]
    return [int(float(m) * (r.step() / _TWO48)) for _ in range(n)]


def raw_state_stream(seed: int, n: int):
    """The raw 48-bit states.  Not reachable from Perl-level code."""
    r = Drand48(seed)
    return [r.step() for _ in range(n)]


# --------------------------------------------------------------------------
# srand() argument coercion -- 5.14 vs 5.40
# --------------------------------------------------------------------------

_UV_MAX = (1 << 64) - 1


def _numify_svuv(arg) -> int:
    """Perl 5.14.2 `POPu` == `SvUV`: leading-numeric prefix, truncate toward
    zero, wrap negatives into the UV range.  Non-numeric -> 0."""
    if isinstance(arg, int):
        return arg & _UV_MAX
    if isinstance(arg, float):
        return int(arg) & _UV_MAX
    s = str(arg).strip()
    # longest leading numeric prefix perl's grok/atof would consume
    i, n = 0, len(s)
    if i < n and s[i] in "+-":
        i += 1
    start_digits = i
    while i < n and s[i].isdigit():
        i += 1
    intpart_end = i
    if i < n and s[i] == ".":
        i += 1
        while i < n and s[i].isdigit():
            i += 1
    if i < n and s[i] in "eE" and i > start_digits:
        j = i + 1
        if j < n and s[j] in "+-":
            j += 1
        if j < n and s[j].isdigit():
            while j < n and s[j].isdigit():
                j += 1
            i = j
    if intpart_end == start_digits and not (start_digits < n and s[start_digits:start_digits + 1] == "."):
        return 0                                   # nothing numeric at all
    try:
        v = int(float(s[:i]))
    except ValueError:
        return 0
    return v & _UV_MAX


def _numify_grok(arg):
    """Perl 5.40 `pp_srand`: grok_number; if the string is not an integer that
    fits a UV, warn and use UV_MAX.  Negative integers yield the MAGNITUDE
    (grok_number reports sign in flags and writes |value| through the pointer).
    Returns (uv, overflowed)."""
    if isinstance(arg, int):
        return (arg if arg >= 0 else -arg) & _UV_MAX, False
    if isinstance(arg, float):
        f = abs(arg)
        return int(f) & _UV_MAX, False
    s = str(arg).strip()
    neg = s.startswith("-")
    body = s[1:] if s[:1] in "+-" else s
    if body.isdigit():
        return int(body) & _UV_MAX, False
    # "3.7" -> grok_number sets NOT_INT but still fills the UV with 3
    if body.count(".") == 1:
        a, b = body.split(".")
        if a.isdigit() and (b.isdigit() or b == ""):
            return int(a or 0) & _UV_MAX, False
    return _UV_MAX, True


def srand_arg_to_seed(arg, era: str = "5.14"):
    """Map a literal `srand(ARG)` argument to the 32-bit drand48 seed.

    Returns (seed32, uv, diverges_from_other_era).
    """
    uv514 = _numify_svuv(arg)
    uv540, _ = _numify_grok(arg)
    uv = uv514 if era == "5.14" else uv540
    return uv & 0xFFFFFFFF, uv, (uv514 & 0xFFFFFFFF) != (uv540 & 0xFFFFFFFF)


# --------------------------------------------------------------------------
# Reductions to Z_29
# --------------------------------------------------------------------------
# `_TRANS` is only needed by the Latin-letter-pad reduction; import lazily so
# this module stays usable (for validation) without the repo on sys.path.

def _latin_to_rune_table():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, "..", "..", "..", ".."))
    sys.path.insert(0, os.path.join(root, "liber-primus", "src"))
    from lp import gematria as gp                       # noqa
    alias = {"V": 1, "K": 5, "Z": 15, "Q": 5}
    tab = []
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        idx = None
        for t, i in gp._TRANS_SORTED:
            if t == c:
                idx = i
                break
        if idx is None:
            idx = alias.get(c)
        if idx is None:
            raise RuntimeError(f"no rune index for Latin {c!r}")
        tab.append(idx)
    return tab


_LAT = None


def _lat():
    global _LAT
    if _LAT is None:
        _LAT = _latin_to_rune_table()
    return _LAT


# Each generator: (seed:int, nsym:int) -> list[int] of length nsym, values 0..28
# The `perl` field is the literal source line the reduction models.

def g_r29(seed, nsym):
    return int_rand_stream(seed, 29, nsym)


def g_r29_nodup(seed, nsym):
    """`do { $k = int(rand(29)) } while ($k == $last);`

    L1 sec.6.3 item 5 predicts exactly this loop shape from F8 (defaults-only
    tooling) plus Round 17's machine-applied filter finding.  It is a *competing*
    explanation of LP2's suppressed doublet rate to the repo's encipher-time
    key-skip model, and is flagged to I1 as such.
    """
    r = Drand48(seed)
    out, last = [], -1
    while len(out) < nsym:
        k = (29 * r.step()) >> 48
        if k != last:
            out.append(k)
            last = k
    return out


def g_r32_rej(seed, nsym):
    """`do { $k = int(rand(32)) } while ($k > 28);` -- the unbiased author."""
    r = Drand48(seed)
    out = []
    while len(out) < nsym:
        k = (32 * r.step()) >> 48
        if k < 29:
            out.append(k)
    return out


def g_r256_mod(seed, nsym):
    return [v % 29 for v in int_rand_stream(seed, 256, nsym)]


def g_r2p32_mod(seed, nsym):
    return [v % 29 for v in int_rand_stream(seed, 1 << 32, nsym)]


def g_r255_mod(seed, nsym):
    return [v % 29 for v in int_rand_stream(seed, 255, nsym)]


def g_r100_mod(seed, nsym):
    return [v % 29 for v in int_rand_stream(seed, 100, nsym)]


def g_r1000_mod(seed, nsym):
    return [v % 29 for v in int_rand_stream(seed, 1000, nsym)]


def g_r26_lat(seed, nsym):
    """`chr(65 + int(rand(26)))` -- a LETTER pad, then read as a running key
    through the repo's canonical Latin->futhorc map (`skipdecode.eng_to_idx`)."""
    t = _lat()
    return [t[v] for v in int_rand_stream(seed, 26, nsym)]


# --- not reachable from Perl; carried only for de-duplication accounting -----

def g_raw48_mod(seed, nsym):
    """`state % 29`.  Perl never exposes the 48-bit state, so this models a C
    author using `srand48`/`erand48` directly, not a Perl author."""
    return [v % 29 for v in raw_state_stream(seed, nsym)]


def g_lrand48_mod(seed, nsym):
    """`srand48(S); lrand48() % 29` -- the 31 high bits.  This is CENSUS
    generator 11, already swept in `round10/L5-seed32` at RIGID alignment."""
    return [(v >> 17) % 29 for v in raw_state_stream(seed, nsym)]


REDUCTIONS = {
    # name          fn              rank  perl_reachable  source line
    "r29":        (g_r29,        1, True,  "int(rand(29))"),
    "r29_nodup":  (g_r29_nodup,  2, True,  "do { $k = int(rand(29)) } while ($k == $last)"),
    "r32_rej":    (g_r32_rej,    3, True,  "do { $k = int(rand(32)) } while ($k > 28)"),
    "r256_mod":   (g_r256_mod,   4, True,  "int(rand(256)) % 29"),
    "r2p32_mod":  (g_r2p32_mod,  5, True,  "int(rand(2**32)) % 29"),
    "r255_mod":   (g_r255_mod,   6, True,  "int(rand(255)) % 29"),
    "r100_mod":   (g_r100_mod,   7, True,  "int(rand(100)) % 29"),
    "r1000_mod":  (g_r1000_mod,  8, True,  "int(rand(1000)) % 29"),
    "r26_lat":    (g_r26_lat,    9, True,  "chr(65 + int(rand(26)))"),
    "raw48_mod":  (g_raw48_mod, 10, False, "C only: erand48 state % 29"),
    "lrand48_mod":(g_lrand48_mod,11, False, "C only: lrand48() % 29  [CENSUS gen 11]"),
}

PERL_REACHABLE = [k for k, v in REDUCTIONS.items() if v[2]]
RED_NAMES = list(REDUCTIONS)


# --------------------------------------------------------------------------
# Keystream production interface -- mirrors round13/B04/ks.py so Phase 2 can
# drop this in beside `ks.make_ks` without a shim.
# --------------------------------------------------------------------------

def make_ks(red: str, seed: int, nsym: int):
    """Return exactly `nsym` keystream symbols in Z_29.

    Signature deliberately parallels `round13/B04/ks.py: make_ks(gen, red, seed,
    nsym)` minus the `gen` axis, because in this family the generator IS
    drand48 and the only axis is the reduction.
    """
    return REDUCTIONS[red][0](int(seed) & 0xFFFFFFFF, nsym)


def make_ks_block(red: str, seeds, nsym: int):
    """Keystreams for a block of seeds.  Kept simple and sequential: the beam
    decoder downstream costs ~10^4 x more per decode than generation, so
    vectorising here buys nothing measurable (see READY.md sec.4)."""
    return [make_ks(red, s, nsym) for s in seeds]


# Era-plausible explicit seed forms, for reporting a hit in the author's own
# terms.  NONE of these widen the space -- every one lands inside 0..2**32-1.
ERA_SEED_FORMS = {
    "srand(time)":                "unix seconds; 2011-01-01..2015-01-01 = 1293840000..1420070400",
    "srand($$)":                  "pid; 1..32768 on Linux 2.6/3.x default pid_max",
    "srand(time ^ $$)":           "perlfunc's own documented historical idiom; xors <=15 bits of time",
    "srand(time ^ ($$+($$<<15)))":"perlfunc's second documented idiom; xors <=30 bits of time",
    "srand(<literal int>)":       "3301, 1033, 761, 845145127, 29, ...",
    "srand(<string>)":            "numified; see srand_arg_to_seed (5.14 rule: non-numeric -> 0)",
    "<no srand at all>":          "Perl_seed(): 4 bytes of /dev/urandom into a U32 -- uniform on 0..2**32-1",
}


if __name__ == "__main__":
    for name, (fn, rank, reachable, src) in REDUCTIONS.items():
        ks = fn(3301, 16)
        mark = " " if reachable else "*"
        print(f"{mark}{rank:2d} {name:12s} {str(ks):48s}  {src}")
    print("\n* = not reachable from Perl-level code")
