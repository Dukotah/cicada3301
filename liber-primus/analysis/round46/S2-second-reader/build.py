"""R46/S2 — build the blind deck (PREREG.md §3), seal labels, render batch montages.

Run from liber-primus/:  PYTHONUTF8=1 python analysis/round46/S2-second-reader/build.py
Outputs (this dir): sealed.json (labels — do NOT open before all reads_batchNN.json exist),
                    manifest.json (crop id -> batch, montage; no labels), build_log.txt,
                    crops/ (gitignored: per-batch montages + reference chart from solved 73.jpg)
Prints no label of any item.
"""
import hashlib
import json
import os
import random
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP)
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis", "stones"))
from lp import gematria as gp  # noqa: E402
import pipeline as P  # noqa: E402

CROPS = os.path.join(HERE, "crops")
os.makedirs(CROPS, exist_ok=True)
CTRL = os.path.join(os.path.dirname(LP), "corpus", "A-primary-artifacts", "cijhho123", "2014",
                    "Liber Primus", "liber primus images full", "73.jpg")
PIN = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
H = 200
UNION = [set("ᚩᚪᚫ"), set("ᛗᛞ"), set("ᚦᚹᚱ"), set("ᚾᛁ"), set("ᛒᛖ")]
U = set().union(*UNION)
CORE = [set("ᚩᚪᚫ"), set("ᛗᛞ"), set("ᚦᚹ")]
log = []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} PREREG.md sha256 {sha(os.path.join(HERE, 'PREREG.md'))}")

# ------------------------------------------------------------ canon stream
gl, po = P.global_lines()
pos_map = [(li, j) for li, L in enumerate(gl) for j in range(len(L))]
x = [gp.RUNE_TO_IDX[c] for L in gl for c in L]
flat = [c for L in gl for c in L]
assert hashlib.sha256(",".join(map(str, x)).encode()).hexdigest() == PIN
N = len(x)
start = np.cumsum([0] + [len(L) for L in gl])[:-1]

pins = json.load(open("analysis/round19/C3/l3/hashes.json"))
for n in range(56):
    assert sha(f"data/relikd/p{n}.jpg") == pins["target_renders"][f"p{n}.jpg"]["sha256"], n
assert sha(CTRL) == pins["control_renders"]["73.jpg"]["sha256"]

# ------------------------------------------------------------ S1 read-set replay (seed 45013, S1 build_set.py order)
rng = random.Random(45013)
F1 = []
for b in range(11):
    lo, hi = b * 5, b * 5 + 4
    cand = [i for i in range(N) if lo <= po[pos_map[i][0]] <= hi]
    F1 += rng.sample(cand, 6)
FAM_S1 = [set("ᚩᚪᚫ"), set("ᚱᚹ"), set("ᛗᛞ"), set("ᚾᛁ"), set("ᛒᛖ")]
dbl = [i for i in range(N - 1) if x[i] == x[i + 1]]
near = [i for i in range(N - 1) if flat[i] != flat[i + 1] and any(flat[i] in f and flat[i + 1] in f for f in FAM_S1)]
F3 = sorted(rng.sample(near, 40))
excl = set(dbl) | set(near)
F4 = sorted(rng.sample([i for i in range(N - 1) if i not in excl], 40))
S1set = set(F1) | {i for p in dbl + F3 + F4 for i in (p, p + 1)}

# ------------------------------------------------------------ exact-registered boxes (S1 corrected_map)
cm = json.load(open("analysis/round45/S1-transcription/corrected_map.json"))
grays, box_of = {}, {}
for n in range(56):
    lines, b, gray = P.segment_image(f"data/relikd/p{n}.jpg")
    grays[n] = np.asarray(gray)
    clean = [L for L in lines if len(L) >= 10]
    for r in cm[str(n)]:
        G = r["true_gline"]
        if G is None or r["count"] != r["true_len"]:
            continue
        for j, bx in enumerate(clean[r["clean_i"]]):
            box_of[int(start[G] + j)] = (n, bx)
exact = sorted(box_of)
log.append(f"exact-registered positions {len(exact)} / {N}")

A = sorted(i for i in S1set if flat[i] in U and i in box_of)
log.append(f"S1 replay glyphs {len(S1set)}; family {sum(flat[i] in U for i in S1set)}; frame A (exact) {len(A)}")
R = sorted(random.Random(46021).sample([i for i in exact if i not in S1set], 100))

# swap control
rw = random.Random(46024)
used = set(A) | set(R) | S1set
core_pos = [i for i in exact if i not in used and any(flat[i] in f for f in CORE)]
W = []
for i in rw.sample(core_pos, 8):
    fam = next(f for f in CORE if flat[i] in f)
    donors = [d for d in core_pos if flat[d] in fam and flat[d] != flat[i] and d != i]
    W.append((i, rw.choice(donors)))

# controls on solved 73.jpg (drop cap: box[i] <-> canon[i+1])
RC = [c for c in open("data/krisyotam_runes.txt", encoding="utf-8").read().split("%")[55] if c in P.RUNES]
lines, b, gray = P.segment_image(CTRL)
grays["73"] = np.asarray(gray)
BC = [bx for L in lines if len(L) >= 3 for bx in L]
assert len(BC) == len(RC) - 1
lab = {i: RC[i + 1] for i in range(len(BC))}
rc = random.Random(46022)
fam_c = [i for i in lab if lab[i] in U]
oth_c = [i for i in lab if lab[i] not in U]
C = rc.sample(fam_c, 16) + rc.sample(oth_c, 8)


# ------------------------------------------------------------ rendering (S1 crop_box glue, H=200)
def crop_box(key, box, pad=10):
    a = grays[key].astype(np.float32)
    y0, y1 = max(0, box["y0"] - pad), box["y1"] + pad
    x0, x1 = max(0, box["x0"] - pad - 14), box["x1"] + pad + 14
    sub = a[y0:y1, x0:x1].copy()
    m = np.ones_like(sub, dtype=bool)
    m[box["y0"] - y0:box["y1"] - y0, box["x0"] - x0:box["x1"] - x0] = False
    sub[m] = 255 - (255 - sub[m]) * 0.18
    im = Image.fromarray(sub.astype(np.uint8))
    return im.resize((max(1, int(im.width * H / im.height)), H), Image.LANCZOS)


items = []
for i in A:
    items.append(("A", crop_box(*box_of[i]), {"frame": "A", "gpos": i, "canon": flat[i], "gline": pos_map[i][0],
                                              "page": po[pos_map[i][0]]}))
for i in R:
    items.append(("R", crop_box(*box_of[i]), {"frame": "R", "gpos": i, "canon": flat[i], "gline": pos_map[i][0],
                                              "page": po[pos_map[i][0]]}))
for i in C:
    items.append(("C", crop_box("73", BC[i]), {"frame": "C", "img": "73.jpg", "box_index": i, "canon": lab[i]}))
for i, d in W:
    items.append(("W", crop_box(*box_of[d]), {"frame": "W", "gpos": i, "canon": flat[i], "claimed": flat[i],
                                              "donor_gpos": d, "donor_canon": flat[d]}))

# shuffle, deal controls round-robin into 13 batches
r3 = random.Random(46023)
main = [it for it in items if it[0] in "AR"]
ctl = [it for it in items if it[0] in "CW"]
r3.shuffle(main)
r3.shuffle(ctl)
NB = 13
batches = [[] for _ in range(NB)]
for k, it in enumerate(ctl):
    batches[k % NB].append(it)
k = 0
for it in main:
    while len(batches[k % NB]) >= 24:
        k += 1
    batches[k % NB].append(it)
    k += 1
for bt in batches:
    r3.shuffle(bt)
assert all(len(bt) <= 24 for bt in batches) and sum(map(len, batches)) == len(items)

try:
    FONT = ImageFont.truetype("arial.ttf", 22)
except OSError:
    FONT = ImageFont.load_default()

sealed, manifest = {}, []
for bi, bt in enumerate(batches, 1):
    for half in range(2):
        ents = bt[half * 12:(half + 1) * 12]
        if not ents:
            continue
        cw, chh = 200, H + 36
        out = Image.new("L", (4 * cw, ((len(ents) + 3) // 4) * chh), 255)
        d = ImageDraw.Draw(out)
        name = f"b{bi:02d}_{'ab'[half]}.png"
        for k2, (_, im, rec) in enumerate(ents):
            cid = f"S{bi:02d}{half * 12 + k2:02d}"
            r_, c_ = divmod(k2, 4)
            if im.width > cw - 10:
                im = im.resize((cw - 10, int(H * (cw - 10) / im.width)))
            out.paste(im, (c_ * cw + 5, r_ * chh + 2))
            d.text((c_ * cw + 8, r_ * chh + H + 6), cid, fill=0, font=FONT)
            d.rectangle([c_ * cw, r_ * chh, c_ * cw + cw - 1, r_ * chh + chh - 1], outline=170)
            sealed[cid] = rec
            manifest.append({"id": cid, "batch": bi, "montage": name})
        out.save(os.path.join(CROPS, name))

# reference chart: exemplars from solved 73.jpg, disjoint from control boxes (labels = decrypted page)
cset = set(C)
ex = {}
for i in range(len(BC)):
    if i not in cset and len(ex.setdefault(lab[i], [])) < 2:
        ex[lab[i]].append(i)
order = sorted(ex, key=lambda r_: gp.RUNE_TO_IDX[r_])
cw, hh = 150, 140
chart = Image.new("L", (10 * cw, ((len(order) + 9) // 10) * (hh + 30)), 255)
d = ImageDraw.Draw(chart)
Hs = 130
for k2, r_ in enumerate(order):
    rr, cc = divmod(k2, 10)
    xo = cc * cw + 4
    for i in ex[r_]:
        bx = BC[i]
        sub = grays["73"][max(0, bx["y0"] - 4):bx["y1"] + 4, max(0, bx["x0"] - 4):bx["x1"] + 4]
        im = Image.fromarray(sub)
        im = im.resize((max(1, int(im.width * Hs / im.height)), Hs))
        if xo + im.width <= cc * cw + cw:
            chart.paste(im, (xo, rr * (hh + 30)))
            xo += im.width + 4
    d.text((cc * cw + 6, rr * (hh + 30) + hh), gp.RUNE_TO_TRANS[r_], fill=0, font=FONT)
chart.save(os.path.join(CROPS, "reference_73.png"))
missing = sorted(gp.RUNE_TO_TRANS[r_] for r_ in gp.RUNE_TO_TRANS if r_ not in ex)
log.append(f"reference chart runes {len(order)}; absent from 73.jpg: {missing}")
log.append(f"frames A={len(A)} R={len(R)} C={len(C)} W={len(W)} total={len(items)} batches={[len(b_) for b_ in batches]}")

json.dump({"seeds": {"replay": 45013, "R": 46021, "C": 46022, "deal": 46023, "W": 46024}, "items": sealed},
          open(os.path.join(HERE, "sealed.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(manifest, open(os.path.join(HERE, "manifest.json"), "w"), indent=1)
open(os.path.join(HERE, "build_log.txt"), "w", encoding="utf-8").write("\n".join(log) + "\n")
open(os.path.join(HERE, ".gitignore"), "w").write("crops/\n__pycache__/\n")
print("\n".join(log))
