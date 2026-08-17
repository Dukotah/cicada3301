"""L1-TEMPLATE stage 2c -- label-free reader, component-filtered.

Adds to read2.py the one thing that mattered most, and it is canon-free:

  the DP is shown ONLY the ink of components that can be runes.

Page 0 (and every page) carries, besides the runes: a multi-line ornate DROP
CAP, two large margin ornaments (the cross/dagger figures), full-height dotted
columns and single dots (the word / phrase separators), and assorted furniture.
read.py and read2.py fed all of that to the DP, which duly "explained" it with
rune templates.  Filtering by connected-component geometry removes it without
consulting any transcription:

    keep component  <=>  H_MIN <= height <= H_MAX  and  width <= 130

  * separators  : height 9-12          -> dropped
  * dotted cols : height 60-90         -> dropped
  * ornaments   : height >130 or w>130 -> dropped
  * drop caps   : height ~300-400      -> dropped  (KNOWN DEFICIT: the drop cap
                                          IS a rune; it is counted separately
                                          and reported, never silently absorbed)

Also merges the three sub-pixel-split class pairs found by cross-class shape
distance -- c15/c31 (d=0.099), c26/c29 (d=0.124), c0/c11 (both plain bars,
w=9 vs w=10) -- taking the 32 stage-1 classes to 29, which is the Gematria
Primus alphabet size recovered from the images with no labels.

No canonical rune, line length or page length is read by this file.
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
CAN = 160
MINCLASS = 100
DS = 2
H_MIN, H_MAX, W_MAX = 100, 126, 130
MERGE = [(0, 11), (15, 31), (26, 29)]      # sub-pixel splits of one shape
K_VARIANTS = int(os.environ.get('KVAR', '4'))


def ds(a):
    h, w = a.shape
    h2, w2 = h - h % DS, w - w % DS
    return a[:h2, :w2].reshape(h2 // DS, DS, w2 // DS, DS).mean((1, 3))


def load_glyphs():
    d = np.load(os.path.join(GEO, 'glyphs2.npz'))
    return d


def masked(cp, H, W, i):
    c = np.unpackbits(cp[i], axis=-1)[:, :CAN]
    h, w = int(H[i]), int(W[i])
    t = CAN // 2 - (h + 1) // 2
    l = CAN // 2 - (w + 1) // 2
    if t < 0 or l < 0 or t + h > CAN or l + w > CAN:
        return None
    return c[t:t + h, l:l + w]


def load_templates():
    t = np.load(os.path.join(RT, 'templates.npz'))
    X, label, sizes, centres = t['X'], t['label'], t['sizes'], t['centres']
    kh, kw = t['keys_h'], t['keys_w']
    cover = np.bincount(label, weights=sizes, minlength=label.max() + 1)
    keep = [c for c in range(len(cover)) if cover[c] >= MINCLASS]
    parent = {c: c for c in keep}
    for a, b in MERGE:
        parent[b] = a
    tmpl = []
    for c in keep:
        idx = np.where(label == c)[0]
        idx = idx[np.argsort(-sizes[idx])][:K_VARIANTS]
        for i in idx:
            h, w = int(kh[i]), int(kw[i])
            can = X[i].reshape(PAD_H, PAD_W).astype(np.float32)
            top, left = (PAD_H - h) // 2, (PAD_W - w) // 2
            tmpl.append((parent[c], ds(can[top:top + h, left:left + w])))
    return tmpl, sorted(set(parent.values()))


def integral2(I2, th, tw):
    S = np.zeros((I2.shape[0] + 1, I2.shape[1] + 1), np.float64)
    S[1:, 1:] = I2.cumsum(0).cumsum(1)
    return S[th:, tw:] - S[:-th, tw:] - S[th:, :-tw] + S[:-th, :-tw]


def line_costs(ink, tmpl):
    H, W = ink.shape
    I2 = ink * ink
    out = []
    for cid, T in tmpl:
        th, tw = T.shape
        if th > H or tw >= W:
            continue
        corr = fftconvolve(ink, T[::-1, ::-1], mode='valid')
        box = integral2(I2, th, tw)
        ssd = float((T * T).sum()) + box - 2.0 * corr
        r = np.argmin(ssd, 0)
        out.append((ssd[r, np.arange(ssd.shape[1])].astype(np.float32), tw, cid))
    return out


def decode(costs, colE, W, lam):
    INF = 1e30
    f = np.full(W + 1, INF); bk = [None] * (W + 1); f[0] = 0.0
    for x in range(W):
        if f[x] >= INF:
            continue
        nc = f[x] + colE[x]
        if nc < f[x + 1]:
            f[x + 1] = nc; bk[x + 1] = ('s', x)
        for cost, tw, cid in costs:
            if x >= len(cost):
                continue
            nc = f[x] + cost[x] + lam
            if nc < f[x + tw]:
                f[x + tw] = nc; bk[x + tw] = ('g', x, cid, float(cost[x]))
    out, x = [], W
    while x > 0 and bk[x] is not None:
        b = bk[x]
        if b[0] == 'g':
            out.append((b[2], b[1], b[3])); x = b[1]
        else:
            x = b[1]
    out.reverse()
    return out, float(f[W])


def main():
    lams = [float(v) for v in os.environ.get('LAMS', '30').split(',') if v]
    pages = os.environ.get('PAGES', '')
    only = set(int(v) for v in pages.split(',') if v) if pages else None
    tag_out = os.environ.get('OUT', 'read3')
    tmpl, classes = load_templates()
    print('templates: %d variants over %d merged classes' % (len(tmpl), len(classes)), flush=True)
    d = load_glyphs()
    page, x0, y0, x1, y1, cp = d['page'], d['x0'], d['y0'], d['x1'], d['y1'], d['crop']
    Hc, Wc = (y1 - y0), (x1 - x0)
    bands = d['bands']
    ok = (Hc >= H_MIN) & (Hc <= H_MAX) & (Wc <= W_MAX) & (Wc >= 4)
    print('rune-candidate components: %d / %d  (dropped %d)'
          % (ok.sum(), len(ok), (~ok).sum()), flush=True)
    keepb = [i for i, b in enumerate(bands) if only is None or b[0] in only]
    res = {l: [] for l in lams}
    stats = []
    cur, inkp = -1, None
    t0 = time.time()
    for bi in keepb:
        p, ys, ye, ng, medh = bands[bi]
        if p != cur:
            a = np.asarray(Image.open(os.path.join(IMG, 'p%d.jpg' % p)).convert('L'))
            full = np.zeros(a.shape, np.float32)
            sel = np.where((page == p) & ok)[0]
            for i in sel:
                m = masked(cp, Hc, Wc, i)
                if m is None:
                    continue
                full[y0[i]:y1[i], x0[i]:x1[i]] = np.maximum(
                    full[y0[i]:y1[i], x0[i]:x1[i]], m)
            inkp = ds(full)
            cur = p
            print('  page %d  comps %d  t=%.0fs' % (p, len(sel), time.time() - t0), flush=True)
        band = inkp[ys // DS:(ye + DS) // DS]
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
                               glyphs=[[int(c), int((x + x_lo) * DS), round(float(k), 1)]
                                       for c, x, k in seq]))
    for l in lams:
        t = ('_l%g' % l) if len(lams) > 1 else ''
        fn = os.path.join(HERE, '%s%s.json' % (tag_out, t))
        json.dump(res[l], open(fn, 'w'))
        n = sum(len(o['glyphs']) for o in res[l])
        ks = np.array([g[2] for o in res[l] for g in o['glyphs']]) if n else np.array([0.])
        print('lam=%-7g glyphs=%6d  median %.2f  frac<2 %.3f  -> %s'
              % (l, n, np.median(ks), float((ks < 2).mean()), os.path.basename(fn)), flush=True)
    print('elapsed %.0fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
