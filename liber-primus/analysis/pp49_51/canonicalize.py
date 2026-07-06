"""Phase 1: canonicalize the pp49-51 base-60 payload into 256 bytes.

Three witnesses:
  A) relikd  data/relikd/p40-53.txt  -- tab-separated token tables (structure-authoritative)
  B) scream314 data/scream314_lp.md  -- space-separated token tables
  C) scream314 decimal column        -- the site's own decode (independent tie-breaker)

Base-60 digit set = 0-9 A-Z a-x (60 symbols, values 0..59); byte = d0*60 + d1.
'f'=41 is a legal symbol that simply never occurs (the F-skip fingerprint).
"""
import os, re, sys, math, collections

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

def digit_val(c):
    if c.isdigit(): return ord(c) - 48          # 0-9 -> 0-9
    if 'A' <= c <= 'Z': return ord(c) - 65 + 10  # A-Z -> 10-35
    if 'a' <= c <= 'x': return ord(c) - 97 + 36  # a-x -> 36-59
    raise ValueError(f"illegal base60 digit {c!r}")

def tok_to_byte(t):
    return digit_val(t[0]) * 60 + digit_val(t[1])

TOKROW = re.compile(r'^\s*([0-9A-Za-z]{2})([ \t]+[0-9A-Za-z]{2}){7}\s*$')

def extract_tables(path, sep):
    """Return list of token-tables; each table is a flat list of 2-char tokens.
    A table is a run of consecutive 8-column token rows separated by blanks."""
    tables, cur = [], []
    for line in open(path, encoding="utf-8"):
        if TOKROW.match(line):
            cur.extend(line.split())
        else:
            if cur: tables.append(cur); cur = []
    if cur: tables.append(cur)
    return tables

def extract_decimals(path):
    """scream314 decimal blocks: runs of rows of 8 integers."""
    DEC = re.compile(r'^\s*(\d{1,3})(\s+\d{1,3}){7}\s*$')
    blocks, cur = [], []
    for line in open(path, encoding="utf-8"):
        if DEC.match(line):
            cur.extend(int(x) for x in line.split())
        else:
            if cur: blocks.append(cur); cur = []
    if cur: blocks.append(cur)
    return blocks

# --- gather relikd tables (the three pp49-51 tables have 80/104/72 = 256) ---
relikd = extract_tables(os.path.join(ROOT, "data/relikd/p40-53.txt"), sep="\t")
relikd_tabs = [t for t in relikd if len(t) in (80, 104, 72)]
scream = extract_tables(os.path.join(ROOT, "data/scream314_lp.md"), sep=" ")
scream_tabs = [t for t in scream if len(t) in (80, 104, 72)]
dec_blocks = [b for b in extract_decimals(os.path.join(ROOT, "data/scream314_lp.md")) if len(b) in (80, 104, 72)]

print("relikd token-tables (len):", [len(t) for t in relikd_tabs])
print("scream token-tables (len):", [len(t) for t in scream_tabs])
print("scream decimal blocks (len):", [len(b) for b in dec_blocks])

def stitch(tabs):
    order = {80:0, 104:1, 72:2}
    picked = {}
    for t in tabs:
        picked.setdefault(order[len(t)], t)
    return [tok for k in (0,1,2) for tok in picked[k]]

A = stitch(relikd_tabs)                 # relikd tokens
B = stitch(scream_tabs)                 # scream tokens
# scream decimal: take first block of each length in order
decpick = {}
for b in dec_blocks: decpick.setdefault(len(b), b)
C = [v for k in (80,104,72) for v in decpick.get(k, [None]*k)] if all(k in decpick for k in (80,104,72)) else None

print(f"\ncounts: relikd={len(A)} scream={len(B)} decimal={len(C) if C else 'MISSING'}")

# --- three-way adjudication by MAJORITY vote ---
# Two variants: `maj` = strict majority of {relikd-tok, scream-tok, scream-dec};
# `decpref` = prefer scream's decimal on any disagreement. They differ only on the
# "both tokens agree, decimal alone differs" cells, which are genuinely contested.
maj, decpref, conflicts, contested = [], [], [], []
for i in range(256):
    a = A[i]; av = tok_to_byte(a)
    b = B[i]; bv = tok_to_byte(b)
    c = C[i]
    votes = collections.Counter([av, bv, c])
    winner, wn = votes.most_common(1)[0]      # majority (>=2 always exists unless 3-way split)
    maj.append(winner)
    decpref.append(c)
    if not (av == bv == c):
        # classify the disagreement
        if av == bv and c != av:
            kind = "CONTESTED: both tokens agree, decimal differs (needs image)"
            contested.append(i)
        elif av != bv:
            kind = f"token-split, decimal breaks -> {winner}"
        else:
            kind = "3-way split"
        conflicts.append((i, a, av, b, bv, c, winner, kind))

byts = bytes(maj)
byts_dec = bytes(decpref)
print(f"\nMajority-vote canon assembled. total conflicts: {len(conflicts)}  contested(image-needed): {len(contested)}")
for (i,a,av,b,bv,c,w,kind) in conflicts:
    print(f"  idx {i:3d} (r{i//8},c{i%8}): relikd {a}={av:<3} scream {b}={bv:<3} decimal={c:<3} -> maj={w:<3}  [{kind}]")
delta = sum(1 for x,y in zip(byts, byts_dec) if x != y)
print(f"\nmajority vs decimal-preferred streams differ in {delta} / 256 bytes (== the contested cells)")

# --- characterization ---
hist = collections.Counter(byts)
H = -sum((n/256)*math.log2(n/256) for n in hist.values())
print(f"\nentropy = {H:.3f} bits/byte  (max 8.0; 256 iid draws expect ~6.2-6.7 due to collisions)")
print(f"distinct byte values: {len(hist)} / 256")
print(f"min={min(byts)} max={max(byts)}  0x00 present: {0 in byts}  0xFF present: {255 in byts}")
printable = sum(1 for x in byts if 32 <= x < 127)
print(f"ASCII-printable bytes: {printable}/256 ({100*printable/256:.0f}%)")

open(os.path.join(HERE, "canon_256.bin"), "wb").write(byts)
open(os.path.join(HERE, "canon_256.hex"), "w").write(byts.hex())
open(os.path.join(HERE, "canon_256_decpref.bin"), "wb").write(byts_dec)
print(f"\nwrote canon_256.bin (majority) + canon_256_decpref.bin (decimal-preferred)")
print("majority hex:", byts.hex())
