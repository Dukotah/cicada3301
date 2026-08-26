"""C3 / L3 -- stratify gate G-A2 by the reader's OWN pre-existing RUNIC/NON-RUNIC call.

Why this is not a post-hoc cut fished to flatter the instrument, and where it IS post-hoc,
stated plainly:

  * The stratifying variable is NOT invented here. `read_bands.py` (Round 18, written before
    any band was read) assigns every band a `call` of RUNIC / DEGENERATE / NON-RUNIC / EMPTY
    from `cost_median <= 300` and `degeneracy < 0.60`. Those two constants were fixed in
    Round 18. Nothing about the rule is chosen after seeing C3's results.
  * What IS post-hoc is the DECISION TO REPORT ALONG THIS AXIS. That is disclosed. The
    unstratified pooled number stays the headline gate figure and is not replaced.

The question this answers is the one the lane actually needs: not "how accurate is the
reader on average" but **"when the reader says a short band is runes, how often is it right,
and how good is the read?"** -- because that is the only condition under which this lane is
permitted to quote a band's content.

Reads `band_control.json`; writes `control_strata.json`.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))


def pool(rows):
    m = sum(r['matched'] for r in rows)
    n = sum(r['n_read'] for r in rows)
    return dict(n_bands=len(rows), glyphs_read=n, matched=m,
                precision_pct=round(100.0 * m / max(n, 1), 2))


def main():
    d = json.load(open(os.path.join(HERE, 'band_control.json')))
    S = [r for r in d['sensitivity'] if r['n_read'] > 0]
    SP = d['specificity']
    out = dict()

    # ---- 1. stratified by the reader's own call, all sizes
    out['by_call'] = {c: pool([r for r in S if r['call'] == c])
                      for c in ('RUNIC', 'NON-RUNIC', 'DEGENERATE')}

    # ---- 2. the band size P-9 actually nominated
    short = [r for r in S if r['n_read'] <= 16]
    out['short_le16'] = dict(
        all=pool(short),
        RUNIC=pool([r for r in short if r['call'] == 'RUNIC']),
        not_RUNIC=pool([r for r in short if r['call'] != 'RUNIC']))

    # ---- 3. the two-sided table for SHORT objects: does a RUNIC call mean anything?
    short_spec = [r for r in SP if 0 < r['n_glyphs'] <= 16]
    tp = len([r for r in short if r['call'] == 'RUNIC'])
    fn = len([r for r in short if r['call'] != 'RUNIC'])
    fp = len([r for r in short_spec if r['call'] == 'RUNIC'])
    tn = len([r for r in short_spec if r['call'] != 'RUNIC'])
    out['short_confusion'] = dict(
        note=('rows = ground truth (known rune ink vs known non-rune ink), '
              'columns = the reader RUNIC call. Objects of <= 16 glyphs only.'),
        true_rune_called_RUNIC=tp, true_rune_called_other=fn,
        non_rune_called_RUNIC=fp, non_rune_called_other=tn,
        sensitivity=round(tp / max(tp + fn, 1), 3),
        specificity=round(tn / max(tn + fp, 1), 3),
        positive_predictive_value=round(tp / max(tp + fp, 1), 3),
        n_non_rune_probes_le16=len(short_spec))

    # ---- 4. all sizes, same table
    tpA = len([r for r in S if r['call'] == 'RUNIC'])
    fnA = len([r for r in S if r['call'] != 'RUNIC'])
    fpA = len([r for r in SP if r['call'] == 'RUNIC'])
    tnA = len([r for r in SP if r['call'] != 'RUNIC'])
    out['all_sizes_confusion'] = dict(
        true_rune_called_RUNIC=tpA, true_rune_called_other=fnA,
        non_rune_called_RUNIC=fpA, non_rune_called_other=tnA,
        sensitivity=round(tpA / max(tpA + fnA, 1), 3),
        specificity=round(tnA / max(tnA + fpA, 1), 3),
        positive_predictive_value=round(tpA / max(tpA + fpA, 1), 3))

    # ---- 5. the LP2 face -- the typeface of all 56 target pages
    lp2 = [r for r in S if r['era'] == 'LP2']
    out['LP2_face'] = dict(all=pool(lp2),
                           RUNIC=pool([r for r in lp2 if r['call'] == 'RUNIC']))

    # ---- 6. the false-positive probes, listed so they can be inspected by eye
    out['false_positive_probes'] = [r for r in SP if r['call'] == 'RUNIC']

    json.dump(out, open(os.path.join(HERE, 'control_strata.json'), 'w'), indent=1)

    print('=== stratified by the reader\'s own RUNIC call ===')
    for c, v in out['by_call'].items():
        print('  %-11s bands %2d  glyphs %4d  precision %6.2f%%'
              % (c, v['n_bands'], v['glyphs_read'], v['precision_pct']))
    print('\n=== bands of <= 16 glyphs (P-9\'s nominated size) ===')
    for k, v in out['short_le16'].items():
        print('  %-11s bands %2d  glyphs %4d  precision %6.2f%%'
              % (k, v['n_bands'], v['glyphs_read'], v['precision_pct']))
    print('\n=== does a RUNIC call on a SHORT object mean anything? ===')
    cf = out['short_confusion']
    print('  known rune ink : RUNIC %d | other %d' % (cf['true_rune_called_RUNIC'],
                                                      cf['true_rune_called_other']))
    print('  known NON-rune : RUNIC %d | other %d' % (cf['non_rune_called_RUNIC'],
                                                      cf['non_rune_called_other']))
    print('  sensitivity %.3f  specificity %.3f  PPV %.3f'
          % (cf['sensitivity'], cf['specificity'], cf['positive_predictive_value']))
    print('\n=== LP2 typeface (the face of all 56 target pages) ===')
    for k, v in out['LP2_face'].items():
        print('  %-11s bands %2d  glyphs %4d  precision %6.2f%%'
              % (k, v['n_bands'], v['glyphs_read'], v['precision_pct']))
    print('\nwrote control_strata.json')


if __name__ == '__main__':
    main()
