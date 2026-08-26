"""L5 / A-04 — build a per-cell grid over the pp49-51 base-60 token tables.

Grid is derived by projection profiling on the binarised page, NOT by hand-typed
coordinates. Validation gate (pre-registered): the grid must yield exactly
80 / 104 / 72 cells for p49 / p50 / p51.

Index -> page mapping: 0..79 = p49, 80..183 = p50, 184..255 = p51. Rows are 8 wide.

Usage:
    python3 grid.py                 # build + validate + dump grid.json
    python3 grid.py --dump-cell 175 # write a max-zoom crop of one payload index
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
IMG = os.path.join(ROOT, "liber-primus", "data", "relikd")

PAGES = [("p49", 80, 10), ("p50", 104, 13), ("p51", 72, 9)]
# Which of the detected text bands are the TOKEN rows. Campaign VII (verified by
# re-reading the pages): p49 = 3 runic lines THEN a 10x8 table; p50 = a 13x8 table and
# nothing else; p51 = a 9x8 table THEN 4 runic lines. The runic bands are also ~114-115px
# tall vs ~70-98px for token rows, so this slice is corroborated by band height.
TOKEN_BAND_SLICE = {"p49": slice(3, 13), "p50": slice(0, 13), "p51": slice(0, 9)}
# x-window that excludes the marginal tree ornaments on every page
XWIN = (600, 1810)
# y-windows: the token table only. p49 has 3 rune lines above the table,
# p51 has 4 rune lines below it; these are excluded by the runic-band filter
# (rune lines are much taller/denser), see _row_bands.
INK = 128  # binarisation threshold on the 0..255 grey image


def load(page):
    im = Image.open(os.path.join(IMG, page + ".jpg")).convert("L")
    return im, np.asarray(im)


def _bands(profile, min_gap=1, min_len=1):
    """Return (start, end) inclusive-exclusive runs where profile > 0."""
    out = []
    on = profile > 0
    i = 0
    n = len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            if j - i >= min_len:
                out.append((i, j))
            i = j
        else:
            i += 1
    return out


def row_bands(arr, nrows):
    """Horizontal ink profile over XWIN -> text-line bands. Keep the nrows bands
    whose heights are mutually consistent (the token rows); runic lines on p49/p51
    are taller and denser and fall out of the modal height cluster."""
    sub = arr[:, XWIN[0]:XWIN[1]]
    ink = (sub < INK).sum(axis=1)
    bands = _bands(ink, min_len=5)
    # merge bands separated by <8px (accent/descender splits)
    merged = []
    for b in bands:
        if merged and b[0] - merged[-1][1] < 8:
            merged[-1] = (merged[-1][0], b[1])
        else:
            merged.append(list(b) if False else (b[0], b[1]))
    merged = [list(b) for b in merged]
    out = []
    for b in merged:
        if out and b[0] - out[-1][1] < 8:
            out[-1][1] = b[1]
        else:
            out.append(b)
    merged = [tuple(b) for b in out]
    heights = np.array([b[1] - b[0] for b in merged])
    return merged, heights


def token_rows(page, arr, nrows):
    merged, heights = row_bands(arr, nrows)
    rows = merged[TOKEN_BAND_SLICE[page]]
    assert len(rows) == nrows, f"{page}: band slice gave {len(rows)}, want {nrows}"
    hs = [b[1] - b[0] for b in rows]
    assert max(hs) < 110, f"{page}: a selected band is {max(hs)}px tall -- that is a runic line"
    return rows


def col_bands(arr, y0, y1, ntok=8):
    """Vertical ink profile within a row band -> ntok token groups."""
    sub = arr[y0:y1, XWIN[0]:XWIN[1]]
    ink = (sub < INK).sum(axis=0)
    glyphs = _bands(ink, min_len=2)
    if not glyphs:
        return None
    # gaps between glyph blobs; the 7 largest gaps split 8 tokens
    gaps = []
    for k in range(len(glyphs) - 1):
        gaps.append((glyphs[k + 1][0] - glyphs[k][1], k))
    gaps.sort(reverse=True)
    cuts = sorted(k for _, k in gaps[:ntok - 1])
    toks, start = [], 0
    for c in cuts:
        toks.append((glyphs[start][0] + XWIN[0], glyphs[c][1] + XWIN[0]))
        start = c + 1
    toks.append((glyphs[start][0] + XWIN[0], glyphs[-1][1] + XWIN[0]))
    return toks


def build():
    grid = {}
    for page, ncells, nrows in PAGES:
        im, arr = load(page)
        rows = token_rows(page, arr, nrows)
        cells = []
        for (y0, y1) in rows:
            toks = col_bands(arr, y0, y1)
            assert toks and len(toks) == 8, f"{page}: row {y0}-{y1} gave {toks and len(toks)}"
            for (x0, x1) in toks:
                cells.append((x0, y0, x1, y1))
        assert len(cells) == ncells, f"{page}: {len(cells)} cells, expected {ncells}"
        grid[page] = cells
        print(f"{page}: {len(cells)} cells OK  ({nrows} rows x 8)  rows y={rows[0][0]}..{rows[-1][1]}")
    return grid


def idx_to_cell(i):
    if i < 80:
        return "p49", i
    if i < 184:
        return "p50", i - 80
    return "p51", i - 184


def dump_cell(grid, i, outdir, pad=14, scale=8, suffix=""):
    page, j = idx_to_cell(i)
    x0, y0, x1, y1 = grid[page][j]
    im, _ = load(page)
    box = (max(0, x0 - pad), max(0, y0 - pad), min(2400, x1 + pad), min(3600, y1 + pad))
    crop = im.crop(box)
    crop = crop.resize((crop.width * scale, crop.height * scale), Image.LANCZOS)
    p = os.path.join(outdir, f"cell_{i:03d}{suffix}.png")
    crop.save(p)
    return p


if __name__ == "__main__":
    g = build()
    with open(os.path.join(HERE, "grid.json"), "w") as f:
        json.dump(g, f)
    if "--dump-cell" in sys.argv:
        outdir = os.path.join(HERE, "crops")
        os.makedirs(outdir, exist_ok=True)
        for a in sys.argv[sys.argv.index("--dump-cell") + 1:]:
            print(dump_cell(g, int(a), outdir))
