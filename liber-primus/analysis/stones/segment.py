"""Segmentation library for Liber Primus relikd vector renders.

Approach:
- binarize (ink = dark)
- detect text-line bands via row profile over a central column window (excludes side artwork)
- within each band, connected components; drop small components (word-separator dots,
  stray artwork specks); each remaining component = one rune glyph (multi-stem runes
  are single CCs in this font).
- BUT some runes may split into 2 non-touching strokes; we merge components whose
  x-gap is below a threshold AND that are both full-height, when needed.

Returns per page: list of lines; each line = list of glyph bounding boxes (x0,x1,y0,y1)
in full-page coordinates.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

RUNES = set('ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ')


def load_bin(path, thr=128):
    im = Image.open(path).convert('L')
    a = np.asarray(im)
    return (a < thr).astype(np.uint8), a


def detect_bands(b, cx0=480, cx1=1820, min_h=40, min_ink=3):
    core = b[:, cx0:cx1]
    row = core.sum(1)
    inrow = row > min_ink
    bands = []
    s = None
    for y, v in enumerate(inrow):
        if v and s is None:
            s = y
        if not v and s is not None:
            bands.append((s, y))
            s = None
    if s is not None:
        bands.append((s, len(inrow)))
    return [(s, e) for s, e in bands if e - s > min_h]


def components_in_band(b, y0, y1, cx0=480, cx1=1900):
    """Connected components within a band, restricted to text column."""
    sub = b[y0:y1, cx0:cx1]
    lbl, n = ndimage.label(sub)
    objs = ndimage.find_objects(lbl)
    comps = []
    for i, sl in enumerate(objs):
        ys, xs = sl
        h = ys.stop - ys.start
        w = xs.stop - xs.start
        area = int((lbl[sl] == i + 1).sum())
        comps.append({
            'x0': xs.start + cx0, 'x1': xs.stop + cx0,
            'y0': ys.start + y0, 'y1': ys.stop + y0,
            'h': h, 'w': w, 'area': area,
        })
    comps.sort(key=lambda c: c['x0'])
    return comps


def segment_line(b, y0, y1, cx0=480, cx1=1900, min_h_frac=0.35, merge_gap=0):
    """Return glyph boxes for a single line band, and the dropped dots."""
    bandh = y1 - y0
    comps = components_in_band(b, y0, y1, cx0, cx1)
    if not comps:
        return [], []
    maxh = max(c['h'] for c in comps)
    minh = max(40, int(min_h_frac * bandh))
    glyphparts = [c for c in comps if c['h'] >= minh]
    dots = [c for c in comps if c['h'] < minh]
    # merge components with tiny x-gap (split strokes of one rune)
    merged = []
    for c in glyphparts:
        if merged and c['x0'] - merged[-1]['x1'] < merge_gap:
            m = merged[-1]
            m['x1'] = max(m['x1'], c['x1'])
            m['y0'] = min(m['y0'], c['y0'])
            m['y1'] = max(m['y1'], c['y1'])
            m['area'] += c['area']
            m['w'] = m['x1'] - m['x0']
        else:
            merged.append(dict(c))
    return merged, dots


def segment_page(path, cx0=480, cx1=1900, merge_gap=4):
    b, gray = load_bin(path)
    bands = detect_bands(b, cx0=cx0, cx1=min(cx1, 1820))
    lines = []
    for (y0, y1) in bands:
        glyphs, dots = segment_line(b, y0, y1, cx0, cx1, merge_gap=merge_gap)
        lines.append({'y0': y0, 'y1': y1, 'glyphs': glyphs, 'dots': dots})
    return lines, b, gray


def canon_pages(path='data/krisyotam_runes.txt'):
    t = open(path, encoding='utf-8').read()
    chunks = t.split('%')
    pages = []
    for ch in chunks:
        lines = [l for l in ch.split('/') if any(c in RUNES for c in l)]
        pl = []
        for l in lines:
            seq = [c for c in l if c in RUNES]
            pl.append(seq)
        pages.append(pl)
    return pages
