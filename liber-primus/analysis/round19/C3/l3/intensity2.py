"""C3 / L3 -- ADDENDUM #2: repair H9's positive control, then re-measure the ink channel.

WHAT WENT WRONG IN ROUND 18
---------------------------
`intensity.py` implements the addendum's rule faithfully and reports 1 098 intensity
outliers book-wide. Its positive control -- lighten K=40 random body components by dL grey
levels and require >= 90% recovery -- returns:

    dL= 2 recall 0.050 | dL= 5 recall 0.025 | dL=10 recall 0.050 | dL=20 recall 0.000 | dL=40 recall 0.100

It fails at EVERY planted level, including a lightening of 40 grey levels that is glaring to
the eye. Per doctrine mechanic 2 that makes the 1 098 outliers uninterpretable in both
directions: they are not a positive, and their absence would not have been a negative.

The cause is diagnosable and is a defect in the CONTROL, not in the hypothesis. `detect()`
estimates the page's body-text mean and standard deviation from a set that INCLUDES the
planted components. Body ink on these renders is nearly saturated (mean grey ~0.7, sd ~1.4),
so lifting 40 of ~270 body components by 40 levels drags the mean up by ~6 and inflates the
sd from ~1.4 to ~15. The z-score of a planted component is then 40/15 = 2.7 -- below the
4-sigma bar it is supposed to trip. The plant destroys its own null.

THE REPAIR, AND WHY IT IS NOT A THRESHOLD EDIT
----------------------------------------------
The addendum's rule is kept verbatim: *a component is an outlier iff its mean grey exceeds
the page's body-text distribution by > 4 sigma, with a stroke-width-matched re-test*. What
changes is only the ESTIMATOR of that distribution: median and 1.4826 x MAD replace mean and
sd. Both estimate the same quantity for a clean Gaussian; MAD has a 50% breakdown point, so a
15% contamination cannot move it. That is a repair to the instrument, not a relaxation of the
bar, and it is filed openly here rather than edited into the addendum.

Also measured here, because it is what prompted the whole addendum: the ACTUAL grey
difference between `3299` and the other fifteen entries of the page-15 numeric grid.

Writes `intensity2.json`.
"""
import json, os, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402
from intensity import page_stats                                       # noqa: E402

IMG = os.path.join(R.LP, 'data', 'relikd')
RUNE_BODY = (95, 140)
K_SIGMA = 4.0


def robust(v):
    """median and MAD-based sigma. 50% breakdown, so a plant cannot inflate it."""
    med = float(np.median(v))
    mad = float(np.median(np.abs(v - med)))
    return med, max(1.4826 * mad, 1e-6)


def detect_robust(mean, h, sw, k_sigma=K_SIGMA):
    body = (h >= RUNE_BODY[0]) & (h <= RUNE_BODY[1])
    if body.sum() < 20:
        body = np.ones(len(h), bool)
    mu, sd = robust(mean[body])
    z = (mean - mu) / sd
    cand = np.where(z > k_sigma)[0]
    keep = []
    for i in cand:
        m = (np.abs(sw - sw[i]) < 0.15 * max(sw[i], 1e-6)) & \
            (np.abs(h - h[i]) < 0.20 * max(h[i], 1))
        m[i] = False
        if m.sum() >= 10:
            mu2, sd2 = robust(mean[m])
            if (mean[i] - mu2) / sd2 > k_sigma:      # survives the stroke-matched re-test
                keep.append(int(i))
        else:
            keep.append(int(i))                      # no matched reference: keep, flag below
    return keep, cand, mu, sd, int(body.sum())


def control(mean, h, sw, rng, dL, K=40):
    body = np.where((h >= RUNE_BODY[0]) & (h <= RUNE_BODY[1]))[0]
    K = min(K, len(body))
    pick = set(int(x) for x in rng.choice(body, K, replace=False))
    m2 = mean.copy()
    for i in pick:
        m2[i] += dL
    got, _, _, _, _ = detect_robust(m2, h, sw)
    gi = set(got)
    return len(gi & pick) / max(K, 1), len(gi - pick), K


def main():
    t0 = time.time()
    rng = np.random.default_rng(3301)
    res = dict(rule=('addendum #1 rule kept verbatim: >4 sigma above the page body-text '
                     'distribution, stroke-width-matched re-test. Estimator changed from '
                     'mean/sd to median/MAD so the plant cannot inflate its own null.'),
               control=[], pages=[], outliers=[])

    # -------------------------------------------------- control on a dense page
    st = page_stats(os.path.join(IMG, 'p10.jpg'))
    for dL in (2, 5, 10, 20, 40):
        rec, fp, K = control(st['mean'], st['h'], st['sw'], rng, dL)
        res['control'].append(dict(page=10, dL=dL, K=K, recall=round(rec, 3), false_pos=fp))
        print('CONTROL p10  dL=%-3d K=%d  recall %.3f  false-pos %d' % (dL, K, rec, fp),
              flush=True)
    passing = [c['dL'] for c in res['control'] if c['recall'] >= 0.90]
    res['control_bar'] = 0.90
    res['smallest_recoverable_dL'] = min(passing) if passing else None
    res['control_verdict'] = 'PASS' if passing else 'FAIL at every planted level tested'
    del st

    # -------------------------------------------------- sweep
    for p in range(56):
        st = page_stats(os.path.join(IMG, 'p%d.jpg' % p))
        if st is None:
            continue
        keep, cand, mu, sd, nbody = detect_robust(st['mean'], st['h'], st['sw'])
        for i in keep:
            res['outliers'].append(dict(
                page=p, mean=round(float(st['mean'][i]), 2),
                z=round(float((st['mean'][i] - mu) / sd), 2),
                h=int(st['h'][i]), w=int(st['w'][i]), area=int(st['area'][i]),
                box=[int(st['x0'][i]), int(st['y0'][i]),
                     int(st['x1'][i]), int(st['y1'][i])]))
        res['pages'].append(dict(page=p, n_components=int(len(st['h'])), n_body=nbody,
                                 body_median_grey=round(mu, 3), body_mad_sigma=round(sd, 4),
                                 n_candidates=int(len(cand)), n_after_matched_retest=len(keep)))
        print('p%-2d comps %4d body %4d  med %6.2f  mad-sigma %6.3f  cand %4d  kept %4d'
              % (p, len(st['h']), nbody, mu, sd, len(cand), len(keep)), flush=True)
        del st

    res['n_outliers_total'] = len(res['outliers'])
    res['n_candidates_total'] = sum(p['n_candidates'] for p in res['pages'])

    # -------------------------------------------------- the p15 `3299` measurement
    st = page_stats(os.path.join(IMG, 'p15.jpg'))
    # the 4x4 grid sits below the rune text; take digit-height components (30..80 px)
    dig = np.where((st['h'] >= 30) & (st['h'] <= 80))[0]
    if len(dig):
        ys = st['y0'][dig]
        order = np.argsort(ys)
        grey = st['mean'][dig]
        med, sig = robust(grey)
        z = (grey - med) / sig
        top = np.argsort(-z)[:8]
        res['p15_grid'] = dict(
            n_digit_components=int(len(dig)),
            median_grey=round(med, 2), mad_sigma=round(sig, 3),
            lightest=[dict(mean_grey=round(float(grey[i]), 2), z=round(float(z[i]), 2),
                           box=[int(st['x0'][dig][i]), int(st['y0'][dig][i]),
                                int(st['x1'][dig][i]), int(st['y1'][dig][i])],
                           h=int(st['h'][dig][i]), w=int(st['w'][dig][i]))
                      for i in top],
            max_z=round(float(z.max()), 2),
            note=('measured delta between the lightest digit component and the page-15 digit '
                  'median, in 8-bit grey levels: %.2f' % float(grey[top[0]] - med)))
        print('\np15 grid: %d digit components, median grey %.2f, MAD-sigma %.3f, max z %.2f'
              % (len(dig), med, sig, z.max()))

    json.dump(res, open(os.path.join(HERE, 'intensity2.json'), 'w'), indent=1)
    print('\nCONTROL VERDICT : %s  (smallest recoverable dL: %s)'
          % (res['control_verdict'], res['smallest_recoverable_dL']))
    print('candidates %d -> outliers after stroke-matched re-test %d'
          % (res['n_candidates_total'], res['n_outliers_total']))
    print('%.1fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
