"""R44 WAVE-2 / A3 — the positive-control GATE, run BEFORE the sweep (PREREG Q1/Q5).

Four keyskip1-filtered reset plants (PA page / PL line / PS section / PD deep-section),
enciphered through R44-R1's own `encipher_reset` and pushed through THIS cell's full-grid
task runner (identical code path as the real pages).  Writes gate_a3.json.
Any failure => INSTRUMENT-INCOMPLETE (run_sweep.py refuses to run).
"""
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a3lib as L                                # noqa: E402
from a3lib import R, A, free_bar                 # noqa: E402

sys.path.insert(0, os.path.join(L.LP, "src"))
from lp import gematria as gp                    # noqa: E402

sys.path.insert(0, L.R1)
import plant_gate as r1pg                        # noqa: E402  (PT1-3, the controls of record)


def to_idx(text):
    out = []
    for w in text.split():
        out.extend(gp.keyword_to_indices(w))
    return out


PLANTS = [
    # id, key, mode, offset, cfg, seg_lens, plaintext builder, seed, reset-bearing tid
    ("PA", "G-bash-3301", "page", 11, "beau_atb", [120, 120],
     lambda: (to_idx(r1pg.PT3) + to_idx(r1pg.PT1))[:240], 761, "PA_1"),
    ("PL", "P-totient", "line", 5, "vigp", [24] * 10,
     lambda: to_idx(r1pg.PT2)[:240], 1033, "PL_0"),
    ("PS", "G-bash-1325734783", "section", 3, "vigm", [360],
     lambda: (to_idx(r1pg.PT1) + to_idx(r1pg.PT2))[:360], 29, "PS_2"),
]


def build_plant_targets(keys):
    """Encipher the plants and lay them out as page/line/section targets (same structure
    as real_targets), so the identical run_task sweeps them."""
    tp, tl, ts, truth = [], [], [], {}
    for pid, kname, mode, o, cfg, segs, mk, seed, _ in PLANTS:
        P = mk()
        C = R.encipher_reset(P, keys[kname], cfg, segs, offset=o, keyskip=True,
                             supp=0.83, seed=seed)
        n_pages = (len(C) + 119) // 120
        group = []
        a = 0
        for t in range(n_pages):
            c = np.asarray(C[t * 120:(t + 1) * 120], dtype=np.int64)
            tid = "%s_%d" % (pid, t)
            truth[tid] = P[t * 120:(t + 1) * 120]
            tp.append((tid, c, free_bar(120)))
            tl.append((tid, c, [24] * 5, free_bar(120)))
            group.append((tid, a, a + len(c), free_bar(120)))
            a += len(c)
        ts.append((pid, np.asarray(C, dtype=np.int64), group))
        truth[pid + "_full"] = (P, C)
    return {"page": tp, "line": tl, "section": ts}, truth


def main():
    t0 = time.time()
    keys = L.init({"page": [], "line": [], "section": []})
    targets, truth = build_plant_targets(keys)
    L.TARGETS = targets

    tasks = [(m, k) for m in R.MODES for k in keys]
    # 2026-11-09 mp fix: fork after the parent's BLAS threads hung on py3.14 — use spawn
    # with a worker initializer that rebuilds PAN/KEYS and unpickles TARGETS per worker.
    results, last_hb = [], time.time()
    with mp.get_context("spawn").Pool(6, initializer=L.worker_init,
                                      initargs=(targets,)) as pool:
        for r in pool.imap_unordered(L.run_task, tasks):
            results.append(r)
            if time.time() - last_hb >= 300:
                L.heartbeat("plant_gate %d/%d tasks" % (len(results), len(tasks)))
                last_hb = time.time()
    # grid max per (tid): over all modes x keys x offsets x cfgs
    gridmax, n_cells = {}, 0
    for r in results:
        n_cells += r["n_cells"]
        for tid, b in r["best"].items():
            cur = gridmax.get(tid)
            if cur is None or b["pmax"] > cur["pmax"]:
                gridmax[tid] = dict(b, mode=r["mode"], key=r["key"])
                gridmax[tid].pop("dec", None)

    out = {"n_cells": n_cells, "bars": {"120": round(free_bar(120), 4),
                                        "240": round(free_bar(240), 4)},
           "controls": [], "passed": None}

    for pid, kname, mode, o, cfg, segs, mk, seed, bind_tid in PLANTS:
        P, C = truth[pid + "_full"]
        K = keys[kname]
        # the planted cell's own decode, exactly as the sweep applies it
        if mode == "page":
            t = int(bind_tid.split("_")[1])
            c = np.asarray(C[t * 120:(t + 1) * 120], dtype=np.int64)
            dec = R.beam_reset_decode(c, K, cfg, [len(c)], offset=o)
            pt = truth[bind_tid]
            rigid = R.beam_rigid_decode(np.asarray(C), K, cfg, offset=o)
            rig_rec = R.recovery(rigid[t * 120:(t + 1) * 120], pt)
            diff_name = "rigid (no reset) beam on the post-reset page"
        elif mode == "line":
            # check on the first 120-rune chunk, exactly as the grid's line target sees it
            c = np.asarray(C[:120], dtype=np.int64)
            dec = R.beam_reset_decode(c, K, cfg, [24] * 5, offset=o)
            pt = truth[bind_tid]
            rigid = R.beam_rigid_decode(c, K, cfg, offset=o)
            rig_rec = R.recovery(rigid, pt)
            diff_name = "rigid (no line resets) beam"
        else:
            t = int(bind_tid.split("_")[1])
            full_dec = R.beam_reset_decode(np.asarray(C), K, cfg, [len(C)], offset=o)
            dec = full_dec[t * 120:(t + 1) * 120]
            pt = truth[bind_tid]
            # differential: R1 tier-2's mid-section entry approximation (zero accumulated
            # rejections) on the same page -- the hole this cell repairs
            approx = R.beam_reset_decode(np.asarray(C[t * 120:(t + 1) * 120]), K, cfg,
                                         [120], offset=o + t * 120)
            rig_rec = R.recovery(approx, pt)
            diff_name = "R1-approx mid-section entry (zero-rejection assumption)"
        rec = R.recovery(dec, pt)
        full = A.adjudicate(np.asarray(dec, dtype=np.int64), pan=L.PAN)
        gm = gridmax[bind_tid]
        planted_is_max = bool(full["pmax"] >= gm["pmax"] - 1e-9)
        bar = free_bar(120)
        ctl = dict(name=pid, cell=dict(key=kname, mode=mode, offset=o, cfg=cfg,
                                       keyskip=True, supp=0.83, seed=seed),
                   bind_tid=bind_tid, recovery=round(float(rec), 4),
                   planted_pmax=round(float(full["pmax"]), 3),
                   planted_degenerate=bool(full["degenerate"]),
                   planted_is_grid_max=planted_is_max,
                   grid_max={k: gm[k] for k in ("pmax", "mode", "key", "offset", "cfg")},
                   bar=round(bar, 4), differential=diff_name,
                   differential_recovery=round(float(rig_rec), 4))
        ctl["passed"] = bool(rec >= 0.85 and planted_is_max and not full["degenerate"]
                             and full["pmax"] >= bar and rig_rec < 0.85)
        out["controls"].append(ctl)
        print(json.dumps(ctl), flush=True)

    # PD: deep-section depth control (depth measurement, not a grid-max test; PREREG)
    pts = (to_idx(r1pg.PT1) + to_idx(r1pg.PT2) + to_idx(r1pg.PT3))
    Pd = (pts * 5)[:3400]
    Cd = R.encipher_reset(Pd, keys["P-prime"], "vigm", [3400], offset=0, keyskip=True,
                          supp=0.83, seed=58)
    dd = R.beam_reset_decode(np.asarray(Cd), keys["P-prime"], "vigm", [3400], offset=0)
    tail_rec = R.recovery(dd[-120:], Pd[-120:])
    full_rec = R.recovery(dd, Pd)
    pd = dict(name="PD", cell=dict(key="P-prime", mode="section-depth-3400", offset=0,
                                   cfg="vigm", keyskip=True, supp=0.83, seed=58),
              tail120_recovery=round(float(tail_rec), 4),
              full_recovery=round(float(full_rec), 4),
              passed=bool(tail_rec >= 0.85))
    out["controls"].append(pd)
    print(json.dumps(pd), flush=True)

    out["passed"] = bool(all(c["passed"] for c in out["controls"]))
    out["verdict"] = "GATE-PASSED" if out["passed"] else "INSTRUMENT-INCOMPLETE"
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "gate_a3.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("n_cells", "passed", "verdict", "elapsed_s")}))


if __name__ == "__main__":
    main()
