"""R47/T2 POST-HOC (Addendum T2-A, written after unsealing; descriptive, not pre-registered).
Template calls (same leave-line-out instrument as unseal.py) on every box of the two strips where T2 read M for a
canon D: T2-s25 (line 455, holds target 9877) and T2-s27 (line 12, non-target gpos 280). Both strips are 1:1 tokens:boxes.
Output: posthoc_md.json"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP)
sys.path.insert(0, os.path.join(LP, "src")); sys.path.insert(0, os.path.join(LP, "analysis", "stones"))
import pipeline as P
from build_dataset import norm_crop
from lp import gematria as gp
T = gp.RUNE_TO_TRANS
# ------------------------------------------------------------ template instrument (R46/S2 template_call.py)
T = gp.RUNE_TO_TRANS
gl, po = P.global_lines()
start = np.cumsum([0] + [len(L) for L in gl])[:-1]
flat = [c for L in gl for c in L]
line_of = np.repeat(np.arange(len(gl)), [len(L) for L in gl])
cm = json.load(open("analysis/round45/S1-transcription/corrected_map.json"))
vec, segs = {}, {}
for n in range(56):
    lines, b, gray = P.segment_image(f"data/relikd/p{n}.jpg")
    g = np.asarray(gray)
    clean = [L for L in lines if len(L) >= 10]
    segs[n] = (g, clean)
    for r in cm[str(n)]:
        G = r["true_gline"]
        if G is None or r["count"] != r["true_len"]:
            continue
        for j, bx in enumerate(clean[r["clean_i"]]):
            v = norm_crop(g, bx)
            if v is not None:
                vec[int(start[G] + j)] = v.ravel().astype(np.float64)
runes = sorted(set(flat), key=lambda r: gp.RUNE_TO_IDX[r])
tot = {r: np.zeros_like(next(iter(vec.values()))) for r in runes}
cnt = {r: 0 for r in runes}
per_line = {}
for p, v in vec.items():
    r = flat[p]
    tot[r] += v
    cnt[r] += 1
    s = per_line.setdefault(int(line_of[p]), {}).setdefault(r, [np.zeros_like(v), 0])
    s[0] += v
    s[1] += 1


def corr(a, b):
    a = a - a.mean()
    b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))


def tcall(v, line):
    ex = per_line.get(line, {})
    sc = {}
    for r in runes:
        s, c = tot[r].copy(), cnt[r]
        if r in ex:
            s -= ex[r][0]
            c -= ex[r][1]
        if c > 0:
            sc[r] = corr(v, s / c)
    best = sorted(sc, key=sc.get, reverse=True)
    return T[best[0]], {T[r]: round(sc[r], 3) for r in best[:3]}


print(f"templates built ({len(vec)} exact-line glyph vectors)")


S = json.load(open(os.path.join(HERE, "sealed.json"), encoding="utf-8"))["items"]
R = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
tok = {s["id"]: s["tokens"] for s in R["strips_T"]}
out = {}
for cid in ("T2-s25", "T2-s27"):
    rec = S[cid]; g, clean = segs[rec["image"]]
    rows = []
    for k in range(rec["box_hi"] - rec["box_lo"] + 1):
        v = norm_crop(g, clean[rec["clean_i"]][rec["box_lo"] + k])
        c, top = tcall(v.ravel().astype(np.float64), rec["gline"]) if v is not None else (None, None)
        rows.append({"box": rec["box_lo"] + k, "t2": tok[cid][k], "template": c, "top3": top})
    out[cid] = {"gline": rec["gline"], "canon_line": rec["canon_line"], "boxes": rows}
json.dump(out, open(os.path.join(HERE, "posthoc_md.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for cid, o in out.items():
    print(cid, o["gline"], [(r["t2"], r["template"], r["top3"]) for r in o["boxes"]])
