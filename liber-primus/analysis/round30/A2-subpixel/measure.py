"""A2 sub-pixel measurement primitives.

Given a grayscale ink image (dark ink on light bg) and a bounding box for a
glyph, measure its sub-pixel position via ink-mass centroid. Centroid of a
rasterized-then-JPEG'd shape is a robust sub-pixel position estimator; its
noise floor is set by JPEG quantization + antialias, which we characterize
empirically with controls.
"""
import numpy as np


def to_ink(gray):
    """Convert grayscale (0=black ink,255=white paper) to ink weight in [0,1]."""
    g = gray.astype(np.float32)
    return (255.0 - g) / 255.0


def centroid(ink, x0, y0, x1, y1, thresh=0.15):
    """Sub-pixel centroid of ink mass in box. Returns (cx, cy, mass)."""
    sub = ink[y0:y1, x0:x1]
    w = sub.copy()
    w[w < thresh] = 0.0          # kill paper/JPEG ringing near white
    m = w.sum()
    if m <= 0:
        return None
    ys, xs = np.mgrid[y0:y1, x0:x1]
    cx = (w * xs).sum() / m
    cy = (w * ys).sum() / m
    return float(cx), float(cy), float(m)


def col_profile(ink, x0, y0, x1, y1):
    return ink[y0:y1, x0:x1].sum(axis=0)


def row_profile(ink, x0, y0, x1, y1):
    return ink[y0:y1, x0:x1].sum(axis=1)


def edge_subpixel(profile, rising=True, frac=0.5):
    """Sub-pixel crossing of `frac` of the profile peak. rising=leading edge."""
    p = profile.astype(np.float32)
    if p.max() <= 0:
        return None
    lvl = frac * p.max()
    idx = range(len(p) - 1) if rising else range(len(p) - 1, 0, -1)
    for i in idx:
        a, b = (p[i], p[i + 1]) if rising else (p[i], p[i - 1])
        if (a < lvl <= b) or (a >= lvl > b):
            # linear interp
            if b == a:
                return float(i)
            t = (lvl - a) / (b - a)
            return float(i + t) if rising else float(i - t)
    return None
