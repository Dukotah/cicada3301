"""Autokey ciphers over the 29-symbol Gematria Primus.

Motivation: the unsolved LP pages show a DOUBLET DEFICIT (≈0.66% vs 3.45%
random). Among classical constructions, a *ciphertext autokey* uniquely
suppresses doublets:

    ciphertext autokey:  c_i = (p_i + c_{i-1} + K) mod 29,  c_{-1} = seed
      => c_{i+1} == c_i  iff  p_{i+1} == -K (mod 29)
         i.e. a doublet occurs only when the plaintext rune is one fixed value.
         Observed doublet rate should equal that rune's plaintext frequency.

    plaintext autokey:   c_i = (p_i + p_{i-1} + K) mod 29
      => doublet iff p_{i-1} == p_{i+1}  -> rate ≈ IoC(English) ≈ 6%  (MORE
         doublets, not fewer) -> RULED OUT by the deficit.

Decryption of a ciphertext autokey needs only the seed + K (29*29 combos), and
the keystream is the ciphertext we already hold — no external key text. This is
the cheapest possible attack and the doublet stat points right at it.

Variants supported: sign (Vigenère vs Beaufort-ish), optional Atbash on the
plaintext alphabet, and a fixed per-step offset K.
"""
from . import gematria as gp

N = gp.N


# ---------------------------------------------------------------- encrypt (for synthetic validation)
def encrypt_ciphertext_autokey(plain_idx, seed=0, K=0, sign=+1):
    out = []
    prev = seed
    for p in plain_idx:
        c = (p * 1 + sign * prev + K) % N
        out.append(c)
        prev = c
    return out


def encrypt_plaintext_autokey(plain_idx, seed=0, K=0, sign=+1):
    out = []
    prev = seed
    for p in plain_idx:
        c = (p + sign * prev + K) % N
        out.append(c)
        prev = p
    return out


# ---------------------------------------------------------------- decrypt
def decrypt_ciphertext_autokey(cipher_idx, seed=0, K=0, sign=+1, atbash=False):
    """p_i = (c_i - sign*c_{i-1} - K). Keystream = the ciphertext itself."""
    out = []
    prev = seed
    for c in cipher_idx:
        p = (c - sign * prev - K) % N
        if atbash:
            p = (N - 1) - p
        out.append(p)
        prev = c
    return out


def decrypt_plaintext_autokey(cipher_idx, seed=0, K=0, sign=+1, atbash=False):
    """p_i = (c_i - sign*p_{i-1} - K). Keystream = recovered plaintext (chained)."""
    out = []
    prev = seed
    for c in cipher_idx:
        p = (c - sign * prev - K) % N
        pp = (N - 1) - p if atbash else p
        out.append(pp)
        prev = p  # chain on pre-atbash plaintext index
    return out
