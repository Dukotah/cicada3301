"""R44 / W2-C8 real sweep — PREREG section 2 enumeration over LP2 unsolved.

Gated on plant_results.json all_passed (PREREG Q5).  Streams: continuous 12,956-rune
unsolved stream + 55 per-segment.  Persists per-row R3 stats (rows.npz, rebuildable) +
full records for top-200 and every crosser (sweep_results.json) + the diagnostic
deterministic-null gap (null_diag.json).
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import c8lib as L                                            # noqa: E402


def gate():
    p = json.load(open(os.path.join(HERE, "plant_results.json")))
    assert p.get("all_passed") is True, "plant gate not passed - refusing to run"
    return p


FAMC = {"ctaff": 0, "ctwin": 1, "pmaff": 2, "pmwin": 3}


def main():
    plant = gate()
    t0 = time.time()
    U = np.array(L.nc.unsolved(), dtype=np.int64)
    segs = [np.array(s, dtype=np.int64) for s in L.nc.segments()[:-2]]
    assert len(U) == 12956 and len(segs) == 55

    sink, state = L.make_topsink(top_n=200)
    cols = dict(stream=[], orient=[], k=[], fam=[], row_in_batch=[],
                pmax=[], pmax_ne=[], pcon=[], ioc=[])

    def my_sink(stream_id, orient, k, n, meta, r, ioc, X):
        B = len(meta)
        cols["stream"].append(np.full(B, stream_id if isinstance(stream_id, int) else -1,
                                      dtype=np.int16))
        cols["orient"].append(np.full(B, 0 if orient == "fwd" else 1, dtype=np.int8))
        cols["k"].append(np.full(B, k, dtype=np.int8))
        cols["fam"].append(np.array([FAMC[m[0]] for m in meta], dtype=np.int8))
        cols["row_in_batch"].append(np.arange(B, dtype=np.int16))
        cols["pmax"].append(r["pmax"].astype(np.float32))
        cols["pmax_ne"].append(r["pmax_ne"].astype(np.float32))
        cols["pcon"].append(r["pcon"].astype(np.float32))
        cols["ioc"].append(ioc.astype(np.float32))
        sink(stream_id, orient, k, n, meta, r, ioc, X)

    L.sweep_stream(U, -1, lambda *a: my_sink(*a))            # continuous, stream id -1
    t_cont = time.time() - t0
    for si, seg in enumerate(segs):
        L.sweep_stream(seg, si, lambda *a: my_sink(*a))
    t_sweep = time.time() - t0

    arrs = {k: np.concatenate(v) for k, v in cols.items()}
    np.savez_compressed(os.path.join(HERE, "rows.npz"), **arrs)
    n_rows = int(arrs["pmax"].size)

    # full SWEEPROW records for top-200 (adjudicate the rows that matter)
    top = L.top_rows(state)

    # per-family / per-scope best
    fam_best = {}
    cont = arrs["stream"] == -1
    for fam, code in FAMC.items():
        m = arrs["fam"] == code
        for scope, msk in (("continuous", m & cont), ("segments", m & ~cont)):
            if msk.any():
                fam_best[f"{fam}/{scope}"] = round(float(arrs["pmax"][msk].max()), 3)

    # diagnostic deterministic-null gap: 200 shuffles x ct-affine k=7 fwd batch
    rng = np.random.default_rng(3301)
    null_max = []
    for _d in range(200):
        S = rng.permutation(U)
        Xa = L.decode_ct_affine(S, 7)
        r = L.A.adjudicate_batch(Xa, pan=L.PAN)
        null_max.append(float(r["pmax"].max()))
    null_max = np.array(null_max)
    null = dict(draws=200, family="ct-affine k=7 fwd, 812 cells, shuffled unsolved stream",
                seed=3301, per_draw_max_pmax_mean=round(float(null_max.mean()), 3),
                p99=round(float(np.quantile(null_max, 0.99)), 3),
                max=round(float(null_max.max()), 3),
                bar_of_record_729=L.BARS[729])
    json.dump(null, open(os.path.join(HERE, "null_diag.json"), "w"), indent=1)

    best = state["best"]
    out = dict(
        n_rows=n_rows, n_rows_primary=state["n_rows_primary"],
        n_rows_diag_short=state["n_rows_diag"], n_bar=L.N_BAR, bars=L.BARS,
        plant_gate=dict(all_passed=plant["all_passed"],
                        short_L_power=plant["short_L_power_diagnostics"]),
        best=best, n_crossers=len(state["crossers"]), crossers=state["crossers"],
        family_best=fam_best, top200=top, null_diag=null,
        wall_s=round(time.time() - t0, 1), wall_continuous_s=round(t_cont, 1),
        wall_sweep_s=round(t_sweep, 1))
    json.dump(out, open(os.path.join(HERE, "sweep_results.json"), "w"), indent=1)
    print(f"rows={n_rows} (primary {state['n_rows_primary']}, short-L diag "
          f"{state['n_rows_diag']})  crossers={len(state['crossers'])}")
    b = best
    print(f"best pmax={b['pmax']:.3f} vs bar {b['bar']} | stream={b['stream']} "
          f"orient={b['orient']} k={b['k']} fam={b['family']} src={b['src']} "
          f"cell={b['cell']} seed={b['seed']} n={b['n']} preg={L.PAN.registers[b['preg']]}")
    print("family best:", fam_best)
    print("null diag:", null)
    print("wall %.1fs" % out["wall_s"])


if __name__ == "__main__":
    main()
