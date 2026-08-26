"""Score the indel probe: plant power, then the production flags and the BOUND."""
import os, json, math, collections
import numpy as np
import t2lib as T
from lp.gematria import IDX_TO_TRANS

d = json.load(open(os.path.join(T.HERE, 'out_indel.json')))
rows, plants = d['rows'], d['plants']

print('=== C5  INDEL PLANT POWER  (a planted CANON length error) ===')
agg = collections.defaultdict(lambda: dict(n=0, fired=0, loc=0, rune=0, nr=0))
for p in plants:
    a = agg[(p['kind'], p['stratum'])]
    a['n'] += 1; a['fired'] += p['fired']; a['loc'] += p['loc']
    if p['rune'] is not None:
        a['nr'] += 1; a['rune'] += p['rune']
for k in sorted(agg):
    a = agg[k]
    extra = ('   rune named %.4f' % (a['rune'] / a['nr'])) if a['nr'] else ''
    print('%-20s %-12s n %4d   fired %.4f   localised %.4f%s'
          % (k[0], k[1], a['n'], a['fired'] / a['n'], a['loc'] / a['n'], extra))

pooled = collections.defaultdict(lambda: dict(n=0, fired=0, loc=0))
for p in plants:
    a = pooled[p['kind']]
    a['n'] += 1; a['fired'] += p['fired']; a['loc'] += p['loc']
print()
for k, a in pooled.items():
    print('POOLED %-20s n %4d  fired %.4f  localised %.4f'
          % (k, a['n'], a['fired'] / a['n'], a['loc'] / a['n']))

# --- threshold from the pages proven correct BY DECRYPTION
print('\n=== C6  production flags -- threshold calibrated on the solved pages ===')
sol = [r for r in rows if r['stratum'] == 'solved-LP2']
print('solved-LP2 lines %d   max_del %s   max_ins %s'
      % (len(sol), max(r['max_del'] for r in sol), max(r['max_ins'] for r in sol)))
TAU_D = max(0.0, max(r['max_del'] for r in sol))
TAU_I = max(0.0, max(r['max_ins'] for r in sol))
print('tau_del = %.1f   tau_ins = %.1f  (the largest value canon-proven-correct '
      'ink produces)' % (TAU_D, TAU_I))

by = collections.defaultdict(lambda: dict(lines=0, fd=0, fi=0))
fl = []
for r in rows:
    a = by[r['stratum']]
    a['lines'] += 1
    if r['max_del'] > TAU_D:
        a['fd'] += 1; fl.append(('DEL', r))
    if r['max_ins'] > TAU_I:
        a['fi'] += 1; fl.append(('INS', r))
print()
for s in ('solved-LP2', 'pages-0-44', 'dense-45-54'):
    a = by[s]
    print('%-12s lines %4d   lines flagged EXTRA-rune %2d   lines flagged MISSING-rune %2d'
          % (s, a['lines'], a['fd'], a['fi']))
for k, r in sorted(fl, key=lambda t: -max(t[1]['max_del'], t[1]['max_ins'])):
    print('   %s page %-3s gline %-4s L %-3s pos %-3s delta %s'
          % (k, r['num'], r['gline'], r['L'],
             r['arg_del'] if k == 'DEL' else r['arg_ins'],
             r['max_del'] if k == 'DEL' else r['max_ins']))

# --- the BOUND
print('\n=== THE BOUND ===')
n_pos = sum(r['L'] for r in rows)
for kind in pooled:
    a = pooled[kind]
    p_hat = a['loc'] / a['n']
    # Clopper-Pearson-ish lower bound via rule of three when no misses
    miss = a['n'] - a['loc']
    p_lo = (1.0 - 3.0 / a['n']) if miss == 0 else p_hat - 1.96 * math.sqrt(
        p_hat * (1 - p_hat) / a['n'])
    k95 = math.log(0.05) / math.log(1 - p_lo) if p_lo < 1 else 0.0
    print('%-20s power (localised) %.4f  95%% lower bound %.4f  ->  a real canon '
          'error of this kind survives undetected with prob <= %.4f each;\n'
          '%22s  observing ZERO on %d positions bounds the count at k <= %.2f at 95%% confidence'
          % (kind, p_hat, p_lo, 1 - p_lo, '', n_pos, k95))
print('\npositions tested: %d rune slots over %d lines' % (n_pos, len(rows)))
json.dump(dict(tau_del=TAU_D, tau_ins=TAU_I, n_positions=n_pos,
               pooled={k: v for k, v in pooled.items()},
               per_stratum={'%s|%s' % k: v for k, v in agg.items()},
               flags=[[k, r] for k, r in fl]),
          open(os.path.join(T.HERE, 'out_indel_score.json'), 'w'), indent=1)
print('wrote out_indel_score.json')
