"""R44 W2-B4 shared glue: load, diff, blur models, Wiener/RL deconvolution, component stats."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, label, binary_dilation
from scipy.signal import fftconvolve

RELIKD = '/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/'
CORPUS = '/mnt/c/Users/dukot/projects/cicada3301/corpus/A-primary-artifacts/'

PATHS = {
    'p32_relikd': RELIKD + 'p32.jpg',
    'p32_wiki': CORPUS + 'wiki-uncovering-cicada/images/32.jpg',
    'p32_cijhho_full': CORPUS + 'cijhho123/2014/Liber Primus/liber primus images full/32.jpg',
    'p32_hadyn': CORPUS + 'Hadyn_cicada/2014/ky2khlqdf7qdznac.onion/32.jpg',          # byte==relikd
    'p32_onion7': CORPUS + 'cijhho123/2014/Liber Primus/A drop box of all unmodified files/2014onion7/32.jpg',  # byte==relikd
    'p55_relikd': RELIKD + 'p55.jpg',
    'p55_wiki': CORPUS + 'wiki-uncovering-cicada/images/55.jpg',
    'p55_cijhho_full': CORPUS + 'cijhho123/2014/Liber Primus/liber primus images full/55.jpg',
    'p55_onion7': CORPUS + 'cijhho123/2014/Liber Primus/A drop box of all unmodified files/2014onion7/55.jpg',  # byte==relikd
}

# PREREG bounding boxes (y0,y1,x0,x1), full-res 2400x3600
P32_TREE = (2180, 3200, 700, 1630)
P55_GHOST = (1400, 2550, 700, 1750)
P32_RUNES = (650, 1750, 550, 1900)   # sharp rune text block (control material)


def loadY(path):
    return np.asarray(Image.open(path).convert('L'), dtype=np.float64)


def loadRGB(path):
    return np.asarray(Image.open(path).convert('RGB'), dtype=np.float64)


def crop(a, box):
    y0, y1, x0, x1 = box
    return a[y0:y1, x0:x1]


def t1_stats(a, b, tree_box):
    """T1 (PREREG addendum 2026-11-09): p99.9 |dY| inside tree bbox vs SMOOTH pixels
    outside the bbox (master |grad| < 2.0). Fire iff p999_tree >= 8 and >= 2x smooth ref."""
    d = np.abs(a - b)
    mask = np.zeros(a.shape, bool)
    y0, y1, x0, x1 = tree_box
    mask[y0:y1, x0:x1] = True
    gy, gx = np.gradient(a)
    edge = binary_dilation(np.sqrt(gy ** 2 + gx ** 2) >= 2.0, iterations=8)
    smooth = ~edge & ~mask
    p_in = float(np.percentile(d[mask], 99.9))
    p_smooth = float(np.percentile(d[smooth], 99.9))
    p_out = float(np.percentile(d[~mask], 99.9))
    fired = (p_in >= 2.0 * p_smooth) and (p_in >= 8.0)
    return {'p999_tree': round(p_in, 3), 'p999_smooth_ref': round(p_smooth, 3),
            'p999_rest_all': round(p_out, 3),
            'max_tree': float(d[mask].max()), 'max_rest': float(d[~mask].max()),
            'T1_fired': bool(fired)}


# ---------- PSFs ----------
def psf_gauss(sigma, size=None):
    size = size or int(6 * sigma + 1) | 1
    k = np.zeros((size, size)); k[size // 2, size // 2] = 1.0
    return gaussian_filter(k, sigma)


def psf_disk(r):
    size = 2 * r + 1
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    k = ((yy ** 2 + xx ** 2) <= r ** 2).astype(float)
    return k / k.sum()


def psf_motion(length, angle_deg):
    th = np.deg2rad(angle_deg)
    n = max(int(length) | 1, 3)
    k = np.zeros((n, n))
    c = n // 2
    for t in np.linspace(-length / 2, length / 2, 4 * n):
        y = int(round(c + t * np.sin(th))); x = int(round(c + t * np.cos(th)))
        if 0 <= y < n and 0 <= x < n:
            k[y, x] += 1
    return k / k.sum()


def blur_with(img, psf):
    return fftconvolve(img, psf, mode='same')


# ---------- deconvolution ----------
def wiener(img, psf, K=0.01):
    sh = img.shape
    H = np.fft.rfft2(psf, sh)
    G = np.fft.rfft2(img, sh)
    F = np.conj(H) / (np.abs(H) ** 2 + K) * G
    out = np.fft.irfft2(F, sh)
    # center shift: psf was placed at origin; roll back by psf center
    cy, cx = psf.shape[0] // 2, psf.shape[1] // 2
    return np.roll(out, (-cy, -cx), (0, 1))


def richardson_lucy(img, psf, iters=30):
    img = np.clip(img, 1e-6, None)
    est = np.full_like(img, img.mean())
    psf_m = psf[::-1, ::-1]
    for _ in range(iters):
        conv = np.clip(fftconvolve(est, psf, mode='same'), 1e-6, None)
        est = est * fftconvolve(img / conv, psf_m, mode='same')
    return est


# ---------- component analysis (T3) ----------
def stroke_components(binary):
    """Return list of stroke-like components: area 30-3000, elongation 2-20 (PREREG T3)."""
    lab, n = label(binary)
    comps = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        area = ys.size
        if not (30 <= area <= 3000):
            continue
        yc, xc = ys.mean(), xs.mean()
        cov = np.cov(np.vstack([ys - yc, xs - xc]))
        ev = np.linalg.eigvalsh(cov)
        if ev[0] <= 1e-9:
            elong = 50.0
        else:
            elong = float(np.sqrt(ev[1] / ev[0]))
        if 2.0 <= elong <= 20.0:
            comps.append({'area': int(area), 'elong': round(elong, 2),
                          'bbox': [int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())],
                          'mask_idx': (ys, xs)})
    return comps


def novel_stroke_count(deconv, original, dark_thresh=128, overlap_frac=0.30):
    """Stroke-like comps in deconv output that do NOT overlap (>=overlap_frac) the dilated
    dark mask of the original. Returns (count, comps)."""
    d = deconv - np.percentile(deconv, 5)
    rng = np.percentile(deconv, 95) - np.percentile(deconv, 5)
    dn = np.clip(d / max(rng, 1e-6), 0, 1) * 255
    binary = dn < dark_thresh
    orig_dark = binary_dilation(original < 200, iterations=5)
    novel = []
    for c in stroke_components(binary):
        ys, xs = c.pop('mask_idx')
        ov = orig_dark[ys, xs].mean()
        if ov < overlap_frac:
            c['overlap'] = round(float(ov), 3)
            novel.append(c)
    return len(novel), novel


def edge_energy(img):
    gy, gx = np.gradient(img)
    return float(np.sqrt(gy ** 2 + gx ** 2).sum())


def save_png(arr, path):
    a = np.asarray(arr, float)
    a = (a - a.min()) / max(a.max() - a.min(), 1e-9) * 255
    Image.fromarray(a.astype(np.uint8)).save(path)
