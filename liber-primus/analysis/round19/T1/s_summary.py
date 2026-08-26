"""Final accounting + provenance for the lane."""
import os, sys, json, collections
import numpy as np
import t1_reader as T, t1_run as R, t1_align as A
sys.path.insert(0, os.path.join(T.LP, 'src'))
from lp.gematria import IDX_TO_TRANS
TR = [IDX_TO_TRANS[i] for i in range(29)]

cor = json.load(open('out_corpus_lp2.json'))
z = np.load(os.path.join('work', 'corpus_lp2.npz'), allow_pickle=True)

# what are the 82 glyph-with-no-canon and 31 canon-with-no-glyph?
r, votes = R.build('LP2'); S = r['S']; bank = R.Bank(S, votes, r['blab'])
kinds = collections.Counter(); spur = []
for p in S.pages:
    canon = r['cpage'][p]
    full, small, lab = bank.view({p})
    seq, _ = R.read_page((T.relikd_path(p) if p <= 55 else
             T.vendor_path('%d.jpg' % (p + 17))), full, small, page=p,
             fast=bank.fastview({p}))
    if not canon:
        for o in seq: kinds['(page with no canon entry) ' + o['kind']] += 1
        continue
    rep, pairs, bad = R.align_report(seq, canon)
    used = set(i for i, j, ok in pairs)
    for i, o in enumerate(seq):
        if i not in used:
            kinds[o['kind']] += 1
            spur.append(dict(page=p, kind=o['kind'], x0=o['x0'], y0=o['y0'],
                             w=o['w'], h=o['h'], call=TR[o['lab']],
                             d0=round(float(o['d0']), 1) if o['d0'] is not None else None))
print('glyph-with-no-canon, by kind:', dict(kinds))
print('  by call:', collections.Counter(s['call'] for s in spur).most_common(8))
print('  d0 of these:', sorted(set(round(s["d0"]) for s in spur if s["d0"] is not None))[:12])

bad = np.where(z['canon'] != z['t1'])[0]
dis = [dict(page=int(z['page'][i]), cpos=int(z['cpos'][i]), kind=str(z['kind'][i]),
            canon=TR[z['canon'][i]], t1=TR[z['t1'][i]],
            d0=float(z['d0'][i]), d1=float(z['d1'][i]),
            x0=int(z['x0'][i]), y0=int(z['y0'][i])) for i in bad]

prov = {}
for p in [0, 45, 54, 55]:
    prov['relikd/p%d.jpg' % p] = T.sha256(T.relikd_path(p))
for n in ['73.jpg', '74.jpg', '17.jpg', '72.jpg']:
    prov['vendor/%s' % n] = T.sha256(T.vendor_path(n))

out = dict(corpus=dict(n_canon=cor['n_canon'], n_equal=cor['n_equal'],
                       agreement=cor['agreement'],
                       one_to_one_disagreements=len(dis),
                       canon_with_no_glyph=sum(x['missing'] for x in cor['pages']),
                       glyph_with_no_canon=sum(x['spurious'] for x in cor['pages'])),
           disagreements=dis,
           spurious_by_kind=dict(kinds), spurious=spur,
           provenance_sha256=prov)
json.dump(out, open('out_summary.json', 'w'), indent=1)
print('\n1:1 disagreements across the whole LP2 corpus: %d' % len(dis))
for d in dis: print('  ', d)
print('-> out_summary.json')
