"""L3 -- the band reader (shared module).

Wraps the VALIDATED R9 template-DP instrument (`analysis/retranscribe/read.py` +
`templates.npz` + the stored 29-class bijection in `retranscribe/diff_report.json`).
The forced re-segmentation instrument of round12/frontB is deliberately NOT used: it
fails its own positive control at 12.9%.

Everything here uses ONE code path -- `read_strip()` -- so the calibration number
measured on solved control pages is a number about the same machine that reads the
ornament bands.
"""
import os, sys, json
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
LP = HERE
while LP != os.path.dirname(LP) and os.path.basename(LP) != 'liber-primus':
    LP = os.path.dirname(LP)
# liber-primus/  (located by name so this module works from any lane depth)
ROOT = os.path.normpath(os.path.join(LP, '..'))                      # repo root
RT = os.path.join(LP, 'analysis', 'retranscribe')
sys.path.insert(0, os.path.join(LP, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS                     # noqa: E402

PAD_H, PAD_W = 128, 136
MINCLASS = 100


def load_templates():
    t = np.load(os.path.join(RT, 'templates.npz'))
    X, label, sizes, centres = t['X'], t['label'], t['sizes'], t['centres']
    kh, kw = t['keys_h'], t['keys_w']
    cover = np.bincount(label, weights=sizes, minlength=label.max() + 1)
    keep = [c for c in range(len(cover)) if cover[c] >= MINCLASS]
    tmpl = []
    for c in keep:
        i = centres[c]
        h, w = int(kh[i]), int(kw[i])
        canvas = X[i].reshape(PAD_H, PAD_W).astype(np.float32)
        top = (PAD_H - h) // 2
        left = (PAD_W - w) // 2
        tmpl.append((c, canvas[top:top + h, left:left + w]))
    return tmpl


def load_mapping():
    d = json.load(open(os.path.join(RT, 'diff_report.json')))
    return {int(k): int(v) for k, v in d['mapping'].items()}


def decode_line(ink, tmpl, band_h):
    """DP over columns -> [(class_id, x_start, cost)].  Verbatim R9 semantics."""
    Wl = ink.shape[1]
    costs = {}
    for cid, T in tmpl:
        th, tw = T.shape
        if tw >= Wl:
            continue
        best = None
        for dy in (-3, -1, 0, 1, 3):
            top = (band_h - th) // 2 + dy
            if top < 0 or top + th > band_h:
                continue
            sub = ink[top:top + th]
            corr = fftconvolve(sub, T[::-1, ::-1], mode='valid')[0]
            box = np.convolve(sub.sum(0), np.ones(tw), mode='valid')
            mism = T.sum() + box - 2.0 * corr
            best = mism if best is None else np.minimum(best, mism)
        if best is not None:
            costs[cid] = (best, tw)
    colink = ink.sum(0)
    INF = 1e18
    f = np.full(Wl + 1, INF)
    bk = [None] * (Wl + 1)
    f[0] = 0.0
    for x in range(Wl):
        if f[x] == INF:
            continue
        nc = f[x] + colink[x] * 3.0 + 0.5
        if nc < f[x + 1]:
            f[x + 1] = nc
            bk[x + 1] = ('skip', x)
        for cid, (m, tw) in costs.items():
            if x + tw > Wl or x >= len(m):
                continue
            nc = f[x] + m[x] + 6.0
            if nc < f[x + tw]:
                f[x + tw] = nc
                bk[x + tw] = ('g', x, cid, float(m[x]))
    out = []
    x = Wl
    while x > 0 and bk[x] is not None:
        b = bk[x]
        if b[0] == 'g':
            out.append((b[2], b[1], b[3]))
            x = b[1]
        else:
            x = b[1]
    out.reverse()
    return out


_pagecache = {}


def page_ink(path):
    if path not in _pagecache:
        a = np.asarray(Image.open(path).convert('L'))
        _pagecache[path] = (a < 128).astype(np.float32)
        if len(_pagecache) > 6:
            k = next(iter(_pagecache))
            if k != path:
                del _pagecache[k]
    return _pagecache[path]


def read_strip(path, y0, y1, x0=None, x1=None, tmpl=None):
    """THE one code path. Reads a horizontal strip of a page image."""
    ink = page_ink(path)
    band = ink[max(0, y0):min(ink.shape[0], y1)]
    if x0 is not None:
        band = band[:, max(0, x0):min(ink.shape[1], x1)]
        xoff = max(0, x0)
    else:
        xoff = 0
    cols = np.where(band.sum(0) > 0)[0]
    if len(cols) == 0:
        return []
    lo, hi = int(cols[0]), int(cols[-1]) + 1
    sub = band[:, lo:hi]
    seq = decode_line(sub, tmpl, sub.shape[0])
    return [(int(c), int(x + lo + xoff), float(k)) for c, x, k in seq]


def row_bands(path, y0=0, y1=None, x0=0, x1=None, min_gap=8, min_h=12):
    """Split a region into horizontal ink rows (projection profile)."""
    ink = page_ink(path)
    y1 = ink.shape[0] if y1 is None else y1
    x1 = ink.shape[1] if x1 is None else x1
    prof = ink[y0:y1, x0:x1].sum(1)
    on = prof > 0
    out, s = [], None
    gap = 0
    for i, v in enumerate(on):
        if v:
            if s is None:
                s = i
            gap = 0
        else:
            if s is not None:
                gap += 1
                if gap >= min_gap:
                    if i - gap - s >= min_h:
                        out.append((y0 + s, y0 + i - gap + 1))
                    s = None
                    gap = 0
    if s is not None and len(on) - s >= min_h:
        out.append((y0 + s, y1))
    return out


# --------------------------------------------------------------- components
from scipy import ndimage                                            # noqa: E402


def components(path, min_area=6):
    """Connected components of the ink.  Returns dict of arrays
    (x0,y0,x1,y1,area,h,w) sorted by y0."""
    ink = page_ink(path)
    lab, n = ndimage.label(ink > 0)
    if n == 0:
        return dict(x0=np.array([]), y0=np.array([]), x1=np.array([]),
                    y1=np.array([]), area=np.array([]))
    objs = ndimage.find_objects(lab)
    areas = ndimage.sum(ink > 0, lab, index=np.arange(1, n + 1))
    x0 = np.array([s[1].start for s in objs])
    x1 = np.array([s[1].stop for s in objs])
    y0 = np.array([s[0].start for s in objs])
    y1 = np.array([s[0].stop for s in objs])
    keep = areas >= min_area
    o = np.argsort(y0[keep])
    return dict(x0=x0[keep][o], y0=y0[keep][o], x1=x1[keep][o], y1=y1[keep][o],
                area=areas[keep][o])


RUNE_H = (95, 135)          # measured rune body height at 2400x3600
SEP_H = (4, 30)             # inter-word separator dot


def text_rows(path, tol=0.45):
    """Rows built ONLY from rune-height components -- ornament ink (tall swirls,
    woodcuts, hairlines) cannot merge two text lines into one band."""
    c = components(path)
    h = c['y1'] - c['y0']
    m = (h >= RUNE_H[0]) & (h <= RUNE_H[1])
    idx = np.where(m)[0]
    if not len(idx):
        return [], c, m
    order = idx[np.argsort(c['y0'][idx])]
    rows, cur = [], [order[0]]
    for i in order[1:]:
        ytop = min(c['y0'][j] for j in cur)
        ybot = max(c['y1'][j] for j in cur)
        if c['y0'][i] < ybot - tol * (ybot - ytop):
            cur.append(i)
        else:
            rows.append(cur)
            cur = [i]
    rows.append(cur)
    out = []
    for r in rows:
        out.append(dict(y0=int(min(c['y0'][j] for j in r)),
                        y1=int(max(c['y1'][j] for j in r)),
                        x0=int(min(c['x0'][j] for j in r)),
                        x1=int(max(c['x1'][j] for j in r)),
                        n=len(r), idx=[int(j) for j in r]))
    return out, c, m


# ------------------------------------------------- component-filtered ink maps
_labcache = {}


def labelled(path):
    if path not in _labcache:
        ink = page_ink(path)
        lab, n = ndimage.label(ink > 0)
        objs = ndimage.find_objects(lab)
        areas = ndimage.sum(ink > 0, lab, index=np.arange(1, n + 1))
        _labcache.clear()
        _labcache[path] = (lab, objs, areas)
    return _labcache[path]


def comp_table(path, min_area=6):
    lab, objs, areas = labelled(path)
    x0 = np.array([s[1].start for s in objs]); x1 = np.array([s[1].stop for s in objs])
    y0 = np.array([s[0].start for s in objs]); y1 = np.array([s[0].stop for s in objs])
    ids = np.arange(1, len(objs) + 1)
    k = areas >= min_area
    return dict(id=ids[k], x0=x0[k], y0=y0[k], x1=x1[k], y1=y1[k], area=areas[k])


def ink_without(path, drop_ids):
    """Ink map with the given component ids erased."""
    lab, objs, areas = labelled(path)
    ink = page_ink(path).copy()
    if len(drop_ids):
        m = np.isin(lab, np.asarray(list(drop_ids)))
        ink[m] = 0.0
    return ink


def text_ink(path, maxh=200, maxw=420):
    """Ink with 'large' components (vine swirls, woodcuts, drop-caps) erased.
    Returns (ink, dropped_component_table)."""
    c = comp_table(path)
    h = c['y1'] - c['y0']; w = c['x1'] - c['x0']
    drop = (h > maxh) | (w > maxw)
    return ink_without(path, c['id'][drop]), {k: v[drop] for k, v in c.items()}


def rows_from_ink(ink, min_gap=10, min_h=25):
    prof = ink.sum(1)
    on = prof > 0
    out, s, gap = [], None, 0
    for i, v in enumerate(on):
        if v:
            if s is None:
                s = i
            gap = 0
        else:
            if s is not None:
                gap += 1
                if gap >= min_gap:
                    if i - gap - s >= min_h:
                        out.append((s, i - gap + 1))
                    s, gap = None, 0
    if s is not None and len(on) - s >= min_h:
        out.append((s, len(on)))
    return out


def read_ink_strip(ink, y0, y1, tmpl, x0=None, x1=None):
    band = ink[max(0, y0):min(ink.shape[0], y1)]
    xoff = 0
    if x0 is not None:
        band = band[:, max(0, x0):min(ink.shape[1], x1)]
        xoff = max(0, x0)
    cols = np.where(band.sum(0) > 0)[0]
    if len(cols) == 0:
        return []
    lo, hi = int(cols[0]), int(cols[-1]) + 1
    sub = band[:, lo:hi]
    seq = decode_line(sub, tmpl, sub.shape[0])
    return [(int(c), int(x + lo + xoff), float(k)) for c, x, k in seq]


def read_scaled(ink, y0, y1, tmpl, x0=None, x1=None, target_h=125):
    """Read a band that is TOO SHORT for the rune templates to fit, by isotropically
    upscaling it to rune height first.  Tests the hypothesis 'this band is runes set at a
    smaller size'.  Costs are rescaled by the area factor so they stay comparable."""
    from PIL import Image as _I
    band = ink[max(0, y0):min(ink.shape[0], y1)]
    xoff = 0
    if x0 is not None:
        band = band[:, max(0, x0):min(ink.shape[1], x1)]
        xoff = max(0, x0)
    cols = np.where(band.sum(0) > 0)[0]
    if len(cols) == 0 or band.shape[0] < 4:
        return []
    lo, hi = int(cols[0]), int(cols[-1]) + 1
    sub = band[:, lo:hi]
    s = float(target_h) / sub.shape[0]
    if s <= 1.05:
        return []
    im = _I.fromarray((sub * 255).astype(np.uint8))
    im = im.resize((max(1, int(round(sub.shape[1] * s))), target_h), _I.LANCZOS)
    big = (np.asarray(im) > 127).astype(np.float32)
    seq = decode_line(big, tmpl, big.shape[0])
    return [(int(c), int(x / s + lo + xoff), float(k) / (s * s)) for c, x, k in seq]
