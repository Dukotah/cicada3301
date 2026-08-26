"""Is canon's Y rune a TWO-component glyph whose inner stroke my height filter drops?"""
import numpy as np, collections, sys, os
import t1_align as A, t1_reader as T
sys.path.insert(0, os.path.join(T.LP,'src'))
from lp.gematria import IDX_TO_TRANS

r = A.run('LP2', verbose=False)
S, cpage = r['S'], r['cpage']
z = S.z

# rebuild, per page, the full component list and ask: for each ALIGNED crop, what
# non-rune-band components sit inside its x-span within its row's y-band?
import difflib
res = collections.defaultdict(collections.Counter)
hh = collections.defaultdict(list)
for p in [0, 1, 2, 3, 4, 5]:
    path = T.relikd_path(p)
    ink = T.page_ink(path)
    comps = T.components(ink)
    cands = T.rune_candidates(comps)
    rows = T.group_rows(cands)
    glyphs = []
    for ri, rr in enumerate(rows):
        for j in rr:
            g = dict(cands[j]); g['row'] = ri; glyphs.append(g)
    others = [c for c in comps if not (T.RUNE_H[0] <= c['h'] <= T.RUNE_H[1])]
    pred = list(r['pred'][S.idx_by_page[p]])
    m, f = A.align_page(pred, cpage[p])
    for a, b in m + f:
        g = glyphs[a]; lab = IDX_TO_TRANS[cpage[p][b]]
        inside = [c for c in others
                  if c['x0'] >= g['x0'] - 2 and c['x1'] <= g['x1'] + 2
                  and c['y0'] >= g['y0'] - 4 and c['y1'] <= g['y1'] + 4]
        res[lab][len(inside)] += 1
        for c in inside:
            hh[lab].append(c['h'])

print('rune : #glyphs with 0 / 1 / 2 inner components   (median inner height)')
for lab in sorted(res, key=lambda k: -sum(res[k].values())):
    c = res[lab]
    tot = sum(c.values())
    med = int(np.median(hh[lab])) if hh[lab] else -1
    print('%-3s n=%4d  ->  %s   inner-h med %d'
          % (lab, tot, dict(sorted(c.items())), med))
