"""Independent image-derived transcription via template matching.

Alignment is WORD-BASED: the canonical text marks word separators; the images
have interpunct dots. We segment each line into ink-runs, classify each run as
GLYPH / SEPARATOR-DOT / NOISE by geometry, group glyphs into words at dots, then
match the image word-length sequence to canon word lengths. This tolerates the
arbitrary mid-word line wrapping in the corpus and most decoration noise.
"""
import os, re, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from lp import gematria as gp  # noqa

NORM_W, NORM_H = 40, 56
INK = 128


def load_ink(path):
    a = np.asarray(Image.open(path).convert("L"))
    return (a < INK)


def _max_run(col):
    m = cur = 0
    for v in col:
        if v:
            cur += 1
            if cur > m:
                m = cur
        else:
            cur = 0
    return m


def central_window(ink, max_stroke=210, min_ink=6, gap=45):
    W = ink.shape[1]
    colink = ink.sum(0)
    istext = np.zeros(W, bool)
    for x in range(W):
        if colink[x] < min_ink:
            continue
        if 8 < _max_run(ink[:, x]) < max_stroke:
            istext[x] = True
    xs = np.where(istext)[0]
    if len(xs) == 0:
        return 0, W
    blocks = []
    s = p = xs[0]
    for x in xs[1:]:
        if x - p > gap:
            blocks.append((s, p))
            s = x
        p = x
    blocks.append((s, p))
    center = W / 2
    best = max(blocks, key=lambda b: ((b[0] <= center <= b[1]), b[1] - b[0]))
    return max(0, best[0] - 12), min(W, best[1] + 12)


def line_bands(ink, x0, x1, dark=3, min_gap=10, min_h=55):
    rows = ink[:, x0:x1].sum(1)
    on = rows > dark
    raw = []
    i = 0; n = len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            raw.append([i, j]); i = j
        else:
            i += 1
    merged = []
    for b in raw:
        if merged and b[0] - merged[-1][1] < min_gap:
            merged[-1][1] = b[1]
        else:
            merged.append(b)
    merged = [b for b in merged if b[1] - b[0] >= min_h]
    if not merged:
        return merged
    hs = sorted(b[1] - b[0] for b in merged)
    typ = hs[len(hs) // 2]
    out = []
    for (a, b) in merged:
        k = int(round((b - a) / typ))
        if k <= 1:
            out.append([a, b]); continue
        prof = rows[a:b].astype(float)
        cuts = _valley_cuts(prof, k - 1, int(typ * 0.55))
        prev = a
        for c in cuts:
            out.append([prev, a + c]); prev = a + c
        out.append([prev, b])
    return [b for b in out if b[1] - b[0] >= min_h]


def _valley_cuts(prof, n_cuts, min_sep):
    L = len(prof)
    cand = sorted(range(min_sep, L - min_sep), key=lambda i: prof[i])
    chosen = []
    for i in cand:
        if all(abs(i - c) >= min_sep for c in chosen):
            chosen.append(i)
            if len(chosen) == n_cuts:
                break
    return sorted(chosen)


def col_segments(line_ink, min_gap=4, dark=1):
    cols = line_ink.sum(0)
    on = cols > dark
    segs = []
    i = 0; n = len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            segs.append([i, j]); i = j
        else:
            i += 1
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < min_gap:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return merged


def normalize(crop_bool):
    ys, xs = np.where(crop_bool)
    if len(ys) == 0:
        return np.zeros((NORM_H, NORM_W), np.uint8)
    c = crop_bool[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = c.shape
    img = Image.fromarray((c * 255).astype(np.uint8))
    sc = min(NORM_W / w, NORM_H / h)
    nw, nh = max(1, int(round(w * sc))), max(1, int(round(h * sc)))
    img = img.resize((nw, nh), Image.BILINEAR)
    canvas = Image.new("L", (NORM_W, NORM_H), 0)
    canvas.paste(img, ((NORM_W - nw) // 2, (NORM_H - nh) // 2))
    return (np.asarray(canvas) > 64).astype(np.uint8)


def segment_glyphs(path):
    """Return list of glyph dicts (reading order) and the typical glyph width.
    Each glyph: {sub(bool), box(x0,y0,x1,y1), w,h, gap_before, line}."""
    ink = load_ink(path)
    x0, x1 = central_window(ink)
    bands = line_bands(ink, x0, x1)
    glyphs = []
    widths = []
    for li, (ry0, ry1) in enumerate(bands):
        line_ink = ink[ry0:ry1, x0:x1]
        bh = ry1 - ry0
        segs = col_segments(line_ink)
        prev_x1 = None
        for (cx0, cx1) in segs:
            sub = line_ink[:, cx0:cx1]
            ys = np.where(sub.any(1))[0]
            if len(ys) == 0:
                continue
            gy0, gy1 = ys.min(), ys.max() + 1
            sub2 = sub[gy0:gy1]
            w = cx1 - cx0
            h = gy1 - gy0
            gap = (cx0 - prev_x1) if prev_x1 is not None else 9999
            glyphs.append(dict(sub=sub2.copy(), w=w, h=h, bh=bh,
                               area=int(sub2.sum()), line=li,
                               x0=x0 + cx0, gap_before=gap,
                               y0=ry0 + gy0))
            prev_x1 = cx1
            widths.append(w)
    return glyphs, ink, (x0, x1), bands


def classify_runs(glyphs):
    """Tag each segment as 'glyph','dot','noise'. Dots: small area & small h.
    Noise: extreme width (graphics) or extreme height."""
    if not glyphs:
        return
    hs = np.array([g["h"] for g in glyphs])
    ws = np.array([g["w"] for g in glyphs])
    med_h = np.median(hs)
    med_w = np.median(ws)
    for g in glyphs:
        if g["h"] < 0.45 * med_h and g["w"] < 0.7 * med_w and g["area"] < 0.30 * med_h * med_w:
            g["kind"] = "dot"
        elif g["w"] > 3.0 * med_w or g["h"] > 1.9 * med_h or g["w"] < 4:
            g["kind"] = "noise"
        else:
            g["kind"] = "glyph"
    return med_w, med_h
