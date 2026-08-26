"""I4 - identify the runic face used to typeset the Liber Primus.

Observed glyphs come from `glyph_extract.py` (validated R9 template-DP reader,
96.93% control agreement).  Candidate faces are rendered from the bank in fonts/
at the Unicode Runic codepoints of the Gematria Primus, binarised and cropped the
same way.

Two distances per rune, both in [0,1]:
  D_stretch : 1 - IoU after independently stretching both bitmaps to 96x96
              (pure stroke-topology comparison, aspect ignored)
  D_aspect  : 1 - IoU after aspect-preserving fit into 96x96
              (penalises a face whose glyph proportions differ)

PC3 - two controls, both required before any claim:
  PC3a CLEAN leave-one-in: each bank face is scored as if it were the observed
       set. It must rank itself 1st with distance ~0.
  PC3b DEGRADED self-match: each bank face is pushed through a simulation of the
       real pipeline (render large -> JPEG q92 -> downsample to the observed
       ~114 px glyph height -> threshold) and re-matched against the CLEAN bank.
       The self-distance band that survives IS the threshold band that the real
       LP2 glyphs must fall inside for a face to be called identified.  Without
       PC3b the absolute distances are meaningless, because the observed bitmaps
       carry render+JPEG+averaging blur that clean renders do not.

Output: font_match_results.json, font_match_sheet.png
"""
import os, sys, json, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', '..', 'src')))
from lp.gematria import GEMATRIA

FONTS = os.path.join(HERE, 'fonts')
BOX = 96
RENDER_PX = 300


def crop(a):
    m = a > 0
    if not m.any():
        return None
    ys, xs = np.where(m)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def to_box_stretch(a, n=BOX):
    im = Image.fromarray((a * 255).astype('uint8'))
    im = im.resize((n, n), Image.BILINEAR)
    return (np.asarray(im) > 127).astype(np.uint8)


def to_box_aspect(a, n=BOX):
    h, w = a.shape
    s = min((n - 4) / h, (n - 4) / w)
    nh, nw = max(1, int(round(h * s))), max(1, int(round(w * s)))
    im = Image.fromarray((a * 255).astype('uint8')).resize((nw, nh), Image.BILINEAR)
    out = np.zeros((n, n), np.uint8)
    y0, x0 = (n - nh) // 2, (n - nw) // 2
    out[y0:y0 + nh, x0:x0 + nw] = (np.asarray(im) > 127).astype(np.uint8)
    return out


def iou_dist(a, b):
    inter = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    return 1.0 if union == 0 else 1.0 - inter / union


def render_font(path, size=RENDER_PX):
    """Return {rune_idx: cropped binary bitmap} or None if the face lacks Runic."""
    try:
        f = ImageFont.truetype(path, size)
    except Exception:
        return None
    out = {}
    for idx, rune, _t, _p in GEMATRIA:
        img = Image.new('L', (size * 2, size * 2), 0)
        d = ImageDraw.Draw(img)
        try:
            d.text((size // 2, size // 2), rune, fill=255, font=f)
        except Exception:
            return None
        a = (np.asarray(img) > 127).astype(np.uint8)
        c = crop(a)
        if c is None or c.size < 20:
            return None                     # missing glyph -> face has no Runic block
        out[idx] = c
    return out


def degrade(bitmaps, target_h=114):
    """Simulate render -> JPEG q92 -> downsample -> threshold, as the real pages were."""
    import io
    out = {}
    for k, a in bitmaps.items():
        im = Image.fromarray(((1 - a) * 255).astype('uint8'))   # black ink on white
        s = target_h / a.shape[0]
        im = im.resize((max(1, int(round(a.shape[1] * s))), target_h), Image.LANCZOS)
        buf = io.BytesIO()
        im.convert('L').save(buf, 'JPEG', quality=92)
        buf.seek(0)
        b = np.asarray(Image.open(buf).convert('L'))
        g = (b < 128).astype(np.uint8)
        c = crop(g)
        out[k] = c if c is not None else a
    return out


def compare(obs, cand):
    """Mean distances over the runes present in both."""
    ks = sorted(set(obs) & set(cand))
    ds, da, per = [], [], {}
    for k in ks:
        d1 = iou_dist(to_box_stretch(obs[k]), to_box_stretch(cand[k]))
        d2 = iou_dist(to_box_aspect(obs[k]), to_box_aspect(cand[k]))
        ds.append(d1)
        da.append(d2)
        per[k] = [round(d1, 4), round(d2, 4)]
    if not ks:
        return None
    ao = np.array([obs[k].shape[1] / obs[k].shape[0] for k in ks])
    ac = np.array([cand[k].shape[1] / cand[k].shape[0] for k in ks])
    if ao.std() > 0 and ac.std() > 0:
        aspect_r = float(np.corrcoef(ao, ac)[0, 1])
    else:
        aspect_r = float('nan')
    return {'n': len(ks), 'mean_stretch': float(np.mean(ds)),
            'sd_stretch': float(np.std(ds)),
            'mean_aspect': float(np.mean(da)), 'sd_aspect': float(np.std(da)),
            'median_aspect': float(np.median(da)),
            'aspect_pearson_r': aspect_r, 'per_rune': per}


def main():
    obs_npz = np.load(os.path.join(HERE, 'runes_observed.npz'))
    obs = {int(k[1:]): obs_npz[k].astype(np.uint8) for k in obs_npz.files}

    bank = {}
    for p in sorted(glob.glob(os.path.join(FONTS, '*.ttf')) +
                    glob.glob(os.path.join(FONTS, '*.otf'))):
        name = os.path.basename(p)
        r = render_font(p)
        if r is None:
            print('skip (no Runic block or unrenderable): %s' % name)
            continue
        bank[name] = r
        print('rendered %s' % name)

    res = {'bank': sorted(bank), 'n_bank': len(bank)}

    # ---- PC3a clean leave-one-in ----------------------------------------
    pc3a = {}
    for name, glyphs in bank.items():
        scores = {other: compare(glyphs, bank[other])['mean_aspect'] for other in bank}
        rank = sorted(scores, key=scores.get)
        pc3a[name] = {'self_distance': round(scores[name], 5),
                      'rank_of_self': rank.index(name) + 1,
                      'runner_up': rank[1] if len(rank) > 1 else None,
                      'runner_up_distance': round(scores[rank[1]], 5) if len(rank) > 1 else None}
    res['PC3a_clean_leave_one_in'] = pc3a
    res['PC3a_PASS'] = all(v['rank_of_self'] == 1 and v['self_distance'] < 1e-6
                           for v in pc3a.values())

    # ---- PC3b degraded self-match ---------------------------------------
    pc3b = {}
    for name, glyphs in bank.items():
        deg = degrade(glyphs)
        scores = {other: compare(deg, bank[other])['mean_aspect'] for other in bank}
        rank = sorted(scores, key=scores.get)
        pc3b[name] = {'degraded_self_distance': round(scores[name], 5),
                      'rank_of_self': rank.index(name) + 1,
                      'runner_up': rank[1] if len(rank) > 1 else None,
                      'runner_up_distance': round(scores[rank[1]], 5) if len(rank) > 1 else None}
    res['PC3b_degraded_self_match'] = pc3b
    selfd = [v['degraded_self_distance'] for v in pc3b.values()]
    crossd = []
    for name, glyphs in bank.items():
        for other in bank:
            if other != name:
                crossd.append(compare(glyphs, bank[other])['mean_aspect'])
    res['PC3b_PASS'] = all(v['rank_of_self'] == 1 for v in pc3b.values())
    res['calibration'] = {
        'degraded_self_band': [round(min(selfd), 5), round(max(selfd), 5)],
        'degraded_self_mean': round(float(np.mean(selfd)), 5),
        'cross_face_mean': round(float(np.mean(crossd)), 5),
        'cross_face_p05': round(float(np.percentile(crossd, 5)), 5),
        'cross_face_min': round(float(np.min(crossd)), 5),
        'n_cross_pairs': len(crossd),
    }

    # ---- the real match --------------------------------------------------
    real = {}
    for name, glyphs in bank.items():
        c = compare(obs, glyphs)
        c.pop('per_rune')
        real[name] = c
    order = sorted(real, key=lambda n: real[n]['mean_aspect'])
    res['LP2_match'] = {n: real[n] for n in order}
    res['LP2_ranking'] = [(n, round(real[n]['mean_aspect'], 5),
                           round(real[n]['mean_stretch'], 5)) for n in order]

    best, second = order[0], order[1] if len(order) > 1 else None
    band = res['calibration']['degraded_self_band']
    sep = ((real[second]['mean_aspect'] - real[best]['mean_aspect']) /
           real[best]['sd_aspect']) if second and real[best]['sd_aspect'] > 0 else None
    res['verdict'] = {
        'best': best,
        'best_mean_aspect': round(real[best]['mean_aspect'], 5),
        'inside_degraded_self_band': band[0] <= real[best]['mean_aspect'] <= band[1],
        'below_cross_face_p05': real[best]['mean_aspect'] < res['calibration']['cross_face_p05'],
        'runner_up': second,
        'separation_sigma_vs_runner_up': round(sep, 3) if sep is not None else None,
        'n_rune_classes': real[best]['n'],
        'IDENTIFIED_per_prereg': bool(
            band[0] <= real[best]['mean_aspect'] <= band[1] and
            sep is not None and sep >= 2.0 and real[best]['n'] >= 20),
    }

    json.dump(res, open(os.path.join(HERE, 'font_match_results.json'), 'w'), indent=1)
    print(json.dumps({k: res[k] for k in
                      ('n_bank', 'PC3a_PASS', 'PC3b_PASS', 'calibration',
                       'LP2_ranking', 'verdict')}, indent=1))


if __name__ == '__main__':
    main()
