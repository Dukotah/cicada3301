"""C3 / L3 gate G-A2 -- calibrate the band reader on BAND-SHAPED objects of known identity.

WHY THIS EXISTS
---------------
Round 18's `calibrate.py` measured the reader **whole-page**: read every text row of a
solved page, concatenate, align to the page's canonical rune sequence with difflib. That
number (44.2% pooled) is the right number for a whole-page transcription instrument. It is
the WRONG number for this lane, because this lane does not read pages. It reads **bands** --
a box of at most a few dozen glyphs, isolated, read on its own.

Round 9's whole-page vision armada scored 0.145 alignment on dense pages. The claim that a
per-band read is a much easier task is plausible and it is exactly the kind of claim this
repository is supposed to MEASURE rather than assert (doctrine mechanic 2). So: plant the
thing being hunted, in the shape it takes.

THE PLANT
---------
A band record is `(page, x0..x1, y0..y1)`. Take a solved page -- one whose plaintext is
known by DECRYPTION, not by consensus transcription -- and synthesise band records whose
boxes each cover exactly one known text line. Feed them through the **identical** code path
`read_bands.py` uses on the real ornament bands (page ink -> box mask -> `rows_from_ink` ->
`read_ink_strip` / `read_scaled` -> stored R9 bijection -> RUNIC/DEGENERATE/NON-RUNIC call).
Then compare to the canonical runes of that line.

GROUND TRUTH  (flat-stream attribution, per PREREG 0.1)
-------------------------------------------------------
The corpus's rune lines are broken SEMANTICALLY; the image's lines are broken
TYPOGRAPHICALLY, and they do not agree -- a fact Round 18 already recorded in
`calibrate.py`'s docstring. Matching band i to canon line i therefore measures the
transcriber's paragraph breaks, not the reader: on page 05 the image's first row really does
carry `SOMEWISDOM . THEPRIMESARESAC` and the second really does begin `RED`, because the
typesetter wrapped at the column and the transcriber wrapped at the sentence.

So truth is attributed against the page's FLAT canonical rune stream: concatenate the band
reads in reading order, align once with difflib(autojunk=False), then attribute each matched
glyph back to the band that produced it. Per-band agreement = matched / glyphs read
(PRECISION -- of the glyphs this band emitted, how many are right), which is the statistic
that governs whether a band's content may be quoted.

TWO SIDES, BOTH REQUIRED
------------------------
  * SENSITIVITY -- known rune bands must read as runes, and the per-glyph agreement on
    them is the number this lane is allowed to quote about band reads.
  * SPECIFICITY -- known NON-rune bands (blank paper, vine margin, woodcut interior) must
    NOT be called RUNIC. A reader that calls everything runic has 100% sensitivity and no
    information. Round 18 measured only the first half.

Writes `band_control.json`.
"""
import os, sys, json, difflib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402
import read_bands as RB                                                # noqa: E402
sys.path.insert(0, os.path.join(R.LP, 'src'))
from lp import corpus                                                  # noqa: E402
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS                      # noqa: E402

ASSETS = os.path.join(R.ROOT, 'corpus', 'E-tooling', 'vendor',
                      'cicada-solvers__documenting-cicada3301-scream314',
                      'assets', '2014', 'liber-primus-complete')

# (asset, corpus label, title, typeface era)
CONTROL = [('73.jpg', '73.jpg - 56.jpg', 'LP2 p56 (solved: phi(prime) shift)', 'LP2'),
           ('74.jpg', '74.jpg - 57.jpg', 'LP2 p57 (solved: default-gematria sub)', 'LP2'),
           ('01.jpg', 'Runes - 01.jpg', 'A WARNING', 'LP1'),
           ('03.jpg', '03.jpg', 'WELCOME', 'LP1'),
           ('05.jpg', '05.jpg', 'SOME WISDOM', 'LP1'),
           ('06.jpg', '06.jpg', 'A KOAN', 'LP1'),
           ('14.jpg', '14.jpg', 'A KOAN (circumference)', 'LP1')]


def canon_flat(label):
    """The page's canonical rune stream, FLAT -- line breaks discarded, because the
    corpus's line breaks are semantic and the image's are typographic."""
    pg = corpus.page_by_label(label)
    return [RUNE_TO_IDX[c] for c in pg['runes'] if c in RUNE_TO_IDX]


def read_band_box(path, box, tmpl, mapping):
    """EXACTLY the read half of read_bands.py: mask the box, split to ink rows, read.

    Returns (rune_indices, costs, n_rows, degeneracy, call).
    """
    x0, x1, y0, y1 = box
    ink = R.page_ink(path)
    sub = np.zeros_like(ink)
    sub[y0:y1 + 1, x0:x1 + 1] = ink[y0:y1 + 1, x0:x1 + 1]
    rows = R.rows_from_ink(sub, min_gap=10, min_h=20)
    if any(c - a > 400 for a, c in rows):
        tink = R.text_ink(path)[0]
        sub2 = np.zeros_like(tink)
        sub2[y0:y1 + 1, x0:x1 + 1] = tink[y0:y1 + 1, x0:x1 + 1]
        rows2 = R.rows_from_ink(sub2, min_gap=10, min_h=20)
        if len(rows2) > len(rows):
            rows, sub = rows2, sub2
    glyphs, costs = [], []
    for (a, c) in rows:
        if c - a > 400:
            continue
        g = R.read_ink_strip(sub, a - 3, c + 3, tmpl, x0 - 5, x1 + 5)
        if not g and (c - a) < 100:
            g = R.read_scaled(sub, a - 3, c + 3, tmpl, x0 - 5, x1 + 5, target_h=125)
        glyphs += [mapping.get(cid, -1) for cid, x, k in g]
        costs += [k for cid, x, k in g]
    medcost = float(np.median(costs)) if costs else None
    degen = 0.0
    if glyphs:
        vals, cnts = np.unique(np.array(glyphs), return_counts=True)
        degen = float(cnts.max()) / len(glyphs)
    if medcost is None:
        call = 'EMPTY'
    elif medcost <= 300.0 and degen < 0.60:
        call = 'RUNIC'
    elif medcost <= 300.0:
        call = 'DEGENERATE'
    else:
        call = 'NON-RUNIC'
    return glyphs, costs, len(rows), degen, call, medcost


def agreement(read_seq, truth_seq):
    sm = difflib.SequenceMatcher(a=read_seq, b=truth_seq, autojunk=False)
    hit = sum(bl.size for bl in sm.get_matching_blocks())
    return hit, max(len(read_seq), len(truth_seq))


def attribute(page_read, canon, spans):
    """Align the concatenated band reads to the flat canon ONCE, then push each matched
    glyph back to the band it came from.

    `spans` is [(band_index, start, stop)] into `page_read`. Returns per-band matched
    counts and the page totals. difflib's matching blocks are contiguous equal runs, so
    a matched glyph's position in `page_read` identifies its band unambiguously.
    """
    sm = difflib.SequenceMatcher(a=page_read, b=canon, autojunk=False)
    matched_flags = np.zeros(len(page_read), bool)
    for bl in sm.get_matching_blocks():
        if bl.size:
            matched_flags[bl.a:bl.a + bl.size] = True
    per = {}
    for (bi, a, b) in spans:
        per[bi] = int(matched_flags[a:b].sum())
    return per, int(matched_flags.sum())


def main():
    tmpl = R.load_templates()
    mapping = R.load_mapping()
    res = dict(sensitivity=[], specificity=[], pages=[])

    for asset, label, title, era in CONTROL:
        path = os.path.join(ASSETS, asset)
        if not os.path.exists(path):
            print('MISSING', path); continue
        canon = canon_flat(label)
        # Band boxes = the page's image text rows, built from RUNE-HEIGHT components only so
        # ornament ink cannot merge two lines into one box. Each is then read as a band.
        trows, comps, _ = R.text_rows(path)
        reads, page_read, spans = [], [], []
        for bi, r in enumerate(trows):
            bx = (r['x0'], r['x1'], r['y0'], r['y1'])
            g, k, nr, dg, call, mc = read_band_box(path, bx, tmpl, mapping)
            spans.append((bi, len(page_read), len(page_read) + len(g)))
            page_read += g
            reads.append(dict(box=list(bx), glyphs=g, degen=dg, call=call, medcost=mc))

        per, page_matched = attribute(page_read, canon, spans)

        for bi, rd in enumerate(reads):
            n = len(rd['glyphs'])
            m = per.get(bi, 0)
            res['sensitivity'].append(dict(
                asset=asset, era=era, band=bi, box=rd['box'],
                n_read=n, matched=int(m),
                precision=round(100.0 * m / max(n, 1), 2),
                call=rd['call'], degeneracy=round(rd['degen'], 3),
                medcost=None if rd['medcost'] is None else round(rd['medcost'], 1),
                read=''.join(IDX_TO_TRANS[v] if v >= 0 else '?' for v in rd['glyphs'])))

        res['pages'].append(dict(
            asset=asset, title=title, era=era, n_bands=len(trows),
            glyphs_read=len(page_read), canon_runes=len(canon),
            matched=int(page_matched),
            agreement=round(100.0 * page_matched / max(len(page_read), len(canon), 1), 2),
            precision=round(100.0 * page_matched / max(len(page_read), 1), 2)))
        print('%-8s %-4s bands %2d  read %4d  canon %4d  matched %4d  agree %6.2f%%  prec %6.2f%%'
              % (asset, era, len(trows), len(page_read), len(canon), page_matched,
                 100.0 * page_matched / max(len(page_read), len(canon), 1),
                 100.0 * page_matched / max(len(page_read), 1)), flush=True)

    # ---------------------------------------------------------------- specificity
    # Boxes over ink that is KNOWN not to be runes. Blank paper: the outer margin.
    # Woodcut: the large-component bounding boxes on the illustrated pages.
    IMGDIR = os.path.join(R.LP, 'data', 'relikd')
    spec = []
    for p, kind in [(2, 'woodcut'), (3, 'woodcut'), (14, 'woodcut'), (22, 'woodcut'),
                    (32, 'woodcut'), (54, 'woodcut'), (55, 'woodcut')]:
        path = os.path.join(IMGDIR, 'p%d.jpg' % p)
        c = R.comp_table(path)
        h = c['y1'] - c['y0']; w = c['x1'] - c['x0']
        big = np.where((h > 200) | (w > 420))[0]
        if not len(big):
            continue
        k = big[np.argmax((h * w)[big])]
        spec.append((p, kind, (int(c['x0'][k]), int(c['x1'][k]),
                               int(c['y0'][k]), int(c['y1'][k]))))
    for p in (0, 10, 25, 40):
        path = os.path.join(IMGDIR, 'p%d.jpg' % p)
        ink = R.page_ink(path)
        H, W = ink.shape
        spec.append((p, 'blank-margin', (20, 400, 200, 1200)))
        spec.append((p, 'blank-margin', (W - 420, W - 20, 200, 1200)))
    # vine margin: the tall narrow components on the bordered pages
    for p in (41, 45, 50):
        path = os.path.join(IMGDIR, 'p%d.jpg' % p)
        c = R.comp_table(path)
        h = c['y1'] - c['y0']; w = c['x1'] - c['x0']
        vine = np.where((h > 300) & (w < 300))[0]
        if len(vine):
            k = vine[np.argmax(h[vine])]
            spec.append((p, 'vine-margin', (int(c['x0'][k]), int(c['x1'][k]),
                                            int(c['y0'][k]), int(c['y1'][k]))))

    for p, kind, bx in spec:
        path = os.path.join(IMGDIR, 'p%d.jpg' % p)
        g, k, nr, dg, call, mc = read_band_box(path, bx, tmpl, mapping)
        res['specificity'].append(dict(page=p, kind=kind, box=list(bx),
                                       n_glyphs=len(g), call=call,
                                       degeneracy=round(dg, 3),
                                       medcost=None if mc is None else round(mc, 1),
                                       read=''.join(IDX_TO_TRANS[v] if v >= 0 else '?'
                                                    for v in g)[:40]))
        print('SPEC p%-2d %-13s %-11s glyphs %3d deg %.2f cost %s'
              % (p, kind, call, len(g), dg, mc), flush=True)

    # ---------------------------------------------------------------- headline stats
    def pool(rows):
        m = sum(r['matched'] for r in rows)
        n = sum(r['n_read'] for r in rows)
        return dict(matched=m, glyphs_read=n, precision_pct=round(100.0 * m / max(n, 1), 2),
                    n_bands=len(rows))

    S = res['sensitivity']
    P = res['pages']
    lp2 = [r for r in S if r['era'] == 'LP2']
    lp1 = [r for r in S if r['era'] == 'LP1']
    short = [r for r in S if 0 < r['n_read'] <= 16]
    short_lp2 = [r for r in short if r['era'] == 'LP2']
    verbatim = [r for r in S if r['n_read'] > 0 and r['precision'] >= 99.99]

    tot_m = sum(p['matched'] for p in P)
    tot_read = sum(p['glyphs_read'] for p in P)
    tot_canon = sum(p['canon_runes'] for p in P)
    lp2p = [p for p in P if p['era'] == 'LP2']

    res['headline'] = dict(
        gate='G-A2 (band-shaped)', bar_pct=90.0,
        n_control_bands=len(S),
        pooled_agreement_pct=round(100.0 * tot_m / max(tot_read, tot_canon, 1), 2),
        pooled_precision_pct=round(100.0 * tot_m / max(tot_read, 1), 2),
        LP2_agreement_pct=round(100.0 * sum(p['matched'] for p in lp2p)
                                / max(sum(p['glyphs_read'] for p in lp2p),
                                      sum(p['canon_runes'] for p in lp2p), 1), 2),
        all_bands=pool(S), LP2_typeface=pool(lp2), LP1_typeface=pool(lp1),
        short_bands_read_le_16=pool(short), short_bands_LP2=pool(short_lp2),
        n_bands_verbatim=len(verbatim),
        frac_bands_verbatim=round(len(verbatim) / max(len(S), 1), 3),
        sensitivity_called_RUNIC=round(
            sum(1 for r in S if r['call'] == 'RUNIC') / max(len(S), 1), 3),
        specificity_not_called_RUNIC=round(
            sum(1 for r in res['specificity'] if r['call'] != 'RUNIC')
            / max(len(res['specificity']), 1), 3),
        n_specificity_probes=len(res['specificity']),
        specificity_RUNIC_probes=[dict(page=r['page'], kind=r['kind'], n=r['n_glyphs'],
                                       read=r['read'])
                                  for r in res['specificity'] if r['call'] == 'RUNIC'])
    res['headline']['gate_result'] = (
        'PASS' if res['headline']['pooled_agreement_pct'] >= 90.0 else 'FAIL')

    json.dump(res, open(os.path.join(HERE, 'band_control.json'), 'w'), indent=1)
    print('\n=== GATE G-A2 (band-shaped control) ===')
    for k, v in res['headline'].items():
        print('  %-28s %s' % (k, v))


if __name__ == '__main__':
    main()
