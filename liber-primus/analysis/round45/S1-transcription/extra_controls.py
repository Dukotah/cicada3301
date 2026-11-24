"""Addendum A3: 20 extra reader controls from 73.jpg (seed 45014), same crop glue as build_set.py.
Labels via whole-page reading-order alignment with drop-cap offset 1 (A2). Sealed to extra_controls_sealed.json."""
import json, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP); sys.path.insert(0, os.path.join(LP, "analysis", "stones")); import pipeline as P
CTRL = os.path.join(os.path.dirname(LP), "corpus", "A-primary-artifacts", "cijhho123", "2014", "Liber Primus", "liber primus images full", "73.jpg")
H = 170
R = [c for c in open("data/krisyotam_runes.txt", encoding="utf-8").read().split("%")[55] if c in P.RUNES]
lines, b, gray = P.segment_image(CTRL); g = np.asarray(gray).astype(np.float32)
Ls = [L for L in lines if len(L) >= 3]; B = [x for L in Ls for x in L]; assert len(B) == len(R) - 1
# exclude the boxes already used as controls (replay of build_set's count matching, same as relabel_controls.py)
sealed = json.load(open(os.path.join(HERE, "sealed_manifest.json"), encoding="utf-8"))["items"]
clines = [c for c in ([ch for ch in l if ch in P.RUNES] for l in open("data/krisyotam_runes.txt", encoding="utf-8").read().split("%")[55].split("/")) if c]
replay, ci = {}, 0
for L in Ls:
    while ci < len(clines) and len(clines[ci]) != len(L): ci += 1
    if ci >= len(clines): break
    for j, box in enumerate(L): replay[(ci, j)] = box
    ci += 1
used = {(replay[(r["cline"], r["pos_in_line"])]["x0"], replay[(r["cline"], r["pos_in_line"])]["y0"]) for r in sealed.values() if r["frame"] == "C" and r["img"] == "73.jpg"}
cand = [i for i, x in enumerate(B) if (x["x0"], x["y0"]) not in used]
pick = random.Random(45014).sample(cand, 20)
def crop(box, pad=10):
    y0, y1 = max(0, box["y0"] - pad), box["y1"] + pad; x0, x1 = max(0, box["x0"] - pad - 14), box["x1"] + pad + 14
    sub = g[y0:y1, x0:x1].copy(); m = np.ones_like(sub, dtype=bool)
    m[box["y0"] - y0:box["y1"] - y0, box["x0"] - x0:box["x1"] - x0] = False; sub[m] = 255 - (255 - sub[m]) * 0.18
    im = Image.fromarray(sub.astype(np.uint8)); return im.resize((max(1, int(im.width * H / im.height)), H), Image.LANCZOS)
f = ImageFont.truetype("arial.ttf", 20); sealed2 = {}
for mi in range(2):
    out = Image.new("L", (4 * 200, 3 * (H + 34)), 255); d = ImageDraw.Draw(out)
    for k, i in enumerate(pick[mi * 10:(mi + 1) * 10]):
        iid = f"X{mi * 10 + k:02d}"; sealed2[iid] = {"frame": "C2", "img": "73.jpg", "box_index": i, "canon": R[i + 1]}
        r, c = divmod(k, 4); out.paste(crop(B[i]), (c * 200 + 5, r * (H + 34) + 2)); d.text((c * 200 + 6, r * (H + 34) + H + 6), iid, fill=0, font=f)
    out.save(os.path.join(HERE, "crops", f"ctrl2_{mi}.png"))
json.dump(sealed2, open(os.path.join(HERE, "extra_controls_sealed.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(sealed2))
