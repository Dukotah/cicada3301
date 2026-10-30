#!/usr/bin/env python3
"""Run in this directory BEFORE `grind27 --self-test`. grind27.c parses PANEL_SHA256 from engine.dat but never compares it to the file (finding),
so the panel gate is enforced here: panel_lm.f32 must hash to the value recorded in engine.dat AND to the panel-R36 LM blob hash, and NREG must be 12.
Exit 0 = gate inputs are panel-R36; exit 1 = anything else (including the Round 19 hash 14a23d36.., the Round 32 substitute, any other panel)."""
import hashlib, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
PANEL_R36_LM_F32_SHA256 = "e46d4bb73d16adeb02262361325b2a6ff578ae436b1374a7725a0a240f7e9928"     # 12 x 24389 LE float32 of panel-R36
PANEL_R36_NPZ_SHA256    = "a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c"     # models/panel12.npz built by build_r36.py
R19_LM_F32_SHA256       = "14a23d3619fa02dfb6aa20efafdd0fc0ff633c83d8dc5f02ac4d5d035b996297"     # retired gate
ok = True
dat = {}
for ln in open(os.path.join(HERE, "engine.dat")):
    k = ln.split(None, 1)
    if k and k[0] in ("PANEL_SHA256", "NREG", "PANEL_PATH"): dat[k[0]] = k[1].strip()
blob = open(os.path.join(HERE, dat["PANEL_PATH"]), "rb").read()
h = hashlib.sha256(blob).hexdigest()
for name, cond in (("panel_lm.f32 size == 12*24389*4", len(blob) == 12 * 29 ** 3 * 4), ("engine.dat NREG == 12", dat["NREG"] == "12"),
                   ("sha256(panel_lm.f32) == engine.dat PANEL_SHA256", h == dat["PANEL_SHA256"]),
                   ("== panel-R36 LM blob sha256", h == PANEL_R36_LM_F32_SHA256), ("!= retired Round 19 gate 14a23d36..", h != R19_LM_F32_SHA256)):
    print(("PASS " if cond else "FAIL ") + name); ok &= cond
if len(sys.argv) > 1:                                    # optional: path to panel12.npz -> also check the npz hash and that its LM equals the blob
    import numpy as np
    n = hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest()
    lm = np.load(sys.argv[1])["LM"].reshape(12, -1).astype("<f4").tobytes()
    for name, cond in (("panel12.npz sha256 == panel-R36", n == PANEL_R36_NPZ_SHA256), ("npz LM bytes == panel_lm.f32", lm == blob)):
        print(("PASS " if cond else "FAIL ") + name); ok &= cond
print("PANEL GATE:", "panel-R36 OK" if ok else "NOT panel-R36 - do not run the self-test as a gate")
sys.exit(0 if ok else 1)
