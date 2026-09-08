#!/usr/bin/env python3
"""R-lane audit part 2: FRESH adversarial parity, python-direct vs C binary."""
import json, os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
R27 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(R27, "P2-harness"))
import engine, pyref   # pyref imports the R25 pipeline verbatim

V = pyref.vectors()

# A. re-verify 6 fixed vectors against a DIRECT run of the R25 pipeline
fixed = [r for r in V["seed_vectors"] if r["seed"] in (0, 3301, 2149309687, 4294967295)]
bad = 0
for r in fixed:
    g = pyref.stage_a_full(r["seed"])
    ok = (g["pmax"] == float(r["pmax"]) and g["plain_idx"] == r["plain_idx"]
          and g["ks128"] == r["ks128"] and g["n_skips"] == r["n_skips"])
    print("vec seed %-10d py-direct pmax %r vs frozen %s -> %s" % (r["seed"], g["pmax"], r["pmax"], "OK" if ok else "MISMATCH")); bad += not ok

# B. the 6 above-cand-bar seeds from py_scores: re-score python-direct AND C
six = [342028379, 1767045001, 2992200523, 3507020799, 3602920670, 3627553781]
# C. 24 fresh seeds from MY OWN rng (not 27002, not 20260907)
rng = random.Random(987654321)
fresh = [rng.randrange(0, 2**32) for _ in range(24)]
allseeds = six + fresh
py = {w: pyref.stage_a_full(w)["pmax"] for w in allseeds}
crow = engine.score_seeds(allseeds)
cmap = {int(r["seed"]): float(r["pmax"]) for r in crow}
worst = 0.0
for w in allseeds:
    d = abs(py[w] - cmap[w]); worst = max(worst, d)
    tag = "SIX" if w in six else "fresh"
    flag = "C-FLAGGED" if cmap[w] >= 5.0 else ""
    if d > 0 or w in six:
        print("%s seed %-10d py %.15g C %.15g |d|=%.3g %s" % (tag, w, py[w], cmap[w], d, flag))
print("fresh+six parity: %d seeds, worst |d| = %.3g" % (len(allseeds), worst))
missed = [w for w in six if cmap[w] < 5.0]
print("false-reject on the 6 python-flaggable: %d %s" % (len(missed), missed))

# D. NOVEL plant at a seed of MY choosing (never used by P0/P2): 271828182
w = 271828182
plant = pyref.build_plant(w)
c120 = plant["cipher_idx"][:120]
ref = pyref.stage_a_full(w, cipher=c120)
neigh = [w-1, w, w+1, 1234567, 4000000000]
crow = engine.score_seeds(neigh, cipher_idx=c120)
cm = {int(r["seed"]): float(r["pmax"]) for r in crow}
print("novel plant seed %d: py pmax %.15g ; C pmax %.15g ; |d|=%.3g ; clears cand bar: %s"
      % (w, ref["pmax"], cm[w], abs(ref["pmax"]-cm[w]), cm[w] >= 5.0))
for x in neigh:
    if x != w:
        pyx = pyref.stage_a_full(x, cipher=c120)["pmax"]
        print("  non-true seed %d: py %.6f C %.6f |d|=%.3g (should be low+matching)" % (x, pyx, cm[x], abs(pyx-cm[x])))

# E. recovery of the novel plant's plaintext at screen level (magnet check: does the
# beam actually recover the truth, not just score high?)
full = engine.score_seeds([w], cipher_idx=c120, full=True)[0]
truth120 = plant["truth_idx"][:120]
rec = sum(a==b for a,b in zip(full["plain_idx"], truth120))/120.0
print("novel plant screen recovery vs truth: %.3f" % rec)
print("AUDIT2 verdict: %s" % ("OK" if (bad==0 and worst<=1e-9 and not missed and cm[w]>=5.0 and rec>=0.90) else "DEFECT"))
