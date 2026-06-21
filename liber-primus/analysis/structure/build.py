"""End-to-end: segment all pages, align to canon where glyph-count matches,
build 29 templates from canon-labelled glyphs (dominated by correct instances),
then match every glyph and flag image/canon disagreements with margin.

Methodology note: canon labels train the templates, but each rune template is an
average over many (~tens to hundreds) instances, so a single mis-transcribed
glyph is outvoted -- its true shape will then mismatch its (wrong) canon label
and surface as a high-margin disagreement. We separately VALIDATE the matcher by
the round-trip accuracy (best-template == canon-label) on count-matched pages;
high accuracy means templates are sharp and the matcher is trustworthy.
"""
import os, re, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import pipeline as P, stemseg as S
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from lp import gematria as gp  # noqa

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
RELIKD = os.path.join(ROOT, "data", "relikd")
CANON_FILE = os.path.join(ROOT, "data", "krisyotam_runes.txt")
OUT_DIR = os.path.join(ROOT, "analysis", "structure")


def canon_pages():
    data = open(CANON_FILE, encoding="utf-8").read().split("%")
    pages = []
    for sec in data:
        runes = [c for c in sec if 0x16A0 <= ord(c) <= 0x16FF]
        pages.append(runes)
    return pages


def segment_page(path):
    ink = P.load_ink(path)
    x0, x1 = P.central_window(ink)
    bands = [b for b in P.line_bands(ink, x0, x1) if 95 <= b[1] - b[0] <= 135]
    allst = []
    for a, b in bands:
        cs, _ = S.stems(ink[a:b, x0:x1])
        allst.append(cs)
    pitch = S.estimate_pitch(allst)
    glyphs = []
    for a, b in bands:
        li = ink[a:b, x0:x1]
        for (cx0, cx1) in S.split_line(li, pitch):
            sub = li[:, cx0:cx1]
            ys = np.where(sub.any(1))[0]
            if len(ys) == 0:
                continue
            sub2 = sub[ys.min():ys.max() + 1]
            # drop separator dots: very small area
            if sub2.sum() < 0.04 * (b - a) * pitch:
                continue
            glyphs.append(dict(norm=P.normalize(sub2),
                               x0=x0 + cx0, y0=a + ys.min(),
                               w=cx1 - cx0, h=sub2.shape[0]))
    return glyphs, ink


def ncc(a, b):
    af = a.astype(np.float32).ravel()
    bf = b.astype(np.float32).ravel()
    af -= af.mean(); bf -= bf.mean()
    na = np.linalg.norm(af); nb = np.linalg.norm(bf)
    if na == 0 or nb == 0:
        return 0.0
    return float(af.dot(bf) / (na * nb))


def main():
    canon = canon_pages()
    # pass 1: segment all, find count-matched pages for training
    seg = {}
    matched = []
    for pi in range(56):
        path = os.path.join(RELIKD, f"p{pi}.jpg")
        if not os.path.exists(path):
            continue
        glyphs, ink = segment_page(path)
        seg[pi] = glyphs
        cn = len(canon[pi]) if pi < len(canon) else 0
        ok = (cn > 0 and len(glyphs) == cn)
        if ok:
            matched.append(pi)
        print(f"p{pi}: seg={len(glyphs)} canon={cn} {'MATCH' if ok else ''}")
    print(f"count-matched pages: {matched}")
    # build templates from matched pages
    acc = {i: [] for i in range(29)}
    for pi in matched:
        labels = [gp.RUNE_TO_IDX[r] for r in canon[pi]]
        for g, lab in zip(seg[pi], labels):
            acc[lab].append(g["norm"].astype(np.float32))
    templates = {}
    for i in range(29):
        if acc[i]:
            templates[i] = np.mean(acc[i], axis=0)
    print(f"templates built for {len(templates)}/29 runes; "
          f"counts={{ {', '.join(str(len(acc[i])) for i in range(29))} }}")
    return seg, canon, templates, matched


if __name__ == "__main__":
    main()
