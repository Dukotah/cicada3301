"""R45/S1b — build blind line montages (pass L) and pair deck (pass P); seal canon.

Run from liber-primus/:  PYTHONUTF8=1 python analysis/round45/S1b-hidden-doublets/build.py
Outputs: sealed_lines.json, sealed_pairs.json (DO NOT OPEN before reads are frozen),
         items_L.json, items_P.json (opaque ids only), crops/L_*.png, crops/P_*.png
"""
import hashlib, json, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP)
sys.path.insert(0, os.path.join(LP, "src")); sys.path.insert(0, os.path.join(LP, "analysis", "stones"))
from lp import gematria as gp  # noqa: E402
import pipeline as P  # noqa: E402

CROPS = os.path.join(HERE, "crops"); os.makedirs(CROPS, exist_ok=True)
PIN = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
FAMILIES = [set("ᚩᚪᚫ"), set("ᚦᚹ"), set("ᚱᚹ"), set("ᛗᛞ"), set("ᚾᛁ"), set("ᛒᛖ")]
INTERVALS = [(1560, 1625), (3035, 4040), (9565, 9630)]  # pair axis, inclusive
H = 170
SC = 1.8  # addendum B1: line strips upscaled
FONT = ImageFont.truetype("arial.ttf", 22)

gl, po = P.global_lines()
pos_map, start = [], []
for li, L in enumerate(gl):
    start.append(len(pos_map))
    pos_map += [(li, j) for j in range(len(L))]
flat = [c for L in gl for c in L]
x = [gp.RUNE_TO_IDX[c] for c in flat]
assert hashlib.sha256(",".join(map(str, x)).encode()).hexdigest() == PIN
N = len(x)
pins = json.load(open("analysis/round19/C3/l3/hashes.json"))

target_pairs = [t for lo, hi in INTERVALS for t in range(lo, hi + 1)]
target_lines = sorted({pos_map[t][0] for t in target_pairs} | {pos_map[t + 1][0] for t in target_pairs})

# ---------------------------------------------------------------- registration (S1 corrected map)
cm = json.load(open("analysis/round45/S1-transcription/corrected_map.json"))
reg = {}  # gline -> (img, clean_i)
for img, rows in cm.items():
    for r in rows:
        if r["true_gline"] is not None:
            reg[r["true_gline"]] = (int(img), r["clean_i"])

segs, grays = {}, {}
def seg(n):
    if n not in segs:
        p = f"data/relikd/p{n}.jpg"
        assert hashlib.sha256(open(p, "rb").read()).hexdigest() == pins["target_renders"][f"p{n}.jpg"]["sha256"]
        lines, b, gray = P.segment_image(p)
        segs[n] = [L for L in lines if len(L) >= 3]
        grays[n] = np.asarray(gray)
    return segs[n]

def line_boxes(g):
    """(img, boxes) for canon line g, via corrected map; short lines 166/167 via neighbour lines."""
    if g in reg:
        n, ci = reg[g]
        clean = [L for L in seg(n) if len(L) >= 10]
        return n, clean[ci]
    if g in (166, 167):
        # 166 = line after canon 165 on its image; 167 = line before canon 168 on its image
        nb = 165 if g == 166 else 168
        n, ci = reg[nb]
        al = seg(n); clean = [L for L in al if len(L) >= 10]
        k = next(i for i, L in enumerate(al) if L is clean[ci])
        k2 = k + 1 if g == 166 else k - 1
        return n, al[k2]
    return None

# ---------------------------------------------------------------- selection
rng = random.Random(45120)
dbl = [t for t in range(N - 1) if x[t] == x[t + 1]]
fam = lambda a, b: a != b and any(a in f and b in f for f in FAMILIES)  # noqa: E731
tl = set(target_lines)

def exact(g):
    lb = line_boxes(g)
    return lb is not None and len(lb[1]) == len(gl[g])

def pair_ok(t):  # both glyphs on exact-registered lines
    return exact(pos_map[t][0]) and exact(pos_map[t + 1][0])

outside_dbl = [t for t in dbl if pos_map[t][0] not in tl and pos_map[t + 1][0] not in tl
               and pos_map[t][0] == pos_map[t + 1][0]]
outside_dbl_ok = [t for t in outside_dbl if pair_ok(t)]
ctrl_d = rng.sample(outside_dbl_ok, 30)
outside_fam = [t for t in range(N - 1) if fam(flat[t], flat[t + 1]) and pos_map[t][0] not in tl
               and pos_map[t][0] == pos_map[t + 1][0]]
rng.shuffle(outside_fam)
ctrl_f = []
for t in outside_fam:
    if len(ctrl_f) == 30: break
    if pair_ok(t): ctrl_f.append(t)
tgt_fam = [t for t in target_pairs if fam(flat[t], flat[t + 1])]
tgt_fam_ok = [t for t in tgt_fam if pair_ok(t)]
tgt_fam_not = [t for t in tgt_fam if not pair_ok(t)]
others = [t for t in target_pairs if t not in set(tgt_fam) and pair_ok(t)]
decoys = rng.sample(others, 20)
# control lines: exact, outside target, containing a doublet not in ctrl_d
cl_cand = sorted({pos_map[t][0] for t in outside_dbl if t not in ctrl_d and exact(pos_map[t][0])})
ctrl_lines = rng.sample(cl_cand, 8)

# ---------------------------------------------------------------- rendering helpers
def crop_box(n, box, pad=10, fade=True):
    a = grays[n].astype(np.float32)
    y0, y1 = max(0, box["y0"] - pad), box["y1"] + pad
    x0, x1 = max(0, box["x0"] - pad - 14), box["x1"] + pad + 14
    sub = a[y0:y1, x0:x1].copy()
    if fade:
        m = np.ones_like(sub, dtype=bool)
        m[box["y0"] - y0:box["y1"] - y0, box["x0"] - x0:box["x1"] - x0] = False
        sub[m] = 255 - (255 - sub[m]) * 0.18
    im = Image.fromarray(sub.astype(np.uint8))
    return im.resize((max(1, int(im.width * H / im.height)), H), Image.LANCZOS)

def glyph_box(t):
    g, j = pos_map[t]
    n, boxes = line_boxes(g)
    return n, boxes[j]

def strip_rows(n, boxes):
    """two half-strips of the line, unfaded, with box numbers under each box."""
    rows = []
    half = (len(boxes) + 1) // 2
    for lo, hi in ((0, half), (half, len(boxes))):
        bb = boxes[lo:hi]
        X0 = max(0, min(b["x0"] for b in bb) - 30); X1 = max(b["x1"] for b in bb) + 30
        Y0 = max(0, min(b["y0"] for b in bb) - 15); Y1 = max(b["y1"] for b in bb) + 15
        sub = Image.fromarray(grays[n][Y0:Y1, X0:X1].astype(np.uint8))
        sub = sub.resize((int(sub.width * SC), int(sub.height * SC)), Image.LANCZOS)  # addendum B1
        im = Image.new("L", (sub.width, sub.height + 30), 255); im.paste(sub, (0, 0))
        d = ImageDraw.Draw(im)
        for k, b in enumerate(bb):
            d.text((((b["x0"] + b["x1"]) / 2 - X0) * SC - 8, sub.height + 3), str(lo + k), fill=0, font=FONT)
        rows.append(im)
    return rows

# ---------------------------------------------------------------- pass L
line_items = [("T", g) for g in target_lines] + [("C", g) for g in ctrl_lines]
rng.shuffle(line_items)
sealed_L, items_L = {}, []
for k, (kind, g) in enumerate(line_items):
    lid = f"L{k:02d}"
    n, boxes = line_boxes(g)
    sealed_L[lid] = {"kind": kind, "gline": g, "img": n, "page": po[g], "start": start[g],
                     "canon": "".join(gl[g]), "nseg": len(boxes)}
    items_L.append({"id": lid, "nseg": len(boxes)})
    rows = strip_rows(n, boxes)
    W = max(r.width for r in rows) + 20
    out = Image.new("L", (W, sum(r.height + 40 for r in rows) + 10), 255)
    d = ImageDraw.Draw(out); y = 5
    for i, r in enumerate(rows):
        d.text((5, y), f"{lid} part {i+1}/2", fill=0, font=FONT); y += 30
        out.paste(r, (10, y)); y += r.height + 10
    out.save(os.path.join(CROPS, f"{lid}.png"))

# ---------------------------------------------------------------- pass P
deck = ([("T-fam", t) for t in tgt_fam_ok] + [("C-dbl", t) for t in ctrl_d] +
        [("C-fam", t) for t in ctrl_f] + [("T-decoy", t) for t in decoys])
rng.shuffle(deck)
sealed_P, tiles = {}, []
for k, (kind, t) in enumerate(deck):
    pid = f"P{k:03d}"
    n1, b1 = glyph_box(t); n2, b2 = glyph_box(t + 1)
    a, b = crop_box(n1, b1), crop_box(n2, b2)
    tile = Image.new("L", (a.width + b.width + 24, H + 32), 255)
    tile.paste(a, (0, 32)); tile.paste(b, (a.width + 24, 32))
    ImageDraw.Draw(tile).text((2, 2), pid, fill=0, font=FONT)
    tiles.append(tile)
    sealed_P[pid] = {"kind": kind, "t": t, "canon": flat[t] + flat[t + 1], "gline": pos_map[t][0]}
PER = 16; COLS = 4
for m in range(0, len(tiles), PER):
    grp = tiles[m:m + PER]
    cw = max(t.width for t in grp) + 30
    rows_n = (len(grp) + COLS - 1) // COLS
    out = Image.new("L", (cw * COLS, rows_n * (H + 50)), 255)
    for i, t in enumerate(grp):
        out.paste(t, ((i % COLS) * cw, (i // COLS) * (H + 50)))
    out.save(os.path.join(CROPS, f"P_{m // PER:02d}.png"))

json.dump(sealed_L, open(os.path.join(HERE, "sealed_lines.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(sealed_P, open(os.path.join(HERE, "sealed_pairs.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(items_L, open(os.path.join(HERE, "items_L.json"), "w"), indent=1)
json.dump(sorted(sealed_P), open(os.path.join(HERE, "items_P.json"), "w"), indent=1)
print("target pairs", len(target_pairs), "target lines", len(target_lines), "control lines", len(ctrl_lines))
print("target family pairs", len(tgt_fam), "in deck", len(tgt_fam_ok), "line-mode only", len(tgt_fam_not))
print("deck", len(deck), "montages", (len(tiles) + PER - 1) // PER, "| L montages", len(line_items))
print("nseg vs canon len mismatches (line ids only):",
      [i["id"] for i, (kd, g) in zip(items_L, line_items) if i["nseg"] != len(gl[g])])
