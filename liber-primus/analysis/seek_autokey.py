"""Plaintext-feedback AUTOKEY over the prime/totient family — the gap in
seek_primes.py (which only fed back on CIPHERTEXT).

Grounded in Cicada's own signposts: solved page 5 says "THE PRIMES ARE SACRED /
THE TOTIENT FUNCTION IS SACRED", and page 56 was solved with a running
prime-totient keystream. The doublet fingerprint says the cipher is
history-dependent. This tests the natural synthesis: each rune shifted by a
prime/totient FUNCTION OF THE PREVIOUS PLAINTEXT rune (true autokey), decrypted
sequentially from a brute-forced seed, and scored with English quadgrams (not
IoC — autokey partial breaks need a language model to see).

  encrypt: c[i] = p[i] + s * F(p[i-1])           (mod 29),  p[-1] = seed
  decrypt: p[i] = c[i] - s * F(p[i-1])           (sequential, seed brute 0..28)

Reproduce: PYTHONUTF8=1 python analysis/seek_autokey.py
"""
import os, sys
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp
from lp import score as _score

N = 29
P = gp.PRIMES                      # prime value per rune index
TOT = [p - 1 for p in P]           # totient of a prime = p-1
SC = _score.default()

def load_pages():
    segs = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read().split("%")
    pages = [gp.runes_to_indices(s) for s in segs if gp.runes_to_indices(s)]
    return pages[:-2]

# feedback functions F(prev_plain_index) -> shift amount
FUNCS = {
    "identity (Vigenere-autokey)": lambda j: j,
    "prime(prev) mod29":           lambda j: P[j] % N,
    "totient(prime(prev)) mod29":  lambda j: TOT[j] % N,
    "prime_index(prev)+1":         lambda j: (j + 1) % N,
    "prime(prev) mod29 reversed":  lambda j: (N - (P[j] % N)) % N,
}

def decrypt(cix, F, sign, seed):
    out = []
    prev = seed
    for c in cix:
        p = (c - sign * F(prev)) % N
        out.append(p)
        prev = p
    return out

def score(ixs):
    # map rune indices -> transliteration string, score per-quadgram (~-2.2 English)
    return SC.score_norm(gp.indices_to_translit(ixs))

def main():
    pages = load_pages()
    # english baseline + noise floor on this scorer, for calibration
    base_lines = []
    print(f"plaintext-feedback autokey sweep over {len(pages)} unsolved pages")
    print("(per page: 5 funcs x 2 signs x 2 atbash x 29 seeds)\n")
    global_best = (-1e9, None)
    for pi, page in enumerate(pages):
        for atb in (False, True):
            cc = [(N - 1 - c) for c in page] if atb else page
            for fname, F in FUNCS.items():
                for sign in (-1, 1):
                    for seed in range(N):
                        pt = decrypt(cc, F, sign, seed)
                        s = score(pt)
                        if s > global_best[0]:
                            latin = gp.indices_to_translit(pt)[:70]
                            global_best = (s, dict(page=pi, func=fname, sign=sign,
                                                   atbash=atb, seed=seed, head=latin))
    print("BEST decode across all pages/params:")
    b = global_best[1]
    print(f"  score/char = {global_best[0]:.4f}")
    for k in ("page","func","sign","atbash","seed"):
        print(f"    {k}: {b[k]}")
    print(f"    plaintext head: {b['head']}")
    # calibration reference
    eng = "ITISNOTANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAYHEREITISANECESSARYONE"
    print(f"\n  (calibration) English score_norm ~ {SC.score_norm(eng):.4f}  (noise ~ -4.5)")
    print("  A real break scores near the English reference; OTP-class sits far below.")

if __name__ == "__main__":
    main()
