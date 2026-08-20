"""Lane P1 control, part 4: re-run lib_padsweep's STRICT gate at the corrected skip budget.

`lib_padsweep.control()` hardcodes A1's `MAX_SKIP=3`.  On the zero-run block-hash pad that
setting is under-powered (control_ms.json: recovery 0.650 at ms=3, 1.000 at ms=8), so the
strict gate returned PASS=False for reasons that are a decoder setting, not the pad.  This
re-runs the same gate at `MAX_SKIP=8`, on a zero-run pad and on a full-entropy pad.

  python control_pass.py    # -> control_pass.json
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import lib_padsweep as L

L.MAX_SKIP = 8                       # the corrected skip budget, see RESULTS.md
out = {}
for pad in ("hash_display.bin", "merkle_display.bin"):
    blob = open(os.path.join(HERE, "data", pad), "rb").read()
    print("== strict gate at MAX_SKIP=8 on", pad, flush=True)
    r = L.control(blob=blob, n_trials=12, seed=3301)
    out[pad] = {k: v for k, v in r.items() if k != "rows"}
    out[pad]["rows"] = r["rows"]
    print(pad, "PASS" if r["PASS"] else "FAIL", flush=True)
with open(os.path.join(HERE, "control_pass.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "rows"}
                  for k, v in out.items()}, indent=2))
