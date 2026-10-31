#!/usr/bin/env python3
"""R38 X1: O4 matrix recount after Round 38 (C1 H3xF5, C2 7 cells run + 34 no-operation-stated). Reads round37 o4_recount.json."""
import json, re, os, sys
sys.dont_write_bytecode = True
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, "..", "..")
o = json.load(open(os.path.join(R, "round37", "X1-redteam", "o4_recount.json")))
print([k for k in o.keys()])
never = {c.replace(" ", "") for c in o["NEVER_cells_after"]}
txt = open(os.path.join(R, "round38", "C2-never-cells", "closed_no_operation.md"), encoding="utf-8").read()
c1 = set(re.findall(r"\b([HLS]\d+xF5)\b", txt.split("## Cells RUN")[0]))
run = {"H5xF1", "H6xF2", "L8xF6", "L15xF6", "L15xF7", "L17xF7", "L4xF3"}
nop = set(re.findall(r"^\| ([HLS]\d+xF\d+) \|", txt, re.M))
print(len(never), len(c1), len(run), len(nop), "partition_equal:", (c1 | run | nop) == never, "overlap:", (c1 & run) | (c1 & nop) | (run & nop))
print("missing from partition:", sorted(never - (c1 | run | nop)), "extra:", sorted((c1 | run | nop) - never))
cnt = {"NEVER": 60 - len(run) - len(nop) - 1, "NO-OP-STATED": len(nop), "T_added": len(run), "PART_added": 1}
cnt["NEVER_remaining_cells"] = sorted(c1 - {"H3xF5"})
print(cnt)
json.dump({"before_R38": 60, "C2_run_to_T": sorted(run), "C2_no_operation_stated": sorted(nop), "C1_H3xF5_to_PART": "H3xF5",
           "after": {"NEVER": 60 - len(run) - len(nop) - 1, "TRIED": 31 + 7, "T-EN": 21, "T-LEG": 25, "PARTIAL": 3 + 1, "NO-OPERATION-STATED": len(nop),
                     "sum": 60 - len(run) - len(nop) - 1 + 38 + 21 + 25 + 4 + len(nop)}, "NEVER_cells": sorted(c1 - {"H3xF5"}),
           "note": "C2 labelled all 19 F5 cells 'C1-R38'; C1-R38 operationalized only H3xF5 ('meaning is the road'); the other 18 F5 cells remain NEVER (unrun)."},
          open(os.path.join(H, "o4_recount_r38.json"), "w"), indent=1)
