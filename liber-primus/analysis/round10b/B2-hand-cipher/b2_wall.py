"""B2 lane, Stage 1b — three hardening runs on top of b2_sim.py.

(W1) DRIFT-INVARIANT KEY-LENGTH BOUND from whole-stream IoC.
     For a length-k Vigenere, E[IoC*29] = 1 + (IoC_pt*29 - 1)/k, and this is
     INDEPENDENT of key-phase drift (drift only randomises which of the k key
     runes is used; the marginal symbol distribution is unchanged). So the
     measured whole-stream IoC of LP2 bounds k from BELOW no matter what
     correction habit the author had. Calibrated against an empirical null.

(W2) REPLICATED DETECTION WALL. kappa(k) vs the real stream's own max, 5 reps
     per k, for the most phase-destructive rules. Gives k_max honestly.

(W3) STEELMAN DRIFT SWEEP. Suppose the author drifted the key phase far more
     often than doublets occur (extra random drift rate rho). How large must
     rho be before a k=8 key hides? Reported as the drift rate B2 requires.

Usage: PYTHONUTF8=1 python3 b2_wall.py    Writes results_stage1b.json
"""
import io
import json
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from b2_sim import (load_lp2, load_english_runes, ioc_norm, doublet_rate,  # noqa
                    kappa_spectrum, column_ioc, encipher, N, RAND_KAPPA, sigma)


def encipher_extra_drift(pt, key, p_fix, rho, nout, rng):
    """R2_KEYADV plus an EXTRA random key-phase drift with per-position rate rho."""
    k = len(key)
    out = np.empty(nout, dtype=np.int8)
    j = pi = ph = 0
    prev = -1
    ndrift = 0
    npt = len(pt)
    while j < nout and pi < npt:
        if rng.random() < rho:
            ph += 1
            ndrift += 1
        c = (int(pt[pi]) + int(key[ph % k])) % N
        if c == prev and rng.random() < p_fix:
            tries = 0
            while c == prev and tries < N:
                ph += 1
                ndrift += 1
                tries += 1
                c = (int(pt[pi]) + int(key[ph % k])) % N
        pi += 1
        ph += 1
        out[j] = c
        prev = c
        j += 1
    return out[:j], ndrift


def main():
    rng = random.Random(90210)
    real = load_lp2()
    n = len(real)
    pt = load_english_runes(int(n * 2.2))
    ioc_pt = ioc_norm(pt)
    real_ioc = ioc_norm(real)
    real_spec = kappa_spectrum(real, list(range(2, 401)))
    real_max400 = max(real_spec.values())
    sig = sigma(n)
    out = {"n": n, "ioc29_plaintext": ioc_pt, "ioc29_real": real_ioc,
           "real_kappa_max_2_400": real_max400, "sigma": sig}

    # ---- W1: empirical null for IoC*29 of a uniform-random 29-ary stream at n
    print("W1  drift-invariant key-length bound from whole-stream IoC")
    rs = np.random.RandomState(11)
    nulls = [ioc_norm(rs.randint(0, N, n)) for _ in range(400)]
    mu, sd = float(np.mean(nulls)), float(np.std(nulls, ddof=1))
    hi3 = mu + 3 * sd
    kmin = (ioc_pt - 1.0) / max(hi3 - 1.0, 1e-9)
    print(f"    null IoC*29 over n={n}: mean {mu:.5f} sd {sd:.5f}  (+3sd = {hi3:.5f})")
    print(f"    REAL IoC*29 = {real_ioc:.5f}  ->  z = {(real_ioc-mu)/sd:+.2f}")
    print(f"    English runeglish IoC*29 = {ioc_pt:.4f}")
    print(f"    E[IoC*29 | key length k] = 1 + {ioc_pt-1:.4f}/k")
    for k in (4, 8, 12, 16, 24, 32, 48, 64, 96, 128):
        print(f"      k={k:4d} -> predicted IoC*29 {1+(ioc_pt-1)/k:.4f}  "
              f"z vs null {((1+(ioc_pt-1)/k)-mu)/sd:+8.1f}")
    print(f"    => any key length k < {kmin:.0f} is EXCLUDED at 3sd by IoC alone, "
          f"drift-invariantly.")
    out["W1"] = {"null_ioc_mean": mu, "null_ioc_sd": sd, "null_ioc_hi3sd": hi3,
                 "real_ioc_z": (real_ioc - mu) / sd, "k_min_excluded_below": kmin,
                 "predicted": {k: 1 + (ioc_pt - 1) / k
                               for k in (4, 8, 12, 16, 24, 32, 48, 64, 96, 128)}}

    # ---- W2: replicated detection wall
    print("\nW2  replicated detection wall (5 reps/k)")
    wall = []
    for rule in ("R2_KEYADV", "R3_KEYRESET"):
        for k in (4, 6, 8, 10, 12, 16, 20, 24, 28, 32, 40, 48, 64, 80, 100):
            zs, iocs, doubs = [], [], []
            for _ in range(5):
                key = [rng.randrange(N) for _ in range(k)]
                c, _, _ = encipher(pt, key, rule, 0.82, n, rng)
                kk = kappa_spectrum(c, [k])[k]
                zs.append((kk - real_max400) / sig)
                iocs.append(ioc_norm(c))
                doubs.append(doublet_rate(c))
            rec = {"rule": rule, "k": k, "z_vs_real_max_mean": float(np.mean(zs)),
                   "z_vs_real_max_min": float(np.min(zs)),
                   "ioc29_mean": float(np.mean(iocs)),
                   "doublet_mean": float(np.mean(doubs))}
            wall.append(rec)
            print(f"    {rule:11s} k={k:4d}: kappa(k) z vs real max "
                  f"mean {rec['z_vs_real_max_mean']:+6.1f} min {rec['z_vs_real_max_min']:+6.1f}"
                  f"   IoC*29 {rec['ioc29_mean']:.4f}  doublet {rec['doublet_mean']:.4%}")
    out["W2_wall"] = wall

    # ---- W3: steelman drift sweep at k=8
    print("\nW3  steelman: extra random key-phase drift needed to hide a k=8 key")
    steel = []
    for rho in (0.0, 0.03, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 0.70):
        zs, iocs, doubs, drs = [], [], [], []
        for _ in range(5):
            key = [rng.randrange(N) for _ in range(8)]
            c, nd = encipher_extra_drift(pt, key, 0.82, rho, n, rng)
            kk = kappa_spectrum(c, [8])[8]
            zs.append((kk - RAND_KAPPA) / sigma(len(c)))
            iocs.append(ioc_norm(c))
            doubs.append(doublet_rate(c))
            drs.append(nd / len(c))
        rec = {"rho": rho, "kappa8_z_vs_random_mean": float(np.mean(zs)),
               "ioc29_mean": float(np.mean(iocs)),
               "doublet_mean": float(np.mean(doubs)),
               "total_drift_rate": float(np.mean(drs))}
        steel.append(rec)
        print(f"    rho={rho:.2f}: total drift {rec['total_drift_rate']:.1%}  "
              f"kappa(8) z vs random {rec['kappa8_z_vs_random_mean']:+6.1f}  "
              f"IoC*29 {rec['ioc29_mean']:.4f}  doublet {rec['doublet_mean']:.4%}")
    out["W3_steelman"] = steel

    json.dump(out, io.open(os.path.join(HERE, "results_stage1b.json"), "w",
                           encoding="utf-8"))
    print("\nwrote results_stage1b.json")


if __name__ == "__main__":
    main()
