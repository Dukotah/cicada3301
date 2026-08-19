"""Null distributions and SCALE-CORRECTED thresholds.

The single most common way a large sweep fools its operator is a fixed score threshold.
A bar calibrated on a 200-draw null is not a bar at 10^9 decodes, because the maximum of
N draws from a null grows with N. Sweeping 6 million wrong keys and reporting the best one
as "close" is the null behaving exactly as expected, not a lead.

    max of N draws ~ Gumbel:   E[max] = mu + beta*(ln N + gamma)
    family-wise bar at level a: mu + beta*(ln N - ln(-ln(1-a)))

`threshold_for(n_trials, segment_len)` returns the bar you should actually use.

This module is deliberately small and dependency-free so it can be lifted out of this repo
and used against any similar problem.
"""
import math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis", "round11"))
sys.path.insert(0, os.path.join(LP, "analysis", "campaign18_skip"))

import lib_numchannel as nc
import skipdecode as sk

N = 29
EULER_GAMMA = 0.5772156649015329

# Empirical constants, TAIL-CALIBRATED on this repo's own sweeps (see CALIBRATION below).
DEFAULT_MU = -7.2517      # Gumbel location, L~120 segments, skip-aware beam
DEFAULT_BETA = 0.0725     # Gumbel scale, fitted from real order statistics
FIXED_BAR = -5.5          # the repo's historical confirm threshold

# --- CALIBRATION, and a trap worth knowing about --------------------------------
# The obvious way to get beta is from the null's standard deviation
# (sd = beta*pi/sqrt(6)). For THIS statistic that is wrong by a factor of ~2.5, because
# the beam-decoder score distribution is left-skewed and bounded above: its bulk spread
# says nothing useful about its upper tail.
#
# Fitting instead from two real order statistics at the same segment length --
#   n=200 shuffle null, observed max -6.826   (round13/B04/PREREG.md s5)
#   N=1,385,600 Stage A, observed max -6.185  (round13/B04/results_A.json)
# gives beta = 0.0725, mu = -7.2517.
#
# That fit then PREDICTS, out of sample:
#   Stage B, N=1,290,240 -> predicted -6.190, actually observed -6.129   (0.06 off)
# whereas the bulk-sd estimate (beta=0.1798) would have predicted -4.9, i.e. it would have
# declared the entire Stage-B sweep a hit.
#
# The general lesson: calibrate an extreme-value bar from EXTREME VALUES, never from the
# bulk. If you have no order statistics yet, run a small null at two very different N and
# fit the slope -- it costs minutes and it is the difference between a bar and a fiction.
# --------------------------------------------------------------------------------


def shuffle_null(segment, K, n=200, seed0=3301, beam_w=400, max_skip=3):
    """Histogram-preserving, order-destroying null: the standard control in this repo.

    Shuffling keeps the rune frequencies identical and destroys only the ordering, so a
    score difference cannot be explained by the ciphertext's letter distribution.
    """
    vals = []
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(segment)
        r.shuffle(s)
        vals.append(sk.beam_decode(s, K, sign=-1, o=0,
                                   beam_w=beam_w, max_skip=max_skip)["score"])
    m = sum(vals) / len(vals)
    sd = (sum((x - m) ** 2 for x in vals) / len(vals)) ** 0.5
    return {"mean": m, "max": max(vals), "min": min(vals), "sd": sd,
            "n": n, "values": vals}


def gumbel_params(sd):
    """Gumbel scale from a sample sd (sd = beta*pi/sqrt(6))."""
    return sd * math.sqrt(6) / math.pi


def expected_max(n_trials, mu=DEFAULT_MU, beta=DEFAULT_BETA):
    """Where the best-of-N *wrong* answer is expected to land."""
    if n_trials < 2:
        return mu
    return mu + beta * (math.log(n_trials) + EULER_GAMMA)


def threshold_for(n_trials, segment_len=None, alpha=0.01,
                  mu=DEFAULT_MU, beta=DEFAULT_BETA, floor=FIXED_BAR):
    """THE function to use. Family-wise threshold over n_trials at level alpha.

    Returns the more conservative of (a) the scale-corrected family-wise bar and (b) the
    historical -5.5 floor, because at small N the floor is the binding constraint and at
    large N the correction is.

    >>> round(threshold_for(200), 2) == -5.5           # small sweep: floor binds
    True
    >>> threshold_for(10**9) > threshold_for(10**3)    # bigger sweep, higher bar
    True
    """
    if n_trials < 2:
        return floor
    fw = mu + beta * (math.log(n_trials) - math.log(-math.log(1 - alpha)))
    return max(floor, fw)


def report(n_trials, best_score, mu=DEFAULT_MU, beta=DEFAULT_BETA, alpha=0.01):
    """Human-readable adjudication of a sweep's best score."""
    bar = threshold_for(n_trials, alpha=alpha, mu=mu, beta=beta)
    emax = expected_max(n_trials, mu, beta)
    verdict = "HIT" if best_score >= bar else "NOISE"
    return {
        "n_trials": n_trials, "best_score": best_score,
        "expected_null_max": emax, "threshold": bar, "verdict": verdict,
        "margin_over_expected_null": best_score - emax,
        "explanation": (
            f"With {n_trials:,} trials the best WRONG answer is expected near "
            f"{emax:.3f}. Your best is {best_score:.3f}. "
            + ("That clears the family-wise bar of "
               f"{bar:.3f} — worth escalating."
               if verdict == "HIT" else
               f"The bar is {bar:.3f}. This is the order statistic doing its job, "
               "not a signal.")),
    }


def _measure():
    """Re-derive mu and beta on the real ciphertext, and print them."""
    from plant import make_key
    uns = nc.unsolved()
    print("measuring the null on real LP2 ciphertext...")
    for L in (120, 240, 400):
        K = make_key("otp", length=L + 64, seed=7)
        st = shuffle_null(uns[:L], K, n=120)
        beta = gumbel_params(st["sd"])
        print(f"  L={L:4d}  mean={st['mean']:7.3f}  sd={st['sd']:.4f}  "
              f"max={st['max']:7.3f}  -> beta={beta:.4f}")
        print(f"          threshold_for(1e6)={threshold_for(10**6, mu=st['mean'], beta=beta):.3f}"
              f"  threshold_for(1e9)={threshold_for(10**9, mu=st['mean'], beta=beta):.3f}")


if __name__ == "__main__":
    if "--measure" in sys.argv:
        _measure()
    else:
        print("Scale-corrected thresholds (mu=%.2f beta=%.2f):" % (DEFAULT_MU, DEFAULT_BETA))
        print(f"{'trials':>14}  {'E[null max]':>12}  {'bar (a=0.01)':>13}")
        for n in (200, 10**3, 10**4, 10**5, 10**6, 10**7, 10**8, 10**9, 10**10):
            print(f"{n:>14,}  {expected_max(n):>12.3f}  {threshold_for(n):>13.3f}")
        print()
        print("Sanity check against this repo's real sweeps (out-of-sample predictions):")
        for name, n, obs in (("B04 stage B", 1_290_240, -6.129),
                             ("B04 stage C", 3_548_160, -5.885)):
            print(f"  {name}: N={n:>10,}  predicted E[max]={expected_max(n):7.3f}  "
                  f"observed {obs:7.3f}")
        print()
        print("Read the table this way: for THIS scorer and decoder the tail is tight")
        print("(beta=0.0725), so the historical -5.5 floor stays the binding constraint")
        print("out to ~1e9 trials. That is a measured property, NOT a general one --")
        print("a bulk-sd estimate of beta would have been 2.5x too large and would have")
        print("declared a 1.3M-decode null sweep a hit. Recalibrate for any other")
        print("scorer, decoder or segment length before relying on a bar.")
        print()
        print("Run with --measure to re-derive mu/beta on the live ciphertext.")
