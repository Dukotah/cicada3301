"""I3/R32: multi-point null curve. Seed-3301 histogram-preserving shuffle of real LP2,
vectorised exact beam (round19/I3 machinery), several L. Usage: python curve32.py L M [procs]"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
I3 = os.path.abspath(os.path.join(HERE, "..", "..", "round19", "I3"))
sys.path.insert(0, I3)
import run_calibration as RC
import nullcurve19 as NC
OUT = os.path.join(HERE, "cells32.json")

if __name__ == "__main__":
    L, M = int(sys.argv[1]), int(sys.argv[2]); procs = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    t = time.time()
    r, el = RC.run("en_only", L, "keyskip1", M, source="shuffle", seed0=3301, procs=procs, chunk=256)
    v = r["EN_QUAD"]
    f = NC.fit_cell(v)
    cell = {"L": L, "M": int(M), "seed0": 3301, "mu": f["mu"], "beta": f["beta"],
            "beta_regression": f["beta_regression"], "anchor_block": f["anchor_block"],
            "single_mean": f["single_mean"], "single_sd": f["single_sd"],
            "single_max": f["single_max"], "seconds": round(el, 1)}
    d = json.load(open(OUT)) if os.path.exists(OUT) else {}
    d[str(L)] = cell; json.dump(d, open(OUT, "w"), indent=1)
    print(cell)
