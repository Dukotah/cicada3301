import numpy as np, collections, sys, os
import t1_align as A, t1_reader as T
sys.path.insert(0, os.path.join(T.LP,'src'))
from lp.gematria import IDX_TO_TRANS, RUNE_TO_IDX

r = A.run('LP2', verbose=False)
S, votes = r['S'], r['votes']
def art(b, step=3):
    m = S.bitmap(b)
    for y in range(0, m.shape[0], step):
        print('    ' + ''.join('#' if m[y, x] else '.' for x in range(0, m.shape[1], 2)))
    print('    h=%d w=%d ink=%d' % (m.shape[0], m.shape[1], m.sum()))

imp = sorted(((sum(c.values())-c.most_common(1)[0][1], b) for b, c in votes.items()),
             reverse=True)
print('=== top impure bitmaps')
for k, b in imp[:3]:
    print(' bitmap %d  votes=%s' % (b, [(IDX_TO_TRANS[i], v) for i, v in votes[b].most_common()]))
    art(b)
print('=== pure bitmaps labelled U and Y (largest)')
for want in ['U', 'Y']:
    wi = [i for i in range(29) if IDX_TO_TRANS[i] == want][0]
    cand = [(sum(c.values()), b) for b, c in votes.items()
            if len(c) == 1 and c.most_common(1)[0][0] == wi]
    cand.sort(reverse=True)
    print(' %s: %d pure bitmaps, largest n=%s' % (want, len(cand), cand[0] if cand else None))
    if cand: art(cand[0][1])
# totals
tot = collections.Counter()
for b, c in votes.items():
    for k, v in c.items(): tot[IDX_TO_TRANS[k]] += v
print('\ncanon label totals over aligned positions:', tot.most_common())
