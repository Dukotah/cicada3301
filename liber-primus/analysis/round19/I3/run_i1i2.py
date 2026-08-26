"""I3 / Round 19 — calibrate the ACTUAL Round-19 instrument: I1's `driftbeam` feeding I2's
`adjudicate`.

Everything in `run_calibration.py` is measured on this lane's own proxies: the repo's beam
and a private trigram panel. Those give the shape of the problem (how the null moves with
permissiveness, how the registers correlate). They are not the bar Phase 2 will actually use.

This module measures the bar Phase 2 will actually use:

    I1  round19/I1/driftbeam.beam_decode(..., **PRESETS[p])   ->  plain_idx
    I2  round19/I2/adjudicate.adjudicate(plain_idx)           ->  en, pmax, pmax_ne, pcon

on the SAME null (uniform random rune ciphertext, uniform random keystream) at the same
segment lengths, and fits an extreme-value curve to each statistic.

TWO THINGS THIS EXISTS TO CATCH, both of which are false-positive risks rather than power
risks, and therefore worse:

 1. I1's `permissive` relation admits key advances the ciphertext does not license. The
    larger path space per decode raises the null maximum. The lane's `union<lam>` curve
    measures the dose-response; this measures I1's actual chosen dose.
 2. I2 standardises each register's raw trigram score by the MEAN and SD of a
    UNIFORM-RANDOM-RUNE null (`Panel.cal`: `mu`, `sd`). Two distinct problems follow.
    (a) A beam decode's output is not a random rune string -- the beam maximises English --
        so the standardising null is the wrong null. I2's own `null.log` shows the gap:
        random-rune pmax max = 1.163 over 200,000 draws, wrong-key beam pmax max = 1.672
        over 8,000.
    (b) `sd` is a BULK dispersion. `benchmark/null.py`'s own calibration note is that for
        this family the bulk sd overestimates the tail scale by ~2.5x. A z built on a bulk
        sd is not on a scale where `z = 4` means anything in particular.
    Neither breaks `pmax` as a statistic -- but both mean its BAR has to be measured here,
    on the decoder-output null, rather than read off the nominal z scale.
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R19 = os.path.abspath(os.path.join(HERE, ".."))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
for _p in (os.path.join(R19, "I1"), os.path.join(R19, "I2"), os.path.join(LP, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import vecbeam as V              # noqa: E402
import nullcurve19 as NC         # noqa: E402
import run_calibration as RC     # noqa: E402

N = 29
BEAM_W = 400
STATS = ["en", "pmax", "pmax_ne", "pcon"]


def _adj():
    import adjudicate as AD
    return AD


def _db():
    import driftbeam as DB
    return DB


# ------------------------------------------------------------------ fast path (G-EQ cell)
def _work_fast(a):
    seed, T, L, mode = a
    AD = _adj()
    rng = np.random.default_rng(seed)
    KL = L * 8 + 64
    C = rng.integers(0, N, size=(T, L))
    K = rng.integers(0, N, size=(T, KL))
    r = V.batch_decode(C, K, beam_w=BEAM_W, max_skip=3, mode=mode, want_plain=True)
    p = AD.adjudicate_batch(r["plain"])
    out = {"en": r["score"], "pmax": p["pmax"], "pmax_ne": p["pmax_ne"], "pcon": p["pcon"]}
    pan = AD.panel()
    for i, reg in enumerate(pan.registers):
        out["z:" + reg] = p["z"][:, i]
    return out


# ------------------------------------------------------------------ I1 reference path
def _work_i1(a):
    seed, T, L, preset = a
    AD, DB = _adj(), _db()
    rng = np.random.default_rng(seed)
    kw = DB.PRESETS[preset]
    KL = L * (kw["max_skip"] + 2) + 128
    rows = {k: [] for k in STATS}
    pan = AD.panel()
    for k in pan.registers:
        rows["z:" + k] = []
    rows["_nunexp"] = []
    for _ in range(T):
        C = [int(x) for x in rng.integers(0, N, L)]
        K = [int(x) for x in rng.integers(0, N, KL)]
        d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=BEAM_W, **kw)
        a2 = AD.adjudicate(d["plain_idx"], translit=d["translit"])
        rows["en"].append(a2["en"])
        rows["pmax"].append(a2["pmax"])
        rows["pmax_ne"].append(a2["pmax_ne"])
        rows["pcon"].append(a2["pcon"])
        for i, k in enumerate(pan.registers):
            rows["z:" + k].append(a2["z"][i])
        rows["_nunexp"].append(d.get("n_unexplained", 0))
    return {k: np.asarray(v, dtype=np.float64) for k, v in rows.items()}


def run(worker, jobs, M, procs=6):
    t0 = time.time()
    acc = {}
    with Pool(procs) as p:
        for i, d in enumerate(p.imap_unordered(worker, jobs, chunksize=1)):
            for kk, v in d.items():
                acc.setdefault(kk, []).append(v)
            if (i + 1) % 20 == 0:
                done = sum(len(x) for x in acc[list(acc)[0]])
                el = time.time() - t0
                print(f"    {done:>9,}/{M:,}  {done/el:7.1f} dec/s  "
                      f"eta {(M-done)/max(1e-9, done/el)/60:.1f} min", flush=True)
    return {kk: np.concatenate(v) for kk, v in acc.items()}, time.time() - t0


def _cells(vals, L, M, tag, extra=None):
    out = {}
    for k, v in vals.items():
        if k.startswith("_"):
            continue
        cell = RC.summarise(v, L, M)
        if cell is None:
            continue
        cell.update({"statistic_name": k, "instrument": tag, "null_source": "uniform"})
        cell.update(extra or {})
        key = f"I19:{tag}|{k}|L{L}"
        RC.save_cell(key, cell)
        out[key] = cell
    return out


def stage_fast(L, M, mode="keyskip1", procs=6, chunk=512):
    print(f"[i2panel] L={L} mode={mode} M={M:,}", flush=True)
    jobs, k = [], 0
    while k < M:
        t = min(chunk, M - k)
        jobs.append((770000 + len(jobs) * 7919, t, L, mode))
        k += t
    vals, el = run(_work_fast, jobs, M, procs)
    tag = f"vecbeam.{mode}+I2"
    out = {"stage": "i2panel", "L": L, "mode": mode, "M": int(M), "seconds": el,
           "instrument": tag, "cells": _cells(vals, L, M, tag)}
    z = np.stack([vals[k] for k in vals if k.startswith("z:")], axis=1)
    pcell = out["cells"].get(f"I19:{tag}|pmax|L{L}")
    out["panel"] = RC.panel_report(z, pcell) if pcell else None
    if out["panel"] is not None:
        out["panel"]["registers"] = [k[2:] for k in vals if k.startswith("z:")]
        out["panel"]["note"] = ("m_eff_shift here is NOT comparable to the run_calibration "
                                "one: I2's z is standardised on a random-rune BULK sd, not "
                                "on this lane's fitted tail curve.")
    json.dump(out, open(os.path.join(HERE, f"out_i2panel_L{L}.json"), "w",
                        encoding="utf-8"), indent=1, default=float)
    print(f"[i2panel] done in {el/60:.1f} min", flush=True)
    return out


def stage_i1(preset, L, M, procs=6, chunk=None):
    DB = _db()
    chunk = chunk or max(4, min(256, M // (procs * 8) or 1))
    print(f"[i1:{preset}] L={L} M={M:,} kw={DB.PRESETS[preset]}", flush=True)
    jobs, k = [], 0
    while k < M:
        t = min(chunk, M - k)
        jobs.append((880000 + len(jobs) * 7919, t, L, preset))
        k += t
    vals, el = run(_work_i1, jobs, M, procs)
    nun = vals.pop("_nunexp")
    tag = f"driftbeam.{preset}+I2"
    out = {"stage": "i1", "preset": preset, "kw": DB.PRESETS[preset], "L": L,
           "M": int(M), "seconds": el, "instrument": tag,
           "mean_unexplained_advances": float(np.mean(nun)),
           "cells": _cells(vals, L, M, tag, extra={"preset": preset,
                                                   "preset_kw": DB.PRESETS[preset]})}
    json.dump(out, open(os.path.join(HERE, f"out_i1_{preset}_L{L}.json"), "w",
                        encoding="utf-8"), indent=1, default=float)
    print(f"[i1:{preset}] done in {el/60:.1f} min  "
          f"mean_unexplained={out['mean_unexplained_advances']:.2f}", flush=True)
    return out


# ------------------------------------------------------------------ R17 (L, beam_w) cells
def _work_r17(a):
    seed, T, L, bw = a
    rng = np.random.default_rng(seed)
    C = rng.integers(0, N, size=(T, L))
    K = rng.integers(0, N, size=(T, L * 5 + 64))
    r = V.batch_decode(C, K, beam_w=bw, max_skip=3, mode="keyskip1")
    return {"en": r["score"]}


def stage_r17(L, bw, M, procs=6, chunk=512):
    """EN_QUAD null at the (segment_len, beam_w) settings Rounds 13/16/17 actually used.

    G-HONEST needs a bar at each sweep's OWN geometry. R17 escalated at beam_w=120 on head
    windows of 25-400 runes; R13/R16 used beam_w=400 at L=120. `benchmark/null.py`'s
    constants are L~120, beam_w=400 and were quoted at all of them.
    """
    print(f"[r17] L={L} beam_w={bw} M={M:,}", flush=True)
    jobs, k = [], 0
    while k < M:
        t = min(chunk, M - k)
        jobs.append((660000 + len(jobs) * 7919, t, L, bw))
        k += t
    vals, el = run(_work_r17, jobs, M, procs)
    cell = RC.summarise(vals["en"], L, M)
    cell.update({"register": "EN_QUAD", "mode": "keyskip1", "beam_w": bw,
                 "null_source": "uniform", "statistic_name": "score_norm",
                 "seconds": el})
    key = f"EN_QUAD|keyskip1|L{L}|bw{bw}"
    RC.save_cell(key, cell)
    json.dump({"stage": "r17", "L": L, "beam_w": bw, "M": int(M), "cell_key": key,
               "cell": cell},
              open(os.path.join(HERE, f"out_r17_L{L}_bw{bw}.json"), "w", encoding="utf-8"),
              indent=1, default=float)
    print(f"[r17] L={L} bw={bw}: mu={cell['mu']:.4f} beta={cell['beta']:.5f} "
          f"({el/60:.1f} min)", flush=True)
    return cell


def check_geq(n=40, L=120, seed=515):
    """Independent check of I1's own G-EQ claim: driftbeam(keyskip1) == the repo beam,
    which is also what licenses this lane to calibrate the 'exact' preset with its fast
    engine. Cross-lane audit, doctrine R6."""
    import skipdecode as sk
    DB = _db()
    rng = np.random.default_rng(seed)
    KL = L * 6 + 64
    C = rng.integers(0, N, size=(n, L))
    K = rng.integers(0, N, size=(n, KL))
    fast = V.batch_decode(C, K, beam_w=BEAM_W, max_skip=3, mode="keyskip1")["score"]
    d1, d2 = [], []
    for t in range(n):
        c, k = list(map(int, C[t])), list(map(int, K[t]))
        d1.append(DB.beam_decode(c, k, sign=-1, o=0, beam_w=BEAM_W,
                                 **DB.PRESETS["exact"])["score"])
        d2.append(sk.beam_decode(c, k, sign=-1, o=0, beam_w=BEAM_W, max_skip=3)["score"])
    d1, d2 = np.array(d1), np.array(d2)
    return {"n": n, "L": L,
            "max_abs_diff_driftbeam_vs_skipdecode": float(np.abs(d1 - d2).max()),
            "max_abs_diff_driftbeam_vs_vecbeam": float(np.abs(d1 - fast).max()),
            "max_abs_diff_vecbeam_vs_skipdecode": float(np.abs(fast - d2).max()),
            "all_identical_1e9": bool(np.abs(d1 - d2).max() <= 1e-9
                                      and np.abs(d1 - fast).max() <= 1e-9)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--L", type=int, default=120)
    ap.add_argument("--M", type=int, default=100000)
    ap.add_argument("--preset", default="drift")
    ap.add_argument("--mode", default="keyskip1")
    ap.add_argument("--beam_w", type=int, default=120)
    ap.add_argument("--procs", type=int, default=6)
    a = ap.parse_args()
    if a.stage == "i2panel":
        stage_fast(a.L, a.M, mode=a.mode, procs=a.procs)
    elif a.stage == "i1":
        stage_i1(a.preset, a.L, a.M, procs=a.procs)
    elif a.stage == "r17":
        stage_r17(a.L, a.beam_w, a.M, procs=a.procs)
    elif a.stage == "geq":
        r = check_geq()
        json.dump(r, open(os.path.join(HERE, "out_geq.json"), "w", encoding="utf-8"),
                  indent=1)
        print(json.dumps(r, indent=1))
    else:
        raise SystemExit(a.stage)
