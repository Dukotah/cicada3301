#!/usr/bin/env python3
"""
Line + vertical-gap glyph segmentation, then exact-shape clustering.

Pipeline per page:
  1. binarize (ink = pixel < THRESH)
  2. drop ornament/dropcap components (bbox height > 1.6*median rune height OR
     area huge) so cross ornaments & drop-cap don't pollute lines
  3. find text lines via horizontal projection of the cleaned ink
  4. within each line, vertical projection -> split at zero-ink columns (gaps).
     Small tokens (word separators . / -) are classified separately by width/area.
  5. For each glyph token: extract binary crop, trim to bbox.

Clustering:
  Glyphs of the SAME rune should render near-identically (font). We cluster by:
   - group by size bucket (rounded h,w)
   - within bucket, compare pixel overlap (IoU on aligned trimmed masks).
   - a "variant" = a distinct shape cluster among tokens that are otherwise the
     same rune. We can't label runes here without OCR, so we report, per size
     bucket, how many exact-shape sub-clusters exist.

Outputs JSON with per-glyph records and cluster assignments.
"""
import sys, os, json, hashlib
import numpy as np
from PIL import Image
from scipy import ndimage

THRESH = 128

def load_ink(path):
    im = Image.open(path).convert('L')
    a = np.asarray(im)
    return (a < THRESH).astype(np.uint8)

def clean_ornaments(ink, med_h):
    """remove components whose bbox height is far from rune height."""
    lbl, n = ndimage.label(ink)
    slices = ndimage.find_objects(lbl)
    keep = np.zeros_like(ink)
    removed = []
    for i, sl in enumerate(slices, start=1):
        if sl is None: continue
        ys, xs = sl
        h = ys.stop-ys.start; w = xs.stop-xs.start
        # keep glyph strokes (h <= ~1.5x rune) and separator dots (small)
        if h > 1.6*med_h or w > 1.6*med_h:
            removed.append((i,h,w)); continue
        keep[sl][lbl[sl]==i] = 1
    return keep, removed

def median_comp_height(ink):
    lbl, n = ndimage.label(ink)
    slices = ndimage.find_objects(lbl)
    hs = []
    for i, sl in enumerate(slices, start=1):
        if sl is None: continue
        ys,xs=sl; hs.append(ys.stop-ys.start)
    hs.sort()
    return hs[len(hs)//2] if hs else 0

def find_lines(ink, min_gap=8):
    rows = ink.sum(axis=1)
    ink_rows = rows > 0
    lines = []
    y = 0; H = len(rows)
    in_line=False; start=0
    for y in range(H):
        if ink_rows[y] and not in_line:
            in_line=True; start=y
        elif not ink_rows[y] and in_line:
            in_line=False; lines.append((start,y))
    if in_line: lines.append((start,H))
    # merge lines separated by tiny gaps (diacritics) — but rune lines are well separated
    return lines

def segment_line(ink, y0, y1, med_h):
    """split a line row-band into glyph tokens by vertical projection gaps."""
    band = ink[y0:y1]
    cols = band.sum(axis=0)
    ink_cols = cols > 0
    W = len(cols)
    toks=[]
    in_t=False; start=0
    for x in range(W):
        if ink_cols[x] and not in_t:
            in_t=True; start=x
        elif not ink_cols[x] and in_t:
            in_t=False; toks.append((start,x))
    if in_t: toks.append((start,W))
    return toks

def trim(mask):
    ys, xs = np.where(mask)
    if len(ys)==0: return mask
    return mask[ys.min():ys.max()+1, xs.min():xs.max()+1]

def main(path, outdir):
    os.makedirs(outdir, exist_ok=True)
    ink = load_ink(path)
    med_h = median_comp_height(ink)
    clean, removed = clean_ornaments(ink, med_h)
    lines = find_lines(clean)
    glyphs=[]
    for li,(y0,y1) in enumerate(lines):
        toks = segment_line(clean, y0, y1, med_h)
        for ti,(x0,x1) in enumerate(toks):
            sub = clean[y0:y1, x0:x1]
            tm = trim(sub)
            h,w = tm.shape
            area = int(tm.sum())
            glyphs.append(dict(line=li, tok=ti, y0=int(y0),y1=int(y1),
                               x0=int(x0),x1=int(x1), h=int(h),w=int(w),area=area,
                               mask=tm))
    return glyphs, med_h, removed, ink.shape

def classify_tokens(glyphs, med_h):
    """separate real runes from separators (dots/hyphens) by size."""
    runes=[]; seps=[]
    for g in glyphs:
        # separators: small area, short height (dots ~ small, hyphen thin+wide-ish)
        if g['h'] < 0.35*med_h and g['area'] < 0.06*med_h*med_h:
            seps.append(g)
        else:
            runes.append(g)
    return runes, seps

def cluster_exact(runes, iou_thresh=0.985):
    """cluster rune tokens by near-exact pixel shape (size-normalized alignment).
    Groups by (h,w) bucket with +-2 tolerance then IoU on max-aligned masks."""
    clusters=[]  # list of dict(rep_mask, members[idx], hw)
    def iou(m1,m2):
        H=max(m1.shape[0],m2.shape[0]); W=max(m1.shape[1],m2.shape[1])
        A=np.zeros((H,W),bool); B=np.zeros((H,W),bool)
        A[:m1.shape[0],:m1.shape[1]]=m1.astype(bool)
        B[:m2.shape[0],:m2.shape[1]]=m2.astype(bool)
        inter=(A&B).sum(); uni=(A|B).sum()
        return inter/uni if uni else 1.0
    for idx,g in enumerate(runes):
        m=g['mask']
        placed=False
        for c in clusters:
            # size gate
            if abs(c['h']-g['h'])<=3 and abs(c['w']-g['w'])<=3:
                if iou(c['rep'],m) >= iou_thresh:
                    c['members'].append(idx); placed=True; break
        if not placed:
            clusters.append(dict(rep=m, h=g['h'], w=g['w'], members=[idx]))
    return clusters

if __name__=='__main__':
    path=sys.argv[1]; outdir=sys.argv[2]
    glyphs, med_h, removed, shape = main(path, outdir)
    runes, seps = classify_tokens(glyphs, med_h)
    print(f'{path}: med_h={med_h} lines? glyph_tokens={len(glyphs)} runes={len(runes)} seps={len(seps)} ornaments_removed={len(removed)}')
    # per-line token counts
    from collections import Counter
    linec=Counter(g['line'] for g in runes)
    print('lines:', len(linec), 'runes/line:', [linec[k] for k in sorted(linec)])
