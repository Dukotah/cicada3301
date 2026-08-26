"""What is the residual 159/13136?  Full opcode accounting, per page."""
import numpy as np, collections, difflib, sys, os
import t1_align as A, t1_reader as T
sys.path.insert(0, os.path.join(T.LP,'src'))
from lp.gematria import IDX_TO_TRANS

r = A.run('LP2', verbose=False)
S, cpage, pred = r['S'], r['cpage'], r['pred']
agg = collections.Counter(); det = []
for p in S.pages:
    if not cpage[p]: continue
    idx = S.idx_by_page[p]
    pr = list(pred[idx]); cn = cpage[p]
    sm = difflib.SequenceMatcher(None, pr, cn, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            agg['equal'] += i2 - i1
        else:
            agg[tag] += max(i2 - i1, j2 - j1)
            det.append((p, tag, i2 - i1, j2 - j1,
                        [IDX_TO_TRANS[x] if x >= 0 else '<WIDE>' for x in pr[i1:i2]],
                        [IDX_TO_TRANS[x] for x in cn[j1:j2]],
                        [int(S.w[idx[k]]) for k in range(i1, i2)]))
print('opcode totals:', dict(agg))
print('\n%d non-equal blocks:' % len(det))
for d in det:
    print('  p%-2d %-8s seg%d/canon%d  seg=%s canon=%s widths=%s'
          % (d[0], d[1], d[2], d[3], d[4], d[5], d[6]))
