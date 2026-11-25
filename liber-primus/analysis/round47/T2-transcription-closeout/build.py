"""R47/T2 — build the blind strip deck (PREREG.md §2-3), seal labels, render strips.
Run from liber-primus/:  PYTHONUTF8=1 python analysis/round47/T2-transcription-closeout/build.py
Outputs: sealed.json (do NOT open before all reads_batchNN.json are frozen), manifest.json (ids only),
build_log.txt, crops/T2-sNN.png. Prints no label of any item."""
import hashlib
import json
import os
import random
import sys
import time

import numpy as np
from PIL import Image

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
T = gp.RUNE_TO_TRANS


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


log = [f"{time.strftime('%Y-%m-%d %H:%M:%S')} PREREG.md sha256 {sha(os.path.join(HERE, 'PREREG.md'))}"]

gl, po = P.global_lines()
pos_map = [(li, j) for li, L in enumerate(gl) for j in range(len(L))]
flat = [c for L in gl for c in L]
x = [gp.RUNE_TO_IDX[c] for c in flat]
N = len(flat)
assert hashlib.sha256(",".join(map(str, x)).encode()).hexdigest() == PIN
start = np.cumsum([0] + [len(L) for L in gl])[:-1]
pins = json.load(open("analysis/round19/C3/l3/hashes.json"))
for n in range(56):
    assert sha(f"data/relikd/p{n}.jpg") == pins["target_renders"][f"p{n}.jpg"]["sha256"], n
assert sha(CTRL) == pins["control_renders"]["73.jpg"]["sha256"]

# S1 read-set replay (seed 45013), identical to R46/S2 build.py
rng = random.Random(45013)
F1 = []
for b in range(11):
    lo, hi = b * 5, b * 5 + 4
    F1 += rng.sample([i for i in range(N) if lo <= po[pos_map[i][0]] <= hi], 6)
FAM_S1 = [set("ᚩᚪᚫ"), set("ᚱᚹ"), set("ᛗᛞ"), set("ᚾᛁ"), set("ᛒᛖ")]
dbl = [i for i in range(N - 1) if x[i] == x[i + 1]]
near = [i for i in range(N - 1) if flat[i] != flat[i + 1] and any(flat[i] in f and flat[i + 1] in f for f in FAM_S1)]
F3 = sorted(rng.sample(near, 40))
excl = set(dbl) | set(near)
F4 = sorted(rng.sample([i for i in range(N - 1) if i not in excl], 40))
S1set = set(F1) | {i for p in dbl + F3 + F4 for i in (p, p + 1)}
U = set("ᚩᚪᚫᛗᛞᚦᚹᚱᚾᛁᛒᛖ")
CORE = [set("ᚩᚪᚫ"), set("ᛗᛞ"), set("ᚦᚹ")]

cm = json.load(open("analysis/round45/S1-transcription/corrected_map.json"))
al = json.load(open("analysis/stones/alignment.json"))  # repaired v2 (R46-A1)
alw = {G: (int(n), i) for n, L in al.items() for i, G in enumerate(L)}
exact_lines, cmw = {}, {}
for n in range(56):
    for r in cm[str(n)]:
        G = r["true_gline"]
        if G is None:
            continue
        cmw[G] = (n, r["clean_i"])
        if r["count"] == r["true_len"]:
            exact_lines[G] = (n, r["clean_i"])
exact = {i for G in exact_lines for i in range(int(start[G]), int(start[G]) + len(gl[G]))}
targets = sorted(i for i in S1set if flat[i] in U and i not in exact)
assert len(targets) == 27 and {276, 5054, 6054, 9877} <= set(targets)
tlines = sorted({pos_map[i][0] for i in targets})
agree = sum(cmw.get(G) == alw.get(G) for G in tlines)
log.append(f"targets {len(targets)} on {len(tlines)} lines; v2 alignment.json vs corrected_map agree on {agree}/{len(tlines)} "
           f"(disagreeing/null in corrected_map: {[G for G in tlines if cmw.get(G) != alw.get(G)]}); registration used = v2")

pages = sorted({alw[G][0] for G in tlines} | {exact_lines[G][0] for G in exact_lines})
grays, clean_of = {}, {}
for n in pages:
    lines, b, gray = P.segment_image(f"data/relikd/p{n}.jpg")
    grays[n] = np.asarray(gray).astype(np.float32)
    clean_of[n] = [L for L in lines if len(L) >= 10]
for G in tlines:
    n, ci = alw[G]
    log.append(f"  line {G}: image {n} clean {ci} boxes {len(clean_of[n][ci])} canon_len {len(gl[G])}")


def render(a, boxes, pad=10):
    y0 = max(0, min(b["y0"] for b in boxes) - pad)
    y1 = max(b["y1"] for b in boxes) + pad
    xa, xb = min(b["x0"] for b in boxes), max(b["x1"] for b in boxes)
    X0 = max(0, xa - pad - 14)
    X1 = xb + pad + 14
    sub = a[y0:y1, X0:X1].copy()
    m = np.ones_like(sub, dtype=bool)
    m[:, max(0, xa - 3 - X0):xb + 3 - X0] = False
    sub[m] = 255 - (255 - sub[m]) * 0.18
    im = Image.fromarray(np.clip(sub, 0, 255).astype(np.uint8))
    return im.resize((max(1, int(im.width * H / im.height)), H), Image.LANCZOS)


strips = []
# ---- T: one strip per target line
for G in tlines:
    n, ci = alw[G]
    boxes = clean_of[n][ci]
    c, L = len(boxes), len(gl[G])
    js = [pos_map[i][1] for i in targets if pos_map[i][0] == G]
    lo = max(0, int(np.floor(min(js) * c / L)) - 3)
    hi = min(c - 1, int(np.ceil(max(js) * c / L)) + 3)
    strips.append(("T", render(grays[n], boxes[lo:hi + 1]), hi - lo + 1,
                   {"frame": "T", "gline": G, "image": n, "clean_i": ci, "box_lo": lo, "box_hi": hi, "n_boxes_line": c,
                    "canon_line": [T[r] for r in gl[G]], "line_start_gpos": int(start[G]),
                    "targets": [{"gpos": i, "j": pos_map[i][1], "canon": T[flat[i]]} for i in targets if pos_map[i][0] == G]}))

# ---- W: swap strips on exact lines
rw = random.Random(47024)
avoid_lines = {pos_map[i][0] for i in S1set} | set(tlines)
ok = [i for i in sorted(exact) if pos_map[i][0] not in avoid_lines]
core_pos = [i for i in ok if any(flat[i] in f for f in CORE)]
usedW = set()
nW = 0
for i in rw.sample(core_pos, 40):
    if nW == 8:
        break
    G, j = pos_map[i]
    if G in usedW:
        continue
    fam = next(f for f in CORE if flat[i] in f)
    donors = [d for d in core_pos if flat[d] in fam and flat[d] != flat[i] and pos_map[d][0] != G]
    d = rw.choice(donors)
    n, ci = exact_lines[G]
    boxes = clean_of[n][ci]
    s0 = rw.randint(max(0, j - 6), min(j, len(boxes) - 7))
    sb = boxes[s0:s0 + 7]
    a = grays[n].copy()
    rb = boxes[j]
    dn, dci = exact_lines[pos_map[d][0]]
    db = clean_of[dn][dci][pos_map[d][1]]
    dimg = Image.fromarray(np.clip(grays[dn][db["y0"]:db["y1"], db["x0"]:db["x1"]], 0, 255).astype(np.uint8))
    dimg = dimg.resize((rb["x1"] - rb["x0"], rb["y1"] - rb["y0"]), Image.LANCZOS)
    a[rb["y0"]:rb["y1"], rb["x0"]:rb["x1"]] = np.asarray(dimg).astype(np.float32)
    seq = [T[flat[int(start[G]) + s0 + k]] for k in range(7)]
    usedW.add(G)
    nW += 1
    strips.append(("W", render(a, sb), 7, {"frame": "W", "gline": G, "box_lo": s0, "canon_seq": seq, "swap_index": j - s0,
                                           "recipient_gpos": i, "claimed": T[flat[i]], "donor_gpos": d,
                                           "donor_canon": T[flat[d]]}))
assert nW == 8

# ---- C: solved 73.jpg strips (drop cap: box[i] <-> canon[i+1])
RC = [c for c in open("data/krisyotam_runes.txt", encoding="utf-8").read().split("%")[55] if c in P.RUNES]
lines, b, gray = P.segment_image(CTRL)
g73 = np.asarray(gray).astype(np.float32)
BC, lineid = [], []
for li, L in enumerate([l_ for l_ in lines if len(l_) >= 3]):
    BC += L
    lineid += [li] * len(L)
assert len(BC) == len(RC) - 1
rc = random.Random(47022)
taken = set()
nC = 0
while nC < 4:
    s0 = rc.randrange(len(BC) - 6)
    r6 = range(s0, s0 + 6)
    if len({lineid[k] for k in r6}) != 1 or taken & set(r6):
        continue
    taken |= set(r6)
    nC += 1
    strips.append(("C", render(g73, BC[s0:s0 + 6]), 6, {"frame": "C", "img": "73.jpg", "box_lo": s0,
                                                         "canon_seq": [T[RC[k + 1]] for k in r6]}))

# ---- shuffle, deal into batches of <= 25 boxes, batch 1 starts with a control
r3 = random.Random(47023)
r3.shuffle(strips)
k = next(i for i, s in enumerate(strips) if s[0] != "T")
strips.insert(0, strips.pop(k))
batches, cur, nb = [], [], 0
for s in strips:
    if cur and nb + s[2] > 25:
        batches.append(cur)
        cur, nb = [], 0
    cur.append(s)
    nb += s[2]
batches.append(cur)
sealed, manifest = {}, []
sid = 0
for bi, bt in enumerate(batches, 1):
    for s in bt:
        sid += 1
        cid = f"T2-s{sid:02d}"
        s[1].save(os.path.join(CROPS, f"{cid}.png"))
        sealed[cid] = s[3]
        manifest.append({"id": cid, "batch": bi, "file": f"crops/{cid}.png", "n_boxes": s[2]})
log.append(f"strips T={sum(s[0] == 'T' for s in strips)} W={sum(s[0] == 'W' for s in strips)} "
           f"C={sum(s[0] == 'C' for s in strips)}; batches {len(batches)} boxes/batch {[sum(s[2] for s in bt) for bt in batches]}")
json.dump({"seeds": {"replay": 45013, "C": 47022, "deal": 47023, "W": 47024}, "items": sealed},
          open(os.path.join(HERE, "sealed.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(manifest, open(os.path.join(HERE, "manifest.json"), "w"), indent=1)
open(os.path.join(HERE, "build_log.txt"), "w", encoding="utf-8").write("\n".join(log) + "\n")
print("\n".join(log))
