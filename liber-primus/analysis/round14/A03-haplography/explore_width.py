"""A-03 exploration: is the LP render metrically deterministic?

If the book is a digital font render (Round 8 GEOMETRY: median NN Hamming 0.0000),
then a line's inked horizontal extent should be an exact linear function of the
tokens on it.  Fit  width ~= sum_t n_t * adv_t  over SOLVED pages and inspect the
residual scale in pixels.  A haplographic merge (canon records 1 rune where 2 are
inked) makes the measured width exceed the canon-predicted width by ~one advance.
"""
import os, sys, json, collections
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
GEO = os.path.join(ROOT, 'analysis', 'geometry')
IMG = os.path.join(ROOT, 'data', 'relikd')

bands = np.load(os.path.join(GEO, 'glyphs2.npz'))['bands']
txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
segs = txt.split('%')

# canon lines per page (tokens kept: runes + '-' + '.')
KEEP = set('ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ') | set('-.')
canon_pages = {}
for p, s in enumerate(segs):
    ls = []
    for ln in s.split('/'):
        toks = [c for c in ln if c in KEEP]
        if toks:
            ls.append(toks)
    canon_pages[p] = ls

# measured ink extents per band
meas = []
cur, ink = -1, None
for bi, (p, ys, ye, ng, medh) in enumerate(bands):
    p = int(p)
    if p != cur:
        a = np.asarray(Image.open(os.path.join(IMG, 'p%d.jpg' % p)).convert('L'))
        ink = (a < 128)
        cur = p
    band = ink[ys:ye]
    cols = np.where(band.sum(0) > 0)[0]
    if len(cols) == 0:
        meas.append((p, bi, ys, ye, 0, 0, 0, 0))
        continue
    meas.append((p, bi, int(ys), int(ye), int(cols[0]), int(cols[-1]) + 1,
                 int(cols[-1]) + 1 - int(cols[0]), int(band.sum())))

print('bands measured:', len(meas))
byp = collections.defaultdict(list)
for m in meas:
    byp[m[0]].append(m)

# pages where band count == canon line count -> unambiguous 1:1 alignment
exact_pages = [p for p in range(55)
               if len(byp.get(p, [])) == len(canon_pages.get(p, []))]
print('pages with band-count == canon-line-count:', len(exact_pages), exact_pages)

rows = []
for p in exact_pages:
    for m, toks in zip(byp[p], canon_pages[p]):
        rows.append((p, m[1], m[6], m[7], toks))

TOK = sorted(KEEP)
ti = {t: i for i, t in enumerate(TOK)}
X = np.zeros((len(rows), len(TOK)))
y = np.array([r[2] for r in rows], float)
for i, r in enumerate(rows):
    for t in r[4]:
        X[i, ti[t]] += 1
# advance model: width = sum n_t*adv_t - (one inter-glyph gap)  -> add intercept
X1 = np.hstack([X, np.ones((len(rows), 1))])
coef, *_ = np.linalg.lstsq(X1, y, rcond=None)
pred = X1 @ coef
res = y - pred
print('lines in fit:', len(rows))
print('residual px: mean %.2f  sd %.2f  median %.2f  p95 %.1f  max %.1f'
      % (res.mean(), res.std(), np.median(res), np.percentile(np.abs(res), 95),
         np.abs(res).max()))
print('advances:', {t: round(coef[ti[t]], 1) for t in TOK})
print('intercept %.1f' % coef[-1])
json.dump(dict(residual_sd=float(res.std()),
               advances={t: float(coef[ti[t]]) for t in TOK},
               intercept=float(coef[-1]),
               n_lines=len(rows)),
          open(os.path.join(HERE, 'explore_width.json'), 'w'), indent=1)
