"""Q5 kill gate: score ONLY the reader-control (frame C) items. Prints nothing about other frames."""
import json, os, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src")); from lp import gematria as gp
T2R = {v: k for k, v in gp.RUNE_TO_TRANS.items()}
br = os.path.join(HERE, "blind_reads.json")
print("blind_reads sha256", hashlib.sha256(open(br, "rb").read()).hexdigest())
reads = json.load(open(br))["reads"]
sealed = json.load(open(os.path.join(HERE, "sealed_manifest.json"), encoding="utf-8"))["items"]
rl = json.load(open(os.path.join(HERE, "controls_relabel.json"), encoding="utf-8"))["items"]  # addendum A2
ok = n = 0
for iid, rec in sealed.items():
    if rec["frame"] != "C" or iid not in reads: continue
    lab = rl[iid]["new_label"]
    if lab is None: continue
    n += 1; hit = T2R[reads[iid]["read"][0]] == lab; ok += hit
    print("control", iid, reads[iid]["read"][0], gp.RUNE_TO_TRANS[lab], "OK" if hit else "MISS")
print(f"control accuracy {ok}/{n}")
