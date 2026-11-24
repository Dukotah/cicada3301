"""Addendum A2: re-derive control (frame C) labels by whole-page reading-order alignment.

build_set.py matched solved-page image lines to canon lines by equal count, which mislabels when a page
opens with a drop-cap rune (excluded by the segmenter's height filter): image line 1 is then one short and
every later line is matched to the wrong canon line. Fix (decided from the image, before re-scoring):
concatenate all segmented runic boxes of the page in reading order (lines with >= 3 glyphs, top to bottom,
left to right); if that count equals canon-page-count - 1, the first canon rune is the drop cap and
box[i] <-> canon[i+1]; if equal, box[i] <-> canon[i]; otherwise the page is unusable as a control.
The control BOXES (and therefore the crops that were read) are unchanged; only their labels are re-derived.
Output: controls_relabel.json
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP); sys.path.insert(0, os.path.join(LP, "src")); sys.path.insert(0, os.path.join(LP, "analysis", "stones"))
import pipeline as P
CTRL_DIR = os.path.join(os.path.dirname(LP), "corpus", "A-primary-artifacts", "cijhho123", "2014", "Liber Primus", "liber primus images full")
segs = open("data/krisyotam_runes.txt", encoding="utf-8").read().split("%")
sealed = json.load(open(os.path.join(HERE, "sealed_manifest.json"), encoding="utf-8"))["items"]
out = {"pages": {}, "items": {}}
for seg, img in ((55, "73.jpg"), (56, "74.jpg")):
    R = [c for c in segs[seg] if c in P.RUNES]
    lines, b, g = P.segment_image(os.path.join(CTRL_DIR, img))
    B = [box for L in lines if len(L) >= 3 for box in L]
    off = 1 if len(B) == len(R) - 1 else (0 if len(B) == len(R) else None)
    out["pages"][img] = {"n_boxes": len(B), "n_canon": len(R), "offset": off}
    if off is None:
        for iid, rec in sealed.items():
            if rec["frame"] == "C" and rec["img"] == img:
                out["items"][iid] = {"img": img, "old_label": rec["canon"], "new_label": None}
        continue
    key = {(bx["x0"], bx["y0"]): R[i + off] for i, bx in enumerate(B)}
    # replay build_set.py's (buggy) count-matching to recover which box each sealed (cline, j) referred to
    clines = [[c for c in l if c in P.RUNES] for l in segs[seg].split("/")]
    clines = [c for c in clines if c]
    replay, ci = {}, 0
    for L in [L for L in lines if len(L) >= 3]:
        while ci < len(clines) and len(clines[ci]) != len(L):
            ci += 1
        if ci >= len(clines):
            break
        for j, box in enumerate(L):
            replay[(ci, j)] = box
        ci += 1
    for iid, rec in sealed.items():
        if rec["frame"] == "C" and rec["img"] == img:
            box = replay[(rec["cline"], rec["pos_in_line"])]
            assert clines[rec["cline"]][rec["pos_in_line"]] == rec["canon"]
            out["items"][iid] = {"img": img, "old_label": rec["canon"], "new_label": key[(box["x0"], box["y0"])]}
json.dump(out, open(os.path.join(HERE, "controls_relabel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(out["pages"], "relabelled", sum(v["new_label"] is not None for v in out["items"].values()), "dropped", sum(v["new_label"] is None for v in out["items"].values()))
