import os, json, numpy as np
os.environ['D2'] = '1'
import recognizer as R
from PIL import Image
u8 = R.u8; PG = u8.pages(); r = np.random.default_rng(4040); rows = []
os.makedirs('oracle', exist_ok=True)
for v in u8.VARIANTS:
    for pi, words in enumerate(PG):
        segs = u8.walk(words, v); s, g = R.score(segs, v)
        ns = R.null_for(words, v, 200, r, pi if pi < 57 else -1)
        row = dict(var=v, page=pi, score=float(s), template=g, p5=float(np.quantile(ns, .05)), null_min=float(ns.min()), null_med=float(np.median(ns)),
                   below_p5=bool(s < np.quantile(ns, .05)), below_min=bool(s < ns.min()))
        if row['below_min']: u8.save_png(segs, f'oracle/{v}_p{pi}.png')
        rows.append(row)
    print(v, sum(x['below_p5'] for x in rows if x['var'] == v), flush=True)
summ = {v: dict(n=58, below_p5=sum(x['below_p5'] for x in rows if x['var'] == v), expected_by_chance=2.9, below_null_min=sum(x['below_min'] for x in rows if x['var'] == v)) for v in u8.VARIANTS}
json.dump(dict(summary=summ, rows=rows), open('rescore_u8.json', 'w'), indent=1); print(summ)
