"""T2 control C2' -- the INK-SPLICE PLANT (PREREG section 2, C2').

C1 shows the probe reproduces decryption-proven runes.  C2' shows the probe is not
inert: take the REAL page ink, physically overwrite one slot's pixels with a
DIFFERENT rune's glyph, run the probe with UNCORRUPTED canon tokens, and ask whether
the probe reports the spliced rune.  This is the control round12/frontB never ran,
and it runs on the dense pages themselves.

  detection = probe's argmin at the spliced slot != canon    (an error is noticed)
  recovery  = probe's argmin at the spliced slot == spliced   (the truth is read)

Splice runes are drawn only from those that FIT the erased span (slot width + the
gap to the next glyph), so the plant never damages a neighbour.  The fraction of
(slot, rune) pairs excluded by that constraint is reported -- it is a coverage
statement, not a hidden filter.

usage: python3 splice.py [n_per_stratum]
"""
import os, sys, json, collections
import numpy as np
import t2lib as T
from probe import band_of
from lp.gematria import IDX_TO_TRANS

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
rng = np.random.default_rng(3301)

res = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, 'out_probe.json')))
       if 'fail' not in r}
lm = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, 'out_linemap.json')))['map']}
canon = T.canon_lines()
tmpl = T.load_templates()

def stratum(seg):
    if seg in (55, 56): return 'solved-LP2'
    if 45 <= seg <= 54: return 'dense-45-54'
    return 'pages-0-44'

pool = collections.defaultdict(list)
for g, r in res.items():
    for j in range(len(r['canon'])):
        pool[stratum(r['seg'])].append((g, j))

out = []
excluded_pairs = 0
total_pairs = 0
for s in ('solved-LP2', 'dense-45-54', 'pages-0-44'):
    cand = pool[s]
    pick = rng.choice(len(cand), size=min(N, len(cand)), replace=False)
    # group by line so each band is built once
    byline = collections.defaultdict(list)
    for i in pick:
        g, j = cand[i]
        byline[g].append(j)
    done = 0
    for g, slots in byline.items():
        r = res[g]
        rec = lm[g]
        band0, bx, by = band_of(rec)
        W = band0.shape[1]
        keys = list(r['canon'])
        for j in slots:
            x = r['x'][j] - bx
            wc = tmpl[keys[j]].shape[1]
            nxt = (r['x'][j + 1] - bx) if j + 1 < len(keys) else W
            avail = max(wc, nxt - x)
            fit = [q for q in range(29) if q != keys[j] and tmpl[q].shape[1] <= avail]
            total_pairs += 28
            excluded_pairs += 28 - len(fit)
            if not fit:
                continue
            q = int(rng.choice(fit))
            band = band0.copy()
            band[:, x:min(W, x + avail)] = 0.0
            Tq = tmpl[q]
            th, tw = Tq.shape
            top = (band.shape[0] - th) // 2
            if top < 0 or x + tw > W:
                continue
            band[top:top + th, x:x + tw] = np.maximum(band[top:top + th, x:x + tw], Tq)
            cc = T.cost_curves(band, tmpl)
            if any(k not in cc for k in keys):
                continue
            skip = band.sum(0) * T.SKIP_A + T.SKIP_B
            _, _, _, table, _ = T.loo_probe(band, keys, cc, skip, list(range(29)))
            b = int(table[j].argmin())
            out.append(dict(stratum=s, gline=g, slot=j, canon=keys[j], spliced=q,
                            probe=b, detect=int(b != keys[j]), recover=int(b == q)))
            done += 1
    print('%s: %d splices' % (s, done), flush=True)

agg = collections.defaultdict(lambda: dict(n=0, det=0, rec=0))
for o in out:
    a = agg[o['stratum']]
    a['n'] += 1; a['det'] += o['detect']; a['rec'] += o['recover']
print('\n=== C2prime  ink-splice plant recall ===')
for s in sorted(agg):
    a = agg[s]
    print('%-12s n %4d   detection %.4f   recovery %.4f'
          % (s, a['n'], a['det'] / a['n'], a['rec'] / a['n']))
print('\n(slot,rune) pairs excluded because the splice would not fit the erased span: '
      '%d/%d = %.1f%%' % (excluded_pairs, total_pairs, 100.0 * excluded_pairs / max(total_pairs, 1)))
cm = collections.Counter((IDX_TO_TRANS[o['spliced']], IDX_TO_TRANS[o['probe']])
                         for o in out if not o['recover'])
print('misses (spliced -> probe):', cm.most_common(15))
json.dump(dict(n_per_stratum=N, results=out,
               agg={k: v for k, v in agg.items()},
               excluded_pairs=excluded_pairs, total_pairs=total_pairs),
          open(os.path.join(T.HERE, 'out_splice.json'), 'w'), indent=1)
print('wrote out_splice.json')
