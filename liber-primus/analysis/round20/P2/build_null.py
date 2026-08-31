"""Round 20 / P2 -- build nskips_null.json (exact discrete tail, seed 3301, order-preserving)
   + the positive control (plant + recover + on-cipher separation), BOTH tail directions.

The pilot probes established the operative fact this lane must report honestly: on a ciphertext
made by a real rejection loop, the CORRECT key's n_skips can sit on EITHER side of the wrong-key
median depending on (L, supp) -- its genuine footprint grows ~linearly in L while wrong-key
fabrication grows sublinearly, so no single-sided integer bar is valid across L.  We therefore
store the full discrete histogram and report each plant's TWO-SIDED empirical position.

Multiprocessed + incremental (writes nskips_null.json after each section) so a wall-clock cap
never loses completed work.  Seeded from 3301, reproduces exactly on re-run.
"""
import json
import os
import sys
import time
import random
import hashlib
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nskips_lib as NL
from nskips_lib import discrete_tail
import driftbeam as DB

N = 29
KW = {m: {k: v for k, v in NL.PRESET[m].items() if k != "mode"} for m in NL.PRESET}
OUT = os.path.join(HERE, "nskips_null.json")


def _seedhash(tag):
    return int.from_bytes(hashlib.sha256(f"P2|{NL.SEED3301}|{tag}".encode()).digest()[:8], "big")


# -------- worker: a chunk of marginal wrong-key decodes (uniform or shuffle) --------
def _marg_chunk(a):
    L, mode, M, source, seedtag = a
    rng = random.Random(_seedhash(seedtag))
    kw = KW[mode]; ms = kw.get("max_skip", 3); KL = L * (ms + 2) + 64
    uns = NL._unsolved() if source == "shuffle" else None
    out = []
    for _ in range(M):
        if source == "uniform":
            C = [rng.randrange(N) for _ in range(L)]
        else:
            s = rng.randrange(0, len(uns) - L); C = uns[s:s + L][:]; rng.shuffle(C)
        K = [rng.randrange(N) for _ in range(KL)]
        r = NL.decode_preset(C, K, mode, o=0, want_path=False)  # correct beam mode from preset
        out.append(int(r["n_skips"]))
    return out


def _marg(L, mode, M, source, procs, chunk=500):
    jobs = []; k = 0; i = 0
    while k < M:
        t = min(chunk, M - k)
        jobs.append((L, mode, t, source, f"{mode}{L}{source}#{i}")); k += t; i += 1
    acc = []
    with Pool(procs) as p:
        for r in p.imap_unordered(_marg_chunk, jobs):
            acc.extend(r)
    return acc


# -------- worker: one plant cell (plant + recover + on-cipher wrong-key dist) --------
def _plant_cell(a):
    mech, supp, L, reg = a
    M_OC = 1000 if L <= 120 else 300     # L=400 on-cipher decodes are ~28x costlier
    seed = ["LP1_REAL", "LATIN", "OE", "EN_HALFVOWEL", "EN_MODERN"].index(reg)
    C, K, P, gt = NL.plant(reg, L, seed, mech=mech, supp=supp)
    rc = NL.decode_preset(C, K, "keyskip1", o=0, want_path=True)
    rec = DB.recovery(rc["plain_idx"], P)
    rng = random.Random(_seedhash(f"woc{mech}{supp}{L}{reg}"))
    KL = L * (KW["keyskip1"].get("max_skip", 3) + 2) + 64
    woc = []
    for _ in range(M_OC):
        Kw = [rng.randrange(N) for _ in range(KL)]
        r = NL.decode_preset(C, Kw, "keyskip1", o=0, want_path=False)
        woc.append(int(r["n_skips"]))
    n = len(woc)
    cc = rc["n_skips"]
    left = sum(1 for x in woc if x <= cc) / n
    right = sum(1 for x in woc if x >= cc) / n
    return {"mech": mech, "supp": supp, "L": L, "register": reg,
            "gt_nskips": gt, "correct_nskips": cc, "n_unexplained": rc["n_unexplained"],
            "recovery": round(rec, 4), "woc_mean": round(sum(woc) / n, 3),
            "woc_q99": discrete_tail(woc)["q99"], "woc_max": max(woc),
            "p_left": round(left, 4), "p_right": round(right, 4),
            "p_two_sided": round(2 * min(left, right), 4)}


def dump(result):
    result["elapsed_s"] = round(time.time() - result["_t0"], 1)
    r2 = {k: v for k, v in result.items() if not k.startswith("_")}
    json.dump(r2, open(OUT, "w"), indent=1)


def main(procs=6):
    t0 = time.time()
    R = {"v": "P2/nskips_null/1", "seed": NL.SEED3301, "order_preserving": True,
         "fpr": 0.01, "direction": "two-sided (correct-key footprint flips sides with L; "
         "no single-sided integer bar is valid across L -- see plants)",
         "marginal_null": {}, "surrogate_null": {}, "plants": [], "_t0": t0}

    # 1) marginal wrong-key null (general FPR reference). Volumes set to fit the wall-clock
    #    budget given measured cost/decode (keyskip1 L120 1.8ms, L400 51ms; drift L120 54ms,
    #    L400 186ms). Reported M is the exact coverage.
    for mode, L, M in [("keyskip1", 120, 20000), ("keyskip1", 400, 2000),
                       ("drift", 120, 2500), ("drift", 400, 400)]:
        wk = _marg(L, mode, M, "uniform", procs)
        R["marginal_null"][f"{mode}|L{L}"] = discrete_tail(wk)
        c = R["marginal_null"][f"{mode}|L{L}"]
        print(f"[marg] {mode} L={L} M={M}: mean {c['mean']:.2f} q95 {c['q95']} "
              f"q99 {c['q99']} max {c['max']} t={time.time()-t0:.0f}s", flush=True)
        dump(R)

    # 2) order-preserving surrogate control (shuffled real LP2)
    for L, Ms in ((120, 5000), (400, 1500)):
        wk = _marg(L, "keyskip1", Ms, "shuffle", procs)
        c = discrete_tail(wk)
        u = R["marginal_null"][f"keyskip1|L{L}"]["mean"]
        c["mean_ratio_vs_uniform"] = round(c["mean"] / u, 3) if u else None
        R["surrogate_null"][f"keyskip1|L{L}"] = c
        print(f"[surr] keyskip1 L={L}: shuffle-mean {c['mean']:.2f} vs uniform {u:.2f} "
              f"ratio {c['mean_ratio_vs_uniform']} (tol 0.75-1.25) t={time.time()-t0:.0f}s",
              flush=True)
        dump(R)

    # 3) positive control -- register-invariance across 4 cost-registers + EN
    REGS = ["LP1_REAL", "LATIN", "OE", "EN_HALFVOWEL", "EN_MODERN"]
    cells = [(mech, supp, L, reg)
             for mech in ("keyskip", "skip_by_two")
             for supp in (0.60, 0.83, 0.98)
             for L in (120, 400)
             for reg in REGS]
    with Pool(procs) as p:
        for i, row in enumerate(p.imap_unordered(_plant_cell, cells)):
            R["plants"].append(row)
            if (i + 1) % 15 == 0:
                dump(R)
                print(f"[plant] {i+1}/{len(cells)} cells  t={time.time()-t0:.0f}s", flush=True)
    dump(R)
    print(f"WROTE {OUT}  plants={len(R['plants'])}  elapsed {R['elapsed_s']}s", flush=True)
    return R


if __name__ == "__main__":
    main()
