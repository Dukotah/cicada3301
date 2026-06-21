"""Stem-based rune segmentation.

A line is split into glyph cells at the GAPS between glyphs. Runes are tall;
between two runes there is a short vertical whitespace gutter even when the
column-projection never reaches zero (serifs/feet can bridge). We segment by:
  1. column ink projection over the band.
  2. cut points = local minima of the projection that are below a fraction of
     the line's typical glyph-column ink AND spaced by ~ the glyph pitch.
The glyph pitch is estimated from the median spacing of detected vertical stems
(columns with ink over >X% of band height), which is robust.
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pipeline as P


def stems(line_ink, frac=0.55, merge=8):
    bh = line_ink.shape[0]
    colink = line_ink.sum(0)
    st = colink > frac * bh
    xs = np.where(st)[0]
    groups = []
    s = prev = None
    for x in xs:
        if s is None:
            s = x
        elif x - prev > merge:
            groups.append((s + prev) // 2)
            s = x
        prev = x
    if s is not None:
        groups.append((s + prev) // 2)
    return groups, colink


def estimate_pitch(all_stem_centers):
    diffs = []
    for cs in all_stem_centers:
        for i in range(1, len(cs)):
            d = cs[i] - cs[i - 1]
            if d > 8:
                diffs.append(d)
    if not diffs:
        return 50
    diffs.sort()
    return diffs[len(diffs) // 2]


def split_line(line_ink, pitch, valley_frac=0.30):
    """Return list of (cx0, cx1) glyph cell boundaries using projection valleys
    spaced ~pitch apart."""
    bh = line_ink.shape[0]
    colink = line_ink.sum(0).astype(float)
    W = len(colink)
    xs = np.where(colink > 1)[0]
    if len(xs) == 0:
        return []
    lo, hi = xs.min(), xs.max() + 1
    # candidate cut columns: local minima below valley_frac*median glyph ink
    inkvals = colink[lo:hi]
    typ = np.median(inkvals[inkvals > 0.15 * bh]) if np.any(inkvals > 0.15 * bh) else bh
    thresh = valley_frac * typ
    cuts = [lo]
    x = lo
    while x < hi:
        nx = x + pitch
        if nx >= hi:
            break
        # search window around nx for the deepest low column
        w0, w1 = int(nx - pitch * 0.4), int(nx + pitch * 0.4)
        w0, w1 = max(lo, w0), min(hi, w1)
        seg = colink[w0:w1]
        j = int(np.argmin(seg)) + w0
        cuts.append(j)
        x = j
    cuts.append(hi)
    cuts = sorted(set(cuts))
    cells = [(cuts[i], cuts[i + 1]) for i in range(len(cuts) - 1)]
    cells = [c for c in cells if c[1] - c[0] > 6]
    return cells
