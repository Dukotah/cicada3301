"""L5 / A-04 - INDEPENDENT instrument: native-resolution nearest-exemplar glyph matching.

Rationale. The pp49-51 images are 400-DPI Ghostscript renders of typeset text, so two
occurrences of the same character at the same size should be *pixel-identical*, not merely
similar. That is a testable claim, and if it holds it converts glyph identification from a
fuzzy scoring problem into a lookup.

This script does three things, in order:

  1. RENDER-DETERMINISM CONTROL. For every symbol class with >= 2 uncontested exemplars,
     measure the pairwise best-alignment IoU of the native (un-rescaled) glyph bitmaps.
     If within-class IoU ~ 1.0 while between-class IoU is well below, a single exemplar is
     a sufficient template -- which is what licenses using the n=1 classes I, i, l.

  2. LEAVE-ONE-OUT POSITIVE CONTROL. Classify every uncontested glyph (both the leading
     digit and the trailing symbol) by nearest exemplar with itself removed, and score
     against canon_256.bin. This is the automated instrument's measured recovery, and it
     is reported separately for the case-ambiguous glyph classes.

  3. ADJUDICATION. Rank all classes for each contested glyph, reporting best IoU per
     class and the margin between rank 1 and rank 2. Both glyphs of every contested cell
     are classified -- idx 215 is contested in BOTH positions, so its leading digit is
     adjudicated too rather than assumed.

    python3 pixelmatch.py
"""
import json
import os

import numpy as np

import grid
import glyphmatch as gm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CANON = os.path.join(ROOT, "liber-primus", "analysis", "pp49_51", "canon_256.bin")
ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx"
CONTESTED = [25, 175, 182, 199, 215, 237]
CONFLICT = [25, 45, 50, 165, 172, 175, 182, 199, 215, 237, 246]
AMBIG_CLASSES = set("IilL1Oo0QWwSs5KkVv")
SHIFT = 3
# exemplars per class consulted in the leave-one-out control. Control 1 measures
# within-class bitmap agreement; where that is ~1.0 a small number of representatives
# is sufficient and the LOO pass stays inside the anti-stall budget. Adjudication of the
# contested cells always consults EVERY exemplar of every class.
REPS = 3


def best_iou(a, b, shift=SHIFT):
    """Max IoU of two boolean bitmaps over integer translations in [-shift, shift]^2.
    Bitmaps are NOT rescaled: size mismatch is itself evidence."""
    H = max(a.shape[0], b.shape[0]) + 2 * shift
    W = max(a.shape[1], b.shape[1]) + 2 * shift
    A = np.zeros((H, W), bool)
    A[shift:shift + a.shape[0], shift:shift + a.shape[1]] = a
    best = 0.0
    for dy in range(-shift, shift + 1):
        for dx in range(-shift, shift + 1):
            B = np.zeros((H, W), bool)
            y0, x0 = shift + dy, shift + dx
            B[y0:y0 + b.shape[0], x0:x0 + b.shape[1]] = b
            u = np.logical_or(A, B).sum()
            if not u:
                continue
            v = np.logical_and(A, B).sum() / u
            if v > best:
                best = float(v)
    return best


def extract():
    """glyphs[i] = native-resolution digit mask, symbol mask, and baseline metrics."""
    with open(os.path.join(HERE, "grid.json")) as f:
        g = json.load(f)
    ims = gm._pages()
    out = {}
    for i in range(256):
        page, j = grid.idx_to_cell(i)
        gl = gm.cell_glyphs(ims[page], g[page][j])
        if len(gl) != 2:
            out[i] = None
            continue
        (m1, ax0, ay0, ax1, ay1), (m2, bx0, by0, bx1, by1) = gl
        out[i] = {
            "d": m1, "s": m2,
            "h1": ay1 - ay0,
            "dy_top": ay0 - by0, "dy_bot": by1 - ay1,
            "sh": by1 - by0, "sw": bx1 - bx0,
        }
    return out


def main():
    canon = open(CANON, "rb").read()
    G = extract()
    bad = sorted(i for i, v in G.items() if v is None)
    print("segmented %d/256 cells (failed: %s)" % (256 - len(bad), bad))

    uncontested = [i for i in range(256) if i not in CONFLICT and G[i] is not None]
    sym_of = {i: ALPHA[canon[i] % 60] for i in uncontested}
    dig_of = {i: str(canon[i] // 60) for i in uncontested}

    byclass = {}
    for i in uncontested:
        byclass.setdefault(sym_of[i], []).append(i)
    bydigit = {}
    for i in uncontested:
        bydigit.setdefault(dig_of[i], []).append(i)

    report = {}

    # ---- 1. render-determinism control ------------------------------------
    print("\n" + "=" * 74)
    print("CONTROL 1 -- render determinism: within-class pairwise native-bitmap IoU")
    print("=" * 74)
    within = []
    for s, idxs in sorted(byclass.items()):
        if len(idxs) < 2:
            continue
        vals = []
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                vals.append(best_iou(G[idxs[a]]["s"], G[idxs[b]]["s"]))
        within.append((s, len(idxs), min(vals), float(np.mean(vals))))
    worst = sorted(within, key=lambda r: r[2])[:8]
    allmin = min(r[2] for r in within)
    allmean = float(np.mean([r[3] for r in within]))
    print("  classes with n>=2: %d   mean within-class IoU = %.4f   worst single pair = %.4f"
          % (len(within), allmean, allmin))
    print("  lowest-agreement classes: " +
          "  ".join("%s(n=%d) min=%.3f" % (s, n, mn) for s, n, mn, _ in worst))
    bet = []
    keys = [s for s in byclass if s in AMBIG_CLASSES]
    for a in range(len(keys)):
        for b in range(a + 1, len(keys)):
            bet.append((best_iou(G[byclass[keys[a]][0]]["s"], G[byclass[keys[b]][0]]["s"]),
                        keys[a], keys[b]))
    bet.sort(reverse=True)
    print("  highest between-class IoU among the ambiguous classes: " +
          "  ".join("%s/%s=%.3f" % (x, y, v) for v, x, y in bet[:5]))
    report["determinism"] = {
        "within_class_mean_iou": round(allmean, 4),
        "within_class_min_iou": round(allmin, 4),
        "n_classes_ge2": len(within),
        "worst_classes": [{"sym": s, "n": n, "min_iou": round(mn, 4)} for s, n, mn, _ in worst],
        "max_between_class_iou_ambiguous": [
            {"a": x, "b": y, "iou": round(v, 4)} for v, x, y in bet[:5]],
    }

    # ---- 2. leave-one-out positive control --------------------------------
    print("\n" + "=" * 74)
    print("CONTROL 2 -- leave-one-out nearest-exemplar accuracy (uncontested cells)")
    print("=" * 74)
    for what, table, truth, key in (("symbol", byclass, sym_of, "s"),
                                    ("digit", bydigit, dig_of, "d")):
        ok = n = 0
        amb_ok = amb_n = 0
        misses = []
        skipped = []
        for i in uncontested:
            t = truth[i]
            if len(table[t]) < 2:
                skipped.append(i)
                continue
            scores = []
            for c, idxs in table.items():
                pool = [k for k in idxs if k != i][:REPS]
                if not pool:
                    continue
                scores.append((max(best_iou(G[i][key], G[k][key]) for k in pool), c))
            scores.sort(reverse=True)
            hit = scores[0][1] == t
            ok += hit
            n += 1
            if t in AMBIG_CLASSES:
                amb_n += 1
                amb_ok += hit
            if not hit:
                misses.append({"idx": i, "true": t, "got": scores[0][1],
                               "iou": round(scores[0][0], 4)})
        acc = 100.0 * ok / n if n else float("nan")
        aacc = 100.0 * amb_ok / amb_n if amb_n else float("nan")
        print("  %-6s: %d/%d = %.1f%%   ambiguous-class %d/%d = %.1f%%"
              % (what, ok, n, acc, amb_ok, amb_n, aacc))
        if misses:
            print("    misses: %s" % misses[:10])
        if skipped:
            print("    NOT TESTABLE (singleton class, LOO removes the only exemplar): "
                  "%d cells, classes %s"
                  % (len(skipped), sorted(set(truth[i] for i in skipped))))
        report["loo_" + what] = {
            "correct": ok, "n": n, "accuracy": ok / n if n else None,
            "ambiguous_correct": amb_ok, "ambiguous_n": amb_n,
            "ambiguous_accuracy": amb_ok / amb_n if amb_n else None,
            "misses": misses,
            "not_testable_singleton_cells": skipped,
            "not_testable_singleton_classes": sorted(set(truth[i] for i in skipped)),
        }

    # ---- 3. adjudicate the contested cells --------------------------------
    print("\n" + "=" * 74)
    print("ADJUDICATION -- nearest exemplar over all classes, BOTH glyphs")
    print("=" * 74)
    adj = {}
    for i in CONTESTED:
        entry = {}
        for what, table, key in (("digit", bydigit, "d"), ("symbol", byclass, "s")):
            scores = []
            for c, idxs in table.items():
                scores.append((max(best_iou(G[i][key], G[k][key]) for k in idxs), c))
            scores.sort(reverse=True)
            entry[what] = {
                "top": [{"cls": c, "iou": round(v, 4)} for v, c in scores[:6]],
                "margin": round(scores[0][0] - scores[1][0], 4),
                "best": scores[0][1], "best_iou": round(scores[0][0], 4),
            }
        d = entry["digit"]["best"]
        s = entry["symbol"]["best"]
        entry["token"] = d + s
        entry["byte"] = int(d) * 60 + ALPHA.index(s)
        entry["native_px"] = {"digit_h": int(G[i]["h1"]), "sym_h": int(G[i]["sh"]),
                              "sym_w": int(G[i]["sw"]), "dy_top": int(G[i]["dy_top"]),
                              "dy_bot": int(G[i]["dy_bot"])}
        adj[i] = entry
        print("\nidx %3d  ->  token %r  byte %d   (canon %d)"
              % (i, entry["token"], entry["byte"], canon[i]))
        print("   digit : " + "  ".join("%s=%.3f" % (x["cls"], x["iou"])
                                        for x in entry["digit"]["top"][:4])
              + "   margin %.3f" % entry["digit"]["margin"])
        print("   symbol: " + "  ".join("%s=%.3f" % (x["cls"], x["iou"])
                                        for x in entry["symbol"]["top"][:4])
              + "   margin %.3f" % entry["symbol"]["margin"])
        print("   native px: digit_h=%d sym %dx%d dy_top=%d dy_bot=%d"
              % (G[i]["h1"], G[i]["sw"], G[i]["sh"], G[i]["dy_top"], G[i]["dy_bot"]))
    report["contested"] = {str(k): v for k, v in adj.items()}

    with open(os.path.join(HERE, "pixelmatch.json"), "w") as f:
        json.dump(report, f, indent=1)
    print("\nwrote pixelmatch.json")


if __name__ == "__main__":
    main()
