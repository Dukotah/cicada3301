"""P2 -- finish nskips_null.json: run the drift-L400 marginal (small), the surrogate control,
and the positive-control plants, appending to the partial JSON already written by build_null.py.
Uses small chunks so every section parallelizes across all cores (the earlier run serialized the
drift-L400 marginal because its chunk size exceeded M)."""
import json
import os
import sys
import time
import random
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nskips_lib as NL
from nskips_lib import discrete_tail
import driftbeam as DB
import build_null as B   # reuse workers _marg_chunk / _plant_cell / _seedhash

N = 29
OUT = os.path.join(HERE, "nskips_null.json")


def marg(L, mode, M, source, procs, chunk):
    jobs = []; k = 0; i = 0
    while k < M:
        t = min(chunk, M - k)
        jobs.append((L, mode, t, source, f"{mode}{L}{source}#{i}")); k += t; i += 1
    acc = []
    with Pool(procs) as p:
        for r in p.imap_unordered(B._marg_chunk, jobs):
            acc.extend(r)
    return acc


def main(procs=6):
    R = json.load(open(OUT, encoding="utf-8"))
    R["_t0"] = time.time()
    t0 = R["_t0"]

    # drift L400 marginal, small M, small chunk so it parallelizes
    if "drift|L400" not in R["marginal_null"]:
        wk = marg(400, "drift", 300, "uniform", procs, chunk=50)
        R["marginal_null"]["drift|L400"] = discrete_tail(wk)
        c = R["marginal_null"]["drift|L400"]
        print(f"[marg] drift L=400 M=300: mean {c['mean']:.2f} q95 {c['q95']} q99 {c['q99']} "
              f"max {c['max']} t={time.time()-t0:.0f}s", flush=True)
        B.dump(R)

    # surrogate control
    for L, Ms in ((120, 5000), (400, 1500)):
        key = f"keyskip1|L{L}"
        if key in R["surrogate_null"]:
            continue
        wk = marg(L, "keyskip1", Ms, "shuffle", procs, chunk=250)
        c = discrete_tail(wk)
        u = R["marginal_null"][key]["mean"]
        c["mean_ratio_vs_uniform"] = round(c["mean"] / u, 3) if u else None
        R["surrogate_null"][key] = c
        print(f"[surr] keyskip1 L={L}: shuffle-mean {c['mean']:.2f} vs uniform {u:.2f} "
              f"ratio {c['mean_ratio_vs_uniform']} t={time.time()-t0:.0f}s", flush=True)
        B.dump(R)

    # plants (positive control) -- each cell is its own job -> full parallelism
    REGS = ["LP1_REAL", "LATIN", "OE", "EN_HALFVOWEL", "EN_MODERN"]
    cells = [(mech, supp, L, reg)
             for mech in ("keyskip", "skip_by_two")
             for supp in (0.60, 0.83, 0.98)
             for L in (120, 400)
             for reg in REGS]
    done = {(p["mech"], p["supp"], p["L"], p["register"]) for p in R["plants"]}
    cells = [c for c in cells if (c[0], c[1], c[2], c[3]) not in done]
    with Pool(procs) as p:
        for i, row in enumerate(p.imap_unordered(B._plant_cell, cells)):
            R["plants"].append(row)
            if (i + 1) % 10 == 0:
                B.dump(R)
                print(f"[plant] {i+1}/{len(cells)} t={time.time()-t0:.0f}s", flush=True)
    B.dump(R)
    print(f"WROTE {OUT}  plants={len(R['plants'])}  section_elapsed {R['elapsed_s']}s",
          flush=True)


if __name__ == "__main__":
    main()
