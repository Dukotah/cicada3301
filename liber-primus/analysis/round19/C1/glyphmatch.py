"""L5 / A-04 pass 3 — an INDEPENDENT, non-visual instrument for the contested cells.

Every base-60 token is <digit><symbol>: the first character can only be 0..4 (a byte is
< 256 = 4*60+16), so glyph 1 of every cell is a DIGIT of known identity, at cap height and
on the baseline. That makes glyph 1 a per-cell metric ruler: it fixes the local cap height
and baseline with no reference to any transcription.

So for glyph 2 we can measure, in units of the *same cell's* digit:
    hrel   = height(glyph2) / height(glyph1)
    toprel = (top(glyph1) - top(glyph2)) / height(glyph1)   > 0 => ascends above cap height
    botrel = (bottom(glyph2) - bottom(glyph1)) / height(glyph1)  > 0 => descends
    wrel   = width(glyph2) / height(glyph1)
and we can build a *bitmap template* per symbol class from the 245 uncontested cells whose
identity canon_256.bin already fixes, then match a contested glyph against those templates
by IoU. The letter classes that matter here (I / l / i / L / 1 / O / 0 / W / w) differ in
exactly these measures, so this is a real second instrument, not a re-look.

    python3 glyphmatch.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image

import grid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CANON = os.path.join(ROOT, "liber-primus", "analysis", "pp49_51", "canon_256.bin")
ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx"
CONTESTED = [25, 175, 182, 199, 215, 237]
CONFLICT = [25, 45, 50, 165, 172, 175, 182, 199, 215, 237, 246]

# canvas for the normalised glyph template: 1 digit-height = SCALE px,
# origin at (baseline, glyph left edge); room above cap height and below baseline.
SCALE = 64
CANV_H = 128   # y=0 is 0.6*digit-height above cap height; baseline at y=  int(1.6*SCALE)
BASE_Y = 102
CANV_W = 96


def _pages():
    ims = {}
    for p in ("p49", "p50", "p51"):
        ims[p] = np.asarray(Image.open(os.path.join(grid.IMG, p + ".jpg")).convert("L"))
    return ims


def _bbox(mask):
    ys, xs = np.nonzero(mask)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def cell_glyphs(arr, box, pad=10):
    """Return [(mask, x0,y0,x1,y1), ...] for the glyph blobs of one cell, left to right.
    Column-gap segmentation; a dotted 'i'/'j' keeps its dot because the split is on x."""
    x0, y0, x1, y1 = box
    sub = arr[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad] < 128
    if not sub.any():
        return []
    colink = sub.sum(axis=0)
    runs, i = [], 0
    while i < len(colink):
        if colink[i]:
            j = i
            while j < len(colink) and colink[j]:
                j += 1
            runs.append((i, j))
            i = j
        else:
            i += 1
    # Every cell holds exactly TWO glyphs, so split at the single widest inter-run gap
    # rather than at a fixed threshold. (A fixed threshold either fuses the pair or
    # shatters glyphs like 'k'/'x' whose strokes are column-separated.)
    if len(runs) == 1:
        merged = [list(runs[0])]
    else:
        gaps = [(runs[k + 1][0] - runs[k][1], k) for k in range(len(runs) - 1)]
        _, cut = max(gaps)
        merged = [[runs[0][0], runs[cut][1]], [runs[cut + 1][0], runs[-1][1]]]
    out = []
    for (a, b) in merged:
        m = sub[:, a:b]
        if m.sum() < 20:
            continue
        bx0, by0, bx1, by1 = _bbox(m)
        out.append((m[by0:by1, bx0:bx1], a + bx0, by0, a + bx1, by1))
    return out


def cell_metrics(arr, box):
    g = cell_glyphs(arr, box)
    if len(g) != 2:
        return None
    (m1, ax0, ay0, ax1, ay1), (m2, bx0, by0, bx1, by1) = g
    h1 = ay1 - ay0
    return {
        "h1": h1,
        "hrel": (by1 - by0) / h1,
        "toprel": (ay0 - by0) / h1,
        "botrel": (by1 - ay1) / h1,
        "wrel": (bx1 - bx0) / h1,
        "ink": float(m2.sum()) / (h1 * h1),
        "_m2": m2, "_h1": h1,
        "_dy_top": (ay0 - by0), "_dy_bot": (by1 - ay1),
    }


def normalise(m2, h1, dy_top):
    """Render glyph 2 onto the shared canvas at 1 digit-height = SCALE px,
    anchored so the DIGIT's cap line sits at a fixed canvas row."""
    s = SCALE / h1
    h, w = m2.shape
    nh, nw = max(1, int(round(h * s))), max(1, int(round(w * s)))
    im = Image.fromarray((m2 * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS)
    a = np.asarray(im) > 127
    canv = np.zeros((CANV_H, CANV_W), bool)
    cap_y = BASE_Y - SCALE          # canvas row of the digit's cap line
    top = int(round(cap_y - dy_top * s))
    y0 = max(0, top)
    x0 = 4
    ah, aw = a.shape
    canv[y0:y0 + ah, x0:x0 + aw] |= a[:CANV_H - y0, :CANV_W - x0]
    return canv


def build():
    canon = open(CANON, "rb").read()
    with open(os.path.join(HERE, "grid.json")) as f:
        g = json.load(f)
    ims = _pages()

    rows = {}
    for i in range(256):
        page, j = grid.idx_to_cell(i)
        met = cell_metrics(ims[page], g[page][j])
        if met is None:
            rows[i] = None
            continue
        met["canv"] = normalise(met["_m2"], met["_h1"], met["_dy_top"])
        rows[i] = met
    return canon, rows


def main():
    canon, rows = build()
    bad = [i for i, r in rows.items() if r is None]
    print(f"segmented {256 - len(bad)}/256 cells into exactly 2 glyphs"
          + (f"  (failed: {bad})" if bad else ""))

    # class exemplars from the UNCONTESTED cells only
    byclass = {}
    for i, r in rows.items():
        if r is None or i in CONFLICT:
            continue
        sym = ALPHA[canon[i] % 60]
        byclass.setdefault(sym, []).append(i)

    print("\nexemplar counts for the classes that decide these cells:")
    for s in "IilL1OoO0Ww":
        print(f"   '{s}': {len(byclass.get(s, []))}", end="")
    print()

    # per-class metric summary + averaged template
    tmpl, stats = {}, {}
    for s, idxs in byclass.items():
        if not idxs:
            continue
        acc = np.zeros((CANV_H, CANV_W), float)
        for i in idxs:
            acc += rows[i]["canv"]
        tmpl[s] = acc / len(idxs)
        stats[s] = {
            k: (float(np.mean([rows[i][k] for i in idxs])),
                float(np.std([rows[i][k] for i in idxs])))
            for k in ("hrel", "toprel", "botrel", "wrel", "ink")
        }
        stats[s]["n"] = len(idxs)

    print("\nclass metrics (mean+/-sd, in units of the SAME cell's digit height):")
    hdr = f"{'sym':>4} {'n':>3} {'hrel':>14} {'toprel':>14} {'wrel':>14}"
    print(hdr)
    for s in sorted(stats, key=lambda x: (-stats[x]["n"], x)):
        st = stats[s]
        print(f"{s:>4} {st['n']:>3} "
              f"{st['hrel'][0]:>7.3f}+-{st['hrel'][1]:<5.3f} "
              f"{st['toprel'][0]:>7.3f}+-{st['toprel'][1]:<5.3f} "
              f"{st['wrel'][0]:>7.3f}+-{st['wrel'][1]:<5.3f}")

    # --- match the contested cells -----------------------------------------
    print("\n" + "=" * 76)
    print("CONTESTED CELLS -- template IoU against every class template")
    print("=" * 76)
    verdict = {}
    for i in CONTESTED:
        r = rows[i]
        c = r["canv"].astype(float)
        scores = []
        for s, t in tmpl.items():
            tb = t > 0.5
            inter = np.logical_and(c > 0.5, tb).sum()
            union = np.logical_or(c > 0.5, tb).sum()
            scores.append((inter / union if union else 0.0, s))
        scores.sort(reverse=True)
        d0 = int(canon[i]) // 60
        top = scores[:5]

        # --- metric classifier: standardised distance in (hrel, toprel, botrel, wrel).
        # IoU alone under-separates narrow bars (I vs l overlap ~90% because they differ
        # only by a ~9%-of-cap-height ascender), so the metrics are the primary evidence
        # and IoU is corroboration.
        FLOOR = 0.02      # metric noise floor; sd of a 1-exemplar class is 0
        mscores = []
        for s2, st in stats.items():
            d = 0.0
            for k in ("hrel", "toprel", "botrel", "wrel"):
                mu, sd = st[k]
                d += ((r[k] - mu) / max(sd, FLOOR)) ** 2
            mscores.append((d ** 0.5, s2))
        mscores.sort()
        verdict[i] = {
            "measured": {k: round(r[k], 3) for k in ("hrel", "toprel", "botrel", "wrel", "ink")},
            "digit_height_px": int(r["h1"]),
            "top5_iou": [{"sym": s, "iou": round(v, 4), "byte_if": d0 * 60 + ALPHA.index(s)}
                         for v, s in top],
            "top5_metric": [{"sym": s, "z": round(v, 2), "byte_if": d0 * 60 + ALPHA.index(s)}
                            for v, s in mscores[:5]],
        }
        print(f"\nidx {i:3d}  (first glyph = digit {d0})   "
              f"hrel={r['hrel']:.3f} toprel={r['toprel']:+.3f} "
              f"botrel={r['botrel']:+.3f} wrel={r['wrel']:.3f}")
        print("      metric distance (z, lower=better):", "  ".join(
            f"{s}={v:.1f}->{d0*60+ALPHA.index(s)}" for v, s in mscores[:4]))
        print("      template IoU            :", "  ".join(
            f"{s}={v:.3f}->{d0*60+ALPHA.index(s)}" for v, s in top[:4]))

    with open(os.path.join(HERE, "glyphmatch.json"), "w") as f:
        json.dump({"class_stats": stats, "contested": verdict}, f, indent=1)
    print("\nwrote glyphmatch.json")


if __name__ == "__main__":
    main()
