"""Full LP2 glyph pipeline: segment relikd images -> align to global line sequence ->
extract labeled crops -> (caller trains classifier).

Alignment is IMAGE-driven: relikd image numbering does NOT equal krisyotam page
numbering (verified: relikd p54 == krisyotam page 53). But krisyotam line order ==
relikd line order exactly (594 identical lines, pages 0-54). So we segment each image
into runic lines and match the count signature to a contiguous window of the 594-line
global sequence.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

RUNES = set('ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ')


def global_lines():
    t = open('data/krisyotam_runes.txt', encoding='utf-8').read()
    kch = t.split('%')
    lines = []
    page_of = []
    for p in range(55):
        for l in kch[p].split('/'):
            seq = [c for c in l if c in RUNES]
            if seq:
                lines.append(seq)
                page_of.append(p)
    return lines, page_of


def ink(path):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(int)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    red = (R > 110) & (G < 95) & (B < 95)
    dark = (R < 105) & (G < 105) & (B < 105)
    return (red | dark).astype(np.uint8), im.convert('L')


def runic_components(b, hmin=95, hmax=132, wmin=8, wmax=98):
    lbl, n = ndimage.label(b)
    objs = ndimage.find_objects(lbl)
    comps = []
    for i, sl in enumerate(objs):
        ys, xs = sl
        h = ys.stop - ys.start
        w = xs.stop - xs.start
        if hmin <= h <= hmax and wmin <= w <= wmax:
            comps.append({'x0': xs.start, 'x1': xs.stop, 'y0': ys.start, 'y1': ys.stop,
                          'yc': (ys.start + ys.stop) / 2, 'xc': (xs.start + xs.stop) / 2,
                          'h': h, 'w': w})
    return comps


def cluster_lines(comps, ygap=55):
    comps = sorted(comps, key=lambda c: c['yc'])
    lines = []
    cur = []
    for c in comps:
        if cur and c['yc'] - np.median([d['yc'] for d in cur]) > ygap:
            lines.append(cur)
            cur = []
        cur.append(c)
    if cur:
        lines.append(cur)
    for L in lines:
        L.sort(key=lambda c: c['x0'])
    return lines


def central_column_filter(lines, page_w=2400):
    """Drop ornament components far from the dominant text column.
    Determine text column from the median x-extent of the densest lines."""
    # collect all comps
    allc = [c for L in lines for c in L]
    if not allc:
        return lines
    xs = np.array([c['xc'] for c in allc])
    # text column is the big central cluster; estimate via median +/- robust spread
    med = np.median(xs)
    # keep comps within a generous window around center of mass of the biggest lines
    cleaned = []
    for L in lines:
        keep = [c for c in L if 380 < c['xc'] < page_w - 380]
        if keep:
            cleaned.append(keep)
    return cleaned


def segment_image(path):
    b, gray = ink(path)
    comps = runic_components(b)
    lines = cluster_lines(comps)
    lines = central_column_filter(lines)
    return lines, b, gray
