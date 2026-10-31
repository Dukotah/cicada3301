import os, sys, json
import numpy as np
import run as X
R = X.R; u8 = X.u8
mode = sys.argv[1]
P = R.M.parse(max_page=60)
PG = u8.pages(); r = np.random.default_rng(39002); rows = []
os.makedirs(os.path.join(X.HERE, 'oracle'), exist_ok=True)
for pi, words in enumerate(PG):
    if pi < 57:
        idx = [i for i, p in enumerate(P['w_page']) if p == pi]; lines = [P['w_line'][i] for i in idx]
    else:
        lines = [0] * len(words)   # koans text: no line structure -> whole-text shuffle (flagged)
    segs = u8.walk(words, X.VAR); s, g = R.score(segs, X.VAR); ns = X.nullset(words, lines, mode, 200, r)
    row = dict(page=pi, score=float(s), template=g, p5=float(np.quantile(ns, .05)), null_min=float(ns.min()), below_p5=bool(s < np.quantile(ns, .05)), below_min=bool(s < ns.min()))
    if row['below_min']: u8.save_png(segs, os.path.join(X.HERE, 'oracle', 'V2_%s_p%d.png' % (mode, pi)))
    rows.append(row)
summ = dict(variant=mode, n=len(rows), below_p5=sum(x['below_p5'] for x in rows), expected_by_chance=round(0.05 * len(rows), 1), below_null_min=sum(x['below_min'] for x in rows),
            label='variant-limited diagnostic (HUMAN-ORACLE.md), not a hit')
json.dump(dict(summary=summ, rows=rows), open(os.path.join(X.HERE, 'rescore_v2.json'), 'w'), indent=1); print(summ)
