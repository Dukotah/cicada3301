"""FRONT A1 harness — feed the author's own never-fed binary pads under the
skip-aware decoder over the 12,956 unsolved LP2 runes.

Positive-control-gated. Null = nc.shuffled (seed 3301).
"""
import os, sys, random, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "round11"))

from lp import gematria as gp                      # noqa
import lib_numchannel as nc                        # noqa
import skipdecode as sk                            # noqa

N = gp.N
PADDIR = os.path.join(HERE, "pads")

# ------------------------------------------------------------------ pad -> keystream builders
def load_bytes(path):
    with open(path, "rb") as f:
        return f.read()

def ks_mod29(b):
    return [x % N for x in b]

def ks_prime_to_idx(b):
    """byte value, if it is one of the 29 gematria primes, -> its rune index; else b%29.
    Uses gp.PRIMES ordering (idx0=2)."""
    p2i = {p: i for i, p in enumerate(gp.PRIMES)}
    return [p2i.get(x, x % N) for x in b]

def ks_hi_nibble(b):
    return [(x >> 4) % N for x in b]

def ks_lo_nibble(b):
    return [(x & 0xF) % N for x in b]

def ks_bits2(b):
    """expand each byte to 4 base-4 symbols mod 29 (just the 2-bit groups)."""
    out = []
    for x in b:
        out += [(x >> 6) & 3, (x >> 4) & 3, (x >> 2) & 3, x & 3]
    return out

def ks_byte_scaled(b):
    """byte -> rune index by scaling 0..255 into 0..28."""
    return [(x * N) // 256 for x in b]

BUILDERS = {
    "mod29": ks_mod29,
    "prime_to_idx": ks_prime_to_idx,
    "hi_nibble": ks_hi_nibble,
    "lo_nibble": ks_lo_nibble,
    "byte_scaled": ks_byte_scaled,
    # bits2 changes stream length semantics; handled separately if needed
}

# ------------------------------------------------------------------ positive control
def positive_control():
    """Encrypt PARABLE-like plaintext with a real pad (anti-repeat filtered),
    confirm beam_decode recovers it; rigid should fail; wrong pad stays noise."""
    plain_en = (
        "THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
        "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
        "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
        "SACRED GEOMETRY OF THE CIRCUMFERENCE"
    )
    P = sk.eng_to_idx(plain_en)
    # use the real _560.00 pad bytes -> mod29 keystream as the "author pad"
    b = load_bytes(os.path.join(PADDIR, "DATA__560.00"))
    K = ks_mod29(b)
    sign, o_true, supp = -1, 5000, 0.83
    C, skips, used = sk.encipher_keyskip(P, K[o_true:], sign=sign, supp=supp)
    truth = sk.idx_to_trans(P)
    rd = sk.rigid_decode(C, K, sign=sign, o=o_true)
    bd = sk.beam_decode(C, K, sign=sign, o=o_true, beam_w=500, max_skip=3)
    match_b = sum(a == b2 for a, b2 in zip(bd['plain_idx'], P)) / len(P)
    # wrong pad
    bw = load_bytes(os.path.join(PADDIR, "DATA_560.17"))
    WK = ks_mod29(bw)
    wb = sk.beam_decode(C, WK, sign=sign, o=1234, beam_w=500, max_skip=3)
    res = {
        "truth_head": truth[:60],
        "rigid_score": rd["score"], "rigid_head": rd["translit"][:60],
        "beam_score": bd["score"], "beam_head": bd["translit"][:60],
        "beam_match": match_b,
        "wrong_score": wb["score"], "wrong_head": wb["translit"][:60],
        "total_skips": sum(skips),
    }
    res["PASS"] = (match_b > 0.95 and bd["score"] > -5.0 and
                   rd["score"] < -6.0 and wb["score"] < -6.0)
    return res

if __name__ == "__main__":
    r = positive_control()
    print(json.dumps(r, indent=2))
    print("POSITIVE CONTROL:", "PASS" if r["PASS"] else "FAIL")
