"""Recon: rune counts that justify the offset range. Read-only."""
import os, sys, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "round11"))
import lib_numchannel as nc

print("nc dir:", [x for x in dir(nc) if not x.startswith("_")])
U = nc.unsolved()
print("unsolved len:", len(U))

# solved pages
sp = os.path.join(ROOT, "SOLVED-PAGES.json")
if os.path.exists(sp):
    d = json.load(open(sp))
    print("SOLVED-PAGES type", type(d), list(d.keys())[:10] if isinstance(d, dict) else len(d))

pj = os.path.join(ROOT, "PROBLEM.json")
if os.path.exists(pj):
    d = json.load(open(pj))
    def walk(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (dict, list)):
                    walk(v, p + "/" + k)
                else:
                    s = str(v)
                    if len(s) < 120:
                        print(f"  {p}/{k} = {s}")
    walk(d)
