"""Task 17: Explicit interrupter-model short-key search.

We model the doublet-suppressor as a STRUCTURED interrupter and brute short
primer keys (Vigenere & ciphertext-autokey, lengths 1..8) with the interrupter
modeled EXPLICITLY (not the heuristic skip in attack.py).

Interrupter semantics tested (the rune R is the designated interrupter):
  mode 'skip'   : R is a null. Output R literally; keystream index NOT advanced.
                  (== the current attack.py heuristic)
  mode 'advance': R is dropped from the plaintext but DOES advance the keystream
                  (an inserted spacer that still costs a key symbol).
  mode 'reset'  : R resets the keystream to position 0 (segment-restart primer).
  mode 'enc'    : R is enciphered like any rune (no special handling) -> baseline.

We scan ALL 29 candidate interrupter runes for each mode, not just F.

Scoring: quadgram score_norm over the produced plaintext (interrupter runes
excluded from the scored text). Higher (less negative) = more English.
Baseline on these pages ~ -6.23; English ~ -4.2..-5.0.
"""
import sys, itertools, json
sys.path.insert(0, 'src')
from lp import gematria as gp
from lp import score as sc

N = gp.N
Q = sc.default()

pages = open('data/krisyotam_runes.txt').read().split('%')

# rune sequence per page (indices, with positions of interrupter handled at runtime)
def page_runes(p):
    return [c for c in p if c in gp.RUNE_TO_IDX]

# ---- decrypt with explicit interrupter, Vigenere primer key ----
def decrypt_vig(runes, key, interrupt_idx, mode, sign=-1):
    """runes: list of rune chars. key: list of key indices. interrupt_idx: int rune index or None."""
    out = []   # plaintext indices (interrupter excluded)
    k = 0
    klen = len(key)
    for ch in runes:
        ci = gp.RUNE_TO_IDX[ch]
        if interrupt_idx is not None and ci == interrupt_idx and mode != 'enc':
            if mode == 'skip':
                continue
            elif mode == 'advance':
                k += 1
                continue
            elif mode == 'reset':
                k = 0
                continue
        p = (ci + sign * key[k % klen]) % N
        out.append(p)
        k += 1
    return out

# ---- decrypt with explicit interrupter, ciphertext-autokey primer ----
def decrypt_autokey(runes, seed, K, interrupt_idx, mode, sign=+1):
    out = []
    prev = seed
    for ch in runes:
        ci = gp.RUNE_TO_IDX[ch]
        if interrupt_idx is not None and ci == interrupt_idx and mode != 'enc':
            if mode == 'skip':
                continue          # null: doesn't enter the chain
            elif mode == 'advance':
                prev = ci          # enters chain but not output
                continue
            elif mode == 'reset':
                prev = seed
                continue
        p = (ci - sign * prev - K) % N
        out.append(p)
        prev = ci
    return out

def text_of(idxs):
    return gp.indices_to_translit(idxs)

def score_idx(idxs):
    return Q.score_norm(text_of(idxs))
