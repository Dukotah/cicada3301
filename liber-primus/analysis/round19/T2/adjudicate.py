"""T2 -- adjudicate every probe disagreement into SEG / ID / CONF (PREREG section 4).

SEG  : the line's rune-component count disagrees with canon, or the flagged slot sits
       in a run of >=2 adjacent flagged slots  -> the alignment slipped, the slot is
       not evidence about rune identity.
ID   : isolated slot, count-exact line, delta > tau.
CONF : an ID case whose (probe, canon) pair is a known shape-confusable family.

Only ID-and-not-CONF is a candidate canon error.  Writes out_a01.json.
"""
import os, json, collections
import numpy as np
import t2lib as T
from lp.gematria import IDX_TO_TRANS

TAU = 0.0   # fixed by C3: 0/178 solved-page slots have delta > 0

CONF_FAMILIES = [{1, 26}, {3, 24, 25}, {20, 7}, {5, 10}]
def is_conf(a, b):
    return any(a in f and b in f for f in CONF_FAMILIES)

def stratum(seg):
    if seg in (55, 56): return 'solved-LP2'
    if 45 <= seg <= 54: return 'dense-45-54'
    return 'pages-0-44'

res = json.load(open(os.path.join(T.HERE, 'out_probe.json')))
lm = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, 'out_linemap.json')))['map']}
canon = T.canon_lines()

flags, per_page = [], collections.defaultdict(lambda: dict(slots=0, flag=0, seg=0, idd=0, conf=0))
n_slots = n_lines = 0
skipped_initial = 0
fails = collections.Counter()
resid_all = []

for rec in res:
    if 'fail' in rec:
        fails[rec['fail']] += 1
        continue
    n_lines += 1
    skipped_initial += rec.get('skip0', 0)
    ce = (rec['ncomp'] + rec.get('skip0', 0)) == rec['nrune']
    resid_all.append(rec['total'] / max(len(rec['canon']), 1))
    off = rec.get('skip0', 0)
    loc = []
    for j, c in enumerate(rec['canon']):
        n_slots += 1
        d = rec['canon_cost'][j] - rec['best_cost'][j]
        if d > TAU:
            loc.append(j)
    pp = per_page[rec['num']]
    pp['slots'] += len(rec['canon'])
    for j in loc:
        run = (j - 1 in loc) or (j + 1 in loc)
        cls = 'SEG' if (not ce or run) else ('CONF' if is_conf(rec['best'][j], rec['canon'][j]) else 'ID')
        pp['flag'] += 1; pp[{'SEG':'seg','ID':'idd','CONF':'conf'}[cls]] += 1
        flags.append(dict(gline=rec['gline'], seg=rec['seg'], page=rec['num'],
                          src=rec['src'], slot=j + off, x=rec['x'][j],
                          canon=IDX_TO_TRANS[rec['canon'][j]],
                          probe=IDX_TO_TRANS[rec['best'][j]],
                          canon_i=rec['canon'][j], probe_i=rec['best'][j],
                          delta=round(rec['canon_cost'][j] - rec['best_cost'][j], 1),
                          margin=round(rec['second_cost'][j] - rec['best_cost'][j], 1),
                          line_resid=round(rec['total'] / max(len(rec['canon']), 1), 1),
                          count_exact=bool(ce), run=bool(run), cls=cls,
                          stratum=stratum(rec['seg'])))

print('lines probed %d   slots adjudicated %d   canon runes %d'
      % (n_lines, n_slots, sum(len(c['runes']) for c in canon)))
print('slots excluded as illuminated initial: %d' % skipped_initial)
if fails: print('line failures:', dict(fails))
print('median line residual/token %.1f   p95 %.1f'
      % (np.median(resid_all), np.quantile(resid_all, .95)))

by = collections.Counter((f['stratum'], f['cls']) for f in flags)
print('\nflags at tau=%.1f  (total %d)' % (TAU, len(flags)))
for s in ('solved-LP2', 'pages-0-44', 'dense-45-54'):
    tot = sum(1 for r in res if 'fail' not in r and stratum(r['seg']) == s for _ in r['canon'])
    print('  %-12s slots %6d  SEG %3d  CONF %3d  ID %3d'
          % (s, tot, by[(s, 'SEG')], by[(s, 'CONF')], by[(s, 'ID')]))

print('\n--- every ID (candidate canon error) ---')
for f in sorted(flags, key=lambda f: -f['delta']):
    if f['cls'] == 'ID':
        print('  page %-3s seg %-3s gline %-4s slot %-3s x=%-5s canon %-3s probe %-3s '
              'delta %-9s margin %-9s line_resid %s'
              % (f['page'], f['seg'], f['gline'], f['slot'], f['x'], f['canon'],
                 f['probe'], f['delta'], f['margin'], f['line_resid']))
print('\n--- every CONF ---')
for f in flags:
    if f['cls'] == 'CONF':
        print('  page %-3s gline %-4s slot %-3s canon %-3s probe %-3s delta %s'
              % (f['page'], f['gline'], f['slot'], f['canon'], f['probe'], f['delta']))

json.dump(dict(tau=TAU, n_lines=n_lines, n_slots=n_slots,
               skipped_initial=skipped_initial, fails=dict(fails),
               median_resid=float(np.median(resid_all)),
               flags=flags,
               per_page={str(k): v for k, v in per_page.items()}),
          open(os.path.join(T.HERE, 'out_a01.json'), 'w'), indent=1)
print('\nwrote out_a01.json')
