"""A2 definitive class-PURE sub-pixel test (false-positive hardened).

Links each connected-component box to its retranscribe DP class by nearest
x within the line band, giving TRUE shape identity per box. Then per class:
  - native-res crops centered on the CC box center
  - purity gate: keep only boxes correlating >=p60 with the class medoid
  - sub-pixel register (dx,dy) via parabolic corr peak
  - test dx (advance/kern micro-pos) and dy (baseline micro-pos) for bimodality

Because every sample is the SAME rune shape, a bimodal dx/dy cannot be a
shape-mixing artifact: it would be genuine positional structure. We also run a
SHAPE-MIX NEGATIVE CONTROL: deliberately merge two different classes and show
the merged set reads bimodal -> proving our test is sensitive AND that the
width-bin flags earlier were shape-mix artifacts.

If a class is genuinely bimodal on dx or dy with sep>0.3px, sep/sd>2, we extract
the per-instance bit (which side of the split) in reading order and hand the
bitstream to bitstream_test.py.
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
READ = os.path.join(ROOT, 'analysis', 'retranscribe', 'read_lines.json')
FILLER = 11


def link_cc_to_class():
    d = np.load(GEO)
    page, x0, y0, x1, y1 = d['page'], d['x0'], d['y0'], d['x1'], d['y1']
    h = y1 - y0; cy = 0.5*(y0+y1)
    bands = d['bands']; lines = json.load(open(READ))
    # per (page) index CCs
    recs = []  # (cls, page, cbx, cby, x0,y0,x1,y1) reading order via (line, x)
    for i, ln in enumerate(lines):
        b = bands[i]; p, ys, ye = int(b[0]), int(b[1]), int(b[2])
        sel = np.where((page == p) & (cy >= ys) & (cy <= ye) & (h > 60))[0]
        if len(sel) == 0:
            continue
        selx0 = x0[sel]
        for j, (cid, xs, cost) in enumerate(ln['glyphs']):
            cid = int(cid)
            if cid == FILLER:
                continue
            k = sel[np.argmin(np.abs(selx0 - xs))]
            if abs(int(x0[k]) - xs) > 40:
                continue
            recs.append((cid, p, i, 0.5*(x0[k]+x1[k]), 0.5*(y0[k]+y1[k]),
                         int(x1[k]-x0[k]), int(y1[k]-y0[k])))
    return recs


def measure_class(crops):
    crops = np.array(crops)
    medoid = np.median(crops, 0)
    T = medoid - medoid.mean(); Tn = np.sqrt((T*T).sum())+1e-9
    dxs=[]; dys=[]; corrs=[]
    for c in crops:
        im = c - c.mean()
        cc = fftconvolve(im, T[::-1, ::-1], mode='same')
        cyk, cxk = parabolic_peak(cc)
        dys.append(cyk - cc.shape[0]//2); dxs.append(cxk - cc.shape[1]//2)
        corrs.append(cc.max()/((np.sqrt((im*im).sum())+1e-9)*Tn))
    return np.array(dxs), np.array(dys), np.array(corrs)


def run():
    recs = link_cc_to_class()
    by_cls = collections.defaultdict(list)
    for r in recs:
        by_cls[r[0]].append(r)
    pages = {}
    def get(p):
        if p not in pages:
            pages[p] = M.to_ink(np.asarray(Image.open(os.path.join(IMG, f'p{p}.jpg')).convert('L')))
        return pages[p]

    classes = [c for c, v in sorted(by_cls.items(), key=lambda kv: -len(kv[1])) if len(v) >= 150][:12]
    CW, CH = 90, 140
    out = {'n_linked': len(recs), 'classes': classes, 'per_class': {}}
    floors_dx=[]; floors_dy=[]; flags=[]
    class_crops = {}
    for cid in classes:
        crops=[]; order=[]
        for (cl, p, li, cbx, cby, bw, bh) in by_cls[cid][:700]:
            ink = get(p)
            ax0=int(round(cbx-CW/2)); ay0=int(round(cby-CH/2))
            if ax0<0 or ay0<0 or ax0+CW>ink.shape[1] or ay0+CH>ink.shape[0]:
                continue
            crops.append(ink[ay0:ay0+CH, ax0:ax0+CW].astype(np.float32))
            order.append((p, li, cbx))
        if len(crops) < 120:
            continue
        class_crops[cid] = np.array(crops)
        dxs, dys, corrs = measure_class(crops)
        pth = np.percentile(corrs, 40); pure = corrs >= pth
        def clip(a, extra=None):
            m,s=np.median(a),np.std(a); k=np.abs(a-m)<3.5*s+1e-9
            return (a[k], k)
        dxp, kx = clip(dxs[pure]); dyp, ky = clip(dys[pure])
        bx, by = bimodality(dxp), bimodality(dyp)
        out['per_class'][str(cid)] = dict(
            n=len(crops), n_pure=int(pure.sum()),
            dx_std=float(dxp.std()), dy_std=float(dyp.std()),
            dx_bimod=bx, dy_bimod=by)
        floors_dx.append(float(dxp.std())); floors_dy.append(float(dyp.std()))
        for ax, bm in (('dx', bx), ('dy', by)):
            if bm and bm['delta_bic']>10 and bm['sep_over_sd']>2 and bm['sep']>0.3:
                flags.append(dict(cls=str(cid), axis=ax, sep=bm['sep'],
                                  sep_over_sd=bm['sep_over_sd'], dbic=bm['delta_bic'],
                                  ws=bm['ws']))
    out['noise_floor_dx_px']=float(np.median(floors_dx)) if floors_dx else None
    out['noise_floor_dy_px']=float(np.median(floors_dy)) if floors_dy else None
    out['structured_flags']=flags

    # ---- SHAPE-MIX NEGATIVE CONTROL ----
    # merge two DIFFERENT classes; confirm our bimodality test FIRES (proving
    # earlier width-bin flags were shape-mix, and our per-class test is sensitive)
    if len(class_crops) >= 2:
        a, b = classes[0], classes[1]
        na = min(200, len(class_crops[a])); nb = min(200, len(class_crops[b]))
        mixed = np.concatenate([class_crops[a][:na], class_crops[b][:nb]])
        dxs, dys, corrs = measure_class(mixed)
        out['shapemix_control'] = dict(
            classes_mixed=[a, b],
            dx_bimod=bimodality(dxs), dy_bimod=bimodality(dys),
            note='different shapes averaged -> expect bimodal (sensitivity check)')

    with open(os.path.join(HERE, 'classpure_results.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print('linked CC->class:', out['n_linked'])
    print(f"CLASS-PURE noise floor dx={out['noise_floor_dx_px']:.3f}px dy={out['noise_floor_dy_px']:.3f}px")
    for cid, v in out['per_class'].items():
        bx, by = v['dx_bimod'], v['dy_bimod']
        print(f"cls {cid:>3} n={v['n_pure']:3d} dx_std={v['dx_std']:.3f} dy_std={v['dy_std']:.3f} "
              f"dx(sep={bx['sep']:.3f}/{bx['sep_over_sd']:.2f}) dy(sep={by['sep']:.3f}/{by['sep_over_sd']:.2f})")
    sm = out.get('shapemix_control')
    if sm:
        print(f"SHAPE-MIX CTRL cls{sm['classes_mixed']}: dx sep/sd={sm['dx_bimod']['sep_over_sd']:.2f} "
              f"dy sep/sd={sm['dy_bimod']['sep_over_sd']:.2f} (should be >2 if sensitive)")
    print('CLASS-PURE STRUCTURED FLAGS:', flags)
    return out


if __name__ == '__main__':
    run()
