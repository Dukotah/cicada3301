"""Accuracy as a function of local page density (PREREG section 3).

The OTP pages 45-54 are the densest and are where every prior audit was weakest, so the
brief asks for this axis explicitly.  Density is measured two ways: runes per page, and
runes per text row (the local quantity), and agreement is stratified by both.
"""
import os, sys, json, collections
import numpy as np
import t1_reader as T
sys.path.insert(0, os.path.join(T.LP, 'src'))
from lp.gematria import IDX_TO_TRANS  # noqa: E402

z = np.load(os.path.join(T.HERE, 'work', 'corpus_lp2.npz'), allow_pickle=True)
cor = json.load(open(os.path.join(T.HERE, 'out_corpus_lp2.json')))
pg = {r['page']: r for r in cor['pages'] if r['canon']}

# per-page density
rows = []
for p, r in sorted(pg.items()):
    m = z['page'] == p
    nrows = int(z['row'][m].max()) + 1 if m.any() else 1
    rows.append(dict(page=p, canon=r['canon'], rows=nrows,
                     per_row=r['canon'] / nrows, correct=r['correct'],
                     acc=r['accuracy']))
rows.sort(key=lambda x: x['per_row'])
q = np.array([x['per_row'] for x in rows])
print('runes per text row across LP2 pages: min %.1f  p50 %.1f  max %.1f'
      % (q.min(), np.median(q), q.max()))
print('\nquartile of local density (runes per row) -> pooled agreement:')
out = []
for i in range(4):
    lo, hi = int(i * len(rows) / 4), int((i + 1) * len(rows) / 4)
    sl = rows[lo:hi]
    c = sum(x['canon'] for x in sl); k = sum(x['correct'] for x in sl)
    print('  Q%d  per-row %.1f-%.1f  pages %2d  canon %5d  correct %5d  = %.4f%%'
          % (i + 1, sl[0]['per_row'], sl[-1]['per_row'], len(sl), c, k, 100.0 * k / c))
    out.append(dict(q=i + 1, lo=sl[0]['per_row'], hi=sl[-1]['per_row'], pages=len(sl),
                    canon=c, correct=k, accuracy=100.0 * k / c))

print('\nthe OTP dense block, image pages 45-54 (canon entries 44-53):')
dense = [pg[p] for p in range(45, 56) if p in pg]
c = sum(x['canon'] for x in dense); k = sum(x['correct'] for x in dense)
print('  pages %s' % [x['page'] for x in dense])
print('  canon %d  correct %d = %.4f%%   1:1 wrong %d  missing %d  spurious %d'
      % (c, k, 100.0 * k / c, sum(x['wrong'] for x in dense),
         sum(x['missing'] for x in dense), sum(x['spurious'] for x in dense)))
rest = [x for p, x in sorted(pg.items()) if p < 45]
c2 = sum(x['canon'] for x in rest); k2 = sum(x['correct'] for x in rest)
print('  rest of the book (pages 0-44): canon %d correct %d = %.4f%%'
      % (c2, k2, 100.0 * k2 / c2))

# exact-bitmap-match rate by density (the mechanism behind the accuracy)
print('\nfraction of positions whose crop is a BYTE-IDENTICAL twin of a bank exemplar:')
for i, lab in [(0, 'pages 0-44'), (1, 'pages 45-55')]:
    m = (z['page'] < 45) if i == 0 else (z['page'] >= 45)
    d = z['d0'][m & (z['d0'] >= 0)]
    print('  %-12s %d/%d = %.4f%%   d0 p99 %.0f' % (lab, (d == 0).sum(), len(d),
          100.0 * (d == 0).sum() / len(d), np.percentile(d, 99)))

json.dump(dict(quartiles=out, per_page=rows,
               dense_45_55=dict(canon=c, correct=k, accuracy=100.0 * k / c),
               rest_0_44=dict(canon=c2, correct=k2, accuracy=100.0 * k2 / c2)),
          open(os.path.join(T.HERE, 'out_density.json'), 'w'), indent=1)
print('-> out_density.json')
