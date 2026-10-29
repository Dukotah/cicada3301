"""Round 32 / I1 -- beam_decode_v2: the skip construction as an EXPLICIT parameter.

    advance = 1       key advances by 1 per rejection  (encipher_keyskip; the repo's old relation)
    advance = 2       key advances by 2 per rejection  (encipher_skip_by_two; pairs of skipped
                      key positions, first doublet-consistent, second unconstrained)
    advance = "free"  construction-agnostic: any advance <= max_skip, at most max_free of them
                      unexplained, lam penalty each (the Round-19 `drift` preset)

PROVENANCE (found while reading; CAMPAIGN-PLAN s3 I1 did not know this): the transition
relations themselves already exist as round19/I1/driftbeam.py (modes keyskip1 / keyskip2 /
permissive, 15 tests, gates G-EQ/G-BASE/G-FIX/G-FP).  This module does NOT re-derive them; it is
a thin explicit-parameter facade over that decoder (imported, unmodified) plus the three
enciphers and a keystream.  What is new in Round 32 I1 is the MEASUREMENT (L=120, non-English
registers, panel adjudication, seed-3301 shuffle null), not the transition algebra.
"""
import os, sys, random, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round11"),
          os.path.join(LP, "analysis", "round19", "I1"),
          os.path.join(LP, "analysis", "round19", "I2"),
          os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")):
    if p not in sys.path:
        sys.path.insert(0, p)

import driftbeam as DB                  # noqa: E402  (round19/I1, unmodified)
from lp import gematria as gp           # noqa: E402

N = gp.N

ADVANCE = {
    1:      dict(mode="keyskip1", max_skip=8, max_free=0, lam=0.0, start_slack=0),
    2:      dict(mode="keyskip2", max_skip=8, max_free=0, lam=0.0, start_slack=0),
    "free": dict(mode="permissive", max_skip=40, max_free=2, lam=12.0, start_slack=2),
}


def beam_decode_v2(C, K, advance, sign=-1, o=0, beam_w=400, want_path=True, **override):
    """Skip-tolerant beam decode with the skip construction named explicitly."""
    if advance not in ADVANCE:
        raise ValueError("advance must be one of %s, got %r" % (list(ADVANCE), advance))
    kw = dict(ADVANCE[advance])
    kw.update(override)
    return DB.beam_decode(C, K, sign=sign, o=o, beam_w=beam_w, want_path=want_path, **kw)


recovery = DB.recovery


# decode relation p = (c + sign*k) % N with sign=-1  =>  c = (p + k) % N
def encipher_keyskip1(P, K, supp=0.83, seed=3301):
    rng = random.Random(seed); C = []; j = 0; cp = None; ns = 0
    for p in P:
        while True:
            c = (p + K[j]) % N
            if cp is not None and c == cp and rng.random() < supp:
                j += 1; ns += 1; continue
            break
        C.append(c); j += 1; cp = c
    return C, {"n_skips": ns}


def encipher_skip_by_two(P, K, supp=0.83, seed=3301):
    """Same as round18/L7-redteam/b1_power_envelope.enc_skip_by_two."""
    rng = random.Random(seed); C = []; j = 0; cp = None; ns = 0
    for p in P:
        while True:
            c = (p + K[j]) % N
            if cp is not None and c == cp and rng.random() < supp:
                j += 2; ns += 1; continue
            break
        C.append(c); j += 1; cp = c
    return C, {"n_skips": ns}


def encipher_free_drift(P, K, supp=0.83, q=0.05, seed=3301):
    """Same as b1_power_envelope.enc_free_drift: keyskip1 plus an unrelated advance w.p. q."""
    rng = random.Random(seed); C = []; j = 0; cp = None; ns = 0; nd = 0
    for p in P:
        if rng.random() < q:
            j += 1; nd += 1
        while True:
            c = (p + K[j]) % N
            if cp is not None and c == cp and rng.random() < supp:
                j += 1; ns += 1; continue
            break
        C.append(c); j += 1; cp = c
    return C, {"n_skips": ns, "n_drift": nd}


ENCIPHER = {"keyskip1": encipher_keyskip1,
            "skip_by_two": encipher_skip_by_two,
            "free_q05": lambda P, K, supp=0.83, seed=3301: encipher_free_drift(P, K, supp, 0.05, seed)}


def sha_ctr_key(n, seed=b"CICADA3301"):
    """SHA-256 counter-mode keystream over Z_29 (uniform via byte rejection)."""
    out = []; ctr = 0
    while len(out) < n:
        h = hashlib.sha256(seed + ctr.to_bytes(8, "big")).digest()
        out.extend(b % N for b in h if b < 232)
        ctr += 1
    return out[:n]
