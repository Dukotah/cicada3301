"""L5 / A-04 — render labelled max-zoom montages of payload cells for visual reading.

    python3 montage.py calib          # the pre-registered blind calibration sample
    python3 montage.py contested      # the 6 contested cells, 3 independent passes
    python3 montage.py cells 25 175   # arbitrary indices

Writes PNGs under ./crops/ . Crops are rendered artifacts and are gitignored per
CLAUDE.md ("rendered PNG/JPG crops" -> ignore, a committed script rebuilds them).
"""
import json
import os
import random
import sys

from PIL import Image, ImageDraw

import grid

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "crops")
os.makedirs(OUT, exist_ok=True)

CONTESTED = [25, 175, 182, 199, 215, 237]
CONFLICT = [25, 45, 50, 165, 172, 175, 182, 199, 215, 237, 246]


def calib_sample(n=40, seed=3301):
    pool = [i for i in range(256) if i not in CONFLICT]
    return sorted(random.Random(seed).sample(pool, n))


def render(indices, name, scale=6, pad=12, cols=4, label=True):
    with open(os.path.join(HERE, "grid.json")) as f:
        g = json.load(f)
    ims = []
    for i in indices:
        page, j = grid.idx_to_cell(i)
        x0, y0, x1, y1 = g[page][j]
        im = Image.open(os.path.join(grid.IMG, page + ".jpg")).convert("L")
        box = (max(0, x0 - pad), max(0, y0 - pad), min(2400, x1 + pad), min(3600, y1 + pad))
        c = im.crop(box)
        c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
        ims.append((i, c))
    cw = max(c.width for _, c in ims)
    ch = max(c.height for _, c in ims)
    lab = 46 if label else 0
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("L", (cols * (cw + 16), rows * (ch + lab + 16)), 255)
    d = ImageDraw.Draw(sheet)
    for k, (i, c) in enumerate(ims):
        r, cc = divmod(k, cols)
        x = cc * (cw + 16) + 8
        y = r * (ch + lab + 16) + 8
        if label:
            d.text((x + 4, y + 8), f"#{i}", fill=0)
        sheet.paste(c, (x, y + lab))
        d.rectangle([x - 2, y + lab - 2, x + c.width + 2, y + lab + c.height + 2], outline=160)
    p = os.path.join(OUT, name + ".png")
    sheet.save(p)
    print(p, sheet.size)
    return p


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "calib":
        s = calib_sample()
        print("calibration indices:", s)
        for k in range(0, len(s), 8):
            render(s[k:k + 8], f"calib_{k // 8}", scale=6, cols=4)
    elif mode == "contested":
        # three independent passes: different padding, scale and presentation order
        render(CONTESTED, "contested_pass1", scale=6, pad=12, cols=3)
        render(list(reversed(CONTESTED)), "contested_pass2", scale=9, pad=4, cols=2)
        render(sorted(CONTESTED, key=lambda x: x % 7), "contested_pass3", scale=12, pad=20, cols=2)
    elif mode == "cells":
        idx = [int(a) for a in sys.argv[2:]]
        render(idx, "cells_" + "_".join(map(str, idx)), scale=10, cols=3)
