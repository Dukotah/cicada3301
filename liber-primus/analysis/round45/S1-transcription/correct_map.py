"""Corrected image-line -> canon-line registration (does not edit analysis/stones/alignment.json).

build_dataset.py / build_set.py pair clean[i] (image lines with >= 10 segments) with alignment[n][i]
positionally. When a short canon line (< 10 glyphs) is dropped from clean, or a line is missing, every
line above the gap is registered one canon line off; boxes are then 'exact' wherever two adjacent canon
lines happen to share a length. Here: Needleman-Wunsch between ALL segmented lines (>= 3 segments) of the
image and the canon lines of the image's OWN page (majority page of its aligned lines; canon '%' page breaks
are an independent constraint), score +3 equal count, +1 |diff| <= 2, gap -1. (A first version used a
+-3-line window across page breaks; it slid page-first lines onto the previous page and is superseded.)
Output: corrected_map.json  {image: [{"clean_i", "orig_gline", "true_gline", "count", "true_len"}]}"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP); sys.path.insert(0, os.path.join(LP, "analysis", "stones")); import pipeline as P
gl, po = P.global_lines(); align = json.load(open("analysis/stones/alignment.json"))
NEG = -10 ** 9
def nw(a, b):
    n, m = len(a), len(b); S = [[0] * (m + 1) for _ in range(n + 1)]; T = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): S[i][0] = -i; T[i][0] = "u"
    for j in range(1, m + 1): S[0][j] = -j; T[0][j] = "l"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d = abs(a[i - 1] - b[j - 1]); s = 3 if d == 0 else (1 if d <= 2 else NEG)
            S[i][j], T[i][j] = max((S[i - 1][j - 1] + s, "d"), (S[i - 1][j] - 1, "u"), (S[i][j - 1] - 1, "l"))
    i, j, pairs = n, m, {}
    while i > 0 or j > 0:
        t = T[i][j]
        if t == "d": pairs[i - 1] = j - 1; i -= 1; j -= 1
        elif t == "u": i -= 1
        else: j -= 1
    return pairs
out, bad = {}, []
for n in range(56):
    lines, b, g = P.segment_image(f"data/relikd/p{n}.jpg")
    all_lines = [L for L in lines if len(L) >= 3]
    clean_ids = [k for k, L in enumerate(all_lines) if len(L) >= 10]
    al = align[str(n)]
    from collections import Counter
    page = Counter(po[g_] for g_ in al).most_common(1)[0][0]
    pl = [g_ for g_ in range(len(gl)) if po[g_] == page]
    if n == 49:  # images 49 and 50 both carry page-49 lines in alignment.json; keep the committed split
        pl = [g_ for g_ in pl if g_ in al]
    if n == 50:
        pl = [g_ for g_ in pl if g_ in al]
    lo = pl[0]
    pairs = nw([len(L) for L in all_lines], [len(gl[g_]) for g_ in pl])
    rows = []
    for ci, k in enumerate(clean_ids):
        orig = al[ci] if ci < len(al) else None
        true = lo + pairs[k] if k in pairs else None
        rows.append({"clean_i": ci, "orig_gline": orig, "true_gline": true, "count": len(all_lines[k]),
                     "true_len": len(gl[true]) if true is not None else None})
        if orig != true:
            bad.append((n, ci, orig, true, len(all_lines[k]), len(gl[orig]) if orig is not None else None))
    out[n] = rows
json.dump(out, open(os.path.join(HERE, "corrected_map.json"), "w"), indent=1)
print("misregistered clean lines (image, clean_i, orig, true, count, orig_len):")
for r in bad: print(" ", r, "FALSE-EXACT" if r[4] == r[5] else "")
