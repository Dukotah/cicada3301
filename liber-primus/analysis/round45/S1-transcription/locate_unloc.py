"""Render the items whose canon line is not aligned to an image line (PREREG §2).
Prints location only (never canon). The unaligned line is found as the segmented line (any length) lying
between the aligned neighbour lines; the strip is the whole line (read left->right blind)."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP); sys.path.insert(0, os.path.join(LP, "analysis", "stones")); import pipeline as P
sealed = json.load(open(os.path.join(HERE, "sealed_manifest.json"), encoding="utf-8"))["items"]
align = json.load(open("analysis/stones/alignment.v1.json")); gl, po = P.global_lines()
where = {}
for n in range(56):
    for i, g in enumerate(align[str(n)]): where[g] = (n, i)
loc = {}
for iid, r in sealed.items():
    if r["kind"] != "unloc": continue
    lines_needed = sorted({r["gline"], r.get("gline2", r["gline"])})
    print(iid, r["frame"], "page", r["page"], "glines", lines_needed, "pos_in_line", r["pos_in_line"], "line lens", [len(gl[g]) for g in lines_needed])
    strips = []
    for g in lines_needed:
        prev = max(k for k in where if k < g); nxt = min(k for k in where if k > g)
        n = where[prev][0] if where[prev][0] == where.get(nxt, (None,))[0] else where[prev][0]
        lines, b, gray = P.segment_image(f"data/relikd/p{n}.jpg"); a = np.asarray(gray)
        clean = [L for L in lines if len(L) >= 10]
        y_prev = np.median([c["yc"] for c in clean[where[prev][1]]])
        y_next = np.median([c["yc"] for c in clean[where[nxt][1]]]) if where.get(nxt, (None,))[0] == n else 1e9
        cands = [L for L in lines if y_prev + 30 < np.median([c["yc"] for c in L]) < y_next - 30]
        if not cands:  # line may be on the next image's top
            print("  no candidate between neighbours on image", n, "-> try image", n + 1)
            n += 1; lines, b, gray = P.segment_image(f"data/relikd/p{n}.jpg"); a = np.asarray(gray)
            clean = [L for L in lines if len(L) >= 10]
            y_next = np.median([c["yc"] for c in clean[0]]) if clean else 1e9
            cands = [L for L in lines if np.median([c["yc"] for c in L]) < y_next - 30]
        L = max(cands, key=len)
        print("  image", n, "line segs", len(L))
        x0 = min(c["x0"] for c in L) - 15; x1 = max(c["x1"] for c in L) + 15
        y0 = min(c["y0"] for c in L) - 12; y1 = max(c["y1"] for c in L) + 12
        strips.append(Image.fromarray(a[y0:y1, x0:x1]))
    W = max(s.width for s in strips); Hh = sum(s.height + 10 for s in strips)
    out = Image.new("L", (W, Hh), 255); yy = 0
    for s in strips: out.paste(s, (0, yy)); yy += s.height + 10
    out.save(os.path.join(HERE, "crops", f"unloc_{iid}.png"))
