"""Full independent transcription pipeline with PER-LINE alignment.

Canon (krisyotam) marks visual line breaks with '/' or newline. We segment each
image into lines, and for every image-line whose glyph count EXACTLY equals the
corresponding canon visual-line rune count, we have a confident positional
alignment for that line. Templates are trained from all such confidently-aligned
glyphs (each rune averaged over many instances). The matcher is validated by
round-trip accuracy on those same aligned glyphs (sharp templates => high acc).
Disagreements = aligned glyphs whose best template != canon label, with margin.
"""
import os, re, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import pipeline as P, ccseg as C
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from lp import gematria as gp  # noqa

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
RELIKD = os.path.join(ROOT, "data", "relikd")
CANON_FILE = os.path.join(ROOT, "data", "krisyotam_runes.txt")
OUT = os.path.join(ROOT, "analysis", "structure")
CROPS = os.path.join(OUT, "disagree_crops")
os.makedirs(CROPS, exist_ok=True)


def canon_page_lines():
    data = open(CANON_FILE, encoding="utf-8").read().split("%")
    pages = []
    for sec in data:
        lines = re.split(r"[/\n]", sec)
        plines = []
        for ln in lines:
            runes = [c for c in ln if 0x16A0 <= ord(c) <= 0x16FF]
            if runes:
                plines.append(runes)
        pages.append(plines)
    return pages


def segment_page_lines(path):
    """Return list of image-lines; each is a list of glyph dicts."""
    ink = P.load_ink(path)
    x0, x1 = P.central_window(ink)
    bands = [b for b in P.line_bands(ink, x0, x1) if 95 <= b[1] - b[0] <= 135]
    out = []
    for a, b in bands:
        li = ink[a:b, x0:x1]
        cells = C.line_glyphs(li)
        gl = []
        for (cx0, cx1, cy0, cy1) in cells:
            sub = li[cy0:cy1 + 1, cx0:cx1 + 1]
            gl.append(dict(norm=P.normalize(sub), x0=x0 + cx0, y0=a + cy0,
                           x1=x0 + cx1, y1=a + cy1, ink=ink))
        out.append((gl, (a, b)))
    return out, ink


def ncc(a, b):
    af = a.astype(np.float32).ravel(); bf = b.astype(np.float32).ravel()
    af -= af.mean(); bf -= bf.mean()
    na = np.linalg.norm(af); nb = np.linalg.norm(bf)
    return 0.0 if na == 0 or nb == 0 else float(af.dot(bf) / (na * nb))


def main():
    canon = canon_page_lines()
    pages_seg = {}
    aligned = []  # (pi, li, glyph, label)
    page_line_match = {}
    for pi in range(56):
        path = os.path.join(RELIKD, f"p{pi}.jpg")
        if not os.path.exists(path):
            continue
        seg, ink = segment_page_lines(path)
        pages_seg[pi] = (seg, path)
        cpls = canon[pi] if pi < len(canon) else []
        # greedily align image-lines to canon-lines in order; mark exact matches
        nmatch = 0
        m = min(len(seg), len(cpls))
        for li in range(m):
            gl = seg[li][0]
            cl = cpls[li]
            if len(gl) == len(cl):
                nmatch += 1
                for g, r in zip(gl, cl):
                    aligned.append((pi, li, g, gp.RUNE_TO_IDX[r]))
        page_line_match[pi] = (nmatch, len(seg), len(cpls))
    print("per-page (img-lines matching canon-lines / img-lines / canon-lines):")
    for pi in sorted(page_line_match):
        nm, ns, nc = page_line_match[pi]
        print(f"  p{pi}: {nm}/{ns} img, canon-lines={nc}")
    # build templates
    acc = {i: [] for i in range(29)}
    for (pi, li, g, lab) in aligned:
        acc[lab].append(g["norm"].astype(np.float32))
    templates = {i: np.mean(acc[i], axis=0) for i in range(29) if acc[i]}
    print(f"\ntemplates: {len(templates)}/29 runes, "
          f"instance counts: {[len(acc[i]) for i in range(29)]}")
    print(f"total aligned glyphs (training+validation): {len(aligned)}")

    def match(norm):
        scores = sorted(((ncc(norm, t), i) for i, t in templates.items()),
                        reverse=True)
        best = scores[0]; second = scores[1] if len(scores) > 1 else (0, -1)
        return best[1], best[0], best[0] - second[0]

    # VALIDATE on aligned glyphs
    correct = 0
    for (pi, li, g, lab) in aligned:
        mi, sc, mar = match(g["norm"])
        if mi == lab:
            correct += 1
    acc_solved = correct / len(aligned) if aligned else 0.0
    print(f"\nMATCHER round-trip accuracy on aligned glyphs: "
          f"{acc_solved:.4f} ({correct}/{len(aligned)})")
    return pages_seg, canon, templates, match, aligned, acc_solved


if __name__ == "__main__":
    main()
