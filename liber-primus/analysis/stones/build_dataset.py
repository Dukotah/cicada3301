"""Extract normalized glyph crops for all glyphs on exact-count-match lines.
Label by position from canon. Save features + labels + provenance.
"""
import sys, json
sys.path.insert(0, 'analysis/stones')
import numpy as np
from PIL import Image
import pipeline as P

CELL = (56, 40)  # H, W


def norm_crop(gray_arr, box, pad=4):
    x0, x1, y0, y1 = box['x0'], box['x1'], box['y0'], box['y1']
    sub = gray_arr[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad]
    bw = (sub < 128).astype(np.uint8)
    if bw.sum() == 0:
        return None
    ys, xs = np.where(bw)
    sub2 = bw[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = Image.fromarray((sub2 * 255).astype(np.uint8))
    im = im.resize((CELL[1], CELL[0]), Image.LANCZOS)
    a = (np.asarray(im) > 64).astype(np.float32)
    return a


def main():
    gl, po = P.global_lines()
    align = json.load(open('analysis/stones/alignment.json'))
    X = []
    y = []
    prov = []  # (img, line_idx_in_img, glyph_idx_in_line, global_line, canon_rune)
    Xall = []
    provall = []
    boxesall = []
    for n in range(56):
        al = align[str(n)]
        lines, b, gray = P.segment_image(f'data/relikd/p{n}.jpg')
        garr = np.asarray(gray)
        clean = [L for L in lines if len(L) >= 10]
        for i, gli in enumerate(al):
            if i >= len(clean):
                break
            canon = gl[gli]
            L = clean[i]
            match = (len(L) == len(canon))
            for j, box in enumerate(L):
                crop = norm_crop(garr, box)
                if crop is None:
                    continue
                feat = crop.flatten()
                Xall.append(feat)
                provall.append((n, i, j, gli, canon[j] if (match and j < len(canon)) else None, match))
                boxesall.append((n, box['x0'], box['x1'], box['y0'], box['y1']))
                if match:
                    X.append(feat)
                    y.append(canon[j])
                    prov.append((n, i, j, gli, canon[j]))
    X = np.array(X);
    Xall = np.array(Xall)
    np.savez_compressed('analysis/stones/dataset.npz',
                        X=X, y=np.array(y, dtype=object),
                        prov=np.array(prov, dtype=object),
                        Xall=Xall, provall=np.array(provall, dtype=object),
                        boxesall=np.array(boxesall, dtype=object))
    print('clean labeled glyphs:', len(X), 'all glyphs:', len(Xall))


if __name__ == '__main__':
    main()
