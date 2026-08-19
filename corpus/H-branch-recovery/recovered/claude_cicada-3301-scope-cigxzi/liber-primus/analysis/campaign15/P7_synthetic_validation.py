#!/usr/bin/env python3
"""Synthetic validation for P7: plant a real message enciphered under the LP2
stream at a known offset, then confirm Family-1 recovers it (score fires)."""
import sys
sys.path.insert(0, 'src')
import numpy as np
from lp import gematria as gp, score

N = gp.N
RUNE = gp.RUNE_TO_IDX
Q = score.default()

raw = open('data/krisyotam_runes.txt', encoding='utf-8').read()
pages_raw = [p for p in raw.split('%') if any(ch in RUNE for ch in p)]
stream = [RUNE[c] for p in pages_raw[:-2] for c in p if c in RUNE]
KEY = np.array(stream, dtype=np.int64)

# a plausible plaintext -> rune indices via keyword_to_indices
pt = "THEPRIMESARESACREDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBEENCRYPTED"
pidx = np.array(gp.keyword_to_indices(pt), dtype=np.int64)
L = len(pidx)
OFF = 5000
# encipher: cipher = (plain + key) mod 29  -> so decrypt is (cipher - key)
cipher = (pidx + KEY[OFF:OFF+L]) % N

# run the same detector Family-1 uses (fwd key, sub op) over all offsets
best = -999; bi = None
for i in range(len(KEY) - L + 1):
    row = (cipher - KEY[i:i+L]) % N
    s = Q.score_norm(gp.indices_to_translit(row))
    if s > best:
        best = s; bi = i
print(f"planted at offset {OFF}, len {L}")
print(f"detector best score_norm = {best:.3f} at offset {bi}")
print("recovered:", gp.indices_to_translit((cipher - KEY[bi:bi+L]) % N))
print("PASS" if bi == OFF and best > -5.2 else "FAIL")
