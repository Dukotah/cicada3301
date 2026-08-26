"""T2 -- WFA forced alignment + leave-one-out substitution probe.

See PREREG.md §1. Canon supplies the token SEQUENCE (count and order); the ink
chooses the cut points; every slot is then re-opened to all 29 runes with its
neighbours held fixed.

Band construction: the row's ink restricted to components of height >= 40 whose
x-centre lies in the text column. That drops the ~9x10 px separator dots and the
margin ornaments (height classes measured in round12/frontB) and keeps split rune
strokes. Separators are adjudicated separately -- they are a different object.

usage:  python3 probe.py [--pages 45,46,...] [--out out_probe.json]
"""
import os
import sys
import json
import time
import numpy as np
from scipy import ndimage
import t2lib as T


def band_of(rec, pad_y=8, pad_x=24):
    """Ink of one text row, ornament- / dot- / drop-cap-stripped (see t2lib.text_mask)."""
    path = os.path.join(T.ROOT, rec['path'])
    m = T.text_mask(path)
    y0 = max(0, rec['y0'] - pad_y)
    y1 = min(m.shape[0], rec['y1'] + pad_y)
    x0 = max(0, rec['x0'] - pad_x)
    x1 = min(m.shape[1], rec['x1'] + pad_x)
    return np.ascontiguousarray(m[y0:y1, x0:x1]), x0, y0


def run(records, tmpl, log_every=50):
    alt = list(range(29))
    canon = T.canon_lines()
    res = []
    t0 = time.time()
    for k, rec in enumerate(records):
        line = canon[rec['gline']]
        keys = list(line['runes'])
        # An illuminated initial carries canon's first rune at ~5x rune height; no
        # template can match it, so the slot is excluded from adjudication and
        # NAMED, rather than silently misread (PREREG 4: SEG, not ID).
        skip0 = 1 if (rec.get('initial') and keys) else 0
        if skip0:
            keys = keys[1:]
        band, bx, by = band_of(rec)
        if band.shape[1] < 40 or not keys:
            res.append(dict(gline=rec['gline'], fail='empty'))
            continue
        cc = T.cost_curves(band, tmpl)
        missing = [r for r in set(keys + alt) if r not in cc]
        if any(r not in cc for r in keys):
            res.append(dict(gline=rec['gline'], fail='template_wider_than_band',
                            missing=missing))
            continue
        skip = band.sum(0) * T.SKIP_A + T.SKIP_B
        total, alpha, beta, table, xpos = T.loo_probe(band, keys, cc, skip, alt)
        best = table.argmin(1)
        bestc = table.min(1)
        srt = np.sort(table, axis=1)
        second = srt[:, 1]
        canonc = table[np.arange(len(keys)), keys]
        res.append(dict(
            gline=rec['gline'], seg=rec['seg'], num=rec['num'], src=rec['src'],
            ncomp=rec['ncomp'], nrune=rec['nrune'], skip0=skip0,
            total=round(total, 1), W=int(band.shape[1]),
            canon=keys,
            best=[int(b) for b in best],
            canon_cost=[round(float(v), 1) for v in canonc],
            best_cost=[round(float(v), 1) for v in bestc],
            second_cost=[round(float(v), 1) for v in second],
            x=[int(v + bx) for v in xpos],
        ))
        if log_every and (k + 1) % log_every == 0:
            print('  %d/%d  %.1fs' % (k + 1, len(records), time.time() - t0), flush=True)
    return res


def main():
    args = sys.argv[1:]
    pages = None
    out = 'out_probe.json'
    for i, a in enumerate(args):
        if a == '--pages':
            pages = set(args[i + 1].split(','))
        if a == '--out':
            out = args[i + 1]
    lm = json.load(open(os.path.join(T.HERE, 'out_linemap.json')))['map']
    if pages:
        lm = [r for r in lm if '%s:%s' % (r['src'], r['num']) in pages
              or str(r['num']) in pages]
    print('lines to probe: %d' % len(lm))
    tmpl = T.load_templates()
    print('templates: %d runes  widths %s'
          % (len(tmpl), sorted((r, tmpl[r].shape[1]) for r in tmpl)))
    res = run(lm, tmpl)
    json.dump(res, open(os.path.join(T.HERE, out), 'w'))
    print('wrote %s' % out)


if __name__ == '__main__':
    main()
