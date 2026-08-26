import numpy as np, sys, os, json
import t1_reader as T, t1_run as R, t1_align as A
sys.path.insert(0, os.path.join(T.LP,'src'))
from lp.gematria import IDX_TO_TRANS
r, votes = R.build('LP2'); S = r['S']
for p, name in [(56,'73.jpg'), (57,'74.jpg')]:
    lab = R.labels_excluding(S, r['blab'], votes, {p})
    full, small, _, _ = R.matchers(S, lab)
    seq, allrec = R.read_page(T.vendor_path(name), lab, full, small, S)
    canon = r['cpage'][p]
    rep, pairs, bad = R.align_report(seq, canon)
    used = set(i for i, j, ok in pairs)
    print('%s: emitted %d, canon %d' % (name, len(seq), len(canon)))
    for i, o in enumerate(seq):
        if i not in used:
            print('   SPURIOUS idx %d kind=%s row=%d x0=%d y0=%d h=%d w=%d -> %s d0=%s'
                  % (i, o['kind'], o['row'], o['x0'], o['y0'], o['h'], o['w'],
                     IDX_TO_TRANS[o['lab']], ('%.0f' % o['d0']) if o['d0'] else o['d0']))
    print('   kinds:', {k: sum(1 for o in seq if o['kind']==k) for k in ['glyph','split','initial']})
    print('   d0 of ordinary glyphs: max %.0f  p99 %.0f' % (
        max(o['d0'] for o in seq if o['kind']=='glyph'),
        np.percentile([o['d0'] for o in seq if o['kind']=='glyph'], 99)))
