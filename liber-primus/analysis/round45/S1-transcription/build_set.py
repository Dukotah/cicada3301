"""R45/S1 — build the blind read set (PREREG.md §3), seal canon, render montages.

Run from liber-primus/:  PYTHONUTF8=1 python analysis/round45/S1-transcription/build_set.py
Outputs (this dir):  sealed_manifest.json  (canon values — do NOT open before blind_reads.json)
                     items_blind.json      (ids, kind, montage — no canon)
                     crops/*.png           (montages + reference chart; gitignore, regenerable)
"""
import hashlib
import json
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP)
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis", "stones"))
from lp import gematria as gp  # noqa: E402
import pipeline as P  # noqa: E402

SEED = 45013
CROPS = os.path.join(HERE, "crops")
os.makedirs(CROPS, exist_ok=True)
CTRL_DIR = os.path.join(os.path.dirname(LP), "corpus", "A-primary-artifacts", "cijhho123", "2014",
                        "Liber Primus", "liber primus images full")
FAMILIES = [set("ᚩᚪᚫ"), set("ᚱᚹ"), set("ᛗᛞ"), set("ᚾᛁ"), set("ᛒᛖ")]
PIN = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
H = 170  # render height per glyph (addendum A1: was 100)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ---------------------------------------------------------------- canon stream + mapping
gl, po = P.global_lines()
pos_map = []  # global pos -> (global line, idx in line)
for li, L in enumerate(gl):
    for j in range(len(L)):
        pos_map.append((li, j))
x = [gp.RUNE_TO_IDX[c] for L in gl for c in L]
flat = [c for L in gl for c in L]
assert hashlib.sha256(",".join(map(str, x)).encode()).hexdigest() == PIN
N = len(x)

# ---------------------------------------------------------------- image hashes
pins = json.load(open("analysis/round19/C3/l3/hashes.json"))
for n in range(56):
    assert sha(f"data/relikd/p{n}.jpg") == pins["target_renders"][f"p{n}.jpg"]["sha256"], n
for k in ("73.jpg", "74.jpg"):
    assert sha(os.path.join(CTRL_DIR, k)) == pins["control_renders"][k]["sha256"], k

# ---------------------------------------------------------------- segmentation (all 56)
align = json.load(open("analysis/stones/alignment.json"))
line_loc = {}  # global line -> dict(img, boxes, exact)
grays = {}
for n in range(56):
    lines, b, gray = P.segment_image(f"data/relikd/p{n}.jpg")
    grays[n] = np.asarray(gray)
    clean = [L for L in lines if len(L) >= 10]
    for i, gli in enumerate(align[str(n)]):
        if i >= len(clean):
            break
        line_loc[gli] = {"img": n, "boxes": clean[i], "exact": len(clean[i]) == len(gl[gli])}


def locate(gpos):
    li, j = pos_map[gpos]
    L = line_loc.get(li)
    if L is None:
        return None
    if L["exact"]:
        return ("box", L["img"], L["boxes"][j])
    m, n = len(L["boxes"]), len(gl[li])
    k = int(round(j * (m - 1) / max(1, n - 1)))
    return ("win", L["img"], L["boxes"], k)


# ---------------------------------------------------------------- sampling
rng = random.Random(SEED)
blocks = [(b * 5, b * 5 + 4) for b in range(11)]
F1 = []
block_sizes = []
for lo, hi in blocks:
    cand = [i for i in range(N) if lo <= po[pos_map[i][0]] <= hi]
    block_sizes.append(len(cand))
    F1 += [(i, f"{lo}-{hi}") for i in rng.sample(cand, 6)]
dbl = [i for i in range(N - 1) if x[i] == x[i + 1]]
fam = lambda a, b: a != b and any(a in f and b in f for f in FAMILIES)  # noqa: E731
near = [i for i in range(N - 1) if fam(flat[i], flat[i + 1])]
F3 = sorted(rng.sample(near, 40))
excl = set(dbl) | set(near)
F4 = sorted(rng.sample([i for i in range(N - 1) if i not in excl], 40))

# controls: solved pages = canon segments 55, 56 rendered as 73.jpg / 74.jpg
segs = open("data/krisyotam_runes.txt", encoding="utf-8").read().split("%")
ctrl_pool = []
for seg, img in ((55, "73.jpg"), (56, "74.jpg")):
    clines = [[c for c in l if c in P.RUNES] for l in segs[seg].split("/")]
    clines = [c for c in clines if c]
    lines, b, gray = P.segment_image(os.path.join(CTRL_DIR, img))
    grays[img] = np.asarray(gray)
    seglines = [L for L in lines if len(L) >= 3]
    # match image lines to canon lines in order by exact count
    ci = 0
    for L in seglines:
        while ci < len(clines) and len(clines[ci]) != len(L):
            ci += 1
        if ci >= len(clines):
            break
        for j, box in enumerate(L):
            ctrl_pool.append((img, box, clines[ci][j], seg, ci, j))
        ci += 1
print("control pool", len(ctrl_pool), "doublets", len(dbl), "near", len(near))
C = rng.sample(ctrl_pool, 24)


# ---------------------------------------------------------------- rendering
def crop_box(img_key, box, pad=10, fade=True):
    a = grays[img_key].astype(np.float32)
    y0, y1 = max(0, box["y0"] - pad), box["y1"] + pad
    x0, x1 = max(0, box["x0"] - pad - (14 if fade else 0)), box["x1"] + pad + (14 if fade else 0)
    sub = a[y0:y1, x0:x1].copy()
    if fade:  # addendum A1: fade ink outside the target box so neighbours don't read as strokes
        m = np.ones_like(sub, dtype=bool)
        m[box["y0"] - y0:box["y1"] - y0, box["x0"] - x0:box["x1"] - x0] = False
        sub[m] = 255 - (255 - sub[m]) * 0.18
    im = Image.fromarray(sub.astype(np.uint8))
    w = max(1, int(im.width * H / im.height))
    return im.resize((w, H), Image.LANCZOS)


def crop_window(img, boxes, k, extra=4, k2=None):
    lo = max(0, k - extra)
    hi = min(len(boxes) - 1, (k2 if k2 is not None else k) + extra)
    bb = boxes[lo:hi + 1]
    box = {"x0": min(b["x0"] for b in bb), "x1": max(b["x1"] for b in bb),
           "y0": min(b["y0"] for b in bb), "y1": max(b["y1"] for b in bb)}
    return crop_box(img, box, pad=12, fade=False), (lo, hi)


def hcat(ims, gap=24):
    w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    out = Image.new("L", (w, H), 255)
    xo = 0
    for i in ims:
        out.paste(i, (xo, 0))
        xo += i.width + gap
    return out


items = []  # (kind, image, sealed record)


def add_glyph_item(frame, gpos, extra_meta):
    loc = locate(gpos)
    li, j = pos_map[gpos]
    rec = {"frame": frame, "gpos": gpos, "page": po[li], "gline": li, "pos_in_line": j,
           "canon": flat[gpos], **extra_meta}
    if loc is None:
        rec["located"] = "unaligned-line"
        return items.append(("unloc", None, rec))
    if loc[0] == "box":
        rec["located"] = "exact-box"
        return items.append(("single", crop_box(loc[1], loc[2]), rec))
    im, (lo, hi) = crop_window(loc[1], loc[2], loc[3])
    rec.update(located="window", img=loc[1], est_box=loc[3], win_boxes=[lo, hi],
               canon_line=gl[li])
    items.append(("window", im, rec))


def add_pair_item(frame, gpos):
    rec = {"frame": frame, "gpos": gpos, "canon": flat[gpos] + flat[gpos + 1],
           "page": po[pos_map[gpos][0]], "gline": pos_map[gpos][0],
           "pos_in_line": pos_map[gpos][1], "gline2": pos_map[gpos + 1][0]}
    l1, l2 = locate(gpos), locate(gpos + 1)
    if l1 and l2 and l1[0] == "box" and l2[0] == "box":
        rec["located"] = "exact-box"
        return items.append(("pair", hcat([crop_box(l1[1], l1[2]), crop_box(l2[1], l2[2])]), rec))
    parts = []
    for gp_, loc in ((gpos, l1), (gpos + 1, l2)):
        li, j = pos_map[gp_]
        if loc is None:
            rec["located"] = "unaligned-line"
            return items.append(("unloc", None, rec))
        if loc[0] == "box":
            parts.append(crop_box(loc[1], loc[2]))
        else:
            parts.append(None)
    # at least one in a mismatched line: render one window covering the pair (same line) or windows
    ims, wins = [], []
    for gp_, loc in ((gpos, l1), (gpos + 1, l2)):
        if loc[0] == "win":
            im, w = crop_window(loc[1], loc[2], loc[3])
            ims.append(im)
            wins.append({"gpos": gp_, "img": loc[1], "est_box": loc[3], "win_boxes": w,
                         "canon_line": gl[pos_map[gp_][0]], "pos_in_line": pos_map[gp_][1]})
            if l1[0] == "win" and l2[0] == "win" and pos_map[gpos][0] == pos_map[gpos + 1][0]:
                break  # same line window already covers both
        else:
            ims.append(crop_box(loc[1], loc[2]))
            wins.append({"gpos": gp_, "exact": True})
    rec.update(located="window", windows=wins)
    items.append(("pairwin", hcat(ims, gap=60), rec))


for gpos, blk in F1:
    add_glyph_item("F1", gpos, {"block": blk})
for (img, box, rune, seg, ci, j) in C:
    items.append(("single", crop_box(img, box), {"frame": "C", "canon": rune, "img": img,
                                                  "seg": seg, "cline": ci, "pos_in_line": j,
                                                  "located": "exact-box"}))
for i in dbl:
    add_pair_item("F2", i)
for i in F3:
    add_pair_item("F3", i)
for i in F4:
    add_pair_item("F4", i)

# opaque ids, shuffled within render class
rng2 = random.Random(SEED + 1)
order = list(range(len(items)))
rng2.shuffle(order)
sealed, blind = {}, []
groups = {"single": [], "pair": [], "window": [], "pairwin": [], "unloc": []}
for n_, idx in enumerate(order):
    kind, im, rec = items[idx]
    iid = f"K{n_:03d}"
    sealed[iid] = {"kind": kind, **rec}
    groups[kind].append((iid, im))


def montage(name, entries, cols, cell_w):
    rows = (len(entries) + cols - 1) // cols
    cell_h = H + 34
    entries = list(entries)
    out = Image.new("L", (cols * cell_w, rows * cell_h), 255)
    d = ImageDraw.Draw(out)
    try:
        f = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        f = ImageFont.load_default()
    for k, (iid, im) in enumerate(entries):
        r, c = divmod(k, cols)
        x0, y0 = c * cell_w, r * cell_h
        if im.width > cell_w - 10:
            im = im.resize((cell_w - 10, int(H * (cell_w - 10) / im.width)))
        out.paste(im, (x0 + 5, y0 + 2))
        d.text((x0 + 6, y0 + H + 6), iid, fill=0, font=f)
        d.rectangle([x0, y0, x0 + cell_w - 1, y0 + cell_h - 1], outline=180)
    out.save(os.path.join(CROPS, name))
    return name


mont = {}
for kind, per, cols, cw in (("single", 12, 4, 200), ("pair", 8, 2, 420),
                            ("window", 3, 1, 1500), ("pairwin", 3, 1, 1500)):
    ents = groups[kind]
    for m in range(0, len(ents), per):
        nm = montage(f"{kind}_{m // per:02d}.png", ents[m:m + per], cols, cw)
        for iid, _ in ents[m:m + per]:
            mont[iid] = nm
for iid, _ in groups["unloc"]:
    mont[iid] = None

# reference chart: class means over the Campaign-V dataset (aggregate; PREREG §2 conditional)
DS = np.load("analysis/stones/dataset.npz", allow_pickle=True)
X, y = DS["X"], DS["y"]
cells = []
for r in gp.RUNES if hasattr(gp, "RUNES") else sorted(set(y), key=lambda r: gp.RUNE_TO_IDX[r]):
    sel = X[y == r]
    if len(sel) == 0:
        continue
    mean = (1 - sel.mean(0).reshape(56, 40)) * 255
    im = Image.fromarray(mean.astype(np.uint8)).resize((80, 112))
    cells.append((r, im))
chart = Image.new("L", (10 * 120, 3 * 150), 255)
d = ImageDraw.Draw(chart)
try:
    f = ImageFont.truetype("arial.ttf", 18)
except OSError:
    f = ImageFont.load_default()
for k, (r, im) in enumerate(cells):
    rr, cc = divmod(k, 10)
    chart.paste(im, (cc * 120 + 20, rr * 150))
    d.text((cc * 120 + 20, rr * 150 + 115), f"{gp.RUNE_TO_IDX[r]} {gp.RUNE_TO_TRANS[r]}", fill=0, font=f)
chart.save(os.path.join(CROPS, "reference_chart.png"))

json.dump({"seed": SEED, "block_sizes": block_sizes, "n_doublets": len(dbl), "n_near": len(near),
           "items": sealed}, open(os.path.join(HERE, "sealed_manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for iid, rec in sealed.items():
    blind.append({"id": iid, "kind": rec["kind"], "montage": mont[iid]})
json.dump(blind, open(os.path.join(HERE, "items_blind.json"), "w"), indent=1)
print({k: len(v) for k, v in groups.items()}, "montages", sorted(set(m for m in mont.values() if m)))
