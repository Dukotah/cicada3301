"""A2 real-page sub-pixel analysis.

For every glyph the retranscribe DP placed, cut its cell out of the page image,
compute the ink-mass centroid to sub-pixel precision, and study three channels:

  1. BASELINE OFFSET  : glyph cy relative to a per-line fitted baseline
  2. ADVANCE / KERN   : gap between consecutive glyph x-starts (grid pitch)
  3. X/Y JITTER        : centroid vs fitted-grid position within a line

For each we ask: uniform (rendering, null) / gaussian noise / STRUCTURED
(bimodal => candidate binary channel). Bimodality tested by dip statistic
proxy (Hartigan-ish: compare best 2-gaussian fit vs 1-gaussian via BIC) and by
kurtosis/gap. If a channel is bimodal we emit the per-glyph bits and hand off
to a bitstream tester.

Everything is compared to the empirical NOISE FLOOR measured on the SAME real
glyphs: the within-class centroid scatter of runes we KNOW are the same shape
placed on the same nominal grid -- that scatter is rendering+JPEG+segmentation
noise, our null.
"""
import os, sys, json, collections
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure as M

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
IMG = os.path.join(ROOT, 'data', 'relikd')
GEO = os.path.join(ROOT, 'analysis', 'geometry', 'glyphs2.npz')
READ = os.path.join(ROOT, 'analysis', 'retranscribe', 'read_lines.json')

FILLER_CLASS = 11          # separator/filler class (excluded from rune stats)
REAL_MIN_COUNT = 100       # only classes that are real font shapes


def load():
    d = np.load(GEO)
    bands = d['bands']       # page,ys,ye,nglyph,medh
    lines = json.load(open(READ))
    return bands, lines


def page_cache():
    cache = {}
    def get(p):
        if p not in cache:
            im = Image.open(os.path.join(IMG, f'p{p}.jpg')).convert('L')
            cache[p] = M.to_ink(np.asarray(im))
        return cache[p]
    return get


def main():
    bands, lines = load()
    getpage = page_cache()

    # index band by (page,band)
    band_by = {(int(b[0]), i): b for i, b in enumerate(_page_local(bands))}
    # Actually bands are global rows; map via order per page
    # Reconstruct: bands array order matches read_lines order (both 646). Verify.
    assert len(bands) == len(lines), (len(bands), len(lines))

    records = []   # per glyph: page,line,class,x_start,cell_w,cx,cy,mass,ys,ye
    for i, ln in enumerate(lines):
        b = bands[i]
        page, ys, ye = int(b[0]), int(b[1]), int(b[2])
        assert page == ln['page']
        ink = getpage(page)
        gl = ln['glyphs']
        # glyph cell = [x_start, next_x_start)
        for j, (cid, xs, cost) in enumerate(gl):
            xs = int(round(xs))
            xe = int(round(gl[j + 1][1])) if j + 1 < len(gl) else xs + 60
            cw = xe - xs
            if cw < 8 or cw > 400:
                continue
            res = M.centroid(ink, xs, ys, min(xe, ink.shape[1]), ye)
            if res is None:
                continue
            cx, cy, mass = res
            records.append(dict(page=page, line=i, cls=int(cid), xs=xs, xe=xe,
                                cw=cw, cx=cx, cy=cy, mass=mass, ys=ys, ye=ye))

    # class counts
    cc = collections.Counter(r['cls'] for r in records)
    real_classes = {c for c, n in cc.items() if n >= REAL_MIN_COUNT and c != FILLER_CLASS}

    analyze(records, real_classes, cc)


def _page_local(bands):
    return bands


def bimodality(x):
    """Return dict: 1-gauss vs 2-gauss BIC, and a normalized gap statistic.
    Positive delta_bic (bic1 - bic2 > 10) => 2-component wins => bimodal."""
    x = np.asarray(x, float)
    n = len(x)
    if n < 30:
        return None
    x = x - x.mean()
    # 1-gaussian loglik
    s1 = x.std() + 1e-9
    ll1 = -0.5 * n * np.log(2 * np.pi * s1**2) - 0.5 * ((x / s1)**2).sum()
    bic1 = -2 * ll1 + 2 * np.log(n)
    # 2-gaussian EM
    ll2, mus, sds, ws = em2(x)
    bic2 = -2 * ll2 + 5 * np.log(n)  # 5 free params
    return dict(delta_bic=float(bic1 - bic2), mus=[float(m) for m in mus],
                sds=[float(s) for s in sds], ws=[float(w) for w in ws],
                sep=float(abs(mus[1] - mus[0])),
                sep_over_sd=float(abs(mus[1] - mus[0]) / (np.mean(sds) + 1e-9)),
                n=n)


def em2(x, iters=200):
    lo, hi = np.percentile(x, [25, 75])
    mus = np.array([lo, hi], float)
    sds = np.array([x.std(), x.std()], float) + 1e-6
    ws = np.array([0.5, 0.5])
    for _ in range(iters):
        p = np.stack([ws[k] * gauss(x, mus[k], sds[k]) for k in range(2)])
        p_sum = p.sum(0) + 1e-30
        resp = p / p_sum
        Nk = resp.sum(1) + 1e-9
        ws = Nk / len(x)
        mus = (resp * x).sum(1) / Nk
        sds = np.sqrt((resp * (x - mus[:, None])**2).sum(1) / Nk) + 1e-6
    p = np.stack([ws[k] * gauss(x, mus[k], sds[k]) for k in range(2)])
    ll = np.log(p.sum(0) + 1e-30).sum()
    order = np.argsort(mus)
    return ll, mus[order], sds[order], ws[order]


def gauss(x, m, s):
    return np.exp(-0.5 * ((x - m) / s)**2) / (s * np.sqrt(2 * np.pi))


def analyze(records, real_classes, cc):
    out = {'n_glyphs': len(records), 'n_real_classes': len(real_classes),
           'class_counts': {str(k): v for k, v in sorted(cc.items())}}

    # ---- NOISE FLOOR from within-class centroid scatter ----
    # For each rune class, cx-mean-of-class already removed; residual x/y scatter
    # after removing per-line grid is our noise. First fit per-line advance grid.

    by_line = collections.defaultdict(list)
    for r in records:
        by_line[r['line']].append(r)

    # CHANNEL 2: advance/pitch = diff of consecutive centroid-x within a line
    advances = []
    baseline_res = []   # cy - line baseline (mass-weighted mean cy of line)
    xjit = []           # cx - nearest grid node
    for line, rs in by_line.items():
        rs = sorted(rs, key=lambda r: r['xs'])
        cxs = np.array([r['cx'] for r in rs])
        cys = np.array([r['cy'] for r in rs])
        if len(cxs) < 4:
            continue
        # baseline: robust mean cy of line (glyphs share a baseline in this font)
        base = np.median(cys)
        for r, cy in zip(rs, cys):
            baseline_res.append((r['cls'], cy - base))
        # advance
        d = np.diff(cxs)
        for a in d:
            advances.append(a)
        # x-grid: fit pitch via median advance, then residual of each glyph to
        # the best integer-multiple lattice anchored at first glyph
        med = np.median(d[d > 5]) if np.any(d > 5) else np.median(d)
        if med <= 0:
            continue
        anchor = cxs[0]
        for cx in cxs:
            k = round((cx - anchor) / med)
            xjit.append(cx - (anchor + k * med))

    baseline_arr = np.array([b for _, b in baseline_res])
    out['channel_baseline'] = summ(baseline_arr, 'baseline_offset_px')
    bm = bimodality(baseline_arr)
    out['channel_baseline']['bimodality'] = bm

    adv = np.array(advances)
    adv = adv[(adv > 5) & (adv < 200)]   # drop word-gaps and merges
    out['channel_advance'] = summ(adv, 'advance_px')
    out['channel_advance']['bimodality'] = bimodality(adv)

    xj = np.array(xjit)
    xj = xj[np.abs(xj) < 40]
    out['channel_xjitter'] = summ(xj, 'xgrid_residual_px')
    out['channel_xjitter']['bimodality'] = bimodality(xj)

    # ---- per-CLASS baseline offset: does a SPECIFIC rune shift bimodally? ----
    # (a positional channel could be keyed per-repeated-glyph)
    per_class = {}
    cls_base = collections.defaultdict(list)
    for cls, b in baseline_res:
        cls_base[cls].append(b)
    for cls in sorted(real_classes):
        arr = np.array(cls_base[cls])
        if len(arr) < 60:
            continue
        arr = arr - np.median(arr)
        bm = bimodality(arr)
        per_class[str(cls)] = dict(n=len(arr), std=float(arr.std()),
                                   bimodality=bm)
    out['per_class_baseline'] = per_class

    # NOISE FLOOR = median within-class std of baseline residual
    stds = [v['std'] for v in per_class.values()]
    out['noise_floor_baseline_px'] = float(np.median(stds)) if stds else None

    with open(os.path.join(HERE, 'realpage_results.json'), 'w') as f:
        json.dump(out, f, indent=2)

    # console summary
    print('glyphs measured:', out['n_glyphs'], 'real classes:', out['n_real_classes'])
    print('NOISE FLOOR (within-class baseline std):', out['noise_floor_baseline_px'], 'px')
    for ch in ['channel_baseline', 'channel_advance', 'channel_xjitter']:
        c = out[ch]
        bm = c['bimodality']
        print(f"{ch}: mean={c['mean']:.3f} std={c['std']:.3f} "
              f"deltaBIC={bm['delta_bic']:.1f} sep/sd={bm['sep_over_sd']:.2f}")
    # flag any per-class bimodal
    flagged = [(k, v['bimodality']['delta_bic'], v['bimodality']['sep_over_sd'])
               for k, v in per_class.items()
               if v['bimodality'] and v['bimodality']['delta_bic'] > 10
               and v['bimodality']['sep_over_sd'] > 2]
    print('per-class bimodal flags (deltaBIC>10 & sep/sd>2):', flagged)
    return out


def summ(a, name):
    a = np.asarray(a, float)
    return dict(name=name, n=int(len(a)), mean=float(a.mean()), std=float(a.std()),
                min=float(a.min()), max=float(a.max()),
                p05=float(np.percentile(a, 5)), p50=float(np.percentile(a, 50)),
                p95=float(np.percentile(a, 95)),
                kurtosis=float(kurt(a)))


def kurt(a):
    a = a - a.mean(); s = a.std()
    return float((a**4).mean() / (s**4 + 1e-12) - 3) if s > 0 else 0.0


if __name__ == '__main__':
    main()
