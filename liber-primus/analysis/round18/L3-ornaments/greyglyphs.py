"""L3 / PREREG-ADDENDUM #1 -- the clean form of the ink-intensity detector.

The MEAN grey of a component is confounded by stroke width and antialiasing.  The
MINIMUM grey is not: a glyph printed in solid black has at least one pixel at ~0 no matter
how thin it is, while a glyph printed in a lighter tone has a floor above 0 across its whole
body.  That makes `min grey` an almost confound-free discriminator, and it is what this
script sweeps over all 56 sha256-verified renders.

Detector:  a component with area >= 300 px whose MINIMUM grey exceeds `FLOOR` is set in a
           lighter tone than the body text.
Positive control: lighten K random components by dL grey levels and require >= 90% recovery,
           and require the false-positive count on the untouched page to be reported.

Writes greyglyphs.json.
"""
import os, sys, json, time
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402

IMG = os.path.join(R.LP, 'data', 'relikd')
FLOOR = 30.0            # a solid-black glyph reaches ~0; this is far above JPEG ringing
MIN_AREA = 300


def page_components(path):
    g = np.asarray(Image.open(path).convert('L')).astype(np.float32)
    ink = g < 200
    lab, n = ndimage.label(ink)
    if n == 0:
        return None
    idx = np.arange(1, n + 1)
    objs = ndimage.find_objects(lab)
    area = ndimage.sum(ink, lab, index=idx)
    mn = ndimage.minimum(g, lab, index=idx)
    mean = ndimage.mean(g, lab, index=idx)
    x0 = np.array([s[1].start for s in objs]); x1 = np.array([s[1].stop for s in objs])
    y0 = np.array([s[0].start for s in objs]); y1 = np.array([s[0].stop for s in objs])
    k = area >= MIN_AREA
    return dict(area=area[k], min=mn[k], mean=mean[k],
                x0=x0[k], x1=x1[k], y0=y0[k], y1=y1[k])


def main():
    t0 = time.time()
    out, pages, ctrl = [], [], []
    for p in range(56):
        c = page_components(os.path.join(IMG, 'p%d.jpg' % p))
        if c is None:
            continue
        hit = np.where(c['min'] > FLOOR)[0]
        for i in hit:
            out.append(dict(page=p, box=[int(c['x0'][i]), int(c['y0'][i]),
                                         int(c['x1'][i]), int(c['y1'][i])],
                            min_grey=round(float(c['min'][i]), 1),
                            mean_grey=round(float(c['mean'][i]), 1),
                            area=int(c['area'][i])))
        pages.append(dict(page=p, n_components=int(len(c['min'])),
                          min_grey_median=round(float(np.median(c['min'])), 2),
                          min_grey_p99=round(float(np.quantile(c['min'], 0.99)), 2),
                          n_light=int(len(hit))))
        if p == 0:
            # positive control on an untouched page
            for dL in (10, 20, 40, 60):
                m2 = c['min'].copy()
                pick = np.random.default_rng(3301).choice(len(m2), 20, replace=False)
                m2[pick] += dL
                got = set(np.where(m2 > FLOOR)[0].tolist())
                rec = len(got & set(int(v) for v in pick)) / 20.0
                ctrl.append(dict(dL=dL, K=20, recall=round(rec, 3),
                                 false_pos=int(len(got - set(int(v) for v in pick)))))
        print('p%-2d comps %4d  median min-grey %5.2f  p99 %6.2f  light components %d'
              % (p, len(c['min']), np.median(c['min']),
                 np.quantile(c['min'], 0.99), len(hit)), flush=True)

    res = dict(floor=FLOOR, min_area=MIN_AREA, pages=pages, light=out,
               n_light=len(out), control=ctrl)
    json.dump(res, open(os.path.join(HERE, 'greyglyphs.json'), 'w'), indent=1)
    print('\nCONTROL (page 0, plant dL on 20 components):', ctrl)
    print('LIGHT-INK COMPONENTS BOOK-WIDE (area>=%d, min grey>%.0f): %d'
          % (MIN_AREA, FLOOR, len(out)))
    for o in out:
        print('  p%-3d box %s  min %5.1f  mean %5.1f  area %d'
              % (o['page'], o['box'], o['min_grey'], o['mean_grey'], o['area']))
    print('%.1fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
