"""Round 18 / L4-FORCING — POSITIVE CONTROL and POWER CURVE.

Round 18 rule 2: a null from an unvalidated instrument is not a negative. This script
plants forcing at a known strength and measures at what strength each detector stops
firing. The curve, not the null, is what makes this lane's negative mean anything.

Generative model (H0), fitted rather than assumed:
  * uniform draws over 29 runes,
  * a MEMORYLESS, UNSCOPED, LAG-1 anti-repeat rejection filter at s = 0.8075
    (round17/D-01: every richer human-randomness model is excluded at >=0.99 power),
  * LP2's real separator pattern, laid out by the greedy line-breaker and fitted glyph
    widths recovered in confound_layout.py -- so the synthetic carries the SAME
    inspection-paradox size bias at line-initial position that the real book does.
    Without that the control would be measuring power against a straw null.

Two forcing mechanisms, because they leave different signatures (PREREG.md section 1):
  M1 "assign"      : write the wanted rune unconditionally.
                     Where it collides with the previous rune it creates a doublet,
                     so this mechanism is visible to Arm C as an EXCESS.
  M2 "filter-wins" : write the wanted rune unless it collides, in which case the
                     anti-repeat predicate wins and the natural draw stays.
                     Doublet rate at the boundary is untouched: Arm C cannot see it.

Detectors measured:
  D_flat   Arm A chi-square of line initials vs the full-text distribution, judged
           against the FLAT size-matched null. This is the literal C-02 detector and
           it is CONFOUNDED by typography -- its power is reported to show how large
           the confound's contribution is, not because it should be used.
  D_layout the same statistic judged against the LAYOUT-AWARE null. This is the
           honest detector after the confound analysis, and its f80 is the number
           that bounds this lane's negative.
  D_C1     Arm C's doublet-rate-by-line-position G^2.
  D_B1     Arm B's family-max English score on the 594-rune line-initial sequence,
           which additionally requires the forced content to BE a message.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LP = os.path.join(ROOT, "liber-primus")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp  # noqa: E402
from parse_structure import Geometry  # noqa: E402
import confound_layout as CL  # noqa: E402
import armB_message as B  # noqa: E402

N = 29
S_FILTER = 0.8075
ALPHA_TEST = 0.001 / 21
FGRID = [1.00, 0.80, 0.60, 0.40, 0.30, 0.20, 0.10, 0.05, 0.00]
PHRASE = ("THEPRIMESARESACREDTOTALLYWITHINTHEDEEPWEBTHEREEXISTSAMAPTHATISNOTAMAP"
          "ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHATISNOTAPAGEBELIEVENOTHING")


# ------------------------------------------------------------------ generator
def gen_filtered(n, rng):
    """Uniform runes under a memoryless lag-1 anti-repeat rejection filter."""
    u = rng.integers(0, N, size=n + 64)
    v = rng.random(n + 64)
    w = rng.integers(0, N - 1, size=n + 64)
    out = np.empty(n, dtype=np.int16)
    prev = -1
    for i in range(n):
        c = u[i]
        if c == prev and v[i] < S_FILTER:
            c = w[i]
            if c >= prev:
                c += 1
        out[i] = c
        prev = c
    return out


def validate_generator(rng, n=12956, reps=20):
    d, ioc = [], []
    for _ in range(reps):
        x = gen_filtered(n, rng)
        d.append(float(np.mean(x[1:] == x[:-1])))
        c = np.bincount(x, minlength=N)
        ioc.append(float(N * (c * (c - 1)).sum() / (n * (n - 1))))
    return {"doublet_rate_mean": float(np.mean(d)), "doublet_rate_sd": float(np.std(d)),
            "LP2_doublet_rate": 86 / 12955, "IoC_times_N_mean": float(np.mean(ioc)),
            "LP2_IoC_times_N": 1.000}


# ------------------------------------------------------------------ layout
def make_stream(rng, widths, budget, sep_pattern):
    """Synthetic token stream with LP2's separator pattern, laid out by the same
    greedy line-breaker, so it carries the same size bias at line-initial position."""
    n_runes = int((np.asarray(sep_pattern) < N).sum())
    runes = gen_filtered(n_runes, rng)
    toks, k = [], 0
    for t in sep_pattern:
        if t < N:
            toks.append(int(runes[k])); k += 1
        else:
            toks.append(int(t))
    lines = CL.reflow(toks, widths, budget)
    return lines


def line_slots(lines):
    """(flat rune array, index of each line's first rune, index of each line's last)"""
    flat, first, last = [], [], []
    for L in lines:
        rs = [t for t in L if t < N]
        if not rs:
            continue
        first.append(len(flat))
        flat.extend(rs)
        last.append(len(flat) - 1)
    return np.array(flat, dtype=np.int16), np.array(first), np.array(last)


# ------------------------------------------------------------------ statistics
def chi2_initials(flat, first, p_ref):
    vals = flat[first]
    c = np.bincount(vals, minlength=N).astype(float)
    e = p_ref * len(first)
    return float(((c - e) ** 2 / e).sum())


def g2_c1(flat, first):
    """Arm C's C1 on a synthetic stream: doublets at the line boundary vs interior."""
    n = len(flat)
    is0 = np.zeros(n, dtype=bool)
    is0[first[first > 0]] = True
    d = flat[1:] == flat[:-1]
    b = is0[1:]
    k0, n0 = int(d[b].sum()), int(b.sum())
    k1, n1 = int(d[~b].sum()), int((~b).sum())
    tot, ntot = k0 + k1, n0 + n1
    if tot == 0:
        return 0.0
    p = tot / ntot
    g = 0.0
    for k, nn in ((k0, n0), (k1, n1)):
        for obs, exp in ((k, nn * p), (nn - k, nn * (1 - p))):
            if obs > 0:
                g += 2 * obs * math.log(obs / exp)
    return float(g)


def force(flat, first, msg, f, mech, rng):
    """Force a fraction f of line initials to the message; return a modified copy."""
    y = flat.copy()
    m = len(first)
    k = int(round(f * m))
    if k == 0:
        return y
    which = rng.choice(m, k, replace=False)
    for j in which:
        i = int(first[j])
        tgt = int(msg[j % len(msg)])
        if mech == "M1_assign":
            y[i] = tgt
        else:  # M2_filter_wins
            if i == 0 or y[i - 1] != tgt:
                y[i] = tgt
    return y


def gamma_isf(sample, alpha):
    """Tail critical value from a moment-matched gamma (the layout null is a shifted,
    right-skewed chi-square-like statistic; 2,000 draws cannot resolve 4.8e-5 directly)."""
    m, v = float(np.mean(sample)), float(np.var(sample))
    if v <= 0:
        return float(m)
    try:
        from scipy.stats import gamma
        return float(gamma.isf(alpha, a=m * m / v, scale=v / m))
    except Exception:
        return float(np.quantile(sample, 1 - alpha))


# ------------------------------------------------------------------ main
def main(n_base=200, n_null=2000, seed=90210):
    rng = np.random.default_rng(seed)
    g = Geometry()
    lines_real = CL.token_lines()
    mask = CL.full_line_mask(lines_real)
    widths, M = CL.fit_widths(lines_real, use=mask)
    budget = float(np.median(M[mask] @ widths))
    sep_pattern = [t for _, L in lines_real for t in L]

    gv = validate_generator(np.random.default_rng(7))
    print("generator validation:", json.dumps(gv))

    msg = gp.keyword_to_indices(PHRASE)
    while len(msg) < 700:
        msg = msg + msg

    # ---- null distributions (f = 0) -------------------------------------
    p_ref = np.full(N, 1.0 / N)
    print(f"building layout-aware null on synthetic streams (n={n_null}) ...", flush=True)
    null_layout = np.empty(n_null)
    null_c1 = np.empty(n_null)
    for i in range(n_null):
        lines = make_stream(rng, widths, budget, sep_pattern)
        flat, first, last = line_slots(lines)
        pr = np.bincount(flat, minlength=N) / len(flat)
        null_layout[i] = chi2_initials(flat, first, pr)
        null_c1[i] = g2_c1(flat, first)
        if (i + 1) % 250 == 0:
            print(f"  null {i + 1}/{n_null}", flush=True)

    try:
        from scipy.stats import chi2 as _c2
        crit_flat = float(_c2.isf(ALPHA_TEST, N - 1))
        crit_flat_001 = float(_c2.isf(0.001, N - 1))
    except Exception:
        crit_flat = 68.0; crit_flat_001 = 56.9
    crit_layout = gamma_isf(null_layout, ALPHA_TEST)
    crit_layout_001 = gamma_isf(null_layout, 0.001)
    crit_c1 = gamma_isf(null_c1, ALPHA_TEST)

    print(f"critical values @ alpha={ALPHA_TEST:.3g}: "
          f"D_flat {crit_flat:.2f}   D_layout {crit_layout:.2f} "
          f"(null mean {null_layout.mean():.2f} sd {null_layout.std():.2f})   "
          f"D_C1 {crit_c1:.2f}", flush=True)

    # ---- base streams reused across every (f, mechanism) cell ------------
    print(f"generating {n_base} base streams ...", flush=True)
    bases = []
    for i in range(n_base):
        lines = make_stream(rng, widths, budget, sep_pattern)
        bases.append(line_slots(lines))
    print("  done", flush=True)

    out = {"alpha_test": ALPHA_TEST, "n_base": n_base, "n_null": n_null,
           "generator_validation": gv,
           "critical_values": {"D_flat": crit_flat, "D_flat_at_0.001": crit_flat_001,
                               "D_layout": crit_layout, "D_layout_at_0.001": crit_layout_001,
                               "D_C1": crit_c1,
                               "layout_null_mean": float(null_layout.mean()),
                               "layout_null_sd": float(null_layout.std()),
                               "c1_null_mean": float(null_c1.mean())},
           "curve": []}

    for mech in ("M1_assign", "M2_filter_wins"):
        for f in FGRID:
            hits = {"D_flat": 0, "D_layout": 0, "D_C1": 0}
            b1 = []
            for bi, (flat, first, last) in enumerate(bases):
                y = force(flat, first, msg, f, mech, rng)
                pr = np.bincount(y, minlength=N) / len(y)
                st = chi2_initials(y, first, pr)
                if st > crit_flat:
                    hits["D_flat"] += 1
                if st > crit_layout:
                    hits["D_layout"] += 1
                if g2_c1(y, first) > crit_c1:
                    hits["D_C1"] += 1
                if bi < 20:
                    b1.append(B.family_max([y[first].tolist()])[0][0])
            row = {"mechanism": mech, "f": f,
                   "power_D_flat": hits["D_flat"] / len(bases),
                   "power_D_layout": hits["D_layout"] / len(bases),
                   "power_D_C1": hits["D_C1"] / len(bases),
                   "armB_B1_best_mean": float(np.mean(b1)), "armB_B1_best_max": float(np.max(b1))}
            out["curve"].append(row)
            print(f"  {mech:15s} f={f:.2f}  D_flat={row['power_D_flat']:.3f} "
                  f"D_layout={row['power_D_layout']:.3f} D_C1={row['power_D_C1']:.3f} "
                  f"B1max={row['armB_B1_best_max']:.3f}", flush=True)
            json.dump(out, open(os.path.join(HERE, "results_power.json"), "w"), indent=2)

    # f80 per detector per mechanism
    f80 = {}
    for mech in ("M1_assign", "M2_filter_wins"):
        for det in ("power_D_flat", "power_D_layout", "power_D_C1"):
            ok = [r["f"] for r in out["curve"] if r["mechanism"] == mech and r[det] >= 0.80]
            f80[f"{mech}/{det}"] = min(ok) if ok else None
    out["f80"] = f80
    json.dump(out, open(os.path.join(HERE, "results_power.json"), "w"), indent=2)
    print("f80:", json.dumps(f80))
    print("wrote results_power.json")


if __name__ == "__main__":
    main(n_base=int(sys.argv[1]) if len(sys.argv) > 1 else 200,
         n_null=int(sys.argv[2]) if len(sys.argv) > 2 else 2000)
