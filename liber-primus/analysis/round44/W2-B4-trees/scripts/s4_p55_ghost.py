"""S4: PC4 compositing plants + T4 grey-level/alpha analysis of the p55 ghost tree.

Model: ghost = flat-alpha black composite over white paper (Y = 255*(1-alpha)).
T4 fires iff mean |chroma| in ghost interior > 2.0, OR interior residual RMS > 3x the same
statistic on a black-ink interior control, OR the interior residual field has a coherent
spectral peak (ratio > 10, validated by the PC4 modulated plant).
"""
import io, json, os, sys
import numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imglib as L

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PEAK_BAR = 10.0


def interior_stats(Y, mask):
    m = binary_erosion(mask, iterations=3)
    vals = Y[m]
    return m, {'n_px': int(m.sum()), 'meanY': round(float(vals.mean()), 2),
               'alpha': round(float(1 - vals.mean() / 255), 4),
               'rms': round(float(vals.std()), 3),
               'p5': float(np.percentile(vals, 5)), 'p95': float(np.percentile(vals, 95))}


def spectral_peak(Y, m):
    field = np.zeros_like(Y)
    field[m] = Y[m] - Y[m].mean()
    F = np.abs(np.fft.fftshift(np.fft.fft2(field)))
    h, w = F.shape
    cy, cx = h // 2, w // 2
    F[cy - 2:cy + 3, cx - 2:cx + 3] = 0  # kill DC + leakage
    return float(F.max() / max(np.median(F[F > 0]), 1e-9))


def roundtrip(arr, q=90):
    buf = io.BytesIO()
    Image.fromarray(arr.astype(np.uint8)).save(buf, format='JPEG', quality=q)
    buf.seek(0)
    return np.asarray(Image.open(buf).convert('L'), float)


def main():
    out = {}
    rgb = L.loadRGB(L.PATHS['p55_relikd'])
    Y = rgb.mean(axis=2)
    y0, y1, x0, x1 = L.P55_GHOST
    bbox = np.zeros(Y.shape, bool); bbox[y0:y1, x0:x1] = True
    ghost_mask = bbox & (Y < 248) & (Y > 100)   # grey object, excludes any black
    black_mask = ~bbox & (Y < 60)               # vines + cicada ink

    gm, gstats = interior_stats(Y, ghost_mask)
    bm, bstats = interior_stats(Y, black_mask)

    # ---------- PC4 ----------
    shape = ghost_mask[y0:y1, x0:x1]  # object shape only (shape is irrelevant to the model)
    white = np.full(shape.shape, 255.0)
    flat = white.copy(); flat[shape] = 255 * (1 - 0.18)
    flat_rt = roundtrip(flat)
    mflat = binary_erosion(shape, iterations=3)
    alpha_rec = 1 - flat_rt[mflat].mean() / 255
    rms_flat = float(flat_rt[mflat].std())
    pk_flat = spectral_peak(flat_rt, mflat)

    yy = np.arange(shape.shape[0])[:, None] * np.ones(shape.shape[1])[None, :]
    mod = white.copy()
    amod = 0.18 + 0.08 * np.sign(np.sin(2 * np.pi * yy / 16))
    mod[shape] = 255 * (1 - amod[shape])
    mod_rt = roundtrip(mod)
    rms_mod = float(mod_rt[mflat].std())
    pk_mod = spectral_peak(mod_rt, mflat)

    bar_rms = 3 * bstats['rms']
    pc4 = {'alpha_true': 0.18, 'alpha_recovered': round(float(alpha_rec), 4),
           'alpha_ok': bool(abs(alpha_rec - 0.18) <= 0.05),
           'rms_flat': round(rms_flat, 3), 'flat_below_bar': bool(rms_flat <= bar_rms),
           'peak_flat': round(pk_flat, 1),
           'rms_mod': round(rms_mod, 3), 'peak_mod': round(pk_mod, 1),
           'modulated_detected': bool(rms_mod > bar_rms or pk_mod > PEAK_BAR),
           'bar_rms_3x_black': round(bar_rms, 3)}
    pc4['passed'] = pc4['alpha_ok'] and pc4['flat_below_bar'] and pc4['modulated_detected']
    out['PC4'] = pc4
    print('PC4:', pc4)
    assert pc4['passed'], 'POSITIVE CONTROL PC4 FAILED - stop'

    # ---------- real ghost ----------
    chroma = (rgb.max(axis=2) - rgb.min(axis=2))
    mean_chroma = float(chroma[gm].mean())
    pk_real = spectral_peak(Y, gm)
    real = {'ghost_interior': gstats, 'black_control_interior': bstats,
            'mean_chroma_ghost': round(mean_chroma, 3),
            'mean_chroma_black_control': round(float(chroma[bm].mean()), 3),
            'rms_ratio_ghost_vs_black': round(gstats['rms'] / max(bstats['rms'], 1e-9), 3),
            'spectral_peak_ghost': round(pk_real, 1)}
    fired = (mean_chroma > 2.0) or (gstats['rms'] > bar_rms) or (pk_real > PEAK_BAR)
    real['T4_fired'] = bool(fired)
    out['real_p55_ghost'] = real
    print('REAL:', json.dumps(real, indent=1))

    # record crops: ghost region luminance (levels stretched) + interior residual field
    L.save_png(Y[y0:y1, x0:x1], os.path.join(HERE, 'crops', 'p55_ghost_region.png'))
    resid = np.zeros_like(Y); resid[gm] = Y[gm] - Y[gm].mean()
    L.save_png(resid[y0:y1, x0:x1], os.path.join(HERE, 'crops', 'p55_ghost_interior_residual.png'))
    # grey-level histogram for the record
    hist, edges = np.histogram(Y[gm], bins=64, range=(0, 256))
    out['ghost_hist'] = {'edges': [float(e) for e in edges[:-1]], 'counts': [int(c) for c in hist]}
    json.dump(out, open(os.path.join(HERE, 'results', 'p55_ghost.json'), 'w'), indent=1)
    print('T4 fired:', fired)


if __name__ == '__main__':
    main()
