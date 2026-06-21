#!/usr/bin/env python3
import json, os, difflib

FOUND = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/foundation"
DUDE = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/transcriptions/dude123124144_OCR__transcriptions.rne"
streams = json.load(open(os.path.join(FOUND,"_streams.json")))
canon = streams["canon"]

RUNES = set("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
def norm(s): return s.replace("ᛂ","ᛄ")
def runes_only(s): return "".join(ch for ch in norm(s) if ch in RUNES)

raw = open(DUDE, encoding="utf-8").read()
# how many ᛂ before norm
print("dude raw ᛂ count:", raw.count("ᛂ"), " ᛄ count:", raw.count("ᛄ"))
dude = runes_only(raw)
print("dude total runes:", len(dude), " canon:", len(canon))

sm = difflib.SequenceMatcher(None, canon, dude, autojunk=False)
print("ratio (autojunk=False):", round(sm.ratio(),6))
edits = [op for op in sm.get_opcodes() if op[0]!="equal"]
print("num edit blocks:", len(edits))
# show first 40 edits with context
for tag,i1,i2,j1,j2 in edits[:60]:
    ca=canon[i1:i2]; cb=dude[j1:j2]
    print(f"  {tag:7s} canon[{i1}:{i2}]={ca!r} dude[{j1}:{j2}]={cb!r}")

# replacements only (true single-rune disagreements where lengths match)
repl = [(i1,i2,j1,j2) for tag,i1,i2,j1,j2 in edits if tag=="replace"]
print("\nreplace blocks:", len(repl))
# count single-rune replacements
single = [r for r in repl if r[1]-r[0]==1 and r[3]-r[2]==1]
print("single-rune replacements:", len(single))
