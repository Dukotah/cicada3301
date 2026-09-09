#!/usr/bin/env python3
"""Round 28 L2 — INDEPENDENT BLIND read of the pp49-51 conflict cells.

Purpose (PREREG Amendment 1): A-04 (round19/C1) resolved all 11 witness-conflict cells
with a pixel instrument, but its not_covered(e)/reopens_if names "an independent BLIND
transcription of the 11 conflict cells" as the one read-side thing still missing. This
script IS that read, built independently:

  - own segmentation (connected components + row clustering + gap-split), no reuse of
    round18/L5 grid.py / pixelmatch.py code or their grid.json;
  - normalized cross-correlation (NCC) matching, not IoU;
  - templates labeled ONLY from witness-unanimous cells (relikd tok == scream tok ==
    scream decimal), never from canon at conflict cells;
  - gate: single-template regime must score 100/100 exact-token on a blind seeded sample
    of 100 witness-unanimous cells BEFORE any conflict cell is read;
  - 3 independent passes (crop padding 0/1/2 px) must agree for any verdict.

Also attempts the 4 cells A-04 never verified: 186, 210, 211 (unsegmented in L5) and
209 (mis-segmented in L5).

Outputs reader_out.json. Exit nonzero if the gate fails (lane falls back to
enumeration-only per PREREG Q5).
"""
import json, os, re, sys, collections, random
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))  # cicada3301/
LP = os.path.join(ROOT, "liber-primus")

CONFLICT = [25, 45, 50, 165, 172, 175, 182, 199, 215, 237, 246]
PREREG6 = [25, 175, 182, 199, 215, 237]
UNVERIFIED = [186, 209, 210, 211]
SEED = 3301
GATE_N = 100

# ---------------------------------------------------------------- witnesses (lifted
# from pp49_51/canonicalize.py extraction logic; re-implemented here, same regexes)
def digit_val(c):
    if c.isdigit(): return ord(c) - 48
    if 'A' <= c <= 'Z': return ord(c) - 65 + 10
    if 'a' <= c <= 'x': return ord(c) - 97 + 36
    raise ValueError(c)

def tok_to_byte(t): return digit_val(t[0]) * 60 + digit_val(t[1])

TOKROW = re.compile(r'^\s*([0-9A-Za-z]{2})([ \t]+[0-9A-Za-z]{2}){7}\s*$')
DEC = re.compile(r'^\s*(\d{1,3})(\s+\d{1,3}){7}\s*$')

def extract_tables(path):
    tables, cur = [], []
    for line in open(path, encoding="utf-8"):
        if TOKROW.match(line): cur.extend(line.split())
        else:
            if cur: tables.append(cur); cur = []
    if cur: tables.append(cur)
    return [t for t in tables if len(t) in (80, 104, 72)]

def extract_decimals(path):
    blocks, cur = [], []
    for line in open(path, encoding="utf-8"):
        if DEC.match(line): cur.extend(int(x) for x in line.split())
        else:
            if cur: blocks.append(cur); cur = []
    if cur: blocks.append(cur)
    return [b for b in blocks if len(b) in (80, 104, 72)]

def stitch(tabs):
    order = {80: 0, 104: 1, 72: 2}
    picked = {}
    for t in tabs: picked.setdefault(order[len(t)], t)
    return [tok for k in (0, 1, 2) for tok in picked[k]]

A = stitch(extract_tables(os.path.join(LP, "data/relikd/p40-53.txt")))
B = stitch(extract_tables(os.path.join(LP, "data/scream314_lp.md")))
decs = extract_decimals(os.path.join(LP, "data/scream314_lp.md"))
decpick = {}
for b in decs: decpick.setdefault(len(b), b)
C = [v for k in (80, 104, 72) for v in decpick[k]]
assert len(A) == len(B) == len(C) == 256

UNANIMOUS = [i for i in range(256)
             if tok_to_byte(A[i]) == tok_to_byte(B[i]) == C[i]]
assert len(UNANIMOUS) == 245, len(UNANIMOUS)
assert set(range(256)) - set(UNANIMOUS) == set(CONFLICT)

# ---------------------------------------------------------------- segmentation
PAGES = {  # page -> (image, expected rows, global index offset)
    "p49": (os.path.join(LP, "data/relikd/p49.jpg"), 10, 0),
    "p50": (os.path.join(LP, "data/relikd/p50.jpg"), 13, 80),
    "p51": (os.path.join(LP, "data/relikd/p51.jpg"), 9, 184),
}

def components(mask):
    """4-connected components on a boolean mask. Returns list of (y0,y1,x0,x1,npix)."""
    from collections import deque
    h, w = mask.shape
    lab = np.zeros((h, w), dtype=np.int32)
    boxes = []
    nxt = 0
    for sy in range(h):
        xs = np.nonzero(mask[sy] & (lab[sy] == 0))[0]
        for sx in xs:
            if lab[sy, sx]: continue
            nxt += 1
            q = deque([(sy, sx)]); lab[sy, sx] = nxt
            y0 = y1 = sy; x0 = x1 = sx; n = 0
            while q:
                y, x = q.popleft(); n += 1
                if y < y0: y0 = y
                if y > y1: y1 = y
                if x < x0: x0 = x
                if x > x1: x1 = x
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx_ = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx_ < w and mask[ny, nx_] and not lab[ny, nx_]:
                        lab[ny, nx_] = nxt; q.append((ny, nx_))
            boxes.append([y0, y1, x0, x1, n])
    return boxes

def segment_page(path, exp_rows):
    im = np.asarray(Image.open(path).convert("L"))
    mask = im < 128
    boxes = [b for b in components(mask) if 20 <= b[4] <= 6000  # drop trees/specks
             and b[2] >= 500 and b[3] <= 1900]  # central table band (trees+dots flank it)
    # cluster into lines by y-center
    boxes.sort(key=lambda b: (b[0] + b[1]) / 2)
    lines, cur, last = [], [], None
    for b in boxes:
        yc = (b[0] + b[1]) / 2
        if last is None or yc - last <= 40:
            cur.append(b)
        else:
            lines.append(cur); cur = [b]
        last = yc
    if cur: lines.append(cur)

    rows = []
    for ln in lines:
        ln.sort(key=lambda b: b[2])
        # merge boxes with strong horizontal overlap (i/j dots onto stems)
        merged = []
        for b in ln:
            if merged:
                m = merged[-1]
                ov = min(m[3], b[3]) - max(m[2], b[2])
                if ov > 0 and ov >= 0.5 * min(m[3] - m[2], b[3] - b[2]):
                    m[0] = min(m[0], b[0]); m[1] = max(m[1], b[1])
                    m[2] = min(m[2], b[2]); m[3] = max(m[3], b[3]); m[4] += b[4]
                    continue
            merged.append(list(b))
        if len(merged) != 16:
            continue  # not a token row (runes, ornaments, partial)
        # 16 glyphs pair deterministically into 8 two-glyph tokens: (0,1)(2,3)...(14,15).
        # ('11' has a wider intra gap than some inter gaps, so gap inference is unsafe.)
        toks = [[merged[2 * k], merged[2 * k + 1]] for k in range(8)]
        rows.append((np.mean([b[0] for b in merged]), toks))
    rows.sort(key=lambda r: r[0])
    if len(rows) != exp_rows:
        raise SystemExit(f"SEGMENTATION HARD STOP: {path} rows {len(rows)} != {exp_rows}")
    return im, [t for _, r in rows for t in r]

def crop(im, box, pad):
    y0, y1, x0, x1, _ = box
    h, w = im.shape
    return (np.asarray(im[max(0, y0 - pad):min(h, y1 + 1 + pad),
                          max(0, x0 - pad):min(w, x1 + 1 + pad)]) < 128).astype(np.float64)

# ---------------------------------------------------------------- NCC matcher
def ncc_best(a, b, max_shift=3):
    """Best NCC of binary images a (glyph) vs b (template) over integer shifts,
    after embedding both in a common canvas anchored top-left."""
    H = max(a.shape[0], b.shape[0]) + 2 * max_shift
    W = max(a.shape[1], b.shape[1]) + 2 * max_shift
    ca = np.zeros((H, W)); ca[max_shift:max_shift + a.shape[0], max_shift:max_shift + a.shape[1]] = a
    va = ca - ca.mean(); na = np.sqrt((va * va).sum())
    best = -1.0
    for dy in range(-max_shift, max_shift + 1):
        for dx in range(-max_shift, max_shift + 1):
            cb = np.zeros((H, W))
            y0, x0 = max_shift + dy, max_shift + dx
            cb[y0:y0 + b.shape[0], x0:x0 + b.shape[1]] = b
            vb = cb - cb.mean(); nb = np.sqrt((vb * vb).sum())
            if na == 0 or nb == 0: continue
            v = float((va * vb).sum() / (na * nb))
            if v > best: best = v
    return best

# Height/vertical position are discriminative for I/l and W/w and MUST NOT be thrown
# away by tight-bbox NCC alone; encode them as auxiliary features gated into the score.
def features(im, box):
    y0, y1, x0, x1, _ = box
    return (y1 - y0 + 1, x1 - x0 + 1, y0, y1)

class Classifier:
    def __init__(self, templates, pad):
        # templates: cls -> (cropimg, (h,w,y0,y1), rowtop) single exemplar
        self.t = templates
        self.pad = pad

    def classify(self, im, box, rowtop):
        h, w, y0, y1 = features(im, box)
        g = crop(im, box, self.pad)
        scored = []
        for cls, (timg, (th, tw, ty0, ty1), trowtop) in self.t.items():
            ncc = ncc_best(g, timg)
            # penalize mismatched geometry: height diff and cap-line offset
            dh = abs(h - th) / max(h, th)
            dtop = abs((y0 - rowtop) - (ty0 - trowtop)) / 100.0
            scored.append((ncc - dh - dtop, ncc, cls))
        scored.sort(reverse=True)
        top = scored[0]; second = scored[1]
        return top[2], top[0] - second[0], top, second

def main():
    out = {"seed": SEED, "gate_n": GATE_N, "passes": [0, 1, 2]}
    ims, cells = {}, {}
    for pg, (path, rows, off) in PAGES.items():
        im, toks = segment_page(path, rows)
        ims[pg] = im
        for i, tok in enumerate(toks):
            cells[off + i] = (pg, tok)
    assert len(cells) == 256
    print("segmentation: 256 cells, all pages OK (incl. 186/209/210/211 -> "
          f"{[len(cells[i][1]) for i in UNVERIFIED]} glyphs each)")

    # row top (cap line proxy): min y0 of digit glyphs in the same row of 8 tokens
    rowtop = {}
    for gi, (pg, tok) in cells.items():
        base = (gi // 8) * 8
        tops = [cells[j][1][0][0] for j in range(base, base + 8)]  # leading digits
        rowtop[gi] = float(np.median(tops))

    # templates: single exemplar per class, from the LOWEST-index unanimous cell
    lead_t, trail_t = {}, {}
    for gi in UNANIMOUS:
        pg, tok = cells[gi]
        lab = A[gi]
        for k, table in ((0, lead_t), (1, trail_t)):
            cls = lab[k]
            if cls not in table:
                table[cls] = (gi, tok[k])
    print(f"template classes: lead {len(lead_t)} digits, trail {len(trail_t)} symbols")

    def build(table, pad):
        return {cls: (crop(ims[cells[gi][0]], box, pad),
                      features(ims[cells[gi][0]], box), rowtop[gi])
                for cls, (gi, box) in table.items()}

    def read_cell(gi, pad):
        pg, tok = cells[gi]
        cl = Classifier(build(lead_t, pad), pad)
        ct = Classifier(build(trail_t, pad), pad)
        r1 = cl.classify(ims[pg], tok[0], rowtop[gi])
        r2 = ct.classify(ims[pg], tok[1], rowtop[gi])
        return r1, r2

    # ---------------- GATE: blind 100-cell control, single-template regime ----------
    # Pool excludes exemplar cells (their glyph IS the template): same regime as A-04's
    # Control 3. Singleton classes (I,R,h,i,l per A-04) are inherently un-testable this
    # way; their discrimination rests on render determinism + the geometry features.
    exemplar_cells = {gi for gi, _ in lead_t.values()} | {gi for gi, _ in trail_t.values()}
    pool = [gi for gi in UNANIMOUS if gi not in exemplar_cells]
    rng = random.Random(SEED)
    sample = rng.sample(pool, GATE_N)
    out["gate_pool"] = len(pool)
    correct, margins, misses = 0, [], []
    for gi in sample:
        (c1, m1, _, _), (c2, m2, _, _) = read_cell(gi, pad=1)
        tok = c1 + c2
        if tok == A[gi]:
            correct += 1; margins.append(min(m1, m2))
        else:
            misses.append({"idx": gi, "read": tok, "truth": A[gi]})
    out["gate"] = {"correct": correct, "n": GATE_N, "misses": misses,
                   "min_margin_correct": min(margins) if margins else None}
    print(f"GATE: {correct}/{GATE_N} blind exact-token"
          f"  min-margin(correct)={min(margins):.4f}" if margins else "GATE: 0")
    if correct < GATE_N:
        print("GATE FAILED (<100/100) — reader untrusted, enumeration-only fallback.")
        json.dump(out, open(os.path.join(HERE, "reader_out.json"), "w"), indent=1)
        sys.exit(2)
    min_margin = min(margins)

    # ---------------- read targets blind (3 passes: pad 0/1/2) ----------------------
    verdicts = {}
    for gi in CONFLICT + UNVERIFIED:
        passes = []
        for pad in (0, 1, 2):
            (c1, m1, t1, s1), (c2, m2, t2, s2) = read_cell(gi, pad)
            passes.append({"pad": pad, "tok": c1 + c2, "margin": round(min(m1, m2), 4),
                           "lead_top": [t1[2], round(t1[1], 4)], "lead_2nd": [s1[2], round(s1[1], 4)],
                           "trail_top": [t2[2], round(t2[1], 4)], "trail_2nd": [s2[2], round(s2[1], 4)]})
        toks = {p["tok"] for p in passes}
        unanim = len(toks) == 1
        tok = passes[0]["tok"]
        strong = unanim and all(p["margin"] >= min_margin for p in passes)
        verdicts[gi] = {"passes": passes, "unanimous_3pass": unanim,
                        "margin_clears_control_min": strong,
                        "verdict_tok": tok if unanim else None,
                        "verdict_byte": tok_to_byte(tok) if unanim else None}
    out["verdicts"] = verdicts
    json.dump(out, open(os.path.join(HERE, "reader_out.json"), "w"), indent=1)

    # ---------------- unblind & compare (report only) -------------------------------
    canon = list(open(os.path.join(LP, "analysis/pp49_51/canon_256.bin"), "rb").read())
    resolved = list(open(os.path.join(LP, "analysis/round19/C1/payload_resolved.bin"), "rb").read())
    print("\nidx | this blind read | canon | A-04/resolved | agree(A-04)")
    for gi in CONFLICT + UNVERIFIED:
        v = verdicts[gi]
        b = v["verdict_byte"]
        tag = "CONFLICT" if gi in CONFLICT else "UNVERIFIED"
        print(f"{gi:4d} [{tag}] read={v['verdict_tok']}({b}) canon={canon[gi]} "
              f"resolved={resolved[gi]} agree={'YES' if b == resolved[gi] else 'NO' if b is not None else 'NO-VERDICT'}")

if __name__ == "__main__":
    main()
