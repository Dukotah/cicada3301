"""R47/T2 sizing probe (run before PREREG; prints NO canon rune of any position).
Replays S1's read set (seed 45013, as R46/S2 build.py), finds look-alike-union glyphs NOT on exact-registered
lines, and reports per target: gpos, gline, image, clean line index under repaired alignment.json (v2) and
under S1 corrected_map, box count vs canon length. Also checks whether the 4 disputed gpos are in the set."""
import json, os, random, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP)
sys.path.insert(0, os.path.join(LP, "src")); sys.path.insert(0, os.path.join(LP, "analysis", "stones"))
import pipeline as P
gl, po = P.global_lines()
pos_map = [(li, j) for li, L in enumerate(gl) for j in range(len(L))]
flat = [c for L in gl for c in L]; x = flat; N = len(flat)
start = np.cumsum([0] + [len(L) for L in gl])[:-1]
rng = random.Random(45013); F1 = []
for b in range(11):
    lo, hi = b * 5, b * 5 + 4
    F1 += rng.sample([i for i in range(N) if lo <= po[pos_map[i][0]] <= hi], 6)
FAM_S1 = [set("ᚩᚪᚫ"), set("ᚱᚹ"), set("ᛗᛞ"), set("ᚾᛁ"), set("ᛒᛖ")]
dbl = [i for i in range(N - 1) if x[i] == x[i + 1]]
near = [i for i in range(N - 1) if flat[i] != flat[i + 1] and any(flat[i] in f and flat[i + 1] in f for f in FAM_S1)]
F3 = sorted(rng.sample(near, 40)); excl = set(dbl) | set(near)
F4 = sorted(rng.sample([i for i in range(N - 1) if i not in excl], 40))
S1set = set(F1) | {i for p in dbl + F3 + F4 for i in (p, p + 1)}
U = set("ᚩᚪᚫᛗᛞᚦᚹᚱᚾᛁᛒᛖ")
cm = json.load(open("analysis/round45/S1-transcription/corrected_map.json"))
al = json.load(open("analysis/stones/alignment.json"))
exact = set(); where = {}
for n in range(56):
    for r in cm[str(n)]:
        G = r["true_gline"]
        if G is None: continue
        where[G] = (n, r["clean_i"], r["count"], r["true_len"])
        if r["count"] == r["true_len"]:
            exact.update(range(int(start[G]), int(start[G]) + len(gl[G])))
alw = {G: (int(n), i) for n, L in al.items() for i, G in enumerate(L)}
T = sorted(i for i in S1set if flat[i] in U and i not in exact)
print("S1set", len(S1set), "family", sum(flat[i] in U for i in S1set), "window-family targets", len(T))
print("disputed in T:", {g: g in T for g in (276, 5054, 6054, 9877)})
for i in T:
    G = pos_map[i][0]
    print(i, "gline", G, "j", pos_map[i][1], "cm", where.get(G), "v2", alw.get(G))
