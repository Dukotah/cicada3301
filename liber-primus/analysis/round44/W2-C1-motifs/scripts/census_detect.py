"""R44 / W2-C1 census glue — figural-region detector (PREREG section 4).

ONE code path used by the plant (PC1) and the real census: detect(page_image_path) ->
candidate figural regions with bboxes/centroids, crops saved. The agent classifier then
reads the crops + full pages.

Method (fixed in PREREG before first run):
  - luminance Y; ink masks at Y<128 (black) and Y<200 (pale/grey);
  - 1/2-scale connected components (8-conn), merge components whose bboxes are within
    24 px (full-scale) of each other;
  - text-line suppression: detect text-line bands from the horizontal ink-row profile;
    a region overlapping >= 2 text bands over >= 70% of its area is text, not figural;
  - candidate iff merged bbox > 110 px in BOTH dims, or > 200 px in one dim with
    aspect < 10.
"""
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.dirname(HERE)
LP = os.path.abspath(os.path.join(CELL, "..", "..", ".."))
RELIKD = os.path.join(LP, "data", "relikd")

SCALE = 2                     # work at 1/2 scale
MERGE_GAP = 24                # full-scale px
MIN_BOTH = 110                # full-scale px
MIN_ONE = 200
MAX_ASPECT = 10.0
BLACK_T = 128
PALE_T = 200


def load_Y(path):
    im = Image.open(path).convert("L")
    return np.asarray(im, dtype=np.uint8)


def load_Y_red(path):
    """(Y, red_mask). Red ink (the P1 channel) is excluded from the BLACK text/figural
    mask so tall red marginal glyphs cannot weld text lines together (control-phase
    repair 2, run.log)."""
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)
    Y = np.asarray(Image.open(path).convert("L"), dtype=np.uint8)
    red = (a[:, :, 0] - a[:, :, 1] > 40) & (a[:, :, 0] > 100)
    return Y, red


def text_bands(Y, red=None):
    """Rows belonging to rune-text lines, from the black-ink row profile of the central
    column band (margins excluded so marginal art does not register as text)."""
    ink = (Y < BLACK_T)
    if red is not None:
        ink = ink & ~red
    H, W = ink.shape
    prof = ink[:, int(0.12 * W):int(0.88 * W)].mean(axis=1)
    thr = max(0.02, 0.15 * (prof.max() if prof.max() > 0 else 1))
    rows = prof > thr
    # bands = runs of text rows, closed over small gaps (<=10 px)
    lab, n = ndimage.label(rows.astype(np.int8))
    bands = []
    for i in range(1, n + 1):
        idx = np.where(lab == i)[0]
        bands.append((int(idx[0]), int(idx[-1])))
    merged = []
    for b in bands:
        if merged and b[0] - merged[-1][1] <= 10:
            merged[-1] = (merged[-1][0], b[1])
        else:
            merged.append(b)
    # keep bands with plausible glyph-line height (25..140 px full scale)
    return [b for b in merged if 25 <= (b[1] - b[0]) <= 160]


def _merge_boxes(boxes, gap):
    """Greedy merge of bboxes closer than gap. boxes: [y0,y1,x0,x1]."""
    boxes = [list(b) for b in boxes]
    changed = True
    while changed:
        changed = False
        out = []
        while boxes:
            b = boxes.pop()
            for o in out:
                if not (b[0] > o[1] + gap or o[0] > b[1] + gap or
                        b[2] > o[3] + gap or o[2] > b[3] + gap):
                    o[0] = min(o[0], b[0]); o[1] = max(o[1], b[1])
                    o[2] = min(o[2], b[2]); o[3] = max(o[3], b[3])
                    changed = True
                    break
            else:
                out.append(b)
        boxes = []
        if changed:
            boxes, out = out, []
        else:
            return out
    return out


def detect(path, pale=True):
    """Return (regions, bands). Each region: dict(bbox=[y0,y1,x0,x1] full-scale,
    centroid, w, h, mask_kind)."""
    Y, red = load_Y_red(path)
    bands = text_bands(Y, red)
    Ys = Y[::SCALE, ::SCALE]
    reds = red[::SCALE, ::SCALE]
    W = Y.shape[1]
    # text-column bounds measured from the band rows' own column ink profile
    # (control-phase repair 3: the fixed 12%/88% proxy was off by ~300 px on pages with
    # wide margins, making the text-run drop fire on margin motifs)
    colL, colR = int(0.12 * W), int(0.88 * W)
    bink = (Y < BLACK_T) & ~red
    brows = np.zeros(Y.shape[0], dtype=bool)
    for (b0, b1) in bands:
        brows[b0:b1] = True
    if brows.any():
        cprof = bink[brows].mean(axis=0)
        cols = np.where(cprof > 0.15 * cprof.max())[0] if cprof.max() > 0 else None
        if cols is not None and len(cols):
            colL, colR = int(cols.min()), int(cols.max())
    regions = []
    for kind, thr in (("black", BLACK_T),) + ((("pale", PALE_T),) if pale else ()):
        ink = Ys < thr
        if kind == "black":
            ink = ink & ~reds
        # close small gaps so drawings with thin strokes connect
        ink = ndimage.binary_closing(ink, structure=np.ones((3, 3)))
        lab, n = ndimage.label(ink, structure=np.ones((3, 3)))
        if n == 0:
            continue
        sl = ndimage.find_objects(lab)
        boxes = []
        for s in sl:
            if s is None:
                continue
            y0, y1 = s[0].start * SCALE, s[0].stop * SCALE
            x0, x1 = s[1].start * SCALE, s[1].stop * SCALE
            h, w = y1 - y0, x1 - x0
            if h < 40 and w < 40:        # too small to ever reach candidate size
                continue
            # ADDENDUM (control phase, see run.log): drop per-component text-glyph runs
            # BEFORE merging — a component whose height is <=160 px and whose vertical
            # extent lies >=60% inside detected text bands is rune text, not figural.
            if h <= 160:
                inb = sum(max(0, min(y1, b1) - max(y0, b0)) for (b0, b1) in bands)
                incol = max(0, min(x1, colR) - max(x0, colL))
                if inb >= 0.60 * h and incol >= 0.80 * w:
                    continue
            boxes.append([y0, y1, x0, x1])
        for b in _merge_boxes(boxes, MERGE_GAP):
            y0, y1, x0, x1 = b
            h, w = y1 - y0, x1 - x0
            big = (h > MIN_BOTH and w > MIN_BOTH) or \
                  ((h > MIN_ONE or w > MIN_ONE) and max(h, w) / max(1, min(h, w)) < MAX_ASPECT)
            if not big:
                continue
            # text suppression
            cover = 0
            for (b0, b1) in bands:
                ov = max(0, min(y1, b1) - max(y0, b0))
                if ov > 0.5 * (b1 - b0):
                    cover += ov
            n_bands = sum(1 for (b0, b1) in bands
                          if max(0, min(y1, b1) - max(y0, b0)) > 0.5 * (b1 - b0))
            if n_bands >= 2 and cover >= 0.70 * h:
                continue
            regions.append(dict(bbox=[int(y0), int(y1), int(x0), int(x1)],
                                centroid=[float((x0 + x1) / 2), float((y0 + y1) / 2)],
                                w=int(w), h=int(h), mask_kind=kind))
    # cross-kind dedupe: drop a region contained (>=80% area) in another
    keep = []
    regions.sort(key=lambda r: -(r["w"] * r["h"]))
    for r in regions:
        y0, y1, x0, x1 = r["bbox"]
        dup = False
        for k in keep:
            Y0, Y1, X0, X1 = k["bbox"]
            iy = max(0, min(y1, Y1) - max(y0, Y0)); ix = max(0, min(x1, X1) - max(x0, X0))
            if iy * ix >= 0.8 * (y1 - y0) * (x1 - x0):
                dup = True
                break
        if not dup:
            keep.append(r)
    return keep, bands


def save_crops(path, regions, outdir, tag):
    im = Image.open(path)
    outs = []
    for i, r in enumerate(regions):
        y0, y1, x0, x1 = r["bbox"]
        pad = 30
        c = im.crop((max(0, x0 - pad), max(0, y0 - pad),
                     min(im.width, x1 + pad), min(im.height, y1 + pad)))
        fn = os.path.join(outdir, "%s_r%02d.png" % (tag, i))
        c.save(fn)
        r["crop"] = os.path.basename(fn)
        outs.append(fn)
    return outs


def main(pages, outdir, imgdir=RELIKD, prefix="p"):
    os.makedirs(outdir, exist_ok=True)
    all_out = {}
    for p in pages:
        path = os.path.join(imgdir, "%s%d.jpg" % (prefix, p))
        if not os.path.exists(path):
            path = os.path.join(imgdir, "%s%d.png" % (prefix, p))
        regs, bands = detect(path)
        save_crops(path, regs, outdir, "p%02d" % p)
        all_out["p%d" % p] = dict(n_regions=len(regs), regions=regs, n_text_bands=len(bands))
        print("p%d: %d candidate regions, %d text bands" % (p, len(regs), len(bands)))
    return all_out


if __name__ == "__main__":
    pages = [int(a) for a in sys.argv[1:]] or list(range(56))
    out = main(pages, os.path.join(CELL, "crops"))
    json.dump(out, open(os.path.join(CELL, "results", "detect.json"), "w"), indent=1)
