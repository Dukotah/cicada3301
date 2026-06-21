#!/usr/bin/env python3
import re, sys, os, difflib
from collections import Counter

FOUND = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/foundation"
CANON = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt"

# 29-rune Gematria Primus set
RUNES = set("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
# normalization: ᛂ (U+16C2) -> ᛄ
def norm(s):
    return s.replace("ᛂ","ᛄ")

def runes_only(s):
    return "".join(ch for ch in norm(s) if ch in RUNES)

# load canonical: split on %
canon_raw = open(CANON, encoding="utf-8").read()
canon_pages = [runes_only(p) for p in canon_raw.split("%")]
# drop trailing empties
while canon_pages and canon_pages[-1]=="":
    canon_pages.pop()
print("CANON pages:", len(canon_pages), "total runes:", sum(len(p) for p in canon_pages))

def load_lines(name):
    path = os.path.join(FOUND, name)
    pages=[]
    for line in open(path, encoding="utf-8"):
        r = runes_only(line)
        if r:
            pages.append(r)
    return pages

sources = {
    "krisyotam": load_lines("trans_krisyotam.txt"),
    "relikd": load_lines("trans_relikd.txt"),
    "scream314": load_lines("trans_scream314.txt"),
    "r4nd0mD3v3l0p3r": load_lines("trans_r4nd0mD3v3l0p3r.txt"),
    "uncovering_wiki": load_lines("trans_uncovering_wiki.txt"),
    "cicadasolvers": load_lines("trans_cicadasolvers.txt"),
}
sources["canon"] = canon_pages

for k,v in sources.items():
    print(f"{k:18s} pages={len(v):3d} runes={sum(len(p) for p in v)}")

# Concatenate each source into single stream for stream-level comparison
streams = {k:"".join(v) for k,v in sources.items()}
print("\n=== STREAM-LEVEL DIFF vs canon ===")
canon_stream = streams["canon"]
for k,s in streams.items():
    if k=="canon": continue
    ratio = difflib.SequenceMatcher(None, canon_stream, s).ratio()
    print(f"{k:18s} len={len(s):6d} (canon {len(canon_stream)}) ratio={ratio:.6f}")

# Save streams for next stage
import json
json.dump(streams, open(os.path.join(FOUND,"_streams.json"),"w"))
print("\nstreams saved")
