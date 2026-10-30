#!/usr/bin/env python3
"""R35-B2 leg R30-B1 FULL (T2 + folly + canon). Original round30 run.py source exec'd with only: HERE -> arm dir,
BLOBS paths substituted, pycryptodome -> shim (adds AES.encrypt for the original positive control). usage: run_b1.py <arm>
arm in control|superseded|promoted"""
import os, sys, json, shutil
LANE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(LANE, "..", "..", ".."))
arm = sys.argv[1]
OUT = os.path.join(LANE, "R30-B1", arm); os.makedirs(OUT, exist_ok=True); os.chdir(OUT)
os.environ["GNUPGHOME"] = "gnupghome"; os.makedirs("gnupghome", exist_ok=True)
sys.path.insert(0, os.path.join(LANE, "shim")); B1 = os.path.join(LP, "analysis", "round30", "B1-blob-crypto"); sys.path.insert(0, B1)
import battery
cdir = {"control": "superseded", "superseded": "superseded", "promoted": "promoted"}[arm]
battery.BLOBS.update({"T2": os.path.join(LANE, "inputs", "T2", "T2.bin"), "folly": os.path.join(LANE, "inputs", "folly", "folly.bin"),
                      "canon": os.path.join(LANE, "inputs", cdir, "canon_256.bin")})
src = open(os.path.join(B1, "run.py"), encoding="utf-8").read()
if arm == "control":
    src = src.split("# ---------------------------------------------------------------- load blobs")[0] + \
          "\njson.dump(out, open(os.path.join(HERE,'results.json'),'w'), indent=1)\n"
a = "HERE = os.path.dirname(os.path.abspath(__file__))"
assert a in src; src = src.replace(a, "HERE = %r" % OUT)
a = "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))"
assert a in src; src = src.replace(a, "pass")
exec(compile(src, "run.py[%s]" % arm, "exec"), {"__name__": "run", "__file__": os.path.join(B1, "run.py")})
shutil.rmtree("gnupghome", ignore_errors=True)
