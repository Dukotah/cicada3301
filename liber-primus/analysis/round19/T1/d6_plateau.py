import numpy as np, collections, json, os
import t1_bank as B, t1_reader as T

for face, tau in [('LP2', 155.0), ('LP1', 155.0)]:
    z, mask, ids, keys = B.distinct(face)
    X = B.to_canvas(keys); D = B.pairwise(X)
    lab, k = B.single_linkage(D, tau)
    cnt = collections.Counter()
    for i in range(len(z['h'])):
        if ids[i] >= 0:
            cnt[lab[ids[i]]] += 1
    tot = sum(cnt.values())
    sz = sorted(cnt.values(), reverse=True)
    print('%s tau=%.0f -> %d clusters over %d crops' % (face, tau, k, tot))
    print('  sizes:', sz)
    big = [c for c, v in cnt.items() if v >= 50]
    print('  clusters with >=50 crops: %d  covering %.3f%% of crops'
          % (len(big), 100.0 * sum(cnt[c] for c in big) / tot))
    for thr in [5, 10, 20, 50, 100]:
        b = [c for c, v in cnt.items() if v >= thr]
        print('    >=%3d crops: %2d clusters, %.3f%% coverage'
              % (thr, len(b), 100.0*sum(cnt[c] for c in b)/tot))
    # bitmaps per cluster
    bpc = collections.Counter(lab)
    print('  distinct bitmaps per cluster (desc):', sorted(bpc.values(), reverse=True))
    np.savez_compressed(os.path.join(B.WORK, 'plateau_%s.npz' % face),
                        ids=ids, lab=lab)
    print()
