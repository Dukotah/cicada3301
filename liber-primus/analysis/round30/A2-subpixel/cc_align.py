"""A2 cleanest sub-pixel test: native-res, per-shape, using CC boxes.

The connected-component boxes (geometry x0,y0,x1,y1) precisely bound each ink
blob. For runes that are a single un-merged component (the majority), the box
IS the glyph. We:
  1. Cut each CC at native res from p*.jpg with a fixed margin.
  2. Cluster CCs into shape classes by correlating against the retranscribe
     templates is overkill; instead we cluster by (w,h) THEN refine: within a
     coarse size bin, keep only boxes whose bitmap correlates >0.9 with the bin
     medoid -> a pure single-shape set.
  3. Sub-pixel register each to the medoid; dx=horizontal micro-pos, dy=vertical.
     The box top-left is integer; the glyph's sub-pixel offset within it is what
     we recover. Crucially we align to the BOX, so cell-placement error is gone.

We separate:
  - box_x0 fractional part is meaningless (integer pixels), BUT
  - the glyph centroid RELATIVE to box gives sub-pixel position; and the box
    left edge relative to the line's glyph pitch gives the advance channel.

Two honest channels:
  A) intra-box centroid (dx,dy): pure rendering micro-position of a fixed shape.
  B) advance residual: box_x0 minus fitted per-line lattice (kerning channel).
"""
import os, sys, json, collections
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure as M
from realfloor import parabolic_peak, bimodality

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
IMG = os.path.join(ROOT, 'data', 'relikd')
GEO = os.path.join(ROOT, 'analysis', 'geometry', 'glyphs2.npz')
MARGIN = 10


def run():
    d = np.load(GEO)
    page, line, x0, y0, x1, y1, area = (d['page'], d['line'], d['x0'], d['y0'],
                                        d['x1'], d['y1'], d['area'])
    w = x1 - x0; h = y1 - y0
    # focus on full-height single runes (h ~ 110-118) to avoid diacritics/dots
    mask = (h >= 108) & (h <= 120) & (w >= 24) & (w <= 60)
    idx = np.where(mask)[0]

    pages = {}
    def get(p):
        if p not in pages:
            pages[p] = M.to_ink(np.asarray(Image.open(os.path.join(IMG, f'p{p}.jpg')).convert('L')))
        return pages[p]

    # coarse size bins
    binkey = list(zip((np.round(w[idx]/6)*6).astype(int), np.full(len(idx), 114)))
    bins = collections.defaultdict(list)
    for k, i in zip(binkey, idx):
        bins[k].append(int(i))

    out = {'bins': {}}
    floors_dx = []; floors_dy = []; adv_floors = []
    struct_flags = []

    for (bw, bh), ids in sorted(bins.items(), key=lambda kv: -len(kv[1])):
        if len(ids) < 120:
            continue
        # fixed native canvas from box center
        CW, CH = bw + 2*MARGIN + 20, 140
        crops = []; keep_ids = []
        for i in ids[:800]:
            p = int(page[i])
            ink = get(p)
            cx = 0.5*(x0[i]+x1[i]); cy = 0.5*(y0[i]+y1[i])
            ax0 = int(round(cx - CW/2)); ay0 = int(round(cy - CH/2))
            if ax0 < 0 or ay0 < 0 or ax0+CW > ink.shape[1] or ay0+CH > ink.shape[0]:
                continue
            crops.append(ink[ay0:ay0+CH, ax0:ax0+CW].astype(np.float32))
            keep_ids.append(i)
        if len(crops) < 120:
            continue
        crops = np.array(crops)
        medoid = np.median(crops, 0)
        T = medoid - medoid.mean()
        Tn = np.sqrt((T*T).sum())+1e-9
        dxs=[]; dys=[]; corrs=[]
        for c in crops:
            im = c - c.mean()
            cc = fftconvolve(im, T[::-1,::-1], mode='same')
            cy, cx = parabolic_peak(cc)
            dys.append(cy - cc.shape[0]//2); dxs.append(cx - cc.shape[1]//2)
            # normalized peak corr as purity
            corrs.append(cc.max()/((np.sqrt((im*im).sum())+1e-9)*Tn))
        dxs=np.array(dxs); dys=np.array(dys); corrs=np.array(corrs)
        # purity filter: keep high-correlation (same shape) instances
        pth = np.percentile(corrs, 40)
        pure = corrs >= pth
        dxp, dyp = dxs[pure], dys[pure]
        def clip(a):
            m,s=np.median(a),np.std(a); return a[np.abs(a-m)<3.5*s+1e-9]
        dxp, dyp = clip(dxp), clip(dyp)
        bx, by = bimodality(dxp), bimodality(dyp)
        rec = dict(n_raw=len(ids), n_used=int(pure.sum()),
                   dx_std=float(dxp.std()), dy_std=float(dyp.std()),
                   dx_bimod=bx, dy_bimod=by)
        out['bins'][f'{bw}px'] = rec
        floors_dx.append(float(dxp.std())); floors_dy.append(float(dyp.std()))
        for ax, bm in (('dx', bx), ('dy', by)):
            if bm and bm['delta_bic'] > 10 and bm['sep_over_sd'] > 2 and bm['sep'] > 0.3:
                struct_flags.append(dict(bin=f'{bw}px', axis=ax, **{k: bm[k] for k in ('sep','sep_over_sd','delta_bic')}))

    out['noise_floor_dx_px'] = float(np.median(floors_dx)) if floors_dx else None
    out['noise_floor_dy_px'] = float(np.median(floors_dy)) if floors_dy else None
    out['structured_flags'] = struct_flags
    with open(os.path.join(HERE, 'cc_align_results.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print(f"NATIVE-CC noise floor dx={out['noise_floor_dx_px']}, dy={out['noise_floor_dy_px']}")
    for k, v in out['bins'].items():
        bx, by = v['dx_bimod'], v['dy_bimod']
        print(f"bin {k:>6} n={v['n_used']:3d} dx_std={v['dx_std']:.3f} dy_std={v['dy_std']:.3f} "
              f"dx(sep={bx['sep']:.3f}/{bx['sep_over_sd']:.2f}) dy(sep={by['sep']:.3f}/{by['sep_over_sd']:.2f})")
    print('STRUCTURED FLAGS:', struct_flags)
    return out


if __name__ == '__main__':
    run()
