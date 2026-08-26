"""Round 18 / L2 -- SUB-ATTACK A: which stream does the rejection sampler act on?

PREREG section 2.  Calibrate every parameterised model to the real lag-1 rate, generate 200
replicates of each at n = 12,956, measure the fixed battery, build the pairwise Gaussian
log-LR classifier, measure power at a 5 % false-positive rate against M1, and adjudicate the
real stream.  A model may only be called EXCLUDED if the measured power is >= 0.99.

Run:  PYTHONUTF8=1 python3 a_locus.py [--reps 200]
"""
import os, sys, json, math, time, random, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import filter_models as fm                              # noqa: E402

PRIMARY = fm.PRIMARY
SD_FLOOR = 1e-9


def gaussian_ll(v, mu, sd):
    sd = max(sd, SD_FLOOR)
    return -0.5 * math.log(2 * math.pi * sd * sd) - 0.5 * ((v - mu) / sd) ** 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    a = ap.parse_args()
    t0 = time.time()

    X = fm.real_stream()
    n = len(X)
    real = fm.battery(X)
    target = real["lag1_rate"]
    print(f"real stream: n={n}  lag1_rate={target:.8f}  doublets={real['run2']}")

    P = fm.english_runes(n)
    dP = float(np.mean(np.asarray(P[1:]) == np.asarray(P[:-1])))
    print(f"english plaintext doublet rate d_P = {dP:.5f}   "
          f"=> M3 predicted ct lag-1 = {(1-dP)/28:.5f}, M4 predicted = {1/29:.5f}")

    # ---------------------------------------------------------------- calibration
    print("\ncalibrating suppression parameters to the real lag-1 rate ...")
    cal = {}
    for name in fm.MODELS:
        s = fm.calibrate(name, P, target)
        cal[name] = s
        print(f"  {name:16s} supp = {('%.4f' % s) if s is not None else '   n/a'}")

    # PREREG section 1: s* from the analytic law must reproduce lane P4's bisected 0.8131
    q = 1.0 / 29
    s_star = (q - target) / (q - q * target)
    print(f"\nanalytic s* from r(s)=q(1-s)/(1-qs): {s_star:.4f}   "
          f"(P4 bisected 0.8131; |delta| = {abs(s_star-0.8131):.4f})")
    rho = q * s_star / (1 - q * s_star)
    print(f"analytic rho = q s/(1-q s) = {rho:.6f}  => E[extra draws over 12,956] "
          f"= {rho*n:.1f}")

    # ---------------------------------------------------------------- replicates
    print(f"\ngenerating {a.reps} replicates x {len(fm.MODELS)} models at n={n} ...")
    reps = {}
    achieved = {}
    for mi, (name, (fn, par)) in enumerate(fm.MODELS.items()):
        rows = []
        kw = {} if par is None else {par: cal[name]}
        for r in range(a.reps):
            rng = random.Random(770000 + 7919 * r + 131 * mi)
            C, skips = fn(P, rng, **kw)
            b = fm.battery(C)
            b["_skips"] = skips
            rows.append(b)
        reps[name] = rows
        achieved[name] = float(np.mean([r["lag1_rate"] for r in rows]))
        print(f"  {name:16s} lag1 {achieved[name]:.6f} +/- "
              f"{np.std([r['lag1_rate'] for r in rows]):.6f}   "
              f"skips {np.mean([r['_skips'] for r in rows]):.1f}   "
              f"({time.time()-t0:.0f}s)")

    # ---------------------------------------------------------------- classifier
    stats = {m: {k: np.array([r[k] for r in reps[m]]) for k in PRIMARY} for m in reps}
    mu = {m: {k: float(stats[m][k].mean()) for k in PRIMARY} for m in reps}
    sd = {m: {k: float(stats[m][k].std(ddof=1)) for k in PRIMARY} for m in reps}

    def llr(vec, alt, base="M1_ct_keyskip"):
        s = 0.0
        for k in PRIMARY:
            s += gaussian_ll(vec[k], mu[alt][k], sd[alt][k])
            s -= gaussian_ll(vec[k], mu[base][k], sd[base][k])
        return s

    base = "M1_ct_keyskip"
    verdicts = {}
    for alt in reps:
        if alt == base:
            continue
        h0 = np.array([llr(r, alt) for r in reps[base]])       # M1 replicates
        h1 = np.array([llr(r, alt) for r in reps[alt]])        # alt replicates
        thr = float(np.percentile(h0, 95))
        power = float((h1 > thr).mean())
        rl = llr(real, alt)
        verdicts[alt] = {
            "power_vs_M1_at_5pct_fpr": power,
            "threshold_logLR": thr,
            "real_logLR": rl,
            "real_called": alt if rl > thr else base,
            "separable": power >= 0.99,
            "underpowered": power < 0.80,
            "mean_logLR_alt": float(h1.mean()),
            "mean_logLR_M1": float(h0.mean()),
        }

    # ---- goodness-of-fit containment: is the REAL stream inside each model?
    # The log-LR test is a two-hypothesis test; it can name a model even when the data fit
    # NEITHER.  Containment is the test that actually excludes, exactly as lane P4 used it.
    contain = {}
    for m in reps:
        rows = {}
        worst = 0.0
        for k in PRIMARY:
            v = stats[m][k]
            mm, ss = float(v.mean()), float(v.std(ddof=1))
            z = (real[k] - mm) / ss if ss > SD_FLOOR else float("inf")
            lo = float((v <= real[k]).mean()); hi = float((v >= real[k]).mean())
            rows[k] = {"model_mean": mm, "model_sd": ss, "real": real[k],
                       "z": z, "p_two_sided": 2 * min(lo, hi)}
            worst = max(worst, abs(z))
        contain[m] = {"per_stat": rows, "max_abs_z": worst,
                      "real_inside": worst < 4.0}

    # ---------------------------------------------------------------- delta-spectrum
    dz = real["max_abs_delta_z"]
    nudge_bar = 3.57                      # PREREG: Bonferroni 28 cells, alpha .01, 2-sided
    delta_verdict = {
        "real_max_abs_delta_z": dz,
        "real_argmax_delta": real["argmax_delta"],
        "bar_bonferroni_28_alpha01": nudge_bar,
        "nudge_signature_detected": dz >= nudge_bar,
        "real_delta_chi2_df": real["delta_chi2_df"],
        "M1_delta_chi2_df": mu[base]["delta_chi2_df"],
        "M2n_delta_chi2_df": mu["M2n_ct_nudge"]["delta_chi2_df"],
        "M2n_max_abs_delta_z": mu["M2n_ct_nudge"]["max_abs_delta_z"],
    }

    out = {
        "n": n, "reps": a.reps,
        "real": {k: real[k] for k in sorted(real)},
        "english_plaintext_doublet_rate": dP,
        "analytic": {"s_star": s_star, "P4_bisected_supp": 0.8131,
                     "delta_vs_P4": abs(s_star - 0.8131),
                     "rho": rho, "expected_extra_draws": rho * n},
        "calibrated_supp": cal,
        "achieved_lag1": achieved,
        "model_means": mu, "model_sds": sd,
        "pairwise_vs_M1": verdicts,
        "containment": contain,
        "delta_spectrum": delta_verdict,
        "elapsed_s": round(time.time() - t0, 1),
    }
    json.dump(out, open(os.path.join(HERE, "a_locus.json"), "w"), indent=1)

    # ---------------------------------------------------------------- report
    print("\n" + "=" * 78)
    print("SUB-ATTACK A -- adjudication (bar: power >= 0.99 to exclude)")
    print("=" * 78)
    print(f"{'model':17s} {'lag1':>10s} {'power':>7s} {'max|z| real':>12s}  verdict")
    final = {}
    for m in fm.MODELS:
        cz = contain[m]["max_abs_z"]
        if m == base:
            vd = ("REFERENCE - real inside" if contain[m]["real_inside"]
                  else "REFERENCE - real OUTSIDE (model wrong)")
            print(f"{m:17s} {achieved[m]:10.6f} {'--':>7s} {cz:12.2f}  {vd}")
            final[m] = vd
            continue
        v = verdicts[m]
        if v["separable"] and cz >= 4.0:
            vd = "EXCLUDED"
        elif v["underpowered"] and cz < 4.0:
            vd = "UNDERPOWERED-TO-SEPARATE"
        elif cz < 4.0:
            vd = "CONSISTENT-WITH-REAL"
        else:
            vd = "excluded-but-underpowered-pair"
        final[m] = vd
        print(f"{m:17s} {achieved[m]:10.6f} {v['power_vs_M1_at_5pct_fpr']:7.3f} "
              f"{cz:12.2f}  {vd}")
    out["verdicts"] = final
    json.dump(out, open(os.path.join(HERE, "a_locus.json"), "w"), indent=1)
    print(f"\ndelta-spectrum: real max|z| over 28 cells = {dz:.2f} (bar {nudge_bar}); "
          f"M2n control = {mu['M2n_ct_nudge']['max_abs_delta_z']:.1f}")
    print(f"elapsed {out['elapsed_s']}s -> a_locus.json")


if __name__ == "__main__":
    main()
