"""DECISIVE TEST for the SEG diagnosis.

Hypothesis: every T2 flag (26 indel + 2 substitution) is the MID-SIZE mark class
(35-94 px tall thin ticks) leaking into the band, not an error in canon.

Test: rebuild the bands with the mask raised to rune bodies only (h >= 95) and re-run
BOTH probes on (a) the 10 decryption-proven control lines and (b) every flagged line.
  - if the diagnosis is right : control stays at 1.0000 AND the flags disappear
  - if canon is really wrong  : the flags survive
"""
import os, json, collections
import numpy as np
import t2lib as T
from indel import del_deltas, ins_deltas
from lp.gematria import IDX_TO_TRANS

lm = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, 'out_linemap.json')))['map']}
adj = json.load(open(os.path.join(T.HERE, 'out_indel_adj.json')))
canon = T.canon_lines()
tmpl = T.load_templates()
ALT = list(range(29))

targets = sorted({a['gline'] for a in adj} | {51, 452} | set(range(594, 604)))


def band_hi(rec, hmin, pad_y=8, pad_x=24):
    m = T.text_mask(os.path.join(T.ROOT, rec['path']), hmin=hmin)
    y0 = max(0, rec['y0'] - pad_y); y1 = min(m.shape[0], rec['y1'] + pad_y)
    x0 = max(0, rec['x0'] - pad_x); x1 = min(m.shape[1], rec['x1'] + pad_x)
    return np.ascontiguousarray(m[y0:y1, x0:x1]), x0


for hmin, tag in ((40, 'BASELINE h>=40'), (95, 'VARIANT  h>=95 (rune bodies only)')):
    sub_bad = ind_bad = 0
    ctrl_slots = ctrl_hit = 0
    rows = []
    for gl in targets:
        rec = lm[gl]
        line = canon[gl]
        keys = list(line['runes'])
        if rec.get('initial') and keys:
            keys = keys[1:]
        band, bx = band_hi(rec, hmin)
        W = band.shape[1]
        cc = T.cost_curves(band, tmpl)
        if any(r not in cc for r in keys) or W < 40:
            continue
        skip = band.sum(0) * T.SKIP_A + T.SKIP_B
        S = np.concatenate([[0.0], np.cumsum(skip)])
        a = T.forward(band, keys, cc, skip, S)
        b = T.backward(band, keys, cc, skip, S)
        C = float(a[len(keys)][W])
        _, _, _, table, _ = T.loo_probe(band, keys, cc, skip, ALT, S)
        best = table.argmin(1)
        nbad = int(sum(1 for j, c in enumerate(keys) if best[j] != c))
        dd = del_deltas(a, b, C, len(keys))
        di, _ = ins_deltas(a, b, C, len(keys), cc, W)
        fl = (dd.max() > 0) or (di.max() > 0)
        sub_bad += nbad
        ind_bad += int(fl)
        if 594 <= gl <= 603:
            ctrl_slots += len(keys); ctrl_hit += len(keys) - nbad
        rows.append((gl, nbad, float(dd.max()), float(di.max())))
    print('%-34s  control loo_agreement %s   substitution disagreements %d   '
          'lines with an indel flag %d/%d'
          % (tag, ('%.4f' % (ctrl_hit / ctrl_slots)) if ctrl_slots else 'n/a',
             sub_bad, ind_bad, len(rows)))
