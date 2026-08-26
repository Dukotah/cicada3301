"""Inventory of LARGE in-column components (candidate illuminated initials)."""
import os, json
import t2lib as T
from linemap import PAGE_TO_SEG, path_of
rows = []
for (src, num), seg in sorted(PAGE_TO_SEG.items(), key=lambda kv: kv[1]):
    p = path_of(src, num)
    ink = T.page_ink(p)
    big = [c for c in T.components(ink)
           if c['h'] > 140 and c['w'] > 40 and 330 < (c['x0']+c['x1'])/2 < 2070]
    if big:
        print('%s %-3s seg %-3s' % (src, num, seg),
              [(c['h'], c['w'], c['x0'], c['y0']) for c in big])
    rows.append((src, num, seg, len(big)))
print('pages with >=1 large in-column component: %d/%d'
      % (sum(1 for r in rows if r[3]), len(rows)))
