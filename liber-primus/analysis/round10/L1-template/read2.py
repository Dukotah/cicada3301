"""L1-TEMPLATE stage 2b -- rebuilt label-free reader.

Why rebuild. The Round-9 read.py produced 16,245 glyphs for 13,136 canonical
runes and only 38.4% of lines came out rune-count-exact.  Diagnosis (see
class_audit.log / cost_audit.log):

  * one template per class, taken as the single most populous EXACT bitmap.
    The font renders each rune at several sub-pixel phases (1,067 distinct
    bitmaps for ~29 shapes), so a correct match against the wrong phase costs
    a whole boundary layer -- median placement cost 129 px, only 14.6% of
    placements below 20 px.  On a supposedly exact font render, a correct
    match should cost ~0.
  * with every correct match already costing ~130, the DP can pay for itself
    by SPLITTING a wide rune into two narrow ones.  Class 11 (a 10-px-wide
    bar) was used 1,289 times against a stage-1 population of 151; class 26
    (43 px wide, population 263) was never used once.  That is the whole
    3,109-glyph surplus.
  * vertical placement was searched over only dy in {-3,-1,0,1,3} around the
    band centre.

Fixes, all canon-free:
  * anti-aliased 2x down-sample of both page ink and templates.  Area-mean of
    a binary mask turns a sub-pixel phase shift into a small grey-level
    change instead of a whole boundary layer of flipped pixels.
  * up to K exact-bitmap variants per class, cost = min over variants.
  * full vertical search: 2-D 'valid' correlation covers every vertical
    placement inside the band, not a hand-picked set of offsets.
  * proper objective.  Cost = squared-error of the reconstruction + lambda per
    glyph.  Un-modelled ink costs exactly its own energy, which is what
    leaving it unexplained actually costs; no ad-hoc x3 factor.

lambda is chosen by a PLATEAU criterion on the total glyph count (canon-free):
sweep lambda, plot n(lambda), take the centre of the widest interval over which
n is stable.  No canonical label or length is consulted anywhere in this file.
"""
import os, sys, json, time
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
RT = os.path.join(ROOT, 'analysis', 'retranscribe')
GEO = os.path.join(ROOT, 'analysis', 'geometry')
IMG = os.path.join(ROOT, 'data', 'relikd')
PAD_H, PAD_W = 128, 136
MINCLASS = 100
K_VARIANTS = int(os.environ.get('KVAR', '4'))
DS = 2


def ds(a):
    """area-mean 2x down-sample of a float array"""
    h, w = a.shape
    h2, w2 = h - h % DS, w - w % DS
    return a[:h2, :w2].reshape(h2 // DS, DS, w2 // DS, DS).mean((1, 3))


def load_templates():
    t = np.load(os.path.join(RT, 'templates.npz'))
    X, label, sizes, centres = t['X'], t['label'], t['sizes'], t['centres']
    kh, kw = t['keys_h'], t['keys_w']
    cover = np.bincount(label, weights=sizes, minlength=label.max() + 1)
    keep = [c for c in range(len(cover)) if cover[c] >= MINCLASS]
    tmpl = []
    for c in keep:
        idx = np.where(label == c)[0]
        idx = idx[np.argsort(-sizes[idx])][:K_VARIANTS]
        for i in idx:
            h, w = int(kh[i]), int(kw[i])
            can = X[i].reshape(PAD_H, PAD_W).astype(np.float32)
            top, left = (PAD_H - h) // 2, (PAD_W - w) // 2
            m = can[top:top + h, left:left + w]
            tmpl.append((int(c), ds(m), int(sizes[i])))
    return tmpl, cover


def integral2(I2, th, tw):
    """sum of I2 over every th x tw window -> (H-th+1, W-tw+1)"""
    S = np.zeros((I2.shape[0] + 1, I2.shape[1] + 1), np.float64)
    S[1:, 1:] = I2.cumsum(0).cumsum(1)
    return (S[th:, tw:] - S[:-th, tw:] - S[th:, :-tw] + S[:-th, :-tw])


def line_costs(ink, tmpl):
    """for each template return (per-x min SSD, best row, width)"""
    H, W = ink.shape
    I2 = ink * ink
    out = []
    for cid, T, _ in tmpl:
        th, tw = T.shape
        if th > H or tw >= W:
            out.append(None); continue
        corr = fftconvolve(ink, T[::-1, ::-1], mode='valid')
        box = integral2(I2, th, tw)
        ssd = float((T * T).sum()) + box - 2.0 * corr
        r = np.argmin(ssd, 0)
        out.append((ssd[r, np.arange(ssd.shape[1])].astype(np.float32),
                    r.astype(np.int16), tw, cid))
    return [o for o in out if o is not None]


def decode(costs, colE, W, lam):
    INF = 1e30
    f = np.full(W + 1, INF); bk = [None] * (W + 1); f[0] = 0.0
    for x in range(W):
        if f[x] >= INF:
            continue
        nc = f[x] + colE[x]
        if nc < f[x + 1]:
            f[x + 1] = nc; bk[x + 1] = ('s', x)
        for cost, rows, tw, cid in costs:
            if x >= len(cost):
                continue
            nc = f[x] + cost[x] + lam
            if nc < f[x + tw]:
                f[x + tw] = nc; bk[x + tw] = ('g', x, cid, float(cost[x]), int(rows[x]))
    out, x = [], W
    while x > 0 and bk[x] is not None:
        b = bk[x]
        if b[0] == 'g':
            out.append((b[2], b[1], b[3], b[4])); x = b[1]
        else:
            x = b[1]
    out.reverse()
    return out, float(f[W])


def main():
    lams = [float(v) for v in os.environ.get('LAMS', '').split(',') if v]
    pages = os.environ.get('PAGES', '')
    only = set(int(v) for v in pages.split(',') if v) if pages else None
    tmpl, cover = load_templates()
    ncls = len({c for c, _, _ in tmpl})
    print('templates: %d variants over %d classes (K=%d)' % (len(tmpl), ncls, K_VARIANTS), flush=True)
    bands = np.load(os.path.join(GEO, 'glyphs2.npz'))['bands']
    if only is not None:
        keepb = [i for i, b in enumerate(bands) if b[0] in only]
    else:
        keepb = list(range(len(bands)))
    print('bands: %d' % len(keepb), flush=True)
    if not lams:
        lams = [30.0]
    res = {l: [] for l in lams}
    cur, inkp = -1, None
    t0 = time.time()
    for bi in keepb:
        p, ys, ye, ng, medh = bands[bi]
        if p != cur:
            a = np.asarray(Image.open(os.path.join(IMG, 'p%d.jpg' % p)).convert('L'))
            inkp = ds((a < 128).astype(np.float32))
            cur = p
            print('  page %d  t=%.0fs' % (p, time.time() - t0), flush=True)
        band = inkp[ys // DS:ye // DS]
        cols = np.where(band.sum(0) > 0)[0]
        if len(cols) == 0:
            for l in lams:
                res[l].append(dict(page=int(p), band=int(bi), glyphs=[]))
            continue
        x_lo, x_hi = int(cols[0]), int(cols[-1]) + 1
        sub = np.ascontiguousarray(band[:, x_lo:x_hi])
        costs = line_costs(sub, tmpl)
        colE = (sub * sub).sum(0)
        for l in lams:
            seq, tot = decode(costs, colE, sub.shape[1], l)
            res[l].append(dict(page=int(p), band=int(bi), cost=round(tot, 1),
                               glyphs=[[int(c), int((x + x_lo) * DS), round(float(k), 1), int(r)]
                                       for c, x, k, r in seq]))
    for l in lams:
        tag = ('_l%g' % l) if len(lams) > 1 else ''
        fn = os.path.join(HERE, 'read2%s.json' % tag)
        json.dump(res[l], open(fn, 'w'))
        n = sum(len(o['glyphs']) for o in res[l])
        ks = [g[2] for o in res[l] for g in o['glyphs']]
        print('lam=%-7g glyphs=%6d  median cost %.2f  frac<1: %.3f  -> %s'
              % (l, n, np.median(ks) if ks else -1,
                 float(np.mean(np.array(ks) < 1.0)) if ks else -1, os.path.basename(fn)), flush=True)
    print('elapsed %.0fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
