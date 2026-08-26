import numpy as np, collections, difflib, sys, os
import t1_align as A, t1_reader as T
sys.path.insert(0, os.path.join(T.LP,'src'))
from lp.gematria import IDX_TO_TRANS
r = A.run('LP2', verbose=False)
S = r['S']; z = S.z
wide = np.where(z['w'] > A.MAXW)[0]
print('merge-candidate crops: %d' % len(wide))
g = collections.Counter((int(z['h'][i]), int(z['w'][i])) for i in wide)
print('  (h,w) multiset:', g.most_common())
for (h, w), n in g.most_common(6):
    ii = [i for i in wide if z['h'][i] == h and z['w'][i] == w]
    print('  h=%d w=%d n=%d  x0 range %d..%d  pages %s' %
          (h, w, n, min(z['x0'][i] for i in ii), max(z['x0'][i] for i in ii),
           sorted(set(int(z['page'][i]) for i in ii))[:14]))
print()
# where do the w=113 ones sit relative to the page text column?
ii = [i for i in wide if z['w'][i] == 113]
print('w=113: x0 %s  y0 %s' % (sorted(set(int(z['x0'][i]) for i in ii))[:12],
                               sorted(set(int(z['y0'][i]) for i in ii))[:6]))
print('   rows they land in:', collections.Counter(int(z['row'][i]) for i in ii).most_common(6))
print('   pos_in_row:', collections.Counter(int(z['pos'][i]) for i in ii).most_common(6))
# text-column x extent of normal glyphs
norm = np.where(z['w'] <= A.MAXW)[0]
print('   normal glyph x0: p5 %d p50 %d p95 %d  max x1 %d'
      % (np.percentile(z['x0'][norm], 5), np.percentile(z['x0'][norm], 50),
         np.percentile(z['x0'][norm], 95), z['x1'][norm].max()))
print()
print('=== p57 (74.jpg) read vs canon')
idx = S.idx_by_page[57]
pr = [IDX_TO_TRANS[x] if x >= 0 else '<W%d>' % z['w'][idx[k]]
      for k, x in enumerate(r['pred'][idx])]
cn = [IDX_TO_TRANS[x] for x in r['cpage'][57]]
print(' seg  (%d): %s' % (len(pr), ' '.join(pr)))
print(' canon(%d): %s' % (len(cn), ' '.join(cn)))
print(' row/pos/x of first 10 seg:', [(int(z['row'][i]), int(z['pos'][i]), int(z['x0'][i]), int(z['w'][i])) for i in idx[:10]])
print()
print('=== p56 (73.jpg) read vs canon')
idx = S.idx_by_page[56]
pr = [IDX_TO_TRANS[x] if x >= 0 else '<W%d>' % z['w'][idx[k]]
      for k, x in enumerate(r['pred'][idx])]
cn = [IDX_TO_TRANS[x] for x in r['cpage'][56]]
print(' seg  (%d): %s' % (len(pr), ' '.join(pr)))
print(' canon(%d): %s' % (len(cn), ' '.join(cn)))
