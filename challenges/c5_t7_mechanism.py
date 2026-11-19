"""C5 checker: propose a generator that reproduces the T7 doublet anomaly (CHALLENGES.md, C5).

    python challenges/c5_t7_mechanism.py                                       # flat filter baseline
    python challenges/c5_t7_mechanism.py my_generator.py --draws 500           # your submission

Your file defines   generate(rng, page) -> int array of length 12,956, values 0-28
where rng is a numpy Generator and page is the segment index of each position (0-54),
in case your mechanism works per page or per session. Return a ciphertext-like stream:
the checker only looks at where adjacent runes repeat (doublet sites) and their values.

It computes the registered R44 W2-B3 battery (liber-primus/analysis/round44/W2-B3-doublet-sites)
on the real unsolved stream and on each of your draws, and reports where the real value
falls in your model's distribution. A mechanism FITS when every statistic's two-sided p is
at least 0.05. The flat filter (the old D-01 model) fits everything except T7, which is
the anomaly to explain.

Rules (CHALLENGES.md): at most 5 free parameters, named in your submission; the generator
may not read the LP2 stream, its doublet positions or its gaps.
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

sys.path.insert(0, os.path.join(C.LP, "analysis", "round44", "W2-B3-doublet-sites"))
import b3lib as B  # noqa: E402

STATS = [("n_sites", "doublet sites"), ("T1_ks", "position KS"), ("T2_gapcv2", "gap CV^2"),
         ("T3_chi2_mod29", "chi2 pos mod 29"), ("T4_chi2_mod60", "chi2 pos mod 60"),
         ("T6_dispersion", "per-page dispersion"), ("T7_gap_ac1", "lag-1 gap autocorr (T7)")]


def flat_filter(rng, page, keep_repeat=86 / 447):
    """D-01's model: uniform runes, an anti-repeat filter that lets a fixed fraction of repeats
    through. 447 is the expected doublet count with no filter (12,955 / 29); 86 are observed.
    One free parameter: keep_repeat."""
    n = len(page)
    x = np.empty(n, dtype=np.int64)
    x[0] = rng.integers(C.N)
    draws = rng.integers(C.N, size=n)
    keep = rng.random(n) < keep_repeat
    alt = rng.integers(C.N - 1, size=n)
    for i in range(1, n):
        v = draws[i]
        if v == x[i - 1] and not keep[i]:
            v = alt[i] if alt[i] < x[i - 1] else alt[i] + 1
        x[i] = v
    return x


def stats(x, page):
    s = B.battery_stats(x, page, B.N_PAGES_U, len(x))
    s["n_sites"] = float(len(B.sites(x)))
    return s


def simulate(gen, page, draws, seed, shape):
    rng = np.random.default_rng(seed)
    sims = []
    for _ in range(draws):
        y = np.asarray(gen(rng, page), dtype=np.int64)
        assert y.shape == shape and y.min() >= 0 and y.max() < C.N, "bad stream shape or values"
        sims.append(stats(y, page))
    return sims


def evidence(sims, obs, scale):
    """Kernel estimate of the model's density at the real statistics (ABC, Gaussian kernel,
    bandwidth 1 in units of the flat model's spread). A vague model that spreads its draws
    widely 'fits' every statistic but scores low here; a sharp one that lands on the real
    values scores high."""
    keys = [k for k, _ in STATS]
    d2 = np.array([sum(((s[k] - obs[k]) / scale[k]) ** 2 for k in keys) for s in sims])
    return float(np.mean(np.exp(-d2 / 2)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("submission", nargs="?", help=".py defining generate(rng, page)")
    ap.add_argument("--draws", type=int, default=300)
    ap.add_argument("--seed", type=int, default=3301)
    a = ap.parse_args()

    gen = C.load_module(a.submission).generate if a.submission else flat_filter
    x, page = C.unsolved_stream()
    obs = stats(x, page)
    sims = simulate(gen, page, a.draws, a.seed, x.shape)
    flat = sims if gen is flat_filter else simulate(flat_filter, page, a.draws, a.seed + 1, x.shape)
    scale = {k: float(np.std([s[k] for s in flat])) for k, _ in STATS}

    print(f"C5 - {a.submission or 'flat filter baseline (D-01 model)'}, {a.draws} draws\n")
    print(f"{'statistic':28s} {'real':>9} {'model median':>13} {'model 2.5-97.5%':>20} {'p (2-sided)':>12}")
    fits = True
    for key, label in STATS:
        v = np.array([s[key] for s in sims])
        lo, med, hi = np.percentile(v, [2.5, 50, 97.5])
        p = min(1.0, 2 * min((np.sum(v >= obs[key]) + 1), (np.sum(v <= obs[key]) + 1)) / (len(v) + 1))
        fits &= p >= 0.05
        print(f"{label:28s} {obs[key]:9.3f} {med:13.3f} {f'[{lo:.3f}, {hi:.3f}]':>20} {p:12.3f}"
              + ("" if p >= 0.05 else "   <- misfit"))
    print("\nFITS all statistics" if fits else "\nDOES NOT FIT (see misfits)")
    ev, ev_flat = evidence(sims, obs, scale), evidence(flat, obs, scale)
    ratio = ev / ev_flat if ev_flat > 0 else float("inf")
    print(f"evidence ratio vs flat filter: {ratio:.2f}   (flat = 1 by definition; the scored number)")
    sys.exit(0 if fits else 1)


if __name__ == "__main__":
    main()
