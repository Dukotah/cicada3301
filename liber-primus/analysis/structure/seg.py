"""Glyph segmentation for Liber Primus rune pages.

Strategy:
 1. Binarize (ink = dark pixels).
 2. Find text-LINE bands via row-darkness, but first crop to a central column
    window that excludes side decorations (crosses) — we detect the dominant
    vertical text block by column-darkness clustering.
 3. Within each line band, split into glyphs by vertical gaps (columns with ~no
    ink). Word-separator dots and stray marks are filtered by width/height/area.
 4. Each glyph -> bounding box, normalized to fixed size, binarized.

Returns list of glyph dicts in reading order: {page,line,box,norm(np.uint8)}.
"""
import numpy as np
from PIL import Image

NORM_W, NORM_H = 48, 64
INK_THRESH = 128


def load_ink(path):
    a = np.asarray(Image.open(path).convert("L"))
    return (a < INK_THRESH)


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


def central_text_window(ink, max_stroke=200, min_ink=5, gap=40):
    """Find the main vertical text block columns. Text columns contain short
    vertical strokes (glyph stems, run length << page height); large decorations
    (crosses, borders, graphics) contain very long ink runs. Keep columns whose
    longest ink run is < max_stroke, then return the widest contiguous block
    (gaps < `gap` bridged) nearest the page center."""
    W = ink.shape[1]
    colink = ink.sum(0)
    istext = np.zeros(W, bool)
    for x in range(W):
        if colink[x] < min_ink:
            continue
        if 10 < _max_run(ink[:, x]) < max_stroke:
            istext[x] = True
    xs = np.where(istext)[0]
    if len(xs) == 0:
        return 0, W
    # contiguous blocks bridging small gaps
    blocks = []
    s = xs[0]
    p = xs[0]
    for x in xs[1:]:
        if x - p > gap:
            blocks.append((s, p))
            s = x
        p = x
    blocks.append((s, p))
    center = W / 2
    # score by width, prefer ones overlapping center
    def score(b):
        w = b[1] - b[0]
        overlaps = b[0] <= center <= b[1]
        return (overlaps, w)
    best = max(blocks, key=score)
    return max(0, best[0] - 15), min(W, best[1] + 15)


def line_bands(ink, x0, x1, min_gap=10, min_band_h=55, dark_thresh=3):
    sub = ink[:, x0:x1]
    rows = sub.sum(axis=1)
    on = rows > dark_thresh
    bands = []
    i = 0
    n = len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            bands.append([i, j])
            i = j
        else:
            i += 1
    merged = []
    for b in bands:
        if merged and b[0] - merged[-1][1] < min_gap:
            merged[-1][1] = b[1]
        else:
            merged.append(b)
    merged = [b for b in merged if b[1] - b[0] >= min_band_h]
    if not merged:
        return merged
    # estimate the typical line height from the modal band height
    hs = sorted(b[1] - b[0] for b in merged)
    typ = hs[len(hs) // 2]
    # tall bands = multiple merged lines; split them at row-darkness valleys
    out = []
    for (a, b) in merged:
        h = b - a
        k = int(round(h / typ))
        if k <= 1:
            out.append([a, b])
            continue
        prof = rows[a:b].astype(float)
        # find k-1 deepest interior valleys spaced >= 0.5*typ apart
        cuts = _valley_cuts(prof, k - 1, int(typ * 0.55))
        prev = a
        for c in cuts:
            out.append([prev, a + c])
            prev = a + c
        out.append([prev, b])
    out = [b for b in out if b[1] - b[0] >= min_band_h]
    return out


def _valley_cuts(prof, n_cuts, min_sep):
    """Return up to n_cuts indices (into prof) at local minima, greedily picking
    the lowest valleys at least min_sep apart and away from the ends."""
    L = len(prof)
    cand = list(range(min_sep, L - min_sep))
    cand.sort(key=lambda i: prof[i])
    chosen = []
    for i in cand:
        if all(abs(i - c) >= min_sep for c in chosen):
            chosen.append(i)
            if len(chosen) == n_cuts:
                break
    return sorted(chosen)


def glyph_cols(line_ink, min_gap=3, dark_thresh=1):
    cols = line_ink.sum(axis=0)
    on = cols > dark_thresh
    segs = []
    i = 0
    n = len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            segs.append([i, j])
            i = j
        else:
            i += 1
    # merge segments separated by < min_gap (parts of one glyph)
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < min_gap:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return merged


def normalize(crop):
    """crop: bool array. Return uint8 0/255 normalized to NORM_W x NORM_H,
    preserving aspect by padding."""
    ys, xs = np.where(crop)
    if len(ys) == 0:
        return np.zeros((NORM_H, NORM_W), np.uint8)
    crop = crop[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = crop.shape
    img = Image.fromarray((crop * 255).astype(np.uint8))
    # scale to fit within NORM box preserving aspect
    scale = min(NORM_W / w, NORM_H / h)
    nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    img = img.resize((nw, nh), Image.NEAREST)
    canvas = Image.new("L", (NORM_W, NORM_H), 0)
    canvas.paste(img, ((NORM_W - nw) // 2, (NORM_H - nh) // 2))
    out = np.asarray(canvas)
    return (out > 64).astype(np.uint8) * 255
