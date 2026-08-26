"""L5 / A-04 - extra scrutiny for idx 215, the only cell contested in BOTH glyph
positions (witness tokens say '1O' = 84, scream314's decimal column says '05' = 5).

Renders one strip: the contested cell's two glyphs beside labelled uncontested exemplars
of every competing class -- digits 0/1/5 and symbols O/Q/0/G/C. Rendered at native scale
so the comparison is of actual stroke geometry, not of a resampled approximation.

    python3 compare215.py
"""
import json
import os

from PIL import Image, ImageDraw

import grid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CANON = os.path.join(ROOT, "liber-primus", "analysis", "pp49_51", "canon_256.bin")
ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx"
OUT = os.path.join(HERE, "crops")

# cell index -> (label, which half of the cell to show)
ROWS = [
    ("CONTESTED #215", 215, "both"),
    ("digit '1' exemplar #4", 4, "both"),
    ("digit '0' exemplar #13", 13, "both"),
    ("symbol '5' exemplar #39", 39, "both"),
    ("symbol 'O' exemplar #41", 41, "both"),
    ("symbol 'O' exemplar #93", 93, "both"),
    ("symbol 'Q' exemplar #52", 52, "both"),
    ("symbol 'Q' exemplar #130", 130, "both"),
    ("symbol '0' exemplar #168", 168, "both"),
    ("symbol 'G' exemplar #61", 61, "both"),
]


def main():
    with open(os.path.join(HERE, "grid.json")) as f:
        g = json.load(f)
    canon = open(CANON, "rb").read()
    scale, pad = 9, 12
    tiles = []
    for label, i, _ in ROWS:
        page, j = grid.idx_to_cell(i)
        x0, y0, x1, y1 = g[page][j]
        im = Image.open(os.path.join(grid.IMG, page + ".jpg")).convert("L")
        box = (max(0, x0 - pad), max(0, y0 - pad), min(2400, x1 + pad), min(3600, y1 + pad))
        c = im.crop(box)
        c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
        tok = ("?? contested" if i == 215
               else ALPHA[canon[i] // 60] + ALPHA[canon[i] % 60])
        tiles.append((label + "   token=" + tok, c))

    cw = max(t[1].width for t in tiles)
    ch = max(t[1].height for t in tiles)
    cols = 5
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("L", (cols * (cw + 18), rows * (ch + 40 + 18)), 255)
    d = ImageDraw.Draw(sheet)
    for k, (label, im) in enumerate(tiles):
        r, cc = divmod(k, cols)
        x = cc * (cw + 18) + 9
        y = r * (ch + 40 + 18) + 9
        d.text((x + 4, y + 8), label, fill=0)
        sheet.paste(im, (x, y + 40))
        d.rectangle([x - 2, y + 38, x + im.width + 2, y + 40 + im.height + 2], outline=150)
    p = os.path.join(OUT, "compare215.png")
    sheet.save(p)
    print(p, sheet.size)


if __name__ == "__main__":
    main()
