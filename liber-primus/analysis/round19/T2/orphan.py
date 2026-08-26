"""Inventory the MID-SIZE mark class: ink that is neither a rune body nor a separator dot.

Height classes at 2400x3600 (frontB measured, T2 confirms):
    rune body      95 -132 px
    'mid'          35 - 94 px   <-- this class
    separator dot   4 - 34 px
Every one of T2's 26 indel flags and both substitution candidates sit on this class.
"""
import os, json, collections
import t2lib as T

lm = json.load(open(os.path.join(T.HERE, 'out_linemap.json')))['map']
adjset = {(a['gline'], a['pos']) for a in json.load(open(os.path.join(T.HERE, 'out_indel_adj.json')))}
flagged_lines = {a['gline'] for a in json.load(open(os.path.join(T.HERE, 'out_indel_adj.json')))}

rows = []
hist = collections.Counter()
per_line = collections.Counter()
for rec in lm:
    ink = T.page_ink(os.path.join(T.ROOT, rec['path']))
    sub = ink[max(0, rec['y0'] - 6):rec['y1'] + 6]
    n = 0
    for c in T.components(sub):
        xc = (c['x0'] + c['x1']) / 2
        if 35 <= c['h'] <= 94 and rec['x0'] - 40 < xc < rec['x1'] + 60:
            n += 1
            hist[(c['h'] // 10 * 10, c['w'] // 10 * 10)] += 1
            rows.append(dict(gline=rec['gline'], page=rec['num'], seg=rec['seg'],
                             h=c['h'], w=c['w'], x=c['x0'] + 0,
                             y=c['y0'] + max(0, rec['y0'] - 6)))
    per_line[rec['gline']] = n

tot = sum(per_line.values())
print('mid-size marks (35-94 px tall) inside text rows: %d over %d lines'
      % (tot, len(lm)))
print('lines carrying at least one: %d/%d'
      % (sum(1 for v in per_line.values() if v), len(lm)))
print('\n(height,width) decades:')
for k in sorted(hist, key=lambda k: -hist[k])[:12]:
    print('   h~%d w~%d : %d' % (k[0], k[1], hist[k]))

fl = [g for g in flagged_lines]
print('\nindel-flagged lines carrying a mid-size mark: %d/%d'
      % (sum(1 for g in fl if per_line.get(g, 0) > 0), len(fl)))
print('unflagged lines carrying a mid-size mark: %d/%d'
      % (sum(1 for g, v in per_line.items() if v > 0 and g not in flagged_lines),
         sum(1 for g in per_line if g not in flagged_lines)))
by_page = collections.Counter(r['page'] for r in rows)
print('\nper page:', dict(sorted(by_page.items())))
json.dump(dict(total=tot, marks=rows, per_line={str(k): v for k, v in per_line.items()}),
          open(os.path.join(T.HERE, 'out_orphan.json'), 'w'))
print('wrote out_orphan.json')
