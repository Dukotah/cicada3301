"""Exemplar sheet: 10 random dataset bitmaps per look-alike class (seed 7). Output crops/ref_exemplars.png"""
import os, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src")); from lp import gematria as gp
DS = np.load(os.path.join(LP, "analysis/stones/dataset.npz"), allow_pickle=True); X, y = DS["X"], DS["y"]
rng = random.Random(7); sel = sys.argv[1] if len(sys.argv) > 1 else "ᚠᚩᚪᚫ"
out = Image.new("L", (60 + 10 * 90, len(sel) * 130), 255); d = ImageDraw.Draw(out); f = ImageFont.truetype("arial.ttf", 22)
for r_i, r in enumerate(sel):
    idx = rng.sample(list(np.flatnonzero(y == r)), 10)
    d.text((5, r_i * 130 + 50), gp.RUNE_TO_TRANS[r], fill=0, font=f)
    for k, i in enumerate(idx):
        im = Image.fromarray(((1 - X[i].reshape(56, 40)) * 255).astype(np.uint8)).resize((80, 112), Image.NEAREST)
        out.paste(im, (60 + k * 90, r_i * 130 + 5))
out.save(os.path.join(HERE, "crops", ("ref_exemplars.png" if len(sys.argv) < 3 else sys.argv[2])))
