"""Adjudication helper for transcription cross-verification.

Detects the rune rows on an authentic LP page image (horizontal projection of
dark ink) and crops a chosen line at high zoom, so a disputed rune can be
re-read by eye against the canonical line. Pairs with the canonical line
structure (krisyotam uses '/' line breaks within a page).

Usage:
  python linecrop.py <page_index> [line_index]
    no line_index -> prints detected row bands + canonical per-line rune counts
    with line_index -> saves analysis/transcription/_p<page>_L<line>.png (zoom crop)

Image source: data/relikd/p<page>.jpg  (SHA1-verified == onion7 original).
"""
import sys, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp.gematria import RUNE_TO_IDX, RUNE_TO_TRANS  # noqa: E402

IMG = os.path.join(ROOT, "data", "relikd", "p{}.jpg")
CANON = os.path.join(ROOT, "data", "krisyotam_runes.txt")


def canonical_lines(page):
    raw = open(CANON, encoding="utf-8").read().split("%")
    if page >= len(raw):
        return []
    lines = []
    for ln in raw[page].split("/"):
        runes = "".join(c for c in ln if c in RUNE_TO_IDX)
        if runes:
            lines.append(runes)
    return lines


def detect_rows(page, dark_thresh=128, min_gap=12, min_height=20):
    im = Image.open(IMG.format(page)).convert("L")
    a = np.asarray(im)
    H, W = a.shape
    # project ink only over the CENTER text column, excluding the margin
    # cross/dagger decorations (far left/right) that span the full height.
    cx0, cx1 = int(W * 0.22), int(W * 0.78)
    center = a[:, cx0:cx1]
    cw = cx1 - cx0
    ink = (center < dark_thresh).sum(axis=1)
    on = ink > (0.01 * cw)  # a row has text if >1% of the center is dark
    bands, y = [], 0
    while y < H:
        if on[y]:
            y0 = y
            while y < H and on[y]:
                y += 1
            if y - y0 >= min_height:
                bands.append((y0, y))
        else:
            y += 1
    # merge bands separated by tiny gaps
    merged = []
    for b in bands:
        if merged and b[0] - merged[-1][1] < min_gap:
            merged[-1] = (merged[-1][0], b[1])
        else:
            merged.append(list(b))
    return [(int(a0), int(a1)) for a0, a1 in merged], (W, H)


def main():
    page = int(sys.argv[1])
    rows, (W, H) = detect_rows(page)
    clines = canonical_lines(page)
    if len(sys.argv) < 3:
        print(f"p{page}: image {W}x{H}; detected {len(rows)} ink rows; "
              f"canonical has {len(clines)} rune lines")
        for i, (y0, y1) in enumerate(rows):
            cl = clines[i] if i < len(clines) else ""
            tr = "".join(RUNE_TO_TRANS[c] for c in cl)
            print(f"  row {i:>2}: y {y0:>4}-{y1:>4} ({y1-y0:>3}px) | "
                  f"canon[{i}] {len(cl):>2} runes: {tr[:46]}")
        if len(rows) != len(clines):
            print(f"  NOTE: row count {len(rows)} != canonical line count {len(clines)} "
                  f"(decorations/margins can split rows; map by eye)")
        return
    line = int(sys.argv[2])
    y0, y1 = rows[line]
    pad = int((y1 - y0) * 0.25)
    im = Image.open(IMG.format(page)).convert("RGB")
    # crop full text width band; trim outer margins a bit
    box = (int(W * 0.18), max(0, y0 - pad), int(W * 0.82), min(H, y1 + pad))
    crop = im.crop(box)
    # upscale for legibility
    crop = crop.resize((crop.width, crop.height), Image.LANCZOS)
    out = os.path.join(HERE, f"_p{page}_L{line}.png")
    crop.save(out)
    cl = clines[line] if line < len(clines) else ""
    print(f"saved {out}  (canonical line {line}: "
          f"{''.join(RUNE_TO_TRANS[c] for c in cl)})")


if __name__ == "__main__":
    main()
