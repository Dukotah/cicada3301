"""R44/W2-C2 canon lane — the full 13,136-rune canon stream as running key over each of the
55 unsolved pages at ALL offsets, 3 relations x 3 shifts, fwd only (PREREG section 3).

Self-overlap cells (key window intersects the ct page's own canon interval) are computed but
reported separately and excluded from the verdict family. Gated on the plants.
Writes canon_results.json.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import c2lib as C                                     # noqa: E402


def gate():
    for f in ("plant_pair.json", "plant_canon.json"):
        p = os.path.join(HERE, f)
        if not (os.path.exists(p) and json.load(open(p)).get("passed")):
            print("GATE NOT PASSED (%s) — refusing to run (PREREG Q5)." % f)
            sys.exit(1)


def main():
    gate()
    t0 = time.time()
    pages = C.canon_pages()
    ok, facts = C.verify_premise(pages)
    if not ok:
        print("PREMISE RE-VERIFICATION FAILED:", facts)
        sys.exit(2)

    canon = np.asarray([i for pg in pages for i in pg["idx"]], dtype=np.int64)
    lens = [len(pg["idx"]) for pg in pages]
    starts = [sum(lens[:k]) for k in range(57)]

    best = C.Best(k=100)
    best_ov = C.Best(k=20)
    n = n_ov = 0
    for j in range(55):
        ct = np.asarray(pages[j]["idx"], dtype=np.int64)
        a, b = C.scan_ct_against_canon(ct, canon, best, best_ov,
                                       (starts[j], starts[j] + lens[j]),
                                       tag="canon|ct=%d" % j)
        n += a
        n_ov += b
        if j == 4:   # PREREG Q5(iii) sanity checkpoint ~10% in
            pms = np.array([v for v, m, _ in best.rows])
            med_top = float(np.median(pms))
            if not (-3.0 <= med_top <= 16.8) or len(set(pms.round(6))) <= 1:
                print("SANITY CHECKPOINT FAILED: top-row median %.3f" % med_top)
                sys.exit(3)
            print("sanity checkpoint ok (top-100 median %.3f) after page 4" % med_top)

    rows = C.full_rows(best)
    rows_ov = C.full_rows(best_ov)
    out = dict(
        lane="canon", n_cells=n, n_self_overlap_cells=n_ov,
        bars=C.BARS, n_bar=C.N_BAR,
        summary=best.summary(), summary_self_overlap=best_ov.summary(),
        n_crossers=len(best.crossers),
        crossers=[dict(pmax=v, meta=m) for v, m, _ in best.crossers],
        self_overlap_crossers=[dict(pmax=v, meta=m) for v, m, _ in best_ov.crossers],
        top_rows_full=rows[:100], top_self_overlap_rows_full=rows_ov[:20],
        runtime_s=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(HERE, "canon_results.json"), "w"), indent=1)
    nd = [r for r in rows if not r["degenerate"]]
    print("canon lane: %d cells (+%d self-overlap), best non-degenerate pmax %.3f vs bar %.3f,"
          " crossers %d, %.1fs" % (n, n_ov, nd[0]["pmax"] if nd else float("nan"),
                                   nd[0]["bar"] if nd else float("nan"),
                                   len(best.crossers), time.time() - t0))


if __name__ == "__main__":
    main()
