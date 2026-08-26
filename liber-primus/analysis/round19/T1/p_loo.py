"""P-3 (PREREG section 4) -- LEAVE-ONE-BITMAP-OUT, and gate G-OAE at full corpus power.

The plants P-1/P-2 measure detection but are limited to ~100 sites.  This measures the
classifier's ceiling on EVERY glyph in the book: each distinct bitmap is classified
against a bank with ITSELF REMOVED, so nothing is ever matched to a copy of itself.

Then the quantity gate G-OAE turns on: for the {O, A, AE} triple, the within-class
distance against the between-class distance, and the pairwise confusion in both
directions, over all 1,4xx family glyphs rather than a 21-site plant.
"""
import os, sys, json, collections
import numpy as np
import t1_reader as T, t1_run as R, t1_align as A
from t1_match import Matcher
sys.path.insert(0, os.path.join(T.LP, 'src'))
from lp.gematria import IDX_TO_TRANS  # noqa: E402

TR = [IDX_TO_TRANS[i] for i in range(29)]
TRIPLE = [TR.index(x) for x in ('O', 'A', 'AE')]


def main():
    r, votes = R.build('LP2')
    S, blab = r['S'], r['blab']
    ids = np.array(sorted(k for k in blab if k in S.sm_pos))
    BL = np.array([blab[int(k)] for k in ids])
    Y = S.X[[S.sm_pos[int(k)] for k in ids]]
    M = Matcher(Y, BL)
    freq = collections.Counter(int(b) for b in S.ids)

    conf = np.zeros((29, 29), int)      # crop-weighted, leave-one-bitmap-out
    confb = np.zeros((29, 29), int)     # bitmap-weighted
    D = None
    rows = []
    for s in range(0, len(ids), 256):
        ch = np.arange(s, min(s + 256, len(ids)))
        Dc = M.distances(Y[ch])
        for k, gi in enumerate(ch):
            row = Dc[k].copy()
            row[gi] = np.inf                       # LEAVE ITSELF OUT
            j = int(row.argmin())
            call = int(BL[j])
            true = int(BL[gi])
            n = freq[int(ids[gi])]
            conf[true, call] += n
            confb[true, call] += 1
            same = row.copy(); same[BL != true] = np.inf
            other = row.copy(); other[BL == true] = np.inf
            rows.append(dict(bitmap=int(ids[gi]), n=n, true=true, call=call,
                             d_same=float(same.min()), d_other=float(other.min())))
        print('   loo %d/%d' % (ch[-1] + 1, len(ids)), flush=True)

    tot = conf.sum(); ok = np.trace(conf)
    print('\nP-3 leave-one-bitmap-out, crop-weighted: %d/%d = %.4f%%' % (ok, tot, 100.0*ok/tot))
    print('P-3 bitmap-weighted: %d/%d = %.4f%%'
          % (np.trace(confb), confb.sum(), 100.0*np.trace(confb)/confb.sum()))
    print('\nper-class recall (crop-weighted):')
    for i in range(29):
        n = conf[i].sum()
        if n:
            mis = {TR[j]: int(conf[i][j]) for j in range(29) if j != i and conf[i][j]}
            print('   %-3s n=%5d recall %8.4f%%  %s' % (TR[i], n, 100.0*conf[i][i]/n,
                  ('MISCALLS ' + str(mis)) if mis else ''))

    print('\n=== G-OAE : the {O, A, AE} triple at full corpus power')
    print('        ' + ''.join('%9s' % t for t in ('O', 'A', 'AE')) + '%12s' % 'recall')
    oae = {}
    for a in TRIPLE:
        n = conf[a].sum()
        print('   %-4s' % TR[a] + ''.join('%9d' % conf[a][b] for b in TRIPLE)
              + '%12s' % ('%.4f%%' % (100.0*conf[a][a]/n)))
        for b in TRIPLE:
            if a != b:
                oae['%s->%s' % (TR[a], TR[b])] = dict(n=int(conf[a][b]), of=int(n),
                                                      rate=float(conf[a][b])/n)
        oae['recall_' + TR[a]] = dict(n=int(conf[a][a]), of=int(n), rate=float(conf[a][a])/n)
    print('   family size: %d crops = %.2f%% of the corpus'
          % (sum(conf[a].sum() for a in TRIPLE),
             100.0*sum(conf[a].sum() for a in TRIPLE)/tot))

    print('\n  separation, within-class vs between-class nearest-exemplar distance:')
    for a in TRIPLE:
        rs = [x for x in rows if x['true'] == a]
        ds = np.array([x['d_same'] for x in rs]); do = np.array([x['d_other'] for x in rs])
        print('   %-3s bitmaps=%3d  d(same) max %6.0f p99 %6.0f | d(other) MIN %6.0f p1 %6.0f'
              '  -> separated at every bitmap: %s'
              % (TR[a], len(rs), ds.max(), np.percentile(ds, 99),
                 do.min(), np.percentile(do, 1), bool((ds < do).all())))
    allsep = all(x['d_same'] < x['d_other'] for x in rows)
    print('  every bitmap in the WHOLE book closer to its own class than to any other: %s'
          % allsep)
    json.dump(dict(conf=conf.tolist(), conf_bitmap=confb.tolist(),
                   crop_accuracy=float(ok)/tot,
                   bitmap_accuracy=float(np.trace(confb))/confb.sum(),
                   oae=oae, all_separated=bool(allsep), rows=rows),
              open(os.path.join(T.HERE, 'out_loo.json'), 'w'), indent=1)
    print('-> out_loo.json')


if __name__ == '__main__':
    main()
