# R45-X1: is "top-5 gap pairs carry 0.29 of r=0.38" (T1 E0) evidence of LOCALISED T7, or a generic property of a
# Pearson lag-1 AC on heavy-tailed (near-exponential) gaps?  Null = 86 sites uniform on the 12,955 adjacencies.
# Also: does the rank AC (Fable52's "distributed" statistic) survive deletion of the 5 top-contributing pairs?
import sys, os, math, json, random
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'T1-t7-mechanism'))
import t1lib as L

def decomp(ev):
    g = np.diff(ev).astype(float); x, y = g[:-1], g[1:]
    cx, cy = x - x.mean(), y - y.mean(); den = math.sqrt((cx**2).sum() * (cy**2).sum())
    c = cx * cy / den; o = np.argsort(-np.abs(c))
    return c.sum(), c[o[:5]].sum(), c.sum() - c[o[:5]].sum(), o[:5], x, y

def rank_r(x, y):
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])

D = L.load(); ev = np.asarray(D['ev']); T = D['T']
r, top, rest, o5, x, y = decomp(ev)
keep = np.setdiff1d(np.arange(len(x)), o5)
obs = dict(r=r, top5=top, without_top5=rest, top5_share=top / r, rank_r_all=rank_r(x, y), rank_r_drop5=rank_r(x[keep], y[keep]),
           pearson_drop5=float(np.corrcoef(x[keep], y[keep])[0, 1]))
rng = np.random.default_rng(4545)
N = 20000; R = []; TOP = []; REST = []; SH = []; RR5 = []; P5 = []
for _ in range(N):
    e = np.sort(rng.choice(T, size=len(ev), replace=False))
    a, b, c, oo, xx, yy = decomp(e); kk = np.setdiff1d(np.arange(len(xx)), oo)
    R.append(a); TOP.append(b); REST.append(c); RR5.append(rank_r(xx[kk], yy[kk])); P5.append(np.corrcoef(xx[kk], yy[kk])[0, 1])
R = np.array(R); TOP = np.array(TOP); REST = np.array(REST); RR5 = np.array(RR5); P5 = np.array(P5)
p = lambda arr, v: float((1 + (arr >= v).sum()) / (len(arr) + 1))
out = dict(observed=obs, null_n=N,
           p_r=p(R, r), p_top5=p(TOP, top), p_without_top5=p(REST, rest), p_rank_drop5=p(RR5, obs['rank_r_drop5']),
           p_pearson_drop5=p(P5, obs['pearson_drop5']),
           null_top5_share_given_r_ge_0p3=float(np.median(TOP[R >= 0.3] / R[R >= 0.3])) if (R >= 0.3).any() else None,
           null_n_r_ge_0p3=int((R >= 0.3).sum()),
           null_median_abs_top5_over_abs_r=float(np.median(np.abs(TOP) / np.maximum(np.abs(R), 1e-9))))
print(json.dumps(out, indent=1, default=float))
json.dump(out, open('x1_t7_concentration.json', 'w'), indent=1, default=float)
