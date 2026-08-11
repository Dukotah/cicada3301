"""Track GEOMETRY — segmentation v2: projection-profile line bands.

v1 clustered components by vertical overlap and merged adjacent text lines
(463 bands found vs 604 canonical lines). v2 finds line bands from the page's
horizontal ink projection, which is the standard and far more reliable method
for a uniformly typeset page, then segments components inside each band and
merges horizontally-overlapping blobs into single glyphs.

Also stores, per glyph, a native-resolution crop padded into a fixed canvas so
that the shape test can align sub-pixel before comparing (v1 compared
aspect-normalised masks, which conflates size quantisation with shape).

Output: glyphs2.npz
"""
import os, sys, json, hashlib
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
IMG = os.path.join(ROOT, 'data', 'relikd')
CAN = 160          # native-resolution canvas for each glyph crop


def line_bands(ink):
    """Line bands from the horizontal ink projection.

    The profile never reaches zero between lines (ascenders/descenders of
    adjacent lines overlap), so an absolute threshold merges the whole page into
    2-3 bands. Threshold adaptively: peaks run ~500-700 px of ink per row,
    inter-line valleys ~85-150, so cut at 45% of the median peak height.
    """
    prof = ink.sum(1).astype(float)
    hi = prof[prof > 0.2 * prof.max()]
    if len(hi) == 0:
        return []
    thr = 0.45 * np.median(hi)
    on = prof > thr
    bands, s = [], None
    for i, v in enumerate(on):
        if v and s is None:
            s = i
        elif not v and s is not None:
            if i - s >= 40:
                bands.append((s, i))
            s = None
    if s is not None and len(on) - s >= 40:
        bands.append((s, len(on)))
    # grow each band to the local valley floor so glyph extremities are included
    out = []
    for (a, b) in bands:
        while a > 0 and prof[a-1] > 0.12 * thr and prof[a-1] <= prof[a]:
            a -= 1
        while b < len(prof)-1 and prof[b] > 0.12 * thr and prof[b] <= prof[b-1]:
            b += 1
        out.append((a, b))
    return out


def main():
    P, BX0, BY0, BX1, BY1, AR, LINE, BAND = [], [], [], [], [], [], [], []
    CROPS = []
    lineno = 0
    band_meta = []
    for p in range(56):
        im = Image.open(os.path.join(IMG, 'p%d.jpg' % p)).convert('L')
        a = np.asarray(im)
        ink = a < 128
        bands = line_bands(ink)
        heights = [b[1] - b[0] for b in bands]
        med = np.median(heights) if heights else 0
        for (ys, ye) in bands:
            sub = ink[ys:ye]
            lab, n = ndimage.label(sub)
            objs = ndimage.find_objects(lab)
            comps = []
            for i, sl in enumerate(objs, start=1):
                yy, xx = sl
                h, w = yy.stop - yy.start, xx.stop - xx.start
                if h < 6 or w < 4:
                    continue
                m = (lab[sl] == i)
                if m.sum() < 40:
                    continue
                comps.append([xx.start, yy.start + ys, xx.stop, yy.stop + ys,
                              int(m.sum()), h])
            if not comps:
                continue
            comps.sort(key=lambda c: c[0])
            # merge horizontally overlapping blobs (one rune, several strokes)
            merged = []
            for c in comps:
                if merged:
                    g = merged[-1]
                    ov = min(g[2], c[2]) - max(g[0], c[0])
                    if ov > 0.55 * min(g[2]-g[0], c[2]-c[0]):
                        g[0] = min(g[0], c[0]); g[1] = min(g[1], c[1])
                        g[2] = max(g[2], c[2]); g[3] = max(g[3], c[3])
                        g[4] += c[4]
                        continue
                merged.append(list(c))
            band_meta.append((p, ys, ye, len(merged),
                              int(np.median([m[3]-m[1] for m in merged]))))
            for m in merged:
                P.append(p); BX0.append(m[0]); BY0.append(m[1])
                BX1.append(m[2]); BY1.append(m[3]); AR.append(m[4])
                LINE.append(lineno); BAND.append(int(med))
                # native crop, centred in a fixed canvas
                cx, cy = (m[0]+m[2])//2, (m[1]+m[3])//2
                x0c, y0c = cx - CAN//2, cy - CAN//2
                crop = np.zeros((CAN, CAN), np.uint8)
                sx0, sy0 = max(0, x0c), max(0, y0c)
                sx1, sy1 = min(a.shape[1], x0c+CAN), min(a.shape[0], y0c+CAN)
                crop[sy0-y0c:sy1-y0c, sx0-x0c:sx1-x0c] = ink[sy0:sy1, sx0:sx1]
                CROPS.append(crop)
            lineno += 1
        print('p%-2d bands=%d glyph-groups=%d' % (p, len(bands), len(P)), flush=True)
    np.savez_compressed(os.path.join(HERE, 'glyphs2.npz'),
                        page=np.array(P, np.int16), line=np.array(LINE, np.int32),
                        x0=np.array(BX0, np.int32), y0=np.array(BY0, np.int32),
                        x1=np.array(BX1, np.int32), y1=np.array(BY1, np.int32),
                        area=np.array(AR, np.int32),
                        crop=np.packbits(np.array(CROPS, np.uint8), axis=-1),
                        bands=np.array(band_meta, np.int32))
    print('lines: %d   glyph groups: %d' % (lineno, len(P)))


if __name__ == '__main__':
    main()
