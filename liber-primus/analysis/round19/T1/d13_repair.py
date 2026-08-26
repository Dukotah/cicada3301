"""Test the two repairs on the control pages and across LP2."""
import numpy as np, collections, sys, os
import t1_align as A, t1_reader as T, t1_split as SP, t1_bank as B
sys.path.insert(0, os.path.join(T.LP,'src'))
from lp.gematria import IDX_TO_TRANS

r = A.run('LP2', verbose=False)
S, blab = r['S'], r['blab']
ids = np.array(sorted(blab))
Y = S.X[[S.sm_pos[int(k)] for k in ids]]
BL = np.array([blab[int(k)] for k in ids])
z = S.z

print('--- merge repair on all %d merge candidates' % int((z['w'] > A.MAXW).sum()))
res = collections.Counter()
for i in np.where(z['w'] > A.MAXW)[0]:
    m = S.mask(i)
    parts, cost = SP.split_wide(m, Y, BL)
    tag = 'NONRUNE' if parts is None else '%d-part' % len(parts)
    res[(int(z['h'][i]), int(z['w'][i]), tag)] += 1
    if parts and int(z['page'][i]) in (56, 57):
        print('   p%d w=%d -> %s (cost %.0f)' % (z['page'][i], z['w'][i],
              [IDX_TO_TRANS[p[0]] for p in parts], cost))
for k, v in sorted(res.items()):
    print('   h=%d w=%d -> %s  x%d' % (k[0], k[1], k[2], v))

print('\n--- large-initial repair on the two control pages')
for name in ['73.jpg', '74.jpg']:
    path = T.vendor_path(name)
    ink = T.page_ink(path)
    comps = T.components(ink)
    big = [c for c in comps if c['h'] > 200]
    big.sort(key=lambda c: (c['y0'], c['x0']))
    for c in big[:3]:
        lab, d = SP.read_initial(c['mask'], Y, BL)
        print('   %s comp h=%d w=%d x0=%d y0=%d -> %s (d=%.0f)'
              % (name, c['h'], c['w'], c['x0'], c['y0'],
                 IDX_TO_TRANS[lab] if lab is not None else 'REJECT', d if d else -1))
