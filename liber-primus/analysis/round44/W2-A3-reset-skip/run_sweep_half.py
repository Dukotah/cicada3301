"""R44 WAVE-2 / A3 — the PREREG-addendum (2026-11-11) PRIOR-RANKED HALF sweep.

The full 1,514,700-cell grid projected to ~7.3 h at the 10% checkpoint (page-mode arms cost
~191 s/task, not the Q3-estimated ~0.8 s); run_sweep.py fired PARTIAL-ABORT per PREREG Q5 and
its partial is saved as a3_results_partial_abort.json.  This runner executes the pre-registered
contingency: the first 26 of the 51 keys in the PREREG prior order (FAM-P then FAM-G seedprior20
order), ALL 3 reset modes x 30 offsets x 6 configs = 757,350 cells (exactly half the grid).

NO threshold / bar / key-def / beam param / adjudicator / recognizer is changed from PREREG —
only the key count is halved and the uncovered half is declared in coverage.  Same gate
discipline (refuses unless gate_a3.json AND R1 gate.json passed), same heartbeat, same crosser
handling.  Writes a3_results.json.  Pure python3 + numpy, no network.
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

HALF_N = 26                                      # ceil(51/2), prior-ranked


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
    all_keys = list(keys.keys())                 # PREREG prior order (build_keys order)
    half_keys = all_keys[:HALF_N]
    not_covered_keys = all_keys[HALF_N:]
    tasks = [(m, k) for m in R.MODES for k in half_keys]    # 3 x 26 = 78 tasks
    assert len(tasks) == 3 * HALF_N

    out = {"split": "prior-ranked-half (PREREG addendum 2026-11-11)",
           "n_keys_swept": len(half_keys), "n_keys_total": len(all_keys),
           "keys_swept": half_keys, "keys_not_covered": not_covered_keys,
           "n_bar": R.N_BAR,
           "bars": {"120": round(free_bar(120), 4), "240": round(free_bar(240), 4)},
           "beam": {"beam_w": 200, "max_rej": 3}, "pages": {}, "crossers": [],
           "tasks": [], "verdict": None}

    best_pm = {}                                 # (tid, mode) -> best dict (with dec)
    n_cells, done = 0, 0
    last_hb = time.time()
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
            if done % 10 == 0:
                proj = el / done * len(tasks) / 3600
                print("task %d/%d  cells %d  %.0fs  proj %.2fh"
                      % (done, len(tasks), n_cells, el, proj), flush=True)
            if time.time() - last_hb >= 300:
                L.heartbeat("run_sweep_half %d/%d tasks, %d cells, %.0fs elapsed"
                            % (done, len(tasks), n_cells, el))
                last_hb = time.time()

    # per (page, mode) best: full adjudicate for the language-agnostic stats (doctrine R3)
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
    out["aborted_at_checkpoint"] = False
    out["observed_global_best"] = gbest
    out["n_crossers"] = len(out["crossers"])
    out["verdict"] = ("NEGATIVE (prior-ranked half; uncovered half declared)"
                      if not out["crossers"]
                      else "CROSSER(S) — FLAGGED-FOR-ORACLE per HUMAN-ORACLE.md, not certified")
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "a3_results.json"), "w"), indent=1)
    print(json.dumps({"n_cells": n_cells, "n_tasks_done": done, "n_keys_swept": len(half_keys),
                      "n_crossers": out["n_crossers"], "observed_global_best": gbest,
                      "verdict": out["verdict"], "bars": out["bars"],
                      "elapsed_s": out["elapsed_s"]}, indent=1))


if __name__ == "__main__":
    main()
