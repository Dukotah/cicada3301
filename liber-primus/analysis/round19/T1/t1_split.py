"""Two segmentation repairs, each of which is itself a test.

1.  MERGE REPAIR.  A component wider than MAXW=90 px is a merge candidate: the font's
    C (the futhorc `cen`, a "<" shape) tucks under the following rune and their ink
    touches.  We do not assume a wide component is a merge -- we TEST it, by asking
    whether it can be cut into pieces each of which matches a bank exemplar well.  A
    wide component that cannot be cut that way is reported NON-RUNE rather than forced.

2.  LARGE-INITIAL REPAIR.  Some pages open with an illuminated initial: the first rune
    drawn at ~5x rune height and fused with vine ornament into one huge component (on
    73.jpg h=498 w=150, on 74.jpg h=608 w=281).  We test whether the top-left of such a
    component, isotropically reduced to rune height, matches a bank exemplar.

Both repairs are adjudicated by the SAME distance the classifier uses, so a repair that
does not actually produce runes cannot smuggle a glyph into the stream.
"""
import numpy as np
from PIL import Image
import t1_bank as B
import t1_align as A


def _trim(m):
    ys, xs = np.where(m)
    if len(ys) == 0:
        return None
    return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1], int(xs.min())


def _canvas(masks, ch=A.CH, cw=A.CW):
    X = np.zeros((len(masks), ch, cw), np.float32)
    for i, m in enumerate(masks):
        h, w = m.shape
        if h > ch or w > cw:
            m = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                           .resize((min(w, cw), min(h, ch)), Image.LANCZOS)) > 127
            h, w = m.shape
        y, x = (ch - h) // 2, (cw - w) // 2
        X[i, y:y + h, x:x + w] = m
    return X


def split_wide(mask, Ybank, blabels, maxparts=3, min_w=20, accept=900.0):
    """Try to cut `mask` into 2..maxparts rune pieces.  Returns
    (list of (label, x_offset, cost), total_cost) or (None, None) if no cut is good."""
    h, w = mask.shape
    best = None
    for nparts in range(2, maxparts + 1):
        if w < min_w * nparts:
            continue
        cuts = _search(mask, Ybank, blabels, nparts, min_w)
        if cuts is not None and (best is None or cuts[1] < best[1]):
            best = cuts
    if best is None or best[1] > accept * (len(best[0])):
        return None, None if best is None else best[1]
    return best


def _search(mask, Ybank, blabels, nparts, min_w):
    h, w = mask.shape
    if nparts == 2:
        xs = list(range(min_w, w - min_w + 1))
        parts = [[(0, x), (x, w)] for x in xs]
    else:
        parts = []
        step = max(1, (w - 2 * min_w) // 40)
        for x1 in range(min_w, w - 2 * min_w + 1, step):
            for x2 in range(x1 + min_w, w - min_w + 1, step):
                parts.append([(0, x1), (x1, x2), (x2, w)])
    if not parts:
        return None
    flat, owner = [], []
    for pi, seg in enumerate(parts):
        for (a, b) in seg:
            t = _trim(mask[:, a:b])
            flat.append(t[0] if t else np.zeros((4, 4), bool))
            owner.append((pi, a + (t[1] if t else 0)))
    X = _canvas(flat)
    D = B.pairwise_cross(X, Ybank)
    dmin = D.min(1); arg = D.argmin(1)
    tot = np.zeros(len(parts))
    for k, (pi, off) in enumerate(owner):
        tot[pi] += dmin[k]
    bi = int(tot.argmin())
    out = []
    for k, (pi, off) in enumerate(owner):
        if pi == bi:
            out.append((int(blabels[arg[k]]), off, float(dmin[k])))
    return out, float(tot[bi])


def read_initial(mask, Ybank, blabels, target_h=114, accept=1200.0):
    """An illuminated initial: reduce the component to rune height and match.  Also
    tries the left/upper portions, since the initial is fused with vine ornament."""
    h, w = mask.shape
    best = None
    for fy in (1.0, 0.9, 0.8, 0.65, 0.5, 0.4, 0.33):
        for fx in (1.0, 0.9, 0.8, 0.65, 0.5, 0.4, 0.33):
            sub = mask[:int(h * fy), :int(w * fx)]
            t = _trim(sub)
            if t is None or t[0].shape[0] < 20:
                continue
            m = t[0]
            s = float(target_h) / m.shape[0]
            nw = max(4, int(round(m.shape[1] * s)))
            if nw > A.CW - 4:
                continue
            im = Image.fromarray((m * 255).astype(np.uint8)).resize((nw, target_h), Image.LANCZOS)
            r = np.asarray(im) > 127
            X = _canvas([r])
            D = B.pairwise_cross(X, Ybank)
            d = float(D.min()); lab = int(blabels[int(D.argmin())])
            if best is None or d < best[1]:
                best = (lab, d, fy, fx)
    if best is None or best[1] > accept:
        return None, (None if best is None else best[1])
    return best[0], best[1]
