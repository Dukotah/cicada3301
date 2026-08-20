#!/usr/bin/env python3
"""Canonical rune extractor + hasher for LANE E.

Extracts Anglo-Saxon futhorc runes (Unicode block U+16A0-U+16F8) from any
text file, maps them to Gematria Primus indices 0-28, and emits the SHA-256
of the comma-joined index string -- the same identity used by
liber-primus/PROBLEM.json.
"""
import sys, hashlib, re, os

# Gematria Primus order, 29 runes.
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
IDX = {r: i for i, r in enumerate(GP)}
# Codepoint aliases seen in the wild: some transcriptions encode GP index 11 (J)
# as U+16C2 RUNIC LETTER E rather than U+16C4 RUNIC LETTER GER. Same glyph slot,
# different codepoint -- an ENCODING variant, not a reading difference.
IDX["ᛂ"] = 11

def runes_of(text):
    return [c for c in text if c in IDX]

def digest(text):
    rs = runes_of(text)
    idx = [IDX[c] for c in rs]
    s = ",".join(str(i) for i in idx)
    return len(idx), hashlib.sha256(s.encode()).hexdigest(), idx

if __name__ == "__main__":
    for p in sys.argv[1:]:
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except Exception as e:
            print(f"{p}\tERR\t{e}"); continue
        n, h, _ = digest(t)
        if n == 0: continue
        print(f"{n}\t{h}\t{p}")
