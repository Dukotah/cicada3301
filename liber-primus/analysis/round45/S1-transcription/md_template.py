"""Reinspection aid for M/D calls: correlation of each crossed glyph's normalized bitmap (build_dataset.norm_crop
glue) with the M and D class means of the Campaign-V dataset. Lists every box on the given image line whose
best-of-(M,D) correlation is highest, in reading order, so the pair can be matched to canon context."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP); sys.path.insert(0, os.path.join(LP, "analysis", "stones")); sys.path.insert(0, "analysis/stones")
import pipeline as P
from build_dataset import norm_crop
DS = np.load("analysis/stones/dataset.npz", allow_pickle=True); X, y = DS["X"], DS["y"]
means = {r: X[y == r].mean(0) for r in "ᛗᛞᛖᚻ"}
def corr(a, b): a = a - a.mean(); b = b - b.mean(); return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))
for n, ci in [(41, None), (19, None)]:
    lines, b, gray = P.segment_image(f"data/relikd/p{n}.jpg"); g = np.asarray(gray)
    clean = [L for L in lines if len(L) >= 10]
    al = json.load(open("analysis/stones/alignment.json"))[str(n)]
    target_line = 455 if n == 41 else 220
    L = clean[al.index(target_line)]
    out = []
    for k, box in enumerate(L):
        v = norm_crop(g, box)
        if v is None: continue
        v = v.ravel(); s = {P_: corr(v, m) for P_, m in means.items()}
        if max(s, key=s.get) in "ᛗᛞ":
            out.append((k, round(s["ᛗ"], 3), round(s["ᛞ"], 3), "M" if s["ᛗ"] > s["ᛞ"] else "D"))
    print("image", n, "line", target_line, "(box idx, corr M, corr D, call):", out)
