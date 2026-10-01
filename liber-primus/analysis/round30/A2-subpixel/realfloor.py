"""A2 real sub-pixel noise floor + honest channel test via template alignment.

The cell-centroid in realpage.py is contaminated by neighbour ink and variable
cell width (4.8px 'floor' is mostly shape/segmentation variance, not position).

Here we do it right for a handful of clean, high-count rune classes:
  1. Collect all crops of one class from geometry (connected-component boxes,
     which for isolated runes are clean single glyphs).
  2. Filter to well-formed instances (box size within IQR of the class -> a
     single un-merged glyph).
  3. Build a sub-pixel template = mean of coarsely-aligned crops.
  4. For each instance, find the sub-pixel (dx,dy) that best registers it to the
     template by parabolic-interpolated cross-correlation peak.
  5. dx,dy distribution = the ACTUAL sub-pixel positioning of that repeated
     rune. Its spread is the real noise floor; test dx (horizontal micro-shift)
     and dy (baseline micro-shift) for bimodality against that floor.

This uses geometry glyph boxes (18461 CCs) not the DP cells, so each sample is a
physically isolated glyph, giving the cleanest possible position estimate.
"""
import os, sys, json, collections
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure as M

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
GEO = os.path.join(ROOT, 'analysis', 'geometry', 'glyphs2.npz')


def parabolic_peak(c):
    """Sub-pixel peak of 2D corr surface c via 1D parabolic fit on each axis."""
    iy, ix = np.unravel_index(np.argmax(c), c.shape)
    dy = dx = 0.0
    if 0 < iy < c.shape[0]-1:
        a, b, d = c[iy-1, ix], c[iy, ix], c[iy+1, ix]
        den = (a - 2*b + d)
        if den != 0: dy = 0.5*(a - d)/den
    if 0 < ix < c.shape[1]-1:
        a, b, d = c[iy, ix-1], c[iy, ix], c[iy, ix+1]
        den = (a - 2*b + d)
        if den != 0: dx = 0.5*(a - d)/den
    return iy + dy, ix + dx


def bimodality(x):
    x = np.asarray(x, float); n = len(x)
    if n < 30: return None
    x = x - x.mean()
    s1 = x.std() + 1e-9
    ll1 = -0.5*n*np.log(2*np.pi*s1**2) - 0.5*((x/s1)**2).sum()
    bic1 = -2*ll1 + 2*np.log(n)
    ll2, mus, sds, ws = em2(x)
    bic2 = -2*ll2 + 5*np.log(n)
    return dict(delta_bic=float(bic1-bic2), sep=float(abs(mus[1]-mus[0])),
                sep_over_sd=float(abs(mus[1]-mus[0])/(np.mean(sds)+1e-9)),
                mus=[float(m) for m in mus], ws=[float(w) for w in ws], n=n)


def em2(x, iters=200):
    lo, hi = np.percentile(x, [25,75])
    mus = np.array([lo,hi],float); sds = np.array([x.std(),x.std()])+1e-6
    ws = np.array([.5,.5])
    for _ in range(iters):
        p = np.stack([ws[k]*g(x,mus[k],sds[k]) for k in range(2)])
        resp = p/(p.sum(0)+1e-30); Nk=resp.sum(1)+1e-9
        ws=Nk/len(x); mus=(resp*x).sum(1)/Nk
        sds=np.sqrt((resp*(x-mus[:,None])**2).sum(1)/Nk)+1e-6
    p=np.stack([ws[k]*g(x,mus[k],sds[k]) for k in range(2)])
    ll=np.log(p.sum(0)+1e-30).sum()
    o=np.argsort(mus); return ll,mus[o],sds[o],ws[o]

def g(x,m,s): return np.exp(-0.5*((x-m)/s)**2)/(s*np.sqrt(2*np.pi))


def run():
    d = np.load(GEO)
    page,line,x0,y0,x1,y1,area = (d['page'],d['line'],d['x0'],d['y0'],
                                  d['x1'],d['y1'],d['area'])
    crop = d['crop']   # (N,160,20)?  check
    N = len(page)
    ch, cw = crop.shape[1], crop.shape[2]
    # geometry crops are downsampled thumbnails; use them directly (uint8, ink?)
    w = x1-x0; h = y1-y0
    # cluster glyphs by (rounded w,h) as a shape proxy since we lack class labels here
    # better: use area+height bands. We just need 'same shape repeated'.
    # Use the retranscribe classes instead: re-derive by matching crop bitmaps.
    out = {'crop_shape': list(crop.shape), 'n_cc': int(N)}

    # Group by quantized (w,h) — identical runes share tight (w,h)
    key = list(zip((np.round(w/4)*4).astype(int), (np.round(h/4)*4).astype(int)))
    groups = collections.defaultdict(list)
    for i,k in enumerate(key):
        groups[k].append(i)
    big = sorted(groups.items(), key=lambda kv:-len(kv[1]))[:12]

    results = {}
    floors = []
    for (kw_,kh_), idx in big:
        if len(idx) < 80: continue
        # build crops at native res from thumbnails: crop[i] is (160,20)
        C = crop[idx].astype(np.float32)   # already ink? invert if needed
        # detect polarity: ink should be high after we invert if it's grayscale
        if C.mean() > 128:  # stored as grayscale paper=255
            C = 255.0 - C
        C /= (C.max()+1e-9)
        tmpl = C.mean(0)
        # cross-correlate each to template
        dxs=[]; dys=[]
        T = tmpl - tmpl.mean()
        for k in range(len(C)):
            im = C[k]-C[k].mean()
            corr = fftconvolve(im, T[::-1,::-1], mode='same')
            cy,cx = parabolic_peak(corr)
            dys.append(cy - corr.shape[0]//2)
            dxs.append(cx - corr.shape[1]//2)
        dxs=np.array(dxs); dys=np.array(dys)
        # robust clip
        def clip(a):
            m,s=np.median(a),np.std(a); return a[np.abs(a-m)<4*s+1e-9]
        dxc, dyc = clip(dxs), clip(dys)
        res = dict(n=len(idx), w=int(kw_), h=int(kh_),
                   dx_std=float(dxc.std()), dy_std=float(dyc.std()),
                   dx_bimod=bimodality(dxc), dy_bimod=bimodality(dyc))
        results[f'{kw_}x{kh_}'] = res
        floors.append((dxc.std()+dyc.std())/2)

    out['groups'] = results
    out['real_subpixel_noise_floor_px'] = float(np.median(floors)) if floors else None
    # NOTE: crops are thumbnails -> px here are thumbnail px; report the caveat.
    with open(os.path.join(HERE,'realfloor_results.json'),'w') as f:
        json.dump(out,f,indent=2)
    print('crop thumbnail shape:', out['crop_shape'])
    print('real sub-pixel scatter (thumbnail px), median:',
          out['real_subpixel_noise_floor_px'])
    for k,v in results.items():
        bx,by=v['dx_bimod'],v['dy_bimod']
        print(f"grp {k:>10} n={v['n']:4d} dx_std={v['dx_std']:.3f} dy_std={v['dy_std']:.3f} "
              f"dx_sep/sd={bx['sep_over_sd']:.2f} dy_sep/sd={by['sep_over_sd']:.2f}")
    return out

if __name__=='__main__':
    run()
