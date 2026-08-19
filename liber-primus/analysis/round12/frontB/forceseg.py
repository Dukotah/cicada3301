"""Front B — forced per-line glyph-count re-segmentation of the dense OTP pages.

Connected-component-free. For each text line we know the target number of glyph
POSITIONS from canon (runes + word-separators + dots). We take the line's text
ink strip, isolate it from the page-border ornaments, and cut it into exactly
that many pieces at the deepest inter-glyph valleys of the vertical ink
projection. Each forced piece is then matched (label-free) to the shape-cluster
library built in analysis/retranscribe/templates.npz. Cluster->rune naming reuses
the SAME low-bandwidth 1-1 permutation the R9 audit recovered (fit on solved
pages only, never on 45-54). Finally we diff the forced read against canon on the
runes only and catalogue every disagreement.

Positive control: run the identical machinery on a solved page (p3, p5) and check
it recovers the known runes.
"""
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS

GEO = os.path.join(ROOT, 'analysis', 'geometry', 'glyphs2.npz')
IMG = os.path.join(ROOT, 'data', 'relikd')
TPL = os.path.join(ROOT, 'analysis', 'retranscribe', 'templates.npz')
PAD_H, PAD_W = 128, 136
MINCLASS = 100

# ---------------------------------------------------------------- canon
def load_canon_full():
    txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
    lines = []
    for seg in txt.split('%'):
        for ln in seg.split('/'):
            s = ln.strip().replace('\n', '')
            if any(c in RUNE_TO_IDX for c in s):
                lines.append(s)
    return lines   # list of full strings (runes + '-' + '.')

def canon_tokens(s):
    """token stream in reading order: ('r',idx) rune, ('s',) separator/dot."""
    toks = []
    for c in s:
        if c in RUNE_TO_IDX:
            toks.append(('r', RUNE_TO_IDX[c]))
        elif c in '-.':
            toks.append(('s',))
    return toks

# ---------------------------------------------------------------- templates
def load_templates():
    t = np.load(TPL)
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

# ---------------------------------------------------------------- geometry
def load_geo():
    d = np.load(GEO)
    return dict(page=d['page'], line=d['line'], x0=d['x0'], y0=d['y0'],
                x1=d['x1'], y1=d['y1'], bands=d['bands'])

def line_ids_for_page(geo, p):
    return sorted(set(int(l) for pp, l in zip(geo['page'], geo['line']) if int(pp) == p))

# ---------------------------------------------------------------- forced cut
RUNE_HMIN, RUNE_HMAX = 95, 128     # full-height rune component band

def text_strip(geo, gli, ink_page):
    """Isolate the TEXT ink of the line from page-border ornaments.

    Ornament removal (NOT glyph segmentation) uses connected components purely to
    drop the big swirls / curls / corner dots. We keep:
      - full-height rune components (height in [RUNE_HMIN,RUNE_HMAX]);
      - small dot components (word-separator '.') that sit within the rune y-band
        and inside the rune x-span.
    Everything else (swirls h~91, curls h~41, corner dots at page edge) is zeroed.
    The kept mask is then returned as a clean binary strip over the rune x-span.
    """
    m = geo['line'] == gli
    y0 = int(geo['y0'][m].min()); y1 = int(geo['y1'][m].max())
    band = ink_page[y0:y1].astype(bool)
    lab, n = ndimage.label(band)
    if n == 0:
        return band.astype(np.float32), 0, y0
    objs = ndimage.find_objects(lab)
    rune_ids, dot_cands = [], []
    for i, sl in enumerate(objs):
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        cx = (sl[1].start + sl[1].stop) // 2
        cy = (sl[0].start + sl[0].stop) // 2
        if RUNE_HMIN <= h <= RUNE_HMAX and w <= 130:
            rune_ids.append((i + 1, sl))
        elif h <= 16 and w <= 16:
            dot_cands.append((i + 1, sl, cx, cy))
    if not rune_ids:
        # degenerate: fall back to geometry box span
        x0 = int(geo['x0'][m].min()); x1 = int(geo['x1'][m].max())
        return band[:, x0:x1].astype(np.float32), x0, y0
    # Keep only the largest contiguous RUN of rune components: real text is a
    # dense evenly-spaced row; ornament remnants that survived the height filter
    # are isolated outliers separated by a large x-gap from the text block.
    rune_ids.sort(key=lambda t: t[1][1].start)
    centres = [ (sl[1].start + sl[1].stop) / 2 for _, sl in rune_ids ]
    widths = [ sl[1].stop - sl[1].start for _, sl in rune_ids ]
    medw = np.median(widths)
    # split into groups where consecutive centre gap > 3*median rune width
    groups, cur = [], [0]
    for k in range(1, len(rune_ids)):
        if centres[k] - centres[k - 1] > 3.0 * medw:
            groups.append(cur); cur = [k]
        else:
            cur.append(k)
    groups.append(cur)
    best = max(groups, key=len)
    rune_ids = [rune_ids[k] for k in best]
    xs = [sl[1].start for _, sl in rune_ids] + [sl[1].stop for _, sl in rune_ids]
    tx0, tx1 = min(xs), max(xs)
    ys = [sl[0].start for _, sl in rune_ids] + [sl[0].stop for _, sl in rune_ids]
    ty0, ty1 = min(ys), max(ys)
    keep_run = {cid for cid, _ in rune_ids}
    keep = np.zeros(n + 1, bool)
    for cid in keep_run:
        keep[cid] = True
    # keep dots that are inside the rune x-span and vertically near the mid band
    ymid = (ty0 + ty1) / 2
    for cid, sl, cx, cy in dot_cands:
        if tx0 - 5 <= cx <= tx1 + 5 and abs(cy - ymid) < (ty1 - ty0):
            keep[cid] = True
    mask = keep[lab]
    strip = mask[:, tx0:tx1].astype(np.float32)
    return strip, tx0, y0

def _zero_gaps(colink, thresh):
    """runs of columns with ink <= thresh; return their centres and widths."""
    low = colink <= thresh
    gaps = []
    x = 0
    W = len(colink)
    while x < W:
        if low[x]:
            s = x
            while x < W and low[x]:
                x += 1
            gaps.append(((s + x - 1) / 2.0, x - s))
        else:
            x += 1
    return gaps

def _ink_blobs(colink, thresh):
    """maximal runs of ABOVE-threshold ink -> (start,end) pieces, each an inked
    glyph (rune or separator dot)."""
    hi = colink > thresh
    blobs = []
    x = 0
    W = len(colink)
    while x < W:
        if hi[x]:
            s = x
            while x < W and hi[x]:
                x += 1
            blobs.append((s, x))
        else:
            x += 1
    return blobs

def forced_cuts(colink, n_pieces):
    """Segment a 1-D ink profile into EXACTLY n_pieces inked glyphs.

    We isolate inked BLOBS (runs of above-threshold ink) -- each is one glyph
    (rune or separator dot). Then FORCE the count to n_pieces:
      - if too many blobs: merge the closest-adjacent pairs (thin split strokes)
        until n_pieces remain;
      - if too few blobs: split the WIDEST blob at its deepest interior valley
        until n_pieces remain.
    Returns bounds [0, c1, ..., W] of length n_pieces+1.
    """
    W = len(colink)
    if n_pieces <= 1 or W < n_pieces:
        return [0, W]
    thresh = max(1.0, 0.10 * colink.max())
    blobs = _ink_blobs(colink, thresh)
    if not blobs:
        return list(np.linspace(0, W, n_pieces + 1).astype(int))
    blobs = [list(b) for b in blobs]
    # MERGE if too many: repeatedly merge the pair with the smallest inter-gap
    while len(blobs) > n_pieces:
        gaps = [(blobs[i + 1][0] - blobs[i][1], i) for i in range(len(blobs) - 1)]
        gaps.sort()
        _, i = gaps[0]
        blobs[i][1] = blobs[i + 1][1]
        del blobs[i + 1]
    # SPLIT if too few: split widest blob at its deepest interior column
    while len(blobs) < n_pieces:
        widths = [(b[1] - b[0], k) for k, b in enumerate(blobs)]
        widths.sort(key=lambda t: -t[0])
        _, k = widths[0]
        a, b = blobs[k]
        if b - a < 4:
            break
        seg = colink[a + 2:b - 2]
        if len(seg) == 0:
            break
        x = a + 2 + int(np.argmin(seg))
        blobs[k] = [a, x]
        blobs.insert(k + 1, [x, b])
    # build bounds at blob midpoints of gaps
    bounds = [0]
    for i in range(len(blobs) - 1):
        bounds.append((blobs[i][1] + blobs[i + 1][0]) // 2)
    bounds.append(W)
    return bounds

def match_piece(piece, tmpl):
    """Best template class for a forced piece via the R9 mismatch cost.

    Places each template on a common canvas with the piece (both centred), allows
    a small +/-3 px alignment search in x and y, and scores
        mismatch = |piece XOR template|  (Hamming over the union bbox)
    normalised by the template ink mass. Width mismatch is penalised because a
    template that is much narrower/wider than the piece leaves unexplained ink.
    """
    ph, pw = piece.shape
    if pw < 2 or piece.sum() < 3:
        return None, 1e18
    best_c, best_m = None, 1e18
    pink = piece.sum()
    for cid, T in tmpl:
        th, tw = T.shape
        H = max(ph, th) + 6
        Wc = max(pw, tw) + 6
        A = np.zeros((H, Wc), np.float32)
        A[(H - ph) // 2:(H - ph) // 2 + ph, (Wc - pw) // 2:(Wc - pw) // 2 + pw] = piece
        Bc = np.zeros((H, Wc), np.float32)
        Bc[(H - th) // 2:(H - th) // 2 + th, (Wc - tw) // 2:(Wc - tw) // 2 + tw] = T
        m = None
        for dy in (-3, -1, 0, 1, 3):
            for dx in (-3, -1, 0, 1, 3):
                Bs = np.roll(np.roll(Bc, dy, 0), dx, 1)
                mm = np.abs(A - Bs).sum()
                m = mm if m is None else min(m, mm)
        # normalise by mean ink of piece & template (symmetric)
        norm = m / max(0.5 * (pink + T.sum()), 1.0)
        if norm < best_m:
            best_m = norm; best_c = cid
    return best_c, best_m

def band_for_line(geo, gli, ink_page):
    """R9-style band: full-width slice over the line's y-extent, cropped to the
    ink column span. This is exactly analysis/retranscribe/read.py's extraction.
    """
    m = geo['line'] == gli
    ys = int(geo['y0'][m].min()); ye = int(geo['y1'][m].max())
    band = ink_page[ys:ye]
    cols = np.where(band.sum(0) > 0)[0]
    if len(cols) == 0:
        return band
    return band[:, cols[0]:cols[-1] + 1]


def read_line_forced(geo, gli, ink_page, n_runes, tmpl):
    """Forced RUNE-count template DP on the ornament-isolated text strip.

    Pipeline: text_strip() removes page-border ornaments; separator dots are
    zeroed from the ink profile (they carry no template); the exact-count DP then
    explains the remaining rune ink with EXACTLY n_runes glyphs, choosing cut
    positions and shape clusters jointly. Returns list of (class_id, cost), one
    per rune position in reading order.
    """
    import forcedp
    strip, x0, y0 = text_strip(geo, gli, ink_page)
    col = strip.sum(0).astype(np.float32)
    th = max(1.0, 0.10 * col.max())
    blobs = _ink_blobs(col, th)
    if blobs:
        peaks = [col[a:b].max() for a, b in blobs]
        medpk = np.median(peaks)
        keep = np.zeros(len(col), bool)
        for (a, b), pk in zip(blobs, peaks):
            if pk >= 0.55 * medpk and (b - a) >= 6:
                keep[a:b] = True
        strip = strip * keep[None, :]
    seq = forcedp.forced_count_decode(strip, tmpl, n_runes)
    out = [(cid, cost) for cid, x, cost in seq]
    if len(out) < n_runes:
        out += [(None, 1e18)] * (n_runes - len(out))
    return out[:n_runes]
