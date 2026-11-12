"""R44 / P1 step 3 — POSITIVE CONTROLS planted through THIS lane's own glue (PREREG §5).

P1  selection plant, image -> extractor -> reader END TO END:
    120 runes of the solved "WELCOME PILGRIM ..." plaintext are embedded as a red SELECTION:
    walking the canon in reading order over images with NO genuine red, each next plaintext
    rune is matched to the next canon-valued glyph of that rune and its stones box is painted
    red (RGB ~ (200,2,3)) in a COPY of the page image. The lane's own census extractor
    (census.py, identical code path) is then run on the copies; the extracted red-glyph
    stream must equal the planted 120 indices EXACTLY, and its direct reading must clear the
    L_cap-120 bar (12.8507) under panel-R36.

P2  dot-block plant: one 13-dot and one 10-dot red block painted onto a copy of a no-red
    page; the census must return exactly those two blocks with counts [13, 10] in y-order.

P3  reading-C decode-glue plant: known "A WARNING ..." plaintext (240 runes) encrypted with
    k = prime_totient_stream offset 17 (vigm); fed through the SAME reading-C sweep function
    used on real pages; must recover at the planted cell with pmax >= bar(240) = 17.1842.
"""
import json, os, shutil, subprocess, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))
from lp import gematria as gp, ciphers  # noqa
import adjudicate as A  # noqa
import bars_v3 as B  # noqa

Image.MAX_IMAGE_PIXELS = None
N = gp.N
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
BAR120 = B.bar_v3(10000, 120, "free")
BAR240 = B.bar_v3(10000, 240, "free")
RELIKD = os.path.join(LP, "data", "relikd")
WORK = os.path.join(HERE, "plant_work")
RED = (200, 2, 3)

PT2 = ("WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY "
       "TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU "
       "WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR "
       "CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF")
PT1 = ("A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE "
       "KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR "
       "THE MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED "
       "SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD "
       "BE ENCRYPTED KNOW THIS")


def to_idx(text, n):
    out = []
    for w in text.split():
        try:
            out.extend(gp.keyword_to_indices(w))
        except Exception:
            pass
    return out[:n]


def main():
    census = json.load(open(os.path.join(HERE, "census.json")))
    red_imgs = {g["img"] for g in census["red_glyphs"]}
    red_imgs |= {int(k) for k, v in census["images"].items() if v["n_components"] > 0}

    sys.path.insert(0, HERE)
    import census as C  # the lane's own extractor, same code path

    glyphs = C.load_glyphs()
    results = {"bar120": round(BAR120, 4), "bar240": round(BAR240, 4)}

    # ---------------- P1 ----------------
    plan = to_idx(PT2, 120)
    assert len(plan) == 120
    order = sorted((g for g in glyphs if g["img"] not in red_imgs),
                   key=lambda g: (g["gli"], g["gi"]))
    sel, k = [], 0
    for g in order:
        if k >= len(plan):
            break
        if g["rune"] in gp.RUNE_TO_IDX and gp.RUNE_TO_IDX[g["rune"]] == plan[k]:
            sel.append(g)
            k += 1
    assert k == len(plan), f"only matched {k}/120"
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    by_img = {}
    for g in sel:
        by_img.setdefault(g["img"], []).append(g)
    for img, gs in sorted(by_img.items()):
        rgb = np.array(Image.open(os.path.join(RELIKD, f"p{img}.jpg")).convert("RGB"))
        for g in gs:
            x0, x1, y0, y1 = g["box"]
            sub = rgb[y0:y1, x0:x1]
            ink = sub.mean(2) < C.INK_THR
            sub[ink] = RED
            rgb[y0:y1, x0:x1] = sub
        Image.fromarray(rgb).save(os.path.join(WORK, f"p{img}.png"))
    # extract with the lane's own census code on the copies
    ex = []
    for img in sorted(by_img):
        gb = [g["box"] for g in glyphs if g["img"] == img]
        rgb, redm, comps, blocks = C.census_image(os.path.join(WORK, f"p{img}.png"), gb)
        for g in sorted((g for g in glyphs if g["img"] == img),
                        key=lambda g: (g["gli"], g["gi"])):
            x0, x1, y0, y1 = g["box"]
            if C.box_red_fraction(rgb, redm, x0, x1, y0, y1) > C.RED_FRAC_THR:
                ex.append(g)
    ex.sort(key=lambda g: (g["gli"], g["gi"]))
    got = [gp.RUNE_TO_IDX[g["rune"]] for g in ex]
    exact = got == plan
    res = A.adjudicate(np.array(got, dtype=np.int64), pan=PAN)
    p1 = dict(planted=len(plan), extracted=len(got), exact_recovery=bool(exact),
              pmax=round(float(res["pmax"]), 3), preg=int(res["preg"]),
              degenerate=bool(res["degenerate"]), bar=round(BAR120, 4),
              passed=bool(exact and res["pmax"] >= BAR120 and not res["degenerate"]),
              n_images=len(by_img))
    results["P1"] = p1
    print("P1:", json.dumps(p1))

    # ---------------- P2 ----------------
    img2 = 9   # no red on p9
    assert img2 not in red_imgs
    rgb = np.array(Image.open(os.path.join(RELIKD, f"p{img2}.jpg")).convert("RGB"))
    def paint_block(cx, cy, n_dots):
        # diamond-ish layout, 10px dots, 18px pitch (mimics the real 39x86 ornaments)
        layout = [(r, c) for r in range(5) for c in range(3)]
        pts = layout[:n_dots]
        for r, c in pts:
            y, x = cy + r * 18, cx + c * 18
            rgb[y:y + 10, x:x + 10] = RED
    # margin placement: real ornament blocks are free-standing; a block painted over a text
    # line overlaps stones glyph boxes and is (correctly) classified RUNE_OVERLAP, not DOT
    paint_block(900, 3050, 13)
    paint_block(1300, 3050, 10)
    path2 = os.path.join(WORK, f"p{img2}_dots.png")
    Image.fromarray(rgb).save(path2)
    _, _, comps, blocks = C.census_image(path2, [g["box"] for g in glyphs if g["img"] == img2])
    counts = [b["n_dots"] for b in sorted(blocks, key=lambda b: b["bbox"][2])]
    p2 = dict(blocks_found=counts, expect=[13, 10], passed=bool(counts == [13, 10]))
    results["P2"] = p2
    print("P2:", json.dumps(p2))

    # ---------------- P3 ----------------
    from readings import sweep_reading_c   # the SAME glue used on real pages
    pt = np.array(to_idx(PT1, 240), dtype=np.int64)
    kk = np.array(ciphers.prime_totient_stream(240 + 17)[17:17 + 240], dtype=np.int64)
    cpage = (pt + kk) % N
    best, crossers, count = sweep_reading_c(cpage, offsets=[17, 3, 90], pan=PAN)
    hit = (best["gen"] == "prime_totient" and best["offset"] == 17 and best["cfg"] == "vigm"
           and best["pmax"] >= best["bar"])
    rec = bool(hit and best["decode"] == pt.tolist())
    p3 = dict(grid=count, best={k: best[k] for k in ("pmax", "gen", "offset", "cfg", "bar")},
              found_planted_cell=bool(hit), plaintext_recovered=rec,
              passed=bool(hit and rec))
    results["P3"] = p3
    print("P3:", json.dumps(p3))

    results["all_passed"] = bool(p1["passed"] and p2["passed"] and p3["passed"])
    json.dump(results, open(os.path.join(HERE, "plant_results.json"), "w"), indent=1)
    print("ALL PASSED" if results["all_passed"] else "CONTROL FAILURE")


if __name__ == "__main__":
    main()
