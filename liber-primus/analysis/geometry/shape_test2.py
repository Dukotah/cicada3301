"""Track GEOMETRY — the decisive shape test, sharpened.

shape_test.py clustered resized 48x48 masks; its worst "outliers" turned out to
be broken-stroke segmentation artifacts (visible in shape_outliers.png), so the
tail measured segmentation quality, not glyph fidelity. This version removes the
resampling and the clustering entirely.

Key fact about a font render: a given rune at a fixed point size always
rasterises to the SAME bounding-box dimensions, and to one of only a few pixel
patterns (one per sub-pixel placement phase). So:

  1. group glyphs by their EXACT (height, width) in pixels -- this is a shape
     signature that needs no alignment, no resizing and no transcription;
  2. inside each populated group, compare every mask to the group's modal mask
     pixel-for-pixel (no interpolation);
  3. the Hamming distance / ink area is then pure JPEG-threshold noise plus
     rasterisation phase. A deliberately modified, rotated, mirrored or
     substituted glyph cannot sit in that distribution.

Reported: the (h,w) inventory (how many distinct glyph geometries the book
contains), the per-group noise floor, and every instance beyond it.
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


def masked(i):
    c = np.unpackbits(cp[i], axis=-1)[:, :CAN]
    h, w = H[i], W[i]
    top = CAN // 2 - (h + 1) // 2
    left = CAN // 2 - (w + 1) // 2
    if top < 0 or left < 0 or top + h > CAN or left + w > CAN:
        return None
    return c[top:top+h, left:left+w]


def main():
    modal = int(np.median(H[H > 60]))
    sel = np.where((H >= modal - 6) & (H <= modal + 6) & (W >= 6) & (W <= 130))[0]
    groups = collections.defaultdict(list)
    for i in sel:
        groups[(H[i], W[i])].append(i)
    big = {k: v for k, v in groups.items() if len(v) >= 40}
    covered = sum(len(v) for v in big.values())
    print('components %d | full-height glyphs %d | distinct (h,w) geometries %d'
          % (len(H), len(sel), len(groups)))
    print('geometries with n>=40: %d, covering %d glyphs (%.1f%% of full-height)'
          % (len(big), covered, 100.0 * covered / len(sel)))
    print('\n%-12s %6s %10s %10s %10s %8s' %
          ('(h,w)', 'n', 'meanHam', 'sd', 'p99', 'max'))

    allz, recs = [], []
    rows = []
    for k in sorted(big, key=lambda k: -len(big[k])):
        idx = [i for i in big[k] if masked(i) is not None]
        if len(idx) < 40:
            continue
        M = np.stack([masked(i) for i in idx]).astype(np.uint8)
        modal_mask = (M.mean(0) > 0.5).astype(np.uint8)
        ink = max(int(modal_mask.sum()), 1)
        ham = np.abs(M - modal_mask).sum(axis=(1, 2)) / ink
        rows.append((k, len(idx), ham.mean(), ham.std(),
                     np.percentile(ham, 99), ham.max()))
        z = (ham - ham.mean()) / (ham.std() + 1e-9)
        allz.append(z)
        for t in np.argsort(ham)[::-1][:4]:
            if ham[t] > 0.25:                     # >25% of ink differs
                i = idx[t]
                recs.append(dict(h=int(k[0]), w=int(k[1]), n=len(idx),
                                 ham=float(ham[t]), z=float(z[t]),
                                 page=int(page[i]), x=int(x0[i]), y=int(y0[i]),
                                 gi=int(i)))
    for r in rows[:16]:
        print('%-12s %6d %10.4f %10.4f %10.4f %8.4f'
              % (str(r[0]), r[1], r[2], r[3], r[4], r[5]))
    allham = np.concatenate([np.abs(np.stack([masked(i) for i in big[k]
                                              if masked(i) is not None]).astype(np.uint8)
                                    - (np.stack([masked(i) for i in big[k]
                                                 if masked(i) is not None]).mean(0) > 0.5)
                                    ).sum(axis=(1, 2))
                             / max(int((np.stack([masked(i) for i in big[k]
                                                  if masked(i) is not None]).mean(0) > 0.5).sum()), 1)
                             for k in big if len([i for i in big[k] if masked(i) is not None]) >= 40])
    print('\npooled Hamming/ink over %d glyphs: mean %.4f sd %.4f  pct %s'
          % (len(allham), allham.mean(), allham.std(),
             np.percentile(allham, [50, 90, 99, 99.9]).round(4)))
    print('instances with >25%% of ink differing from their geometry-mates: %d'
          % len(recs))

    json.dump(dict(components=int(len(H)), fullheight=int(len(sel)),
                   geometries=len(groups), geometries_big=len(big),
                   covered=int(covered),
                   pooled_mean=float(allham.mean()), pooled_sd=float(allham.std()),
                   pooled_p999=float(np.percentile(allham, 99.9)),
                   groups=[dict(h=int(r[0][0]), w=int(r[0][1]), n=r[1],
                                mean=float(r[2]), sd=float(r[3]),
                                p99=float(r[4]), max=float(r[5])) for r in rows],
                   outliers=recs[:60]),
              open(os.path.join(HERE, 'shape_report2.json'), 'w'), indent=1)

    if recs:
        recs.sort(key=lambda r: -r['ham'])
        tiles = []
        for r in recs[:32]:
            m = masked(r['gi'])
            im = Image.fromarray(((1 - m) * 255).astype(np.uint8))
            im = im.resize((int(96 * m.shape[1] / max(m.shape)),
                            int(96 * m.shape[0] / max(m.shape))))
            t = np.full((100, 100), 255, np.uint8)
            a = np.asarray(im)
            t[:a.shape[0], :a.shape[1]] = a
            tiles.append(t)
        cols = 8
        rn = (len(tiles) + cols - 1) // cols
        sheet = np.full((rn * 100, cols * 100), 255, np.uint8)
        for t, tile in enumerate(tiles):
            rr, cc = divmod(t, cols)
            sheet[rr*100:rr*100+100, cc*100:cc*100+100] = tile
        Image.fromarray(sheet).save(os.path.join(HERE, 'shape_outliers2.png'))
        print('wrote shape_outliers2.png')
    print('wrote shape_report2.json')


if __name__ == '__main__':
    main()
