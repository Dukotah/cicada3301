"""Front B final measurement.

Established by exhaustive diagnosis (see RESULTS.md):
  * The R9 template DP (analysis/retranscribe/read.py) is a validated instrument:
    on lines whose RAW-band glyph count naturally equals the canon rune count it
    agrees with canon at ~98% (positive control PASSES on those lines).
  * FORCING a glyph count on ornament/separator-ambiguous lines does NOT recover
    per-rune identity: the segmentation ambiguity is real, so forced reads on the
    dense pages fall to chance (~3-12%). Forcing cannot manufacture information the
    image does not localise.

Therefore the honest measurement mirrors R9 but (a) additionally runs the
ornament-stripped text_strip decode to try to lift more OTP lines into the
count-exact set, and (b) reports the count-exact agreement and every disagreement
SPECIFICALLY on pages 45-54, adjudicating whether any is a real rune-value error
(a reopener) versus known-confusable / segmentation noise.

Positive control = count-exact agreement on solved control pages (must be high).
"""
import os, sys, json, collections
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'analysis', 'retranscribe'))
sys.path.insert(0, HERE)
import read as R9read
import forceseg as F
from lp.gematria import IDX_TO_TRANS

CONTROL = list(range(2, 14))
TARGET = list(range(45, 55))


def decode_variants(geo, gli, ink, tmpl):
    """Return the decode (list of class ids) from (a) the raw R9 band and (b) the
    ornament-stripped text_strip, whichever yields more glyphs matched to canon
    count later. We return both so the caller can pick the count-exact one."""
    band = F.band_for_line(geo, gli, ink)
    strip, _, _ = F.text_strip(geo, gli, ink)
    raw = [c for c, x, k in R9read.decode_line(band, tmpl, band.shape[0])]
    strp = [c for c, x, k in R9read.decode_line(strip, tmpl, strip.shape[0])]
    return raw, strp


def measure(geo, canon, tmpl, pages, mapping=None):
    """Decode each line both ways; a line is 'count-exact' if EITHER variant's
    glyph count equals the canon rune count. Collect (class,rune) pairs on those.
    If mapping given, also compute agreement + disagreements."""
    rows = []
    for p in pages:
        a = np.asarray(Image.open(os.path.join(F.IMG, 'p%d.jpg' % p)).convert('L'))
        ink = (a < 128).astype(np.float32)
        for gli in F.line_ids_for_page(geo, p):
            if gli >= len(canon):
                continue
            runes = [t[1] for t in F.canon_tokens(canon[gli]) if t[0] == 'r']
            if len(runes) < 3:
                continue
            raw, strp = decode_variants(geo, gli, ink, tmpl)
            pick = None
            if len(raw) == len(runes):
                pick = raw
            elif len(strp) == len(runes):
                pick = strp
            rows.append(dict(page=p, gli=gli, runes=runes,
                             nraw=len(raw), nstrip=len(strp),
                             exact=pick is not None, pick=pick))
    return rows


def build_mapping(rows):
    M = np.zeros((32, 29), np.int64)
    for r in rows:
        if not r['exact']:
            continue
        for c, rune in zip(r['pick'], r['runes']):
            M[c, rune] += 1
    from scipy.optimize import linear_sum_assignment
    rr, cc = linear_sum_assignment(-M)
    return {int(a): int(b) for a, b in zip(rr, cc)}, M


def agreement(rows, mapping):
    hit = tot = 0
    dis = []
    for r in rows:
        if not r['exact']:
            continue
        for pos, (c, rune) in enumerate(zip(r['pick'], r['runes'])):
            tot += 1
            m = mapping.get(c)
            if m == rune:
                hit += 1
            else:
                dis.append(dict(page=r['page'], gli=r['gli'], pos=pos,
                                image=IDX_TO_TRANS[m] if m is not None else '?',
                                canon=IDX_TO_TRANS[rune]))
    return hit, tot, dis


def main():
    geo = F.load_geo(); canon = F.load_canon_full(); tmpl = F.load_templates()

    print('measuring CONTROL pages %s ...' % CONTROL, flush=True)
    cr = measure(geo, canon, tmpl, CONTROL)
    mapping, M = build_mapping(cr)
    # bijection check
    bij = len(set(mapping.values())) == len(mapping)
    ch, ct, cd = agreement(cr, mapping)
    ce = sum(1 for r in cr if r['exact'])
    print('control lines %d | count-exact %d (%.1f%%) | agreement %.2f%% (%d)'
          % (len(cr), ce, 100 * ce / len(cr), 100 * ch / max(ct, 1), ct))
    print('mapping bijection: %s (%d distinct targets)' % (bij, len(set(mapping.values()))))

    print('\nmeasuring TARGET pages 45-54 ...', flush=True)
    tr = measure(geo, canon, tmpl, TARGET)
    th, tt, td = agreement(tr, mapping)
    te = sum(1 for r in tr if r['exact'])
    print('target lines %d | count-exact %d (%.1f%%) | agreement %.2f%% (%d)'
          % (len(tr), te, 100 * te / max(len(tr), 1), 100 * th / max(tt, 1), tt))

    conf = collections.Counter((d['image'], d['canon']) for d in td)
    ann = []
    for r in tr:
        ann.append(dict(page=r['page'], gli=r['gli'], canon_runes=len(r['runes']),
                        nraw=r['nraw'], nstrip=r['nstrip'], count_exact=r['exact']))
    out = dict(
        method='R9 template DP (raw band + ornament-stripped strip), count-exact only',
        control_pages=CONTROL, target_pages=TARGET,
        control_lines=len(cr), control_count_exact=ce,
        control_agreement=100 * ch / max(ct, 1), control_compared=ct,
        mapping_bijection=bool(bij), mapping_distinct=len(set(mapping.values())),
        target_lines=len(tr), target_count_exact=te,
        target_agreement=100 * th / max(tt, 1), target_compared=tt,
        target_disagreements=len(td),
        target_confusions=[[a, b, n] for (a, b), n in conf.most_common(40)],
        target_dis_detail=td,
        target_line_annot=ann,
        mapping={str(k): v for k, v in mapping.items()},
    )
    json.dump(out, open(os.path.join(HERE, 'results.json'), 'w'), indent=1)
    print('\nwrote results.json')
    print('target confusions (image->canon):')
    for (a, b), n in conf.most_common(15):
        print('  %-4s -> %-4s  %d' % (a, b, n))


if __name__ == '__main__':
    main()
