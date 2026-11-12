"""R44/R1 — the pre-registered reset sweep over the 55 unsolved LP2 pages (tier 1 + tier 2).

Refuses to run unless gate.json says GATE-PASSED (PREREG Q5).  Includes an anchor-function
self-test (a synthetic key constructed to satisfy the 7-gram constraint must be found).
Writes r1_results.json.  Pure python3 + numpy, no network.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import resets as R                               # noqa: E402

LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))
sys.path.insert(0, os.path.join(LP, "analysis", "round34", "I1-v3-null"))
sys.path.insert(0, os.path.join(LP, "analysis"))
import adjudicate as A                           # noqa: E402
import bars_v3 as B                              # noqa: E402
from run_stats import load_pages                 # noqa: E402  (canon loader of record)

PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
FREE_LS = (120, 240, 400, 729)
TOP_M = 20                                       # tier-2 beam on top-20 cells + all crossers


def free_bar(L):
    cand = [x for x in FREE_LS if x <= L] or [120]
    return B.bar_v3(R.N_BAR, max(cand), "free")


def anchor_selftest():
    """A synthetic key that satisfies the 7-gram constraint at o=5 (page & section modes)
    must be found by anchor_offsets; FAM-P/G keys at those positions must not be mangled."""
    rng = np.random.RandomState(1033)
    K = rng.randint(0, 29, R.KEY_LEN).astype(np.int64)
    o = 35                                        # outside the base range -> must be an extra
    for j in range(7):
        K[o + 70 + j] = K[o + 28 + j]
    K[o + 0] = K[o + 34]                          # page-mode crossing condition
    ex_p, _ = R.anchor_offsets(K, "page")
    ex_s, _ = R.anchor_offsets(K, "section")
    assert o in ex_p and o in ex_s, (ex_p, ex_s)
    ex_l, fl = R.anchor_offsets(K, "line")
    assert ex_l == [] and not any(fl)
    return True


def main():
    t0 = time.time()
    gate = json.load(open(os.path.join(HERE, "gate.json")))
    if not gate.get("passed"):
        print("GATE NOT PASSED — INSTRUMENT-INCOMPLETE; refusing to sweep (PREREG Q5).")
        sys.exit(1)
    assert anchor_selftest()

    pages_meta = R.parse_pages()
    pages = load_pages()[:-2]
    assert len(pages) == 55
    for pi in range(55):                          # the lane's parse must equal the loader of record
        assert list(pages[pi]) == pages_meta[pi]["idx"], pi
    phases = R.phase_vectors(pages_meta)

    keys = R.build_keys()
    anchors = {m: {k: R.anchor_offsets(K, m) for k, K in keys.items()} for m in R.MODES}
    n_anchored = {m: {k: len(v[0]) for k, v in anchors[m].items() if v[0]} for m in R.MODES}
    anchor_flags_any = any(any(v[1]) for m in R.MODES for v in anchors[m].values())

    out = {"n_keys": len(keys), "n_bar": R.N_BAR,
           "bars": {"120": round(free_bar(120), 4), "240": round(free_bar(240), 4)},
           "anchored_extras_by_mode": n_anchored,
           "anchor_holds_at_any_base_offset": bool(anchor_flags_any),
           "pages": [], "crossers": [], "tier2": [], "verdict": None}

    total = 0
    gbest = {"pmax": -99.0}
    allbest = []
    for pi, c in enumerate(pages):
        bar = free_bar(len(c))
        cnt, best, cross = R.tier1_sweep_page(np.asarray(c, dtype=np.int64), phases[pi],
                                              keys, anchors, bar, A, PAN)
        total += cnt
        best["page"] = pi
        out["pages"].append(best)
        allbest.append(dict(best))
        for x in cross:
            x["page"] = pi
        out["crossers"].extend(cross)
        if best["pmax"] > gbest["pmax"]:
            gbest = dict(best)
        if pi % 10 == 0:
            print("page %d/55  cells %d  gbest %.3f (p%s %s/%s o%s %s)  %.0fs"
                  % (pi, total, gbest["pmax"], gbest.get("page"), gbest.get("key"),
                     gbest.get("mode"), gbest.get("offset"), gbest.get("cfg"),
                     time.time() - t0), flush=True)

    out["n_cells_tier1"] = total
    out["observed_global_best"] = gbest
    out["n_crossers"] = len(out["crossers"])

    # ---------------- tier 2: reset-aware keyskip1 beam on top-20 cells + all crossers
    cand = sorted(allbest, key=lambda b: -b["pmax"])[:TOP_M]
    cand += [dict(x) for x in out["crossers"]]
    for b in cand:
        pi = b["page"]
        c = pages[pi]
        mode = b["mode"]
        lo = pages_meta[pi]["line_of"]
        if mode == "page":
            segs = [len(c)]
        elif mode == "line":
            segs, cur, n = [], lo[0], 0
            for x in lo:
                if x != cur:
                    segs.append(n)
                    n, cur = 0, x
                n += 1
            segs.append(n)
        else:                                     # section: the page is mid-section; the key
            segs = [len(c)]                       # pointer enters at offset + section base
        off = b["offset"] + (int(phases[pi]["section"][0]) if mode == "section" else 0)
        dec = R.beam_reset_decode(np.asarray(c), keys[b["key"]], b["cfg"], segs, offset=off)
        full = A.adjudicate(np.asarray(dec, dtype=np.int64), pan=PAN)
        bar = free_bar(len(c))
        out["tier2"].append(dict(page=pi, key=b["key"], mode=mode, offset=b["offset"],
                                 cfg=b["cfg"], tier1_pmax=round(b["pmax"], 3),
                                 beam_pmax=round(float(full["pmax"]), 3),
                                 degenerate=bool(full["degenerate"]),
                                 bar=round(float(bar), 4),
                                 crosses=bool(full["pmax"] >= bar and not full["degenerate"])))
    out["n_cells_tier2"] = len(cand)
    t2cross = [x for x in out["tier2"] if x["crosses"]]

    out["verdict"] = ("NEGATIVE" if not out["crossers"] and not t2cross
                      else "CROSSER(S) — FLAGGED-FOR-ORACLE per HUMAN-ORACLE.md, not certified")
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "r1_results.json"), "w"), indent=1)
    best_t2 = max((x["beam_pmax"] for x in out["tier2"]), default=None)
    print(json.dumps({"n_cells_tier1": total, "n_crossers": out["n_crossers"],
                      "observed_global_best": gbest, "best_tier2_pmax": best_t2,
                      "anchored_extras_by_mode": n_anchored,
                      "anchor_holds_at_any_base_offset": anchor_flags_any,
                      "verdict": out["verdict"], "bars": out["bars"],
                      "elapsed_s": out["elapsed_s"]}, indent=1))


if __name__ == "__main__":
    main()
