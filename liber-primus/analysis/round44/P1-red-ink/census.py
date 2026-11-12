"""R44 / P1 step 1 — book-wide RED-MARK CENSUS of the 56 relikd masters.

Pre-registered in PREREG.md §4 (census C) BEFORE this file produced any output.

Red rule (verified, prior art analysis/armada_osint/redrune/): R-(G+B)/2>40 & R>120 & G<80.
Components (scipy.ndimage.label, 8-conn), noise floor area >= 20 px, each classified ONCE:
  RUNE_OVERLAP  overlaps a stones glyph box on that image
  DROP_CAP      height >= 300 px
  DOT           compact small blob (area <= 2500, max dim <= 60) -> clustered into blocks
  OTHER         everything else (bbox recorded for identification: numerals, p53 paragraph...)

Also reproduces the prior-art glyph-level red extraction (red-fraction > 0.30 per stones box)
as the census' validation gate: must yield 187 red text-runes and canon p0 red opening
HEOGMIAFSYENGC.

Usage: python3 census.py [--images DIR] [--out census.json]
  --images lets the plant lane point the SAME census code at modified page copies.
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
STONES = os.path.join(LP, "analysis", "stones")
from lp import gematria as gp  # noqa

Image.MAX_IMAGE_PIXELS = None
NOISE_AREA = 20
RED_FRAC_THR = 0.30
INK_THR = 128
DOT_MAX_AREA = 2500
DOT_MAX_DIM = 60
DROPCAP_MIN_H = 300
CLUSTER_GAP = 80  # px, union-find proximity for dot blocks


def red_mask(rgb):
    R = rgb[:, :, 0].astype(np.int16)
    G = rgb[:, :, 1].astype(np.int16)
    B = rgb[:, :, 2].astype(np.int16)
    return (R - (G + B) / 2 > 40) & (R > 120) & (G < 80)


def load_glyphs():
    """All 12,764 segmented glyphs with canon/classifier rune + box, keyed by image."""
    d = np.load(os.path.join(STONES, "dataset.npz"), allow_pickle=True)
    provall, boxesall = d["provall"], d["boxesall"]
    pred = np.load(os.path.join(STONES, "all_pred.npy"), allow_pickle=True)
    conf = np.load(os.path.join(STONES, "all_conf.npy"))
    glyphs = []
    for i in range(len(provall)):
        img, line, gi, gli, canon, match = provall[i]
        _, x0, x1, y0, y1 = boxesall[i]
        glyphs.append(dict(img=int(img), line=int(line), gi=int(gi), gli=int(gli),
                           rune=str(canon if canon is not None else pred[i]),
                           matched=bool(match), conf=float(conf[i]),
                           box=(int(x0), int(x1), int(y0), int(y1))))
    return glyphs


def box_red_fraction(rgb, red, x0, x1, y0, y1):
    sub, subred = rgb[y0:y1, x0:x1], red[y0:y1, x0:x1]
    ink = (sub.mean(2) < INK_THR) | subred
    n = int(ink.sum())
    return (int(subred.sum()) / n) if n else 0.0


def cluster_blocks(dots):
    """Union-find proximity clustering of dot components into blocks."""
    n = len(dots)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    cx = [( (d["x0"] + d["x1"]) / 2, (d["y0"] + d["y1"]) / 2) for d in dots]
    for i in range(n):
        for j in range(i + 1, n):
            # gap between bounding boxes
            dx = max(0, max(dots[i]["x0"], dots[j]["x0"]) - min(dots[i]["x1"], dots[j]["x1"]))
            dy = max(0, max(dots[i]["y0"], dots[j]["y0"]) - min(dots[i]["y1"], dots[j]["y1"]))
            if max(dx, dy) <= CLUSTER_GAP:
                parent[find(i)] = find(j)
    blocks = {}
    for i in range(n):
        blocks.setdefault(find(i), []).append(i)
    out = []
    for members in blocks.values():
        xs0 = min(dots[i]["x0"] for i in members); xs1 = max(dots[i]["x1"] for i in members)
        ys0 = min(dots[i]["y0"] for i in members); ys1 = max(dots[i]["y1"] for i in members)
        out.append(dict(n_dots=len(members), bbox=[xs0, xs1, ys0, ys1],
                        dot_ids=sorted(members)))
    out.sort(key=lambda b: (b["bbox"][2], b["bbox"][0]))
    return out


def census_image(path, glyph_boxes):
    rgb = np.asarray(Image.open(path).convert("RGB"))
    red = red_mask(rgb)
    lab, nlab = ndimage.label(red, structure=np.ones((3, 3), dtype=np.int8))
    comps = []
    if nlab:
        objs = ndimage.find_objects(lab)
        areas = ndimage.sum_labels(red, lab, index=np.arange(1, nlab + 1))
        for k, sl in enumerate(objs):
            a = int(areas[k])
            if a < NOISE_AREA or sl is None:
                continue
            y0, y1 = sl[0].start, sl[0].stop
            x0, x1 = sl[1].start, sl[1].stop
            comps.append(dict(x0=int(x0), x1=int(x1), y0=int(y0), y1=int(y1),
                              area=a, h=int(y1 - y0), w=int(x1 - x0)))
    # classify
    for c in comps:
        overl = any(c["x0"] < bx1 and c["x1"] > bx0 and c["y0"] < by1 and c["y1"] > by0
                    for (bx0, bx1, by0, by1) in glyph_boxes)
        if overl:
            c["cls"] = "RUNE_OVERLAP"
        elif c["h"] >= DROPCAP_MIN_H:
            c["cls"] = "DROP_CAP"
        elif c["area"] <= DOT_MAX_AREA and max(c["h"], c["w"]) <= DOT_MAX_DIM:
            c["cls"] = "DOT"
        else:
            c["cls"] = "OTHER"
    dots = [c for c in comps if c["cls"] == "DOT"]
    blocks = cluster_blocks(dots) if dots else []
    return rgb, red, comps, blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", default=os.path.join(LP, "data", "relikd"))
    ap.add_argument("--out", default=os.path.join(HERE, "census.json"))
    ap.add_argument("--no-validate", action="store_true",
                    help="skip the 187/p0 validation gate (plant workspaces)")
    args = ap.parse_args()

    glyphs = load_glyphs()
    by_img = {}
    for g in glyphs:
        by_img.setdefault(g["img"], []).append(g)

    align = json.load(open(os.path.join(STONES, "alignment.json")))
    gli_to_page = {gl: int(pg) for pg, gls in align.items() for gl in gls}

    # census scope = every pN.jpg master, including pages with no stones glyphs (e.g. p50)
    import re
    all_imgs = sorted(int(m.group(1)) for f in os.listdir(args.images)
                      for m in [re.match(r"^p(\d+)\.(jpg|png)$", f)] if m)

    out = dict(images={}, totals={}, red_glyphs=[], blocks=[])
    cls_tot = {}
    for img in all_imgs:
        path = os.path.join(args.images, f"p{img}.jpg")
        if not os.path.exists(path):
            path = os.path.join(args.images, f"p{img}.png")
        if not os.path.exists(path):
            continue
        gb = [g["box"] for g in by_img.get(img, [])]
        rgb, red, comps, blocks = census_image(path, gb)
        # glyph-level red extraction (prior-art rule)
        page_red = []
        for g in by_img.get(img, []):
            x0, x1, y0, y1 = g["box"]
            fr = box_red_fraction(rgb, red, x0, x1, y0, y1)
            if fr > RED_FRAC_THR:
                page_red.append(dict(img=img, gli=g["gli"], gi=g["gi"], rune=g["rune"],
                                     frac=round(fr, 3), canon_page=gli_to_page.get(g["gli"]),
                                     box=list(g["box"])))
        out["red_glyphs"].extend(page_red)
        for b in blocks:
            b["img"] = img
        out["blocks"].extend(blocks)
        tally = {}
        for c in comps:
            tally[c["cls"]] = tally.get(c["cls"], 0) + 1
            cls_tot[c["cls"]] = cls_tot.get(c["cls"], 0) + 1
        out["images"][str(img)] = dict(
            n_components=len(comps), tally=tally,
            red_px=int(red.sum()),
            n_red_glyphs=len(page_red),
            others=[dict(bbox=[c["x0"], c["x1"], c["y0"], c["y1"]], area=c["area"])
                    for c in comps if c["cls"] == "OTHER"],
            dropcaps=[dict(bbox=[c["x0"], c["x1"], c["y0"], c["y1"]], area=c["area"])
                      for c in comps if c["cls"] == "DROP_CAP"])
        print(f"p{img}: comps={len(comps)} {tally} red_glyphs={len(page_red)} "
              f"blocks={[b['n_dots'] for b in blocks]}", flush=True)

    out["red_glyphs"].sort(key=lambda g: (g["gli"], g["gi"]))
    out["totals"] = dict(components=cls_tot, n_red_glyphs=len(out["red_glyphs"]),
                         n_blocks=len(out["blocks"]),
                         block_dot_counts=[b["n_dots"] for b in sorted(
                             out["blocks"], key=lambda b: (b["img"], b["bbox"][2]))])

    if not args.no_validate:
        reds = out["red_glyphs"]
        n = len(reds)
        p0 = "".join(g["rune"] for g in reds if g["canon_page"] == 0)
        p0_lat = gp.indices_to_translit([gp.RUNE_TO_IDX[r] for r in p0 if r in gp.RUNE_TO_IDX])
        ok = (n == 187) and (p0_lat == "HEOGMIAFSYENGC")
        out["validation"] = dict(n_red_glyphs=n, expect=187,
                                 p0_red=p0_lat, expect_p0="HEOGMIAFSYENGC",
                                 passed=bool(ok))
        print(f"VALIDATION: n={n}/187  p0={p0_lat}  passed={ok}")

    json.dump(out, open(args.out, "w"), indent=1)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
