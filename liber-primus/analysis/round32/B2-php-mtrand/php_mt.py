"""PHP mt_rand engines: canonical MT19937 ("mt") and pre-7.1 broken twist ("php"), PHP 5.x init (php_mt_initialize + php_mt_reload).
php_mt_initialize: s[0]=seed; s[i]=1812433253*(s[i-1]^(s[i-1]>>30))+i.   mt_rand() = tempered_u32 >> 1 (31 bit).
Twist: m ^ (mixBits(u,v)>>1) ^ (-(loBit(X)) & 0x9908b0df); canonical X=v (=s[i+1]); PHP<=7.0 legacy X=u (=s[i]) [the bug].
Reductions (31-bit n = mt_rand()):  "scale": PHP5 RAND_RANGE for mt_rand(0,28) = floor(29*n/2^31) (exact integer form (n*29)>>31);
"mod": n % 29.  Version assumed for the legacy twist: PHP 5.x (<=7.0) default mode == PHP>=7.1 MT_RAND_PHP.
"""
import numpy as np
MASK = 0xFFFFFFFF
N, M = 624, 397

def _tw(m, u, v, legacy):
    y = (u & 0x80000000) | (v & 0x7FFFFFFF)
    return (m ^ (y >> 1) ^ (0x9908B0DF if ((u if legacy else v) & 1) else 0)) & MASK

def stream31(seed, twist, n):
    """Exact scalar mt_rand() 31-bit outputs (n may exceed 624: in-place reload repeats like php_mt_reload)."""
    legacy = twist == "php"
    s = [0] * N; s[0] = int(seed) & MASK
    for i in range(1, N): s[i] = (1812433253 * (s[i - 1] ^ (s[i - 1] >> 30)) + i) & MASK
    out = []
    while len(out) < n:
        for p in range(N - M): s[p] = _tw(s[p + M], s[p], s[p + 1], legacy)
        for p in range(N - M, N - 1): s[p] = _tw(s[p + M - N], s[p], s[p + 1], legacy)
        s[N - 1] = _tw(s[M - 1], s[N - 1], s[0], legacy)
        for y in s:
            y ^= y >> 11; y ^= (y << 7) & 0x9D2C5680; y ^= (y << 15) & 0xEFC60000; y ^= y >> 18
            out.append((y & MASK) >> 1)
    return out[:n]

def red(n31, red_):
    return (n31 * 29) >> 31 if red_ == "scale" else n31 % 29

def ks(seed, twist, red_, n):
    return [red(x, red_) for x in stream31(seed, twist, n)]

def heads_all(seeds, m=16):
    """Vectorised first m 31-bit outputs for all 4 twist cells. seeds uint32-able array. Returns {twist: (m,B) uint32}."""
    s0 = (np.asarray(seeds, dtype=np.uint64) & np.uint64(MASK)).astype(np.uint32)
    need = set(range(m + 1)) | set(range(M, M + m))
    keep = {}; cur = s0.copy(); keep[0] = cur.copy()
    mul = np.uint32(1812433253)
    for i in range(1, M + m):
        cur = mul * (cur ^ (cur >> np.uint32(30))) + np.uint32(i)    # uint32 wraps
        if i in need: keep[i] = cur
    res = {}
    for tw in ("mt", "php"):
        out = np.empty((m, len(s0)), dtype=np.uint32)
        for i in range(m):
            u, v, mm = keep[i], keep[i + 1], keep[i + M]
            y = (u & np.uint32(0x80000000)) | (v & np.uint32(0x7FFFFFFF))
            lo = (v if tw == "mt" else u) & np.uint32(1)
            x = mm ^ (y >> np.uint32(1)) ^ (np.uint32(0x9908B0DF) * lo)
            x ^= x >> np.uint32(11); x ^= (x << np.uint32(7)) & np.uint32(0x9D2C5680)
            x ^= (x << np.uint32(15)) & np.uint32(0xEFC60000); x ^= x >> np.uint32(18)
            out[i] = x >> np.uint32(1)
        res[tw] = out
    return res

def reduce_heads(h31, red_):
    if red_ == "scale": return ((h31.astype(np.uint64) * np.uint64(29)) >> np.uint64(31)).astype(np.int8)
    return (h31 % np.uint32(29)).astype(np.int8)

def selftest():
    import os, sys, importlib.util
    r = {}
    r["canonical_seed1_first_u32_is_1791095845"] = stream31(1, "mt", 1)[0] == 1791095845 >> 1
    r["canonical_vs_numpy_MT19937_raw"] = None
    try:
        bg = np.random.MT19937(); bg._legacy_seeding(12345)
        raw = [int(bg.random_raw()) >> 1 for _ in range(700)]
        r["canonical_vs_numpy_MT19937_raw"] = raw == stream31(12345, "mt", 700)
    except Exception as e: r["canonical_vs_numpy_MT19937_raw"] = "n/a %r" % e
    r["legacy_seed1_first"] = stream31(1, "php", 1)[0]
    r["legacy_seed1_first_equals_remembered_1244335972"] = stream31(1, "php", 1)[0] == 1244335972
    here = os.path.dirname(os.path.abspath(__file__))
    g = os.path.abspath(os.path.join(here, "..", "..", "round28", "L4", "gen28.py"))
    try:
        sp = importlib.util.spec_from_file_location("gen28", g); G = importlib.util.module_from_spec(sp); sp.loader.exec_module(G)
        ok = True
        for sd in (1, 777, 3301, 1325734783, 4294967295):
            for tw in ("mt", "php"):
                for rd in ("scale", "mod"):
                    ok &= ks(sd, tw, rd, 1100) == G.php_stream(sd, tw, rd, 1100)
        r["matches_round28_L4_gen28_(validated_vs_real_php_8.5.4)"] = bool(ok)
    except Exception as e: r["gen28"] = "n/a %r" % e
    sd = np.array([1, 777, 3301, 1325734783, 4294967295, 0, 2**31], dtype=np.uint64); H = heads_all(sd)
    ok = True
    for tw in ("mt", "php"):
        for i, s in enumerate(sd): ok &= [int(x) for x in H[tw][:, i]] == stream31(int(s), tw, 16)
    r["vectorised_heads_equal_scalar"] = bool(ok)
    return r

if __name__ == "__main__":
    import json; print(json.dumps(selftest(), indent=1))
