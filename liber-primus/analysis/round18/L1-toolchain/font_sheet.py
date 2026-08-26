"""PC3c + visual: (a) measure LP2's OWN within-corpus reproducibility by splitting
each rune class's glyph instances into two independent halves and comparing the two
centroids - this is the correct denominator for the font distances, because it is the
noise floor the observed bitmaps actually carry; (b) render a side-by-side contact
sheet of the observed runes against the best-scoring candidate faces.
"""
import os, sys, json, glob
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.normpath(os.path.join(HERE, '..', '..', 'retranscribe'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', '..', 'src')))
from lp.gematria import IDX_TO_TRANS
from font_match import (crop, to_box_aspect, to_box_stretch, iou_dist,
                        render_font, degrade, compare, FONTS)

PAD_H, PAD_W = 128, 136


def half_centroids(seed=3301):
    """Two independent centroid sets from disjoint halves of each class's glyphs."""
    t = np.load(os.path.join(RT, 'templates.npz'))
    X, label = t['X'], t['label']
    kh, kw = t['keys_h'], t['keys_w']
    mapping = json.load(open(os.path.join(RT, 'diff_report.json')))['mapping']
    rng = np.random.default_rng(seed)
    A, B = {}, {}
    for cls_s, rune in mapping.items():
        c = int(cls_s)
        idx = np.where(label == c)[0]
        if len(idx) < 4:
            continue
        rng.shuffle(idx)
        for half, out in ((idx[:len(idx) // 2], A), (idx[len(idx) // 2:], B)):
            acc = np.zeros((PAD_H, PAD_W), np.float64)
            for i in half:
                acc += X[i].reshape(PAD_H, PAD_W)
            acc /= len(half)
            g = (acc > 0.5).astype(np.uint8)
            cg = crop(g)
            if cg is not None:
                out[int(rune)] = cg
    return A, B


def main():
    A, B = half_centroids()
    c = compare(A, B)
    c.pop('per_rune')
    noise = {'PC3c_LP2_within_corpus_split_half': c}
    print('PC3c LP2 split-half noise floor: mean_aspect=%.4f  mean_stretch=%.4f  n=%d'
          % (c['mean_aspect'], c['mean_stretch'], c['n']))

    res = json.load(open(os.path.join(HERE, 'font_match_results.json')))
    res.update(noise)
    band = res['calibration']['degraded_self_band']
    best = res['verdict']['best']
    best_d = res['verdict']['best_mean_aspect']
    res['PC3c_interpretation'] = {
        'lp2_split_half_mean_aspect': round(c['mean_aspect'], 5),
        'best_candidate_mean_aspect': round(best_d, 5),
        'ratio_best_over_noise_floor': round(best_d / c['mean_aspect'], 2)
        if c['mean_aspect'] > 0 else None,
        'degraded_self_band': band,
        'cross_face_mean': res['calibration']['cross_face_mean'],
        'reading': ('The LP2 glyph set reproduces itself at this distance, so any face that '
                    'were the true one should score near it. The best candidate scores far '
                    'above, which places every bank face outside the identification band.')
    }
    json.dump(res, open(os.path.join(HERE, 'font_match_results.json'), 'w'), indent=1)

    # ---- contact sheet: observed vs top candidates ----------------------
    obs_npz = np.load(os.path.join(HERE, 'runes_observed.npz'))
    obs = {int(k[1:]): obs_npz[k].astype(np.uint8) for k in obs_npz.files}
    top = [n for n, _, _ in res['LP2_ranking'][:4]]
    banks = {}
    for n in top:
        p = os.path.join(FONTS, n)
        r = render_font(p)
        if r:
            banks[n] = r
    rows = ['LP2 (observed)'] + top
    cell = 72
    W = cell * 29 + 220
    H = cell * len(rows) + 20
    sheet = np.ones((H, W), np.uint8) * 255
    for ri, name in enumerate(rows):
        src = obs if ri == 0 else banks.get(name, {})
        for k in range(29):
            g = src.get(k)
            if g is None:
                continue
            s = min((cell - 10) / g.shape[0], (cell - 10) / g.shape[1])
            im = Image.fromarray(((1 - g) * 255).astype('uint8')).resize(
                (max(1, int(g.shape[1] * s)), max(1, int(g.shape[0] * s))), Image.LANCZOS)
            a = np.asarray(im)
            y0 = ri * cell + (cell - a.shape[0]) // 2 + 10
            x0 = 220 + k * cell + (cell - a.shape[1]) // 2
            sheet[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    img = Image.fromarray(sheet)
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    for ri, name in enumerate(rows):
        d.text((6, ri * cell + cell // 2), name[:30], fill=0)
    for k in range(29):
        d.text((220 + k * cell + 4, 0), IDX_TO_TRANS[k], fill=0)
    img.save(os.path.join(HERE, 'font_match_sheet.png'))
    print('wrote font_match_sheet.png')


if __name__ == '__main__':
    main()
