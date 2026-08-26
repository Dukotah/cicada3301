"""Round 19 / G1 (a) -- bash `$RANDOM`.

L1's prior (round18/L1-toolchain/RESULTS.md section 6.2 row 4, x2, "never swept"):
F8/F9 show defaults-only CLI usage, so the author reached for the shell first;
F6/F7 pin the box to Ubuntu 11.04-12.04, whose /bin/bash is **4.2**.

Every function below is transcribed from the released GNU bash source
(https://ftp.gnu.org/gnu/bash/, see ref_bash.c for the file/line map) and is
validated byte-for-byte against C compiled from those same sources, and against a
running bash for the versions actually available on this machine.

THE STRUCTURAL FACT THAT MAKES THIS LANE CHEAP
----------------------------------------------
brand() is a pure one-step state map s -> f(s), with the returned 15-bit value a
function of s alone.  RANDOM=<seed> sets s = seed directly (assign_random ->
sbrand -> rseed = strtoul(value, NULL, 10)).  Therefore:

    the keystream for seed s is the ONE master orbit of f, entered at s.

For bash 5.0/5.1 (rseed is u_bits32_t and the negative correction is enabled) f is the
Lehmer generator mod 2**31-1, which has a SINGLE cycle of length 2**31-2 covering every
nonzero state.  So all 2**31-2 nonzero seeds give windows into ONE sequence, and the
sweep is a sliding window over a 2.1e9-element array, not 2.1e9 independent runs.

For bash 4.2/4.3 (rseed is `unsigned long`, and the `if (rseed < 0) rseed += 0x7fffffff`
correction is compiled out by `#if 0`) the map is NOT Lehmer: a negative Schrage residue
is reinterpreted as a huge unsigned value.  The orbit structure is therefore an
empirical question, answered by orbit_report() below rather than asserted.

get_random_number() wraps brand() in
    do rv = brand (); while (rv == last_random_value);
-- bash's $RANDOM carries its OWN anti-repeat rejection loop, at 15-bit granularity, and
sbrand() sets last_random_value = 0 so the first draw of a freshly seeded shell can
never be 0.  That loop is reproduced here exactly.  It suppresses only ~1/32768 of
draws, so it does NOT by itself explain LP2's mod-29 doublet deficit -- but it is the
literal "while x == last: redraw" shape Round 17 found machine-applied, sitting in the
standard library of the shell L1 puts on the author's box.  Noted, not overclaimed.

ABI FORK: in bash 3.2-4.3 rseed is `unsigned long` and h,l are `long`, so the arithmetic
width is the ABI's.  An LP64 box and an ILP32 box emit DIFFERENT $RANDOM streams from
the same seed.  Ubuntu 12.04 shipped both; both are covered here.
"""

M64 = (1 << 64) - 1
M32 = (1 << 32) - 1
RMAX = 32767            # $RANDOM is 0..32767 inclusive


def _to_s32(x):
    x &= M32
    return x - (1 << 32) if x >> 31 else x


# ------------------------------------------------------------------ bash 3.2 (LCG)
def brand_32_lp64(s):
    s = (s * 1103515245 + 12345) & M64
    return ((s >> 16) & 32767), s


def brand_32_ilp32(s):
    s = (s * 1103515245 + 12345) & M32
    return ((s >> 16) & 32767), s


# ----------------------------------------------- bash 4.0 / 4.1 (no zero-reseed const)
# MEASURED, not assumed: in 4.0/4.1 `if (rseed == 0) seedrand();` re-seeds from
# gettimeofday() ^ getpid().  State 0 IS reachable -- RANDOM=2147483647 reaches it in
# ONE step -- so a bash-4.0 $RANDOM stream becomes NON-DETERMINISTIC from that point and
# cannot be swept past it.  raws() returns the deterministic prefix; it never fabricates
# the rest.  (bash 4.2 replaced seedrand() here with the constant 123459876, which is
# what makes 4.2 fully deterministic and 4.0/4.1 not.)
NONDET = -1


def brand_40_lp64(s):
    if s == 0:
        return NONDET, 0
    h = s // 127773
    l = s % 127773
    s = (16807 * l - 2836 * h) & M64
    return (s & 32767), s


# ------------------------------------------- bash 4.2 / 4.3 == Ubuntu 11.04-12.04
def brand_42_lp64(s):
    """VERBATIM bash-4.2 variables.c:1236, LP64.  rseed unsigned long, h/l long,
    negative correction compiled out."""
    if s == 0:
        s = 123459876
    h = s // 127773                    # unsigned division; result < 2**63, so h >= 0
    l = s % 127773
    s = (16807 * l - 2836 * h) & M64   # long arithmetic, then stored back unsigned
    return (s & 32767), s


def brand_42_ilp32(s):
    """The same source compiled ILP32: unsigned long == uint32, long == int32.
    No intermediate signed overflow occurs (16807*127772 = 2147053604 < 2**31-1)."""
    if s == 0:
        s = 123459876
    h = s // 127773
    l = s % 127773
    s = (16807 * l - 2836 * h) & M32
    return (s & 32767), s


# ------------------------------------------------------------------------ bash 5.0
def brand_50(s):
    """bash-5.0 variables.c: rseed u_bits32_t, h/l/t bits32_t, correction ENABLED.
    This is the true Lehmer minimal-standard generator."""
    if s == 0:
        s = 123459876
    h = s // 127773
    l = s - 127773 * h
    t = _to_s32(16807 * l - 2836 * h)
    s = (t + 0x7fffffff) if t < 0 else t
    s &= M32
    return (s & 32767), s


# ------------------------------------------------------- bash 5.1 / 5.2 / 5.3 (>5.0)
def brand_51(s):
    """bash-5.1+ lib/sh/random.c: same Lehmer state, but the 15-bit output is folded
    (rseed >> 16) ^ (rseed & 65535) when shell_compatibility_level > 50."""
    if s == 0:
        s = 123459876
    h = s // 127773
    l = s - 127773 * h
    t = _to_s32(16807 * l - 2836 * h)
    s = (t + 0x7fffffff) if t < 0 else t
    s &= M32
    return (((s >> 16) ^ (s & 65535)) & 32767), s


def brand_51_compat50(s):
    """bash 5.1+ run with BASH_COMPAT=5.0 (or `shopt -s compat50`): unfolded output."""
    if s == 0:
        s = 123459876
    h = s // 127773
    l = s - 127773 * h
    t = _to_s32(16807 * l - 2836 * h)
    s = (t + 0x7fffffff) if t < 0 else t
    s &= M32
    return (s & 32767), s


BRANDS = {
    "bash3.2":      brand_32_lp64,
    "bash3.2_i32":  brand_32_ilp32,
    "bash4.0":      brand_40_lp64,
    "bash4.2":      brand_42_lp64,     # <-- the era-correct one (Ubuntu 11.04-12.04)
    "bash4.2_i32":  brand_42_ilp32,
    "bash5.0":      brand_50,
    "bash5.1":      brand_51,
    "bash5.1c50":   brand_51_compat50,
}

ERA_CORRECT = ("bash4.2", "bash4.2_i32")


def _state_mask(variant):
    return M32 if (variant.endswith("_i32") or variant.startswith("bash5")) else M64


# ------------------------------------------------------------- the $RANDOM wrapper
def raws(seed, n, variant="bash4.2", anti_repeat=True):
    """`RANDOM=<seed>; for ...; do echo $RANDOM; done` -- n values, exactly.

    anti_repeat reproduces get_random_number()'s
        do rv = brand (); while (rv == last_random_value);
    with last_random_value initialised to 0 by sbrand().  Set False only to expose the
    bare brand() stream for analysis; a shell never shows you that.
    """
    bf = BRANDS[variant]
    s = seed & _state_mask(variant)
    last = 0
    out = []
    while len(out) < n:
        rv, s = bf(s)
        if rv == NONDET:                 # bash 4.0/4.1 only: state reached 0
            return out                   # deterministic prefix, nothing fabricated
        if anti_repeat and rv == last:
            continue
        last = rv
        out.append(rv)
    return out


def raws_iter(seed, n, variant="bash4.2", anti_repeat=True):
    return iter(raws(seed, n, variant, anti_repeat))


# ------------------------------------------------------------- the sweep interface
def master_orbit(variant="bash4.2", start=1, length=1000):
    """The one sequence every seed is a window into.  Returns brand() outputs with the
    anti-repeat NOT applied -- window() applies it per-window, because a window's head
    depends on last_random_value = 0."""
    bf = BRANDS[variant]
    s = start
    out = []
    while len(out) < length:
        rv, s = bf(s)
        if rv == NONDET:
            break
        out.append(rv)
    return out


def window(master, i, n, anti_repeat=True):
    """The $RANDOM stream a shell whose rseed reached master-state index i would emit.

    Because the anti-repeat test compares against the PREVIOUSLY RETURNED value and
    sbrand() zeroes it, the returned stream is exactly master[i:] with runs of equal
    consecutive values collapsed, plus a leading 0 dropped.  Deletions are therefore
    seed-independent except at the window head -- which is what makes a sliding-window
    sweep valid and reduces a 2**31-seed enumeration from O(2**31 * L) to O(2**31 + L).
    """
    out = []
    last = 0
    j = i
    ln = len(master)
    while len(out) < n and j < ln:
        rv = master[j]
        j += 1
        if anti_repeat and rv == last:
            continue
        last = rv
        out.append(rv)
    return out


def orbit_report(variant="bash4.2", start=1, limit=20_000_000):
    """Measure, do not assert: walk the state map and report cycle structure.
    Used by RESULTS.md to state the true size of the keystream space per variant."""
    bf = BRANDS[variant]
    seen = {}
    s = start
    i = 0
    while i < limit:
        if s in seen:
            return {"variant": variant, "start": start, "tail": seen[s],
                    "cycle": i - seen[s], "states_visited": i, "terminated": True}
        seen[s] = i
        _, s = bf(s)
        i += 1
    return {"variant": variant, "start": start, "terminated": False, "walked": limit}


if __name__ == "__main__":
    import sys
    v = sys.argv[1] if len(sys.argv) > 1 else "bash4.2"
    print(v, raws(3301, 12, v))
