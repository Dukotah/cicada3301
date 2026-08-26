"""Diagnostic (not a measurement): where does connected-component segmentation lose
glyphs?  Height histograms, per-row counts vs canon per-line counts, and wide/narrow
component inspection.  Informs PREREG section 5's checkpoint; classifies nothing.
"""
import os
import sys
import json
import numpy as np
import t1_reader as T
sys.path.insert(0, os.path.join(T.LP, 'src'))
from lp.gematria import RUNE_TO_IDX  # noqa: E402
from lp import corpus  # noqa: E402


def hist(path, tag):
    ink = T.page_ink(path)
    comps = T.components(ink)
    h = np.array([c['h'] for c in comps])
    w = np.array([c['w'] for c in comps])
    print('%-10s comps=%4d  h: med %d  p10 %d p90 %d  max %d' %
          (tag, len(comps), np.median(h), np.percentile(h, 10),
           np.percentile(h, 90), h.max()))
    # cluster of heights
    vals, cnt = np.unique(h, return_counts=True)
    top = sorted(zip(cnt, vals), reverse=True)[:8]
    print('           top heights:', ', '.join('%d(x%d)' % (v, c) for c, v in top))
    inband = [(c['h'], c['w']) for c in comps if T.RUNE_H[0] <= c['h'] <= T.RUNE_H[1]]
    print('           in [95,135]: %d   widths med %d max %d' %
          (len(inband), np.median([w for _, w in inband]) if inband else -1,
           max([w for _, w in inband]) if inband else -1))
    return comps


def canon_lines(label):
    pg = corpus.page_by_label(label)
    out = []
    for ln in pg['runes'].splitlines():
        r = [c for c in ln if c in RUNE_TO_IDX]
        if r:
            out.append(''.join(r))
    return out


def rowcheck(path, label, tag):
    glyphs, rows = T.segment_page(path)
    cl = canon_lines(label)
    print('\n%s  segmented rows=%d (%s)   canon lines=%d (%s)  totals %d vs %d' %
          (tag, len(rows), [len(r) for r in rows], len(cl), [len(x) for x in cl],
           len(glyphs), sum(len(x) for x in cl)))


if __name__ == '__main__':
    print('=== LP2 target/control ===')
    for p in [0, 45, 54]:
        hist(T.relikd_path(p), 'p%d' % p)
    for n in ['73.jpg', '74.jpg']:
        hist(T.vendor_path(n), n)
    print('\n=== LP1 ===')
    for n in ['01.jpg', '03.jpg', '05.jpg', '06.jpg', '14.jpg']:
        hist(T.vendor_path(n), n)

    print('\n=== row vs canon-line ===')
    rowcheck(T.vendor_path('73.jpg'), '73.jpg - 56.jpg', '73.jpg')
    rowcheck(T.vendor_path('74.jpg'), '74.jpg - 57.jpg', '74.jpg')
    rowcheck(T.vendor_path('01.jpg'), 'Runes - 01.jpg', '01.jpg')
    rowcheck(T.vendor_path('05.jpg'), '05.jpg', '05.jpg')
    rowcheck(T.vendor_path('03.jpg'), '03.jpg', '03.jpg')
    rowcheck(T.vendor_path('06.jpg'), '06.jpg', '06.jpg')
    rowcheck(T.vendor_path('14.jpg'), '14.jpg - 107.jpg', '14.jpg')
