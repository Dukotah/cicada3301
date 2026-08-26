"""L3 stage 3 -- READ EVERY CATALOGUED BAND.  The durable artifact of this lane.

For each of the 109 band records in `inventory.json` (the deduped union of Round 8's
`geometry/ornaments.json` 62 rows and `geometry_report.json:ornaments` 47 rows, with the
y coordinate restored):

  * describe the ink physically  -- component count, height/width/area distribution;
  * classify the band            -- TEXT / VINE / WOODCUT / ALPHANUMERIC / DOT / MIXED,
                                    from component geometry alone, no reading required;
  * read it                      -- validated R9 template DP, one shared code path with
                                    `calibrate.py`, mapped through the stored 29-class
                                    bijection;
  * record the per-glyph template match cost, so a reading can be trusted or distrusted
    against the cost distribution measured on known text.

Writes `bands.json` incrementally (after every band) so a crash leaves a usable artifact.
"""
import os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402
sys.path.insert(0, os.path.join(R.LP, 'src'))
from lp.gematria import IDX_TO_TRANS                                   # noqa: E402

IMG = os.path.join(R.LP, 'data', 'relikd')
OUT = os.path.join(HERE, 'bands.json')

RUNE_BODY = (95, 140)     # rune body height at 2400x3600 (measured: mode 114)
ALNUM_H = (30, 80)        # the alphanumeric tokens on pp.49-51 measure ~44-69 px
DOT_H = 30                # inter-word separator dot / hairline fragment


def classify(hs, ws, areas, medh, n):
    """Physical classification from component geometry only."""
    hs = np.asarray(hs, float); ws = np.asarray(ws, float)
    if n == 0:
        return 'EMPTY'
    frac_rune = float(np.mean((hs >= RUNE_BODY[0]) & (hs <= RUNE_BODY[1])))
    frac_dot = float(np.mean(hs < DOT_H))
    frac_alnum = float(np.mean((hs >= ALNUM_H[0]) & (hs < ALNUM_H[1])))
    big = float(np.mean((hs > 200) | (ws > 400)))
    if big >= 0.5 and n <= 4:
        return 'WOODCUT/DROPCAP'
    if frac_rune >= 0.5:
        return 'TEXT'
    if frac_alnum >= 0.5 and n >= 6:
        return 'ALPHANUMERIC?'
    if frac_dot >= 0.6:
        return 'DOT/HAIRLINE'
    if big > 0:
        return 'VINE/WOODCUT'
    return 'MIXED'


def main():
    tmpl = R.load_templates()
    mapping = R.load_mapping()
    inv = json.load(open(os.path.join(HERE, 'inventory.json')))
    out = []
    t0 = time.time()
    for bi, b in enumerate(inv):
        p = b['page']
        path = os.path.join(IMG, 'p%d.jpg' % p)
        ct = R.comp_table(path)
        # overlap (not strict containment): a component clipped by the band edge is
        # still part of the band's ink and must not vanish into an 'EMPTY' call.
        ox = np.minimum(ct['x1'], b['x'][1]) - np.maximum(ct['x0'], b['x'][0])
        oy = np.minimum(ct['y1'], b['y'][1]) - np.maximum(ct['y0'], b['y'][0])
        inb = (ox > 0) & (oy > 0) &               (ox * oy >= 0.5 * (ct['x1'] - ct['x0']) * (ct['y1'] - ct['y0']))
        hs = (ct['y1'] - ct['y0'])[inb]
        ws = (ct['x1'] - ct['x0'])[inb]
        ar = ct['area'][inb]
        kind = classify(hs, ws, ar, b['medh'], int(inb.sum()))

        # read: split the band into ink rows, read each with the shared code path
        ink = R.page_ink(path)
        sub = np.zeros_like(ink)
        sub[b['y'][0]:b['y'][1] + 1, b['x'][0]:b['x'][1] + 1] = \
            ink[b['y'][0]:b['y'][1] + 1, b['x'][0]:b['x'][1] + 1]
        rows = R.rows_from_ink(sub, min_gap=10, min_h=20)
        if any(c - a > 400 for a, c in rows):
            # a mega-band: vine/woodcut ink bridges the text lines. Re-split using the
            # ink with large components erased, so genuine text rows separate.
            tink = R.text_ink(path)[0]
            sub2 = np.zeros_like(tink)
            sub2[b['y'][0]:b['y'][1] + 1, b['x'][0]:b['x'][1] + 1] =                 tink[b['y'][0]:b['y'][1] + 1, b['x'][0]:b['x'][1] + 1]
            rows2 = R.rows_from_ink(sub2, min_gap=10, min_h=20)
            if len(rows2) > len(rows):
                rows, sub = rows2, sub2
        glyphs, costs, lines = [], [], []
        for (a, c) in rows:
            if c - a > 400:                       # still a mega-row: not a readable line
                lines.append(dict(y=[int(a), int(c)], skipped='row taller than 400px'))
                continue
            g = R.read_ink_strip(sub, a - 3, c + 3, tmpl, b['x'][0] - 5, b['x'][1] + 5)
            if not g and (c - a) < 100:
                # too short for any rune template to fit: re-read upscaled to rune height
                g = R.read_scaled(sub, a - 3, c + 3, tmpl, b['x'][0] - 5, b['x'][1] + 5,
                                  target_h=125)
            rr = [mapping.get(cid, -1) for cid, x, k in g]
            kk = [k for cid, x, k in g]
            lines.append(dict(y=[int(a), int(c)], n=len(g),
                              runes=[int(v) for v in rr],
                              translit=''.join(IDX_TO_TRANS[v] if v >= 0 else '?' for v in rr),
                              cost_median=round(float(np.median(kk)), 1) if kk else None))
            glyphs += rr
            costs += kk
        medcost = round(float(np.median(costs)), 1) if costs else None
        # degeneracy guard: a vine's long vertical stroke reads as a run of the same
        # narrow template (typically I).  A read dominated by one class is not a reading.
        degen = 0.0
        if glyphs:
            vals, cnts = np.unique(np.array(glyphs), return_counts=True)
            degen = float(cnts.max()) / len(glyphs)
        runic = (medcost is not None and medcost <= 300.0 and degen < 0.60)
        rec = dict(id=b['id'], page=p, x=b['x'], y=b['y'], w=b['w'], h=b['h'],
                   n_reported=b['n'], medh_reported=b['medh'], why=b['why'], src=b['src'],
                   n_components=int(inb.sum()),
                   comp_h=dict(min=int(hs.min()) if len(hs) else None,
                               med=int(np.median(hs)) if len(hs) else None,
                               max=int(hs.max()) if len(hs) else None),
                   comp_w=dict(min=int(ws.min()) if len(ws) else None,
                               med=int(np.median(ws)) if len(ws) else None,
                               max=int(ws.max()) if len(ws) else None),
                   ink_class=kind, n_rows=len(rows), n_glyphs_read=len(glyphs),
                   cost_median=medcost, degeneracy=round(degen, 3),
                   call=('RUNIC' if runic else
                         ('DEGENERATE' if (medcost is not None and medcost <= 300.0
                                           and degen >= 0.60) else 'NON-RUNIC')),
                   translit=''.join(IDX_TO_TRANS[v] if v >= 0 else '?' for v in glyphs),
                   runes=[int(v) for v in glyphs],
                   lines=lines)
        out.append(rec)
        json.dump(out, open(OUT, 'w'), indent=1)
        print('%3d/%d %s p%-2d %-15s rows %2d glyphs %3d cost %-8s deg %.2f %-11s %s'
              % (bi + 1, len(inv), b['id'], p, kind, len(rows), len(glyphs),
                 medcost, degen, rec['call'], rec['translit'][:34]), flush=True)
    print('done in %.1fs -> %s' % (time.time() - t0, OUT))


if __name__ == '__main__':
    main()
