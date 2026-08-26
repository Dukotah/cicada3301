"""T2 -- score a probe output.

C1  loo_agreement on the two SOLVED LP2 pages (ground truth by decryption).
C2  analytic plant recall == loo_agreement per stratum (PREREG §2 C2).
C3  flag threshold tau from the solved-page false-positive rate.

usage: python3 score.py out_probe_solved.json [--strata]
"""
import os
import sys
import json
import collections
import numpy as np
import t2lib as T
from lp.gematria import IDX_TO_TRANS

CONF_FAMILIES = [
    {1, 26},                    # U <-> Y
    {3, 24, 25},                # O / A / AE
    {20, 7},                    # L <-> W
    {5, 10},                    # C <-> I
]


def is_conf(a, b):
    return any(a in f and b in f for f in CONF_FAMILIES)


def load(fn):
    return json.load(open(os.path.join(T.HERE, fn)))


def stratum(rec):
    seg = rec.get('seg')
    if seg in (55, 56):
        return 'solved-LP2'
    if seg is not None and 45 <= seg <= 54:
        return 'dense-45-54'
    return 'pages-0-44'


def score(res, label=''):
    per = collections.defaultdict(lambda: dict(n=0, hit=0, lines=0, fails=0,
                                               deltas=[], conf=0, resid=[]))
    fails = collections.Counter()
    for rec in res:
        if 'fail' in rec:
            fails[rec['fail']] += 1
            continue
        s = stratum(rec)
        d = per[s]
        d['lines'] += 1
        d['resid'].append(rec['total'] / max(len(rec['canon']), 1))
        for j, c in enumerate(rec['canon']):
            d['n'] += 1
            b = rec['best'][j]
            if b == c:
                d['hit'] += 1
            else:
                if is_conf(b, c):
                    d['conf'] += 1
            d['deltas'].append(rec['canon_cost'][j] - rec['best_cost'][j])
    print('\n=== %s ===' % label)
    if fails:
        print('line failures:', dict(fails))
    for s in sorted(per):
        d = per[s]
        agr = d['hit'] / max(d['n'], 1)
        print('%-12s lines %4d  slots %6d  loo_agreement %.4f   '
              'non-canon-in-confusable-family %d (%.2f%% of slots)  '
              'median line residual/token %.1f'
              % (s, d['lines'], d['n'], agr, d['conf'],
                 100.0 * d['conf'] / max(d['n'], 1), float(np.median(d['resid']))))
    return per


def main():
    fn = sys.argv[1]
    res = load(fn)
    per = score(res, fn)
    # C3: tau from solved pages
    if 'solved-LP2' in per:
        d = np.array(per['solved-LP2']['deltas'])
        n = len(d)
        for q in (0.90, 0.95, 0.99, 0.995, 1.0):
            print('  solved-page delta quantile %.3f = %.1f' % (q, np.quantile(d, q)))
        print('  slots with delta > 0 on solved pages: %d/%d (%.2f%%)'
              % (int((d > 0).sum()), n, 100.0 * (d > 0).mean()))
    # confusion table
    cm = collections.Counter()
    for rec in res:
        if 'fail' in rec:
            continue
        for j, c in enumerate(rec['canon']):
            b = rec['best'][j]
            if b != c:
                cm[(IDX_TO_TRANS[b], IDX_TO_TRANS[c])] += 1
    print('\ntop probe->canon disagreements:')
    for (a, b), k in cm.most_common(20):
        print('   %-4s -> %-4s  %d' % (a, b, k))


if __name__ == '__main__':
    main()
