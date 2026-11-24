"""Unblinded re-inspection renders (PREREG §4).
(a) zoom_<id>_<slot>.png : 3x-height crop (no fading) of each PENDING-REINSPECTION glyph with +-2 neighbours.
(b) reloc_<id>.png       : not-read targets re-located through corrected_map.json (true line registration):
    exact box if the registered image line's count equals canon, else a window strip. These re-reads are
    UNBLINDED (canon was printed by adjudicate.py) and are labelled so in reinspect.json."""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP); sys.path.insert(0, os.path.join(LP, "analysis", "stones")); import pipeline as P
gl, po = P.global_lines(); pos_map = [(li, j) for li, L in enumerate(gl) for j in range(len(L))]
cmap = json.load(open(os.path.join(HERE, "corrected_map.json"))); align = json.load(open("analysis/stones/alignment.json"))
adj = json.load(open(os.path.join(HERE, "adjudications.json"), encoding="utf-8"))["rows"]
cache = {}
def seg(n):
    if n not in cache:
        lines, b, g = P.segment_image(f"data/relikd/p{n}.jpg"); cache[n] = ([L for L in lines if len(L) >= 10], np.asarray(g))
    return cache[n]
def find_true(line):
    for n, rows in cmap.items():
        for r in rows:
            if r["true_gline"] == line: return int(n), r["clean_i"]
    for n in range(56):  # fall back to the committed positional pairing
        if line in align[str(n)]: return n, align[str(n)].index(line)
def strip(a, boxes, lo, hi, scale):
    bb = boxes[max(0, lo):min(len(boxes), hi + 1)]
    x0 = min(b["x0"] for b in bb) - 10; x1 = max(b["x1"] for b in bb) + 10; y0 = min(b["y0"] for b in bb) - 10; y1 = max(b["y1"] for b in bb) + 10
    im = Image.fromarray(a[y0:y1, x0:x1]); return im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
for r in adj:
    v = str(r.get("verdict", ""))
    if v != "PENDING-REINSPECTION" and not v.startswith("not-read"): continue
    if os.path.exists(os.path.join(HERE, "crops", f"zoom_{r['id']}_{r['slot']}.png")) or os.path.exists(os.path.join(HERE, "crops", f"reloc_{r['id']}_{r['slot']}.png")): continue
    li, j = pos_map[r["gpos"]]
    n, ci = find_true(li); clean, a = seg(n); L = clean[ci]
    exact = len(L) == len(gl[li])
    k = j if exact else int(round(j * (len(L) - 1) / max(1, len(gl[li]) - 1)))
    if v == "PENDING-REINSPECTION":
        strip(a, L, k - 2, k + 2, 2.2).save(os.path.join(HERE, "crops", f"zoom_{r['id']}_{r['slot']}.png"))
        print("zoom", r["id"], r["slot"], "image", n, "exact" if exact else "approx", "target is the 3rd glyph" if k >= 2 else f"target index {k}")
    else:
        if exact:
            strip(a, L, k - 1, k + 1, 1.5).save(os.path.join(HERE, "crops", f"reloc_{r['id']}_{r['slot']}.png"))
            print("reloc", r["id"], r["slot"], "image", n, "EXACT: target is the middle glyph")
        else:
            strip(a, L, k - 5, k + 5, 1.0).save(os.path.join(HERE, "crops", f"reloc_{r['id']}_{r['slot']}.png"))
            print("reloc", r["id"], r["slot"], "image", n, f"WINDOW count {len(L)} vs canon {len(gl[li])}; canon line:", " ".join(P_T for P_T in []))
