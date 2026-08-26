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
import t1_align as A
from t1_match import canvas as _canvas_impl, CH, CW


def _trim(m):
    ys, xs = np.where(m)
    if len(ys) == 0:
        return None
    return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1], int(xs.min())


_canvas = _canvas_impl


def split_wide(mask, M, maxparts=4, min_w=20, accept=900.0, maxw=200):
    """Try to cut `mask` into 2..maxparts rune pieces.  Returns
    (list of (label, x_offset, cost), total_cost) or (None, None) if no cut is good."""
    h, w = mask.shape
    if w > maxw:
        return None, None          # too wide to be a run of runes: ornament band
    best = None
    for nparts in range(2, maxparts + 1):
        if w < min_w * nparts:
            continue
        cuts = _search(mask, M, nparts, min_w)
        if cuts is not None and (best is None or cuts[1] < best[1]):
            best = cuts
    if best is None or best[1] > accept * (len(best[0])):
        return None, None if best is None else best[1]
    return best


def cut_candidates(mask, min_w=20, keep=8):
    """Candidate cut columns: local minima of the column ink profile.  Two touching
    typeset glyphs join at a NECK, so the cut is where the column ink is locally least.
    This replaces an exhaustive scan and is what makes the repair affordable."""
    prof = mask.sum(0).astype(np.int32)
    w = len(prof)
    lo, hi = min_w, w - min_w
    if hi <= lo:
        return []
    xs = list(range(lo, hi + 1))
    xs.sort(key=lambda x: (prof[x], abs(x - w / 2.0)))
    out = []
    for x in xs:
        if all(abs(x - y) >= 8 for y in out):
            out.append(x)
        if len(out) >= keep:
            break
    return sorted(out)


def _search(mask, M, nparts, min_w):
    h, w = mask.shape
    cands = cut_candidates(mask, min_w)
    if not cands:
        return None
    import itertools
    parts = []
    for combo in itertools.combinations(cands, nparts - 1):
        if any(b - a < min_w for a, b in zip((0,) + combo, combo + (w,))):
            continue
        bnds = (0,) + combo + (w,)
        parts.append([(bnds[i], bnds[i + 1]) for i in range(nparts)])
    if not parts:
        return None
    flat, owner = [], []
    for pi, seg in enumerate(parts):
        for (a, b) in seg:
            t = _trim(mask[:, a:b])
            flat.append(t[0] if t else np.zeros((4, 4), bool))
            owner.append((pi, a + (t[1] if t else 0)))
    lab, dmin, _ = M.match(_canvas(flat))
    tot = np.zeros(len(parts))
    for k, (pi, off) in enumerate(owner):
        tot[pi] += dmin[k]
    bi = int(tot.argmin())
    out = []
    for k, (pi, off) in enumerate(owner):
        if pi == bi:
            out.append((int(lab[k]), off, float(dmin[k])))
    return out, float(tot[bi])


def read_initial(mask, M, target_h=114, accept=1200.0):
    """An illuminated initial: reduce the component to rune height and match.  Also
    tries the left/upper portions, since the initial is fused with vine ornament."""
    h, w = mask.shape
    crops, tags = [], []
    for fy in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.42, 0.33, 0.28):
        for fx in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.42, 0.33, 0.28):
            t = _trim(mask[:int(h * fy), :int(w * fx)])
            if t is None or t[0].shape[0] < 20:
                continue
            m = t[0]
            s = float(target_h) / m.shape[0]
            nw = max(4, int(round(m.shape[1] * s)))
            if nw > CW - 4:
                continue
            im = Image.fromarray((m * 255).astype(np.uint8)).resize((nw, target_h), Image.LANCZOS)
            crops.append(np.asarray(im) > 127); tags.append((fy, fx))
    if not crops:
        return None, None
    lab, d0, _ = M.match(_canvas(crops))
    k = int(np.argmin(d0))
    if d0[k] > accept:
        return None, float(d0[k])
    return int(lab[k]), float(d0[k])
