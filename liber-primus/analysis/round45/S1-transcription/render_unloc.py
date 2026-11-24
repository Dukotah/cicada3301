"""Render the 3 unaligned-line items as exact-box pairs. Lines 399 and 432 are the FIRST clean lines of images
36 and 39 (segment counts 23 == canon 23; alignment.json is off by one there, see alignment_audit.json).
Uses only (image, line 0, pos) from sealed location fields; canon not printed."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP); sys.path.insert(0, os.path.join(LP, "analysis", "stones")); import pipeline as P
H = 170
FIRST_LINE_OF = {399: 36, 432: 39}
sealed = json.load(open(os.path.join(HERE, "sealed_manifest.json"), encoding="utf-8"))["items"]
def crop(a, box, pad=10):
    y0, y1 = max(0, box["y0"] - pad), box["y1"] + pad; x0, x1 = max(0, box["x0"] - pad - 14), box["x1"] + pad + 14
    sub = a[y0:y1, x0:x1].astype(np.float32).copy(); m = np.ones_like(sub, dtype=bool)
    m[box["y0"] - y0:box["y1"] - y0, box["x0"] - x0:box["x1"] - x0] = False; sub[m] = 255 - (255 - sub[m]) * 0.18
    im = Image.fromarray(sub.astype(np.uint8)); return im.resize((max(1, int(im.width * H / im.height)), H), Image.LANCZOS)
ents = []
for iid, r in sealed.items():
    if r["kind"] != "unloc": continue
    n = FIRST_LINE_OF[r["gline"]]; lines, b, g = P.segment_image(f"data/relikd/p{n}.jpg"); a = np.asarray(g)
    L = [L for L in lines if len(L) >= 10][0]; assert len(L) == 23
    j = r["pos_in_line"]; ims = [crop(a, L[j]), crop(a, L[j + 1])]
    w = sum(i.width for i in ims) + 24; pair = Image.new("L", (w, H), 255); pair.paste(ims[0], (0, 0)); pair.paste(ims[1], (ims[0].width + 24, 0))
    ents.append((iid, pair))
out = Image.new("L", (3 * 420, H + 34), 255); d = ImageDraw.Draw(out); f = ImageFont.truetype("arial.ttf", 20)
for k, (iid, im) in enumerate(ents):
    out.paste(im, (k * 420 + 5, 2)); d.text((k * 420 + 6, H + 6), iid, fill=0, font=f)
out.save(os.path.join(HERE, "crops", "unloc_pairs.png"))
