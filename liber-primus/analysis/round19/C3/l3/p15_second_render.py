"""C3 / L3 -- is the page-15 grey anomaly IN THE DOCUMENT, or in this JPEG?

`h9_verdict.py` measured it: four adjacent digit components on page 15, all on one row
(y 1016..1094, x 913..1148), sit at mean grey 60.1-61.2 against a page-15 digit median of
10.06 -- a delta of ~51 grey levels at z ~ 92 in MAD units, where every other digit on the
page is at z <= 13. They are the same height and width as their neighbours, so the
stroke-width-and-height-matched re-test cannot explain them away.

That is a real measurement of the render. It is NOT yet a statement about the Liber Primus,
because a JPEG is not a document: local quantisation, a chroma edge, or a lossy re-encode can
lighten a run of adjacent glyphs. The test that separates the two is a SECOND, INDEPENDENT
render of the same page.

The repo holds one candidate: the vendored 2014 asset set. `hashes.py` established that asset
`17.jpg` is byte-identical to `data/relikd/p0.jpg`, so the offset is +17 and page 15 should be
asset `32.jpg`. This script checks whether that file is byte-identical to `relikd/p15.jpg`
(in which case it is the SAME render and buys nothing, and that is the honest answer) or a
genuinely different encode (in which case the anomaly can be confirmed or refuted).

Writes `p15_second_render.json`.
"""
import hashlib, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402
from intensity import page_stats                                       # noqa: E402
from intensity2 import robust                                          # noqa: E402

ASSETS = os.path.join(R.ROOT, 'corpus', 'E-tooling', 'vendor',
                      'cicada-solvers__documenting-cicada3301-scream314',
                      'assets', '2014', 'liber-primus-complete')
RELIKD = os.path.join(R.LP, 'data', 'relikd')

# the four components h9_verdict.py flagged, as [x0,y0,x1,y1] in the relikd p15 render
TARGET_BOXES = [[974, 1016, 1022, 1093],
                [1035, 1016, 1086, 1094],
                [1097, 1016, 1148, 1094],
                [913, 1016, 958, 1094]]


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def digit_stats(path):
    st = page_stats(path)
    if st is None:
        return None
    dig = np.where((st['h'] >= 30) & (st['h'] <= 80))[0]
    grey = st['mean'][dig]
    med, sig = robust(grey)
    return st, dig, grey, med, sig


def main():
    out = {}
    a = os.path.join(RELIKD, 'p15.jpg')
    b = os.path.join(ASSETS, '32.jpg')
    out['relikd_p15'] = dict(path=os.path.relpath(a, R.ROOT).replace('\\', '/'),
                             sha256=sha(a), bytes=os.path.getsize(a))
    if not os.path.exists(b):
        out['second_render'] = None
        out['conclusion'] = 'no second render available in this repository'
        json.dump(out, open(os.path.join(HERE, 'p15_second_render.json'), 'w'), indent=1)
        print(out['conclusion'])
        return
    out['asset_32'] = dict(path=os.path.relpath(b, R.ROOT).replace('\\', '/'),
                           sha256=sha(b), bytes=os.path.getsize(b))
    identical = out['relikd_p15']['sha256'] == out['asset_32']['sha256']
    out['byte_identical'] = identical
    print('relikd p15 sha256 %s' % out['relikd_p15']['sha256'][:16])
    print('asset  32  sha256 %s' % out['asset_32']['sha256'][:16])
    print('byte identical: %s' % identical)

    # measure the anomaly in BOTH files regardless -- if identical, the second column is
    # a consistency check on the measurement code, not independent evidence, and is
    # labelled that way.
    res = {}
    for name, path in (('relikd_p15', a), ('asset_32', b)):
        s = digit_stats(path)
        if s is None:
            continue
        st, dig, grey, med, sig = s
        rows = []
        for bx in TARGET_BOXES:
            # nearest component by bounding-box centre
            cx = (bx[0] + bx[2]) / 2.0; cy = (bx[1] + bx[3]) / 2.0
            ccx = (st['x0'][dig] + st['x1'][dig]) / 2.0
            ccy = (st['y0'][dig] + st['y1'][dig]) / 2.0
            k = int(np.argmin((ccx - cx) ** 2 + (ccy - cy) ** 2))
            rows.append(dict(target_box=bx,
                             found_box=[int(st['x0'][dig][k]), int(st['y0'][dig][k]),
                                        int(st['x1'][dig][k]), int(st['y1'][dig][k])],
                             mean_grey=round(float(grey[k]), 2),
                             z=round(float((grey[k] - med) / sig), 2)))
        res[name] = dict(n_digit_components=int(len(dig)),
                         digit_median_grey=round(med, 2), mad_sigma=round(sig, 3),
                         targets=rows,
                         mean_grey_of_targets=round(float(np.mean(
                             [r['mean_grey'] for r in rows])), 2))
        print('\n%s: %d digit comps, median grey %.2f, MAD-sigma %.3f'
              % (name, len(dig), med, sig))
        for r in rows:
            print('    box %s  grey %6.2f  z %7.2f' % (r['found_box'], r['mean_grey'],
                                                       r['z']))
    out['measurements'] = res
    if identical:
        out['conclusion'] = (
            'The only other render of page 15 held in this repository is BYTE-IDENTICAL to '
            'data/relikd/p15.jpg, so it is the same file, not an independent encode. The '
            'anomaly is therefore established as a property of THIS RENDER and is NOT yet '
            'established as a property of the document. Reopening condition: obtain a second '
            'independent render or the original PDF of page 15 and re-measure these four '
            'component boxes.')
    else:
        same = (res.get('asset_32', {}).get('mean_grey_of_targets') is not None and
                abs(res['asset_32']['mean_grey_of_targets']
                    - res['relikd_p15']['mean_grey_of_targets']) < 10)
        out['reproduces_in_second_render'] = bool(same)
        out['conclusion'] = ('anomaly reproduces in an independent render -> it is in the '
                             'document, not in the JPEG' if same else
                             'anomaly does NOT reproduce in an independent render -> it is '
                             'an artifact of the relikd encode')
    print('\n' + out['conclusion'])
    json.dump(out, open(os.path.join(HERE, 'p15_second_render.json'), 'w'), indent=1)
    print('wrote p15_second_render.json')


if __name__ == '__main__':
    main()
