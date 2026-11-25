"""Q5 gate: after batch NN is frozen, print ONLY the aggregate C/W score for that batch (no per-item label,
no A/R information). python gate.py NN"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); nn = int(sys.argv[1])
reads = json.load(open(os.path.join(HERE, f"reads_batch{nn:02d}.json")))["reads"]
S = json.load(open(os.path.join(HERE, "sealed.json"), encoding="utf-8"))["items"]
import sys as _s; _s.path.insert(0, os.path.join(HERE, "..", "..", "..", "src"))
from lp import gematria as gp
T = gp.RUNE_TO_TRANS
c = [(reads[i]["read"] == T[S[i]["canon"]]) for i in reads if S[i]["frame"] == "C"]
w = [(reads[i]["read"] != T[S[i]["claimed"]]) for i in reads if S[i]["frame"] == "W"]
print(f"batch {nn}: controls correct {sum(c)}/{len(c)}; swaps caught {sum(w)}/{len(w)}; C+W ok {sum(c)+sum(w)}/{len(c)+len(w)}")
