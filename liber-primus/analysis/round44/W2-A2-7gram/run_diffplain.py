"""R44/W2-A2 part 1 — different-plaintext constraint enumeration (PREREG section 4).
Refuses to run unless both plants passed.  Writes diffplain.json."""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a2lib as L                                     # noqa: E402

N = L.N


def gate():
    for f in ("plant_solver.json", "plant_crib.json"):
        if not json.load(open(os.path.join(HERE, f))).get("passed"):
            print("GATE NOT PASSED (%s) — refusing to run (PREREG Q5)." % f)
            sys.exit(1)


def headmask(heads):
    m = np.zeros(N, dtype=np.int64)
    for h in heads:
        m[h] = 1
    return m


def random_vocab(rng, nv3, nh):
    v3 = set()
    while len(v3) < nv3:
        v3.add(tuple(int(x) for x in rng.integers(0, N, 3)))
    heads = set(int(x) for x in rng.choice(N, size=nh, replace=False))
    return v3, heads


def main():
    gate()
    t0 = time.time()
    v3, heads = L.build_vocab()
    nv3, nh = len(v3), len(heads)
    out = {"V3": nv3, "H": nh, "heads": sorted(int(h) for h in heads)}

    # --- real constant/AP scan --------------------------------------------
    tab7, tab6, const_pairs = L.ap_scan(v3, heads)
    const_row = tab7[:, 0]
    out["constant"] = {
        "satisfiable_shifts": [int(s) for s in range(N) if const_row[s] > 0],
        "pairs_per_shift": {str(s): int(const_row[s]) for s in range(N) if const_row[s] > 0},
        "total_pairs": int(const_row.sum()),
        "explicit_pairs": const_pairs,
    }
    ap_mask = tab7.copy()
    ap_mask[:, 0] = 0                                  # b=0 reported as constant
    out["AP"] = {"cells_satisfiable": int((ap_mask > 0).sum()), "cells": 29 * 28,
                 "total_pairs": int(ap_mask.sum()), "max_cell": int(ap_mask.max()),
                 "head_free_cells_satisfiable": int((tab6[:, 1:] > 0).sum())}

    # --- real generator scan ----------------------------------------------
    keys = L.build_keys()
    g3, _ = L.g3_table(v3)
    hm = headmask(heads)
    gen = {}
    anchored = []
    for kname, K in keys.items():
        r = L.gen_scan_key(np.asarray(K, dtype=np.int64), g3, hm, nv3)
        gen[kname] = r
        for tag in ("diag_section", "diag_global"):
            if r[tag]["sat7"] > 0:
                anchored.append(dict(key=kname, diag=tag, sat7=r[tag]["sat7"],
                                     max7=r[tag]["max7"], argmax_o=r[tag]["argmax7"]))
    grid_sat = {k: gen[k]["grid"]["sat7"] for k in gen}
    out["generator"] = {
        "grid_cells_per_key": gen[next(iter(gen))]["grid"]["cells"],
        "grid_sat7_fraction_mean": float(np.mean([v / gen[k]["grid"]["cells"]
                                                  for k, v in grid_sat.items()])),
        "diag_section_sat7_total": int(sum(gen[k]["diag_section"]["sat7"] for k in gen)),
        "diag_global_sat7_total": int(sum(gen[k]["diag_global"]["sat7"] for k in gen)),
        "anchored_diag_cells": anchored,
        "per_key": {k: {t: gen[k][t] for t in gen[k]} for k in gen},
    }

    # --- null of record ----------------------------------------------------
    rng = np.random.default_rng(3301)
    cn, apn = [], []
    for _ in range(200):
        rv3, rh = random_vocab(rng, nv3, nh)
        t7, _t6, _ = L.ap_scan(rv3, rh, list_pairs=False)
        cn.append(int(t7[:, 0].sum()))
        m = t7.copy()
        m[:, 0] = 0
        apn.append(int((m > 0).sum()))
    out["null_constant_pairs"] = dict(mean=float(np.mean(cn)), sd=float(np.std(cn)),
                                      min=int(np.min(cn)), max=int(np.max(cn)))
    out["null_AP_cells"] = dict(mean=float(np.mean(apn)), sd=float(np.std(apn)),
                                min=int(np.min(apn)), max=int(np.max(apn)))
    gs, ds, dg = [], [], []
    for _ in range(20):
        rv3, rh = random_vocab(rng, nv3, nh)
        rg3, _ = L.g3_table(rv3)
        rhm = headmask(rh)
        tots = [0, 0, 0]
        for kname, K in keys.items():
            r = L.gen_scan_key(np.asarray(K, dtype=np.int64), rg3, rhm, nv3)
            tots[0] += r["grid"]["sat7"]
            tots[1] += r["diag_section"]["sat7"]
            tots[2] += r["diag_global"]["sat7"]
        gs.append(tots[0] / (51 * gen[next(iter(gen))]["grid"]["cells"]))
        ds.append(tots[1])
        dg.append(tots[2])
    out["null_generator"] = dict(
        grid_sat7_fraction=dict(mean=float(np.mean(gs)), sd=float(np.std(gs))),
        diag_section_sat7_total=dict(mean=float(np.mean(ds)), sd=float(np.std(ds))),
        diag_global_sat7_total=dict(mean=float(np.mean(dg)), sd=float(np.std(dg))))

    out["wall_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "diffplain.json"), "w"), indent=1)
    brief = {k: out[k] for k in ("V3", "H", "constant", "AP", "null_constant_pairs",
                                 "null_AP_cells", "null_generator", "wall_s")}
    brief["constant"] = {kk: vv for kk, vv in brief["constant"].items()
                         if kk != "explicit_pairs"}
    brief["generator_summary"] = {k: out["generator"][k] for k in out["generator"]
                                  if k != "per_key"}
    print(json.dumps(brief, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
