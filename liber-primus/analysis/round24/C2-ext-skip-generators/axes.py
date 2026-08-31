#!/usr/bin/env python3
"""C2-EXT shared axis harness -- one keystream(axis, seed_or_word, n) call per axis.

Each axis is a (generator, reducer) pair producing >=n rune indices in 0..28 for a
given seed/word. The axes are exactly those C2's RESULTS left OPEN over the already
-existing pair (and, for A6, drift) decoder:

  A1 bash `$RANDOM`   gen_bash bash4.2 (LP64) -> reduce29.mod29     (offset==seed)
  A2 perl int(rand29) gen_perl r29 (drand48)
  A3t tex pgf         gen_tex pgf_rnd29
  A3l tex lcg         gen_tex lcg_mod29
  A4 sha256_ctr       benchmark/plant.ks_sha256_ctr(seed=bytes)     (string seeds)
  A5 py27 off!=0      gen_py27 random29 (the S-G3 generator; offset carried separately)
  A6 py27 free_drift  gen_py27 random29 (same key; the DRIFT decoder covers the cousin)

Nothing here scores. It emits keystreams and the per-axis prior-dense seed slices.
"""
import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in ("analysis/round19/G1", "analysis/round19/G2", "analysis/round19/G4",
           "analysis/round19/G3", "analysis/round19/I1", "analysis/round20/P3",
           "analysis/round13/B04", "src"):
    _q = os.path.join(LP, _p)
    if _q not in sys.path:
        sys.path.insert(0, _q)

import keystream as BASH_KS       # noqa: E402  G1 bash/glibc keystream interface
import gen_perl as GP             # noqa: E402
import gen_tex as GT              # noqa: E402
import gen_py27 as G3             # noqa: E402
import seeds as B04SEEDS          # noqa: E402  the Cicada seed dictionary

# benchmark/plant.py collides with other plant.py on sys.path -> load by file.
_spec = importlib.util.spec_from_file_location(
    "c2ext_bench_plant", os.path.join(LP, "benchmark", "plant.py"))
BPLANT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BPLANT)

N = 29

# --------------------------------------------------------------- keystream per axis

def ks_bash(seed, n):
    spec = {"family": "bash", "generator": "bash4.2", "seed": int(seed) & 0xFFFFFFFF,
            "reduction": "mod29", "sign": -1, "direction": "fwd",
            "atbash": False, "offset": 0}
    return BASH_KS.keystream(spec, n)


def ks_perl(seed, n):
    return GP.make_ks("r29", int(seed) & 0xFFFFFFFF, n)


def ks_tex_pgf(seed, n):
    return GT.make_ks("pgf_rnd29", int(seed), n)


def ks_tex_lcg(seed, n):
    return GT.make_ks("lcg_mod29", int(seed), n)


def ks_sha(seed_bytes, n):
    b = seed_bytes if isinstance(seed_bytes, (bytes, bytearray)) else str(seed_bytes).encode()
    return BPLANT.ks_sha256_ctr(seed=bytes(b), length=n)


def ks_py27(word, n):
    r = G3.MT19937()
    r.init_by_array([int(word) & 0xFFFFFFFF] if word else [0])
    return G3.REDUCERS["random29"](r, n)


AXES = {
    "A1_bash":    dict(fn=ks_bash,    space=2 ** 32, kind="int",   label="bash $RANDOM mod29 (bash4.2 LP64)"),
    "A2_perl":    dict(fn=ks_perl,    space=2 ** 32, kind="int",   label="perl int(rand(29)) (drand48)"),
    "A3t_texpgf": dict(fn=ks_tex_pgf, space=2 ** 31, kind="int",   label="tex pgf_rnd29"),
    "A3l_texlcg": dict(fn=ks_tex_lcg, space=2 ** 31, kind="int",   label="tex lcg_mod29"),
    "A4_sha":     dict(fn=ks_sha,     space=None,    kind="bytes", label="sha256_ctr keytext/string seeds (B04 dict)"),
    "A5_py27off": dict(fn=ks_py27,    space=2 ** 32, kind="int",   label="Py2.7-MT random29, offset!=0"),
    "A6_py27":    dict(fn=ks_py27,    space=2 ** 32, kind="int",   label="Py2.7-MT random29 (free_drift cousin, DRIFT decoder)"),
}


# ------------------------------------------------------------ per-axis prior slices
def _cicada_int_seeds():
    """LP2-plausible INTEGER seeds an author would type into RANDOM=/srand/pgf seed.
    = B04 NUM_INTS + primes + the 3301 family + the 433 Py2.7 seedprior seconds."""
    import json
    ints = []
    seen = set()

    def add(x):
        x = int(x) & 0xFFFFFFFF
        if x not in seen:
            seen.add(x)
            ints.append(x)

    for x in B04SEEDS.NUM_INTS:
        add(x)
    for x in B04SEEDS.FIRST_PRIMES:
        add(x)
    for s in B04SEEDS.NUM_STRINGS:
        try:
            add(int(s))
        except ValueError:
            pass
    for x in (3301, 1033, 761, 845145127, 1595277641, 1325734783,
              1325635200, 1357257600, 1388880000, 2012, 2013, 2014, 29):
        add(x)
    # the Py2.7 seedprior seconds, reused as integer seeds for the other generators
    p = json.load(open(os.path.join(LP, "analysis", "round20", "P3", "seedprior20.json")))
    for e in p["order"]:
        add(int(e["seed"]))
    return ints


def cicada_int_seeds():
    return list(_cicada_int_seeds())


def tex_default_seeds(cap=4000):
    """pgf/randomtex date-derived default seeds -- a THIN, enumerable slice."""
    s = set(GT.CICADA_SEEDS)
    s |= set(GT.pgf_default_seeds())
    out = sorted(x % (2 ** 31) for x in s if x)
    return out[:cap]


def b04_byte_seeds():
    """The full Cicada seed dictionary (bytes) for the sha256_ctr axis."""
    return [b for _label, b in B04SEEDS.build()]


def py27_top_seeds(topn=64):
    import json
    p = json.load(open(os.path.join(LP, "analysis", "round20", "P3", "seedprior20.json")))
    return [int(e["seed"]) & 0xFFFFFFFF for e in p["order"][:topn]]


if __name__ == "__main__":
    print("axes:", list(AXES))
    print("cicada int seeds:", len(cicada_int_seeds()))
    print("tex default seeds (cap):", len(tex_default_seeds()))
    print("b04 byte seeds:", len(b04_byte_seeds()))
    print("py27 top-64:", len(py27_top_seeds()))
    for name, spec in AXES.items():
        s = spec["fn"](3301 if spec["kind"] == "int" else b"CICADA3301", 12)
        print(f"  {name:12s} len={len(s)} head={s[:6]}")
