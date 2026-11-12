"""R44 / W2-B2 step 3 — the registered finite reads (PREREG §4) over census.json.

R-A cluster identity: the 7 cuneiform-cluster instances aligned by translation (bbox
    top-left), black-mask IoU pairwise. IoU >= 0.95 -> same stamp (placement-only channel).
R-B cluster decomposition: per-instance component geometry.
R-C dot selection stream: all UNLOGGED is_dot components book-wide (0_wisdom excluded: no
    stones glyphs exist for it) in row-major reading order -> nearest-glyph rune indices.
    Adjudicated vs the fixed bar ONLY if L >= 60; else enumeration (measured-only).
R-D per-page UNLOGGED counts (56 values) - enumeration only (L < 60).
R-E constellation geometry: p23 + its p7 twin + the p33/p39 dot rows: centers, pairwise
    distances, the mirror-twin relation, nearest-rune mapping, named-constant comparisons
    ({29, 3301, first primes, gematria}) - RECORDED enumeration, NO verdict (n=5).
"""
import itertools, json, os, sys
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
from scipy import ndimage  # noqa

Image.MAX_IMAGE_PIXELS = None
RELIKD = os.path.join(LP, "data", "relikd")
CEN = json.load(open(os.path.join(HERE, "census.json")))
BARS = {L: B.bar_v3(2000, L, "free") for L in (120, 240, 400, 729)}

CLUSTER_IDS = [("p33", "p33_obj3"), ("p34", "p34_obj0"), ("p35", "p35_obj0"),
               ("p36", "p36_obj0"), ("p37", "p37_obj0"), ("p38", "p38_obj0"),
               ("p39", "p39_obj0")]


def black_crop(page, bbox):
    rgb = np.asarray(Image.open(os.path.join(RELIKD, page + ".jpg")).convert("RGB"))
    x0, x1, y0, y1 = bbox
    sub = rgb[y0:y1, x0:x1]
    lum = sub.mean(axis=2)
    R = sub[:, :, 0].astype(np.int16); G = sub[:, :, 1].astype(np.int16)
    Bc = sub[:, :, 2].astype(np.int16)
    red = (R - (G + Bc) / 2 > 40) & (R > 120) & (G < 80)
    return (lum < C.INK_THR) & ~red


def pad_to(m, shape):
    out = np.zeros(shape, bool)
    out[:m.shape[0], :m.shape[1]] = m
    return out


def best_iou(a, b, search=6):
    """IoU of b over a, translation search +-search px."""
    H = max(a.shape[0], b.shape[0]) + search
    W = max(a.shape[1], b.shape[1]) + search
    A_ = pad_to(a, (H + search, W + search))
    best = 0.0
    for dy in range(-search, search + 1):
        for dx in range(-search, search + 1):
            B_ = np.zeros_like(A_)
            y0, x0 = search + dy, search + dx
            B_[y0:y0 + b.shape[0], x0:x0 + b.shape[1]] = b
            inter = (A_ & B_).sum()
            union = (A_ | B_).sum()
            if union and inter / union > best:
                best = inter / union
    return float(best)


def r_a():
    masks = [(pg, black_crop(pg, CEN["images"][pg]["objects"][
        [o["id"] for o in CEN["images"][pg]["objects"]].index(oid)]["bbox"]))
        for pg, oid in CLUSTER_IDS]
    pairs = {}
    for (p1, m1), (p2, m2) in itertools.combinations(masks, 2):
        pairs["%s~%s" % (p1, p2)] = round(best_iou(m1, m2), 4)
    mn = min(pairs.values())
    return dict(n_instances=len(masks), pairwise_iou=pairs, min_iou=mn,
                same_stamp=bool(mn >= 0.95))


def r_b():
    out = []
    for pg, oid in CLUSTER_IDS:
        rec = CEN["images"][pg]
        o = next(x for x in rec["objects"] if x["id"] == oid)
        comps = [rec["unlogged_components"][i] for i in o["comp_ids"]]
        out.append(dict(page=pg, bbox=o["bbox"], n_components=o["n_components"],
                        comps=[dict(x0=c["x0"], y0=c["y0"], w=c["w"], h=c["h"],
                                    area=c["area"]) for c in comps]))
    return out


def r_c():
    pages = ["p%d" % i for i in range(56)]
    dot_list = glue.dots_reading_order(CEN, pages=pages)
    mapped = glue.map_dots_to_runes(dot_list)
    stream = [m["rune_idx"] for m in mapped if m["rune_idx"] is not None]
    Lx = len(stream)
    res = dict(n_dots=len(mapped), L=Lx, mapped=mapped,
               stream=stream,
               translit="".join(gp.IDX_TO_TRANS[i] for i in stream))
    if Lx >= 60:
        pan = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
        cand = [x for x in (120, 240, 400, 729) if x <= Lx] or [120]
        bar = BARS[max(cand)]
        best = dict(pmax=-99.0)
        n = 0
        s = np.asarray(stream, dtype=np.int64)
        for direction in ("fwd", "rev"):
            x = s if direction == "fwd" else s[::-1]
            for a in range(1, 29):
                for sh in range(29):
                    y = (a * x + sh) % 29
                    r = A.adjudicate(y, pan=pan)
                    n += 1
                    if r["pmax"] > best["pmax"]:
                        best = dict(pmax=float(r["pmax"]), preg=r["preg"],
                                    dir=direction, a=a, s=sh,
                                    degenerate=bool(r["degenerate"]))
        res.update(adjudicated=True, n_decodes=n, bar=round(float(bar), 4), best=best,
                   crossers=int(best["pmax"] >= bar and not best["degenerate"]))
    else:
        res.update(adjudicated=False,
                   verdict="measured-only: L=%d < 60, no bar exists (pending W2-A1)" % Lx)
    return res


def r_d():
    counts = {}
    for i in range(56):
        rec = CEN["images"].get("p%d" % i, {})
        counts["p%d" % i] = rec.get("counts", {}).get("UNLOGGED", 0)
    return dict(per_page_unlogged=counts,
                verdict="measured-only: 56 values < 60, no bar exists")


BIGDOT_SETS = dict(
    p23_constellation=["p23_obj0", "p23_obj1", "p23_obj2", "p23_obj3", "p23_obj4"],
    p7_twin=["p7_obj2", "p7_obj3", "p7_obj4", "p7_obj5", "p7_obj6"],
    p33_row=["p33_obj0", "p33_obj1", "p33_obj2"],
    p39_row=["p39_obj2", "p39_obj3", "p39_obj4"])


def r_e():
    by_img = C.load_glyphs()
    out = {}
    for name, ids in BIGDOT_SETS.items():
        pg = ids[0].split("_")[0]
        rec = CEN["images"][pg]
        objs = {o["id"]: o for o in rec["objects"]}
        dots = []
        for oid in ids:
            x0, x1, y0, y1 = objs[oid]["bbox"]
            dots.append(dict(id=oid, center=[(x0 + x1) / 2, (y0 + y1) / 2],
                             bbox=[x0, x1, y0, y1]))
        comps = [dict(x0=d["bbox"][0], x1=d["bbox"][1], y0=d["bbox"][2], y1=d["bbox"][3],
                      area=0, h=d["bbox"][3] - d["bbox"][2], w=d["bbox"][1] - d["bbox"][0])
                 for d in dots]
        mapped = glue.map_dots_to_runes([(pg, c) for c in comps], by_img=by_img)
        for d, m in zip(dots, mapped):
            d["nearest_rune"] = m["nearest"]
            d["rune_idx"] = m["rune_idx"]
            d["dist_px"] = m["dist"]
        dd = {}
        cs = [d["center"] for d in dots]
        for i, j in itertools.combinations(range(len(cs)), 2):
            dd["%d-%d" % (i, j)] = round(float(np.hypot(cs[i][0] - cs[j][0],
                                                        cs[i][1] - cs[j][1])), 1)
        out[name] = dict(dots=dots, pairwise_dist_px=dd)
    # mirror-twin relation p23 <-> p7 (computed, not assumed)
    a = sorted([d["center"] for d in out["p23_constellation"]["dots"]])
    b = sorted([d["center"] for d in out["p7_twin"]["dots"]])
    resid = [[round(ax - bx, 1), round(ay + by, 1)] for (ax, ay), (bx, by) in zip(a, b)]
    ysums = [r[1] for r in resid]
    out["mirror_twin"] = dict(
        x_matched_residuals=[r[0] for r in resid], y_sums=ysums,
        relation="p23(x,y) == p7(x, %s - y)" % ysums[0] if len(set(ysums)) == 1 and
        all(abs(r[0]) <= 2 for r in resid) else "NOT an exact vertical mirror",
        exact=bool(len(set(ysums)) == 1 and all(abs(r[0]) <= 2 for r in resid)))
    # named-constant comparisons (recorded enumeration, NO verdict; PREREG R-E)
    consts = dict(n_dots_p23=5, n_dots_p33row=3, n_dots_p39row=3,
                  note="5 and 3 are primes; no further structure asserted (n=5, no null)")
    out["constants_enumeration"] = consts
    return out


def main():
    out = dict(bars={str(k): round(v, 4) for k, v in BARS.items()})
    out["R_A_cluster_identity"] = r_a()
    print("R-A done: min IoU %.3f same_stamp=%s" % (
        out["R_A_cluster_identity"]["min_iou"],
        out["R_A_cluster_identity"]["same_stamp"]), flush=True)
    out["R_B_decomposition"] = r_b()
    out["R_C_dot_stream"] = r_c()
    print("R-C: n_dots=%d L=%d adjudicated=%s" % (
        out["R_C_dot_stream"]["n_dots"], out["R_C_dot_stream"]["L"],
        out["R_C_dot_stream"]["adjudicated"]), flush=True)
    out["R_D_page_counts"] = r_d()
    out["R_E_constellations"] = r_e()
    print("R-E mirror:", out["R_E_constellations"]["mirror_twin"]["relation"])
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    rc = out["R_C_dot_stream"]
    print("done. crossers:", rc.get("crossers", 0) if rc["adjudicated"] else "n/a")


if __name__ == "__main__":
    main()
