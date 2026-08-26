"""Round 18 / L4-FORCING — Arm A: the literal C-02 uniformity detector.

For each positional subset (line-initial, word-initial, page-initial, ... and two
adjacency controls), test whether its 29-bin rune histogram differs from
  (a) the full-text empirical distribution of all 12,956 runes, and
  (b) the flat uniform distribution (the proposal's literal wording).

p-values are EMPIRICAL, from size-matched resamples of positions drawn without
replacement from the same 12,956 positions. That null is built from the
ciphertext's own model by construction and needs no distributional assumption.

Pre-registered gate: alpha_test = 0.001 / 21 = 4.762e-5  (Bonferroni, 21 tests).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from parse_structure import Geometry  # noqa: E402
from lp.gematria import IDX_TO_TRANS as TRANS  # noqa: E402

ALPHA_TEST = 0.001 / 21
NPERM = 200_000
N = 29


def chisq(counts, expect):
    return float(((counts - expect) ** 2 / expect).sum())


def empirical_p(obs_stat, null_stats):
    """One-sided upper-tail p with the +1 correction (never returns 0)."""
    return (1.0 + np.sum(null_stats >= obs_stat)) / (1.0 + len(null_stats))


def run(seed=3301, nperm=NPERM, verbose=True):
    g = Geometry()
    x = np.array(g.runes, dtype=np.int8)
    n_tot = len(x)
    full_counts = np.bincount(x, minlength=N).astype(float)
    p_full = full_counts / n_tot
    rng = np.random.default_rng(seed)

    results = {}
    for name, pos in g.subsets().items():
        k = len(pos)
        sub = x[np.array(pos)]
        c = np.bincount(sub, minlength=N).astype(float)

        exp_full = p_full * k
        exp_unif = np.full(N, k / N, dtype=float)
        s_full = chisq(c, exp_full)
        s_unif = chisq(c, exp_unif)

        # --- size-matched null over positions -------------------------------
        # Exact: drawing k of the 12,956 positions without replacement makes the
        # 29-bin count vector multivariate hypergeometric in the full-text urn.
        # (Multinomial would be the with-replacement approximation and would
        # overstate the variance by 1/(1-k/n); we use the exact draw.)
        null_full = np.empty(nperm)
        null_unif = np.empty(nperm)
        BLOCK = 50_000
        done = 0
        while done < nperm:
            b = min(BLOCK, nperm - done)
            cc = rng.multivariate_hypergeometric(
                full_counts.astype(np.int64), k, size=b).astype(float)
            null_full[done:done + b] = ((cc - exp_full) ** 2 / exp_full).sum(axis=1)
            null_unif[done:done + b] = ((cc - exp_unif) ** 2 / exp_unif).sum(axis=1)
            done += b

        pf = empirical_p(s_full, null_full)
        pu = empirical_p(s_unif, null_unif)
        # asymptotic cross-check
        try:
            from scipy.stats import chi2
            pf_asym = float(chi2.sf(s_full, N - 1))
            pu_asym = float(chi2.sf(s_unif, N - 1))
        except Exception:
            pf_asym = pu_asym = None

        top = sorted(range(N), key=lambda v: -(c[v] - exp_full[v]))[:3]
        results[name] = {
            "n": k,
            "chi2_vs_fulltext": s_full, "p_empirical_vs_fulltext": pf,
            "p_asymptotic_vs_fulltext": pf_asym,
            "chi2_vs_uniform": s_unif, "p_empirical_vs_uniform": pu,
            "p_asymptotic_vs_uniform": pu_asym,
            "null_max_vs_fulltext": float(null_full.max()),
            "null_mean_vs_fulltext": float(null_full.mean()),
            "verdict": ("HIT" if min(pf, pu) < ALPHA_TEST
                        else "SUBTHRESHOLD" if min(pf, pu) < 0.001 else "NEGATIVE"),
            "largest_excess_runes": [
                {"rune": int(v), "translit": TRANS[v],
                 "obs": int(c[v]), "exp": round(float(exp_full[v]), 2)} for v in top],
            "counts": [int(v) for v in c],
        }
        if verbose:
            r = results[name]
            print(f"{name:22s} n={k:5d}  chi2_full={s_full:8.3f} p={pf:.6g}   "
                  f"chi2_unif={s_unif:8.3f} p={pu:.6g}   {r['verdict']}")
    return results


if __name__ == "__main__":
    nperm = int(sys.argv[1]) if len(sys.argv) > 1 else NPERM
    print(f"Arm A — uniformity of positional subsets   nperm={nperm:,}  "
          f"alpha_test={ALPHA_TEST:.4g}")
    res = run(nperm=nperm)
    out = os.path.join(HERE, "results_armA.json")
    json.dump({"alpha_test": ALPHA_TEST, "nperm": nperm, "tests": res},
              open(out, "w"), indent=2)
    print("wrote", out)
