import os
import sys
import json
import numpy as np
import t2lib as T
from lp.gematria import IDX_TO_TRANS

fn = sys.argv[1]
g = int(sys.argv[2])
res = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, fn))) if 'gline' in r}
r = res[g]
canon = T.canon_lines()[g]
print('seg %s line %s  ncomp %s nrune %s  W %s  total %s' %
      (r['seg'], canon['line_in_seg'], r['ncomp'], r['nrune'], r['W'], r['total']))
print('canon :', ' '.join(IDX_TO_TRANS[c] for c in r['canon']))
print('probe :', ' '.join(IDX_TO_TRANS[c] for c in r['best']))
print('tokens:', ''.join('r' if t[0] == 'r' else t[1] for t in canon['tokens']))
tm = T.load_templates()
print('widths:', [tm[c].shape[1] for c in r['canon']],
      'sum', sum(tm[c].shape[1] for c in r['canon']))
print('x     :', r['x'])
print('delta :', [round(a - b) for a, b in zip(r['canon_cost'], r['best_cost'])])
