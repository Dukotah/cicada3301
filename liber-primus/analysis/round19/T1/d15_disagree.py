import numpy as np, collections, sys, os, json
import t1_reader as T
sys.path.insert(0, os.path.join(T.LP,'src'))
from lp.gematria import IDX_TO_TRANS
z = np.load(os.path.join(T.HERE,'work','corpus_lp2.npz'), allow_pickle=True)
bad = np.where(z['canon'] != z['t1'])[0]
print('1:1 disagreements: %d of %d aligned' % (len(bad), len(z['canon'])))
for i in bad:
    print('  p%-2d cpos %5d row %2d x0 %4d y0 %4d w %3d kind=%-7s canon=%-3s T1=%-3s d0=%.0f d1=%.0f'
          % (z['page'][i], z['cpos'][i], z['row'][i], z['x0'][i], z['y0'][i], z['w'][i],
             z['kind'][i], IDX_TO_TRANS[z['canon'][i]], IDX_TO_TRANS[z['t1'][i]],
             z['d0'][i], z['d1'][i]))
print('\npairs:', collections.Counter('%s->%s' % (IDX_TO_TRANS[z['canon'][i]], IDX_TO_TRANS[z['t1'][i]]) for i in bad).most_common())
print('\nd0 distribution over ALL aligned positions:')
d0 = z['d0'][z['d0'] >= 0]
for q in [50, 90, 99, 99.9, 100]:
    print('   p%-5s %.0f' % (q, np.percentile(d0, q)))
print('  d0 == 0: %d (%.3f%%)' % ((d0 == 0).sum(), 100.0*(d0==0).sum()/len(d0)))
d1 = z['d1'][z['d1'] > 0]
print('margin d1 (nearest DIFFERENT-label exemplar): min %.0f p1 %.0f p50 %.0f' %
      (d1.min(), np.percentile(d1,1), np.percentile(d1,50)))
print('  agreeing positions: d1 min %.0f' % z['d1'][(z['canon']==z['t1']) & (z['d1']>0)].min())
print('  disagreeing:', [(int(z['d0'][i]), int(z['d1'][i])) for i in bad])
