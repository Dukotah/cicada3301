#!/usr/bin/env python3
"""
A1-font glyph extractor.
Segment runic glyphs from a 400dpi relikd render, then cluster instances of
each rune by exact pixel shape to detect glyph variants.

Approach:
 1. binarize (Otsu-ish, ink=dark)
 2. drop huge components (drop-caps, cross ornaments, flourishes) by bbox size
 3. find text lines by horizontal ink projection
 4. within each line, split glyphs by vertical projection gaps
    (word-separator dots '.'/'-' handled as small components, kept as tokens)
 5. emit per-glyph binary crops + coordinates
"""
import sys, os, json
import numpy as np
from PIL import Image

def load_bin(path, thresh=128):
    im = Image.open(path).convert('L')
    a = np.asarray(im)
    ink = (a < thresh).astype(np.uint8)  # 1 = ink
    return a, ink

def connected_components(ink):
    # simple flood fill labeling (4-conn via scipy if available, else BFS)
    try:
        from scipy import ndimage
        lbl, n = ndimage.label(ink)
        return lbl, n
    except Exception:
        pass
    # fallback BFS
    h, w = ink.shape
    lbl = np.zeros((h,w), np.int32)
    n = 0
    from collections import deque
    for y in range(h):
        for x in range(w):
            if ink[y,x] and lbl[y,x]==0:
                n += 1
                q = deque([(y,x)]); lbl[y,x]=n
                while q:
                    cy,cx = q.popleft()
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny,nx=cy+dy,cx+dx
                        if 0<=ny<h and 0<=nx<w and ink[ny,nx] and lbl[ny,nx]==0:
                            lbl[ny,nx]=n; q.append((ny,nx))
    return lbl, n

def main(path, outdir, page):
    os.makedirs(outdir, exist_ok=True)
    a, ink = load_bin(path)
    H, W = ink.shape
    lbl, n = connected_components(ink)
    # component stats
    from scipy import ndimage
    slices = ndimage.find_objects(lbl)
    comps = []
    for i, sl in enumerate(slices, start=1):
        if sl is None: continue
        ys, xs = sl
        h = ys.stop - ys.start
        w = xs.stop - xs.start
        area = int((lbl[sl]==i).sum())
        comps.append(dict(id=i, y0=ys.start, y1=ys.stop, x0=xs.start, x1=xs.stop,
                          h=h, w=w, area=area))
    # Heuristics: typical rune glyph height at 400dpi. Estimate from median height
    heights = sorted(c['h'] for c in comps)
    # drop caps / ornaments are >> median. dots are << median.
    med_h = heights[len(heights)//2] if heights else 0
    return comps, med_h, (H,W), lbl

if __name__ == '__main__':
    path = sys.argv[1]
    outdir = sys.argv[2]
    page = sys.argv[3] if len(sys.argv)>3 else 'p'
    comps, med_h, dims, lbl = main(path, outdir, page)
    print(f'{path}: dims={dims} ncomp={len(comps)} med_h={med_h}')
    hs = sorted(c['h'] for c in comps)
    ws = sorted(c['w'] for c in comps)
    ars = sorted(c['area'] for c in comps)
    def pct(v,p): return v[int(len(v)*p)] if v else 0
    print('h pctiles 10/50/90/99:', pct(hs,.1),pct(hs,.5),pct(hs,.9),pct(hs,.99))
    print('w pctiles 10/50/90/99:', pct(ws,.1),pct(ws,.5),pct(ws,.9),pct(ws,.99))
    print('area pctiles 10/50/90/99:', pct(ars,.1),pct(ars,.5),pct(ars,.9),pct(ars,.99))
