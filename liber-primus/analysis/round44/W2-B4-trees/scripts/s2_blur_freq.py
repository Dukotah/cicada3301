"""S2 (v2, PREREG addendum 2): PC2 blur-type plants + frequency-domain characterization of the
real p32 tree blur by parametric model comparison.

Model: P(fy,fx) = A * f^-alpha * |H(f)|^2 + floor, fit on the 2D power spectrum (coarse grid,
0.015 <= f <= 0.35) in log domain; H in {Gaussian sigma, disk r, motion (L, theta)}.
Class = argmin SSE over {gaussian, disk, motion}; param = argmin within class.
"""
import json, os, sys
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imglib as L

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def power_spectrum(img):
    a = img - img.mean()
    wy = np.hanning(a.shape[0])[:, None]
    wx = np.hanning(a.shape[1])[None, :]
    F = np.fft.fft2(a * wy * wx)
    P = np.abs(F) ** 2
    h, w = P.shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    return P, fy, fx


def H2_of(psf, shape):
    H = np.fft.fft2(psf, shape)
    return np.abs(H) ** 2


def sample_grid(P, fy, fx, step=6, flo=0.015, fhi=0.35):
    f = np.sqrt(fy ** 2 + fx ** 2)
    m = (f >= flo) & (f <= fhi)
    m[::1, :] &= False  # placeholder, replaced below
    # coarse subsample
    sel = np.zeros_like(m)
    sel[::step, ::step] = True
    m = (f >= flo) & (f <= fhi) & sel
    return m, f


def fit_sse(P, f, H2, mask):
    """Fit lnP = ln(A f^-alpha H2 + floor) over mask; return SSE."""
    lp = np.log(P[mask] + 1e-20)
    lf = np.log(f[mask])
    lh = np.log(H2[mask] + 1e-20)
    floor0 = np.median(P[mask][lh < lh.max() - 20]) if (lh < lh.max() - 20).sum() > 50 else np.percentile(P[mask], 5)
    floor0 = max(floor0, 1e-12)

    def nll(th):
        lnA, alpha, lnfloor = th
        model = np.log(np.exp(lnA - alpha * lf + lh) + np.exp(lnfloor))
        return ((lp - model) ** 2).mean()

    best = None
    for a0 in (1.5, 2.5):
        r = minimize(nll, [lp.max(), a0, np.log(floor0)], method='Nelder-Mead',
                     options={'maxiter': 400, 'xatol': 1e-3, 'fatol': 1e-5})
        if best is None or r.fun < best.fun:
            best = r
    return float(best.fun), [float(x) for x in best.x]


def classify(crop, tag=''):
    P, fy, fx = power_spectrum(crop)
    mask, f = sample_grid(P, fy, fx)
    sh = P.shape
    results = {'gaussian': [], 'disk': [], 'motion': []}
    for s in range(1, 31):
        sse, th = fit_sse(P, f, H2_of(L.psf_gauss(s), sh), mask)
        results['gaussian'].append({'param': {'sigma': s}, 'sse': sse})
    for r_ in range(1, 31):
        sse, th = fit_sse(P, f, H2_of(L.psf_disk(r_), sh), mask)
        results['disk'].append({'param': {'r': r_}, 'sse': sse})
    Ls = (3, 5, 8, 10, 14, 20, 28, 40)
    for Lm in Ls:
        for ang in np.arange(0, 180, 7.5):
            sse, th = fit_sse(P, f, H2_of(L.psf_motion(Lm, ang), sh), mask)
            results['motion'].append({'param': {'L': Lm, 'theta': float(ang)}, 'sse': sse})
    # refinement around the best coarse motion candidate (angle +/-7.5 in 2.5 steps, dense L)
    b = min(results['motion'], key=lambda d: d['sse'])['param']
    for Lm in (3, 4, 5, 6, 8, 10, 12, 14, 17, 20, 24, 28, 34, 40):
        for ang in np.arange(b['theta'] - 7.5, b['theta'] + 7.6, 2.5):
            sse, th = fit_sse(P, f, H2_of(L.psf_motion(Lm, ang % 180), sh), mask)
            results['motion'].append({'param': {'L': Lm, 'theta': float(ang % 180)}, 'sse': sse})
    summary = {}
    for k, v in results.items():
        b = min(v, key=lambda d: d['sse'])
        summary[k] = {'best_param': b['param'], 'sse': round(b['sse'], 4)}
    label = min(summary, key=lambda k: summary[k]['sse'])
    print(f'  [{tag}] ->', label, summary)
    return {'label': label, 'per_class': summary}


if __name__ == '__main__':
    out = {}
    runesY = L.crop(L.loadY(L.PATHS['p32_relikd']), L.P32_RUNES)
    # ---- PC2 plants ----
    plants = {
        'gauss8': (L.blur_with(runesY, L.psf_gauss(8)), 'gaussian', {'sigma': 8}),
        'disk8': (L.blur_with(runesY, L.psf_disk(8)), 'disk', {'r': 8}),
        'motion20_30': (L.blur_with(runesY, L.psf_motion(20, 30)), 'motion', {'L': 20, 'theta': 30}),
    }
    pc2, ok = {}, True
    for k, (img, exp_label, exp_param) in plants.items():
        r = classify(img, tag='PC2 ' + k)
        r['expected'] = exp_label
        good = r['label'] == exp_label
        if good:
            bp = r['per_class'][exp_label]['best_param']
            for pk, pv in exp_param.items():
                if pk == 'theta':
                    d = abs((bp[pk] - pv + 90) % 180 - 90)
                    good &= d <= 15
                else:
                    good &= abs(bp[pk] - pv) <= 0.25 * pv
        r['correct'] = bool(good)
        ok &= good
        pc2[k] = r
    out['PC2'] = pc2
    out['PC2_passed'] = bool(ok)
    assert ok, 'POSITIVE CONTROL PC2 FAILED - stop'

    # ---- real target ----
    tree = L.crop(L.loadY(L.PATHS['p32_relikd']), L.P32_TREE)
    real = classify(tree, tag='REAL p32 tree')
    out['real_p32_tree'] = real
    json.dump(out, open(os.path.join(HERE, 'results', 'blur_freq.json'), 'w'), indent=1)
    print('REAL:', json.dumps(real, indent=1))
