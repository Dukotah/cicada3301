"""Lane B1 - SKIP-AWARE arm.

PA-3's caveat I: any lane feeding never-fed artifact key material must run it under the
Campaign XVIII skip-tolerant beam, because the rigid additive model is the wrong model
under a soft anti-repeat rewrite (rigid misses a KNOWN planted key at -7.24; the beam
recovers it at -4.15). This arm reuses that decoder VERBATIM (no new solver) and feeds it
only the B1 artifact key set, which was never in any campaign18 corpus.

Positive control = keywords_skip.gate() (plants CIRCUMFERENCE under the ~83% doublet-skip
filter; rigid must miss, beam must recover). If the gate fails, the arm aborts.

Run:
  PYTHONUTF8=1 python3 analysis/round10b/B1-overlooked-artifact/b1_skip_arm.py --pages 12
"""
import argparse
import json
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
C18 = os.path.join(ROOT, "analysis", "campaign18_skip")
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, C18)
sys.path.insert(0, os.path.join(C18, "armada2"))
sys.path.insert(0, HERE)

import keywords_skip as KS                      # noqa  (the validated keyword arm)
from sweep import Q, N                          # noqa
from run_stats import load_pages                # noqa
from b1_keys import build                       # noqa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=12,
                    help="number of unsolved pages to sweep (scaled run)")
    ap.add_argument("--nogate", action="store_true")
    a = ap.parse_args()

    log = []

    def p(m):
        print(m, flush=True)
        log.append(str(m))

    if not a.nogate:
        p("--- POSITIVE CONTROL: campaign18 keyword skip-beam gate ---")
        g = KS.gate(verbose=True)
        ok, gstats = (g if isinstance(g, tuple) else (g, {}))
        payload_gate = gstats
        p(f"GATE: {'PASS' if ok else 'FAIL'}  {gstats}")
        if not ok:
            p("ABORT: skip-beam gate failed; no negative from this arm is trustworthy.")
            return
    else:
        ok = None

    alpha, _ = build()
    kws = []
    for r in alpha:
        try:
            ki = KS.eng_to_idx(r["key"])
        except Exception:
            continue
        if 3 <= len(ki) <= 14:   # the author's demonstrated key lengths (DIVINITY 8, FIRFUMFERENFE 13)
            kws.append((r["key"], ki))
    p(f"B1 artifact keywords into the skip beam: {len(kws)}")

    pages = load_pages()[:-2]
    sel = list(range(0, len(pages), max(1, len(pages) // a.pages)))[:a.pages]
    p(f"pages swept (scaled): {sel}")

    t0 = time.time()
    best_real = (-99.0, None)
    hits_real = []
    for pi in sel:
        ct = np.array(pages[pi], dtype=np.int64)
        h, bg = KS.attack_page_keyword_fast(ct, kws)
        if bg[0] > best_real[0]:
            best_real = (bg[0], (pi,) + tuple(bg[1]) if bg[1] else (pi,))
        hits_real += [(pi,) + tuple(x) for x in h]
        p(f"  p{pi:<3} best={bg[0]:.3f} key={bg[1][0] if bg[1] else '-'}  "
          f"({time.time()-t0:.0f}s)")
    p(f"REAL skip-beam best = {best_real[0]:.3f}  {best_real[1]}")
    p(f"REAL confirmed hits (> {KS.CONF_THR}) = {len(hits_real)}")

    # ---- NULL: same grid, per-page shuffled ciphertext ----
    rnd = random.Random(20260812)
    best_null = (-99.0, None)
    hits_null = []
    for pi in sel:
        q = list(pages[pi])
        rnd.shuffle(q)
        ct = np.array(q, dtype=np.int64)
        h, bg = KS.attack_page_keyword_fast(ct, kws)
        if bg[0] > best_null[0]:
            best_null = (bg[0], (pi,) + tuple(bg[1]) if bg[1] else (pi,))
        hits_null += [(pi,) + tuple(x) for x in h]
    p(f"NULL skip-beam best = {best_null[0]:.3f}  {best_null[1]}")
    p(f"NULL confirmed hits = {len(hits_null)}")
    p(f"DELTA (real - null) = {best_real[0]-best_null[0]:+.3f}   "
      f"[positive and > +0.5 would be signal; <= 0 is a clean negative]")

    out = {"gate": bool(ok), "gate_stats": {k: round(float(v),3) for k,v in (gstats or {}).items()}, "n_keywords": len(kws), "pages": sel,
           "real_best": best_real[0], "real_best_rec": str(best_real[1]),
           "null_best": best_null[0], "null_best_rec": str(best_null[1]),
           "real_hits": len(hits_real), "null_hits": len(hits_null),
           "conf_thr": KS.CONF_THR, "screen_thr": KS.SCREEN_THR}
    json.dump(out, open(os.path.join(HERE, "b1_skip_results.json"), "w"), indent=2)
    with open(os.path.join(HERE, "RUN-skip.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")


if __name__ == "__main__":
    main()
