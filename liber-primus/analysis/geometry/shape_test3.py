"""Track GEOMETRY — the decisive shape test, final form.

Question, stated so it needs no transcription, no clustering and no alignment:

    Does the book contain any glyph that has no near-duplicate elsewhere in
    the book?

In a font render the answer must be no: every rune is drawn from the same
outline, so every instance has hundreds of siblings differing only by
rasterisation phase and JPEG threshold noise. A deliberately altered glyph -- a
rotation, a mirror, a modified stroke, a substituted face, a second font -- is
by construction the one thing that would have no sibling.

Method: for every full-height glyph, compute the exact pixel Hamming distance to
its NEAREST NEIGHBOUR among glyphs of the same (height, width) +/- 1 px.
Hamming for 0/1 masks is ||x||^2 + ||y||^2 - 2 x.y, so the whole thing is one
Gram matrix per size group. No resampling anywhere.

Earlier versions of this test failed for reasons now fixed and worth recording:
 - shape_test.py  clustered 48x48 RESIZED masks; its tail was broken-stroke
   segmentation artifacts, i.e. it measured segmentation, not glyphs.
 - shape_test2.py compared each mask to its size group's MODAL mask, but a
   (h,w) group contains several different runes that happen to share a bounding
   box, so the modal mask was a blend of different letters. (It also underflowed
   uint8 subtraction, inflating every distance.)
Nearest-neighbour has neither failure mode.
"""
import os, json, collections
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CAN = 160

d = np.load(os.path.join(HERE, 'glyphs2.npz'))
page, x0, y0, x1, y1, area = d['page'], d['x0'], d['y0'], d['x1'], d['y1'], d['area']
cp = d['crop']
H, W = (y1 - y0).astype(int), (x1 - x0).astype(int)


def masked(i, h, w):
    """glyph ink in a fixed (h,w) window centred on its own bbox"""
    c = np.unpackbits(cp[i], axis=-1)[:, :CAN]
    top = CAN // 2 - (h + 1) // 2
    left = CAN // 2 - (w + 1) // 2
    if top < 0 or left < 0 or top + h > CAN or left + w > CAN:
        return None
    return c[top:top+h, left:left+w]


def main():
    modal = int(np.median(H[H > 60]))
    sel = np.where((H >= modal - 6) & (H <= modal + 6) & (W >= 6) & (W <= 130))[0]
    print('components %d | full-height glyphs analysed %d' % (len(H), len(sel)))

    # bucket by width; compare within width +/-1 at a common window size
    bywidth = collections.defaultdict(list)
    for i in sel:
        bywidth[W[i]].append(i)

    nn_all, owner = [], []
    for w in sorted(bywidth):
        idx = [i for ww in (w-1, w, w+1) for i in bywidth.get(ww, [])]
        if len(idx) < 5:
            continue
        hh = modal + 6
        ww = w + 2
        X = []
        keep = []
        for i in idx:
            m = masked(i, hh, ww)
            if m is None:
                continue
            X.append(m.ravel().astype(np.float32))
            keep.append(i)
        if len(X) < 5:
            continue
        X = np.stack(X)
        sq = (X * X).sum(1)
        G = sq[:, None] + sq[None, :] - 2.0 * (X @ X.T)
        np.fill_diagonal(G, np.inf)
        nn = G.min(1)
        # only score glyphs whose own width is exactly w (avoid double counting)
        for t, i in enumerate(keep):
            if W[i] == w:
                nn_all.append(nn[t] / max(sq[t], 1.0))
                owner.append(i)
    nn_all = np.array(nn_all)
    owner = np.array(owner)
    print('glyphs with a computable nearest neighbour: %d' % len(nn_all))
    print('\nnearest-neighbour Hamming distance / own ink:')
    print('  mean %.4f  median %.4f  pct %s  max %.4f'
          % (nn_all.mean(), np.median(nn_all),
             np.percentile(nn_all, [90, 99, 99.9]).round(4), nn_all.max()))
    frac = (nn_all > 0.25).mean()
    print('  glyphs whose closest sibling differs by >25%% of their ink: %d (%.3f%%)'
          % (int((nn_all > 0.25).sum()), 100 * frac))

    order = np.argsort(nn_all)[::-1]
    recs = []
    for t in order[:60]:
        i = int(owner[t])
        recs.append(dict(nn=float(nn_all[t]), page=int(page[i]), x=int(x0[i]),
                         y=int(y0[i]), w=int(W[i]), h=int(H[i]),
                         area=int(area[i]), gi=i))
    json.dump(dict(analysed=int(len(nn_all)),
                   mean=float(nn_all.mean()), median=float(np.median(nn_all)),
                   p999=float(np.percentile(nn_all, 99.9)), max=float(nn_all.max()),
                   over25pct=int((nn_all > 0.25).sum()),
                   worst=recs),
              open(os.path.join(HERE, 'shape_report3.json'), 'w'), indent=1)

    tiles = []
    for r in recs[:32]:
        m = masked(r['gi'], modal + 6, r['w'] + 2)
        if m is None:
            continue
        im = Image.fromarray(((1 - m) * 255).astype(np.uint8))
        sc = 96.0 / max(m.shape)
        im = im.resize((max(1, int(m.shape[1]*sc)), max(1, int(m.shape[0]*sc))))
        t = np.full((100, 100), 255, np.uint8)
        a = np.asarray(im)
        t[:a.shape[0], :a.shape[1]] = a
        tiles.append(t)
    cols = 8
    rn = (len(tiles) + cols - 1) // cols
    sheet = np.full((max(rn, 1) * 100, cols * 100), 255, np.uint8)
    for t, tile in enumerate(tiles):
        rr, cc = divmod(t, cols)
        sheet[rr*100:rr*100+100, cc*100:cc*100+100] = tile
    Image.fromarray(sheet).save(os.path.join(HERE, 'shape_outliers3.png'))
    print('wrote shape_report3.json + shape_outliers3.png')


if __name__ == '__main__':
    main()
