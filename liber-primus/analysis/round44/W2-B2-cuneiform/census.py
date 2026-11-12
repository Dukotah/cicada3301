"""R44 / W2-B2 step 1 — book-wide BLACK NON-RUNIC INK CENSUS of the 57 relikd masters.

Pre-registered in PREREG.md (hash-stamped in run.log) BEFORE this file produced any output.

Mask: luminance mean(RGB) < 128 AND NOT red (P1's verified red rule — red is R44-P1's
censused territory). Components scipy.ndimage.label 8-conn, area >= 20 px. Each classified
exactly ONCE, priority order (PREREG §3):
  RUNE_GLYPH    overlaps a stones glyph box padded 6 px
  BAND_COVERED  center inside one of the round19/C3 band boxes whose ink_class != "TEXT"
                (A-06 territory; TEXT-class band boxes are the rune text column itself --
                including them swallowed in-text marks and failed PC-B; glue fix #1, run.log)
  TEXT_PUNCT    small (area<=2500, maxdim<=60), center inside a stones text-line bbox
                padded x+-40 / y+-10 (word separators / punctuation, logged in canon)
  UNLOGGED      the census target -> proximity-clustered into OBJECTS at gap <= 100 px

Usage: python3 census.py [--images DIR] [--out census.json] [--pages p1,p2] [--no-crops]
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
BANDS = os.path.join(LP, "analysis", "round19", "C3", "l3", "bands.json")

Image.MAX_IMAGE_PIXELS = None
NOISE_AREA = 20
INK_THR = 128
PAD_GLYPH = 6
PUNCT_MAX_AREA = 2500
PUNCT_MAX_DIM = 60
LINE_PAD_X = 40
LINE_PAD_Y = 10
CLUSTER_GAP = 100


def red_mask(rgb):
    R = rgb[:, :, 0].astype(np.int16)
    G = rgb[:, :, 1].astype(np.int16)
    B = rgb[:, :, 2].astype(np.int16)
    return (R - (G + B) / 2 > 40) & (R > 120) & (G < 80)


def load_glyphs():
    d = np.load(os.path.join(STONES, "dataset.npz"), allow_pickle=True)
    provall, boxesall = d["provall"], d["boxesall"]
    pred = np.load(os.path.join(STONES, "all_pred.npy"), allow_pickle=True)
    by_img = {}
    for i in range(len(provall)):
        img, line, gi, gli, canon, match = provall[i]
        _, x0, x1, y0, y1 = boxesall[i]
        by_img.setdefault(int(img), []).append(dict(
            line=int(line), gi=int(gi), gli=int(gli),
            rune=str(canon if canon is not None else pred[i]),
            box=(int(x0), int(x1), int(y0), int(y1))))
    return by_img


def line_boxes(glyphs):
    """Per-gli text-line bbox from the stones glyph boxes."""
    lines = {}
    for g in glyphs:
        x0, x1, y0, y1 = g["box"]
        b = lines.setdefault(g["gli"], [x0, x1, y0, y1])
        b[0] = min(b[0], x0); b[1] = max(b[1], x1)
        b[2] = min(b[2], y0); b[3] = max(b[3], y1)
    return list(lines.values())


def cluster_objects(comps):
    n = len(comps)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i in range(n):
        for j in range(i + 1, n):
            dx = max(0, max(comps[i]["x0"], comps[j]["x0"]) - min(comps[i]["x1"], comps[j]["x1"]))
            dy = max(0, max(comps[i]["y0"], comps[j]["y0"]) - min(comps[i]["y1"], comps[j]["y1"]))
            if max(dx, dy) <= CLUSTER_GAP:
                parent[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    out = []
    for members in groups.values():
        xs0 = min(comps[i]["x0"] for i in members); xs1 = max(comps[i]["x1"] for i in members)
        ys0 = min(comps[i]["y0"] for i in members); ys1 = max(comps[i]["y1"] for i in members)
        out.append(dict(n_components=len(members), bbox=[xs0, xs1, ys0, ys1],
                        area=sum(comps[i]["area"] for i in members),
                        comp_ids=sorted(members)))
    out.sort(key=lambda b: (b["bbox"][2], b["bbox"][0]))
    return out


def census_image(path, glyph_boxes, lboxes, band_boxes):
    rgb = np.asarray(Image.open(path).convert("RGB"))
    lum = rgb.mean(axis=2)
    black = (lum < INK_THR) & ~red_mask(rgb)
    lab, nlab = ndimage.label(black, structure=np.ones((3, 3), dtype=np.int8))
    comps = []
    if nlab:
        objs = ndimage.find_objects(lab)
        areas = ndimage.sum_labels(black, lab, index=np.arange(1, nlab + 1))
        for k, sl in enumerate(objs):
            a = int(areas[k])
            if a < NOISE_AREA or sl is None:
                continue
            y0, y1 = int(sl[0].start), int(sl[0].stop)
            x0, x1 = int(sl[1].start), int(sl[1].stop)
            comps.append(dict(x0=x0, x1=x1, y0=y0, y1=y1, area=a,
                              h=y1 - y0, w=x1 - x0))
    for c in comps:
        cx, cy = (c["x0"] + c["x1"]) / 2, (c["y0"] + c["y1"]) / 2
        if any(c["x0"] < bx1 + PAD_GLYPH and c["x1"] > bx0 - PAD_GLYPH and
               c["y0"] < by1 + PAD_GLYPH and c["y1"] > by0 - PAD_GLYPH
               for (bx0, bx1, by0, by1) in glyph_boxes):
            c["cls"] = "RUNE_GLYPH"
        elif any(bx0 <= cx <= bx1 and by0 <= cy <= by1 for (bx0, bx1, by0, by1) in band_boxes):
            c["cls"] = "BAND_COVERED"
        elif (c["area"] <= PUNCT_MAX_AREA and max(c["h"], c["w"]) <= PUNCT_MAX_DIM and
              any(lx0 - LINE_PAD_X <= cx <= lx1 + LINE_PAD_X and
                  ly0 - LINE_PAD_Y <= cy <= ly1 + LINE_PAD_Y
                  for (lx0, lx1, ly0, ly1) in lboxes)):
            c["cls"] = "TEXT_PUNCT"
        else:
            c["cls"] = "UNLOGGED"
    unlogged = [c for c in comps if c["cls"] == "UNLOGGED"]
    objects = cluster_objects(unlogged) if unlogged else []
    return rgb, comps, objects


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", default=os.path.join(LP, "data", "relikd"))
    ap.add_argument("--out", default=os.path.join(HERE, "census.json"))
    ap.add_argument("--pages", default=None, help="comma list like p23,p33 (default: all)")
    ap.add_argument("--no-crops", action="store_true")
    args = ap.parse_args()

    by_img = load_glyphs()
    bands = json.load(open(BANDS))
    bands_by_page = {}
    for b in bands:
        if b.get("ink_class") == "TEXT":
            continue  # the rune text column itself; not a band exclusion (glue fix #1)
        bands_by_page.setdefault(b["page"], []).append(
            (b["x"][0], b["x"][1], b["y"][0], b["y"][1]))

    names = (args.pages.split(",") if args.pages else
             ["p%d" % i for i in range(56)] + ["0_wisdom"])
    cropdir = os.path.join(HERE, "crops")
    os.makedirs(cropdir, exist_ok=True)

    out = dict(images={}, totals={})
    totals = {}
    for name in names:
        path = os.path.join(args.images, name + ".jpg")
        if not os.path.exists(path):
            out["images"][name] = dict(missing=True)
            continue
        pno = int(name[1:]) if name.startswith("p") else None
        glyphs = by_img.get(pno, []) if pno is not None else []
        gboxes = [g["box"] for g in glyphs]
        lboxes = line_boxes(glyphs)
        bboxes = bands_by_page.get(pno, []) if pno is not None else []
        rgb, comps, objects = census_image(path, gboxes, lboxes, bboxes)
        counts = {}
        for c in comps:
            counts[c["cls"]] = counts.get(c["cls"], 0) + 1
            totals[c["cls"]] = totals.get(c["cls"], 0) + 1
        for oi, o in enumerate(objects):
            o["id"] = "%s_obj%d" % (name, oi)
            if not args.no_crops:
                x0, x1, y0, y1 = o["bbox"]
                m = 25
                crop = rgb[max(0, y0 - m):y1 + m, max(0, x0 - m):x1 + m]
                Image.fromarray(crop).save(os.path.join(cropdir, o["id"] + ".png"))
        out["images"][name] = dict(
            counts=counts,
            unlogged_components=[c for c in comps if c["cls"] == "UNLOGGED"],
            objects=objects)
        print(name, counts, "objects:", len(objects), flush=True)
    out["totals"] = totals
    out["params"] = dict(noise_area=NOISE_AREA, ink_thr=INK_THR, pad_glyph=PAD_GLYPH,
                         punct_max_area=PUNCT_MAX_AREA, punct_max_dim=PUNCT_MAX_DIM,
                         line_pad=[LINE_PAD_X, LINE_PAD_Y], cluster_gap=CLUSTER_GAP)
    json.dump(out, open(args.out, "w"), indent=1)
    print("totals:", totals)


if __name__ == "__main__":
    main()
