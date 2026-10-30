"""Round 37 / I1: re-decode O3's ILP32 free cell (L=729) under panel-R36 and judge it against null_free.json."""
import sys, os, json, math
sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_null_free as R
import numpy as np
SEED = 1354603465; L = 729
res = {}
nf = json.load(open(os.path.join(HERE, "null_free.json")))
cell = nf["cells"]["729"]; draws = np.array(nf["draws_raw"]["729"])
O3 = json.load(open(os.path.join(R.LP, "analysis", "round36", "O3-nearmiss-1354603465", "cells.json")))
for abi in ("bash4.2_i32", "bash4.2"):
    K = R.C1.ks(SEED, abi, R.kl(L)); C = list(R.U[0:L])
    d = R.V.beam_decode_v3(C, K, "free", "panel_max", sign=-1, o=0, beam_w=400, tau=0.0, lam_u=4.0)
    x = d["plain_idx"]; r = R.AD.adjudicate_batch(np.asarray([x], dtype=np.int64), pan=R.PAN)
    pm = float(r["pmax"][0]); reg = R.PAN.registers[int(r["preg"][0])]
    o3 = [c for c in O3["rows"] if c["abi"] == abi and c["rel"] == "free" and c["sign"] == -1 and c["L"] == 729 and c["o"] == 0 and c["c0"] == 0][0]
    beta, mu = cell["beta"], cell["mu"]
    p_single = 1 - math.exp(-math.exp(-(pm - mu) / beta))      # Gumbel-max single-decode exceedance
    p_pot = cell["p_u"] * math.exp(-(pm - cell["u"]) / beta) if pm > cell["u"] else None
    # family-wise over ~460 free cells in the O3 grid (upper bound; treats cells as independent)
    fw = 1 - (1 - (p_pot if p_pot is not None else 1.0)) ** 460
    res[abi] = {"pmax12_r36_beam": pm, "register": reg, "n_skips": d["n_skips"], "ptr_end": d["ptr_end"], "O3_stored_pmax9_9reg_beam": o3["pmax9"], "O3_stored_pmax12_9reg_beam": o3["pmax12"],
                "null_n": len(draws), "null_median": float(np.median(draws)), "null_max": float(draws.max()), "emp_exceed_frac": float((draws >= pm).mean()),
                "emp_quantile": float((draws < pm).mean()), "gumbel_p_single": p_pot, "gumbel_p_single_alt_cdf": p_single, "bar_N1e3": cell["bars"]["1000"], "bar_N1e5": cell["bars"]["100000"], "bar_N1e6": cell["bars"]["1e+06"],
                "familywise_p_460_cells": fw, "above_bar_N460": bool(pm >= cell["mu"] + beta * math.log(460 / -math.log1p(-0.01)))}
json.dump(res, open(os.path.join(HERE, "o3_cell_rejudged.json"), "w"), indent=1); print(json.dumps(res, indent=1))
