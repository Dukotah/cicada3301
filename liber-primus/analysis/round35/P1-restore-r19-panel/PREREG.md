# R35 / P1 - restore the Round 19 panel byte-exact - PREREG (2026-10-30, written before any fetch)

Recognizer (binary): sha256(round19/I2/models/panel.npz rebuilt) == 14a23d3619fa02df... (full hash from round34/S1-build-box).
Recorded corpus hashes: round19/I2/out_build.json. Current state (hashed before fetch): 8 of 11 inputs already match;
three do not: data/kjv.txt (rec 4,436,268 B), data/keys/mabinogion.txt (rec 617,362 B), data/keys/welsh/welsh_mabinogion.txt
(rec 524,561 B, Middle-Welsh Mabinogion; current = R32 modern-Welsh substitute, 761,030 B).
Plan: back up substitutes to ./backup; fetch Gutenberg #10 (variants -0.txt, .txt, utf-8), #5160 (variants) and search for the
Welsh original, each into its own directory; hash raw / LF / BOM-stripped / Gutenberg-trimmed variants; compare to recorded.
Place only on exact match. Q5: any corpus not matching => STOP, no substitution, panel not rebuilt, restore substitutes.
Rebuild (only if all match): python build_models.py, full params (20000 draws, seed 3301). Hard rules: no git, one process, data never executed.
Writes outside lane dir: only gitignored data/kjv.txt, data/keys/mabinogion.txt, data/keys/welsh/welsh_mabinogion.txt, round19/I2/models/panel.npz - and only on match.
