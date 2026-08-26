"""L3 -- H1 strengthened: quadgram-score every short band's read against a size-matched null.

The word-list form of H1 can only see strings it was told about.  This scores each short
band's transliteration with the repo's own English quadgram model () and compares
it to a null of same-length strings drawn from the LP2 rune frequency distribution.  Bar is
the campaign's own: , never a fixed
-5.5.
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R
sys.path.insert(0, os.path.join(R.LP, 'src'))
from lp import score as _score
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS

sc = _score.default()
bands = json.load(open(os.path.join(HERE, 'bands.json')))
txt = open(os.path.join(R.LP, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
flat = np.array([RUNE_TO_IDX[c] for c in txt if c in RUNE_TO_IDX])
freq = np.bincount(flat, minlength=29) / len(flat)
rng = np.random.default_rng(3301)

short = [b for b in bands if b['n_reported'] <= 16 and b['n_glyphs_read'] >= 8]
out = []
print('%-6s %-4s %-4s %-11s %8s %8s %8s %8s' % ('id','pg','n','call','score','nullmu','nullmax','z'))
for b in short:
    s = b['translit']
    v = sc.score_norm(s)
    n = len(b['runes'])
    null = np.array([sc.score_norm(''.join(IDX_TO_TRANS[i] for i in rng.choice(29, n, p=freq)))
                     for _ in range(2000)])
    z = (v - null.mean()) / null.std()
    out.append(dict(id=b['id'], page=b['page'], n=n, call=b['call'], score=round(v,3),
                    null_mean=round(float(null.mean()),3), null_sd=round(float(null.std()),3),
                    null_max=round(float(null.max()),3), z=round(float(z),2),
                    beats_null_max=bool(v > null.max()), translit=s))
    print('%-6s %-4d %-4d %-11s %8.3f %8.3f %8.3f %8.2f' % (b['id'], b['page'], n, b['call'], v, null.mean(), null.max(), z))
best = max(out, key=lambda o: o['score']) if out else None
nb = sum(1 for o in out if o['beats_null_max'])
print()
print('short bands scored: %d | beating their own null MAX: %d' % (len(out), nb))
if best: print('best: %s p%d %.3f (null max %.3f, z=%.2f) %r' % (best['id'],best['page'],best['score'],best['null_max'],best['z'],best['translit'][:40]))
json.dump(dict(bands=out, n=len(out), n_beating_null_max=nb,
               bar='band score must exceed its own size-matched null MAX over 2000 draws',
               verdict='PASS' if nb else 'FAIL'),
          open(os.path.join(HERE,'h1score.json'),'w'), indent=1)
