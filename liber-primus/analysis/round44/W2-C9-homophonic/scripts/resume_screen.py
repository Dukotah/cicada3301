"""W2-C9 resume runner — restartable, spawn-context screen (semaphore-leak fix).

The original `homophonic.py screen` died at ~300/2,001 replicate rows with a
leaked-semaphore interpreter shutdown (fork-context Pool + numpy). This runner:

  * reads results/rows.jsonl, skips every tag already present (resume-exact: each
    null stream is generated from its own per-tag seed, independent of order);
  * uses multiprocessing spawn context with maxtasksperchild=40 (fresh workers,
    no inherited fork state, no semaphore accumulation);
  * appends rows to rows.jsonl with per-row flush;
  * exits cleanly after --max-minutes so it can be driven in foreground slices,
    writing a heartbeat line (ISO time + rows done) to ../run.log at slice start
    and every subsequent heartbeat interval;
  * --finalize recomputes screen.json from rows.jsonl with the PREREG-fixed bar
    (999th order statistic of BOTH families), identical logic to run_screen().

No statistic, seed, budget or bar is changed from the frozen PREREG/glue.
"""
import argparse
import datetime
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import homophonic as H  # noqa: E402

RESULTS = os.path.join(HERE, "..", "results")
ROWS = os.path.join(RESULTS, "rows.jsonl")
RUNLOG = os.path.join(HERE, "..", "run.log")


def log(msg):
    line = "%s %s" % (datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), msg)
    print(line, flush=True)
    with open(RUNLOG, "a") as fh:
        fh.write(line + "\n")


def done_tags():
    tags = set()
    if os.path.exists(ROWS):
        for line in open(ROWS):
            line = line.strip()
            if not line:
                continue
            try:
                tags.add(json.loads(line)["tag"])
            except Exception:
                pass
    return tags


def all_tags():
    yield "real"
    for i in range(H.NULL_DRAWS):
        yield "A%d" % i
    for i in range(H.NULL_DRAWS):
        yield "B%d" % i


def build_task(tag, real, s):
    if tag == "real":
        return ("real", real, 424242, True)
    fam, i = tag[0], int(tag[1:])
    if fam == "A":
        return (tag, H.shuffle_pages(real, H.SEED_A + i), H.SEED_A * 100 + i, True)
    return (tag, H.filtered_uniform(real, s, H.SEED_B + i), H.SEED_B * 100 + i, True)


def run(procs, max_minutes, heartbeat_minutes):
    import multiprocessing as mp
    real = H.real_pages()
    s = 29 * H.doublet_rate(real)
    done = done_tags()
    remaining = [t for t in all_tags() if t not in done]
    total = 1 + 2 * H.NULL_DRAWS
    log("RESUME slice start: %d/%d rows done, %d remaining, procs=%d spawn "
        "maxtasksperchild=40" % (len(done), total, len(remaining), procs))
    if not remaining:
        log("RESUME: nothing remaining")
        return 0
    t0 = time.time()
    next_hb = t0 + heartbeat_minutes * 60
    deadline = t0 + max_minutes * 60
    n_new = 0
    ctx = mp.get_context("spawn")
    stop = False
    with ctx.Pool(procs, maxtasksperchild=40) as pool, open(ROWS, "a") as fh:
        it = pool.imap(H.eval_replicate,
                       (build_task(t, real, s) for t in remaining), chunksize=1)
        for tag, ra, rn in it:
            fh.write(json.dumps({"tag": tag, "annealed": ra, "natural": rn}) + "\n")
            fh.flush()
            n_new += 1
            now = time.time()
            if now >= next_hb:
                log("HEARTBEAT: %d/%d rows (%d this slice, %.1f s/row)" %
                    (len(done) + n_new, total, n_new, (now - t0) / n_new))
                next_hb = now + heartbeat_minutes * 60
            if now >= deadline:
                stop = True
                break
        if stop:
            pool.terminate()
    left = len(remaining) - n_new
    log("RESUME slice end: +%d rows in %.1f min, %d remaining" %
        (n_new, (time.time() - t0) / 60, left))
    return left


def finalize():
    """screen.json from rows.jsonl — identical verdict logic to run_screen()."""
    real = H.real_pages()
    s = 29 * H.doublet_rate(real)
    acc = {"annealed": {k: {"A": [], "B": []} for k in H.KS},
           "natural": {}, "real": None}
    seen = set()
    for line in open(ROWS):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        tag = r["tag"]
        if tag in seen:
            continue
        seen.add(tag)
        ra = {int(k): v for k, v in r["annealed"].items()}
        rn = r["natural"]
        if tag == "real":
            acc["real"] = {"annealed": ra, "natural": rn}
        else:
            fam = tag[0]
            for k in H.KS:
                acc["annealed"][k][fam].append(ra[k])
            for name, v in rn.items():
                acc["natural"].setdefault(name, {"A": [], "B": []})[fam].append(v)
    assert acc["real"] is not None, "real row missing"

    def bar(v):
        return sorted(v)[998] if len(v) >= 999 else max(v)

    screen = {"s_keep": s, "cells": {}}
    for k in H.KS:
        tA, tB = bar(acc["annealed"][k]["A"]), bar(acc["annealed"][k]["B"])
        tr = acc["real"]["annealed"][k]
        screen["cells"]["anneal_k%d" % k] = {
            "T_real": tr, "bar_A_p999": tA, "bar_B_p999": tB,
            "n_A": len(acc["annealed"][k]["A"]), "n_B": len(acc["annealed"][k]["B"]),
            "crosser": bool(tr > tA and tr > tB)}
    for name, v in acc["natural"].items():
        tA, tB = bar(v["A"]), bar(v["B"])
        tr = acc["real"]["natural"][name]
        screen["cells"]["natural_%s" % name] = {
            "T_real": tr, "bar_A_p999": tA, "bar_B_p999": tB,
            "n_A": len(v["A"]), "n_B": len(v["B"]),
            "crosser": bool(tr > tA and tr > tB)}
    Mtr, Mte, Utr, tp = H.split_counts(real)
    details = {}
    for k in H.KS:
        A, obj = H.best_anneal(Mtr, k, 424242 + k * 104729)
        details["k%d" % k] = {"partition": A.tolist(), "train_mi": obj,
                              "T": H.t_stat(A, k, Mtr, Mte, Utr),
                              "r3": H.r3_stats(A, k, tp)}
    screen["real_details"] = details
    screen["n_crossers"] = sum(c["crosser"] for c in screen["cells"].values())
    json.dump(screen, open(os.path.join(RESULTS, "screen.json"), "w"), indent=1)
    log("FINALIZE: %d cells, %d crossers, rows=%d" %
        (len(screen["cells"]), screen["n_crossers"], len(seen)))
    return screen


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=6)
    ap.add_argument("--max-minutes", type=float, default=9.0)
    ap.add_argument("--heartbeat-minutes", type=float, default=10.0)
    ap.add_argument("--finalize", action="store_true")
    a = ap.parse_args()
    if a.finalize:
        finalize()
    else:
        left = run(a.procs, a.max_minutes, a.heartbeat_minutes)
        sys.exit(0 if left == 0 else 3)
