"""Measure the separator mark classes before adjudicating anything.

Round 8's separator_audit counted EVERY component with h<30 as one 'dot'. The
sentence mark `.` is not a dot -- it is a LOZENGE of ~9px dots (visible at
74.jpg x=1140..1179, a 3-column x 4-5 row array, and it is exactly why L4's fitted
advance width for `.` is 1.82 against 0.32 for `-`). So a single `.` contributes
~12 components to that count, which is the mechanism that produced the 19
'disagreements' A-05/B-23 asks about.
"""
import os, json, collections
import numpy as np
import t2lib as T

lm = json.load(open(os.path.join(T.HERE, 'out_linemap.json')))['map']
canon = T.canon_lines()

def marks_of(rec):
    path = os.path.join(T.ROOT, rec['path'])
    ink = T.page_ink(path)
    y0, y1 = rec['y0'] - 10, rec['y1'] + 10
    sub = ink[max(0, y0):y1]
    out = []
    for c in T.components(sub):
        if 4 <= c['h'] <= 34 and 4 <= c['w'] <= 34:
            xc = (c['x0'] + c['x1']) / 2
            if rec['x0'] - 40 < xc < rec['x1'] + 80:
                out.append(dict(x0=c['x0'], x1=c['x1'], y0=c['y0'] + max(0, y0),
                                h=c['h'], w=c['w'], xc=xc))
    return sorted(out, key=lambda c: c['xc'])

def cluster(marks, gap=22):
    cl, cur = [], []
    for m in marks:
        if cur and m['xc'] - cur[-1]['xc'] > gap:
            cl.append(cur); cur = []
        cur.append(m)
    if cur:
        cl.append(cur)
    return cl

sizes = collections.Counter()
spans = collections.Counter()
tot_dash = tot_dot = 0
rows = []
for rec in lm:
    line = canon[rec['gline']]
    nd = sum(1 for t in line['tokens'] if t == ('s', '-'))
    ndot = sum(1 for t in line['tokens'] if t == ('s', '.'))
    cl = cluster(marks_of(rec))
    for c in cl:
        sizes[len(c)] += 1
        spans[min(int(c[-1]['x1'] - c[0]['x0']), 60)] += 1
    rows.append((rec['gline'], nd, ndot, len(cl), [len(c) for c in cl]))
    tot_dash += nd; tot_dot += ndot

print('canon total  "-" %d   "." %d   sum %d' % (tot_dash, tot_dot, tot_dash + tot_dot))
print('image clusters total %d' % sum(len(r[4]) for r in rows))
print('\ncluster SIZE (n components) histogram:')
for k in sorted(sizes):
    print('   %2d dots : %4d clusters' % (k, sizes[k]))
print('\ncluster X-SPAN histogram (px, capped 60):')
for k in sorted(spans):
    print('   %2d px : %4d' % (k, spans[k]))
