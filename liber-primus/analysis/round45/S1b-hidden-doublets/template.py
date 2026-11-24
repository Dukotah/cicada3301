"""R45/S1b — objective second instrument for the unblinded adjudication of look-alike candidates (PREREG §1
"unblinded high-zoom re-inspection"; added at adjudication, see RESULTS Addendum B2).

For TH/W, M/D and A/AE/O glyphs: (1) nearest-class-mean call (templates from canon-labelled glyphs on
corrected-map exact lines OUTSIDE the 56 target lines), validated on every target-line glyph of those classes;
(2) direct glyph-glyph correlation for adjacent pairs: distribution over canon doublets (same) vs canon
look-alike pairs (different) stream-wide, then the candidate pairs.
Output: template.json.  Run: PYTHONUTF8=1 python template.py  (~2 min, segments 56 images)
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP); sys.path.insert(0, os.path.join(LP, "analysis", "stones"))
import pipeline as P  # noqa: E402
from build_dataset import norm_crop  # noqa: E402

gl, po = P.global_lines()
start = np.cumsum([0] + [len(L) for L in gl])[:-1]
cm = json.load(open("analysis/round45/S1-transcription/corrected_map.json"))
SL = json.load(open(os.path.join(HERE, "sealed_lines.json"), encoding="utf-8"))
target = {r["gline"] for r in SL.values() if r["kind"] == "T"}
CAND = [3087, 9612, 9630, 3385, 3928, 3394, 1623, 3782, 3500]  # pairs flagged by pass L / pass P

vec = {}  # global pos -> normalized bitmap
for n in range(56):
    lines, b, gray = P.segment_image(f"data/relikd/p{n}.jpg"); g = np.asarray(gray)
    clean = [L for L in lines if len(L) >= 10]
    for r in cm[str(n)]:
        G = r["true_gline"]
        if G is None: continue
        boxes = clean[r["clean_i"]]
        if len(boxes) == len(gl[G]):
            rng = range(len(boxes))
        elif G == 176:  # canon-1 line; boxes 0..9 precede the C+B merge (pass L read), still 1:1
            rng = range(10)
        else:
            continue
        for j in rng:
            v = norm_crop(g, boxes[j])
            if v is not None: vec[int(start[G] + j)] = v.ravel()
flat = [c for L in gl for c in L]
gline_of = np.repeat(np.arange(len(gl)), [len(L) for L in gl])
FAM = {"THW": "ᚦᚹ", "MD": "ᛗᛞ", "AO": "ᚪᚫᚩ"}
def corr(a, b):
    a = a - a.mean(); b = b - b.mean(); return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))
out = {"n_vec": len(vec), "families": {}}
for fam, runes in FAM.items():
    means = {r: np.mean([v for p, v in vec.items() if flat[p] == r and gline_of[p] not in target], 0) for r in runes}
    call = lambda v: max(means, key=lambda r: corr(v, means[r]))  # noqa: E731
    val = [(p, flat[p], call(v)) for p, v in vec.items() if flat[p] in runes and gline_of[p] in target]
    acc = sum(a == b for _, a, b in val)
    # pair similarity
    same = [corr(vec[p], vec[p + 1]) for p in vec if p + 1 in vec and flat[p] in runes and flat[p] == flat[p + 1]]
    diff = [corr(vec[p], vec[p + 1]) for p in vec if p + 1 in vec and flat[p] in runes and flat[p + 1] in runes
            and flat[p] != flat[p + 1] and p not in CAND]
    out["families"][fam] = {"validation_n": len(val), "validation_correct": acc,
                            "validation_errors": [(p, a, b) for p, a, b in val if a != b],
                            "pair_corr_same": sorted(round(x, 3) for x in same),
                            "pair_corr_diff_summary": [len(diff), round(float(np.max(diff)), 3) if diff else None,
                                                       round(float(np.percentile(diff, 95)), 3) if diff else None],
                            "pair_corr_diff_top5": sorted(round(x, 3) for x in diff)[-5:]}
    for t in CAND:
        if flat[t] in runes and t in vec and t + 1 in vec:
            out.setdefault("candidates", {})[t] = {"canon": [flat[t], flat[t + 1]], "family": fam,
                "template_call": [call(vec[t]), call(vec[t + 1])],
                "corr_to_means": [{r: round(corr(vec[q], m), 3) for r, m in means.items()} for q in (t, t + 1)],
                "pair_corr": round(corr(vec[t], vec[t + 1]), 3)}
json.dump(out, open(os.path.join(HERE, "template.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for fam, d in out["families"].items():
    print(fam, "validation", d["validation_correct"], "/", d["validation_n"], "errors", d["validation_errors"][:8])
    print("   same-pair corr", d["pair_corr_same"], " diff n/max/p95", d["pair_corr_diff_summary"], d["pair_corr_diff_top5"])
for t, c in out.get("candidates", {}).items():
    print("CAND", t, c)
