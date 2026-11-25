"""Audit analysis/stones/alignment.json: for each image, compare the segmented clean-line counts to canon line
lengths under the committed alignment and under shifts -2..+2. Reports images where a shift fits better.
Output: alignment_audit.json (used by adjudicate.py to re-locate items; committed alignment is NOT edited)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP); sys.path.insert(0, os.path.join(LP, "analysis", "stones")); import pipeline as P
gl, po = P.global_lines(); align = json.load(open("analysis/stones/alignment.v1.json"))
out = {}
for n in range(56):
    lines, b, g = P.segment_image(f"data/relikd/p{n}.jpg"); clean = [len(L) for L in lines if len(L) >= 10]
    al = align[str(n)]
    def score(shift):
        return sum(1 for i, c in enumerate(clean) if 0 <= al[0] + shift + i < len(gl) and len(gl[al[0] + shift + i]) == c)
    sc = {s: score(s) for s in range(-2, 3)}
    best = max(sc, key=lambda s: (sc[s], -abs(s)))
    contiguous = al == list(range(al[0], al[0] + len(al)))
    out[n] = {"aligned_first": al[0], "n_aligned": len(al), "n_clean": len(clean), "contiguous": contiguous,
              "exact_by_shift": sc, "best_shift": best, "clean_counts": clean}
    if best != 0 or not contiguous or len(al) != len(clean):
        print(n, "first", al[0], "n_al", len(al), "n_clean", len(clean), "contig", contiguous, sc)
json.dump(out, open(os.path.join(HERE, "alignment_audit.json"), "w"), indent=1)
