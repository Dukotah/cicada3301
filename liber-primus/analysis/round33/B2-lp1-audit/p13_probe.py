import os, sys, json
sys.dont_write_bytecode = True
exec(open('p27_probe.py').read().split("r, votes = R.build('LP2')")[0])
r, votes = R.build('LP2'); S = r['S']; bank = R.Bank(S, votes, r['blab'])
pg = 13; full, small, lab = bank.view({pg}); fast = bank.fastview({pg})
seq, _ = R.read_page(T.relikd_path(pg), full, small, page=pg, fast=fast)
canon = r['cpage'][pg]; rep, pairs, bad = R.align_report(seq, canon)
print(rep)
for (i, j, ok) in pairs:
    if 92 <= j <= 100: o = seq[i]; print(j, TR[canon[j]], TR[o['lab']], ok, o['x0'], o['y0'], o['w'], o['d0'], o['d1'])
# what does the all-corpus bootstrap alignment say at the same glyph?
idx = S.idx_by_page[pg]; pred = r['pred'][idx]
m, f = A.align_page(list(pred), r['cpage'][pg])
cp = r['cpage'][pg]
for a, b in sorted(m + f, key=lambda t: t[1]):
    if 92 <= b <= 100: print('boot', b, TR[cp[b]], 'bitmap', int(S.ids[idx[a]]), 'pred', TR[int(pred[a])] if int(pred[a]) < 29 else '?', 'forced' if (a,b) in f else 'equal')
