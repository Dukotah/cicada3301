"""R46/S2 — template instrument for adjudication (PREREG §5). Run AFTER all reads are frozen.

Nearest class mean (Pearson correlation of build_dataset.norm_crop bitmaps), templates from every glyph on
S1 corrected_map exact-registered lines EXCLUDING the item's own line (leave-line-out). For a W (swap) item the
vector is the donor's crop (what was shown) and the excluded line is the donor's. Also validates the template
on every exact-line glyph of the look-alike union (leave-line-out). Output: template_calls.json (~2 min).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP)
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis", "stones"))
import pipeline as P  # noqa: E402
from build_dataset import norm_crop  # noqa: E402
from lp import gematria as gp  # noqa: E402

for nn in range(1, 14):
    assert os.path.exists(os.path.join(HERE, f"reads_batch{nn:02d}.json")), nn
T = gp.RUNE_TO_TRANS
gl, po = P.global_lines()
start = np.cumsum([0] + [len(L) for L in gl])[:-1]
flat = [c for L in gl for c in L]
line_of = np.repeat(np.arange(len(gl)), [len(L) for L in gl])
cm = json.load(open("analysis/round45/S1-transcription/corrected_map.json"))
vec = {}
for n in range(56):
    lines, b, gray = P.segment_image(f"data/relikd/p{n}.jpg")
    g = np.asarray(gray)
    clean = [L for L in lines if len(L) >= 10]
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
    d = per_line.setdefault(int(line_of[p]), {})
    s = d.setdefault(r, [np.zeros_like(v), 0])
    s[0] += v
    s[1] += 1


def corr(a, b):
    a = a - a.mean()
    b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))


def call(v, line):
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


S = json.load(open(os.path.join(HERE, "sealed.json"), encoding="utf-8"))["items"]
out = {"n_vec": len(vec), "items": {}, "validation": {}}
for cid, rec in S.items():
    if rec["frame"] in ("A", "R"):
        p = rec["gpos"]
    elif rec["frame"] == "W":
        p = rec["donor_gpos"]
    else:
        continue
    if p not in vec:
        out["items"][cid] = None
        continue
    c, top = call(vec[p], int(line_of[p]))
    out["items"][cid] = {"call": c, "top3": top}

U = set("ᚩᚪᚫᛗᛞᚦᚹᚱᚾᛁᛒᛖ")
fam_name = {**{r: "OA" for r in "ᚩᚪᚫ"}, **{r: "MD" for r in "ᛗᛞ"}, **{r: "THWR" for r in "ᚦᚹᚱ"},
            **{r: "NI" for r in "ᚾᛁ"}, **{r: "BE" for r in "ᛒᛖ"}}
val = {}
for p, v in vec.items():
    if flat[p] not in U:
        continue
    c, _ = call(v, int(line_of[p]))
    f = fam_name[flat[p]]
    val.setdefault(f, [0, 0, []])
    val[f][0] += 1
    if c == T[flat[p]]:
        val[f][1] += 1
    else:
        val[f][2].append([p, T[flat[p]], c])
for f, (n, k, errs) in val.items():
    out["validation"][f] = {"n": n, "correct": k, "errors_first20": errs[:20], "n_errors": len(errs)}
json.dump(out, open(os.path.join(HERE, "template_calls.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({f: (d["correct"], d["n"]) for f, d in out["validation"].items()})
