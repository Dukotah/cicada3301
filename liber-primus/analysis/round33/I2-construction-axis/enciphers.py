"""Round 33 / I2 enciphers. Decode relation p=(c-k)%N  =>  c=(p+k)%N (same as round32 beam_v2).
All return (C, info). Rejection = keyskip1-style output-side doublet filter with strength `supp`."""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "round32", "I1-skipbytwo-decoder"))
import beam_v2 as B
N = B.N
keyskip1 = B.encipher_keyskip1
skip_by_two = B.encipher_skip_by_two

def _core(P, K, supp, seed, adv, resets=()):
    """resets: sorted set of plaintext indices at which the key pointer returns to 0."""
    rng = random.Random(seed); rs = set(resets)
    C = []; j = 0; cp = None; ns = 0
    for i, p in enumerate(P):
        if i in rs:
            j = 0
        while True:
            c = (p + K[j]) % N
            if cp is not None and c == cp and rng.random() < supp:
                j += adv; ns += 1; continue
            break
        C.append(c); j += 1; cp = c
    return C, {"n_skips": ns, "n_resets": len(rs)}

def _bounds(lens, L):
    out, a = [], 0
    for x in lens:
        a += x
        if a < L: out.append(a)
    return out

def encipher_reset_per_page(P, K, page_lens, supp=0.83, seed=3301):
    return _core(P, K, supp, seed, 1, _bounds(page_lens, len(P)))

def encipher_reset_per_line(P, K, line_lens, supp=0.83, seed=3301):
    return _core(P, K, supp, seed, 1, _bounds(line_lens, len(P)))

def encipher_skip_by_k(P, K, k=3, supp=0.83, seed=3301):
    return _core(P, K, supp, seed, k)
