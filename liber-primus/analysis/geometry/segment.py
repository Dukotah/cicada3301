"""Track GEOMETRY — stage 1: glyph segmentation of the 56 authentic LP2 pages.

The prior stego sweep (analysis/stego/STEGO-VERDICT.md) covered *file-level*
channels: appended bytes, EXIF/COM/XMP, carve, spatial LSB, DQT tables, OutGuess
DCT. All empty. But its own provenance finding is that these pages are 400-DPI
Ghostscript renders of a PDF -- i.e. a TYPESET DOCUMENT. The canonical covert
channel for a typeset document is not the file bytes, it is the GEOMETRY:
inter-glyph advance, baseline offset, and glyph-shape substitution. That plane
has never been measured here. The vision armada tried to READ the glyphs; it
never COMPARED them.

This stage emits one record per ink component per page:
    page, x0, y0, x1, y1, area, cx, cy, and a 32x32 normalized bitmap
plus the components rejected as ornament (outside the text column) -- which every
previous pipeline in this repo silently discarded.

Output: glyphs.npz
"""
import os, sys, json, hashlib
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
IMG = os.path.join(ROOT, 'data', 'relikd')
BOX = 32


def verify():
    rows = json.load(open(os.path.join(ROOT, 'analysis', 'stego',
                                       'provenance.json')))['rows']
    for r in rows:
        f = os.path.join(IMG, 'p%d.jpg' % r['page'])
        h = hashlib.sha1(open(f, 'rb').read()).hexdigest()
        assert h == r['published_sha1'], 'page %d not authentic' % r['page']
    return len(rows)


def page_components(path):
    im = Image.open(path).convert('L')
    a = np.asarray(im)
    ink = a < 128                       # black-on-white render
    lab, n = ndimage.label(ink)
    objs = ndimage.find_objects(lab)
    recs = []
    for i, sl in enumerate(objs, start=1):
        ys, xs = sl
        h, w = ys.stop - ys.start, xs.stop - xs.start
        if h < 6 or w < 4:              # speckle / JPEG ringing
            continue
        sub = (lab[sl] == i)
        area = int(sub.sum())
        if area < 40:
            continue
        recs.append((xs.start, ys.start, xs.stop, ys.stop, area, sub))
    return recs, a.shape


def normalize(sub):
    """scale the component mask into a BOXxBOX box, preserving aspect"""
    h, w = sub.shape
    s = max(h, w)
    pad = np.zeros((s, s), dtype=np.uint8)
    y0 = (s - h) // 2
    x0 = (s - w) // 2
    pad[y0:y0+h, x0:x0+w] = sub
    im = Image.fromarray(pad * 255)
    im = im.resize((BOX, BOX), Image.BILINEAR)
    return (np.asarray(im) > 96).astype(np.uint8)


def main():
    n = verify()
    print('provenance: %d/%d pages hash-authentic' % (n, n))
    P, X0, Y0, X1, Y1, A, BM = [], [], [], [], [], [], []
    for p in range(56):
        recs, shape = page_components(os.path.join(IMG, 'p%d.jpg' % p))
        for (x0, y0, x1, y1, area, sub) in recs:
            P.append(p); X0.append(x0); Y0.append(y0)
            X1.append(x1); Y1.append(y1); A.append(area)
            BM.append(normalize(sub))
        print('p%-2d %5d components  (page %s)' % (p, len(recs), shape), flush=True)
    np.savez_compressed(os.path.join(HERE, 'glyphs.npz'),
                        page=np.array(P, np.int16),
                        x0=np.array(X0, np.int32), y0=np.array(Y0, np.int32),
                        x1=np.array(X1, np.int32), y1=np.array(Y1, np.int32),
                        area=np.array(A, np.int32),
                        bmp=np.array(BM, np.uint8))
    print('total components:', len(P))


if __name__ == '__main__':
    main()
