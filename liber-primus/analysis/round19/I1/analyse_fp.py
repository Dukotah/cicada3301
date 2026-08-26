"""Round 19 / I1 -- turn the wrong-key samples into an EXTREME-VALUE bar for each mode.

`benchmark/null.py` carries a warning this lane obeys: for the beam score, the bulk sd
under-states the tail by ~2.5x, so a Gumbel scale must be fitted from ORDER STATISTICS,
not from the sd.  Here that is done inside each sample by block maxima at two block sizes:

    E[max of b draws] = mu + beta*(ln b + gamma)
    => beta = (m_b2 - m_b1) / ln(b2/b1),   mu = m_b1 - beta*(ln b1 + gamma)

The output is the handoff I3 needs: per decoder mode, the (mu, beta) of ITS null and the
family-wise bar that null implies at 10^6 / 10^9 decodes.  A permissive decoder does not
merely shift the mean; it re-scales the tail, and a sweep that keeps using the -5.5 floor
after switching decoder is reading a bar that no longer belongs to its instrument.

    python3 analyse_fp.py
"""
import os
import sys
import json
import math
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
GAMMA = 0.5772156649015329


def blockmax(v, b, reps=40, seed=11):
    """Mean of block maxima over `reps` random partitions into blocks of size b."""
    r = random.Random(seed)
    acc = []
    for _ in range(reps):
        w = list(v)
        r.shuffle(w)
        nb = len(w) // b
        for k in range(nb):
            acc.append(max(w[k * b:(k + 1) * b]))
    return statistics.fmean(acc), len(acc)


def fit(v):
    n = len(v)
    b1 = 10 if n < 1000 else 20
    b2 = min(n // 4, 200)
    m1, _ = blockmax(v, b1)
    m2, _ = blockmax(v, b2)
    beta = (m2 - m1) / math.log(b2 / b1)
    mu = m1 - beta * (math.log(b1) + GAMMA)
    return {"b1": b1, "b2": b2, "m_b1": m1, "m_b2": m2, "mu": mu, "beta": beta,
            "bulk_mean": statistics.fmean(v), "bulk_sd": statistics.pstdev(v),
            "beta_from_bulk_sd": statistics.pstdev(v) * math.sqrt(6) / math.pi,
            "observed_max": max(v), "n": n}


def emax(mu, beta, N):
    return mu + beta * (math.log(N) + GAMMA)


def fwbar(mu, beta, N, alpha=0.01):
    return mu + beta * (math.log(N) - math.log(-math.log(1 - alpha)))


def main():
    rows = []
    for f in ("out_fp_deep.json", "out_fp_deep2.json", "out_fp_curve.json"):
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            rows.extend(json.load(open(p))["rows"])
    if not rows:
        print("no G-FP output yet")
        return
    keys = sorted({(r["null"], r["mode"]) for r in rows})
    out = []
    print(f"{'null':6s} {'mode':11s} {'n':>5s} {'mu':>8s} {'beta':>7s} "
          f"{'obs max':>8s} {'E[max] 1e6':>11s} {'bar 1e6':>9s} {'bar 1e9':>9s}")
    for (nu, m) in keys:
        v = [r["score"] for r in rows if r["null"] == nu and r["mode"] == m]
        sk = [r["n_skips"] for r in rows if r["null"] == nu and r["mode"] == m]
        f = fit(v)
        rec = {"null": nu, "mode": m, **f,
               "mean_n_skips": statistics.fmean(sk),
               "E_max_1e6": emax(f["mu"], f["beta"], 1e6),
               "E_max_1e9": emax(f["mu"], f["beta"], 1e9),
               "fw_bar_1e6": fwbar(f["mu"], f["beta"], 1e6),
               "fw_bar_1e9": fwbar(f["mu"], f["beta"], 1e9)}
        out.append(rec)
        print(f"{nu:6s} {m:11s} {f['n']:5d} {f['mu']:8.3f} {f['beta']:7.4f} "
              f"{f['observed_max']:8.3f} {rec['E_max_1e6']:11.3f} "
              f"{rec['fw_bar_1e6']:9.3f} {rec['fw_bar_1e9']:9.3f}")
    json.dump({"lane": "round19/I1", "what": "extreme-value fit of the wrong-key null "
                                             "per decoder mode",
               "method": "block maxima at two block sizes (see benchmark/null.py "
                         "CALIBRATION: never fit beta from the bulk sd)",
               "fits": out},
              open(os.path.join(HERE, "out_fp_tail.json"), "w"), indent=1)
    print("\nwrote out_fp_tail.json")


if __name__ == "__main__":
    main()
