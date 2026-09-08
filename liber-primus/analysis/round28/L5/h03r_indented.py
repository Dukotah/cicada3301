#!/usr/bin/env python3
"""Amendment 3 cell: the 2012 P.S. block with line 1 visually indented by "P.S. "."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l5_payload_micro as L5

raw = open(L5.PS_TXT, "rb").read().decode("utf-8", "replace")
lines = []
grab = False
for line in raw.splitlines():
    t = line.strip().rstrip("\\")
    if "P.S." in line:
        grab = True
        t = t.split("P.S.")[1].strip().rstrip("\\")
    if grab and t and all(c.isdigit() for c in t):
        lines.append(t)
    elif grab and lines:
        break
assert [len(l) for l in lines] == [40, 45, 46]
block = ["....." + lines[0], lines[1], lines[2]]  # 5-col visual indent, non-digit skipped

_orig = L5.h03r_readings
def readings_skip(ls):
    reads = {}
    ncols = max(len(l) for l in ls)
    for coldir, rowdir, name in ((1, 1, "cols_L2R_top2bot"), (1, -1, "cols_L2R_bot2top"),
                                 (-1, 1, "cols_R2L_top2bot"), (-1, -1, "cols_R2L_bot2top")):
        s = []
        cols = range(ncols) if coldir == 1 else range(ncols - 1, -1, -1)
        rows = ls if rowdir == 1 else ls[::-1]
        for c in cols:
            for row in rows:
                if c < len(row) and row[c].isdigit():
                    s.append(row[c])
        reads[name] = "".join(s)
    return reads  # concat readings unchanged by indent; already covered in main run

L5.h03r_readings = readings_skip
rows = L5.h03r_test(block, "2012_PS_indent5")
for r in rows:
    print(f"{r['reading']}: printable={r['pair_ascii_printable']} 3301x{r['n_3301']} "
          f"1033x{r['n_1033']} prime={r['is_prime']} verdict={r['verdict']}")
    print("   text:", r["pair_ascii_text"][:70])
res = json.load(open(os.path.join(L5.HERE, "results.json")))
res["H-03r_indent5"] = rows
res["hits"] += [r for r in rows if r["verdict"].startswith("HIT")]
if res["hits"]:
    res["verdict"] = "FLAGGED-FOR-ORACLE"
json.dump(res, open(os.path.join(L5.HERE, "results.json"), "w"), indent=1)
print("total hits now:", len(res["hits"]))
