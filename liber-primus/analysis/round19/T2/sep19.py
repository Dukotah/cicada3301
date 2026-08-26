"""A-05 / B-23 -- read and adjudicate THE 19 LINES, one by one.

The shortlist is `analysis/geometry/separator_audit.json.disagreements`, entries
[image_line, canon_line, image_dots - canon_separators]. canon_line indexes the same
604-line canon list this lane uses, so it is a gline.
"""
import os, json, collections
import t2lib as T
from lp.gematria import IDX_TO_TRANS

GEO = os.path.join(T.LP, 'analysis', 'geometry', 'separator_audit.json')
old = json.load(open(GEO))['disagreements']
sep = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, 'out_separators.json')))['rows']}
lm = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, 'out_linemap.json')))['map']}
canon = T.canon_lines()

print('A-05 / B-23 shortlist: %d lines\n' % len(old))
print('%-6s %-5s %-5s %-8s %-9s %-9s %s' %
      ('gline', 'page', 'seg', 'old_diff', 'canon', 'image(T2)', 'verdict'))
out = []
nres = collections.Counter()
for img_line, gl, diff in old:
    r = sep.get(gl)
    rec = lm.get(gl)
    if r is None:
        print('%-6s  -- not mapped' % gl)
        continue
    predicted = r['canon_dot'] * 12          # a '.' lozenge fragments into ~13 dots
    if r['canon_dash'] == r['img_dash'] and r['canon_dot'] == r['img_dot']:
        if r['canon_dot'] > 0:
            v = 'RESOLVED: old diff is the "." lozenge counted as ~%d dots' % (predicted + 1)
            k = 'lozenge'
        else:
            v = 'RESOLVED: counts agree; old diff was a line-alignment slip'
            k = 'alignment'
    elif not r['dis']:
        v = 'RESOLVED: positions agree'
        k = 'alignment'
    elif all(d['gap'] == 0 or d['gap'] >= len(canon[gl]['runes']) - 2 for d in r['dis']):
        v = 'RESOLVED: line-boundary attribution only (gap %s)' % \
            ','.join(str(d['gap']) for d in r['dis'])
        k = 'boundary'
    else:
        v = 'RESIDUAL: %s' % '; '.join('gap%d canon=%s image=%s'
                                       % (d['gap'], d['canon'], d['image']) for d in r['dis'])
        k = 'residual'
    nres[k] += 1
    print('%-6s %-5s %-5s %-8s -%d .%-6d -%d .%-6d %s'
          % (gl, r['page'], r['seg'], '%+d' % diff, r['canon_dash'], r['canon_dot'],
             r['img_dash'], r['img_dot'], v))
    out.append(dict(gline=gl, page=r['page'], seg=r['seg'], old_diff=diff,
                    canon_dash=r['canon_dash'], canon_dot=r['canon_dot'],
                    img_dash=r['img_dash'], img_dot=r['img_dot'],
                    dis=r['dis'], verdict=v, klass=k))
print('\nadjudication:', dict(nres))
json.dump(out, open(os.path.join(T.HERE, 'out_sep19.json'), 'w'), indent=1)
print('wrote out_sep19.json')
