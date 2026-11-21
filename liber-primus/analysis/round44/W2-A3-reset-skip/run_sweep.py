"""R44 WAVE-2 / A3 — the pre-registered FULL-grid reset+keyskip1 beam sweep over the 55
unsolved LP2 pages: 51 keys x 30 offsets x 6 configs x 3 reset modes = 1,514,700 beam cells.

Refuses to run unless BOTH this cell's gate_a3.json AND R44-R1's gate.json say passed
(the R1 gate.json discipline, carried).  Checkpoint at 10% of tasks (PREREG Q5): abort if
projected wall > 6 h.  Writes a3_results.json.  Pure python3 + numpy, no network.
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

CHECK_AT = 16                                    # ~10% of 153 tasks
MAX_WALL_H = 6.0


def main():
    t0 = time.time()
    gate = json.load(open(os.path.join(HERE, "gate_a3.json")))
    r1gate = json.load(open(os.path.join(L.R1, "gate.json")))
    if not (gate.get("passed") and r1gate.get("passed")):
        print("GATE NOT PASSED (a3: %s, r1: %s) — INSTRUMENT-INCOMPLETE; refusing to sweep."
              % (gate.get("passed"), r1gate.get("passed")))
        sys.exit(1)

    keys = L.init(None)
    L.TARGETS = L.real_targets()
    tasks = [(m, k) for m in R.MODES for k in keys]        # 153 tasks
    assert len(tasks) == 153

    out = {"n_keys": len(keys), "n_bar": R.N_BAR,
           "bars": {"120": round(free_bar(120), 4), "240": round(free_bar(240), 4)},
           "beam": {"beam_w": 200, "max_rej": 3}, "pages": {}, "crossers": [],
           "tasks": [], "verdict": None}

    best_pm = {}                                 # (tid, mode) -> best dict (with dec)
    n_cells, done = 0, 0
    aborted = False
    last_hb = time.time()
    # 2026-11-09 mp fix: spawn + worker initializer (py3.14 fork-after-threads hang)
    with mp.get_context("spawn").Pool(6, initializer=L.worker_init,
                                      initargs=(L.TARGETS,)) as pool:
        for r in pool.imap_unordered(L.run_task, tasks):
            done += 1
            n_cells += r["n_cells"]
            out["crossers"].extend(r["crossers"])
            out["tasks"].append(dict(mode=r["mode"], key=r["key"], n_cells=r["n_cells"],
                                     elapsed=r["elapsed"]))
            for tid, b in r["best"].items():
                k = (tid, r["mode"])
                if k not in best_pm or b["pmax"] > best_pm[k]["pmax"]:
                    best_pm[k] = dict(b, mode=r["mode"], key=r["key"])
            el = time.time() - t0
            if done % 10 == 0 or done == CHECK_AT:
                proj = el / done * len(tasks) / 3600
                print("task %d/153  cells %d  %.0fs  proj %.2fh" % (done, n_cells, el, proj),
                      flush=True)
            if time.time() - last_hb >= 300:
                L.heartbeat("run_sweep %d/153 tasks, %d cells, %.0fs elapsed"
                            % (done, n_cells, el))
                last_hb = time.time()
            if done == CHECK_AT and (time.time() - t0) / done * len(tasks) > MAX_WALL_H * 3600:
                print("CHECKPOINT ABORT: projected wall exceeds %.1fh (PREREG Q5)" % MAX_WALL_H)
                aborted = True
                pool.terminate()
                break

    # per (page, mode) best: full adjudicate for the language-agnostic stats (R3)
    gbest = {"pmax": -99.0}
    for (tid, mode), b in sorted(best_pm.items()):
        full = A.adjudicate(np.asarray(b["dec"], dtype=np.int64), pan=L.PAN)
        row = dict(page=tid, mode=mode, key=b["key"], offset=b["offset"], cfg=b["cfg"],
                   pmax=round(float(full["pmax"]), 3), preg=int(full["preg"]),
                   ioc=round(float(full["ioc"]), 4), mds=int(full["mds"]),
                   degenerate=bool(full["degenerate"]), L=b["L"], bar=b["bar"])
        out["pages"].setdefault(tid, []).append(row)
        if row["pmax"] > gbest["pmax"]:
            gbest = dict(row)

    out["n_cells"] = n_cells
    out["n_tasks_done"] = done
    out["aborted_at_checkpoint"] = aborted
    out["observed_global_best"] = gbest
    out["n_crossers"] = len(out["crossers"])
    out["verdict"] = ("PARTIAL-ABORT" if aborted else
                      ("NEGATIVE" if not out["crossers"]
                       else "CROSSER(S) — FLAGGED-FOR-ORACLE per HUMAN-ORACLE.md, not certified"))
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "a3_results.json"), "w"), indent=1)
    print(json.dumps({"n_cells": n_cells, "n_tasks_done": done,
                      "n_crossers": out["n_crossers"], "observed_global_best": gbest,
                      "verdict": out["verdict"], "bars": out["bars"],
                      "elapsed_s": out["elapsed_s"]}, indent=1))


if __name__ == "__main__":
    main()
