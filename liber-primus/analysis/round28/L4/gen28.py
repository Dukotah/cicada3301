#!/usr/bin/env python3
"""Round 28 / L4 -- pure-Python reference generators for grind28.

Implements, bit-exactly:
  * PHP mt_rand, BOTH engine modes (MT_RAND_MT19937 canonical twist /
    MT_RAND_PHP pre-7.1 broken twist), seeded php_mt_initialize(seed) =
    init_genrand(seed), output temper(u32) >> 1 (31-bit), reduced to [0,28] by
    (a) RAND_RANGE_BADSCALING: (int)(29.0 * (r / 2147483648.0))   [pre-7.1 mt_rand(0,28)]
    (b) mod29: r % 29                                             [naive idiom]
  * glibc random() TYPE_3 additive-feedback (x^31 + x^3 + 1, 310-discard init),
    output >> 1 (31-bit), reduced by mod29 -- the R19-G3-CORRECTION gen=0 open row.
    glibc rand() is measured IDENTICAL to random() (see receipts/genval.json).

Validation (--selftest): every stream is checked |delta|=0 against the on-box
references: /usr/bin/php 8.5.4 (ref_php.php) and the resident glibc (ref_glibc).
An implementation that cannot reproduce its reference exactly DOES NOT SWEEP
(PREREG Q5a). Py2.7-MT reducers are NOT reimplemented here -- grind28 inherits
them from gen_py27 (R21-L3-validated) via the same code grind27 V1-passed.

This module SCORES NOTHING; it emits keystreams for vector/gate construction.
"""
import json
import os
import subprocess
import sys

MASK32 = 0xFFFFFFFF
HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ PHP MT19937


class PhpMT:
    """php-src ext/random mt19937 engine (state layout + reload verbatim)."""

    N, M = 624, 397

    def __init__(self, seed, mode):
        assert mode in ("mt", "php")
        self.mode = mode
        st = [0] * self.N
        st[0] = seed & MASK32
        for i in range(1, self.N):
            st[i] = (1812433253 * (st[i - 1] ^ (st[i - 1] >> 30)) + i) & MASK32
        self.state = st
        self.count = self.N

    @staticmethod
    def _twist(m, u, v):
        """canonical: mask selected by low bit of v (== mt19937ar / grind27)."""
        y = (u & 0x80000000) | (v & 0x7FFFFFFF)
        return (m ^ (y >> 1) ^ (0x9908B0DF if (v & 1) else 0)) & MASK32

    @staticmethod
    def _twist_php(m, u, v):
        """MT_RAND_PHP: mask selected by low bit of u -- the documented bug."""
        y = (u & 0x80000000) | (v & 0x7FFFFFFF)
        return (m ^ (y >> 1) ^ (0x9908B0DF if (u & 1) else 0)) & MASK32

    def _reload(self):
        st = self.state
        tw = self._twist if self.mode == "mt" else self._twist_php
        N, M = self.N, self.M
        for p in range(N - M):
            st[p] = tw(st[p + M], st[p], st[p + 1])
        for p in range(N - M, N - 1):
            st[p] = tw(st[p + M - N], st[p], st[p + 1])
        st[N - 1] = tw(st[M - 1], st[N - 1], st[0])
        self.count = 0

    def u32(self):
        if self.count >= self.N:
            self._reload()
        y = self.state[self.count]
        self.count += 1
        y ^= y >> 11
        y ^= (y << 7) & 0x9D2C5680
        y ^= (y << 15) & 0xEFC60000
        y ^= y >> 18
        return y & MASK32

    def mt_rand(self):
        return self.u32() >> 1                     # 31-bit, PHP_MT_RAND_MAX


def php_badscale(r31):
    """RAND_RANGE_BADSCALING(r, 0, 28, 0x7FFFFFFF) -- exact PHP double arithmetic."""
    return int(29.0 * (r31 / 2147483648.0))


def php_stream(seed, mode, scaling, n):
    g = PhpMT(seed, mode)
    if scaling == "scale":
        return [php_badscale(g.mt_rand()) for _ in range(n)]
    if scaling == "mod":
        return [g.mt_rand() % 29 for _ in range(n)]
    if scaling == "raw":
        return [g.mt_rand() for _ in range(n)]
    raise ValueError(scaling)


# ------------------------------------------------------------------ glibc TYPE_3


class GlibcRandom:
    """glibc srandom()/random(), default 128-byte TYPE_3 state (deg 31, sep 3)."""

    def __init__(self, seed):
        seed &= MASK32
        if seed == 0:
            seed = 1                               # glibc: "seed must not be 0"
        r = [0] * 344
        # glibc random_r.c seeds the Schrage chain from state[0], an int32_t --
        # seed >= 2^31 therefore enters NEGATIVE with C truncating division.
        # MEASURED against the resident glibc (receipts/genval.json): the int32
        # reading is |delta|=0 on all probe seeds incl. 2^31 and 2^32-1; the
        # unsigned-long reading was tried and REJECTED by the same probes.
        word = seed - (1 << 32) if seed >= 0x80000000 else seed
        r[0] = word
        for i in range(1, 31):
            if word >= 0:
                hi = word // 127773
            else:
                hi = -((-word) // 127773)          # C truncation toward zero
            lo = word - hi * 127773
            word = 16807 * lo - 2836 * hi
            if word < 0:
                word += 2147483647
            r[i] = word
        for i in range(31, 34):
            r[i] = r[i - 31]
        for i in range(34, 344):
            r[i] = (r[i - 31] + r[i - 3]) & MASK32
        self.ring = r[313:344]                     # last 31 values
        self.p = 0

    def u31(self):
        p = self.p
        v = (self.ring[p] + self.ring[(p + 28) % 31]) & MASK32
        self.ring[p] = v
        self.p = (p + 1) % 31
        return v >> 1


def glibc_stream(seed, scaling, n):
    g = GlibcRandom(seed)
    if scaling == "mod":
        return [g.u31() % 29 for _ in range(n)]
    if scaling == "raw":
        return [g.u31() for _ in range(n)]
    raise ValueError(scaling)


# ------------------------------------------------------------------ cell registry
# reducer-name -> stream fn(seed, n) producing rune indices 0..28
CELL_GENS = {
    "php_mt_scale":  lambda s, n: php_stream(s, "mt", "scale", n),
    "php_mt_mod":    lambda s, n: php_stream(s, "mt", "mod", n),
    "php_php_scale": lambda s, n: php_stream(s, "php", "scale", n),
    "php_php_mod":   lambda s, n: php_stream(s, "php", "mod", n),
    "glibc_mod":     lambda s, n: glibc_stream(s, "mod", n),
}


# ------------------------------------------------------------------ validation
def selftest(nseeds=5, ndraws=2000, extra_seeds=()):
    """|delta|=0 gate vs /usr/bin/php and the resident glibc. Returns receipt dict."""
    seeds = [0, 1, 777, 3301, 2**32 - 1][:nseeds] + list(extra_seeds)
    rec = {"seeds": seeds, "ndraws": ndraws, "php": {}, "glibc": {}, "pass": True}

    out = subprocess.run(
        ["php", os.path.join(HERE, "ref_php.php"), json.dumps(seeds), str(ndraws)],
        capture_output=True, text=True, check=True)
    ref = json.loads(out.stdout)
    assert ref["getrandmax"] == 2147483647
    rec["php"]["version"] = ref["php_version"]
    for row in ref["seeds"]:
        s = row["seed"]
        for mode in ("mt", "php"):
            for scaling, key in (("raw", "raw"), ("scale", "scaled"), ("mod", "mod29")):
                mine = php_stream(s, mode, scaling, ndraws)
                ok = mine == row[mode][key]
                rec["php"][f"seed{s}_{mode}_{scaling}"] = ok
                rec["pass"] &= ok
        rec["php"][f"seed{s}_legacy_range_path"] = row["php_range_matches_badscaling"]
        rec["pass"] &= row["php_range_matches_badscaling"]

    out = subprocess.run(
        [os.path.join(HERE, "ref_glibc"), " ".join(map(str, seeds)), str(ndraws)],
        capture_output=True, text=True, check=True)
    ref = json.loads(out.stdout)
    for row in ref["seeds"]:
        s = row["seed"]
        ok_raw = glibc_stream(s, "raw", ndraws) == row["random_raw"]
        ok_mod = glibc_stream(s, "mod", ndraws) == row["mod29"]
        rec["glibc"][f"seed{s}_raw"] = ok_raw
        rec["glibc"][f"seed{s}_mod29"] = ok_mod
        rec["glibc"][f"seed{s}_rand_equals_random"] = row["rand_equals_random"]
        rec["pass"] &= ok_raw and ok_mod and row["rand_equals_random"]
    return rec


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        rec = selftest()
        path = os.path.join(HERE, "receipts", "genval.json")
        with open(path, "w") as f:
            json.dump(rec, f, indent=1)
        n_ok = sum(1 for k, v in list(rec["php"].items()) + list(rec["glibc"].items())
                   if v is True)
        print(f"gen28 selftest: pass={rec['pass']}  ({n_ok} checks true) -> {path}")
        sys.exit(0 if rec["pass"] else 1)
    print(__doc__)
