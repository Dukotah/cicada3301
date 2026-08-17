"""B2 lane, W4 — EMPIRICAL DISTRIBUTION of whole-stream IoC under a short key
with arbitrary phase drift.

W1 gave the expectation argument: E[IoC*29 | key length k] = 1 + (IoC_pt - 1)/k,
drift-invariant.  W4 closes the one loophole in it: an *individual* random key
of length k has a realised IoC that scatters around that expectation (the k
shifts are not perfectly "independent" — English autocorrelation at particular
shift differences can pull the mixture IoC down).  So the honest question is
not "what is the expected IoC" but "what fraction of random length-k keys
produce an IoC as flat as the real LP2 stream (1.00 +/- 3 null sd)?"

Method: for each k, sample many random keys, encipher real English runeglish
with a Bernoulli(rho) key-phase drift (fully vectorised — drift is a monotone
counter, so phase[i] = (i + cumsum(drift)[i]) mod k), and record IoC*29.

The anti-repeat CORRECTION itself is omitted from the vectorised sampler and
its effect measured separately against the exact sequential encipher() from
b2_sim, so the approximation is bounded rather than assumed.

Usage: PYTHONUTF8=1 python3 b2_w4_iocdist.py    Writes results_w4_iocdist.json
"""
import io
import json
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from b2_sim import load_lp2, load_english_runes, ioc_norm, encipher, N  # noqa

KS = [4, 5, 6, 7, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 96, 128, 200, 300,
      400, 500, 600, 800]
NKEY = 400
RHOS = (0.0, 0.03, 0.10, 0.30)


def vec_encipher(pt, key, rho, rs):
    n = len(pt)
    k = len(key)
    if rho > 0:
        drift = np.cumsum(rs.random_sample(n) < rho)
    else:
        drift = 0
    phase = (np.arange(n) + drift) % k
    return (pt.astype(np.int64) + np.asarray(key, dtype=np.int64)[phase]) % N


def main():
    rs = np.random.RandomState(777)
    rng = random.Random(777)
    real = load_lp2()
    n = len(real)
    real_ioc = ioc_norm(real)
    pt = load_english_runes(n).astype(np.int64)
    ioc_pt = ioc_norm(pt)

    nulls = [ioc_norm(rs.randint(0, N, n)) for _ in range(400)]
    mu, sd = float(np.mean(nulls)), float(np.std(nulls, ddof=1))
    lo, hi = mu - 3 * sd, mu + 3 * sd
    print(f"n={n}  real IoC*29={real_ioc:.5f}  uniform null {mu:.5f}+/-{sd:.5f}"
          f"  -> flatness window [{lo:.5f}, {hi:.5f}]")
    print(f"English runeglish plaintext IoC*29 = {ioc_pt:.4f}\n")

    out = {"n": n, "real_ioc29": real_ioc, "null_mean": mu, "null_sd": sd,
           "window": [lo, hi], "ioc_pt": ioc_pt, "nkey": NKEY, "rows": []}

    print(f"{'k':>5} {'rho':>5} {'mean':>8} {'sd':>8} {'min':>8} "
          f"{'pred':>8} {'#in window':>11}")
    for k in KS:
        for rho in RHOS:
            vals = np.empty(NKEY)
            for t in range(NKEY):
                key = rs.randint(0, N, k)
                vals[t] = ioc_norm(vec_encipher(pt, key, rho, rs))
            nin = int(np.sum((vals >= lo) & (vals <= hi)))
            pred = 1 + (ioc_pt - 1) / k
            print(f"{k:5d} {rho:5.2f} {vals.mean():8.5f} {vals.std(ddof=1):8.5f} "
                  f"{vals.min():8.5f} {pred:8.5f} {nin:6d}/{NKEY}")
            out["rows"].append({"k": k, "rho": rho, "mean": float(vals.mean()),
                                "sd": float(vals.std(ddof=1)),
                                "min": float(vals.min()),
                                "max": float(vals.max()),
                                "predicted": pred, "n_in_window": nin,
                                "nkey": NKEY})

    # ---- bound the vectorised approximation: exact sequential encipher WITH
    #      the R2_KEYADV anti-repeat correction, same k, 20 keys each.
    print("\nexact sequential check (R2_KEYADV correction, p_fix 0.82, 20 keys):")
    pt_long = load_english_runes(int(n * 2.2))
    chk = []
    for k in (4, 8, 12, 24, 48, 96):
        seq, vec = [], []
        for _ in range(20):
            key = [rng.randrange(N) for _ in range(k)]
            c, _, _ = encipher(pt_long, key, "R2_KEYADV", 0.82, n, rng)
            seq.append(ioc_norm(c))
            vec.append(ioc_norm(vec_encipher(pt, key, 0.03, rs)))
        rec = {"k": k, "seq_mean": float(np.mean(seq)),
               "vec_mean": float(np.mean(vec)),
               "seq_min": float(np.min(seq)),
               "delta": float(np.mean(seq) - np.mean(vec))}
        chk.append(rec)
        print(f"  k={k:3d}: sequential-with-correction {rec['seq_mean']:.5f} "
              f"(min {rec['seq_min']:.5f})   vectorised {rec['vec_mean']:.5f}   "
              f"delta {rec['delta']:+.5f}")
    out["exact_check"] = chk

    # ---- smallest k for which ANY sampled key landed in the flatness window
    hits = [r["k"] for r in out["rows"] if r["n_in_window"] > 0]
    out["smallest_k_with_any_flat_key"] = min(hits) if hits else None
    print(f"\nsmallest k with ANY key inside the real stream's flatness window: "
          f"{out['smallest_k_with_any_flat_key']}")

    json.dump(out, io.open(os.path.join(HERE, "results_w4_iocdist.json"), "w",
                           encoding="utf-8"))
    print("wrote results_w4_iocdist.json")


if __name__ == "__main__":
    main()
