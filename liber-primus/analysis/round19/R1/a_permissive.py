"""R1 / sub-attack A — I1's permissiveness frontier.

Pre-registered in PREREG.md §3. Own instrument (r1_lib.py); nothing here imports I1.

THE QUESTION.  I1 is specified as: "generalise the beam's transition relation to cover
skip_by_two, free drift, and unrepresentable key advances -- WITHOUT losing power on the
baseline construction OR ADMITTING WRONG KEYS."  A drift-tolerant beam searches a strictly
larger hypothesis space per decode.  The failure mode is that a WRONG key, given enough freedom
to skip, is steered toward English-looking output.  Measure where that happens.

    python3 a_permissive.py            # full run -> out_a.json
    python3 a_permissive.py --quick
"""
import json
import math
import os
import random
import statistics as st
import sys
import time
from multiprocessing import Pool

import r1_lib as R

HERE = os.path.dirname(os.path.abspath(__file__))
BEAM_W = 400
L_MAIN = 240
L_ALT = 120
NREP = 7
NULL_N = 200
SEED0 = 19101

# (label, model, max_skip, lam)
CONFIGS = [
    ("exact/ms1", "exact", 1, 0.0),
    ("exact/ms3", "exact", 3, 0.0),
    ("exact/ms8", "exact", 8, 0.0),
    ("by2/ms1", "by2", 1, 0.0),
    ("by2/ms3", "by2", 3, 0.0),
    ("union/ms3", "union", 3, 0.0),
    ("union/ms4", "union", 4, 0.0),
    ("free/ms1", "free", 1, 0.0),
    ("free/ms2", "free", 2, 0.0),
    ("free/ms3", "free", 3, 0.0),
    ("free/ms4", "free", 4, 0.0),
    ("freepen0.25/ms3", "freepen", 3, 0.25),
    ("freepen0.5/ms3", "freepen", 3, 0.5),
    ("freepen1.0/ms3", "freepen", 3, 1.0),
    ("freepen2.0/ms3", "freepen", 3, 2.0),
    ("freepen4.0/ms3", "freepen", 3, 4.0),
]

_REG = None


def regs():
    global _REG
    if _REG is None:
        _REG = R.build_registers()
    return _REG


# --------------------------------------------------------------- correct-key arm
def correct_arm(model, ms, lam, L, plant, nrep=NREP):
    EN = regs()["EN"]
    enc = {"keyskip": R.encipher_keyskip,
           "skip2": R.encipher_skip2,
           "drift": R.encipher_drift}[plant]
    sc, rc, ln = [], [], []
    for rep in range(nrep):
        rng = random.Random(SEED0 + rep * 977 + L)
        s = rng.randrange(0, len(EN) - L - 1)
        P = EN[s:s + L]
        K = R.sha_key(b"CICADA3301" + bytes([rep]), L * 10 + 512)
        if plant == "drift":
            C, _ = enc(P, K, supp=0.83, q=0.05, seed=SEED0 + rep)
        else:
            C, _ = enc(P, K, supp=0.83, seed=SEED0 + rep)
        bd = R.beam_decode(C, K, beam_w=BEAM_W, max_skip=ms, model=model, lam=lam)
        sc.append(bd["score"])
        rc.append(R.recovery(bd["plain_idx"], P))
        ln.append(len(bd["plain_idx"]))
    return {"median_score": st.median(sc), "median_recovery": st.median(rc),
            "min_score": min(sc), "max_score": max(sc),
            "median_decoded_len": st.median(ln), "n": nrep, "scores": sc}


# --------------------------------------------------------------- null arm
def _null_one(args):
    model, ms, lam, L, k = args
    uns = R.unsolved()
    rng = random.Random(70000 + k)
    off = rng.randrange(0, len(uns) - L - 1)
    C = uns[off:off + L]
    K = R.random_key(rng, L * 10 + 512)
    bd = R.beam_decode(C, K, beam_w=BEAM_W, max_skip=ms, model=model, lam=lam)
    return bd["score"]


def null_arm(model, ms, lam, L, n=NULL_N, pool=None):
    args = [(model, ms, lam, L, k) for k in range(n)]
    vals = pool.map(_null_one, args, chunksize=4) if pool else [_null_one(a) for a in args]
    mu, beta = R.gumbel_fit(vals)
    out = {"n": n, "mean": st.mean(vals), "sd": st.pstdev(vals),
           "max": max(vals), "min": min(vals),
           "mu": mu, "beta": beta}
    if mu is not None:
        for nt in (10 ** 4, 10 ** 6, 10 ** 9, 4.3e9):
            out[f"bar_{nt:.0e}"] = R.bar_at(nt, mu, beta)
            out[f"emax_{nt:.0e}"] = R.expected_max(nt, mu, beta)
    return out


def main():
    quick = "--quick" in sys.argv
    cfgs = CONFIGS[:6] if quick else CONFIGS
    nn = 40 if quick else NULL_N
    nrep = 3 if quick else NREP

    out = {"meta": {"beam_w": BEAM_W, "L_main": L_MAIN, "null_n": nn, "nrep": nrep,
                    "seed0": SEED0, "started": time.strftime("%Y-%m-%dT%H:%M:%S")},
           "controls": {}, "frontier": []}

    # ---- pre-registered positive controls (PREREG A.2) -----------------------
    print("== positive controls ==")
    for L in (L_ALT, L_MAIN):
        pc1 = correct_arm("exact", 3, 0.0, L, "keyskip")
        pc2 = correct_arm("exact", 3, 0.0, L, "skip2")
        out["controls"][f"PC-A1_L{L}"] = pc1
        out["controls"][f"PC-A2_L{L}"] = pc2
        print(f"  L={L}  PC-A1 keyskip {pc1['median_score']:.3f} rec {pc1['median_recovery']:.3f}"
              f"   PC-A2 skip2 {pc2['median_score']:.3f} rec {pc2['median_recovery']:.3f}")

    with Pool(6) as pool:
        pc3 = null_arm("exact", 3, 0.0, L_MAIN, n=nn, pool=pool)
        out["controls"]["PC-A3_null_exact_L240"] = pc3
        print(f"  PC-A3 wrong-key null (exact/ms3, real LP2, n={nn}): "
              f"mean {pc3['mean']:.3f} max {pc3['max']:.3f}")

        # ---- the frontier ---------------------------------------------------
        print("\n== frontier ==")
        for (label, model, ms, lam) in cfgs:
            t0 = time.time()
            row = {"label": label, "model": model, "max_skip": ms, "lam": lam,
                   "mean_branching": R.mean_branching(model, ms)}
            for plant in ("keyskip", "skip2", "drift"):
                row[plant] = correct_arm(model, ms, lam, L_MAIN, plant, nrep=nrep)
            row["null"] = null_arm(model, ms, lam, L_MAIN, n=nn, pool=pool)
            row["sec"] = time.time() - t0
            # derived separation numbers
            nb6 = row["null"].get("bar_1e+06")
            row["sep_keyskip_vs_bar1e6"] = (row["keyskip"]["median_score"] - nb6) if nb6 else None
            row["sep_skip2_vs_bar1e6"] = (row["skip2"]["median_score"] - nb6) if nb6 else None
            row["sep_drift_vs_bar1e6"] = (row["drift"]["median_score"] - nb6) if nb6 else None
            out["frontier"].append(row)
            print(f"  {label:18s} branch {row['mean_branching']:5.3f} | "
                  f"keyskip {row['keyskip']['median_score']:7.3f} "
                  f"skip2 {row['skip2']['median_score']:7.3f}(rec {row['skip2']['median_recovery']:.2f}) "
                  f"drift {row['drift']['median_score']:7.3f} | "
                  f"null mean {row['null']['mean']:7.3f} max {row['null']['max']:7.3f} "
                  f"bar1e6 {nb6 if nb6 is None else round(nb6,3)} | {row['sec']:.0f}s")

    # ---- pre-registered triggers -------------------------------------------
    ok_cfgs = []
    for row in out["frontier"]:
        a = row["skip2"]["median_score"] >= -5.5 and row["skip2"]["median_recovery"] >= 0.80
        b = (row["sep_skip2_vs_bar1e6"] is not None and row["sep_skip2_vs_bar1e6"] >= 0.30)
        row["passes_Ai_a"] = a
        row["passes_Ai_b"] = b
        if a and b:
            ok_cfgs.append(row["label"])
    out["A_i_configs_passing"] = ok_cfgs
    out["A_i_verdict"] = "NO-ERROR-FOUND" if ok_cfgs else "FOUND-ERROR"

    base = next(r for r in out["frontier"] if r["label"] == "exact/ms3")
    if ok_cfgs:
        winner = next(r for r in out["frontier"] if r["label"] == ok_cfgs[0])
        d_score = winner["keyskip"]["median_score"] - base["keyskip"]["median_score"]
        d_bar = winner["null"].get("bar_1e+06", 0) - base["null"].get("bar_1e+06", 0)
        out["A_ii"] = {"winner": winner["label"], "delta_baseline_score": d_score,
                       "delta_bar_1e6": d_bar,
                       "verdict": "FOUND-ERROR" if (d_score <= -0.40 or d_bar >= 0.40)
                                  else "NO-ERROR-FOUND"}
    else:
        out["A_ii"] = {"winner": None, "verdict": "N/A (A-i already FOUND-ERROR)"}

    out["meta"]["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(os.path.join(HERE, "out_a.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\nA-i:", out["A_i_verdict"], "passing configs:", ok_cfgs)
    print("A-ii:", out["A_ii"])


if __name__ == "__main__":
    main()
