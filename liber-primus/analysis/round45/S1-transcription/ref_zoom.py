"""Large reference chart of look-alike classes (aggregate class means, Campaign-V dataset). Output crops/ref_zoom.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src")); from lp import gematria as gp
DS = np.load(os.path.join(LP, "analysis/stones/dataset.npz"), allow_pickle=True); X, y = DS["X"], DS["y"]
sel = "ᚠᚩᚪᚫᚱᚹᛗᛞᚾᛁᛒᛖᛉᛠᚳᛋ"
out = Image.new("L", (8 * 170, 2 * 260), 255); d = ImageDraw.Draw(out)
f = ImageFont.truetype("arial.ttf", 22)
for k, r in enumerate(sel):
    m = (1 - X[y == r].mean(0).reshape(56, 40)) * 255
    im = Image.fromarray(m.astype(np.uint8)).resize((150, 210), Image.LANCZOS)
    rr, cc = divmod(k, 8); out.paste(im, (cc * 170 + 10, rr * 260)); d.text((cc * 170 + 10, rr * 260 + 215), gp.RUNE_TO_TRANS[r], fill=0, font=f)
out.save(os.path.join(HERE, "crops", "ref_zoom.png"))
