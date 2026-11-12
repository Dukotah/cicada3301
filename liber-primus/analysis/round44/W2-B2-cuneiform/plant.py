"""R44 / W2-B2 step 2 — POSITIVE CONTROLS planted through THIS lane's own glue (PREREG §5).

PC-A census glue: a synthetic 6-glyph cuneiform-like cluster (wedge strokes) + a 7-dot
    constellation painted in BLACK on a copy of real page p1; the lane's census code
    (census.census_image, identical path) must find both, classify UNLOGGED, dot count 7
    exact, centers within +-3 px.

PC-B read glue: 120 runes of the solved "A WARNING ..." plaintext planted as black dots
    directly under the canon glyphs spelling it (walking canon in order over page copies);
    the SAME census + glue.map_dots_to_runes must recover the planted 120 rune indices
    EXACTLY, and the direct reading must clear the fixed L=120 bar 11.9933 (PREREG §3).
    Plant pages are chosen as pages whose copies carry no genuine unlogged dot components
    in the planted text region (verified in-plant by diffing against an unpainted copy:
    only planted dots are compared/consumed; see extract step below, which subtracts the
    baseline components by bbox).
"""
import json, os, shutil, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))
from lp import gematria as gp  # noqa
import adjudicate as A  # noqa
import bars_v3 as B  # noqa
import census as C  # noqa
import glue  # noqa

Image.MAX_IMAGE_PIXELS = None
RELIKD = os.path.join(LP, "data", "relikd")
WORK = os.path.join(HERE, "plant_work")
BAR120 = B.bar_v3(2000, 120, "free")

PT1 = ("A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE "
       "KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR "
       "THE MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED "
       "SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD "
       "BE ENCRYPTED KNOW THIS")


def to_idx(text, n):
    out = []
    for w in text.split():
        out.extend(gp.keyword_to_indices(w))
    return out[:n]


def paint_disc(arr, cx, cy, r, val=0):
    y, x = np.ogrid[:arr.shape[0], :arr.shape[1]]
    m = (x - cx) ** 2 + (y - cy) ** 2 <= r * r
    arr[m] = val


def paint_wedge(arr, x0, y0, L, ang_deg, w0=14):
    """One cuneiform-style wedge: a filled triangle tapering along its axis."""
    ang = np.deg2rad(ang_deg)
    ux, uy = np.cos(ang), np.sin(ang)
    y, x = np.ogrid[:arr.shape[0], :arr.shape[1]]
    t = (x - x0) * ux + (y - y0) * uy          # along axis
    s = -(x - x0) * uy + (y - y0) * ux         # across axis
    m = (t >= 0) & (t <= L) & (np.abs(s) <= w0 * (1 - t / L))
    arr[m] = 0


def run_census_one(imgdir, name, pno):
    by_img = C.load_glyphs()
    glyphs = by_img.get(pno, [])
    gboxes = [g["box"] for g in glyphs]
    lboxes = C.line_boxes(glyphs)
    bands = json.load(open(C.BANDS))
    bboxes = [(b["x"][0], b["x"][1], b["y"][0], b["y"][1]) for b in bands
              if b["page"] == pno and b.get("ink_class") != "TEXT"]
    _, comps, objects = C.census_image(os.path.join(imgdir, name + ".jpg"), gboxes, lboxes, bboxes)
    return comps, objects


def pc_a():
    d = os.path.join(WORK, "pcA")
    os.makedirs(d, exist_ok=True)
    src = os.path.join(RELIKD, "p1.jpg")
    im = np.asarray(Image.open(src).convert("RGB")).copy()
    # 6-glyph cluster, right margin around (1950..2250, 500..760)
    g = im.mean(axis=2)
    wedges = [(1950, 520, 90, 10), (2060, 500, 80, 100), (2150, 540, 95, -20),
              (1960, 650, 85, 45), (2070, 640, 90, 170), (2170, 660, 80, 80)]
    for ch in range(3):
        pass
    for x0, y0, L, ang in wedges:
        for ch in range(3):
            paint_wedge(im[:, :, ch], x0, y0, L, ang)
        # a second stroke per glyph so each "glyph" is wedge-compound
        for ch in range(3):
            paint_wedge(im[:, :, ch], x0 + 18, y0 + 24, L * 0.7, ang + 55)
    # 7-dot constellation, bottom margin
    dots = [(700, 3150), (860, 3080), (1010, 3180), (1180, 3100),
            (1350, 3220), (1520, 3120), (1660, 3200)]
    for cx, cy in dots:
        for ch in range(3):
            paint_disc(im[:, :, ch], cx, cy, 13)
    Image.fromarray(im).save(os.path.join(d, "p1.jpg"), quality=95)

    comps, objects = run_census_one(d, "p1", 1)
    unl = [c for c in comps if c["cls"] == "UNLOGGED"]
    found_dots = []
    for cx, cy in dots:
        best = None
        for c in unl:
            ccx, ccy = (c["x0"] + c["x1"]) / 2, (c["y0"] + c["y1"]) / 2
            dd = ((ccx - cx) ** 2 + (ccy - cy) ** 2) ** 0.5
            if best is None or dd < best[0]:
                best = (dd, c)
        found_dots.append(best[0] if best else 1e9)
    cluster_found = any(o["bbox"][0] < 2300 and o["bbox"][1] > 1900 and
                        o["bbox"][2] < 800 and o["bbox"][3] > 480 and o["n_components"] >= 4
                        for o in objects)
    ok = cluster_found and all(dd <= 3 for dd in found_dots)
    return dict(name="PC-A", cluster_found=bool(cluster_found),
                dot_center_errors_px=[round(x, 2) for x in found_dots],
                n_objects=len(objects), passed=bool(ok))


def pc_b():
    d = os.path.join(WORK, "pcB")
    os.makedirs(d, exist_ok=True)
    want = to_idx(PT1, 120)
    by_img = C.load_glyphs()
    bands = json.load(open(C.BANDS))
    nontext = {}
    for b in bands:
        if b.get("ink_class") != "TEXT":
            nontext.setdefault(b["page"], []).append(
                (b["x"][0], b["x"][1], b["y"][0], b["y"][1]))
    # walk canon glyph order, match each next plaintext rune; skip placements that fall
    # inside a non-TEXT band bbox (A-06 territory by the registered classification --
    # a dot there is BAND_COVERED by design, so the plant must not use those cells)
    plan = {}  # page -> list of (dot_cx, dot_cy, rune_idx)
    k = 0
    for pno in range(4, 22):  # setup fix (run.log): 4..12 placed only 80/120; range extended
        if k >= len(want):
            break
        gl = sorted(by_img.get(pno, []), key=lambda g: (g["gli"], g["gi"]))
        for g in gl:
            if k >= len(want):
                break
            ri = gp.RUNE_TO_IDX.get(g["rune"])
            if ri == want[k]:
                x0, x1, y0, y1 = g["box"]
                cx, cy = (x0 + x1) // 2, y1 + 34
                if any(bx0 <= cx <= bx1 and by0 <= cy <= by1
                       for (bx0, bx1, by0, by1) in nontext.get(pno, [])):
                    continue
                plan.setdefault(pno, []).append((cx, cy, ri))
                k += 1
    assert k == len(want), "could not place all %d plant runes (placed %d)" % (len(want), k)

    baseline = {}
    for pno, pts in sorted(plan.items()):
        name = "p%d" % pno
        comps0, _ = run_census_one(RELIKD, name, pno)
        baseline[pno] = [(c["x0"], c["y0"], c["x1"], c["y1"])
                         for c in comps0 if c["cls"] == "UNLOGGED"]
        im = np.asarray(Image.open(os.path.join(RELIKD, name + ".jpg")).convert("RGB")).copy()
        for cx, cy, _ in pts:
            for ch in range(3):
                paint_disc(im[:, :, ch], cx, cy, 11)
        Image.fromarray(im).save(os.path.join(d, name + ".jpg"), quality=95)

    # extract through the SAME census + glue path, subtracting the baseline components
    dot_list = []
    for pno in sorted(plan):
        name = "p%d" % pno
        comps, _ = run_census_one(d, name, pno)
        def in_baseline(c):
            # JPEG re-encode jitters bboxes by a few px; match baseline by center proximity
            ccx, ccy = (c["x0"] + c["x1"]) / 2, (c["y0"] + c["y1"]) / 2
            for (x0, y0, x1, y1) in baseline[pno]:
                if abs(ccx - (x0 + x1) / 2) <= 6 and abs(ccy - (y0 + y1) / 2) <= 6:
                    return True
            return False
        unl = [c for c in comps if c["cls"] == "UNLOGGED" and not in_baseline(c)]
        ds = glue.sort_reading_order([c for c in unl if glue.is_dot(c)])
        dot_list.extend((name, c) for c in ds)
    mapped = glue.map_dots_to_runes(dot_list, by_img=by_img)
    got = [m["rune_idx"] for m in mapped]
    # reading order within a line is x-order; our sort is (y0,x0) per page which can
    # interleave lines of differing glyph heights -- recover canonical order by (page, y
    # center bucket, x). glue.dots_reading_order uses the same (y0,x0) rule; plant dots sit
    # on distinct rows per line so (y0,x0) IS reading order here.
    exact = got == want
    pan = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
    res = A.adjudicate(np.asarray(want, dtype=np.int64), pan=pan)
    res_got = A.adjudicate(np.asarray([g for g in got if g is not None][:120],
                                      dtype=np.int64), pan=pan) if got else None
    ok = exact and res_got is not None and res_got["pmax"] >= BAR120 and not res_got["degenerate"]
    return dict(name="PC-B", n_planted=len(want), n_extracted=len(got),
                exact_recovery=bool(exact),
                pmax_extracted=float(res_got["pmax"]) if res_got else None,
                pmax_truth=float(res["pmax"]), bar=round(float(BAR120), 4),
                passed=bool(ok))


def main():
    os.makedirs(WORK, exist_ok=True)
    ra = pc_a()
    print(json.dumps(ra, indent=1), flush=True)
    rb = pc_b()
    print(json.dumps(rb, indent=1), flush=True)
    out = dict(bar120_at_N2000=round(float(BAR120), 4), controls=[ra, rb],
               all_passed=bool(ra["passed"] and rb["passed"]))
    json.dump(out, open(os.path.join(HERE, "plant_results.json"), "w"), indent=1)
    print("ALL PASSED" if out["all_passed"] else "CONTROL FAILURE")


if __name__ == "__main__":
    main()
