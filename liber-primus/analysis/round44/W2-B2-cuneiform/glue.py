"""R44 / W2-B2 shared glue — dot subclass + dot->nearest-glyph->rune-index mapping (PREREG §4 R-C).

Used identically by the plant (PC-B) and by the real reads, per doctrine ("plant through
YOUR OWN glue").
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp  # noqa

from census import load_glyphs  # noqa  (same package dir)

DOT_MAX_AREA = 2500
DOT_MAX_DIM = 60


ROW_GAP = 40  # px; y-center gap that starts a new reading row (glue fix #2, run.log)


def is_dot(c):
    return c["area"] <= DOT_MAX_AREA and max(c["h"], c["w"]) <= DOT_MAX_DIM


def sort_reading_order(comps):
    """Row-major reading order: bucket by y-center (new row when the gap to the previous
    y-center exceeds ROW_GAP), then x within a row. Raw (y0,x0) sorting scrambled x-order
    within a row when component heights differ (caught by PC-B)."""
    cs = sorted(comps, key=lambda c: (c["y0"] + c["y1"]) / 2)
    rows, cur, last_y = [], [], None
    for c in cs:
        yc = (c["y0"] + c["y1"]) / 2
        if last_y is not None and yc - last_y > ROW_GAP:
            rows.append(cur)
            cur = []
        cur.append(c)
        last_y = yc
    if cur:
        rows.append(cur)
    out = []
    for r in rows:
        out.extend(sorted(r, key=lambda c: c["x0"]))
    return out


def dots_reading_order(census, pages=None):
    """All UNLOGGED dot components book-wide in reading order (page, then y, then x).
    Returns list of (page_name, comp)."""
    out = []
    names = pages or (["p%d" % i for i in range(56)] + ["0_wisdom"])
    for name in names:
        rec = census["images"].get(name)
        if not rec or rec.get("missing"):
            continue
        ds = sort_reading_order([c for c in rec.get("unlogged_components", []) if is_dot(c)])
        out.extend((name, c) for c in ds)
    return out


def map_dots_to_runes(dot_list, by_img=None):
    """dot_list: list of (page_name, comp). Nearest stones glyph center on that image ->
    rune index. Returns list of dicts (page, center, nearest glyph, dist, rune_idx or None)."""
    if by_img is None:
        by_img = load_glyphs()
    centers = {}
    for img, gl in by_img.items():
        arr = np.array([[(g["box"][0] + g["box"][1]) / 2, (g["box"][2] + g["box"][3]) / 2]
                        for g in gl])
        centers[img] = arr
    out = []
    for name, c in dot_list:
        pno = int(name[1:]) if name.startswith("p") and name[1:].isdigit() else None
        cx, cy = (c["x0"] + c["x1"]) / 2, (c["y0"] + c["y1"]) / 2
        rec = dict(page=name, center=[cx, cy], bbox=[c["x0"], c["x1"], c["y0"], c["y1"]],
                   rune_idx=None, nearest=None, dist=None)
        if pno in centers and len(centers[pno]):
            d2 = ((centers[pno] - np.array([cx, cy])) ** 2).sum(1)
            j = int(d2.argmin())
            g = by_img[pno][j]
            rec["nearest"] = dict(gli=g["gli"], gi=g["gi"], rune=g["rune"])
            rec["dist"] = float(np.sqrt(d2[j]))
            rec["rune_idx"] = gp.RUNE_TO_IDX.get(g["rune"])
        out.append(rec)
    return out
