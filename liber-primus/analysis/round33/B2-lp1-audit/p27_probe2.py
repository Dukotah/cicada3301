import os, sys, json
sys.dont_write_bytecode = True
exec(open('p27_probe.py').read().split("r, votes = R.build('LP2')")[0])
r, votes = R.build('LP2'); S = r['S']; bank = R.Bank(S, votes, r['blab'])
z, mask = E_.load('LP2')
ks = [int(k) for k in range(S.n) if int(S.ids[k]) == 421]
print('bitmap 421 crops', [(int(z['page'][k]), int(z['x0'][k]), int(z['y0'][k]), int(z['row'][k]), int(z['pos'][k])) for k in ks])
out = []
for k in ks:
    pg = int(z['page'][k])
    full, small, lab = bank.view({pg}); fast = bank.fastview({pg})
    seq, _ = R.read_page(T.relikd_path(pg) if pg <= 55 else T.vendor_path('%d.jpg' % (pg + 17)), full, small, page=pg, fast=fast)
    canon = r['cpage'][pg]
    rep, pairs, bad = R.align_report(seq, canon)
    for (i, j, ok) in pairs:
        o = seq[i]
        if abs(o['x0'] - int(z['x0'][k])) <= 2 and abs(o['y0'] - int(z['y0'][k])) <= 2:
            ctxs = ''.join(TR[canon[q]] + ' ' for q in range(max(0, j - 5), min(len(canon), j + 6)))
            print('page', pg, 'cpos', j, 'canon', TR[canon[j]], 't1', TR[o['lab']], 'ok', ok, 'd0', o['d0'], 'd1', o['d1'], 'ctx', ctxs)
            out.append(dict(page=pg, cpos=j, canon=TR[canon[j]], t1=TR[o['lab']], ok=bool(ok), x0=int(o['x0']), y0=int(o['y0']), w=int(o['w']), d0=float(o['d0']), d1=float(o['d1']), ctx=ctxs.strip()))
json.dump(out, open('_p27_b421.json', 'w'), indent=1)
# bank info: label of bitmap 421 in the full-corpus labelling
print('blab[421] =', TR[r['blab'][421]], '; blab[282] =', TR[r['blab'][282]], '; blab[586] =', r['blab'].get(586))
# U vs B exemplars: pixel overlap between 421 and 282 and 586
import numpy as np
a, b, c = S.bitmap(421), S.bitmap(282), S.bitmap(586)
print('shapes', a.shape, b.shape, c.shape)
