#!/usr/bin/env python3
"""Regenerate corpus/B-liber-primus/crops/ -- the glyph neighbourhoods at the
henkman/liberprimus reading conflicts on LP2 pages 33 and 35.

Those two conflicts sit in the UNSOLVED corpus, so no plaintext can adjudicate
them. The page image is the only ground truth available. The images used here are
the archived onion7 renders, SHA-1-pinned in
`liber-primus/analysis/stego/provenance.json` (56/56 match).

Line and column coordinates are DERIVED, not eyeballed:
  * the line band is found from the row-wise ink profile of the page,
  * the glyph column is found from the column-wise ink profile inside that band,
  * the glyph ordinal inside the line comes from `PAGES.json`
    (`segment_boundaries.line_break_offsets`).

Run:  PYTHONUTF8=1 python corpus/B-liber-primus/make_crops.py
Outputs are rendered PNGs -- derived data, gitignored; this script rebuilds them.
"""
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
IMGD = os.path.join(ROOT, "liber-primus", "data", "relikd")
OUT = os.path.join(HERE, "crops")

# Conflicts to image, from CONFLICT-henkman-2016.json.
# (page, rune_index, canon_glyph, henkman_glyph, output basename)
TARGETS = [
    (33, 100, "ᛒ B", "ᚹ W", "p33_rune100"),
    (33, 115, "ᚹ W", "ᚹ W", "p33_rune115_W_reference"),  # in-line control
    (33, 117, "ᛒ B", "ᚹ W", "p33_rune117"),
    (35, 155, "ᚣ Y", "ᛒ B", "p35_rune155"),
    (35, 160, "ᛒ B", "(absent)", "p35_rune160"),
]


def ink_bands(arr, axis, thresh=200):
    """Contiguous runs along `axis` that contain any ink."""
    ink = (arr < thresh).sum(axis=axis) > 0
    runs, s = [], None
    for i, v in enumerate(ink):
        if v and s is None:
            s = i
        elif not v and s is not None:
            runs.append((s, i - 1))
            s = None
    if s is not None:
        runs.append((s, len(ink) - 1))
    return runs


def body_lines(page):
    """Row bands of the runic body text, one entry per written line.

    Three complications, all handled from the pixels:
      * a red drop cap spans three text lines, so the raw row profile fuses
        those three into one tall band -> split on the recovered line pitch;
      * decorative header/footer glyph clusters also produce bands -> rejected
        because their horizontal ink extent is far narrower than a text line;
      * the '...' stanza separator produces a short band -> same rejection.
    """
    a = np.asarray(Image.open(os.path.join(IMGD, "p%d.jpg" % page)).convert("L"))
    raw = [b for b in ink_bands(a, 1) if b[1] - b[0] > 8]
    heights = sorted(b[1] - b[0] for b in raw)
    h = heights[len(heights) // 2]                        # modal single-line height
    tops = sorted(b[0] for b in raw)
    d = [b - a2 for a2, b in zip(tops, tops[1:])]
    pitch = int(round(np.median([x for x in d if h < x <= 2 * h])))
    out = []
    for lo, hi in raw:
        cols = ink_bands(a[lo:hi + 1, :], 0)
        if not cols or cols[-1][1] - cols[0][0] < 900:    # decoration, not a text line
            continue
        n = max(1, int(round((hi - lo + 1) / float(pitch))))
        for k in range(n):
            out.append((lo + k * pitch, lo + k * pitch + h))
    return out, h, pitch


def main():
    os.makedirs(OUT, exist_ok=True)
    pages = json.load(open(os.path.join(HERE, "PAGES.json"), encoding="utf-8"))["pages"]
    for page, idx, canon_g, henk_g, name in TARGETS:
        rec = pages[page]
        assert rec["page_index"] == page
        lb = rec["segment_boundaries"]["line_break_offsets"]
        starts = [0] + lb
        # runic line ordinal (skip zero-length lines: those are blank-line stanza breaks)
        runic, col = 0, None
        for i, s in enumerate(starts):
            e = starts[i + 1] if i + 1 < len(starts) else rec["n_runes"]
            if e == s:
                continue
            if s <= idx < e:
                col = idx - s
                break
            runic += 1
        assert col is not None, (page, idx)

        body, h, pitch = body_lines(page)
        n_written = sum(1 for i, s in enumerate(starts)
                        if (starts[i + 1] if i + 1 < len(starts) else rec["n_runes"]) > s)
        assert len(body) == n_written, (
            "page %d: %d image lines vs %d transcription lines" % (page, len(body), n_written))
        y0, y1 = body[runic]
        img = Image.open(os.path.join(IMGD, "p%d.jpg" % page))
        arr = np.asarray(img.convert("L"))[y0:y1 + 1, :]
        groups = ink_bands(arr, 0)
        # drop the drop-cap: on p33 the red initial occupies the leftmost wide run
        print("page %2d rune %3d  runic-line %d col %2d  band y=%d..%d  %d ink groups"
              % (page, idx, runic, col, y0, y1, len(groups)))
        img.crop((450, y0 - 12, 2000, y1 + 12)).resize(
            (int(1550 * 1.6), int((y1 - y0 + 24) * 1.6)), Image.LANCZOS
        ).save(os.path.join(OUT, name + "_line.png"))

    # the hand-verified tight crops (x windows read off the ink-group tables above)
    tight = [
        (33, (1180, 1905, 1300, 2035), 6, "p33_rune100_B_tight.png"),
        (33, (1080, 1905, 1470, 2035), 4, "p33_rune100_context.png"),
        (33, (1290, 2095, 1400, 2225), 6, "p33_rune117_B_tight.png"),
        (33, (1180, 2095, 1410, 2225), 5, "p33_rune115W_vs_rune117B.png"),
        (35, (590, 2020, 720, 2150), 6, "p35_rune155_Y_tight.png"),
        (35, (815, 2020, 915, 2150), 6, "p35_rune160_B_tight.png"),
        (35, (590, 2020, 920, 2150), 5, "p35_runes155-160_context.png"),
    ]
    for page, box, sc, name in tight:
        im = Image.open(os.path.join(IMGD, "p%d.jpg" % page)).crop(box)
        im.resize((im.width * sc, im.height * sc), Image.LANCZOS).save(os.path.join(OUT, name))
    for page in (33, 35):
        im = Image.open(os.path.join(IMGD, "p%d.jpg" % page))
        im.resize((600, 900)).save(os.path.join(OUT, "_overview_p%d.png" % page))
    print("wrote %d files to %s" % (len(os.listdir(OUT)), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
