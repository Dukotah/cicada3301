"""R40 B1 generators: bash 3.2 / 4.0 / 4.1 / 5.1 $RANDOM, transcribed from the release tarballs.
Sources (GNU release tarballs, https://ftp.gnu.org/gnu/bash/bash-<v>.tar.gz):
 3.2 variables.c: rseed unsigned long; brand(): rseed = rseed*1103515245+12345; return (rseed>>16)&32767;
     init: sbrand(dollar_dollar_pid + shell_start_time)  [initialize_shell_variables]; sbrand sets last_random_value=0;
     get_random_number(): do rv=brand(); while(rv==last_random_value).
 4.0 / 4.1 variables.c (RANDOM code textually IDENTICAL between the two): brand(): `long h,l; if (rseed==0) seedrand();
     h=rseed/127773; l=rseed%127773; rseed=16807*l-2836*h;` (the `if (rseed<0) rseed+=0x7fffffff` is #if 0) return rseed&32767;
     seedrand(): gettimeofday; sbrand(tv_sec ^ tv_usec ^ getpid()); called at init and again in a new subshell.
 4.2 differs ONLY in the zero branch (`if (rseed==0) rseed=123459876;`, deterministic).
 5.1 lib/sh/random.c: intrand32() 32-bit Lehmer with Schrage (u_bits32_t rseed, signed h,l,t, +0x7fffffff correction, 0 -> 123459876);
     brand(): ret=(shell_compatibility_level>50)? (rseed>>16)^(rseed&65535) : rseed; return ret&32767;
     seedrand(): genseed() = tv_sec ^ tv_usec ^ getpid() ^ getppid() ^ current_user.uid ^ (u32)(address of seedrand).
get_random_number() anti-repeat loop (rv==last_random_value, last=0 after sbrand) is identical in all versions.
"""
import numpy as np
M64 = (1 << 64) - 1; M32 = (1 << 32) - 1
SEC0, SEC1 = 1325376000, 1401580800
PID_MAX = 32768
NONDET = -1
ZERO_EVENTS = {}          # variant -> count of state-0 entries seen by the vector head generator (4.0/4.1 only)

VARIANTS = ("bash3.2", "bash4.0", "bash4.1", "bash4.1_i32", "bash4.0_i32", "bash5.1")

# ---------------- orbits
def pref_range(v):
    if v in ("bash4.0", "bash4.1", "bash4.0_i32", "bash4.1_i32"):
        return list(range(SEC0 >> 20, (SEC1 >> 20) + 1))                    # 74
    if v == "bash5.1":
        base = set(p ^ x for p in range(SEC0 >> 20, (SEC1 >> 20) + 1) for x in range(8))
        return sorted(base)                                                   # 1264..1343 = 80
    return None

def orbit_chunks(v, SUB=1 << 18):
    """List of (lo, hi) seed ranges (half-open) of width <= SUB covering the version's enumerated orbit."""
    if v == "bash3.2":
        lo, hi = SEC0 + 1, SEC1 + PID_MAX + 1
        return [(a, min(a + SUB, hi)) for a in range(lo, hi, SUB)]
    P = pref_range(v)
    if v == "bash5.1":      # prior-weighted order: non-PIE text address >>20 is 4 or 5 (0x400000-0x5fffff) -> x=4 image first, then x=5, then rest
        base = list(range(SEC0 >> 20, (SEC1 >> 20) + 1)); g4 = [p ^ 4 for p in base]
        g5 = [p ^ 5 for p in base if (p ^ 5) not in g4]; rest = [p for p in P if p not in g4 and p not in g5]
        P = g4 + g5 + rest
    return [((p << 20) | s, ((p << 20) | s) + SUB) for p in P for s in range(0, 1 << 20, SUB)]

def orbit_size(v):
    return sum(b - a for a, b in orbit_chunks(v))

def sample_seed(v, rng):
    if v == "bash3.2":
        return rng.randrange(SEC0 + 1, SEC1 + PID_MAX + 1)
    return (rng.choice(pref_range(v)) << 20) | rng.randrange(1 << 20)

# ---------------- scalar brand functions: (state) -> (raw15, new_state)
def brand_32(s):
    s = (s * 1103515245 + 12345) & M64
    return (s >> 16) & 32767, s

def _park_ul(s, mask, zero):
    if s == 0:
        if zero is None: return NONDET, 0
        s = zero
    h = s // 127773; l = s % 127773
    s = (16807 * l - 2836 * h) & mask
    return s & 32767, s

def brand_40(s): return _park_ul(s, M64, None)
def brand_40_i32(s): return _park_ul(s, M32, None)

def brand_51(s):
    if s == 0: s = 123459876
    h = s // 127773; l = s - 127773 * h
    t = 16807 * l - 2836 * h
    if t < 0: t += 0x7fffffff
    s = t & M32
    return ((s >> 16) ^ (s & 65535)) & 32767, s

BRANDS = {"bash3.2": brand_32, "bash4.0": brand_40, "bash4.1": brand_40, "bash4.0_i32": brand_40_i32, "bash4.1_i32": brand_40_i32, "bash5.1": brand_51}
MASK = {"bash3.2": M64, "bash4.0": M64, "bash4.1": M64, "bash4.0_i32": M32, "bash4.1_i32": M32, "bash5.1": M32}
TRUNC = {}   # variant -> count of ks() calls that hit state 0 (nondeterministic tail filled with the 4.2 constant)

def raws(seed, n, v, fill_zero=True):
    bf = BRANDS[v]; s = int(seed) & MASK[v]; last = 0; out = []; hit = False
    while len(out) < n:
        rv, s = bf(s)
        if rv == NONDET:
            hit = True
            if not fill_zero: return out, True
            s = 123459876; continue          # tail is NONDETERMINISTIC in the real shell; filler flagged via TRUNC
        if rv == last: continue
        last = rv; out.append(rv)
    return out, hit

def ks(seed, v, n=1024):
    out, hit = raws(seed, n, v)
    if hit: TRUNC[v] = TRUNC.get(v, 0) + 1
    return [r % 29 for r in out]

# ---------------- vectorised first-m heads (anti-repeat NOT applied, as in R32/R37 heads)
def heads(seeds, m, variant):
    s = seeds.astype(np.uint64)
    out = np.empty((m, len(s)), dtype=np.int8)
    if variant == "bash3.2":
        for t in range(m):
            s = s * np.uint64(1103515245) + np.uint64(12345)
            out[t] = ((s >> np.uint64(16)) & np.uint64(32767)) % np.uint64(29)
        return out
    if variant in ("bash4.0", "bash4.1", "bash4.0_i32", "bash4.1_i32"):
        i32 = variant.endswith("_i32")
        if i32: s = s & np.uint64(M32)
        for t in range(m):
            z = s == 0
            if z.any():
                ZERO_EVENTS[variant] = ZERO_EVENTS.get(variant, 0) + int(z.sum())
                s = np.where(z, np.uint64(123459876), s)
            h = s // np.uint64(127773); l = s - h * np.uint64(127773)
            s = np.uint64(16807) * l - np.uint64(2836) * h
            if i32: s = s & np.uint64(M32)
            out[t] = (s & np.uint64(32767)) % np.uint64(29)
        return out
    if variant == "bash5.1":
        s = s & np.uint64(M32)
        for t in range(m):
            s = np.where(s == 0, np.uint64(123459876), s)
            h = s // np.uint64(127773); l = s - h * np.uint64(127773)
            t_ = (np.uint64(16807) * l).astype(np.int64) - (np.uint64(2836) * h).astype(np.int64)
            t_ = np.where(t_ < 0, t_ + 0x7fffffff, t_)
            s = t_.astype(np.uint64) & np.uint64(M32)
            out[t] = (((s >> np.uint64(16)) ^ (s & np.uint64(65535))) & np.uint64(32767)) % np.uint64(29)
        return out
    raise KeyError(variant)
