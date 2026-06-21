#!/usr/bin/env python3
import json, os, difflib

FOUND = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/foundation"
streams = json.load(open(os.path.join(FOUND,"_streams.json")))
canon = streams["canon"]

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"

# Verify the tail-truncated sources agree with canon on the shared prefix
print("=== PREFIX AGREEMENT (does each source == canon over its full length?) ===")
for k in ["cicadasolvers","r4nd0mD3v3l0p3r","relikd","uncovering_wiki"]:
    s = streams[k]
    L = len(s)
    pref = canon[:L]
    identical = (s == pref)
    print(f"{k:18s} len={L} == canon[:{L}] ? {identical}")
    if not identical:
        # find first mismatch
        for i in range(L):
            if s[i]!=pref[i]:
                print(f"   first mismatch at {i}: src={s[i]} canon={pref[i]}")
                break

# Now build per-page mapping for scream's disagreements
# Need canon page boundaries
CANON = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt"
def runes_only(s): return "".join(ch for ch in s.replace("ᛂ","ᛄ") if ch in RUNES)
canon_raw = open(CANON, encoding="utf-8").read()
canon_pages = [runes_only(p) for p in canon_raw.split("%")]
while canon_pages and canon_pages[-1]=="": canon_pages.pop()
# cumulative offsets
offsets=[]
c=0
for p in canon_pages:
    offsets.append((c, c+len(p)))
    c+=len(p)

def globpos_to_page(gp):
    for pi,(a,b) in enumerate(offsets):
        if a<=gp<b:
            return pi, gp-a
    return None,None

print("\n=== SCREAM314 disagreements located by page ===")
# scream global positions in CANON coordinate: 5891 replace, 13121 replace (ignore tail insert at 12956 which is the skip-F)
for gp, canonr, screamr in [(5891,"ᚫ","ᚪ"),(13121,"ᚣ","ᛖ")]:
    pi,idx = globpos_to_page(gp)
    print(f"  global {gp}: page {pi} idx {idx}  canon={canonr} scream={screamr}")
# tail insert
pi,idx = globpos_to_page(12955)
print(f"  global 12956 (extra F in scream): near page {pi} idx {idx} -> tail/page-56 skip-F convention")
print(f"  total canon pages={len(canon_pages)} page lens={[len(p) for p in canon_pages]}")
