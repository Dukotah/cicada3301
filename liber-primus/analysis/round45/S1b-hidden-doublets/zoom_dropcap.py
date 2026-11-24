"""R45/S1b — UNBLINDED: render the page-15 drop cap that opens canon line 168 (canon 'L'), plus reference L and U
glyphs from the same line, to decide whether a U,U doublet could hide at t=3612. Run from liber-primus/."""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, "analysis/stones"); import pipeline as P
z = json.load(open(os.path.join(HERE, "zoom.json"), encoding="utf-8"))["168"]
b, gray = P.ink("data/relikd/p15.jpg"); g = np.asarray(gray)
bx = z["boxes_x"]; y0 = min(x[2] for x in bx); y1 = max(x[3] for x in bx)
sub = g[y0 - 40:y1 + 330, 520:830]
Image.fromarray(sub.astype(np.uint8)).save(os.path.join(HERE, "crops", "zoom_dropcap_p15.png"))
print("crop", sub.shape, "line band", y0, y1)
