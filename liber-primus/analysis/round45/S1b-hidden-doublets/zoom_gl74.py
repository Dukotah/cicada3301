"""R45/S1b — UNBLINDED: the merged, unboxed component at the start of canon line 74 (p6, x 764-871; canon C E)."""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, "analysis/stones"); import pipeline as P
z = json.load(open(os.path.join(HERE, "zoom.json"), encoding="utf-8"))["74"]
b, gray = P.ink("data/relikd/p6.jpg"); g = np.asarray(gray)
bx = z["boxes_x"]; y0 = min(x[2] for x in bx); y1 = max(x[3] for x in bx)
sub = Image.fromarray(g[y0 - 15:y1 + 15, 740:1000].astype(np.uint8))
sub.resize((sub.width * 2, sub.height * 2), Image.LANCZOS).save(os.path.join(HERE, "crops", "zoom_gl74_start.png"))
