import os, sys, json
sys.dont_write_bytecode = True
exec(open('p27_probe.py').read().split("r, votes = R.build('LP2')")[0])
r, votes = R.build('LP2'); S = r['S']; bank = R.Bank(S, votes, r['blab'])
print('votes[421]', {(p, TR[c]): n for (p, c), n in votes[421].items()})
print('votes[586]', {(p, TR[c]): n for (p, c), n in votes[586].items()})
full, small, lab = bank.view(set())
from t1_match import canvas
X = canvas([S.bitmap(586)])
D = full.distances(X)[0]; labs = full.labels
Bi = [TR.index('B')]; Ui = [TR.index('U')]
for name, L in (('B', TR.index('B')), ('U', TR.index('U'))):
    ks = [k for k in np.argsort(D) if int(labs[k]) == L][:4]
    print(name, [(int(bank.ids[k]), int(bank.freq[int(bank.ids[k])]), float(D[k])) for k in ks])
# all-corpus count of B and U exemplars, and a typical B-vs-U distance
Mb = [k for k in range(len(labs)) if int(labs[k]) == TR.index('B')]
print('n B exemplars', len(Mb), 'n U', sum(int(l) == TR.index('U') for l in labs))
# the distance of a typical high-frequency B exemplar to the U-prototype 282
k282 = list(bank.ids).index(282)
Dq = full.distances(S.X[[S.sm_pos[282]]][:, :, :] if False else canvas([S.bitmap(282)]))[0]
bs = sorted([(float(Dq[k]), int(bank.ids[k]), int(bank.freq[int(bank.ids[k])])) for k in Mb])[:5]
print('U282 -> nearest B exemplars', bs)
print('crop pages of bitmap 421 / 586 identical shape sizes', S.bitmap(421).shape, S.bitmap(586).shape)
import numpy as np
a, c = S.bitmap(421), S.bitmap(586); print('xor px 421 vs 586 (same canvas):', int((a ^ c).sum()) if a.shape == c.shape else 'diff shape', 'ink px', int(a.sum()), int(c.sum()))
