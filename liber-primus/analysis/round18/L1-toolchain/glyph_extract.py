"""I3 - extract one clean binary bitmap per Gematria Primus rune from the LP2 pages.

Uses the VALIDATED R9 template-DP instrument (analysis/retranscribe/), whose
class->rune mapping is bijective and whose control agreement is 96.93% over 5207
compared glyphs (analysis/retranscribe/diff_report.json).  It does NOT use
round12/frontB/forceseg.py, whose forced re-segmentation fails its control at
12.9% and cannot be trusted for per-rune identity.

The R9 templates.npz holds, per cluster, the centroid glyph bitmap harvested from
the page images.  Combined with diff_report.json's class->rune mapping that gives
a per-rune reference bitmap AS DRAWN IN THE BOOK - which is what a font matcher
needs.

Output: runes_observed.npz  (29 binary bitmaps, cropped to ink bbox)
        runes_observed.png  (contact sheet for eyeballing)
"""
import os, sys, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.normpath(os.path.join(HERE, '..', '..', 'retranscribe'))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', '..', 'src')))
from lp.gematria import IDX_TO_TRANS, IDX_TO_RUNE

PAD_H, PAD_W = 128, 136


def crop_ink(a, thresh=0.5):
    m = a > thresh
    if not m.any():
        return None
    ys, xs = np.where(m)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def main():
    t = np.load(os.path.join(RT, 'templates.npz'))
    X, label, sizes, centres = t['X'], t['label'], t['sizes'], t['centres']
    kh, kw = t['keys_h'], t['keys_w']
    mapping = json.load(open(os.path.join(RT, 'diff_report.json')))['mapping']
    cover = np.bincount(label, weights=sizes, minlength=int(label.max()) + 1)

    out = {}
    meta = {}
    for cls_s, rune_idx in mapping.items():
        c = int(cls_s)
        i = centres[c]
        h, w = int(kh[i]), int(kw[i])
        canvas = X[i].reshape(PAD_H, PAD_W).astype(np.float32)
        top = (PAD_H - h) // 2
        left = (PAD_W - w) // 2
        g = canvas[top:top + h, left:left + w]
        g = (g > 0.5).astype(np.uint8)
        cg = crop_ink(g.astype(np.float32))
        if cg is None:
            continue
        out['r%02d' % rune_idx] = cg.astype(np.uint8)
        meta['r%02d' % rune_idx] = {
            'class': c, 'translit': IDX_TO_TRANS[rune_idx],
            'rune': IDX_TO_RUNE[rune_idx],
            'n_glyphs_in_class': int(cover[c]),
            'shape': list(cg.shape),
            'aspect_w_over_h': round(cg.shape[1] / cg.shape[0], 4),
            'ink_fraction': round(float(cg.mean()), 4),
        }
    np.savez_compressed(os.path.join(HERE, 'runes_observed.npz'), **out)
    json.dump(meta, open(os.path.join(HERE, 'runes_observed_meta.json'), 'w'), indent=1)

    # contact sheet
    cell = 100
    cols, rows = 8, 4
    sheet = np.ones((rows * cell, cols * cell), np.uint8) * 255
    for k in range(29):
        key = 'r%02d' % k
        if key not in out:
            continue
        g = out[key]
        s = min((cell - 12) / g.shape[0], (cell - 12) / g.shape[1])
        im = Image.fromarray((1 - g) * 255).resize(
            (max(1, int(g.shape[1] * s)), max(1, int(g.shape[0] * s))), Image.LANCZOS)
        a = np.asarray(im)
        r, c = divmod(k, cols)
        y0 = r * cell + (cell - a.shape[0]) // 2
        x0 = c * cell + (cell - a.shape[1]) // 2
        sheet[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    Image.fromarray(sheet).save(os.path.join(HERE, 'runes_observed.png'))
    print(json.dumps({'n_runes': len(out),
                      'missing': [i for i in range(29) if 'r%02d' % i not in out],
                      'meta': meta}, indent=1))


if __name__ == '__main__':
    main()
