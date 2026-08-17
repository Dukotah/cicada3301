"""L1-TEMPLATE stage 2d -- per-component label-free read.  THE instrument.

Once the ink is filtered to rune-candidate components (read3.py), a line-level
DP is the wrong tool: on pages 0-2 the filter yields 739 candidate components
against 729 canonical runes (+1.4%), so the segmentation is already essentially
one-component-per-rune and the DP's only remaining freedom is to SPLIT correct
glyphs, which is exactly what it did (838 glyphs from 739 components).

So: classify each component directly against the template library.

    for each rune-candidate component
        cost(class) = min over that class's exact-bitmap variants, over
                      +/-1 downsampled pixel of alignment, of the squared
                      difference between the component's anti-aliased mask
                      and the variant's
        label       = argmin, margin = second-best - best

Anti-aliased 2x down-sampling is what makes this exact: the font renders each
rune at several sub-pixel phases (1,067 distinct exact bitmaps for 29 shapes),
and area-mean down-sampling turns a phase shift into a small grey change
instead of a flipped boundary layer.

Outputs read4.json: one record per component with page, band, x, class,
best/second cost, margin.  No canonical rune or length is read here.
"""
import os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
RT = os.path.join(ROOT, 'analysis', 'retranscribe')
GEO = os.path.join(ROOT, 'analysis', 'geometry')
PAD_H, PAD_W = 128, 136
CAN = 160
MINCLASS = 100
DS = 2
H_MIN, H_MAX, W_MAX = 100, 126, 130
MERGE = [(0, 11), (15, 31), (26, 29)]
K_VARIANTS = int(os.environ.get('KVAR', '12'))


def ds2(a):
    h, w = a.shape
    return a.reshape(h // DS, DS, w // DS, DS).mean((1, 3))


def canvas_of(m):
    out = np.zeros((PAD_H, PAD_W), np.float32)
    h, w = m.shape
    t, l = (PAD_H - h) // 2, (PAD_W - w) // 2
    if t < 0 or l < 0:
        return None
    out[t:t + h, l:l + w] = m
    return out


def main():
    t0 = time.time()
    t = np.load(os.path.join(RT, 'templates.npz'))
    X, label, sizes, centres = t['X'], t['label'], t['sizes'], t['centres']
    kh, kw = t['keys_h'], t['keys_w']
    cover = np.bincount(label, weights=sizes, minlength=label.max() + 1)
    keep = [c for c in range(len(cover)) if cover[c] >= MINCLASS]
    parent = {c: c for c in keep}
    for a, b in MERGE:
        parent[b] = a
    tv, tc = [], []
    for c in keep:
        idx = np.where(label == c)[0]
        idx = idx[np.argsort(-sizes[idx])][:K_VARIANTS]
        for i in idx:
            tv.append(ds2(X[i].reshape(PAD_H, PAD_W).astype(np.float32)))
            tc.append(parent[c])
    T = np.stack(tv).reshape(len(tv), -1)
    tc = np.array(tc)
    classes = sorted(set(tc.tolist()))
    print('templates %d over %d merged classes; dims %d' % (len(T), len(classes), T.shape[1]), flush=True)

    d = np.load(os.path.join(GEO, 'glyphs2.npz'))
    page, x0, y0, x1, y1, cp = d['page'], d['x0'], d['y0'], d['x1'], d['y1'], d['crop']
    bands = d['bands']
    Hc, Wc = (y1 - y0), (x1 - x0)
    ok = np.where((Hc >= H_MIN) & (Hc <= H_MAX) & (Wc <= W_MAX) & (Wc >= 4))[0]
    print('rune-candidate components %d of %d' % (len(ok), len(Hc)), flush=True)

    # band assignment by y-centre
    bcent = {}
    for bi, (p, ys, ye, ng, mh) in enumerate(bands):
        bcent.setdefault(int(p), []).append((bi, int(ys), int(ye)))

    G, gi = [], []
    for i in ok:
        c = np.unpackbits(cp[i], axis=-1)[:, :CAN]
        h, w = int(Hc[i]), int(Wc[i])
        tt = CAN // 2 - (h + 1) // 2
        ll = CAN // 2 - (w + 1) // 2
        if tt < 0 or ll < 0 or tt + h > CAN or ll + w > CAN:
            continue
        cv = canvas_of(c[tt:tt + h, ll:ll + w].astype(np.float32))
        if cv is None:
            continue
        G.append(ds2(cv).ravel()); gi.append(int(i))
    G = np.stack(G)
    gi = np.array(gi)
    print('classified components %d  (%.0fs)' % (len(G), time.time() - t0), flush=True)

    Hs, Ws = PAD_H // DS, PAD_W // DS
    gsq = (G * G).sum(1)
    best = None
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            Y = np.roll(np.roll(T.reshape(-1, Hs, Ws), dy, 1), dx, 2).reshape(len(T), -1)
            D = gsq[:, None] + (Y * Y).sum(1)[None, :] - 2.0 * (G @ Y.T)
            best = D if best is None else np.minimum(best, D)
    best = np.maximum(best, 0)
    # collapse variants -> class
    C = np.full((len(G), len(classes)), np.inf, np.float32)
    for k, c in enumerate(classes):
        C[:, k] = best[:, tc == c].min(1)
    order = np.argsort(C, 1)
    lab = np.array(classes)[order[:, 0]]
    b1 = C[np.arange(len(G)), order[:, 0]]
    b2 = C[np.arange(len(G)), order[:, 1]]
    lab2 = np.array(classes)[order[:, 1]]
    print('assignment done (%.0fs)  median best %.2f  median margin %.2f'
          % (time.time() - t0, np.median(b1), np.median(b2 - b1)), flush=True)

    recs = []
    for k, i in enumerate(gi):
        p = int(page[i]); yc = (int(y0[i]) + int(y1[i])) // 2
        bi = -1
        for bb, ys, ye in bcent.get(p, []):
            if ys - 20 <= yc <= ye + 20:
                bi = bb; break
        recs.append(dict(page=p, band=bi, x=int(x0[i]), y=int(y0[i]),
                         w=int(Wc[i]), h=int(Hc[i]), comp=int(i),
                         cls=int(lab[k]), d1=round(float(b1[k]), 2),
                         cls2=int(lab2[k]), d2=round(float(b2[k]), 2)))
    recs.sort(key=lambda r: (r['page'], r['band'], r['x']))
    json.dump(recs, open(os.path.join(HERE, 'read4.json'), 'w'))
    print('wrote read4.json  %d components  elapsed %.0fs' % (len(recs), time.time() - t0))


if __name__ == '__main__':
    main()
