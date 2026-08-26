"""L3 / PREREG-ADDENDUM #1 -- the ink-intensity channel (H9).

Never measured in this repository. Round 8's GEOMETRY track swept glyph SHAPE
(nearest-neighbour Hamming 0.0000), ADVANCE (1.86 sigma, unimodal) and BASELINE JITTER
(BIC rejects two components) -- and stopped. Per-glyph ink TONE was not looked at, and page
15 shows at least one element (`3299` in the 4x4 numeric grid) set visibly lighter than its
neighbours.

Measures, for every connected component on all 56 sha256-verified renders:
    mean grey of the component's pixels, and the 10th-percentile (darkest core) value,
    from the ORIGINAL 8-bit greyscale, before binarisation.

Outlier rule fixed in the addendum: > 4 sigma above the page's own body-text mean-grey
distribution, with a stroke-width-matched re-test for every candidate.

Positive control: plant known lightening at dL in {measured, 5, 10, 20, 40} on K random
components and require >= 90% recovery.
"""
import os, sys, json, time
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402

IMG = os.path.join(R.LP, 'data', 'relikd')
RUNE_BODY = (95, 140)


def page_stats(path):
    g = np.asarray(Image.open(path).convert('L')).astype(np.float32)
    ink = (g < 128)
    lab, n = ndimage.label(ink)
    if n == 0:
        return None
    objs = ndimage.find_objects(lab)
    idx = np.arange(1, n + 1)
    area = ndimage.sum(ink, lab, index=idx)
    mean = ndimage.mean(g, lab, index=idx)
    mn = ndimage.minimum(g, lab, index=idx)
    x0 = np.array([s[1].start for s in objs]); x1 = np.array([s[1].stop for s in objs])
    y0 = np.array([s[0].start for s in objs]); y1 = np.array([s[0].stop for s in objs])
    keep = area >= 20
    h = (y1 - y0)[keep]; w = (x1 - x0)[keep]
    a = area[keep]
    # stroke-width proxy: ink area / bounding-box perimeter
    sw = a / np.maximum(2.0 * (h + w), 1.0)
    return dict(mean=mean[keep], min=mn[keep], area=a, h=h, w=w,
                x0=x0[keep], y0=y0[keep], x1=x1[keep], y1=y1[keep], sw=sw,
                grey=g, ink=ink, lab=lab, keep_ids=idx[keep])


def detect(st, k_sigma=4.0):
    """Body-text reference = rune-body-height components. Outlier iff mean grey exceeds the
    body reference by > k sigma AND survives a stroke-width-matched re-test."""
    body = (st['h'] >= RUNE_BODY[0]) & (st['h'] <= RUNE_BODY[1])
    if body.sum() < 20:
        body = np.ones(len(st['h']), bool)
    mu, sd = float(st['mean'][body].mean()), float(st['mean'][body].std())
    sd = max(sd, 1e-6)
    z = (st['mean'] - mu) / sd
    cand = np.where(z > k_sigma)[0]
    out = []
    for i in cand:
        # stroke-width + height matched reference
        m = (np.abs(st['sw'] - st['sw'][i]) < 0.15 * max(st['sw'][i], 1e-6)) & \
            (np.abs(st['h'] - st['h'][i]) < 0.20 * max(st['h'][i], 1))
        m[i] = False
        if m.sum() >= 10:
            mu2, sd2 = float(st['mean'][m].mean()), max(float(st['mean'][m].std()), 1e-6)
            z2 = (st['mean'][i] - mu2) / sd2
        else:
            z2 = float('nan')
        out.append(dict(i=int(i), z_body=round(float(z[i]), 2),
                        z_matched=None if np.isnan(z2) else round(float(z2), 2),
                        mean=round(float(st['mean'][i]), 1),
                        h=int(st['h'][i]), w=int(st['w'][i]), area=int(st['area'][i]),
                        box=[int(st['x0'][i]), int(st['y0'][i]),
                             int(st['x1'][i]), int(st['y1'][i])],
                        n_matched=int(m.sum())))
    return out, mu, sd, int(body.sum())


def control(st, rng, dL, K=40, k_sigma=4.0):
    """Plant: lighten K random body components by dL grey levels, re-detect, measure recall."""
    body = np.where((st['h'] >= RUNE_BODY[0]) & (st['h'] <= RUNE_BODY[1]))[0]
    if len(body) < K:
        K = len(body)
    pick = rng.choice(body, K, replace=False)
    m2 = st['mean'].copy()
    m2[pick] = m2[pick] + dL
    stp = dict(st); stp['mean'] = m2
    got, _, _, _ = detect(stp, k_sigma)
    gi = {g['i'] for g in got}
    rec = len(gi & set(int(p) for p in pick)) / max(K, 1)
    fp = len(gi - set(int(p) for p in pick))
    return rec, fp, K


def main():
    t0 = time.time()
    res = dict(pages=[], outliers=[], control=[])
    rng = np.random.default_rng(3301)
    ctrl_done = False
    for p in range(56):
        path = os.path.join(IMG, 'p%d.jpg' % p)
        st = page_stats(path)
        if st is None:
            continue
        out, mu, sd, nbody = detect(st)
        for o in out:
            o['page'] = p
        res['outliers'] += out
        res['pages'].append(dict(page=p, n_components=int(len(st['h'])),
                                 n_body=nbody, body_mean_grey=round(mu, 2),
                                 body_sd=round(sd, 3), n_outliers=len(out)))
        if not ctrl_done and nbody >= 100:
            for dL in (2, 5, 10, 20, 40):
                rec, fp, K = control(st, rng, dL)
                res['control'].append(dict(page=p, dL=dL, K=K,
                                           recall=round(rec, 3), false_pos=fp))
            ctrl_done = True
        print('p%-2d comps %4d body %4d mean %6.2f sd %5.3f outliers %d'
              % (p, len(st['h']), nbody, mu, sd, len(out)), flush=True)
        del st
    res['n_outliers_total'] = len(res['outliers'])
    json.dump(res, open(os.path.join(HERE, 'intensity.json'), 'w'), indent=1)
    print('\ntotal intensity outliers (>4sigma, stroke-matched recorded): %d'
          % len(res['outliers']))
    print('control:', res['control'])
    print('%.1fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
