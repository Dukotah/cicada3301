"""C3 / L3 -- H9 verdict, now that the detector passes its own plant.

`intensity2.py` repaired the control (recall 1.000 down to a planted dL of 2 grey levels), so
for the first time the ink-tone channel is measured by a validated instrument. It flags
1 504 components book-wide after the stroke-width-and-height-matched re-test.

1 504 is not a covert channel and it is not "a single anomaly" either -- it is ~8% of all ink
on the page set, and the addendum has a clause for neither. So this script answers the
question that decides which it is:

  **Is being flagged predicted by how the component was RENDERED, or is it unexplained?**

A thin, small, or isolated stroke antialiases lighter in a JPEG; that is physics, not a
message. The test: how well does component geometry alone (area, height, width, stroke-width
proxy, aspect) separate flagged from unflagged components? Reported as AUC per page and
pooled. Fixed before running:

  * AUC >= 0.80  -> the flags are a render artifact. H9 NEGATIVE, and the negative is now
    a real one because the instrument passed its plant.
  * AUC <= 0.60  -> geometry does not explain the flags; they are unexplained and get
    reported as an annotated anomaly list, per the addendum.
  * in between   -> partially explained; report the number and claim nothing.

Also reports the measurement that prompted the whole addendum: the actual grey delta on the
page-15 4x4 numeric grid, where `3299` is set visibly lighter than its fifteen neighbours.

Writes `h9_verdict.json`.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402
from intensity import page_stats                                       # noqa: E402
from intensity2 import detect_robust, robust                           # noqa: E402

IMG = os.path.join(R.LP, 'data', 'relikd')


def auc(scores, labels):
    """Rank AUC; no sklearn dependency."""
    labels = np.asarray(labels).astype(bool)
    if labels.sum() == 0 or (~labels).sum() == 0:
        return float('nan')
    order = np.argsort(scores)
    ranks = np.empty(len(scores), float)
    ranks[order] = np.arange(1, len(scores) + 1)
    n1 = labels.sum(); n0 = (~labels).sum()
    return float((ranks[labels].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def main():  # noqa
    d = json.load(open(os.path.join(HERE, 'intensity2.json')))
    out = dict(control=d['control'], control_verdict=d['control_verdict'],
               smallest_recoverable_dL=d['smallest_recoverable_dL'],
               n_outliers_total=d['n_outliers_total'],
               n_candidates_total=d['n_candidates_total'])

    per_page_auc, pooled_s, pooled_l = [], {k: [] for k in
                                            ('area', 'h', 'w', 'sw', 'aspect')}, []
    n_comp_total = 0
    for p in range(56):
        st = page_stats(os.path.join(IMG, 'p%d.jpg' % p))
        if st is None:
            continue
        keep, cand, mu, sd, nbody = detect_robust(st['mean'], st['h'], st['sw'])
        lab = np.zeros(len(st['h']), bool)
        lab[list(keep)] = True
        n_comp_total += len(lab)
        feats = dict(area=st['area'].astype(float), h=st['h'].astype(float),
                     w=st['w'].astype(float), sw=st['sw'].astype(float),
                     aspect=st['w'].astype(float) / np.maximum(st['h'], 1))
        row = dict(page=p, n=int(len(lab)), n_flagged=int(lab.sum()))
        for k, v in feats.items():
            row['auc_' + k] = round(auc(-v, lab), 3)      # smaller feature -> flagged
            pooled_s[k] += list(v)
        pooled_l += list(lab)
        per_page_auc.append(row)
        del st

    pooled_l = np.array(pooled_l)
    out['n_components_total'] = n_comp_total
    out['flagged_fraction'] = round(float(pooled_l.mean()), 4)
    out['pooled_auc'] = {k: round(auc(-np.array(v), pooled_l), 3)
                         for k, v in pooled_s.items()}
    out['per_page_auc'] = per_page_auc
    best = max(out['pooled_auc'].values())
    out['best_pooled_auc'] = best
    out['best_feature'] = max(out['pooled_auc'], key=out['pooled_auc'].get)
    out['bar'] = dict(render_artifact_at=0.80, unexplained_at=0.60)
    out['H9_verdict'] = ('NEGATIVE — flags are predicted by render geometry' if best >= 0.80
                         else ('UNEXPLAINED — annotated anomaly list, per the addendum'
                               if best <= 0.60 else
                               'PARTIALLY EXPLAINED — reported as a number, no claim'))

    print('components book-wide %d   flagged %.2f%%'
          % (n_comp_total, 100 * out['flagged_fraction']))
    print('pooled AUC of "is flagged" from geometry alone:')
    for k, v in sorted(out['pooled_auc'].items(), key=lambda x: -x[1]):
        print('    %-8s %.3f' % (k, v))
    print('H9 VERDICT: %s' % out['H9_verdict'])

    # ---------------------------------------------------------------- p15 grid
    g = d.get('p15_grid')
    if g:
        out['p15_grid'] = g
        print('\n--- page 15, the 4x4 numeric grid ---')
        print('  digit components %d   median grey %.2f   MAD-sigma %.3f'
              % (g['n_digit_components'], g['median_grey'], g['mad_sigma']))
        for e in g['lightest'][:6]:
            print('    grey %6.2f  z %7.2f  box %s  %dx%d'
                  % (e['mean_grey'], e['z'], e['box'], e['w'], e['h']))
        # how many grey levels is the lightest above the median?
        delta = g['lightest'][0]['mean_grey'] - g['median_grey']
        out['p15_lightest_delta_grey_levels'] = round(float(delta), 2)
        print('  lightest digit component is %.2f grey levels above the digit median'
              % delta)
        print('  (the detector recovers a planted lightening of 2 grey levels at recall '
              '1.000, so a real delta of this size is inside its power envelope)')

    json.dump(out, open(os.path.join(HERE, 'h9_verdict.json'), 'w'), indent=1)
    print('\nwrote h9_verdict.json')


if __name__ == '__main__':
    main()
