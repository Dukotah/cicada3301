"""T1 checkpoint -- PREREG section 5 kill condition.

Segment every LP2 page and compare the emitted rune-candidate count with canon's rune
count for that page.  If the streams cannot be put into 1:1 positional correspondence
to within 1% on the LP2 CONTROL pages, the lane stops (per PREREG section 5), because
per-rune classification accuracy is meaningless without positional correspondence --
that is exactly the error analysis/vision/DIFF-REPORT.md made.

Nothing here classifies anything.  This runs BEFORE any exemplar bank exists.
"""
import os
import json
import numpy as np

import t1_reader as T

OUT = os.path.join(T.HERE, 'out_segcheck.json')


def main():
    canon = T.canon_pages()
    rows = []
    for p in range(56):
        path = T.relikd_path(p)
        glyphs, grows = T.segment_page(path)
        n = len(glyphs)
        c = len(canon.get(p, ''))
        rows.append(dict(page=p, src='relikd/p%d.jpg' % p, face='LP2',
                         segmented=n, canon=c, delta=n - c,
                         rows=len(grows),
                         pct=None if c == 0 else 100.0 * (n - c) / c))
        print('p%-2d  seg %5d  canon %5d  delta %+4d  rows %3d' % (p, n, c, n - c, len(grows)),
              flush=True)

    # the two LP2 solved control pages live only in the vendored (same-lineage) set
    for name, lab in [('73.jpg', '73.jpg - 56.jpg'), ('74.jpg', '74.jpg - 57.jpg')]:
        path = T.vendor_path(name)
        glyphs, grows = T.segment_page(path)
        rows.append(dict(page=name, src='vendor/%s' % name, face='LP2',
                         segmented=len(glyphs), canon=None, delta=None,
                         rows=len(grows), pct=None,
                         sha256=T.sha256(path)))
        print('%-8s seg %5d  rows %3d' % (name, len(glyphs), len(grows)), flush=True)

    for name in ['01.jpg', '03.jpg', '05.jpg', '06.jpg', '14.jpg']:
        path = T.vendor_path(name)
        glyphs, grows = T.segment_page(path)
        rows.append(dict(page=name, src='vendor/%s' % name, face='LP1',
                         segmented=len(glyphs), canon=None, delta=None,
                         rows=len(grows), pct=None,
                         sha256=T.sha256(path)))
        print('%-8s seg %5d  rows %3d  (LP1)' % (name, len(glyphs), len(grows)), flush=True)

    lp2 = [r for r in rows if r['canon']]
    tot_s = sum(r['segmented'] for r in lp2)
    tot_c = sum(r['canon'] for r in lp2)
    summ = dict(lp2_pages=len(lp2), lp2_segmented=tot_s, lp2_canon=tot_c,
                lp2_delta=tot_s - tot_c,
                lp2_pct=100.0 * (tot_s - tot_c) / tot_c,
                exact_pages=sum(1 for r in lp2 if r['delta'] == 0),
                within1pct=sum(1 for r in lp2 if abs(r['pct']) <= 1.0))
    print('\nLP2 p0-p55: segmented %d vs canon %d  (delta %+d, %.3f%%)'
          % (tot_s, tot_c, tot_s - tot_c, summ['lp2_pct']))
    print('exact-count pages: %d/%d   within 1%%: %d/%d'
          % (summ['exact_pages'], len(lp2), summ['within1pct'], len(lp2)))
    json.dump(dict(summary=summ, rows=rows), open(OUT, 'w'), indent=1)
    print('->', OUT)


if __name__ == '__main__':
    main()
