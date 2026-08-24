"""
Generate ct.bin (rune index stream) from krisyotam_runes.txt for E-02B.
Minimal dependency version — only needs src/lp/gematria.py.
"""
import sys, os, array
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
from lp.gematria import RUNE_TO_IDX

DATA = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data'))
txt = open(os.path.join(DATA, 'krisyotam_runes.txt'), encoding='utf-8').read()
segs = txt.split('%')
UNSOLVED = segs[:55]  # LP2 pages 0-54

ct = [RUNE_TO_IDX[c] for s in UNSOLVED for c in s if c in RUNE_TO_IDX]
print(f"ct length: {len(ct)} runes")
assert len(ct) == 12956, f"Expected 12956, got {len(ct)}"

out = os.path.join(os.path.dirname(__file__), 'ct_local.bin')
with open(out, 'wb') as f:
    f.write(bytes(ct))
print(f"Written: {out}")
