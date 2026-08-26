"""GATE G-READ (PREREG section 3).  Per-rune accuracy on the solved control pages.

Ground truth is canon's rune stream for a page whose plaintext is known BY DECRYPTION:
  * 73.jpg = LP2 p56  "AN END"   -- phi(prime) shift down forward gematria
  * 74.jpg = LP2 p57  "PARABLE"  -- direct substitution: its runes are fixed by the
                                    documented English text, an external fact
Every glyph on these pages is classified with the control page REMOVED from the label
consensus (leave-one-page-out), so no glyph is judged using its own page.

Reports: raw counts, 29-class confusion matrix, per-class recall, the LP2/LP1 split, the
density stratification, and the O/A/AE pairwise rates (gate G-OAE).
"""
import os, sys, json, collections
import numpy as np
import t1_reader as T, t1_run as R, t1_align as A
sys.path.insert(0, os.path.join(T.LP, 'src'))
from lp.gematria import IDX_TO_TRANS  # noqa: E402

NC = 29
TR = [IDX_TO_TRANS[i] for i in range(NC)]
CONTROL_LP2 = [(56, '73.jpg', 'AN END'), (57, '74.jpg', 'PARABLE')]


def measure(pages, r, bank, S, tag):
    conf = np.zeros((NC, NC), int)
    ins = dele = 0
    per = []
    margins = []
    for (p, name, title) in pages:
        full, small, lab = bank.view({p})
        path = T.vendor_path(name) if name else T.relikd_path(p)
        seq, allrec = R.read_page(path, full, small, page=p, fast=bank.fastview({p}))
        canon = r['cpage'][p]
        rep, pairs, bad = R.align_report(seq, canon)
        for (i, j, ok) in pairs:
            conf[canon[j], seq[i]['lab']] += 1
            if np.isfinite(seq[i].get('d1', np.nan)):
                margins.append((seq[i]['d1'] - seq[i]['d0'], canon[j] == seq[i]['lab']))
        ins += rep['insert']; dele += rep['delete']
        acc = 100.0 * rep['equal'] / rep['n_canon']
        per.append(dict(page=p, image=name, title=title, canon=rep['n_canon'],
                        emitted=rep['n_seq'], correct=rep['equal'],
                        wrong_1to1=rep['replace'], missing=rep['insert'],
                        spurious=rep['delete'], accuracy=acc,
                        errors=[dict(pos=int(j), canon=TR[canon[j]],
                                     read=TR[seq[i]['lab']] if i < len(seq) else None)
                                for (i, j) in bad]))
        print('  %-8s %-10s canon %4d  emitted %4d  correct %4d  wrong %2d  missing %2d'
              '  spurious %2d   ACC %.4f%%'
              % (name or 'p%d' % p, title, rep['n_canon'], rep['n_seq'], rep['equal'],
                 rep['replace'], rep['insert'], rep['delete'], acc))
    tot_c = sum(x['canon'] for x in per); tot_ok = sum(x['correct'] for x in per)
    print('  %s POOLED: %d/%d = %.4f%%  (%d wrong 1:1, %d missing, %d spurious)'
          % (tag, tot_ok, tot_c, 100.0 * tot_ok / tot_c,
             sum(x['wrong_1to1'] for x in per), ins, dele))
    return dict(rows=per, conf=conf.tolist(), n_canon=tot_c, n_correct=tot_ok,
                accuracy=100.0 * tot_ok / tot_c, missing=ins, spurious=dele), conf, margins


def oae_block(conf, tag):
    idx = {t: TR.index(t) for t in ['O', 'A', 'AE']}
    print('\n  %s O/A/AE block (rows = canon, cols = T1):' % tag)
    print('        ' + ''.join('%8s' % t for t in ['O', 'A', 'AE']) + '%10s' % 'recall')
    out = {}
    for a in ['O', 'A', 'AE']:
        row = conf[idx[a]]
        n = row.sum()
        print('   %-4s' % a + ''.join('%8d' % row[idx[b]] for b in ['O', 'A', 'AE'])
              + '%10s' % ('%.4f%%' % (100.0 * row[idx[a]] / n) if n else 'n/a'))
        for b in ['O', 'A', 'AE']:
            if a != b:
                out['%s->%s' % (a, b)] = dict(n=int(row[idx[b]]), of=int(n),
                                              rate=float(row[idx[b]]) / n if n else None)
        out['recall_%s' % a] = dict(n=int(row[idx[a]]), of=int(n),
                                    rate=float(row[idx[a]]) / n if n else None)
    return out


if __name__ == '__main__':
    r, votes = R.build('LP2')
    S = r['S']
    bank = R.Bank(S, votes, r['blab'])
    print('\n=== G-READ-LP2 : the two solved LP2-typeface control pages')
    lp2, confL2, margins = measure(CONTROL_LP2, r, bank, S, 'LP2')
    oae2 = oae_block(confL2, 'LP2 control')

    print('\n=== per-class recall (LP2 control)')
    for i in range(NC):
        n = confL2[i].sum()
        if n:
            print('   %-3s n=%3d recall %.4f%%  %s' % (TR[i], n, 100.0*confL2[i][i]/n,
                  '' if confL2[i][i] == n else
                  'MISCALLS: ' + str({TR[j]: int(confL2[i][j]) for j in range(NC)
                                      if j != i and confL2[i][j]})))
    json.dump(dict(lp2=lp2, oae_lp2=oae2,
                   margins=[[float(m), bool(ok)] for m, ok in margins]),
              open(os.path.join(T.HERE, 'out_gread_lp2.json'), 'w'), indent=1)
    print('\nwrote out_gread_lp2.json')
