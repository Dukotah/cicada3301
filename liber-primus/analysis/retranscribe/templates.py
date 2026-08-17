"""Independent re-transcription — stage 1: build the font's shape templates.

Why this is not Avenue #1 (AI vision re-transcription, closed 2026-06-20 at
alignment 0.145). That avenue asked a generative model to RECOGNISE a rune -- a
judgement call on visually similar glyphs, which is exactly what it is bad at.
This asks a different question: *is this ink blob the same blob as that one?*

Round 8 established the fact that makes this work: these pages are a font render
in which the median glyph's nearest-neighbour pixel Hamming distance is 0.0000 --
the median glyph has a pixel-identical twin somewhere in the book. Matching
against a template library is therefore a lookup, not a recognition problem.

Stage 1 collects every distinct exact bitmap (1,067 of them across 13,140
full-height glyphs -- one per rune per sub-pixel placement phase) and merges them
into shape classes by alignment-tolerant distance. If the render is what we think
it is, that should collapse to ~29 classes with no supervision at all.

Output: templates.npz (class masks + members), and a contact sheet.
"""
import os, sys, collections, hashlib, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.normpath(os.path.join(HERE, '..', 'geometry'))
CAN = 160
PAD_H, PAD_W = 128, 136        # common canvas for cross-class comparison

d = np.load(os.path.join(GEO, 'glyphs2.npz'))
page, x0, y0, x1, y1 = d['page'], d['x0'], d['y0'], d['x1'], d['y1']
cp = d['crop']
H, W = (y1 - y0).astype(int), (x1 - x0).astype(int)


def masked(i):
    c = np.unpackbits(cp[i], axis=-1)[:, :CAN]
    h, w = H[i], W[i]
    t = CAN // 2 - (h + 1) // 2
    l = CAN // 2 - (w + 1) // 2
    if t < 0 or l < 0 or t + h > CAN or l + w > CAN:
        return None
    return c[t:t+h, l:l+w]


def canvas(m):
    """centre a mask in a common canvas so different sizes are comparable"""
    out = np.zeros((PAD_H, PAD_W), np.float32)
    h, w = m.shape
    if h > PAD_H or w > PAD_W:
        return None
    t = (PAD_H - h) // 2
    l = (PAD_W - w) // 2
    out[t:t+h, l:l+w] = m
    return out


def main():
    sel = np.where((H >= 108) & (H <= 120) & (W >= 6) & (W <= 130))[0]
    groups = collections.defaultdict(list)
    for i in sel:
        m = masked(i)
        if m is None:
            continue
        groups[(int(H[i]), int(W[i]),
                hashlib.md5(m.tobytes()).hexdigest())].append(int(i))
    keys = sorted(groups, key=lambda k: -len(groups[k]))
    print('full-height glyphs %d | distinct exact bitmaps %d' % (len(sel), len(keys)))

    reps, sizes, ok_keys = [], [], []
    for k in keys:
        m = masked(groups[k][0])
        c = canvas(m)
        if c is None:
            continue
        reps.append(c.ravel())
        sizes.append(len(groups[k]))
        ok_keys.append(k)
    X = np.stack(reps)
    sizes = np.array(sizes)
    print('comparable bitmaps %d covering %d glyphs'
          % (len(X), int(sizes.sum())))

    # alignment-tolerant distance: shift +/-2 px in x and y, keep the minimum
    sq = (X * X).sum(1)
    best = None
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            Y = np.roll(np.roll(X.reshape(-1, PAD_H, PAD_W), dy, 1), dx, 2)
            Y = Y.reshape(len(X), -1)
            G = sq[:, None] + (Y*Y).sum(1)[None, :] - 2.0 * (X @ Y.T)
            best = G if best is None else np.minimum(best, G)
    D = np.maximum(best, 0)
    # normalise by ink mass so wide and narrow runes are on the same scale
    Dn = D / np.maximum(sq[:, None], 1.0)

    # agglomerate greedily from the most populous bitmaps outward
    order = np.argsort(-sizes)
    THRESH = 0.10                  # <=10% of ink differing == same shape
    label = -np.ones(len(X), int)
    centres = []
    for i in order:
        if label[i] >= 0:
            continue
        c = len(centres)
        centres.append(i)
        near = np.where(Dn[i] <= THRESH)[0]
        for j in near:
            if label[j] < 0:
                label[j] = c
    nclass = len(centres)
    cover = np.bincount(label, weights=sizes, minlength=nclass)
    print('\nshape classes at threshold %.2f: %d' % (THRESH, nclass))
    print('class sizes (glyphs):', np.sort(cover)[::-1].astype(int)[:40].tolist())
    big = int((cover >= 100).sum())
    print('classes with >=100 glyphs: %d covering %.1f%% of glyphs'
          % (big, 100 * cover[cover >= 100].sum() / cover.sum()))

    np.savez_compressed(os.path.join(HERE, 'templates.npz'),
                        label=label, sizes=sizes,
                        centres=np.array(centres),
                        keys_h=np.array([k[0] for k in ok_keys]),
                        keys_w=np.array([k[1] for k in ok_keys]),
                        X=X.astype(np.uint8))
    json.dump({'n_bitmaps': len(X), 'n_classes': nclass,
               'class_glyph_counts': cover.astype(int).tolist(),
               'threshold': THRESH},
              open(os.path.join(HERE, 'templates_report.json'), 'w'), indent=1)

    # contact sheet of the class centroids, largest first
    idx = np.argsort(-cover)[:40]
    tiles = []
    for c in idx:
        m = X[centres[c]].reshape(PAD_H, PAD_W)
        im = Image.fromarray(((1 - m) * 255).astype(np.uint8)).resize((70, 66))
        tiles.append(np.asarray(im))
    cols = 10
    rn = (len(tiles) + cols - 1) // cols
    sheet = np.full((rn * 70, cols * 74), 255, np.uint8)
    for t, tile in enumerate(tiles):
        r, cc = divmod(t, cols)
        sheet[r*70:r*70+66, cc*74:cc*74+70] = tile
    Image.fromarray(sheet).save(os.path.join(HERE, 'templates.png'))
    print('wrote templates.npz, templates.png')


if __name__ == '__main__':
    main()
