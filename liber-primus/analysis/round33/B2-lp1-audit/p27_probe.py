import os, sys, json, collections
sys.dont_write_bytecode = True
T1 = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'round19', 'T1'))
sys.path.insert(0, T1)
OUT = os.path.dirname(os.path.abspath(__file__))
import numpy as np
import t1_reader as T, t1_extract as E_, t1_align as A, t1_run as R
WK = os.path.join(OUT, 'work')
for m in (E_, A, R): m.WORK = WK
T.VENDOR = os.path.join(OUT, 'vendor_fetch')
from lp.gematria import IDX_TO_TRANS
TR = [IDX_TO_TRANS[i] for i in range(29)]
r, votes = R.build('LP2')
S = r['S']
bank = R.Bank(S, votes, r['blab'])
p = 27
full, small, lab = bank.view({p})
fast = bank.fastview({p})
path = T.relikd_path(p)
seq, allrec = R.read_page(path, full, small, page=p, fast=fast)
canon = r['cpage'][p]
rep, pairs, bad = R.align_report(seq, canon)
print('p27 canon', len(canon), 'emitted', len(seq), rep)
print('record keys', sorted(seq[0].keys()))
res = {}
ctx = []
for (i, j, ok) in pairs:
    if 88 <= j <= 98:
        o = seq[i]
        ctx.append(dict(cpos=j, canon=TR[canon[j]], t1=TR[o['lab']], ok=bool(ok), row=int(o['row']), x0=int(o['x0']), y0=int(o['y0']),
                        w=int(o['w']), h=int(o.get('h', -1)), d0=float(o['d0']), d1=float(o['d1']) if np.isfinite(o['d1']) else None, kind=o['kind']))
for c in ctx: print(c)
# target glyph
tg = [c for c in ctx if c['cpos'] == 93][0]
z, mask = E_.load('LP2')
idx = [i for i in range(len(z['page'])) if z['page'][i] == p and abs(int(z['x0'][i]) - tg['x0']) <= 2 and abs(int(z['y0'][i]) - tg['y0']) <= 2]
print('crop idx', idx)
res['ctx'] = ctx
i = idx[0]
m = mask(i)
bid = int(S.ids[i])
print('bitmap id', bid, 'shape', m.shape, 'occurrences in corpus', int((S.ids == bid).sum()), 'label cons', lab if False else None)
res['target'] = dict(crop_index=int(i), bitmap_id=bid, shape=list(m.shape), corpus_occurrences=int((S.ids == bid).sum()),
                     pages_with_bitmap=sorted(set(int(S.page[k]) for k in np.where(S.ids == bid)[0])))
# nearest exemplar per class for this glyph
from t1_match import canvas
X = canvas([m])
D = full.distances(X)[0]
labs = full.labels
byc = {}
for k in np.argsort(D):
    L = int(labs[k])
    if L < 0 or not np.isfinite(D[k]): continue
    if L not in byc: byc[L] = (float(D[k]), int(bank.ids[k]), int(bank.freq[int(bank.ids[k])]))
    if len(byc) >= 5: break
res['nearest_by_class'] = {TR[L]: dict(dist=v[0], exemplar_bitmap=v[1], exemplar_freq=v[2]) for L, v in byc.items()}
print(res['nearest_by_class'])
# save masks for rendering
np.savez_compressed(os.path.join(WK, 'p27_masks.npz'), target=m, **{('ex_%s' % TR[L]): S.bitmap(v[1]) for L, v in byc.items()})
# where is every occurrence of each of U / B exemplar in corpus and its canon-labelled rune?
json.dump(res, open(os.path.join(OUT, '_p27_probe.json'), 'w'), indent=1)
