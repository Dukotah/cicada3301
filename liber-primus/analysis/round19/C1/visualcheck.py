"""Round 19 / C1 -- render the contested cells beside their candidate exemplars so a SECOND
reader can check the pixel instrument's verdict directly.

L5's three visual passes exist only as a table of strings hard-coded into adjudicate_all.py
by the reader who made them. C1 cannot verify that transcript from the outside, so instead of
quoting it as evidence this script re-renders the evidence and a second reader looks at it in
this run. It is labelled honestly in RESULTS as NON-BLIND corroboration (the pixel verdict is
already known when it is read) -- corroboration is all it is claimed to be.

Each strip: the contested cell at left, then every candidate class exemplar, all at the same
magnification, drawn from the same pages.

    python3 visualcheck.py
"""
import json
import os

from PIL import Image, ImageDraw

import grid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "crops")
CANON = os.path.join(ROOT, "liber-primus", "analysis", "pp49_51", "canon_256.bin")
ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx"

# contested cell -> the classes it must be told apart from
CASES = {
    25:  "Iil L",
    45:  "lLI i",
    50:  "lLI i",
    165: "Iil L",
    172: "SsZ 5",
    175: "Iil L",
    182: "lLI i",
    199: "lLI i",
    215: "OQ0 GC",
    237: "WwVM",
    246: "Iil L",
}
SCALE = 9
PAD = 10


def exemplar_index(canon, cls, exclude):
    for i in range(256):
        if i in exclude:
            continue
        if ALPHA[canon[i] % 60] == cls:
            return i
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    canon = open(CANON, "rb").read()
    with open(os.path.join(HERE, "grid.json")) as f:
        g = json.load(f)
    conflict = set(CASES)
    ims = {p: Image.open(os.path.join(grid.IMG, p + ".jpg")).convert("L")
           for p in ("p49", "p50", "p51")}

    def crop(i):
        page, j = grid.idx_to_cell(i)
        x0, y0, x1, y1 = g[page][j]
        box = (max(0, x0 - PAD), max(0, y0 - PAD), x1 + PAD, y1 + PAD)
        c = ims[page].crop(box)
        return c.resize((c.width * SCALE, c.height * SCALE), Image.LANCZOS)

    index = {}
    for i, classes in CASES.items():
        tiles = [("cell %d  <-- READ THIS" % i, crop(i))]
        for cls in classes.replace(" ", ""):
            k = exemplar_index(canon, cls, conflict)
            if k is None:
                continue
            tiles.append(("'%s'  (cell %d, uncontested)" % (cls, k), crop(k)))
        w = sum(t[1].width for t in tiles) + 30 * len(tiles)
        h = max(t[1].height for t in tiles) + 46
        strip = Image.new("L", (w, h), 255)
        d = ImageDraw.Draw(strip)
        x = 15
        for lab, im in tiles:
            strip.paste(im, (x, 40))
            d.text((x, 14), lab, fill=0)
            d.line([(x - 8, 8), (x - 8, h - 8)], fill=160)
            x += im.width + 30
        p = os.path.join(OUT, "c1_cell%03d.png" % i)
        strip.save(p)
        index[i] = os.path.relpath(p, HERE)
        print("wrote %s  (%d tiles)" % (p, len(tiles)))
    json.dump(index, open(os.path.join(HERE, "out_visualcheck_index.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
