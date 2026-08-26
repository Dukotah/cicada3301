"""Adjudicate every indel flag: is there RUNE-CLASS ink that canon does not account for?

The decisive image-side check is the one the line map already computes:
  ncomp (+1 if an illuminated initial) == nrune  ->  the image carries EXACTLY canon's
  number of rune-body components, so no rune is missing and none is extra; any indel
  delta on such a line is ink of a NON-RUNE class (ornament, split stroke, folio mark)
  leaking into the band -- a SEGMENTATION artifact, not a length error in canon.
"""
import os, json, collections
import numpy as np
import t2lib as T
from lp.gematria import IDX_TO_TRANS

sc = json.load(open(os.path.join(T.HERE, 'out_indel_score.json')))
lm = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, 'out_linemap.json')))['map']}
canon = T.canon_lines()

out = []
print('%-4s %-5s %-5s %-4s %-4s %-6s %-6s %-9s %s' %
      ('kind', 'page', 'gline', 'pos', 'L', 'ncomp', 'nrune', 'delta', 'verdict'))
for kind, r in sc['flags']:
    rec = lm[r['gline']]
    eff = rec['ncomp'] + rec.get('initial', 0)
    pos = r['arg_del'] if kind == 'DEL' else r['arg_ins']
    delta = r['max_del'] if kind == 'DEL' else r['max_ins']
    if eff == rec['nrune']:
        v = 'SEG  non-rune ink in band; component count matches canon exactly'
    elif eff < rec['nrune'] and kind == 'INS':
        v = 'SEG? fewer components than runes (merge) -- ambiguous, crop'
    elif eff > rec['nrune'] and kind == 'DEL':
        v = 'CAND more components than runes'
    else:
        v = 'SEG  count mismatch in the direction opposite the flag'
    print('%-4s %-5s %-5s %-4s %-4s %-6s %-6s %-9s %s'
          % (kind, r['num'], r['gline'], pos, r['L'], rec['ncomp'], rec['nrune'],
             delta, v))
    out.append(dict(kind=kind, page=r['num'], gline=r['gline'], pos=pos,
                    ncomp=rec['ncomp'], initial=rec.get('initial', 0),
                    nrune=rec['nrune'], delta=delta, verdict=v.split()[0]))

c = collections.Counter(o['verdict'] for o in out)
print('\nverdicts:', dict(c))
json.dump(out, open(os.path.join(T.HERE, 'out_indel_adj.json'), 'w'), indent=1)
