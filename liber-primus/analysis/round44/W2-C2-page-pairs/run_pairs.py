"""R44/W2-C2 pair lane — all 55x54 directed page pairs, page_i as key over page_j.

Refuses to run unless both plant files passed (PREREG Q5). (27,54) and (54,27) run FIRST
and are reported individually. Sanity checkpoint per PREREG Q5(iii). Writes pair_results.json.
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
    for f, key in (("plant_pair.json", "passed"), ("plant_canon.json", "passed")):
        p = os.path.join(HERE, f)
        if not (os.path.exists(p) and json.load(open(p)).get(key)):
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

    cts = [np.asarray(pg["idx"], dtype=np.int64) for pg in pages[:55]]
    keys_f = cts
    keys_r = [k[::-1].copy() for k in cts]
    offsets = [C.key_offsets(pg) for pg in pages[:55]]

    order = [(27, 54), (54, 27)] + [(i, j) for i in range(55) for j in range(55)
                                    if i != j and (i, j) not in ((27, 54), (54, 27))]
    best = C.Best(k=100)
    n_skipped = 0
    seven = {}
    checked = False
    for np_done, (i, j) in enumerate(order):
        tag = "key=%d|ct=%d" % (i, j)
        n_before = best.n
        C.scan_ct_against_key(cts[j], keys_f[i], keys_r[i], offsets[i], best, tag=tag)
        # count skipped cells (offsets dropped by the L >= MIN_L rule)
        full = len(offsets[i]) * 2 * 9
        n_skipped += full - (best.n - n_before)
        if (i, j) in ((27, 54), (54, 27)):
            fam = {k: dict(v) if isinstance(v, dict) else v
                   for k, v in best.summary()["families"].items()}
            seven[tag] = dict(best_rows=[dict(pmax=v, meta=m) for v, m, _ in
                                         sorted(best.rows, key=lambda r: -r[0])[:5]
                                         if m["tag"] == tag])
        # PREREG Q5(iii): sanity checkpoint after the 7-gram pairs + first 5 key pages
        if not checked and np_done >= 2 + 5 * 54:
            pms = np.array([v for v, m, _ in best.rows])
            med_top = float(np.median(pms))
            # the TOP-100 median must itself be sane; a constant stream or absurd values trip it
            if not (-3.0 <= med_top <= 16.8) or len(set(pms.round(6))) <= 1:
                print("SANITY CHECKPOINT FAILED: top-row median %.3f" % med_top)
                sys.exit(3)
            checked = True
            print("sanity checkpoint ok (top-100 median %.3f) at pair %d" % (med_top, np_done))

    rows = C.full_rows(best)
    out = dict(
        lane="pairs", n_cells=best.n, n_skipped_short=n_skipped,
        bars=C.BARS, n_bar=C.N_BAR, min_L=C.MIN_L,
        summary=best.summary(),
        sevengram_pairs=seven,
        n_crossers=len(best.crossers),
        crossers=[dict(pmax=v, meta=m) for v, m, _ in best.crossers],
        top_rows_full=rows[:100],
        runtime_s=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(HERE, "pair_results.json"), "w"), indent=1)
    nd = [r for r in rows if not r["degenerate"]]
    print("pair lane: %d cells (%d short-skipped), best non-degenerate pmax %.3f vs bar %.3f,"
          " crossers %d, %.1fs" % (best.n, n_skipped,
                                   nd[0]["pmax"] if nd else float("nan"),
                                   nd[0]["bar"] if nd else float("nan"),
                                   len(best.crossers), time.time() - t0))


if __name__ == "__main__":
    main()
