"""Round 16 lane P4 -- CONTROLS and POWER.

AGENTS.md lesson 1: "A null from an unvalidated instrument is not a negative. Plant a
known signal and prove your machinery recovers it BEFORE you trust its silence."

So before any statement about the real ciphertext, this module builds matched synthetic
streams and measures, for every statistic in `fingerprint.measure`, how well it separates
them at the real sample size n=12,956:

  (c) UNIFORM      -- iid uniform over 29 runes, no filter.        [negative control]
  (a) MACHINE      -- `skipdecode.encipher_keyskip` on a uniform plaintext under a
                      uniform keystream: the coded model `if c == c_prev: redraw`
                      (key-skip) with suppression calibrated so the emitted doublet
                      rate equals the real 0.6638%.                [hypothesis A]
  (a2) MACHINE/LINE -- the same coded filter but SCOPED TO A LINE: c_prev resets at each
                      line break, so the check is lost across a line turn. This is the
                      "a person checking the rune they just wrote" implementation and it
                      exists to prove test 5 (placement) has any power at all.
  (b) HAND         -- human-generated randomness: recency avoidance at lags 1..3 plus
                      short-window frequency rebalancing. Lag-1 avoidance is calibrated
                      to the SAME 0.6638% doublet rate as (a), so the lag-1 rate itself
                      carries no information and the battery is forced to work on the
                      structure the two models genuinely differ on.

The HAND model follows the empirical literature on human "random" production
(Wagenaar 1972, Psych. Bull. 77:65; Rapoport & Budescu 1997, Psych. Rev. 104:603):
people under-produce repetitions, avoid symbols used in the recent past (not just the
immediately preceding one), and rebalance symbol frequencies inside short windows.
Because the size of the lag-2/3 bleed is not pinned down for a 29-symbol alphabet, the
lane runs a LADDER of hand models (`HAND_LADDER`) from a barely-there bleed to a strong
one, and reports which rungs the data excludes. That converts a yes/no argument into a
measured bound.

Run:  PYTHONUTF8=1 python controls.py           (writes results.json)
      PYTHONUTF8=1 python controls.py --reps 50 (quick)
"""
import os, sys, json, math, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # liber-primus/
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))
sys.path.insert(0, HERE)

import fingerprint as F                                   # noqa: E402
from skipdecode import encipher_keyskip                   # noqa: E402

N = F.N
Q = F.Q
TARGET_DOUBLET = 86 / 12955.0          # the measured real rate, 0.663836%

# --------------------------------------------------------------- generators
def gen_uniform(n, rng, st=None):
    return rng.integers(0, N, size=n)


def gen_machine(n, rng, st=None, supp=0.813):
    """(a) The coded filter, via the project's own `encipher_keyskip`.
    Uniform plaintext, uniform keystream -> uniform ciphertext, then the key-skip
    anti-repeat rule. Identical mechanism to the one Campaign XVIII/Round 16 assume."""
    P = list(rng.integers(0, N, size=n))
    K = list(rng.integers(0, N, size=n * 6 + 64))
    C, _, _ = encipher_keyskip(P, K, sign=-1, supp=supp, seed=int(rng.integers(1 << 30)))
    return np.asarray(C, dtype=np.int64)


def gen_machine_lines(n, rng, st, supp=0.813):
    """(a2) The same rule but scoped to a line: the "check the rune you just wrote"
    implementation, which cannot see across a line break."""
    line = st["line"]
    x = np.empty(n, dtype=np.int64)
    r = rng.random(n * 2)
    u = rng.integers(0, N, size=n * 2)
    j = 0
    prev = -1
    for i in range(n):
        if i > 0 and line[i] != line[i - 1]:
            prev = -1                              # scope reset at the line turn
        while True:
            c = u[j]; p = r[j]; j += 1
            if j >= len(u) - 2:
                u = np.concatenate([u, rng.integers(0, N, size=n)])
                r = np.concatenate([r, rng.random(n)])
            if c == prev and p < supp:
                continue
            break
        x[i] = c; prev = c
    return x


def gen_hand(n, rng, st=None, a1=1.68, a2=0.0, a3=0.0, beta=0.0, W=58):
    """(b) Human-generated randomness.

    P(next = s) proportional to exp(-a1*[s==x_{i-1}] - a2*[s==x_{i-2}] - a3*[s==x_{i-3}]
                                   - beta*(count_W(s) - W/29)/sqrt(W/29))
    a1  lag-1 repetition avoidance (calibrated to the real doublet rate)
    a2,a3  the recency bleed that a rule-following hand cannot avoid producing
    beta   the "that rune has come up too often lately" rebalancing reflex
    """
    x = np.empty(n, dtype=np.int64)
    logw = np.zeros(N)
    cnt = np.zeros(N)
    sq = math.sqrt(W / N)
    buf = rng.random(n)
    for i in range(n):
        lw = np.zeros(N)
        if i >= 1: lw[x[i - 1]] -= a1
        if i >= 2: lw[x[i - 2]] -= a2
        if i >= 3: lw[x[i - 3]] -= a3
        if beta:
            lw -= beta * (cnt - W / N) / sq
        w = np.exp(lw - lw.max())
        cw = np.cumsum(w)
        v = int(np.searchsorted(cw, buf[i] * cw[-1]))
        if v >= N: v = N - 1
        x[i] = v
        cnt[v] += 1
        if i >= W:
            cnt[x[i - W]] -= 1
    return x


# ------------------------------------------------------- calibration
def _doublet_rate(x):
    return float((x[1:] == x[:-1]).mean())


def calibrate(fn, lo, hi, target=TARGET_DOUBLET, reps=8, n=12956, seed=77, st=None,
              key="supp"):
    """Bisect one parameter of a generator so its emitted doublet rate hits `target`.
    Fairness requirement: the MACHINE and HAND controls must agree with the real data
    AND with each other on lag 1, or every downstream 'discrimination' is really just
    a restatement of the lag-1 rate."""
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        rng = np.random.default_rng(seed)
        r = np.mean([_doublet_rate(fn(n, rng, st, **{key: mid})) for _ in range(reps)])
        if r > target:
            lo = mid            # need more suppression
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------- ladder
# rung name -> (a2, a3, beta).  a1 is calibrated per rung.
HAND_LADDER = [
    ("hand_bleed_none",   dict(a2=0.00, a3=0.00, beta=0.00)),   # == machine pad + a human eye
                                                                #    applying ONLY the lag-1 check
    ("hand_bleed_tiny",   dict(a2=0.05, a3=0.02, beta=0.05)),
    ("hand_bleed_small",  dict(a2=0.10, a3=0.05, beta=0.10)),
    ("hand_bleed_mid",    dict(a2=0.25, a3=0.12, beta=0.20)),
    ("hand_bleed_strong", dict(a2=0.50, a3=0.25, beta=0.40)),
    ("hand_rebalance_only", dict(a2=0.00, a3=0.00, beta=0.40)),  # isolates D-01 test 3
]


# --------------------------------------------- PRE-REGISTERED decision rules
# Fixed before the 200-rep run; see RESULTS.md section 1.
PRIMARY = ["bleed28_z",             # test 1  -- lag-2..8 bleed (the machine/hand split)
           "chi2W58_mean",          # test 3  -- D-01's windowed under-dispersion sweep
           "gap_cv",                # test 2  -- repeat-gap shape
           "page_rate_dispersion"]  # test 6  -- constancy of the suppression rate
SECONDARY = ["lag2_z", "lag3_z", "bleed23_z", "gap_2to4_z", "abab_z",
             "chi2W29_mean", "chi2W116_mean", "chi2W290_mean",
             "page_homog_z", "half_split_z", "supp_drift_z",
             "dbl_line_cross_z", "dbl_page_cross_z", "dbl_posinpage_ks",
             "dbl_posinline_ks", "dbl_gap_disp", "dbl_interrupter_z",
             "bigram_offdiag_z"]
POWER_FLOOR = 0.80        # a statistic below this is UNDERPOWERED and cannot vote
ALPHA = 0.05              # central 95% acceptance interval on a control distribution


def _consistency(v, dist):
    """Empirical two-sided position of `v` inside a control distribution:
    returns (inside_central_95, two-sided p)."""
    lo, hi = np.quantile(dist, ALPHA / 2), np.quantile(dist, 1 - ALPHA / 2)
    q = float((dist <= v).mean())
    p = 2 * min(q, 1 - q)
    return bool(lo <= v <= hi), float(p)


def _diag_gauss_llr(vec, dA, dB, feats):
    """Sum of per-feature Gaussian log-likelihood ratios, machine over hand."""
    tot = 0.0
    for k in feats:
        a, b = dA[k], dB[k]
        sa, sb = a.std(ddof=1), b.std(ddof=1)
        if sa <= 0 or sb <= 0:
            continue
        za = (vec[k] - a.mean()) / sa
        zb = (vec[k] - b.mean()) / sb
        tot += (-0.5 * za ** 2 - math.log(sa)) - (-0.5 * zb ** 2 - math.log(sb))
    return tot


def combined_classifier(real, dA, dB, feats=PRIMARY):
    """Combined log-LR over the pre-registered primary features. Reports the
    classifier's own power (how often it calls a true hand stream 'hand' at the 5%
    machine-false-positive rate) and where the real ciphertext falls."""
    feats = [k for k in feats if k in dA and k in dB]
    rows_a = [_diag_gauss_llr({k: dA[k][i] for k in feats}, dA, dB, feats)
              for i in range(len(dA[feats[0]]))]
    rows_b = [_diag_gauss_llr({k: dB[k][i] for k in feats}, dA, dB, feats)
              for i in range(len(dB[feats[0]]))]
    a = np.array(rows_a); b = np.array(rows_b)
    thr = float(np.quantile(a, ALPHA))          # machine streams below this are 5%
    power = float((b < thr).mean())             # hand streams correctly flagged
    rv = _diag_gauss_llr(real, dA, dB, feats)
    return {"features": feats, "threshold_5pct_machine": thr,
            "power": power,
            "machine_mean": float(a.mean()), "machine_sd": float(a.std(ddof=1)),
            "hand_mean": float(b.mean()), "hand_sd": float(b.std(ddof=1)),
            "real_logLR_machine_over_hand": float(rv),
            "real_called": "machine" if rv >= thr else "hand"}


# ---------------------------------------------------------------- power
def _dist(gen, reps, n, st, seed0, **kw):
    rows = []
    for k in range(reps):
        rng = np.random.default_rng(seed0 + k)
        rows.append(F.measure(gen(n, rng, st, **kw), st))
    keys = sorted(rows[0])
    return {k: np.array([r[k] for r in rows], dtype=float) for k in keys}


def power_table(dA, dB, alpha=0.05):
    """For each statistic: one-sided power to reject 'stream is MACHINE' when the
    stream is really HAND, at the 5% level, plus the AUC (rank separation)."""
    out = {}
    for k in dA:
        a, b = dA[k], dB[k]
        if not np.isfinite(a).all() or not np.isfinite(b).all():
            continue
        if a.std() == 0 and b.std() == 0:
            continue
        hi = np.quantile(a, 1 - alpha); lo = np.quantile(a, alpha)
        p_hi = float((b > hi).mean()); p_lo = float((b < lo).mean())
        direction = "greater" if p_hi >= p_lo else "less"
        power = max(p_hi, p_lo)
        # AUC via Mann-Whitney
        allv = np.concatenate([a, b])
        r = np.argsort(np.argsort(allv)) + 1.0
        rb = r[len(a):].sum()
        auc = (rb - len(b) * (len(b) + 1) / 2) / (len(a) * len(b))
        out[k] = {"machine_mean": float(a.mean()), "machine_sd": float(a.std(ddof=1)),
                  "hand_mean": float(b.mean()), "hand_sd": float(b.std(ddof=1)),
                  "direction": direction, "power": power,
                  "auc": float(max(auc, 1 - auc))}
    return out


def locate_real(real, dA, dB):
    """Where does the real ciphertext sit relative to each control distribution?"""
    out = {}
    for k, v in real.items():
        if k not in dA or k not in dB:
            continue
        a, b = dA[k], dB[k]
        sa = a.std(ddof=1); sb = b.std(ddof=1)
        za = (v - a.mean()) / sa if sa > 0 else 0.0
        zb = (v - b.mean()) / sb if sb > 0 else 0.0
        llr = 0.0
        if sa > 0 and sb > 0:
            llr = (-0.5 * za ** 2 - math.log(sa)) - (-0.5 * zb ** 2 - math.log(sb))
        out[k] = {"real": float(v), "z_vs_machine": float(za), "z_vs_hand": float(zb),
                  "logLR_machine_over_hand": float(llr),
                  "pct_in_machine": float((a <= v).mean()),
                  "pct_in_hand": float((b <= v).mean())}
    return out


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--out", default=os.path.join(HERE, "results.json"))
    args = ap.parse_args()
    reps = args.reps

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    x, st = F.load_structure()
    n = len(x)
    real = F.measure(x, st)
    print("real stream n=%d pages=%d lines=%d  doublets=%d rate=%.6f"
          % (n, st["n_pages"], int(st["line"].max()) + 1,
             real["n_doublets"], real["lag1_rate"]))

    res = {"n": n, "reps": reps, "target_doublet_rate": TARGET_DOUBLET,
           "transcription": "data/krisyotam_runes.txt",
           "real": real, "calibration": {}, "gates": {}, "controls": {}}

    # ---- calibrate every control to the real lag-1 rate ------------------
    print("calibrating controls to the real doublet rate ...")
    supp = calibrate(gen_machine, 0.0, 0.999, n=n, st=st, key="supp")
    res["calibration"]["machine_supp"] = supp
    supp_l = calibrate(gen_machine_lines, 0.0, 0.999, n=n, st=st, key="supp")
    res["calibration"]["machine_lines_supp"] = supp_l
    print("  machine supp=%.4f   machine/line supp=%.4f" % (supp, supp_l))

    hand_cfg = {}
    for name, kw in HAND_LADDER:
        def g(nn, rng, stt, a1, _kw=kw):
            return gen_hand(nn, rng, stt, a1=a1, **_kw)
        a1 = calibrate(g, 0.0, 6.0, n=n, st=st, key="a1", reps=8)
        hand_cfg[name] = dict(kw, a1=a1)
        print("  %-20s a1=%.4f  %s" % (name, a1, kw))
    res["calibration"]["hand"] = hand_cfg

    # ---- gate: the instrument must see a filter at all --------------------
    print("gate: uniform vs machine ...")
    dU = _dist(gen_uniform, max(40, reps // 4), n, st, 10_000)
    dA = _dist(gen_machine, reps, n, st, 20_000, supp=supp)
    gate = power_table(dU, dA)
    res["gates"]["uniform_vs_machine"] = gate
    g1 = gate["lag1_z"]["power"]
    print("  GATE lag1_z power(uniform vs machine) = %.3f  (must be 1.000)" % g1)
    res["gates"]["PASS"] = bool(g1 >= 0.99)
    res["controls"]["uniform"] = {k: [float(v.mean()), float(v.std(ddof=1))] for k, v in dU.items()}
    res["controls"]["machine"] = {k: [float(v.mean()), float(v.std(ddof=1))] for k, v in dA.items()}

    # ---- machine with LINE scope (does test 5 have power?) ---------------
    print("machine/line-scoped control ...")
    dL = _dist(gen_machine_lines, reps, n, st, 30_000, supp=supp_l)
    res["controls"]["machine_lines"] = {k: [float(v.mean()), float(v.std(ddof=1))] for k, v in dL.items()}
    res["power_machine_vs_machine_lines"] = power_table(dA, dL)
    res["real_vs_machine_lines"] = locate_real(real, dA, dL)
    scope = {}
    for k in ["dbl_line_cross_z", "dbl_line_cross_rate", "dbl_page_cross_z",
              "dbl_posinline_ks", "dbl_posinpage_ks", "n_doublets"]:
        if k not in dA:
            continue
        in_m, p_m = _consistency(real[k], dA[k])
        in_l, p_l = _consistency(real[k], dL[k])
        scope[k] = {"real": float(real[k]),
                    "power_flat_vs_linescoped": res["power_machine_vs_machine_lines"][k]["power"],
                    "inside_flat_95": in_m, "p_flat": p_m,
                    "inside_linescoped_95": in_l, "p_linescoped": p_l}
    scope["combined"] = combined_classifier(
        real, dA, dL, feats=["dbl_line_cross_z", "dbl_posinline_ks", "n_doublets"])
    res["scope_test"] = scope
    print("  scope test: line-cross power=%.3f  combined power=%.3f  real called %s"
          % (scope["dbl_line_cross_z"]["power_flat_vs_linescoped"],
             scope["combined"]["power"], scope["combined"]["real_called"]))

    # ---- the hand ladder --------------------------------------------------
    res["power"] = {}
    res["real_location"] = {}
    for i, (name, _) in enumerate(HAND_LADDER):
        print("hand rung: %s ..." % name)
        cfg = hand_cfg[name]
        dB = _dist(gen_hand, reps, n, st, 40_000 + 1000 * i, **cfg)
        res["controls"][name] = {k: [float(v.mean()), float(v.std(ddof=1))] for k, v in dB.items()}
        res["power"][name] = power_table(dA, dB)
        res["real_location"][name] = locate_real(real, dA, dB)
        pw = res["power"][name]
        top = sorted(pw.items(), key=lambda kv: -kv[1]["power"])[:4]
        print("   best separators: " + ", ".join("%s %.2f" % (k, v["power"]) for k, v in top))

        # --- pre-registered adjudication for this rung ---------------------
        rung = {"lag2to8_rate": float(dB["bleed28_rate"].mean()),
                "lag2to8_suppression": float(1 - dB["bleed28_rate"].mean() / Q),
                "lag1_rate": float(dB["lag1_rate"].mean()),
                "primary": {}, "secondary": {}}
        votes_hand, votes_machine, underpowered = [], [], []
        for k in PRIMARY + SECONDARY:
            if k not in dA or k not in dB:
                continue
            p_here = res["power"][name].get(k, {}).get("power", 0.0)
            in_m, p_m = _consistency(real[k], dA[k])
            in_h, p_h = _consistency(real[k], dB[k])
            rec = {"real": float(real[k]), "power_machine_vs_hand": p_here,
                   "inside_machine_95": in_m, "p_two_sided_machine": p_m,
                   "inside_hand_95": in_h, "p_two_sided_hand": p_h}
            (rung["primary"] if k in PRIMARY else rung["secondary"])[k] = rec
            if k in PRIMARY:
                if p_here < POWER_FLOOR:
                    underpowered.append(k)
                elif in_m and not in_h:
                    votes_machine.append(k)
                elif in_h and not in_m:
                    votes_hand.append(k)
        rung["votes_machine"] = votes_machine
        rung["votes_hand"] = votes_hand
        rung["underpowered_primary"] = underpowered
        rung["combined"] = combined_classifier(real, dA, dB)
        if rung["combined"]["power"] < POWER_FLOOR:
            rung["verdict"] = "UNDERPOWERED-TO-SEPARATE"
        elif votes_machine and not votes_hand:
            rung["verdict"] = "MACHINE"
        elif votes_hand and not votes_machine:
            rung["verdict"] = "HAND"
        else:
            rung["verdict"] = "AMBIGUOUS"
        res.setdefault("adjudication", {})[name] = rung
        loc = res["real_location"][name]
        print("   rung lag2-8 suppression=%.2f%%  combined power=%.3f  real called %s"
              " -> VERDICT %s"
              % (100 * rung["lag2to8_suppression"], rung["combined"]["power"],
                 rung["combined"]["real_called"], rung["verdict"]))
        print("   real bleed28_z=%.2f  z_vs_machine=%.2f  z_vs_hand=%.2f"
              % (real["bleed28_z"], loc["bleed28_z"]["z_vs_machine"],
                 loc["bleed28_z"]["z_vs_hand"]))

    # ---- fairness check: every control must match the real lag-1 rate ----
    res["fairness_lag1_rate"] = {
        "real": real["lag1_rate"],
        "machine": [float(dA["lag1_rate"].mean()), float(dA["lag1_rate"].std(ddof=1))],
        "machine_lines": [float(dL["lag1_rate"].mean()), float(dL["lag1_rate"].std(ddof=1))],
    }
    for name, _ in HAND_LADDER:
        res["fairness_lag1_rate"][name] = res["controls"][name]["lag1_rate"]
    print("fairness (lag-1 rate): real %.5f | " % real["lag1_rate"] +
          " | ".join("%s %.5f" % (k, v[0]) for k, v in res["fairness_lag1_rate"].items()
                     if k != "real"))

    # ---- the analytic bleed bound ----------------------------------------
    sd = float(dA["bleed28_z"].std(ddof=1))
    m = sum(n - k for k in range(2, 9))
    slope = math.sqrt(m * Q / (1 - Q))        # z shifts by -slope * suppression
    zobs = real["bleed28_z"]
    # Under a true lag-2..8 suppression s, bleed28_z ~ N(-slope*s, sd^2). The model H_s is
    # rejected one-sided at level q when z_obs - (-slope*s) > z_q*sd, i.e. s > (z_q*sd - z_obs)/slope.
    res["bleed_bound"] = {
        "machine_bleed28_z_sd": sd,
        "z_observed": zobs,
        "slope_per_unit_suppression": slope,
        "max_lag2to8_suppression_at_95pct": float(max(0.0, (1.645 * sd - zobs) / slope)),
        "max_lag2to8_suppression_at_99pct": float(max(0.0, (2.326 * sd - zobs) / slope)),
    }
    print("bleed bound: lag-2..8 suppression > %.3f%% is excluded at 95%%"
          % (100 * res["bleed_bound"]["max_lag2to8_suppression_at_95pct"]))

    json.dump(res, open(args.out, "w"), indent=1)
    print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
