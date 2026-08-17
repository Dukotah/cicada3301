"""Diagnostics D1-D4 for the G1 line-initial hit (see PREREG-ADDENDUM-D.md)."""
import os, sys, json
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mapcommon as M
from mapcommon import ng_score, zscore, N
from lp import gematria as gp

OUT = {}
d = M.parse()
W = d['words']
lines = [l for l in d['lines'] if l]
pooled = np.array(M.flat(W))
uni = np.bincount(pooled, minlength=N).astype(float); uni /= uni.sum()


def resid(seq):
    c = np.bincount(np.asarray(seq), minlength=N).astype(float)
    e = uni * len(seq)
    return (c - e) / np.sqrt(e), float(((c - e) ** 2 / e).sum())


li = [l[0] for l in lines]
r_li, x_li = resid(li)

# ------------------------------------------------------------------ D1 ----
A = np.zeros((len(lines), N))
for j, l in enumerate(lines):
    A[j] = np.bincount(np.asarray(l), minlength=N)
w, *_ = np.linalg.lstsq(A, np.ones(len(lines)), rcond=None)
pred = A.dot(w)
# line-length variance explained: compare predicted measure spread to raw count spread
lens = np.array([len(l) for l in lines], float)
cv_len = lens.std() / lens.mean()
cv_measure = pred.std() / pred.mean()

rho, p_rho = stats.pearsonr(w, r_li)
srho, sp = stats.spearmanr(w, r_li)
OUT['D1'] = dict(pearson_r=round(float(rho), 4), pearson_p=float('%.3g' % p_rho),
                 spearman_r=round(float(srho), 4), spearman_p=float('%.3g' % sp),
                 cv_line_runecount=round(float(cv_len), 4),
                 cv_fitted_measure=round(float(cv_measure), 4),
                 threshold='H-type confirmed if r>=+0.50 and p<0.01; rejected if |r|<0.30',
                 verdict=('H-type CONFIRMED' if (rho >= 0.5 and p_rho < 0.01)
                          else ('H-type REJECTED' if abs(rho) < 0.3 else 'INDETERMINATE')))
print('D1 width regression')
print('   coefficient of variation: rune-count per line %.4f -> fitted measure %.4f'
      % (cv_len, cv_measure))
print('   Pearson  r(width, line-initial residual) = %+.4f  p=%.3g' % (rho, p_rho))
print('   Spearman r = %+.4f  p=%.3g' % (srho, sp))
print('   verdict:', OUT['D1']['verdict'])
tab = sorted(range(N), key=lambda i: -w[i])
print('   widest  ->', ' '.join('%s(%.3f,%+.2f)' % (gp.IDX_TO_TRANS[i], w[i], r_li[i]) for i in tab[:6]))
print('   narrowest->', ' '.join('%s(%.3f,%+.2f)' % (gp.IDX_TO_TRANS[i], w[i], r_li[i]) for i in tab[-6:]))
OUT['D1']['widths'] = {gp.IDX_TO_TRANS[i]: round(float(w[i]), 4) for i in range(N)}
OUT['D1']['line_initial_resid'] = {gp.IDX_TO_TRANS[i]: round(float(r_li[i]), 3) for i in range(N)}

# ------------------------------------------------------------------ D2 ----
print('\nD2 positional confinement')
rows = []
for pos, name in ((0, 'pos 0'), (1, 'pos 1'), (2, 'pos 2'), (-1, 'pos -1'),
                  (-2, 'pos -2'), (-3, 'pos -3')):
    seq = [l[pos] for l in lines if len(l) > abs(pos)]
    _, x = resid(seq)
    p = 1 - stats.chi2.cdf(x, N - 1)
    rows.append(dict(pos=name, n=len(seq), chi2=round(x, 2), p=float('%.3g' % p)))
    print('   %-7s n=%4d  chi2=%7.2f  p=%.3g' % (name, len(seq), x, p))
OUT['D2'] = dict(rows=rows,
                 confined=bool(all(r['p'] > 0.01 for r in rows if r['pos'] != 'pos 0')))
print('   confined to pos 0:', OUT['D2']['confined'])

# ------------------------------------------------------------------ D3 ----
def variants(seq):
    for base, bn in ((seq, 'id'), ([N - 1 - x for x in seq], 'atbash')):
        for rv, rn in ((base, 'fwd'), (base[::-1], 'rev')):
            for k in range(N):
                yield f'{bn}/{rn}/+{k}', [(x + k) % N for x in rv]


def best_read(seq):
    b = (-99.0, None)
    for nm, v in variants(seq):
        s = ng_score(v)
        if s > b[0]:
            b = (s, nm)
    return b


lf = [l[-1] for l in lines]
real_li = best_read(li); real_lf = best_read(lf)
nulls = []
for s in range(8):
    nw = M.null_A(W, 1300 + s)
    f2 = M.flat(nw); k = 0; s2 = []
    for l in lines:
        s2.append(f2[k]); k += len(l)
    nulls.append(best_read(s2)[0])
OUT['D3'] = dict(line_initial=dict(best=round(real_li[0], 4), reading=real_li[1]),
                 line_final=dict(best=round(real_lf[0], 4), reading=real_lf[1]),
                 null_mean=round(float(np.mean(nulls)), 4),
                 null_max=round(float(np.max(nulls)), 4),
                 z=round(zscore(real_li[0], nulls), 2),
                 threshold='>= -13.5 and z >= +5',
                 HIT=bool(real_li[0] >= -13.5 and zscore(real_li[0], nulls) >= 5))
print('\nD3 read the line-initial stream (116 variants)')
print('   line-initial best %+8.4f (%s)   null %.4f max %.4f  z=%+.2f' %
      (real_li[0], real_li[1], np.mean(nulls), np.max(nulls), zscore(real_li[0], nulls)))
print('   line-final   best %+8.4f (%s)' % (real_lf[0], real_lf[1]))
print('   HIT =', OUT['D3']['HIT'])
print('   line-initial stream, first 60 runes as translit:')
print('   ', M.translit(li[:60]))

# ------------------------------------------------------------------ D4 ----
d2 = M.parse(max_page=56)
solved_lines = [l for l, p in zip(d2['lines'], d2['line_page']) if p in (55, 56) and l]
if solved_lines:
    seq = [l[0] for l in solved_lines]
    _, x = resid(seq)
    OUT['D4'] = dict(n_lines=len(solved_lines), chi2=round(x, 2),
                     note='descriptive only - n too small to test')
    print('\nD4 solved LP2 pages 55-56: %d lines, chi2=%.2f (descriptive only)'
          % (len(solved_lines), x))

json.dump(OUT, open(os.path.join(HERE, 'diag_lineinit.json'), 'w'), indent=1)
print('\nwrote diag_lineinit.json')
