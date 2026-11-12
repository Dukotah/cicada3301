"""R44 W2-C7 — the real sweep: both batteries over the 55 unsolved pages.

Refuses to run unless results/plants.json exists with gate == "passed" (PREREG Q5).
Persists doctrine-R3 statistics (full adjudicate SWEEPROW fields) for every page-best row.

RESTART HARNESS (2026-11-10, after the X1-audited mid-run death at page 12/55):
the original driver kept all per-page rows in memory and wrote sweep_*.json only at
battery end, so the death lost every R3 row; the sweep is RESTARTED from page 0 (pages
independent, reductions deterministic).  This driver adds — with ZERO analytic change
(c7lib.py / reduce.py untouched, same calls, same bars, same space):
  * per-page checkpointing to results/progress_{S,P}.jsonl (skip-completed on start)
  * a 10-min heartbeat thread appending to run.log (X1 dead-man rule)
  * --max-seconds time slices (exit rc=3 = more pages remain) for foreground driving
"""
import argparse
import datetime
import json
import os
import sys
import threading
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c7lib as C                                   # noqa: E402
import reduce as R                                  # noqa: E402

RES = os.path.join(C.CELL, "results")
LOG = os.path.join(C.CELL, "run.log")

_hb_state = {"msg": "starting"}


def ts():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(line, stamp=False):
    s = ("%s %s" % (ts(), line)) if stamp else line
    with open(LOG, "a") as f:
        f.write(s + "\n")
    print(s, flush=True)


def heartbeat(period=600):
    while True:
        time.sleep(period)
        log("HEARTBEAT run_real alive: %s" % _hb_state["msg"], stamp=True)


def r3_fields(decode):
    full = C.A.adjudicate(np.array(decode, dtype=np.int64), pan=C.PAN)
    return {k: (round(float(full[k]), 4) if isinstance(full[k], float) else full[k])
            for k in ("en", "pmax", "preg", "pmax_ne", "pcon", "pcreg", "ioc", "mds",
                      "h2", "zl", "degenerate")}


def load_progress(path):
    done = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    done[rec["page"]] = rec
    return done


def assemble(bat, nbar, done, fname):
    out = {"battery": bat, "n_bar": nbar,
           "bars": {str(L): round(C.free_bar(nbar, L), 4) for L in C.FREE_LS},
           "pages": [], "crossers": []}
    total = 0
    gbest = {"pmax": -99.0}
    elapsed = 0.0
    for pi in range(55):
        rec = done[pi]
        total += rec["count"]
        elapsed += rec.get("secs", 0.0)
        out["pages"].append(rec["row"])
        out["crossers"].extend(rec["crossers"])
        if rec["row"]["pmax"] > gbest["pmax"]:
            gbest = dict(rec["row"])
    assert total <= nbar, (bat, total, nbar)
    out["total_decodes"] = total
    out["observed_global_best"] = gbest
    out["n_crossers"] = len(out["crossers"])
    out["verdict"] = ("NEGATIVE" if not out["crossers"]
                      else "CROSSER(S) - FLAGGED-FOR-ORACLE per HUMAN-ORACLE.md, not certified")
    out["elapsed_s"] = round(elapsed, 1)
    json.dump(out, open(os.path.join(RES, fname), "w"), indent=1)
    log(json.dumps({k: out[k] for k in ("battery", "total_decodes", "n_crossers",
                                        "verdict", "bars", "elapsed_s")}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-seconds", type=float, default=520.0)
    args = ap.parse_args()
    gate = json.load(open(os.path.join(RES, "plants.json")))
    assert gate["gate"] == "passed", "plant gate not passed - no real run (PREREG Q5)"
    t0 = time.time()
    threading.Thread(target=heartbeat, daemon=True).start()

    # ---- reductions of the two real artifacts (deterministic; re-verified every slice)
    streams, pads, manifest = {}, {}, {}
    for name, path in C.ART.items():
        assert C.sha256(path) == C.SHA[name], name
        s, p, m = R.reduce_file(path, name)
        assert m["pcm_deterministic"], "ffmpeg non-deterministic - battery P killed (PREREG Q5 ii)"
        streams.update(s)
        pads.update(p)
        manifest[name] = m
    json.dump(manifest, open(os.path.join(RES, "pcm_manifest.json"), "w"), indent=1)
    json.dump({k: list(map(int, v)) for k, v in streams.items()},
              open(os.path.join(RES, "streams.json"), "w"))
    log("reductions done %s %s" % ({k: len(v) for k, v in streams.items()},
                                   {k: len(v) for k, v in pads.items()}))

    pages = C.unsolved_pages()
    all_done = True

    for bat, fn, nbar, fname in (("S", lambda c: C.sweep_page_S(c, streams), C.N_BAR_S, "sweep_S.json"),
                                 ("P", lambda c: C.sweep_page_P(c, pads), C.N_BAR_P, "sweep_P.json")):
        prog_path = os.path.join(RES, "progress_%s.jsonl" % bat)
        done = load_progress(prog_path)
        gbest = {"pmax": -99.0}
        total = sum(r["count"] for r in done.values())
        for rec in done.values():
            if rec["row"]["pmax"] > gbest["pmax"]:
                gbest = dict(rec["row"])
        for pi, c in enumerate(pages):
            if pi in done:
                continue
            if time.time() - t0 > args.max_seconds:
                log("TIME-SLICE PAUSE battery %s before page %d/55" % (bat, pi), stamp=True)
                sys.exit(3)
            _hb_state["msg"] = "battery %s page %d/55" % (bat, pi)
            tp = time.time()
            cnt, best, cross = fn(c)
            secs = time.time() - tp
            total += cnt
            row = {k: v for k, v in best.items() if k != "decode"}
            row["page"] = pi
            row["r3"] = r3_fields(best["decode"])
            for x in cross:
                x["page"] = pi
            rec = {"page": pi, "count": cnt, "secs": round(secs, 1),
                   "row": row, "crossers": cross}
            with open(prog_path, "a") as f:
                f.write(json.dumps(rec) + "\n")
            done[pi] = rec
            if row["pmax"] > gbest["pmax"]:
                gbest = dict(row)
            log("B%s page %d/55 n=%d gbest %.3f (%s) %.0fs" %
                (bat, pi, total, gbest["pmax"],
                 "%s/%s/%s/%s rot %s pg %s" % (gbest.get("stream"), gbest.get("dir"),
                                               gbest.get("map"), gbest.get("cfg"),
                                               gbest.get("rot"), gbest.get("page")),
                 time.time() - t0))
        if len(done) == 55:
            assemble(bat, nbar, done, fname)
        else:
            all_done = False
    if all_done:
        log("ALL DONE %.0fs" % (time.time() - t0), stamp=True)
    else:
        sys.exit(3)


if __name__ == "__main__":
    main()
