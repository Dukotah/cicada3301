import numpy as np, collections
import t1_bank as B

for face in ['LP2', 'LP1']:
    z, mask, ids, keys = B.distinct(face)
    X = B.to_canvas(keys); D = B.pairwise(X)
    n = len(z['h'])
    print('=== %s' % face)
    for tau in range(40, 200, 5):
        lab, k = B.single_linkage(D, float(tau))
        cnt = collections.Counter(lab[ids[i]] for i in range(n) if ids[i] >= 0)
        tot = sum(cnt.values())
        maj = [c for c, v in cnt.items() if v >= 50]
        cov = 100.0 * sum(cnt[c] for c in maj) / tot
        biggest = max(cnt.values())
        print('  tau %3d: %3d clusters  majors(>=50) %2d  cov %.3f%%  biggest %d'
              % (tau, k, len(maj), cov, biggest))
