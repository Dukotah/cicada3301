"""I3 / Round 19 — run the null cells and fit them.

    python3 run_calibration.py --stage registers --L 120 --M 1000000
    python3 run_calibration.py --stage modes
    python3 run_calibration.py --stage panel_decode --M 100000
    python3 run_calibration.py --stage shuffle --M 20000

Each stage appends its fitted cells to `calib19.json` and writes a per-stage
`out_<stage>_<tag>.json` carrying the fit, the goodness of fit, the GEV shape test, the
G-CAL exceedance table and the G-CAL-X out-of-sample extrapolation check.

Raw score vectors are NOT persisted (1e6 x 9 float64 per cell). What is persisted is
everything a re-reader needs to check the arithmetic without re-running: block maxima at
n in {100, 1000, 10000}, the single-draw quantiles, and the fits.
"""
import argparse
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
for _p in (os.path.join(LP, "src"), os.path.join(LP, "analysis", "round11")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import vecbeam as V              # noqa: E402
import registers as R            # noqa: E402
import nullcurve19 as NC         # noqa: E402

N = 29
BEAM_W, MAX_SKIP = 400, 3
CHUNK = 512
CALIB = os.path.join(HERE, "calib19.json")

_UNS = None


def unsolved():
    global _UNS
    if _UNS is None:
        import lib_numchannel as nc
        _UNS = list(nc.unsolved())
    return _UNS


# --------------------------------------------------------------------------- workers
def _gen(rng, T, L, mode, source="uniform"):
    ms = MAX_SKIP
    KL = L * (2 * ms + 2) + 64
    if source == "uniform":
        C = rng.integers(0, N, size=(T, L))
    else:                                   # histogram-preserving shuffle of real LP2
        u = np.asarray(unsolved(), dtype=np.int64)
        C = np.empty((T, L), dtype=np.int64)
        for t in range(T):
            s = rng.integers(0, len(u) - L)
            seg = u[s:s + L].copy()
            rng.shuffle(seg)
            C[t] = seg
    K = rng.integers(0, N, size=(T, KL))
    return C, K


def _work(a):
    task, seed, T, L, mode, source = a
    rng = np.random.default_rng(seed)
    C, K = _gen(rng, T, L, mode, source)
    if task == "panel_rescore":
        r = V.batch_decode(C, K, beam_w=BEAM_W, max_skip=MAX_SKIP, mode=mode,
                           want_plain=True)
        out = {"EN_QUAD": r["score"].astype(np.float64), "_drift": r["drift"]}
        out.update({k: v.astype(np.float64)
                    for k, v in R.score_panel_rescore(r["plain"]).items()})
        return out
    if task == "en_only":
        r = V.batch_decode(C, K, beam_w=BEAM_W, max_skip=MAX_SKIP, mode=mode)
        return {"EN_QUAD": r["score"].astype(np.float64), "_drift": r["drift"]}
    if task == "panel_decode":
        lms = R.build_lms()
        r = V.batch_decode(C, K, beam_w=BEAM_W, max_skip=MAX_SKIP, mode=mode)
        out = {"EN_QUAD": r["score"].astype(np.float64), "_drift": r["drift"]}
        for reg in R.TRI_REGISTERS:
            rr = V.batch_decode(C, K, scorer="tri_rune", tri=lms[reg], beam_w=BEAM_W,
                                max_skip=MAX_SKIP, mode=mode)
            out[reg] = rr["score"].astype(np.float64)
        return out
    raise ValueError(task)


def run(task, L, mode, M, source="uniform", seed0=190301, procs=6, chunk=CHUNK):
    jobs = []
    k = 0
    while k < M:
        t = min(chunk, M - k)
        jobs.append((task, seed0 + len(jobs) * 7919, t, L, mode, source))
        k += t
    t0 = time.time()
    acc = {}
    with Pool(procs) as p:
        for i, d in enumerate(p.imap_unordered(_work, jobs, chunksize=1)):
            for kk, v in d.items():
                acc.setdefault(kk, []).append(v)
            if (i + 1) % 50 == 0:
                done = sum(len(x) for x in acc[list(acc)[0]])
                el = time.time() - t0
                print(f"    {done:>9,}/{M:,}  {done/el:7.1f} dec/s  "
                      f"eta {(M-done)/max(1e-9, done/el)/60:.1f} min", flush=True)
    return {kk: np.concatenate(v) for kk, v in acc.items()}, time.time() - t0


# --------------------------------------------------------------------------- persistence
def load_calib():
    if os.path.exists(CALIB):
        return json.load(open(CALIB, encoding="utf-8"))
    return {"generated": None, "cells": {}, "notes": {}}


def save_cell(key, cell):
    c = load_calib()
    c["cells"][key] = cell
    c["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(c, open(CALIB, "w", encoding="utf-8"), indent=1)
    NC._CALIB = None


def summarise(vals, L, M, alpha=0.01, provisional_M=1_000_000):
    f = NC.fit_cell(vals)
    if f is None:
        return None
    g = NC.gcal(vals, f["mu"], f["beta"], alpha=alpha)
    g05 = NC.gcal(vals, f["mu"], f["beta"], alpha=0.05)
    bm = {}
    for b in (100, 1000, 10000):
        m = len(vals) // b
        if m >= 8:
            bm[str(b)] = [round(float(x), 5) for x in
                          np.asarray(vals)[:m * b].reshape(m, b).max(axis=1)[:500]]
    qs = [0.5, 0.9, 0.99, 0.999, 0.9999, 0.99999]
    cell = {"L": L, "M": int(M), "mu": f["mu"], "beta": f["beta"],
            "beta_regression": f["beta_regression"], "anchor_block": f["anchor_block"],
            "bulk_sd_beta": f["bulk_sd_beta"], "single_mean": f["single_mean"],
            "single_sd": f["single_sd"], "single_max": f["single_max"],
            "quantiles": {str(q): float(np.quantile(vals, q)) for q in qs},
            "gev": f["gev"], "per_block": f["per_block"],
            "extrapolation_check": f["extrapolation_check"],
            "gcal_a01": g, "gcal_a05": g05,
            "block_maxima": bm,
            "status": "CALIBRATED" if (M >= provisional_M and g["passed"]) else "PROVISIONAL",
            "provisional_reason": (None if M >= provisional_M
                                   else f"M={int(M):,} < 1e6 (G-CAL sample-size floor)")}
    return cell


# --------------------------------------------------------------------------- stages
def stage_registers(L, M, source="uniform", mode="keyskip1", procs=6):
    tag = f"L{L}" + ("" if source == "uniform" else f"_{source}")
    print(f"[registers] L={L} mode={mode} M={M:,} source={source}", flush=True)
    vals, el = run("panel_rescore", L, mode, M, source=source, procs=procs)
    drift = vals.pop("_drift")
    out = {"stage": "registers", "L": L, "mode": mode, "source": source,
           "M": int(M), "seconds": el, "panel_mode": "rescore",
           "mean_realised_drift": float(np.mean(drift)), "cells": {}}
    z = []
    for reg in R.PANEL:
        cell = summarise(vals[reg], L, M)
        cell.update({"register": reg, "mode": mode, "panel_mode": "rescore",
                     "null_source": source})
        key = NC.cell_key(reg, mode, L)
        if source == "uniform":
            save_cell(key, cell)
        out["cells"][key] = cell
        z.append((vals[reg] - cell["mu"]) / cell["beta"])
    Z = np.stack(z, axis=1)
    pm = Z.max(axis=1)
    pcell = summarise(pm, L, M)
    pcell.update({"register": "PANEL", "mode": mode, "panel_mode": "rescore",
                  "null_source": source, "statistic": "panel_max"})
    pkey = NC.cell_key(None, mode, L, statistic="panel_max", panel_mode="rescore")
    if source == "uniform":
        save_cell(pkey, pcell)
    out["cells"][pkey] = pcell
    out["panel"] = panel_report(Z, pcell)
    json.dump(out, open(os.path.join(HERE, f"out_registers_{tag}.json"), "w",
                        encoding="utf-8"), indent=1, default=float)
    print(f"[registers] done in {el/60:.1f} min -> out_registers_{tag}.json", flush=True)
    return out


def panel_report(Z, pcell):
    """The panel-max correction: effective number of independent tests, two estimators."""
    eig = NC.effective_tests_eigen(Z)
    # shift estimator: the z's are standardised so a single register's own max-of-N curve is
    # Gumbel(0, 1) by construction; the panel max curve is Gumbel(mu_P, beta_P).
    m_shift = NC.effective_tests_shift(pcell["mu"], 0.0, 1.0)
    m_shift_b = math.exp(pcell["mu"] / pcell["beta"]) if pcell["beta"] else float("nan")
    ratio = max(m_shift, eig["li_ji"]) / max(1e-9, min(m_shift, eig["li_ji"]))
    return {"m_eff_shift": m_shift, "m_eff_shift_betascaled": m_shift_b,
            "m_eff_li_ji": eig["li_ji"], "m_eff_cheverud": eig["cheverud_nyholt"],
            "naive_bonferroni": len(R.PANEL),
            "estimator_ratio": ratio, "gpanel_passed": bool(ratio <= 1.5),
            "panel_mu": pcell["mu"], "panel_beta": pcell["beta"],
            "eigenvalues": eig["eigenvalues"], "corr": eig["corr"],
            "registers": R.PANEL}


def stage_modes(M_sparse, M_dense, L=120, procs=6):
    modes = ["skip_by_two", "drift1", "drift2", "drift3",
             "union8", "union6", "union4", "union2"]
    out = {"stage": "modes", "L": L, "cells": {}, "curve": []}
    for m in modes:
        sparse = V.mode_spec(m, MAX_SKIP)["sparse"]
        M = M_sparse if sparse else M_dense
        print(f"[modes] {m} M={M:,}", flush=True)
        vals, el = run("en_only", L, m, M, procs=procs)
        drift = vals.pop("_drift")
        cell = summarise(vals["EN_QUAD"], L, M)
        cell.update({"register": "EN_QUAD", "mode": m, "panel_mode": None,
                     "null_source": "uniform", "seconds": el,
                     "mean_realised_drift": float(np.mean(drift)),
                     "nominal_branching": V.branching(m, MAX_SKIP)})
        key = NC.cell_key("EN_QUAD", m, L)
        save_cell(key, cell)
        # the legacy 'EN' alias for the same statistic, so Phase 2 can ask either way
        save_cell(NC.cell_key("EN", m, L), dict(cell, register="EN"))
        out["cells"][key] = cell
        out["curve"].append({"mode": m, "lam": V.mode_spec(m, MAX_SKIP)["lam"],
                             "mu": cell["mu"], "beta": cell["beta"],
                             "mean": cell["single_mean"],
                             "realised_drift": cell["mean_realised_drift"],
                             "bar_1e6_a01": NC._fw(1e6, cell["mu"], cell["beta"], 0.01),
                             "M": int(M)})
        json.dump(out, open(os.path.join(HERE, "out_modes.json"), "w", encoding="utf-8"),
                  indent=1, default=float)
        print(f"[modes] {m}: mu={cell['mu']:.3f} beta={cell['beta']:.4f} "
              f"drift={cell['mean_realised_drift']:.4f} ({el/60:.1f} min)", flush=True)
    return out


def stage_panel_decode(M, L=120, mode="keyskip1", procs=6):
    print(f"[panel_decode] L={L} M={M:,}", flush=True)
    vals, el = run("panel_decode", L, mode, M, procs=procs)
    vals.pop("_drift")
    out = {"stage": "panel_decode", "L": L, "mode": mode, "M": int(M),
           "seconds": el, "panel_mode": "decode", "cells": {}}
    z = []
    for reg in R.PANEL:
        cell = summarise(vals[reg], L, M)
        cell.update({"register": reg, "mode": mode, "panel_mode": "decode",
                     "null_source": "uniform"})
        key = NC.cell_key(reg, mode, L) + "|decode"
        save_cell(key, cell)
        out["cells"][key] = cell
        z.append((vals[reg] - cell["mu"]) / cell["beta"])
    Z = np.stack(z, axis=1)
    pcell = summarise(Z.max(axis=1), L, M)
    pcell.update({"register": "PANEL", "mode": mode, "panel_mode": "decode",
                  "statistic": "panel_max", "null_source": "uniform"})
    pkey = NC.cell_key(None, mode, L, statistic="panel_max", panel_mode="decode")
    save_cell(pkey, pcell)
    out["cells"][pkey] = pcell
    out["panel"] = panel_report(Z, pcell)
    json.dump(out, open(os.path.join(HERE, "out_panel_decode.json"), "w",
                        encoding="utf-8"), indent=1, default=float)
    print(f"[panel_decode] done in {el/60:.1f} min", flush=True)
    return out


# --------------------------------------------------------------------------- PIT panel
def stage_pit(L, M, mode="keyskip1", procs=6):
    """Compare two ways of combining the 9 registers into ONE panel statistic.

    (a) MAX-Z, what I2 does: z_r = (s_r - mu_r)/scale_r, panel = max_r z_r.
        Whatever `scale_r` is, the registers' per-draw SHAPES still differ, so the max is
        driven by whichever register has the widest bulk relative to its tail. The
        multiplicity is then not the dominant term and no "effective number of tests" can
        describe it.
    (b) MIN-P, the probability-integral-transform panel: p_r = P_null(S_r >= s_r) from the
        register's OWN empirical null, panel = -log10 min_r p_r. This makes the registers
        exactly commensurable by construction, whatever their shapes, so the panel null IS
        a pure multiplicity-plus-correlation problem and M_eff becomes meaningful.

    The reference null (for the PIT) and the test sample are DISJOINT halves, so the
    transform is not fitted on the data it is applied to.
    """
    print(f"[pit] L={L} M={M:,}", flush=True)
    vals, el = run("panel_rescore", L, mode, M, procs=procs)
    vals.pop("_drift", None)
    regs = [r for r in R.PANEL if r in vals]
    X = np.stack([vals[r] for r in regs], axis=1)
    h = len(X) // 2
    ref, tst = X[:h], X[h:]
    # (a) max-z on the fitted tail curves of the reference half
    mus, betas = [], []
    for j in range(len(regs)):
        f = NC.fit_cell(ref[:, j])
        mus.append(f["mu"])
        betas.append(f["beta"])
    Z = (tst - np.array(mus)) / np.array(betas)
    maxz = Z.max(axis=1)
    cz = summarise(maxz, L, len(maxz))
    # (b) min-p by empirical PIT against the reference half
    nref = ref.shape[0]
    P = np.empty_like(tst)
    for j in range(len(regs)):
        s = np.sort(ref[:, j])
        # P(S >= x) = (nref - searchsorted_left(x)) / nref, floored at 1/(nref+1)
        k = np.searchsorted(s, tst[:, j], side="left")
        P[:, j] = np.maximum(nref - k, 1.0) / (nref + 1.0)
    minp = -np.log10(P.min(axis=1))
    cp = summarise(minp, L, len(minp))
    # what a single register's min-p looks like, for the shift estimator
    single = -np.log10(P[:, 0])
    cs = summarise(single, L, len(single))
    eig = NC.effective_tests_eigen(Z)
    eigp = NC.effective_tests_eigen(-np.log10(P))
    # TAIL-RATIO estimator, the form I2 uses in its own null.log:
    #   P(panel > t) ~ k_eff * P(z_EN > t), with t the alpha-quantile of the English
    #   register's own null. This is the estimator that matters for a bar, because it is
    #   evaluated where the bar lives rather than at the centre of the distribution.
    i_en = regs.index("EN_MODERN") if "EN_MODERN" in regs else 0
    tail = {}
    for a_ref in (1e-2, 1e-3, 1e-4):
        t = float(np.quantile(Z[:, i_en], 1 - a_ref))
        tail[f"maxz_alpha{a_ref:g}"] = float((maxz > t).mean() / a_ref)
        tp = float(np.quantile(-np.log10(P[:, i_en]), 1 - a_ref))
        tail[f"minp_alpha{a_ref:g}"] = float((minp > tp).mean() / a_ref)
    # For -log10(p) the max-of-M-independent curve is Gumbel(log10(M)/1, ...) in log10 units:
    # a single register's -log10 p has an exponential upper tail with scale 1/ln(10) in
    # log10 units, so M independent registers shift the location by log10(M).
    m_eff_minp = 10 ** (cp["mu"] - cs["mu"])
    out = {"stage": "pit", "L": L, "M": int(M), "seconds": el, "registers": regs,
           "maxz": {"mu": cz["mu"], "beta": cz["beta"],
                    "m_eff_shift": math.exp(cz["mu"]),
                    "li_ji": eig["li_ji"], "cheverud": eig["cheverud_nyholt"]},
           "minp": {"mu": cp["mu"], "beta": cp["beta"],
                    "single_mu": cs["mu"], "single_beta": cs["beta"],
                    "m_eff_shift": m_eff_minp,
                    "li_ji": eigp["li_ji"], "cheverud": eigp["cheverud_nyholt"]},
           "naive_bonferroni": len(regs),
           "k_eff_tail_ratio": tail,
           "english_register_used": regs[i_en],
           "cell_maxz": cz, "cell_minp": cp, "cell_single_minp": cs,
           "corr_z": eig["corr"], "eigenvalues_z": eig["eigenvalues"]}
    save_cell(NC.cell_key(None, mode, L, statistic="panel_max", panel_mode="minp"), cp)
    json.dump(out, open(os.path.join(HERE, f"out_pit_L{L}.json"), "w", encoding="utf-8"),
              indent=1, default=float)
    print(f"[pit] max-z: mu={cz['mu']:.3f} beta={cz['beta']:.3f} m_eff={math.exp(cz['mu']):.1f} "
          f"li_ji={eig['li_ji']:.2f}", flush=True)
    print(f"[pit] min-p: mu={cp['mu']:.3f} beta={cp['beta']:.3f} m_eff={m_eff_minp:.1f} "
          f"li_ji={eigp['li_ji']:.2f}  ({el/60:.1f} min)", flush=True)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--L", type=int, default=120)
    ap.add_argument("--M", type=int, default=100000)
    ap.add_argument("--M2", type=int, default=20000)
    ap.add_argument("--mode", default="keyskip1")
    ap.add_argument("--source", default="uniform")
    ap.add_argument("--procs", type=int, default=6)
    a = ap.parse_args()
    if a.stage == "registers":
        stage_registers(a.L, a.M, source=a.source, mode=a.mode, procs=a.procs)
    elif a.stage == "modes":
        stage_modes(a.M, a.M2, L=a.L, procs=a.procs)
    elif a.stage == "pit":
        stage_pit(a.L, a.M, mode=a.mode, procs=a.procs)
    elif a.stage == "panel_decode":
        stage_panel_decode(a.M, L=a.L, mode=a.mode, procs=a.procs)
    else:
        raise SystemExit(f"unknown stage {a.stage}")
