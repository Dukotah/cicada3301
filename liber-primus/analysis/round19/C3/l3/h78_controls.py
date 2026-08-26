"""C3 / L3 -- the controls that decide whether H7's and H8's PASSes mean anything.

`hypotheses.py` returns exactly two PASSes out of H1-H8, and both are suspect for the same
reason: their nulls are drawn from the wrong reference class, so the test would fire on
almost any input. That is the failure doctrine R1 exists to catch -- an unmeasured
instrument converting structure that is present for a boring reason into a "finding".

C-H7c  SET-RANDOMISATION.  H7 asks whether the 109 band lengths favour {1,2,4,8,16,32}.
       `h7_control.py` already showed that six-element decoy sets score p = 1.4e-15
       (Fibonacci), p = 8.9e-22 (triangular) and -- decisively -- p = 1.7e-06 for a set of
       six integers drawn AT RANDOM from 1..32. When a random set clears the family bar by
       two orders of magnitude, the bar is not measuring what it claims to.
       The correct null holds the DATA fixed and randomises the SET: draw 20 000 random
       six-element subsets of the observed length support, count how many of the 109 lengths
       each captures, and ask where the binary ladder falls in that distribution.
       H7 is a finding iff the ladder's percentile beats the family bar. Fixed before running.

C-H8b  DOES THE SAME TEST FIRE ON ORDINARY TEXT?  H8 rejects uniformity of band positions at
       KS p = 8.2e-11 (x). But a page of typeset text is not uniform over the page -- it sits
       in a column. The control is to run the IDENTICAL test on the 616 ordinary text rows in
       `linegeom.json`, which nobody claims carry a covert channel. If ordinary text also
       rejects uniformity, H8's PASS carries no information about the bands, and the
       registered threshold is simply not a discriminating one.
       H8 is a finding iff the bands reject uniformity AND ordinary text does not. Fixed
       before running.

Writes `h78_controls.json`.
"""
import json, os, sys
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402

RNG = np.random.default_rng(3301)
FAMILY_BAR = 0.001 / 6
NDRAW = 20000
LADDER = np.array([1, 2, 4, 8, 16, 32])


def main():
    inv = json.load(open(os.path.join(HERE, 'inventory.json')))
    lens = np.array([b['n'] for b in inv])
    n = len(lens)
    out = {}

    # ------------------------------------------------------------ C-H7c
    support = np.arange(int(lens.min()), int(lens.max()) + 1)
    lad_hits = int(np.isin(lens, LADDER).sum())
    draws = np.empty(NDRAW, int)
    for i in range(NDRAW):
        S = RNG.choice(support, size=len(LADDER), replace=False)
        draws[i] = int(np.isin(lens, S).sum())
    ge = int((draws >= lad_hits).sum())
    p_set = (ge + 1) / (NDRAW + 1)
    out['C_H7c'] = dict(
        method=('null holds the 109 observed lengths fixed and randomises the 6-element '
                'set over the observed length support %d..%d' % (support[0], support[-1])),
        n_draws=NDRAW, ladder_hits=lad_hits,
        random_set_hits_mean=round(float(draws.mean()), 2),
        random_set_hits_sd=round(float(draws.std()), 2),
        random_set_hits_median=int(np.median(draws)),
        random_set_hits_p95=int(np.quantile(draws, 0.95)),
        random_set_hits_max=int(draws.max()),
        n_random_sets_ge_ladder=ge,
        p_value=p_set, family_bar=FAMILY_BAR,
        verdict='PASS' if p_set < FAMILY_BAR else 'FAIL — length enrichment is not specific '
                                                  'to the binary ladder')
    print('--- C-H7c  randomise the SET, hold the data fixed ---')
    print('  binary ladder captures %d of %d band lengths' % (lad_hits, n))
    print('  random 6-element sets  : mean %.2f  sd %.2f  median %d  p95 %d  max %d'
          % (draws.mean(), draws.std(), np.median(draws), np.quantile(draws, 0.95),
             draws.max()))
    print('  sets scoring >= ladder : %d / %d   p = %.4g  (family bar %.3g)'
          % (ge, NDRAW, p_set, FAMILY_BAR))
    print('  -> %s' % out['C_H7c']['verdict'])

    # ------------------------------------------------------------ C-H8b
    px = np.array([(b['x'][0] + b['x'][1]) / 2.0 for b in inv])
    py = np.array([(b['y'][0] + b['y'][1]) / 2.0 for b in inv])

    def ks(v):
        rng = max(np.ptp(v), 1)
        return float(stats.kstest((v - v.min()) / rng, 'uniform').pvalue)

    band_x, band_y = ks(px), ks(py)

    lg = json.load(open(os.path.join(HERE, 'linegeom.json')))
    rows = lg['rows'] if isinstance(lg, dict) and 'rows' in lg else lg
    if isinstance(rows, dict):
        rows = [r for v in rows.values() for r in (v if isinstance(v, list) else [v])]
    tx, ty = [], []
    for r in rows:
        if not isinstance(r, dict):
            continue
        x0 = r.get('x0', r.get('left')); x1 = r.get('x1', r.get('right'))
        y0 = r.get('y0', r.get('top')); y1 = r.get('y1', r.get('bottom'))
        if None in (x0, x1, y0, y1):
            continue
        tx.append((x0 + x1) / 2.0); ty.append((y0 + y1) / 2.0)
    tx, ty = np.array(tx), np.array(ty)
    if len(tx) >= 20:
        text_x, text_y = ks(tx), ks(ty)
    else:
        text_x = text_y = float('nan')

    out['C_H8b'] = dict(
        n_bands=n, n_ordinary_text_rows=int(len(tx)),
        band_ks_x_p=band_x, band_ks_y_p=band_y,
        ordinary_text_ks_x_p=text_x, ordinary_text_ks_y_p=text_y,
        ordinary_text_also_rejects=bool(min(text_x, text_y) < FAMILY_BAR),
        verdict=('PASS' if (min(band_x, band_y) < FAMILY_BAR
                            and not min(text_x, text_y) < FAMILY_BAR)
                 else 'FAIL — the same test rejects uniformity for ordinary text rows, '
                      'so the registered threshold is not discriminating'))
    print('\n--- C-H8b  does the H8 test also fire on ordinary text? ---')
    print('  catalogued bands (n=%d)   KS x p=%.3g  y p=%.3g' % (n, band_x, band_y))
    print('  ordinary text rows (n=%d) KS x p=%.3g  y p=%.3g' % (len(tx), text_x, text_y))
    print('  -> %s' % out['C_H8b']['verdict'])

    json.dump(out, open(os.path.join(HERE, 'h78_controls.json'), 'w'), indent=1)
    print('\nwrote h78_controls.json')


if __name__ == '__main__':
    main()
