"""Track GEOMETRY — the decisive shape test, label-free.

The question is simply: *does any glyph in this book fail to match one of the
font's shapes?* That does not need the canonical transcription at all, so it is
immune to the segmentation/label contamination that broke the labelled version
(ink-area spread of 15-134% per "class" is alignment error, not a font).

Method
  1. Keep only clean full-height single-rune components (the render draws every
     rune to a common stave height, so height selects them and rejects merged
     blobs, separators and fragments).
  2. Register each on its own bounding box and rasterise to a fixed 48x48 mask.
  3. k-means into K shape clusters, many restarts, best inertia.
  4. In a font render, within-cluster residual must be rasterisation-phase noise
     only. Report the residual distribution and every instance far from ALL
     centroids -- those, and only those, could be a deliberately modified glyph.

A null here is strong: it says the 56 pages contain no glyph that is not a
faithful repeat of the same small set of font outlines, which closes
glyph-substitution steganography as a channel.
"""
import os, sys, json, collections
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CAN = 160
BOX = 48
K = 32

d = np.load(os.path.join(HERE, 'glyphs2.npz'))
page, line, x0, y0, x1, y1, area = (d['page'], d['line'], d['x0'], d['y0'],
                                    d['x1'], d['y1'], d['area'])
cp = d['crop']
H, W = y1 - y0, x1 - x0


def masked(i):
    c = np.unpackbits(cp[i], axis=-1)[:, :CAN]
    h, w = int(H[i]), int(W[i])
    top = CAN // 2 - (h + 1) // 2
    left = CAN // 2 - (w + 1) // 2
    return c[max(0, top):max(0, top) + h, max(0, left):max(0, left) + w]


def main():
    hh = H.astype(int)
    modal = int(np.median(hh[hh > 60]))
    sel = np.where((hh >= modal - 8) & (hh <= modal + 8) &
                   (W >= 6) & (W <= 120))[0]
    print('components %d | modal stave height %d px | clean full-height glyphs %d'
          % (len(H), modal, len(sel)))

    V = np.zeros((len(sel), BOX * BOX), np.float32)
    for t, i in enumerate(sel):
        m = masked(i)
        if m.size == 0:
            continue
        im = Image.fromarray((m * 255).astype(np.uint8)).resize((BOX, BOX),
                                                               Image.BILINEAR)
        V[t] = (np.asarray(im, np.float32) / 255.0).ravel()

    rng = np.random.default_rng(3301)
    best = None
    for restart in range(8):
        C = V[rng.choice(len(V), K, replace=False)].copy()
        for _ in range(60):
            dist = ((V**2).sum(1)[:, None] - 2 * V @ C.T + (C**2).sum(1)[None, :])
            asg = dist.argmin(1)
            for k in range(K):
                m = asg == k
                if m.sum():
                    C[k] = V[m].mean(0)
        inertia = dist.min(1).sum()
        if best is None or inertia < best[0]:
            best = (inertia, C.copy(), asg.copy(), dist.min(1).copy())
    inertia, C, asg, dmin = best
    sizes = np.bincount(asg, minlength=K)
    print('k-means K=%d  inertia %.1f  cluster sizes %s'
          % (K, inertia, sorted(sizes.tolist(), reverse=True)))

    # residual = distance to own centroid, normalised by the glyph's ink mass
    ink = V.sum(1)
    resid = dmin / np.maximum(ink, 1.0)
    print('\nresidual to own centroid (fraction of ink mass):')
    print('  mean %.4f  sd %.4f  pct %s' %
          (resid.mean(), resid.std(),
           np.percentile(resid, [50, 90, 99, 99.9]).round(4)))

    # per-cluster tightness -- a font render should be very tight
    print('\n%-4s %5s %9s %9s %8s' % ('clus', 'n', 'resid', 'sd', 'max z'))
    rows = []
    for k in range(K):
        m = np.where(asg == k)[0]
        if len(m) < 15:
            continue
        r = resid[m]
        z = (r - r.mean()) / (r.std() + 1e-9)
        rows.append((k, len(m), float(r.mean()), float(r.std()), float(z.max()),
                     int(m[int(np.argmax(z))])))
    rows.sort(key=lambda t: -t[4])
    for t in rows[:12]:
        print('%-4d %5d %9.4f %9.4f %8.2f' % t[:5])

    # global outliers: far from EVERY centroid
    thr = np.percentile(resid, 99.5)
    out = np.where(resid > thr)[0]
    print('\nglobal outliers (resid > 99.5th pct = %.4f): %d' % (thr, len(out)))
    recs = []
    for t in out[np.argsort(resid[out])[::-1][:40]]:
        i = sel[t]
        recs.append(dict(page=int(page[i]), x=int(x0[i]), y=int(y0[i]),
                         w=int(W[i]), h=int(H[i]), area=int(area[i]),
                         resid=float(resid[t]), cluster=int(asg[t])))

    # how much of the residual spread is explainable as rasterisation phase?
    # compare against the SAME test on a control: the glyphs of a single page
    ctrl = []
    for p in range(56):
        m = np.where(page[sel] == p)[0]
        if len(m) > 50:
            ctrl.append(resid[m].std())
    print('per-page residual sd: mean %.4f  min %.4f  max %.4f'
          % (np.mean(ctrl), np.min(ctrl), np.max(ctrl)))

    json.dump(dict(components=int(len(H)), clean=int(len(sel)), K=K,
                   inertia=float(inertia),
                   cluster_sizes=sizes.tolist(),
                   resid_mean=float(resid.mean()), resid_sd=float(resid.std()),
                   resid_p999=float(np.percentile(resid, 99.9)),
                   outliers=recs),
              open(os.path.join(HERE, 'shape_report.json'), 'w'), indent=1)

    # render the worst 40 for eyeball adjudication
    tiles = []
    for r in recs:
        i = int(np.where((page == r['page']) & (x0 == r['x']) & (y0 == r['y']))[0][0])
        m = masked(i)
        im = Image.fromarray((1 - m).astype(np.uint8) * 255).resize((96, 96))
        tiles.append(np.asarray(im))
    if tiles:
        cols = 8
        rowsn = (len(tiles) + cols - 1) // cols
        sheet = np.full((rowsn * 100, cols * 100), 255, np.uint8)
        for t, tile in enumerate(tiles):
            r_, c_ = divmod(t, cols)
            sheet[r_*100:r_*100+96, c_*100:c_*100+96] = tile
        Image.fromarray(sheet).save(os.path.join(HERE, 'shape_outliers.png'))
        print('wrote shape_outliers.png (%d tiles)' % len(tiles))
    print('wrote shape_report.json')


if __name__ == '__main__':
    main()
