"""Round 21 / L2 -- measure the n_skips power-crossover length L in (400, 12956).

Reuses the Round 20 P2 assets verbatim (round20/P2/nskips_lib.py: the plant machinery, the two
admitted I1 relations keyskip1/drift, the exact discrete-tail null).  This driver does NOT rebuild
the P2 endpoints from scratch -- it re-derives them with the SAME machinery as the Q1-gate, then
sweeps a geometric L ladder to locate the crossover.

Per PREREG (seed 3301, order-preserving, FPR=0.01 two-sided):
  Q1-gate  : L=400 must NOT separate (p >> 0.01) and L=12956 MUST separate (right-tail, rec>=0.99).
             If either fails -> KILL (Q5), write no crossover.
  ladder   : L in {400,600,900,1200,1600,2400,3600,6000,9000,12956}
  per L     : plant (keyskip supp=0.83, correct-key decode+recover) + size-matched wrong-key null
              (M uniform-random ciphertext x keystream), two-sided p of correct n_skips vs null.
  crossover : smallest ladder L with p<=0.01 that persists for all larger measured L.

Language-agnostic statistics persisted at run time: full wrong-key discrete histogram, correct
n_skips, ground-truth n_skips, recovery, two-sided p. n_skips is register-blind by construction;
no English score gates anything.

Writes nskips_crossover.json incrementally so a wall-clock cap never loses completed L points.
"""
import json
import os
import sys
import time
import random
import hashlib
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
P2 = os.path.abspath(os.path.join(HERE, "..", "..", "round20", "P2"))
sys.path.insert(0, P2)

import nskips_lib as NL          # noqa: E402  -- the Round 20 P2 plant + null machinery, verbatim
from nskips_lib import discrete_tail  # noqa: E402
import driftbeam as DB           # noqa: E402  -- the only decoder allowed on LP2

N = 29
SEED3301 = NL.SEED3301
FPR = 0.01
OUT = os.path.join(HERE, "nskips_crossover.json")

# geometric-ish ladder inside (400, 12956); endpoints 400 and 12956 are the Q1-gate.
LADDER = [400, 600, 900, 1200, 1600, 2400, 3600, 6000, 9000, 12956]
# null size per L.  Larger L is costlier per decode; we hold M constant so every L's two-sided p
# has the same resolution (1/M = 0.33% -> can resolve the 1% FPR two-sided cleanly).
M_NULL = 300
# registers to demonstrate register-invariance of the crossover (PREREG Q4.3).  LP1_REAL at every
# L; the full panel only at the crossover neighbourhood to keep the budget bounded.
REG_PRIMARY = "LP1_REAL"
REG_PANEL = ["LP1_REAL", "LATIN", "OE", "EN_HALFVOWEL", "EN_MODERN"]
MECHS = ["keyskip", "skip_by_two"]   # reported as SEPARATE curves (R18 L7-B: beam misses skip_by_two)


def _seedhash(tag):
    return int.from_bytes(hashlib.sha256(f"L2|{SEED3301}|{tag}".encode()).digest()[:8], "big")


def _wrongkey_chunk(a):
    """A chunk of wrong-key n_skips: uniform-random ciphertext x uniform-random keystream."""
    L, mode, M, seedtag = a
    rng = random.Random(_seedhash(seedtag))
    kw = {k: v for k, v in NL.PRESET[mode].items() if k != "mode"}
    ms = kw.get("max_skip", 3)
    KL = L * (ms + 2) + 64
    out = []
    for _ in range(M):
        C = [rng.randrange(N) for _ in range(L)]
        K = [rng.randrange(N) for _ in range(KL)]
        r = NL.decode_preset(C, K, mode, o=0, want_path=False)
        out.append(int(r["n_skips"]))
    return out


def wrongkey_null(L, mode, M, procs, chunk=25):
    jobs, k, i = [], 0, 0
    while k < M:
        t = min(chunk, M - k)
        jobs.append((L, mode, t, f"{mode}{L}#{i}"))
        k += t
        i += 1
    acc = []
    with Pool(procs) as p:
        for r in p.imap_unordered(_wrongkey_chunk, jobs):
            acc.extend(r)
    return acc


def two_sided_p(null_sample, v):
    """Two-sided empirical p of value v against a discrete null sample."""
    n = len(null_sample)
    left = sum(1 for x in null_sample if x <= v) / n
    right = sum(1 for x in null_sample if x >= v) / n
    return left, right, 2 * min(left, right)


def plant_and_decode(reg, L, mech, supp=0.83):
    """Plant a real-rejection-loop cipher and decode with the CORRECT key under keyskip1.
    Returns (correct_nskips, gt_nskips, recovery)."""
    seed = REG_PANEL.index(reg)
    C, K, P, gt = NL.plant(reg, L, seed, mech=mech, supp=supp)
    rc = NL.decode_preset(C, K, "keyskip1", o=0, want_path=True)
    rec = DB.recovery(rc["plain_idx"], P)
    return int(rc["n_skips"]), int(gt), round(rec, 4)


def measure_L(L, mode, mech, reg, procs, M=M_NULL, supp=0.83):
    """One (L, mode, mech, reg) cell: plant+recover, size-matched wrong-key null, two-sided p."""
    cc, gt, rec = plant_and_decode(reg, L, mech, supp=supp)
    null = wrongkey_null(L, mode, M, procs)
    tail = discrete_tail(null)
    left, right, p2 = two_sided_p(null, cc)
    return {
        "L": L, "mode": mode, "mech": mech, "register": reg, "supp": supp,
        "correct_nskips": cc, "gt_nskips": gt, "recovery": rec,
        "null_M": len(null), "null_mean": round(tail["mean"], 3), "null_max": tail["max"],
        "null_q99": tail["q99"], "null_hist": tail["hist"],
        "p_left": round(left, 4), "p_right": round(right, 4), "p_two_sided": round(p2, 4),
        "separates": p2 <= FPR and rec >= 0.90,
    }


def dump(R, t0):
    R["elapsed_s"] = round(time.time() - t0, 1)
    json.dump({k: v for k, v in R.items() if not k.startswith("_")},
              open(OUT, "w"), indent=1)


def crossover_of(points, mode, mech):
    """Smallest L (over the sorted ladder) whose cell separates AND every larger measured L for
    the same (mode,mech) also separates.  None if no such L."""
    rows = sorted([p for p in points if p["mode"] == mode and p["mech"] == mech and
                   p["register"] == REG_PRIMARY], key=lambda r: r["L"])
    Ls = [r["L"] for r in rows]
    sep = {r["L"]: r["separates"] for r in rows}
    for i, L in enumerate(Ls):
        if sep[L] and all(sep[L2] for L2 in Ls[i:]):
            return L
    return None


def main(procs=6):
    t0 = time.time()
    R = {"v": "L2/nskips_crossover/1", "seed": SEED3301, "order_preserving": True,
         "fpr": FPR, "ladder": LADDER, "null_M_per_L": M_NULL,
         "reuses": "analysis/round20/P2/nskips_lib.py (plant machinery + keyskip1/drift relations)",
         "direction": "two-sided; crossover reported per (mode,mech) as smallest persisting L",
         "q1_gate": {}, "points": []}

    # ---- Q1-gate FIRST (Q5 kill checkpoint): the two R20 endpoints, keyskip1 / keyskip. ----
    print("[Q1-gate] reproducing R20 endpoints L=400 (no-sep) and L=12956 (sep)...", flush=True)
    lo = measure_L(400, "keyskip1", "keyskip", REG_PRIMARY, procs)
    R["q1_gate"]["L400"] = lo
    R["points"].append(lo)
    dump(R, t0)
    print(f"  L=400  keyskip1: correct {lo['correct_nskips']} vs null mean {lo['null_mean']} "
          f"q99 {lo['null_q99']} -> p2={lo['p_two_sided']} rec={lo['recovery']} "
          f"sep={lo['separates']}", flush=True)

    hi = measure_L(12956, "keyskip1", "keyskip", REG_PRIMARY, procs)
    R["q1_gate"]["L12956"] = hi
    R["points"].append(hi)
    dump(R, t0)
    print(f"  L=12956 keyskip1: correct {hi['correct_nskips']} vs null mean {hi['null_mean']} "
          f"max {hi['null_max']} -> p2={hi['p_two_sided']} rec={hi['recovery']} "
          f"sep={hi['separates']}", flush=True)

    gate_pass = (not lo["separates"]) and hi["separates"] and hi["recovery"] >= 0.99
    R["q1_gate"]["pass"] = bool(gate_pass)
    R["q1_gate"]["reason"] = (
        f"L=400 no-sep (p2={lo['p_two_sided']}>{FPR}): {not lo['separates']}; "
        f"L=12956 sep (p2={hi['p_two_sided']}<= {FPR}, rec {hi['recovery']}>=0.99): "
        f"{hi['separates'] and hi['recovery']>=0.99}")
    dump(R, t0)
    if not gate_pass:
        R["killed"] = True
        R["kill_reason"] = ("Q5 KILL: endpoints do not reproduce R20 -> null build broken or "
                            "instrument mismatch. NO crossover reported. " + R["q1_gate"]["reason"])
        dump(R, t0)
        print("[Q5 KILL] " + R["kill_reason"], flush=True)
        return R
    print("[Q1-gate] PASS -- endpoints reproduce; sweeping the ladder.", flush=True)

    # ---- ladder: LP1_REAL at every intermediate L, both channels, keyskip mechanism. ----
    inner = [L for L in LADDER if L not in (400, 12956)]
    for L in inner:
        for mode in ("keyskip1", "drift"):
            cell = measure_L(L, mode, "keyskip", REG_PRIMARY, procs)
            R["points"].append(cell)
            dump(R, t0)
            print(f"  L={L:5d} {mode:8s}: correct {cell['correct_nskips']} vs null mean "
                  f"{cell['null_mean']} q99 {cell['null_q99']} -> p2={cell['p_two_sided']} "
                  f"rec={cell['recovery']} sep={cell['separates']}  t={time.time()-t0:.0f}s",
                  flush=True)
    # keyskip1 at the two endpoints for the drift channel too (completeness of the p-curve)
    for L in (400, 12956):
        cell = measure_L(L, "drift", "keyskip", REG_PRIMARY, procs)
        R["points"].append(cell)
        dump(R, t0)

    # ---- crossover per channel (keyskip mechanism, primary register) ----
    R["crossover"] = {
        "keyskip1|keyskip": crossover_of(R["points"], "keyskip1", "keyskip"),
        "drift|keyskip": crossover_of(R["points"], "drift", "keyskip"),
    }
    dump(R, t0)
    xk = R["crossover"]["keyskip1|keyskip"]
    print(f"[crossover] keyskip1/keyskip smallest persisting-separation L = {xk}", flush=True)

    # ---- skip_by_two as a SEPARATE curve (R18 L7-B: beam misses it) -- keyskip1 channel only ----
    print("[skip_by_two] measuring the second mechanism's curve (reported separately)...",
          flush=True)
    for L in LADDER:
        cell = measure_L(L, "keyskip1", "skip_by_two", REG_PRIMARY, procs)
        R["points"].append(cell)
        dump(R, t0)
        print(f"  [s2] L={L:5d}: correct {cell['correct_nskips']} vs null mean {cell['null_mean']} "
              f"q99 {cell['null_q99']} -> p2={cell['p_two_sided']} rec={cell['recovery']} "
              f"sep={cell['separates']}", flush=True)
    R["crossover"]["keyskip1|skip_by_two"] = crossover_of(R["points"], "keyskip1", "skip_by_two")
    dump(R, t0)

    # ---- register-invariance of the crossover: full panel at the crossover neighbourhood ----
    if xk is not None:
        nbr = sorted(set([xk] + [L for L in LADDER if abs(L - xk) <= 800]))
        print(f"[register-invariance] full 5-register panel at L in {nbr}...", flush=True)
        for L in nbr:
            for reg in REG_PANEL:
                if reg == REG_PRIMARY:
                    continue
                cell = measure_L(L, "keyskip1", "keyskip", reg, procs)
                R["points"].append(cell)
                dump(R, t0)
        # per-register crossover for reporting invariance
        R["crossover_by_register"] = {}
        for reg in REG_PANEL:
            rows = sorted([p for p in R["points"] if p["mode"] == "keyskip1" and
                           p["mech"] == "keyskip" and p["register"] == reg], key=lambda r: r["L"])
            Ls = [r["L"] for r in rows]
            sep = {r["L"]: r["separates"] for r in rows}
            xr = None
            for i, L in enumerate(Ls):
                if sep[L] and all(sep[L2] for L2 in Ls[i:]):
                    xr = L
                    break
            R["crossover_by_register"][reg] = xr
        dump(R, t0)

    R["done"] = True
    dump(R, t0)
    print(f"WROTE {OUT}  points={len(R['points'])}  elapsed {R['elapsed_s']}s", flush=True)
    return R


if __name__ == "__main__":
    main()
