"""T1 chroma follow-up: is the LP 'RGB modification' real red ink, and is it data?

Reproduces the session finding on the stage10 images (and generalizes to any LP page):
  - the marked pixels are genuine saturated RED ink (~#C80000, RGB ~ (187,2,3)),
    NOT a JPEG/compression artifact (an artifact smears all channel pairs; here R
    is offset while G==B, i.e. a Cr-only / red-channel signal).
  - the red is SELECTIVE per glyph: drop-cap + section-opening word(s) + dot ornaments.

Source images (re-download; gitignored):
  https://raw.githubusercontent.com/scream314/cicada3301/master/assets/2014/stage10/{107,167,229}.jpg
  (these are full 2400x3600 LP2 pages; 167 also carries red -- a central dot ornament --
   so it is NOT a clean control, correcting the armada's T1 note.)

The red is a KNOWN LP feature present in 24 local relikd pages; the untested angle is
the red-as-selection, which is extracted + cryptanalytically tested in ../redrune/.
Verdict there: decorative rubrication, cryptographically null.

Usage: python chroma_analysis.py [img.jpg ...]   (defaults to 107/167/229 here)
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

RED_RULE = lambda R, G, B: (R - (G + B) / 2.0 > 40) & (R > 120) & (G < 80)


def analyze(path):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(int)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    L = 0.299 * R + 0.587 * G + 0.114 * B
    re = R - (G + B) / 2.0
    red = RED_RULE(R, G, B)
    ink = L < (L.mean() - 1.0 * L.std())
    stem = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    print(f"=== {stem} {im.size} ===")
    print(f"  red-ink px={int(red.sum())}  meanRGB@red=("
          f"{R[red].mean():.0f},{G[red].mean():.0f},{B[red].mean():.0f})" if red.sum()
          else f"  red-ink px=0")
    # discriminator: signal on ink strokes, not at high-gradient edges (=> not ringing)
    gy, gx = np.gradient(L)
    hi_edge = np.hypot(gx, gy) > np.percentile(np.hypot(gx, gy), 99)
    print(f"  red_excess: ink(strokes)={re[ink].mean():+.2f}  hi_grad_edges={re[hi_edge].mean():+.2f}"
          f"  (ink>>edge => intentional, not JPEG ringing)")
    # isolate marked glyphs -> B/W evidence image
    mask = (re > 5) & (L < 170)
    mask = ndimage.binary_opening(mask, iterations=1)
    out = np.full(L.shape, 255, np.uint8)
    out[mask] = 0
    ys, xs = np.where(mask)
    if len(xs):
        x0, x1, y0, y1 = xs.min() - 30, xs.max() + 30, ys.min() - 30, ys.max() + 30
        crop = Image.fromarray(out).crop((max(0, x0), max(0, y0), min(a.shape[1], x1), min(a.shape[0], y1)))
        w, h = crop.size
        sc = min(2.5, 1400 / max(w, h))
        crop.resize((int(w * sc), int(h * sc))).save(f"marked_{stem}.png")
        print(f"  -> marked_{stem}.png (red-only glyphs)")


if __name__ == "__main__":
    imgs = sys.argv[1:] or ["107.jpg", "167.jpg", "229.jpg"]
    for p in imgs:
        try:
            analyze(p)
        except FileNotFoundError:
            print(f"  (missing {p}; re-download from scream314 stage10)")
