"""T2 -- A-05 / B-23.  Adjudicate the separators POSITIONALLY, all 604 lines.

Round 8's separator_audit compared COUNTS on 170 of 604 lines and left 19
disagreements unread.  Two things are different here:

 1. The mark classes are measured, not assumed (sepmeasure.py).  A `-` is ONE dot
    spanning 9-10 px; a `.` is a LOZENGE spanning 24-60 px which fragments into
    3/4/10/13/23 components depending on JPEG merging.  The old audit counted every
    h<30 component as one dot, so every `.` contributed ~13 to its total.  That is
    the mechanism, and it predicts the SIGN and rough SIZE of the old diffs.

 2. Separators are placed in GAPS between forced-aligned rune slots, so a
    disagreement is localised to a gap instead of being a per-line count.

CONTROL: canon segments 55/56 are LP2 pages proven correct by DECRYPTION.
"""
import os, json, collections
import numpy as np
import t2lib as T
from lp.gematria import IDX_TO_TRANS

SPAN_DOT = 15          # cluster x-span below this = '-', above = '.'

lm = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, 'out_linemap.json')))['map']}
probe = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, 'out_probe.json')))
         if 'fail' not in r}
canon = T.canon_lines()
tmpl = T.load_templates()


def marks_of(rec):
    ink = T.page_ink(os.path.join(T.ROOT, rec['path']))
    y0 = max(0, rec['y0'] - 10)
    sub = ink[y0:rec['y1'] + 10]
    out = []
    for c in T.components(sub):
        if 4 <= c['h'] <= 34 and 4 <= c['w'] <= 34:
            xc = (c['x0'] + c['x1']) / 2
            if rec['x0'] - 40 < xc < rec['x1'] + 80:
                out.append(dict(x0=c['x0'], x1=c['x1'], xc=xc))
    return sorted(out, key=lambda c: c['xc'])


def cluster(marks, gap=22):
    cl, cur = [], []
    for m in marks:
        if cur and m['xc'] - cur[-1]['xc'] > gap:
            cl.append(cur); cur = []
        cur.append(m)
    if cur:
        cl.append(cur)
    return [dict(kind=('-' if (c[-1]['x1'] - c[0]['x0']) < SPAN_DOT else '.'),
                 xc=(c[0]['x0'] + c[-1]['x1']) / 2, n=len(c),
                 span=int(c[-1]['x1'] - c[0]['x0'])) for c in cl]


def canon_gaps(line):
    """gap index (0..nrune) -> list of separator kinds canon puts there"""
    g = collections.defaultdict(list)
    k = 0
    for t in line['tokens']:
        if t[0] == 'r':
            k += 1
        else:
            g[k].append(t[1])
    return g


rows = []
tot = collections.Counter()
for gl, rec in sorted(lm.items()):
    line = canon[gl]
    r = probe.get(gl)
    if r is None:
        continue
    off = r.get('skip0', 0)
    xs = [None] * off + list(r['x'])
    ws = [tmpl[c].shape[1] for c in line['runes']]
    cl = cluster(marks_of(rec))
    cg = canon_gaps(line)
    # assign each image cluster to a gap index by x
    img = collections.defaultdict(list)
    for c in cl:
        gi = 0
        for j in range(len(line['runes'])):
            if xs[j] is None:
                continue
            if c['xc'] > xs[j] + ws[j] * 0.5:
                gi = j + 1
        img[gi].append(c['kind'])
    keys = set(cg) | set(img)
    dis = []
    for k in sorted(keys):
        a = sorted(cg.get(k, []))
        b = sorted(img.get(k, []))
        if a != b:
            dis.append(dict(gap=k, canon=''.join(a) or '-none-', image=''.join(b) or '-none-'))
    nd_c = sum(1 for t in line['tokens'] if t == ('s', '-'))
    nt_c = sum(1 for t in line['tokens'] if t == ('s', '.'))
    nd_i = sum(1 for c in cl if c['kind'] == '-')
    nt_i = sum(1 for c in cl if c['kind'] == '.')
    tot['canon_dash'] += nd_c; tot['canon_dot'] += nt_c
    tot['img_dash'] += nd_i; tot['img_dot'] += nt_i
    tot['lines'] += 1
    if nd_c == nd_i and nt_c == nt_i:
        tot['count_exact'] += 1
    if not dis:
        tot['pos_exact'] += 1
    rows.append(dict(gline=gl, seg=rec['seg'], page=rec['num'],
                     canon_dash=nd_c, canon_dot=nt_c, img_dash=nd_i, img_dot=nt_i,
                     dis=dis))

print('lines %d' % tot['lines'])
print('canon  -: %-5d  .: %-4d      image  -: %-5d  .: %-4d'
      % (tot['canon_dash'], tot['canon_dot'], tot['img_dash'], tot['img_dot']))
print('lines with EXACT separator counts   : %d/%d (%.2f%%)'
      % (tot['count_exact'], tot['lines'], 100.0 * tot['count_exact'] / tot['lines']))
print('lines with EXACT separator POSITIONS: %d/%d (%.2f%%)'
      % (tot['pos_exact'], tot['lines'], 100.0 * tot['pos_exact'] / tot['lines']))

sol = [r for r in rows if r['seg'] in (55, 56)]
print('\nCONTROL (segments 55/56, proven by decryption): %d lines, '
      'positionally exact %d/%d' % (len(sol), sum(1 for r in sol if not r['dis']), len(sol)))

print('\n--- every line with a positional separator disagreement ---')
for r in rows:
    if r['dis']:
        print('  gline %-4s page %-3s seg %-3s  canon -%d .%d | image -%d .%d   %s'
              % (r['gline'], r['page'], r['seg'], r['canon_dash'], r['canon_dot'],
                 r['img_dash'], r['img_dot'],
                 '; '.join('gap%d canon=%s image=%s' % (d['gap'], d['canon'], d['image'])
                           for d in r['dis'])))

json.dump(dict(totals=dict(tot), rows=rows),
          open(os.path.join(T.HERE, 'out_separators.json'), 'w'), indent=1)
print('\nwrote out_separators.json')
