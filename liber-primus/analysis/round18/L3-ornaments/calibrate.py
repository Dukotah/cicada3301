"""L3 gate G-A -- calibrate the band reader on CRYPTOGRAPHICALLY SOLVED pages.

The relikd p0..p55 set contains NO solved page (LP2 0-54 is the unsolved block; the two
solved LP2 pages 56/57 are 404 on that mirror).  But the full 2014 render set IS vendored
in this repo under
  corpus/E-tooling/vendor/cicada-solvers__documenting-cicada3301-scream314/
     assets/2014/liber-primus-complete/
and asset 17.jpg is **byte-identical by sha256** to relikd p0.jpg -- same lineage, same
2400x3600 render.  So the reader can be calibrated on pages whose plaintext is known by
DECRYPTION, not merely by consensus transcription.

Control pages (every LP page with a documented key):
  01.jpg A WARNING | 03.jpg WELCOME | 05.jpg SOME WISDOM | 06.jpg A KOAN
  14.jpg A KOAN (circumference) | 73.jpg LP2 p56 | 74.jpg LP2 p57

Method: read every text row with the SAME `read_strip` used on ornament bands, map
template classes through the stored R9 bijection, concatenate the page, and align to the
page's canonical rune sequence with difflib (line breaks in the markdown source do not
match the image's line breaks, so line-wise matching would measure the wrong thing).

PASS bar fixed in PREREG: per-glyph agreement >= 90%.
"""
import os, sys, json, difflib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402
sys.path.insert(0, os.path.join(R.LP, 'src'))
from lp import corpus                                                  # noqa: E402
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS                      # noqa: E402

ASSETS = os.path.join(R.ROOT, 'corpus', 'E-tooling', 'vendor',
                      'cicada-solvers__documenting-cicada3301-scream314',
                      'assets', '2014', 'liber-primus-complete')

CONTROL = [('01.jpg', 'Runes - 01.jpg', 'A WARNING'),
           ('03.jpg', '03.jpg', 'WELCOME'),
           ('05.jpg', '05.jpg', 'SOME WISDOM'),
           ('06.jpg', '06.jpg', 'A KOAN'),
           ('14.jpg', '14.jpg', 'A KOAN (circumference)'),
           ('73.jpg', '73.jpg - 56.jpg', 'LP2 p56'),
           ('74.jpg', '74.jpg - 57.jpg', 'LP2 p57')]


def canon_runes(label):
    pg = corpus.page_by_label(label)
    return [RUNE_TO_IDX[c] for c in pg['runes'] if c in RUNE_TO_IDX]


def read_page(path, tmpl, mapping, strip=True):
    ink = R.text_ink(path)[0] if strip else R.page_ink(path)
    rows = R.rows_from_ink(ink)
    seq, costs, meta = [], [], []
    for a, b in rows:
        g = R.read_ink_strip(ink, a - 4, b + 4, tmpl)
        for cid, x, k in g:
            seq.append(mapping.get(cid, -1))
            costs.append(k)
            meta.append((a, x))
    return seq, costs, meta, rows


STRIP = ('--raw' not in sys.argv)


def main():
    tmpl = R.load_templates()
    mapping = R.load_mapping()
    print('templates %d classes | stored R9 bijection %d classes' % (len(tmpl), len(mapping)))

    tot_hit = tot_cmp = 0
    costs_text = []
    per_page = []
    for asset, label, title in CONTROL:
        path = os.path.join(ASSETS, asset)
        if not os.path.exists(path):
            print('MISSING %s' % path)
            continue
        canon = canon_runes(label)
        seq, costs, meta, rows = read_page(path, tmpl, mapping, strip=STRIP)
        sm = difflib.SequenceMatcher(a=seq, b=canon, autojunk=False)
        hit = sum(bl.size for bl in sm.get_matching_blocks())
        cmp_ = max(len(seq), len(canon))
        tot_hit += hit
        tot_cmp += cmp_
        costs_text += costs
        per_page.append(dict(asset=asset, title=title, text_rows=len(rows),
                             glyphs_read=len(seq), canon_runes=len(canon),
                             matched=int(hit),
                             agreement=round(100.0 * hit / max(cmp_, 1), 2)))
        print('%-8s %-24s rows %2d  read %4d  canon %4d  matched %4d  agree %6.2f%%'
              % (asset, title, len(rows), len(seq), len(canon), hit,
                 100.0 * hit / max(cmp_, 1)))

    acc = 100.0 * tot_hit / max(tot_cmp, 1)
    med = float(np.median(costs_text))
    q90 = float(np.quantile(costs_text, 0.90))
    q99 = float(np.quantile(costs_text, 0.99))
    print('\nGATE G-A  solved-page per-glyph agreement: %d / %d = %.2f%% (bar 90%%) -> %s'
          % (tot_hit, tot_cmp, acc, 'PASS' if acc >= 90 else 'FAIL'))
    print('template match cost on KNOWN TEXT: median %.1f  p90 %.1f  p99 %.1f'
          % (med, q90, q99))

    json.dump(dict(control_pages=per_page, glyphs_compared=tot_cmp,
                   matched=tot_hit, agreement_pct=round(acc, 3),
                   text_cost_median=med, text_cost_p90=q90, text_cost_p99=q99,
                   runic_cost_bar=300.0,
                   gate='PASS' if acc >= 90 else 'FAIL', bar=90.0),
              open(os.path.join(HERE, 'calibration.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
