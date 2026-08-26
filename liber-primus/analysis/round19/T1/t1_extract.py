"""Extract every rune-band component from all 58 LP2 images + the 17 LP1 images,
at NATIVE resolution, and store them.  This is the crop stage of the per-rune reader.

Output: work/crops_<face>.npz  (rebuildable; not committed).  Records the sha256 of
every source image so the extraction is reproducible and provenance-checked.
"""
import os, sys, json, numpy as np
import t1_reader as T

WORK = os.path.join(T.HERE, 'work')
os.makedirs(WORK, exist_ok=True)


def img_path(face, p):
    if face == 'LP2':
        return T.relikd_path(p) if p <= 55 else T.vendor_path('%d.jpg' % (p + 17))
    return T.vendor_path('%02d.jpg' % p)


def extract(face, pages):
    P, X0, Y0, X1, Y1, H, W, A, R, PI, NI = [], [], [], [], [], [], [], [], [], [], []
    packs, hashes = [], {}
    for p in pages:
        path = img_path(face, p)
        hashes['p%d' % p] = dict(path=os.path.relpath(path, T.ROOT), sha256=T.sha256(path))
        glyphs, rows = T.segment_page(path)
        for g in glyphs:
            P.append(p); X0.append(g['x0']); Y0.append(g['y0'])
            X1.append(g['x1']); Y1.append(g['y1'])
            H.append(g['h']); W.append(g['w']); A.append(g['area'])
            R.append(g['row']); PI.append(g['pos_in_row']); NI.append(g.get('n_inner', 0))
            packs.append(np.packbits(g['mask']).tobytes())
        print('%s p%-2d  %4d glyphs  %2d rows' % (face, p, len(glyphs), len(rows)), flush=True)
    blob = b''.join(packs)
    off = np.cumsum([0] + [len(b) for b in packs])
    np.savez_compressed(os.path.join(WORK, 'crops_%s.npz' % face),
                        page=np.array(P, np.int16), x0=np.array(X0, np.int32),
                        y0=np.array(Y0, np.int32), x1=np.array(X1, np.int32),
                        y1=np.array(Y1, np.int32), h=np.array(H, np.int16),
                        w=np.array(W, np.int16), area=np.array(A, np.int32),
                        row=np.array(R, np.int16), pos=np.array(PI, np.int16),
                        n_inner=np.array(NI, np.int16),
                        blob=np.frombuffer(blob, np.uint8), off=off.astype(np.int64))
    json.dump(hashes, open(os.path.join(WORK, 'hashes_%s.json' % face), 'w'), indent=1)
    print('%s: %d crops' % (face, len(P)))


def load(face):
    z = np.load(os.path.join(WORK, 'crops_%s.npz' % face))
    blob = z['blob'].tobytes(); off = z['off']
    def mask(i):
        h, w = int(z['h'][i]), int(z['w'][i])
        b = np.unpackbits(np.frombuffer(blob[off[i]:off[i + 1]], np.uint8))
        return b[:h * w].reshape(h, w).astype(bool)
    return z, mask


if __name__ == '__main__':
    extract('LP2', list(range(58)))
    extract('LP1', list(range(17)))
