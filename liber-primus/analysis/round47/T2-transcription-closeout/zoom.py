"""Blind zoom: enlarge a horizontal slice of one strip png (reads only crops/<id>.png, no labels).
Usage: python zoom.py T2-s01 [x0_frac x1_frac] [--ref O,A,AE]  -> crops/zoom.png
--ref appends R46/S2's solved-page reference strips (round46/S2-second-reader/crops/ref_<T>.png)."""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
S2C = os.path.join(HERE, "..", "..", "round46", "S2-second-reader", "crops")
args = sys.argv[1:]
refs = []
if "--ref" in args:
    k = args.index("--ref")
    refs = args[k + 1].split(",")
    args = args[:k] + args[k + 2:]
im = Image.open(os.path.join(HERE, "crops", f"{args[0]}.png")).convert("L")
if len(args) == 3:
    a, b = float(args[1]), float(args[2])
    im = im.crop((int(a * im.width), 0, int(b * im.width), im.height))
im = im.resize((int(im.width * 1.6), int(im.height * 1.6)))
rows = [im]
for t in refs:
    r = Image.open(os.path.join(S2C, f"ref_{t}.png")).convert("L")
    lab = Image.new("L", (r.width + 60, r.height), 255)
    lab.paste(r, (60, 0))
    ImageDraw.Draw(lab).text((5, r.height // 2), t, fill=0)
    rows.append(lab)
W = max(r.width for r in rows)
out = Image.new("L", (W, sum(r.height for r in rows)), 255)
y = 0
for r in rows:
    out.paste(r, (0, y))
    y += r.height
out.save(os.path.join(HERE, "crops", "zoom.png"))
print(out.size)
