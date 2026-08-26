"""Round 19 / C1 -- the control L5 could not run: the SINGLE-TEMPLATE regime.

Why this exists. L5's leave-one-out control (pixelmatch.py Control 2) cannot test the five
classes that have exactly one uncontested exemplar in the payload -- I, R, h, i, l -- because
removing the exemplar removes the class. But `I`, `i` and `l` are precisely the classes that
decide 8 of the 11 conflict cells, including four of the six pre-registered ones. The licence
L5 claims for those cells is therefore an extrapolation from classes that had 2-7 exemplars.

This script measures the extrapolation instead of assuming it.

  CONTROL 3 -- single-template regime. Reduce EVERY class to exactly one exemplar (the
    lowest-index uncontested cell of that class) and classify every remaining uncontested cell
    by nearest single template. That is the exact regime I/i/l are used in, run on cells whose
    identity is known. Pre-registered bar (C1/PREREG.md 2.1): >= 99% overall AND 100% on the
    case-ambiguous subset.

  CONTROL 4 -- global class separation. Full all-pairs best-alignment IoU over the segmented
    uncontested cells: min_within vs max_between, over ALL classes rather than L5's ambiguous
    subset only. Pre-registered bar (2.2): the rule "IoU >= 0.995 => same class" is licensed
    iff max_between < 0.995 <= min_within on correctly-segmented pairs.

  PART 3 -- re-derive every physical discriminator L5 RESULTS 2.2 asserts, from the images.

    python3 singletons.py
"""
import json
import os

import numpy as np

import grid
import glyphmatch as gm
import pixelmatch as pm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CANON = os.path.join(ROOT, "liber-primus", "analysis", "pp49_51", "canon_256.bin")
ALPHA = pm.ALPHA
CONFLICT = pm.CONFLICT
CONTESTED = pm.CONTESTED
AMBIG = pm.AMBIG_CLASSES
# a cell is called MIS-SEGMENTED, independently of any adjudication, if its trailing-symbol
# bitmap agrees with no other exemplar of its own canon class above this IoU. On a
# deterministic render the within-class floor is ~0.995, so 0.5 is far below any real glyph
# and only catches extraction failures.
SEG_FAIL = 0.5


def main():
    canon = open(CANON, "rb").read()
    G = pm.extract()
    unseg = sorted(i for i, v in G.items() if v is None)
    unc = [i for i in range(256) if i not in CONFLICT and G[i] is not None]
    sym_of = {i: ALPHA[canon[i] % 60] for i in unc}
    dig_of = {i: str(canon[i] // 60) for i in unc}
    byclass, bydigit = {}, {}
    for i in unc:
        byclass.setdefault(sym_of[i], []).append(i)
        bydigit.setdefault(dig_of[i], []).append(i)
    for d in byclass.values():
        d.sort()

    rep = {"cells_not_segmented": unseg,
           "n_uncontested_segmented": len(unc),
           "n_symbol_classes": len(byclass),
           "singleton_classes": sorted(s for s, v in byclass.items() if len(v) == 1),
           "singleton_exemplars": {s: v[0] for s, v in sorted(byclass.items()) if len(v) == 1}}
    print("uncontested segmented cells: %d   symbol classes: %d" % (len(unc), len(byclass)))
    print("singleton classes (n=1): %s" % rep["singleton_exemplars"])
    print("cells that did not segment into 2 glyphs: %s" % unseg)

    # ---------------- CONTROL 4 first: all-pairs separation --------------------
    print("\n" + "=" * 74)
    print("CONTROL 4 -- global all-pairs separation (every uncontested segmented cell)")
    print("=" * 74)
    n = len(unc)
    M = np.zeros((n, n))
    for a in range(n):
        for b in range(a + 1, n):
            v = pm.best_iou(G[unc[a]]["s"], G[unc[b]]["s"])
            M[a, b] = M[b, a] = v
    # objective segmentation-failure detector: no same-class partner above SEG_FAIL
    misseg = []
    for a in range(n):
        same = [b for b in range(n) if b != a and sym_of[unc[b]] == sym_of[unc[a]]]
        if same and max(M[a, b] for b in same) < SEG_FAIL:
            misseg.append(unc[a])
    print("mis-segmented cells detected objectively (best same-class IoU < %.2f): %s"
          % (SEG_FAIL, misseg))

    def sep(exclude):
        wmin, wmin_pair, bmax, bmax_pair = 1.0, None, 0.0, None
        for a in range(n):
            if unc[a] in exclude:
                continue
            for b in range(a + 1, n):
                if unc[b] in exclude:
                    continue
                v = M[a, b]
                if sym_of[unc[a]] == sym_of[unc[b]]:
                    if v < wmin:
                        wmin, wmin_pair = v, (unc[a], unc[b], sym_of[unc[a]])
                else:
                    if v > bmax:
                        bmax, bmax_pair = v, (unc[a], unc[b],
                                              sym_of[unc[a]] + "/" + sym_of[unc[b]])
        return wmin, wmin_pair, bmax, bmax_pair

    w0, wp0, b0, bp0 = sep(set())
    w1, wp1, b1, bp1 = sep(set(misseg))
    print("  ALL pairs           : min_within=%.4f %s   max_between=%.4f %s"
          % (w0, wp0, b0, bp0))
    print("  excluding mis-seg   : min_within=%.4f %s   max_between=%.4f %s"
          % (w1, wp1, b1, bp1))
    licensed = (b1 < 0.995 <= w1)
    print("  pre-registered rule 'IoU >= 0.995 => same class' LICENSED: %s "
          "(needs max_between < 0.995 <= min_within)" % licensed)
    rep["control4"] = {
        "all_pairs": {"min_within": round(w0, 4), "min_within_pair": wp0,
                      "max_between": round(b0, 4), "max_between_pair": bp0},
        "excluding_missegmented": {"min_within": round(w1, 4), "min_within_pair": wp1,
                                   "max_between": round(b1, 4), "max_between_pair": bp1},
        "missegmented_cells": misseg,
        "threshold_T": 0.995,
        "licensed": bool(licensed),
        "n_pairs": n * (n - 1) // 2,
    }

    # ---------------- CONTROL 3: single-template regime ------------------------
    print("\n" + "=" * 74)
    print("CONTROL 3 -- single-template regime (every class reduced to ONE exemplar)")
    print("=" * 74)
    rep["control3"] = {}
    for what, table, truth, key in (("symbol", byclass, sym_of, "s"),
                                    ("digit", bydigit, dig_of, "d")):
        tmpl = {c: sorted(v)[0] for c, v in table.items()}
        ok = tot = aok = atot = 0
        misses = []
        for i in unc:
            if tmpl[truth[i]] == i:          # this cell IS the template; nothing to test
                continue
            sc = sorted(((pm.best_iou(G[i][key], G[tmpl[c]][key]), c) for c in tmpl),
                        reverse=True)
            hit = sc[0][1] == truth[i]
            ok += hit
            tot += 1
            if truth[i] in AMBIG:
                atot += 1
                aok += hit
            if not hit:
                misses.append({"idx": i, "true": truth[i], "got": sc[0][1],
                               "iou": round(sc[0][0], 4),
                               "true_class_iou": round(
                                   [v for v, c in sc if c == truth[i]][0], 4)})
        acc = ok / tot if tot else float("nan")
        aacc = aok / atot if atot else float("nan")
        print("  %-6s: %d/%d = %.2f%%   case-ambiguous %d/%d = %.2f%%"
              % (what, ok, tot, 100 * acc, aok, atot, 100 * aacc))
        if misses:
            print("    misses: %s" % misses)
        rep["control3"][what] = {
            "templates": {c: tmpl[c] for c in sorted(tmpl)},
            "correct": ok, "n": tot, "accuracy": acc,
            "ambiguous_correct": aok, "ambiguous_n": atot, "ambiguous_accuracy": aacc,
            "misses": misses,
        }
    s3 = rep["control3"]["symbol"]
    gate3 = (s3["accuracy"] >= 0.99) and (s3["ambiguous_accuracy"] == 1.0)
    rep["control3"]["gate_threshold"] = ">=99% overall AND 100% case-ambiguous (symbol)"
    rep["control3"]["gate"] = "PASS" if gate3 else "FAIL"
    print("  pre-registered Control-3 gate (symbol >=99%% overall AND 100%% ambiguous): %s"
          % rep["control3"]["gate"])

    # ---------------- PART 3: physical discriminators --------------------------
    print("\n" + "=" * 74)
    print("PART 3 -- physical discriminators, re-measured from the images")
    print("=" * 74)
    ims = gm._pages()
    with open(os.path.join(HERE, "grid.json")) as f:
        gj = json.load(f)
    met = {}
    for i in range(256):
        page, j = grid.idx_to_cell(i)
        m = gm.cell_metrics(ims[page], gj[page][j])
        met[i] = m
    phys = {}
    for c in sorted(byclass):
        idxs = byclass[c]
        vals = {k: [met[i][k] for i in idxs if met[i]] for k in
                ("hrel", "toprel", "botrel", "wrel")}
        phys[c] = {"n": len(idxs), "exemplars": idxs,
                   **{k: [round(float(np.mean(v)), 4), round(float(np.std(v)), 4)]
                      for k, v in vals.items()},
                   "native_px": [{"idx": i, "sym_w": int(G[i]["sw"]), "sym_h": int(G[i]["sh"]),
                                  "dy_top": int(G[i]["dy_top"]), "digit_h": int(G[i]["h1"])}
                                 for i in idxs[:3] if G[i]]}
    rep["class_physical"] = phys
    for c in ("I", "l", "L", "i", "1", "W", "w", "O", "0", "Q"):
        if c not in phys:
            print("  class %r: NOT PRESENT among uncontested cells" % c)
            continue
        p = phys[c]
        px = p["native_px"][0] if p["native_px"] else {}
        print("  %-2r n=%d  hrel=%.3f toprel=%+.3f wrel=%.3f   native %sx%s dy_top=%s "
              "(digit_h=%s, idx %s)"
              % (c, p["n"], p["hrel"][0], p["toprel"][0], p["wrel"][0],
                 px.get("sym_w"), px.get("sym_h"), px.get("dy_top"), px.get("digit_h"),
                 px.get("idx")))
    print("\n  contested cells, same measurements:")
    rep["conflict_physical"] = {}
    for i in CONFLICT:
        if not met[i]:
            continue
        rep["conflict_physical"][str(i)] = {
            k: round(met[i][k], 4) for k in ("hrel", "toprel", "botrel", "wrel")}
        rep["conflict_physical"][str(i)]["native_px"] = {
            "sym_w": int(G[i]["sw"]), "sym_h": int(G[i]["sh"]),
            "dy_top": int(G[i]["dy_top"]), "digit_h": int(G[i]["h1"])}
        print("  idx %3d  hrel=%.3f toprel=%+.3f wrel=%.3f   native %dx%d dy_top=%d"
              % (i, met[i]["hrel"], met[i]["toprel"], met[i]["wrel"],
                 G[i]["sw"], G[i]["sh"], G[i]["dy_top"]))

    with open(os.path.join(HERE, "out_singletons.json"), "w") as f:
        json.dump(rep, f, indent=1)
    print("\nwrote out_singletons.json")


if __name__ == "__main__":
    main()
