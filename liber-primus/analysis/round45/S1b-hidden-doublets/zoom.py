"""R45/S1b — UNBLINDED zoom of count-discrepancy lines (canon printed). Small crops (<=600 px) for re-inspection.
Prints box geometry and every ink component in the line band (incl. ones the segmenter's size filter dropped).
Run: PYTHONUTF8=1 python zoom.py"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP); sys.path.insert(0, os.path.join(LP, "analysis", "stones")); sys.path.insert(0, os.path.join(LP, "src"))
import pipeline as P  # noqa: E402
from lp import gematria as gp  # noqa: E402
gl, po = P.global_lines()
SL = json.load(open(os.path.join(HERE, "sealed_lines.json"), encoding="utf-8"))
byg = {r["gline"]: r for r in SL.values()}
cm = json.load(open("analysis/round45/S1-transcription/corrected_map.json"))
JOBS = {147: (8, 13), 154: (8, 13), 74: (0, 3), 168: (0, 21)}
out = {}
for G, (a, b) in JOBS.items():
    n = byg[G]["img"]
    lines, bm, gray = P.segment_image(f"data/relikd/p{n}.jpg"); g = np.asarray(gray)
    clean = [L for L in lines if len(L) >= 10]
    ci = next(r["clean_i"] for r in cm[str(n)] if r["true_gline"] == G)
    boxes = clean[ci]
    y0 = min(x["y0"] for x in boxes) - 10; y1 = max(x["y1"] for x in boxes) + 10
    # all ink components in the band
    lbl, k = ndimage.label(bm[y0:y1]); comps = []
    for sl in ndimage.find_objects(lbl):
        ys, xs = sl
        if (ys.stop - ys.start) >= 20:
            comps.append([int(xs.start), int(xs.stop), int(ys.start + y0), int(ys.stop + y0)])
    comps.sort()
    canon = [gp.RUNE_TO_TRANS[c] for c in gl[G]]
    bb = boxes[a:b]
    X0 = (min(x["x0"] for x in bb) - 140) if a == 0 else (min(x["x0"] for x in bb) - 20)
    X1 = max(x["x1"] for x in bb) + 20
    if G == 168:
        X0 = min(x["x0"] for x in boxes) - 160; X1 = max(x["x1"] for x in boxes) + 20
    X0 = max(0, X0)
    sub = Image.fromarray(g[y0:y1, X0:X1].astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(sub)
    for i, x in enumerate(boxes):
        if X0 <= x["x0"] < X1:
            d.rectangle([x["x0"] - X0, x["y0"] - y0, x["x1"] - X0, x["y1"] - y0], outline=(255, 0, 0))
            d.text((x["x0"] - X0 + 2, 2), str(i), fill=(255, 0, 0))
    s = 600 / max(sub.size)
    if G == 168:  # long line: split in 2
        w = sub.width // 2
        for h in range(2):
            p = sub.crop((h * w, 0, (h + 1) * w + 40, sub.height)); s2 = 600 / max(p.size)
            p.resize((int(p.width * s2), int(p.height * s2))).save(os.path.join(HERE, "crops", f"zoom_gl{G}_{h}.png"))
    else:
        sub.resize((int(sub.width * min(1, s)), int(sub.height * min(1, s)))).save(os.path.join(HERE, "crops", f"zoom_gl{G}.png"))
    out[G] = {"img": n, "canon": canon, "nseg": len(boxes),
              "boxes_x": [[x["x0"], x["x1"], x["y0"], x["y1"]] for x in boxes],
              "ink_components_x": comps}
    print("gline", G, "img", n, "canon", len(canon), " ".join(canon))
    print("  boxes", len(boxes), [[x["x0"], x["x1"], x["y1"] - x["y0"]] for x in boxes])
    print("  ink comps (h>=20)", len(comps), [[c[0], c[1], c[3] - c[2]] for c in comps])
json.dump(out, open(os.path.join(HERE, "zoom.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
