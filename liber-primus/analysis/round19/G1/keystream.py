"""Round 19 / G1 -- THE KEYSTREAM PRODUCTION INTERFACE.

One entry point for Phase 2 (S1).  A `spec` is a plain dict; `keystream(spec, n)`
returns `n` integers in 0..28.  Nothing here scores anything.

    spec = {
      "family":    "bash" | "glibc" | "coreutils",
      "generator": e.g. "bash4.2", "glibc_random", "lrand48", "openssl_enc_rc4_k",
                        "shuf_random_source",
      "seed":      int, or (for the dictionary generators) a str/path,
      "reduction": one of reduce29.REDUCTIONS,
      "sign":      -1 | +1,
      "direction": "fwd" | "rev",
      "atbash":    bool,
      "offset":    int  -- how many Z29 symbols to drop off the head,
    }

Two things a caller MUST know, both measured (validation.json, RESULTS.md section 3):

1. For every `bash` generator, `seed` and `offset` are THE SAME AXIS.  brand() is a pure
   state map and `RANDOM=<seed>` writes the state, so seed s at offset k is seed
   f^k(s) at offset 0.  Sweeping offsets on top of a full seed enumeration buys
   nothing; sweeping offsets on top of a PARTIAL seed enumeration is just a second,
   worse way of covering more seeds.
2. `glibc` generators do NOT have that property (state is 31x32 bits, seed is 32), so
   offset is a genuine extra axis there.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gen_bash as GB          # noqa: E402
import gen_glibc as GG         # noqa: E402
import gen_coreutils as GC     # noqa: E402
import reduce29 as R29         # noqa: E402

N = 29

# generator -> (family, raw_iter_factory(seed, n_raw), inclusive rmax)
_BASH = {v: ("bash", (lambda v: (lambda s, n: iter(GB.raws(s, n, v))))(v), GB.RMAX)
         for v in GB.BRANDS}
_GLIBC = {k: ("glibc", (lambda fn: (lambda s, n: iter(fn(s, n))))(f), rmax)
          for k, (f, rmax) in GG.GENERATORS.items()}
_CORE = {
    "openssl_enc_rc4_k": ("coreutils",
                          lambda s, n: iter(GC.raws_openssl_enc(s, n)),
                          GC.RMAX_BYTE),
}

REGISTRY = {}
REGISTRY.update(_BASH)
REGISTRY.update(_GLIBC)
REGISTRY.update(_CORE)

# Rank-ordered by L1 section 6.2. S1 should walk this order, not alphabetical order.
PRIORITY = [
    "glibc_random",        # L1 row 1, x3 -- the top-ranked family
    "bash4.2",             # L1 row 4, x2 -- era-correct, LP64
    "bash4.2_i32",         # L1 row 4, x2 -- era-correct, ILP32
    "lrand48",             # L1 row 1 (drand48); ALREADY COVERED by CENSUS gen 11 --
                           #   de-duplicate, do not re-sweep
    "drand48_x2p53",
    "mrand48",
    "glibc_initstate32", "glibc_initstate64", "glibc_initstate256", "glibc_initstate8",
    "bash4.0",             # deterministic prefix only -- see RESULTS section 3.4
    "bash3.2", "bash3.2_i32", "bash5.0", "bash5.1", "bash5.1c50",  # wrong era, kept for
                                                                   # completeness only
    "openssl_enc_rc4_k",   # dictionary; overlaps R16-KDF
]

# How much raw material a reduction needs per Z29 symbol, worst case.  rej29 discards
# the tail of the range; bits5 yields several symbols per draw.
_RAW_FACTOR = {"mod29": 1.0, "rej29": 1.3, "scale29": 1.0,
               "hi_nib": 1.0, "lo_byte": 1.0, "bits5": 0.4}


def keystream(spec, n):
    """n Z29 symbols for `spec`.  Deterministic; no I/O except for the oracle
    generators (shuf), which are not in REGISTRY and are handled by shuf_keystream."""
    gen = spec["generator"]
    family, mk, rmax = REGISTRY[gen]
    red = spec.get("reduction", "mod29")
    off = int(spec.get("offset", 0))
    need = n + off
    n_raw = int(need * _RAW_FACTOR.get(red, 1.0) * 1.25) + 64
    ks = R29.reduce_stream(mk(spec["seed"], n_raw), rmax, need, red)
    while len(ks) < need:                       # rejection ate more than budgeted
        n_raw *= 2
        ks = R29.reduce_stream(mk(spec["seed"], n_raw), rmax, need, red)
    ks = ks[off:off + n]
    return R29.orient(ks, spec.get("direction", "fwd"), bool(spec.get("atbash", False)))


def shuf_keystream(src_path, n, spec=None):
    """`shuf -i 0-28 -r -n n --random-source=FILE` through the REAL binary.
    Returns None when shuf refuses (usually: source file too short)."""
    spec = spec or {}
    ks = GC.shuf_stream(src_path, n + int(spec.get("offset", 0)))
    if ks is None:
        return None
    ks = ks[int(spec.get("offset", 0)):]
    return R29.orient(ks, spec.get("direction", "fwd"), bool(spec.get("atbash", False)))


def spec_id(spec):
    return "|".join(str(spec.get(k)) for k in
                    ("generator", "seed", "reduction", "sign", "direction",
                     "atbash", "offset"))


def enumerate_specs(generator, seeds, stage="A"):
    """The full (seed x reduction x sign x direction x atbash x offset) cross for one
    generator.  `seeds` may be any iterable, including a range() of 2**32 -- this is a
    generator, it does not materialise."""
    for s in seeds:
        for v in R29.variants(stage):
            d = {"family": REGISTRY[generator][0], "generator": generator, "seed": s}
            d.update(v)
            yield d


def cells_per_seed(stage="A"):
    return R29.variant_count(stage)


# ------------------------------------------------------------------- master-orbit path
def bash_sliding(variant, start_state, n_windows, klen, stride=1):
    """The O(2**31 + L) form of a bash seed sweep: build the master orbit once, then
    slide.  Yields (state_index, raw_window).  Valid because
    validation.json.internal_consistency.sliding_window_<variant>.holds is true.

    NOTE the transient caveat measured in RESULTS.md section 3.2: seeds off the cycle
    reach it only after a tail (13-72 draws for bash4.2 LP64; 210k-500k for
    bash4.2_i32).  Sliding over the cycle therefore covers ON-CYCLE keystreams; the
    transient trees are a separate residue and must be swept seed-by-seed or declared
    not covered.
    """
    master = GB.master_orbit(variant, start=start_state,
                             length=n_windows * stride + klen + 16)
    for i in range(0, n_windows * stride, stride):
        yield i, GB.window(master, i, klen)


if __name__ == "__main__":
    demo = {"family": "bash", "generator": "bash4.2", "seed": 3301,
            "reduction": "mod29", "sign": -1, "direction": "fwd",
            "atbash": False, "offset": 0}
    print(spec_id(demo))
    print(keystream(demo, 24))
    demo2 = dict(demo, generator="glibc_random", reduction="rej29")
    print(spec_id(demo2))
    print(keystream(demo2, 24))
    print("cells/seed stage A:", cells_per_seed("A"), " stage B:", cells_per_seed("B"))
