"""Read all 58 LP2 pages with leave-one-page-out labelling and align each to canon.

Emits, for every canon rune position, this lane's call and its distance/margin, plus a
per-page opcode report.  This is the substrate for the density stratification, the
plant-and-recover controls, and the adjudication of the 450.
"""
import os, sys, json, collections
import numpy as np
import t1_reader as T, t1_run as R, t1_align as A
sys.path.insert(0, os.path.join(T.LP, 'src'))
from lp.gematria import IDX_TO_TRANS  # noqa: E402

OUT = os.path.join(T.HERE, 'out_corpus_lp2.json')
CACHE = os.path.join(T.HERE, 'work', 'corpus_lp2.npz')


def page_path(p):
    return T.relikd_path(p) if p <= 55 else T.vendor_path('%d.jpg' % (p + 17))


def main():
    r, votes = R.build('LP2')
    S = r['S']
    bank = R.Bank(S, votes, r['blab'])
    rows, recs = [], []
    conf = np.zeros((29, 29), int)
    for p in S.pages:
        full, small, lab = bank.view({p})
        fast = bank.fastview({p})
        seq, allrec = R.read_page(page_path(p), full, small, page=p, fast=fast)
        canon = r['cpage'][p]
        if not canon:
            rows.append(dict(page=p, canon=0, emitted=len(seq), correct=0,
                             wrong=0, missing=0, spurious=len(seq)))
            print('  p%-2d  (no canon entry)  emitted %d' % (p, len(seq)), flush=True)
            continue
        rep, pairs, bad = R.align_report(seq, canon)
        for (i, j, ok) in pairs:
            conf[canon[j], seq[i]['lab']] += 1
            o = seq[i]
            recs.append(dict(page=p, cpos=int(j), spos=int(i), row=int(o['row']),
                             x0=int(o['x0']), y0=int(o['y0']), w=int(o['w']),
                             kind=o['kind'], canon=int(canon[j]), t1=int(o['lab']),
                             d0=float(o['d0']) if o['d0'] is not None else None,
                             d1=(float(o['d1']) if o['d1'] is not None
                                 and np.isfinite(o['d1']) else None)))
        rows.append(dict(page=p, canon=rep['n_canon'], emitted=rep['n_seq'],
                         correct=rep['equal'], wrong=rep['replace'],
                         missing=rep['insert'], spurious=rep['delete'],
                         accuracy=100.0 * rep['equal'] / rep['n_canon']))
        print('  p%-2d canon %4d emitted %4d correct %4d wrong %2d missing %2d spurious %2d'
              '  ACC %.4f%%' % (p, rep['n_canon'], rep['n_seq'], rep['equal'],
                                rep['replace'], rep['insert'], rep['delete'],
                                100.0 * rep['equal'] / rep['n_canon']), flush=True)
    tc = sum(x['canon'] for x in rows); tk = sum(x['correct'] for x in rows)
    print('\nLP2 corpus: %d/%d = %.4f%% of canon positions read identically'
          % (tk, tc, 100.0 * tk / tc))
    print('  1:1 disagreements %d   canon-with-no-glyph %d   glyph-with-no-canon %d'
          % (sum(x['wrong'] for x in rows), sum(x['missing'] for x in rows),
             sum(x['spurious'] for x in rows)))
    json.dump(dict(pages=rows, conf=conf.tolist(), n_canon=tc, n_equal=tk,
                   agreement=100.0 * tk / tc), open(OUT, 'w'), indent=1)
    np.savez_compressed(CACHE, **{k: np.array([x[k] if x[k] is not None else -1
                                               for x in recs])
                                  for k in ['page', 'cpos', 'spos', 'row', 'x0', 'y0',
                                            'w', 'canon', 't1', 'd0', 'd1']},
                        kind=np.array([x['kind'] for x in recs]))
    print('-> %s  and  %s (%d aligned positions)' % (OUT, CACHE, len(recs)))


if __name__ == '__main__':
    main()
