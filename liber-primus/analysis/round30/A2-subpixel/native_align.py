"""A2 definitive sub-pixel test at NATIVE page resolution, per rune class.

Uses retranscribe DP output (class id + native x_start per glyph, plus band
ys/ye) to cut each glyph at FULL resolution from p*.jpg, then sub-pixel-registers
every instance of a class to that class's mean template via parabolic-interpolated
2D cross-correlation.

Channels:
  dx  = horizontal micro-position of the glyph in its cell (advance/kern channel)
  dy  = vertical micro-position (baseline channel)

For each clean class we report:
  - dx_std, dy_std  = the REAL sub-pixel noise floor for that repeated rune
  - bimodality (delta_bic, sep/sd) on dx and dy  -> structured binary channel?

Then, since the control proved we resolve <0.1px shifts, if the true font were
placing glyphs on a perturbed lattice to carry bits, dx or dy would be bimodal
with sep >> its own std. A clean rendered font => dx,dy ~ unimodal, std at the
JPEG/centroid floor, no structure. That is the null we expect.
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
CROP_W, CROP_H = 96, 140   # generous native cell around a glyph


def main():
    bands = np.load(GEO)['bands']
    lines = json.load(open(READ))
    pages = {}
    def get(p):
        if p not in pages:
            pages[p] = M.to_ink(np.asarray(Image.open(os.path.join(IMG, f'p{p}.jpg')).convert('L')))
        return pages[p]

    # gather instances per class: (page, x_center_est, ys, ye)
    inst = collections.defaultdict(list)
    for i, ln in enumerate(lines):
        b = bands[i]; page, ys, ye = int(b[0]), int(b[1]), int(b[2])
        gl = ln['glyphs']
        for j, (cid, xs, cost) in enumerate(gl):
            cid = int(cid)
            if cid == FILLER:
                continue
            xs = float(xs)
            xe = float(gl[j+1][1]) if j+1 < len(gl) else xs+50
            xc = 0.5*(xs+xe)
            inst[cid].append((page, xc, ys, ye))

    counts = {c: len(v) for c, v in inst.items()}
    # pick the cleanest high-count classes (real runes), cap instances for speed
    classes = [c for c, n in sorted(counts.items(), key=lambda kv:-kv[1]) if n >= 150][:10]

    out = {'classes_tested': classes, 'counts': {str(k): counts[k] for k in classes}}
    per = {}
    all_floor_dx = []; all_floor_dy = []
    for cid in classes:
        crops = []
        meta = []
        for (page, xc, ys, ye) in inst[cid][:600]:
            ink = get(page)
            cyc = 0.5*(ys+ye)
            x0 = int(round(xc - CROP_W/2)); y0 = int(round(cyc - CROP_H/2))
            if x0 < 0 or y0 < 0 or x0+CROP_W > ink.shape[1] or y0+CROP_H > ink.shape[0]:
                continue
            c = ink[y0:y0+CROP_H, x0:x0+CROP_W].astype(np.float32)
            crops.append(c); meta.append((page, x0, y0))
        if len(crops) < 60:
            continue
        crops = np.array(crops)
        tmpl = crops.mean(0)
        T = tmpl - tmpl.mean()
        dxs = []; dys = []
        for c in crops:
            im = c - c.mean()
            corr = fftconvolve(im, T[::-1, ::-1], mode='same')
            cy, cx = parabolic_peak(corr)
            dys.append(cy - corr.shape[0]//2)
            dxs.append(cx - corr.shape[1]//2)
        dxs = np.array(dxs); dys = np.array(dys)
        def clip(a):
            m, s = np.median(a), np.std(a)
            k = np.abs(a-m) < 4*s+1e-9
            return a[k], k
        dxc, kx = clip(dxs); dyc, ky = clip(dys)
        per[str(cid)] = dict(
            n=len(crops),
            dx_std=float(dxc.std()), dy_std=float(dyc.std()),
            dx_mean=float(dxc.mean()), dy_mean=float(dyc.mean()),
            dx_bimod=bimodality(dxc), dy_bimod=bimodality(dyc),
        )
        all_floor_dx.append(float(dxc.std())); all_floor_dy.append(float(dyc.std()))

    out['per_class'] = per
    out['noise_floor_dx_px'] = float(np.median(all_floor_dx)) if all_floor_dx else None
    out['noise_floor_dy_px'] = float(np.median(all_floor_dy)) if all_floor_dy else None

    # structured-channel decision
    flags = []
    for cid, v in per.items():
        for ax in ('dx', 'dy'):
            bm = v[f'{ax}_bimod']
            if bm and bm['delta_bic'] > 10 and bm['sep_over_sd'] > 2 and bm['sep'] > 0.3:
                flags.append(dict(cls=cid, axis=ax, sep=bm['sep'],
                                  sep_over_sd=bm['sep_over_sd'], dbic=bm['delta_bic']))
    out['structured_flags'] = flags

    with open(os.path.join(HERE, 'native_align_results.json'), 'w') as f:
        json.dump(out, f, indent=2)

    print('classes:', classes)
    print(f"NATIVE noise floor  dx={out['noise_floor_dx_px']:.3f}px  dy={out['noise_floor_dy_px']:.3f}px")
    for cid, v in per.items():
        bx, by = v['dx_bimod'], v['dy_bimod']
        print(f"cls {cid:>3} n={v['n']:3d} dx_std={v['dx_std']:.3f} dy_std={v['dy_std']:.3f} "
              f"dx(sep={bx['sep']:.3f},sep/sd={bx['sep_over_sd']:.2f}) "
              f"dy(sep={by['sep']:.3f},sep/sd={by['sep_over_sd']:.2f})")
    print('STRUCTURED FLAGS (sep>0.3px & sep/sd>2 & dbic>10):', flags)
    return out


if __name__ == '__main__':
    main()
