#!/usr/bin/env python3
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", "..", ".."))

import json, os, difflib
from collections import Counter

FOUND = _REPO + "/liber-primus/analysis/foundation"
streams = json.load(open(os.path.join(FOUND,"_streams.json")))
canon = streams["canon"]

def opcodes_summary(a, b, label):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ops = sm.get_opcodes()
    edits = [op for op in ops if op[0]!="equal"]
    print(f"\n### {label}  (len {len(b)} vs canon {len(a)}, autojunk=False ratio={sm.ratio():.6f})")
    if not edits:
        print("  BYTE-IDENTICAL to canon, no edits")
        return edits
    for tag,i1,i2,j1,j2 in edits:
        ca = a[i1:i2]
        cb = b[j1:j2]
        # show short context
        print(f"  {tag:7s} canon[{i1}:{i2}]={ca!r}  src[{j1}:{j2}]={cb!r}")
    return edits

for k in ["krisyotam","cicadasolvers","r4nd0mD3v3l0p3r","relikd","uncovering_wiki","scream314"]:
    opcodes_summary(canon, streams[k], k)
