"""L5 / A-04 - render the three independent visual passes over the contested cells,
plus labelled reference strips of the competing glyph classes.

Pass A: scale 10, pad 16, one cell per PNG, ascending index.
Pass B: scale 7,  pad 4,  one cell per PNG, descending index (different framing + order).
Pass C: scale 14, pad 24, one cell per PNG, order keyed on i%7 (neither ascending
        nor descending), so pass C is not primed by the previous two.

Reference strips are rendered SEPARATELY and are only consulted after the three passes
are recorded, so the passes are reads of the glyph rather than matches to a candidate.

    python3 visualpass.py
"""
import json
import os

from PIL import Image, ImageDraw

import grid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CANON = os.path.join(ROOT, "liber-primus", "analysis", "pp49_51", "canon_256.bin")
OUT = os.path.join(HERE, "crops")
ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx"
CONTESTED = [25, 175, 182, 199, 215, 237]
CONFLICT = [25, 45, 50, 165, 172, 175, 182, 199, 215, 237, 246]

PASSES = {
    "A": dict(scale=10, pad=16, order=sorted(CONTESTED)),
    "B": dict(scale=7, pad=4, order=sorted(CONTESTED, reverse=True)),
    "C": dict(scale=14, pad=24, order=sorted(CONTESTED, key=lambda x: (x % 7, x))),
}


def cellimg(g, i, scale, pad):
    page, j = grid.idx_to_cell(i)
    x0, y0, x1, y1 = g[page][j]
    im = Image.open(os.path.join(grid.IMG, page + ".jpg")).convert("L")
    box = (max(0, x0 - pad), max(0, y0 - pad), min(2400, x1 + pad), min(3600, y1 + pad))
    c = im.crop(box)
    return c.resize((c.width * scale, c.height * scale), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(HERE, "grid.json")) as f:
        g = json.load(f)
    canon = open(CANON, "rb").read()

    for name, cfg in PASSES.items():
        for k, i in enumerate(cfg["order"]):
            c = cellimg(g, i, cfg["scale"], cfg["pad"])
            p = os.path.join(OUT, "pass%s_%d_cell%03d.png" % (name, k, i))
            c.save(p)
            print(p, c.size)

    # ---- reference strips: every uncontested exemplar of the competing classes ----
    # Grouped so a strip holds one class only, labelled, at a common zoom.
    want = "IilL1Oo0QGCWwVMt5S"
    bysym = {}
    for i in range(256):
        if i in CONFLICT:
            continue
        s = ALPHA[canon[i] % 60]
        if s in want:
            bysym.setdefault(s, []).append(i)
    tiles = []
    for s in want:
        for i in bysym.get(s, [])[:4]:
            tiles.append((s, i, cellimg(g, i, 8, 10)))
    if tiles:
        cw = max(t[2].width for t in tiles)
        ch = max(t[2].height for t in tiles)
        cols = 6
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("L", (cols * (cw + 14), rows * (ch + 44 + 14)), 255)
        d = ImageDraw.Draw(sheet)
        for k, (s, i, im) in enumerate(tiles):
            r, cc = divmod(k, cols)
            x = cc * (cw + 14) + 7
            y = r * (ch + 44 + 14) + 7
            d.text((x + 4, y + 10), "'%s'  #%d" % (s, i), fill=0)
            sheet.paste(im, (x, y + 44))
            d.rectangle([x - 2, y + 42, x + im.width + 2, y + 44 + im.height + 2], outline=160)
        p = os.path.join(OUT, "reference_classes.png")
        sheet.save(p)
        print(p, sheet.size, "classes:", {s: len(bysym.get(s, [])) for s in want})


if __name__ == "__main__":
    main()
