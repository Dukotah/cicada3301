#!/usr/bin/env python3
"""Render-vs-photo classification via noise-residual statistics.
True camera photos have broadband sensor noise (PRNU) with non-trivial residual energy
and near-white residual spectrum. Digital renders (rasterized vector/text) have
near-zero residual in flat regions, blocky JPEG-only residual, and strongly bimodal
histograms. We compute: residual (img - median-denoise) std, high-freq energy fraction,
fraction of near-flat pixels."""
import sys, os, json, numpy as np
from PIL import Image, ImageFilter

def analyze(path):
    try:
        im = Image.open(path).convert('L')
    except Exception as e:
        return {'file':os.path.basename(path),'error':str(e)}
    a = np.asarray(im, dtype=np.float64)
    # denoise with median 3x3 via PIL
    den = np.asarray(im.filter(ImageFilter.MedianFilter(3)), dtype=np.float64)
    res = a - den
    resid_std = float(res.std())
    # fraction of exactly-flat neighborhoods (residual==0) -> render signature
    flat_frac = float((np.abs(res) < 0.5).mean())
    # high-frequency energy: laplacian variance
    lap = np.abs(np.diff(a,axis=0)[:, :-1]) + np.abs(np.diff(a,axis=1)[:-1, :])
    hf = float(lap.mean())
    # tonal histogram bimodality: fraction of pixels that are pure black or white
    extremes = float(((a<8)|(a>247)).mean())
    return {'file':os.path.basename(path),'resid_std':round(resid_std,3),
            'flat_frac':round(flat_frac,4),'hf_energy':round(hf,3),
            'extreme_frac':round(extremes,4)}

if __name__=='__main__':
    out=[analyze(p) for p in sys.argv[1:]]
    for r in out:
        if 'error' in r: print(r['file'],'ERR',r['error']); continue
        # heuristic verdict
        photo_like = r['resid_std']>2.0 and r['flat_frac']<0.5 and r['extreme_frac']<0.3
        r['verdict']='PHOTO-like' if photo_like else 'RENDER-like'
        print(f"{r['file']:32s} resid_std={r['resid_std']:7} flat={r['flat_frac']:7} hf={r['hf_energy']:7} extreme={r['extreme_frac']:7} -> {r['verdict']}")
    json.dump(out, open('prnu.json','w'), indent=1)
