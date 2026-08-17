"""Independent re-transcription — stage 2: read every line by template DP.

Connected-component segmentation cannot deliver an independent read: touching
runes merge into one component and disconnected strokes split into two, which is
why only 184 of 604 lines matched the canonical rune count in Round 8. Template
matching bypasses component analysis entirely.

For each line band we compute, for every template t and every column x, the exact
pixel mismatch of placing t at x, then run a dynamic program over the line:

    f(x) = min( f(x-1) + skip_cost(x)            # blank column
              , min_t f(x - w_t) + cost(t, x-w_t) )   # a glyph ends here

The result is the sequence of template classes that most cheaply explains the
line's ink -- an OCR decode against a closed, known alphabet, with no reference
to the canonical transcription anywhere in this file.

Output: read_lines.json  (per line: page, band, list of template class ids)
"""
import os, sys, json, collections
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.normpath(os.path.join(HERE, '..', 'geometry'))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
IMG = os.path.join(ROOT, 'data', 'relikd')
PAD_H, PAD_W = 128, 136
MINCLASS = 100          # only classes with >=100 glyphs are real font shapes


def load_templates():
    t = np.load(os.path.join(HERE, 'templates.npz'))
    X, label, sizes, centres = t['X'], t['label'], t['sizes'], t['centres']
    kh, kw = t['keys_h'], t['keys_w']
    cover = np.bincount(label, weights=sizes, minlength=label.max()+1)
    keep = [c for c in range(len(cover)) if cover[c] >= MINCLASS]
    tmpl = []
    for c in keep:
        i = centres[c]
        h, w = int(kh[i]), int(kw[i])
        canvas = X[i].reshape(PAD_H, PAD_W).astype(np.float32)
        top = (PAD_H - h) // 2
        left = (PAD_W - w) // 2
        tmpl.append((c, canvas[top:top+h, left:left+w]))
    return tmpl, cover


def line_bands():
    d = np.load(os.path.join(GEO, 'glyphs2.npz'))
    return d['bands']            # (page, ys, ye, nglyph, medh)


def decode_line(ink, tmpl, band_h):
    """DP over columns; returns list of (class_id, x_start, cost)"""
    Wl = ink.shape[1]
    costs = {}
    for cid, T in tmpl:
        th, tw = T.shape
        if tw >= Wl:
            continue
        # vertical placement: centre the template in the band, allow +/-3 px
        best = None
        for dy in (-3, -1, 0, 1, 3):
            top = (band_h - th) // 2 + dy
            if top < 0 or top + th > band_h:
                continue
            sub = ink[top:top+th]
            corr = fftconvolve(sub, T[::-1, ::-1], mode='valid')[0]
            box = np.convolve(sub.sum(0), np.ones(tw), mode='valid')
            mism = T.sum() + box - 2.0 * corr
            best = mism if best is None else np.minimum(best, mism)
        if best is not None:
            costs[cid] = (best, tw)
    colink = ink.sum(0)
    INF = 1e18
    f = np.full(Wl + 1, INF)
    bk = [None] * (Wl + 1)
    f[0] = 0.0
    for x in range(Wl):
        if f[x] == INF:
            continue
        # skip a column: cheap if it is blank, expensive if it has ink
        nc = f[x] + colink[x] * 3.0 + 0.5
        if nc < f[x+1]:
            f[x+1] = nc; bk[x+1] = ('skip', x)
        for cid, (m, tw) in costs.items():
            if x + tw > Wl or x >= len(m):
                continue
            nc = f[x] + m[x] + 6.0            # per-glyph prior
            if nc < f[x + tw]:
                f[x + tw] = nc; bk[x + tw] = ('g', x, cid, float(m[x]))
    out = []
    x = Wl
    while x > 0 and bk[x] is not None:
        b = bk[x]
        if b[0] == 'g':
            out.append((b[2], b[1], b[3]))
            x = b[1]
        else:
            x = b[1]
    out.reverse()
    return out


def main():
    tmpl, cover = load_templates()
    print('templates in use: %d (classes with >=%d glyphs)' % (len(tmpl), MINCLASS))
    bands = line_bands()
    print('line bands: %d' % len(bands))
    out = []
    cur_page, ink_page = -1, None
    for bi, (p, ys, ye, ng, medh) in enumerate(bands):
        if p != cur_page:
            a = np.asarray(Image.open(os.path.join(IMG, 'p%d.jpg' % p)).convert('L'))
            ink_page = (a < 128).astype(np.float32)
            cur_page = p
            print('  page %d' % p, flush=True)
        band = ink_page[ys:ye]
        cols = np.where(band.sum(0) > 0)[0]
        if len(cols) == 0:
            out.append(dict(page=int(p), band=bi, glyphs=[]))
            continue
        x_lo, x_hi = int(cols[0]), int(cols[-1]) + 1
        sub = band[:, x_lo:x_hi]
        seq = decode_line(sub, tmpl, sub.shape[0])
        out.append(dict(page=int(p), band=bi,
                        glyphs=[[int(c), int(x + x_lo), round(float(k), 1)]
                                for c, x, k in seq]))
    json.dump(out, open(os.path.join(HERE, 'read_lines.json'), 'w'))
    tot = sum(len(o['glyphs']) for o in out)
    print('\nglyphs read: %d across %d lines' % (tot, len(out)))


if __name__ == '__main__':
    main()
