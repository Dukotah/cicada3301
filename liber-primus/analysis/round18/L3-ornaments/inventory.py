"""L3 stage 1 -- rebuild the ornament-band inventory WITH y coordinates.

`geometry/ornaments.json` (62 rows) stores (page, x_lo, x_hi, n_components, median_height)
and drops the y coordinate, so the bands cannot be cropped from it.  This script re-runs the
exact row-grouping + ornament-rejection logic of `geometry/analyze.py` on `glyphs.npz`, and
the band logic of `analyze2.py` on `glyphs2.npz`, and emits the union with full bounding
boxes so every catalogued band can be cropped.

Output: inventory.json
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))      # liber-primus/
GEO = os.path.join(ROOT, 'analysis', 'geometry')


def jdef(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError(str(type(o)))


# ----------------------------------------------------------------- analyze.py path
d = np.load(os.path.join(GEO, 'glyphs.npz'))
page, x0, y0, x1, y1 = d['page'], d['x0'], d['y0'], d['x1'], d['y1']
H, W = y1 - y0, x1 - x0
SEP = H < 30


def page_rows(p):
    idx = np.where(page == p)[0]
    if not len(idx):
        return []
    big = idx[~SEP[idx]]
    if not len(big):
        return []
    order = big[np.argsort(y0[big])]
    rows, cur = [], [order[0]]
    for i in order[1:]:
        ytop = min(y0[j] for j in cur)
        ybot = max(y1[j] for j in cur)
        if y0[i] < ybot - 0.45 * (ybot - ytop):
            cur.append(i)
        else:
            rows.append(cur)
            cur = [i]
    rows.append(cur)
    out = []
    seps = idx[SEP[idx]]
    for r in rows:
        ytop = min(y0[j] for j in r)
        ybot = max(y1[j] for j in r)
        mine = [s for s in seps if ytop - 10 <= (y0[s] + y1[s]) / 2 <= ybot + 10]
        out.append((sorted(r, key=lambda j: x0[j]), sorted(mine, key=lambda j: x0[j])))
    return out


def merge_row(row):
    out = []
    for j in row:
        if out:
            g = out[-1]
            glo = min(x0[i] for i in g)
            ghi = max(x1[i] for i in g)
            ov = min(ghi, x1[j]) - max(glo, x0[j])
            if ov > 0.55 * min(ghi - glo, W[j]):
                g.append(j)
                continue
        out.append([j])
    return [tuple(g) for g in out]


def gbox(g):
    return (min(x0[i] for i in g), min(y0[i] for i in g),
            max(x1[i] for i in g), max(y1[i] for i in g))


rows_out = []
for p in range(56):
    rows = page_rows(p)
    if not rows:
        continue
    spans = [(min(x0[j] for j in r), max(x1[j] for j in r)) for r, _ in rows]
    med_lo, med_hi = np.median([s[0] for s in spans]), np.median([s[1] for s in spans])
    for r, seps in rows:
        g = merge_row(r)
        lo = min(gbox(q)[0] for q in g)
        hi = max(gbox(q)[2] for q in g)
        ylo = min(gbox(q)[1] for q in g)
        yhi = max(gbox(q)[3] for q in g)
        hs = [gbox(q)[3] - gbox(q)[1] for q in g]
        why = []
        if hi < med_lo - 50:
            why.append('left-of-column')
        if lo > med_hi + 50:
            why.append('right-of-column')
        if np.median(hs) > 240:
            why.append('tall')
        if why:
            rows_out.append(dict(src='analyze.py', page=int(p), x=[int(lo), int(hi)],
                                 y=[int(ylo), int(yhi)], n=len(g),
                                 medh=int(np.median(hs)), why=why,
                                 comps=[[int(v) for v in gbox(q)] for q in g]))

# ----------------------------------------------------------------- analyze2.py path
rep = json.load(open(os.path.join(GEO, 'geometry_report.json')))
for e in rep['ornaments']:
    rows_out.append(dict(src='analyze2.py', page=int(e['page']), x=[int(e['x'][0]), int(e['x'][1])],
                         y=[int(e['y'][0]), int(e['y'][1])], n=int(e['n']),
                         medh=int(e['medh']), why=['analyze2-skip'], comps=None))

# ----------------------------------------------------------------- dedupe / union
def key(r):
    return (r['page'], r['x'][0] // 8, r['x'][1] // 8, r['y'][0] // 8, r['y'][1] // 8)


seen, union = {}, []
for r in sorted(rows_out, key=lambda r: (r['page'], r['y'][0], r['x'][0])):
    k = key(r)
    if k in seen:
        seen[k]['src'] = seen[k]['src'] + '+' + r['src']
        if seen[k]['comps'] is None:
            seen[k]['comps'] = r['comps']
        continue
    seen[k] = dict(r)
    union.append(seen[k])

for i, r in enumerate(union):
    r['id'] = 'B%03d' % i
    r['w'] = r['x'][1] - r['x'][0]
    r['h'] = r['y'][1] - r['y'][0]

json.dump(union, open(os.path.join(HERE, 'inventory.json'), 'w'), indent=1, default=jdef)

short = [r for r in union if r['n'] <= 16]
print('analyze.py rows      : %d' % sum(1 for r in rows_out if r['src'] == 'analyze.py'))
print('analyze2.py rows     : %d' % sum(1 for r in rows_out if r['src'] == 'analyze2.py'))
print('union (deduped)      : %d bands across %d pages' % (len(union), len(set(r['page'] for r in union))))
print('short bands (n<=16)  : %d' % len(short))
print()
print('%-5s %-4s %-3s %-22s %-22s %-5s %-5s %s' % ('id', 'pg', 'n', 'x', 'y', 'w', 'h', 'why'))
for r in union:
    mark = '*' if r['n'] <= 16 else ' '
    print('%s%-5s %-4d %-3d %-22s %-22s %-5d %-5d %s' %
          (mark, r['id'], r['page'], r['n'], str(r['x']), str(r['y']), r['w'], r['h'],
           ','.join(r['why'])))
