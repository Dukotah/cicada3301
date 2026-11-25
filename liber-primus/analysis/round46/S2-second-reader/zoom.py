"""Blind zoom helper: cut cells (by crop id) out of an already-rendered batch montage, enlarge them, and
optionally append solved-page reference strips (crops/ref_<T>.png, built from 73.jpg with the same glue).
Reads only manifest.json and crops/*.png (no labels).  Usage: python zoom.py S0101 S0105 [--ref M,D]"""
import json, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
man = {m["id"]: m for m in json.load(open(os.path.join(HERE, "manifest.json")))}
args = sys.argv[1:]; refs = []
if "--ref" in args:
    k = args.index("--ref"); refs = args[k + 1].split(","); args = args[:k] + args[k + 2:]
cells = []
for cid in args:
    m = man[cid]; k = int(cid[3:]) % 12; r, c = divmod(k, 4)
    cells.append(Image.open(os.path.join(HERE, "crops", m["montage"])).crop((c * 200, r * 236, c * 200 + 200, r * 236 + 236)))
rows = [cells]
for t in refs:
    im = Image.open(os.path.join(HERE, "crops", f"ref_{t}.png")).convert("L")
    lab = Image.new("L", (im.width + 60, 236), 255); lab.paste(im, (60, 2)); ImageDraw.Draw(lab).text((5, 100), t, fill=0)
    rows.append([lab])
W = max(sum(i.width for i in r) for r in rows); out = Image.new("L", (W, 236 * len(rows)), 255)
for ri, r in enumerate(rows):
    x = 0
    for im in r: out.paste(im, (x, ri * 236)); x += im.width
s = 1.4 if W < 1100 else 1.0
out.resize((int(W * s), int(236 * len(rows) * s))).save(os.path.join(HERE, "crops", "zoom.png"))
