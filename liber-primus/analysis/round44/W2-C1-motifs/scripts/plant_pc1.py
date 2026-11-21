"""R44 / W2-C1 PC1 — census plant (PREREG section 6).

Composites 7 synthetic motifs into copies of REAL pages p05 and p33, logs ground truth,
then runs the SAME detector glue (census_detect.detect) over the planted copies and saves
crops for the agent-classification leg. Bar (PREREG): 7/7 recovered with correct type and
count, correct orientation on the saltire cross and the inverted insect, centroid +/-10 px.
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw

import census_detect as CD

CELL = CD.CELL
PW = os.path.join(CELL, "plant_work")
os.makedirs(PW, exist_ok=True)
INK = 60  # dark grey, ink-like


def draw_cross(d, cx, cy, size, saltire=False):
    s = size // 2
    wd = max(10, size // 9)
    if not saltire:
        d.line([(cx - s, cy), (cx + s, cy)], fill=INK, width=wd)
        d.line([(cx, cy - s), (cx, cy + s)], fill=INK, width=wd)
    else:
        d.line([(cx - s, cy - s), (cx + s, cy + s)], fill=INK, width=wd)
        d.line([(cx - s, cy + s), (cx + s, cy - s)], fill=INK, width=wd)


def draw_tree(d, cx, cy, size):
    """Upright tree: trunk + three branch levels, ~size px tall, centered at (cx,cy)."""
    h = size
    d.line([(cx, cy + h // 2), (cx, cy - h // 2)], fill=INK, width=14)
    for i, frac in enumerate((0.15, 0.45, 0.75)):
        y = int(cy + h // 2 - frac * h)
        sp = int((1.0 - frac) * h * 0.45) + 30
        d.line([(cx, y), (cx - sp, y - sp // 2)], fill=INK, width=10)
        d.line([(cx, y), (cx + sp, y - sp // 2)], fill=INK, width=10)


def draw_insect(d, cx, cy, size, inverted=False):
    """Mayfly-like: round head + two big wing ellipses toward the head end + tapering
    tail filament away from it. Head UP when not inverted."""
    s = size
    sign = 1 if inverted else -1          # head direction on y axis
    head = (cx - s // 8, cy + sign * s // 2 - s // 8, cx + s // 8, cy + sign * s // 2 + s // 8)
    d.ellipse(head, fill=INK)
    d.ellipse((cx - s // 2, cy + sign * s // 4 - s // 6, cx - s // 12, cy + sign * s // 4 + s // 6), outline=INK, width=7)
    d.ellipse((cx + s // 12, cy + sign * s // 4 - s // 6, cx + s // 2, cy + sign * s // 4 + s // 6), outline=INK, width=7)
    d.line([(cx, cy + sign * s // 3), (cx, cy - sign * s // 2)], fill=INK, width=6)
    d.line([(cx, cy - sign * s // 2), (cx - s // 6, cy - sign * (s // 2 + s // 5))], fill=INK, width=4)
    d.line([(cx, cy - sign * s // 2), (cx + s // 6, cy - sign * (s // 2 + s // 5))], fill=INK, width=4)


def draw_corpse(d, cx, cy, size):
    """Shrouded-corpse-like: elongated rounded shroud outline + head bump, UPRIGHT
    (control-phase fix: the first, horizontal 146-px-tall version was shaped exactly like
    a text line and was text-dropped; the real p22 corpse is far taller than any line)."""
    h, w = size, size // 3
    d.rounded_rectangle((cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2),
                        radius=w // 2, outline=INK, width=9)
    d.ellipse((cx - w // 3, cy - h // 2 - 2 * w // 3, cx + w // 3, cy - h // 2),
              outline=INK, width=9)
    for i in range(1, 5):
        y = cy - h // 2 + i * h // 5
        d.line([(cx - w // 2, y), (cx + w // 2, y + w // 4)], fill=INK, width=5)


PLANTS = [
    # (page, type, orientation, cx, cy, size, kwargs)
    (5, "cross", "plus", 1200, 230, 160, {}),
    (5, "cross", "saltire", 420, 3320, 170, dict(saltire=True)),
    (5, "insect", "up", 2080, 3280, 130, {}),
    # tree moved p5(260,1700)->p33(2140,1000) during control phase: its first placement
    # sat ON TOP of a real left-margin vine scroll on p5 (a genuine census find) and the
    # two merged into one region, which tests nothing (run.log).
    (33, "tree", "up", 2140, 1000, 350, {}),
    (33, "cross", "plus", 2050, 260, 150, {}),
    (33, "insect", "down", 300, 1500, 130, dict(inverted=True)),
    # corpse moved (1200,3180)->(1850,3320) during control phase: first placement sat on
    # the REAL p33 bottom cuneiform cluster (W2-B2's channel) and merged with it (run.log)
    (33, "corpse_figure", "na", 1850, 3320, 440, {}),
]


def _ink_center(typ, ori, cx, cy, size, kw):
    """Ground-truth centroid = ink bbox center of the motif rendered alone (the nominal
    (cx,cy) of an asymmetric drawing is not its ink center; fixed during control phase,
    see run.log)."""
    canvas = Image.new("L", (2400, 3600), 255)
    d = ImageDraw.Draw(canvas)
    dict(cross=draw_cross, tree=draw_tree, insect=draw_insect,
         corpse_figure=draw_corpse)[typ](d, cx, cy, size, **kw)
    a = np.asarray(canvas) < 200
    ys, xs = np.where(a)
    return float((xs.min() + xs.max()) / 2), float((ys.min() + ys.max()) / 2)


def build():
    truth = []
    for page in (5, 33):
        im = Image.open(os.path.join(CD.RELIKD, "p%d.jpg" % page)).convert("RGB")
        d = ImageDraw.Draw(im)
        for (pg, typ, ori, cx, cy, size, kw) in PLANTS:
            if pg != page:
                continue
            dict(cross=draw_cross, tree=draw_tree, insect=draw_insect,
                 corpse_figure=draw_corpse)[typ](d, cx, cy, size, **kw)
            icx, icy = _ink_center(typ, ori, cx, cy, size, kw)
            truth.append(dict(page=pg, type=typ, orientation=ori, cx=icx, cy=icy, size=size))
        im.save(os.path.join(PW, "plant%d.jpg" % page), quality=92)
    json.dump(truth, open(os.path.join(PW, "truth.json"), "w"), indent=1)
    return truth


def run_detect():
    out = {}
    for page in (5, 33):
        path = os.path.join(PW, "plant%d.jpg" % page)
        regs, bands = CD.detect(path)
        CD.save_crops(path, regs, PW, "plant%02d" % page)
        out["p%d" % page] = dict(n_regions=len(regs), regions=regs)
        print("plant p%d: %d regions" % (page, len(regs)))
        for r in regs:
            print("  bbox", r["bbox"], r["mask_kind"], "crop", r["crop"])
    json.dump(out, open(os.path.join(PW, "detect_plant.json"), "w"), indent=1)
    return out


def score(classified_json):
    """classified_json: agent-written list of dicts (page,type,orientation,cx,cy) ->
    compare against truth at +/-10 px centroid, exact type, orientation where oriented."""
    truth = json.load(open(os.path.join(PW, "truth.json")))
    cls = json.load(open(classified_json))
    hits, misses = [], []
    for t in truth:
        m = [c for c in cls if c["page"] == t["page"] and c["type"] == t["type"] and
             abs(c["cx"] - t["cx"]) <= 10 and abs(c["cy"] - t["cy"]) <= 10]
        ok = bool(m) and (t["orientation"] in ("na",) or m[0]["orientation"] == t["orientation"])
        (hits if ok else misses).append(dict(truth=t, matched=m))
    res = dict(n_truth=len(truth), n_hit=len(hits), passed=len(hits) == len(truth),
               misses=misses)
    json.dump(res, open(os.path.join(PW, "pc1_score.json"), "w"), indent=1)
    print(json.dumps(res, indent=1)[:2000])
    return res


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "score":
        score(sys.argv[2])
    else:
        build()
        run_detect()
