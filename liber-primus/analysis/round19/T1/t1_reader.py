"""T1 -- the PER-RUNE reader.  ONE code path, used by every measurement in this lane.

Design fixed in PREREG.md sections 2.1 / 2.2 before anything was measured.

WHY THIS SHAPE
--------------
Round 8's geometry lane measured that the median glyph in these pages has a
PIXEL-IDENTICAL twin (median nearest-neighbour Hamming 0.0000 over 13,121 glyphs,
`analysis/geometry/shape_report3.json`).  These are Ghostscript renders of a typeset
font (`round18/L1-toolchain`), not handwriting.  So the right instrument is not a
line-level dynamic program over templates (R9 / C3's `read_bands.py`, which conflates
segmentation with classification and tops out at 95.6% on the LP2 face) and it is
certainly not whole-page vision (0.145, `analysis/vision/`).  It is:

    connected component  ->  native-resolution binary crop  ->  nearest exemplar

with segmentation and classification kept strictly separate so each can be measured
on its own.

NOTHING HERE IS TRAINED ON LABELS.  Exemplars are built by unsupervised clustering of
crops; the only label information that ever enters is a 29-element cluster->rune
bijection, which is a permutation, is disclosed as canon-derived, and carries two
independent checks (PREREG 2.2 B1/B2).
"""
import os
import sys
import json
import hashlib

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
LP = HERE
while LP != os.path.dirname(LP) and os.path.basename(LP) != 'liber-primus':
    LP = os.path.dirname(LP)
ROOT = os.path.normpath(os.path.join(LP, '..'))
RELIKD = os.path.join(LP, 'data', 'relikd')
VENDOR = os.path.join(ROOT, 'corpus', 'E-tooling', 'vendor',
                      'cicada-solvers__documenting-cicada3301-scream314',
                      'assets', '2014', 'liber-primus-complete')
sys.path.insert(0, os.path.join(LP, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS, IDX_TO_RUNE  # noqa: E402

# ---------------------------------------------------------------- fixed constants
INK_T = 128          # geometry/segment.py and C3/l3/reader.py both use <128
MIN_AREA = 40        # verbatim geometry/segment.py
MIN_H, MIN_W = 6, 4  # verbatim geometry/segment.py
RUNE_H = (95, 135)   # C3/l3/reader.py RUNE_H, measured rune body height at 2400x3600

_ink_cache = {}


def page_ink(path):
    if path not in _ink_cache:
        a = np.asarray(Image.open(path).convert('L'))
        if len(_ink_cache) > 8:
            _ink_cache.clear()
        _ink_cache[path] = (a < INK_T)
    return _ink_cache[path]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


# ---------------------------------------------------------------- segmentation
def components(ink):
    """All ink components surviving the geometry/segment.py rejection rule."""
    lab, n = ndimage.label(ink)
    if n == 0:
        return []
    objs = ndimage.find_objects(lab)
    out = []
    for i, sl in enumerate(objs, start=1):
        ys, xs = sl
        h, w = ys.stop - ys.start, xs.stop - xs.start
        if h < MIN_H or w < MIN_W:
            continue
        sub = (lab[sl] == i)
        area = int(sub.sum())
        if area < MIN_AREA:
            continue
        out.append(dict(x0=int(xs.start), y0=int(ys.start),
                        x1=int(xs.stop), y1=int(ys.stop),
                        h=int(h), w=int(w), area=area, mask=sub))
    return out


def rune_candidates(comps):
    return [c for c in comps if RUNE_H[0] <= c['h'] <= RUNE_H[1]]


def group_rows(cands, tol=0.45):
    """Group rune candidates into text rows by vertical overlap, then order
    top-to-bottom / left-to-right.  Same rule as C3/l3/reader.py text_rows()."""
    if not cands:
        return []
    order = sorted(range(len(cands)), key=lambda i: cands[i]['y0'])
    rows, cur = [], [order[0]]
    for i in order[1:]:
        ytop = min(cands[j]['y0'] for j in cur)
        ybot = max(cands[j]['y1'] for j in cur)
        if cands[i]['y0'] < ybot - tol * (ybot - ytop):
            cur.append(i)
        else:
            rows.append(cur)
            cur = [i]
    rows.append(cur)
    rows.sort(key=lambda r: min(cands[j]['y0'] for j in r))
    return [sorted(r, key=lambda j: cands[j]['x0']) for r in rows]


def attach_inner(cands, others, xpad=2, ypad=4):
    """Attach to each rune-band component every SMALLER component nested inside its
    bounding box.

    THIS IS NOT COSMETIC.  Measured in `d9_ycomp.py`: of the 29 runes, exactly one --
    Y (the futhorc `yr`, canon rune index 26) -- is drawn as TWO disconnected pieces,
    an outline identical to U plus a detached inner stroke of median height 58 px.
    54 of 55 sampled Y glyphs carry such an inner component and NO other rune carries
    one at all.  A connected-component segmentation with a rune-height filter therefore
    silently converts every Y in the book into a U, and the two become pixel-identical
    (measured: ink 2134 vs 2133 on the same 114x53 box).  That single defect accounted
    for 100% of the impurity in this lane's first pass, and it is the same defect behind
    the `("U","Y",6)` top confusion in `analysis/retranscribe/diff_report.json`.
    """
    n_attached = 0
    for g in cands:
        extra = [c for c in others
                 if c['x0'] >= g['x0'] - xpad and c['x1'] <= g['x1'] + xpad
                 and c['y0'] >= g['y0'] - ypad and c['y1'] <= g['y1'] + ypad]
        if not extra:
            continue
        m = g['mask'].copy()
        H, W = m.shape
        for c in extra:
            dy, dx = c['y0'] - g['y0'], c['x0'] - g['x0']
            sy0, sx0 = max(0, -dy), max(0, -dx)
            ty0, tx0 = max(0, dy), max(0, dx)
            hh = min(c['h'] - sy0, H - ty0)
            ww = min(c['w'] - sx0, W - tx0)
            if hh <= 0 or ww <= 0:
                continue
            m[ty0:ty0 + hh, tx0:tx0 + ww] |= c['mask'][sy0:sy0 + hh, sx0:sx0 + ww]
        g['mask'] = m
        g['area'] = int(m.sum())
        g['n_inner'] = len(extra)
        n_attached += 1
    return n_attached


def segment_page(path):
    """THE segmentation.  Returns (glyphs, rows) where glyphs is in reading order.

    Each glyph: x0,y0,x1,y1,h,w,area,mask,row,pos_in_row,gi,n_inner.
    """
    ink = page_ink(path)
    comps = components(ink)
    cands = [dict(c) for c in comps if RUNE_H[0] <= c['h'] <= RUNE_H[1]]
    others = [c for c in comps if not (RUNE_H[0] <= c['h'] <= RUNE_H[1])]
    for g in cands:
        g.setdefault('n_inner', 0)
    attach_inner(cands, others)
    rows = group_rows(cands)
    glyphs = []
    for ri, r in enumerate(rows):
        for pi, j in enumerate(r):
            g = dict(cands[j])
            g['row'] = ri
            g['pos_in_row'] = pi
            g['gi'] = len(glyphs)
            glyphs.append(g)
    return glyphs, rows


# ---------------------------------------------------------------- classification
def crop_key(g):
    """The native-resolution binary crop, as a packed immutable key + its shape."""
    m = g['mask']
    return (m.shape[0], m.shape[1], np.packbits(m).tobytes())


def dist(a, b, max_shift=3):
    """Hamming distance between two native-resolution binary masks, minimised over a
    small translation search.  Masks of very different size are far apart by
    construction (the size mismatch counts as mismatched pixels)."""
    ha, wa = a.shape
    hb, wb = b.shape
    H = max(ha, hb) + 2 * max_shift
    W = max(wa, wb) + 2 * max_shift
    A = np.zeros((H, W), bool)
    ya, xa = (H - ha) // 2, (W - wa) // 2
    A[ya:ya + ha, xa:xa + wa] = a
    best = None
    for dy in range(-max_shift, max_shift + 1):
        for dx in range(-max_shift, max_shift + 1):
            B = np.zeros((H, W), bool)
            yb, xb = (H - hb) // 2 + dy, (W - wb) // 2 + dx
            if yb < 0 or xb < 0 or yb + hb > H or xb + wb > W:
                continue
            B[yb:yb + hb, xb:xb + wb] = b
            d = int(np.count_nonzero(A ^ B))
            if best is None or d < best:
                best = d
    return best if best is not None else 10 ** 9


class Bank:
    """Exemplar bank.  `ex` is a list of (mask, class_id); `names` maps class_id ->
    rune index (the 29-element bijection) or -1 if unmapped."""

    def __init__(self, ex, names=None):
        self.ex = ex
        self.names = names or {}
        self._by_shape = {}
        for k, (m, c) in enumerate(ex):
            self._by_shape.setdefault(m.shape, []).append(k)

    def classify(self, mask, max_shift=3, shape_slack=6):
        """Nearest exemplar.  Returns (class_id, d_best, class_id_runnerup, d_runnerup).

        Runner-up is the nearest exemplar of a DIFFERENT class -- that is the margin
        that matters for a confidence, not the second-nearest exemplar overall.
        """
        h, w = mask.shape
        cand = []
        for (eh, ew), idxs in self._by_shape.items():
            if abs(eh - h) <= shape_slack and abs(ew - w) <= shape_slack:
                cand.extend(idxs)
        if not cand:
            cand = range(len(self.ex))
        best = {}
        for k in cand:
            m, c = self.ex[k]
            d = dist(mask, m, max_shift)
            if c not in best or d < best[c]:
                best[c] = d
        if not best:
            return -1, 10 ** 9, -1, 10 ** 9
        ranked = sorted(best.items(), key=lambda kv: kv[1])
        c0, d0 = ranked[0]
        c1, d1 = ranked[1] if len(ranked) > 1 else (-1, 10 ** 9)
        return c0, d0, c1, d1


# ---------------------------------------------------------------- canon helpers
def canon_pages():
    d = json.load(open(os.path.join(LP, 'analysis', 'vision', 'canonical_pages.json'),
                       encoding='utf-8'))
    return {p['page']: p['runes'] for p in d if p['n_runes'] > 0}


def canon_indices(runes):
    return [RUNE_TO_IDX[c] for c in runes if c in RUNE_TO_IDX]


def relikd_path(p):
    return os.path.join(RELIKD, 'p%d.jpg' % p)


def vendor_path(name):
    return os.path.join(VENDOR, name)
