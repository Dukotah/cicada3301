"""Round 18 / L2 -- SUB-ATTACK B: rejection consumes draws, so the keystream is not
index-aligned.

B.1  the drift law                 -- how many extra draws, with what spread
B.2  the rigid-window survival law -- what a rigid screen can still see, by window length
B.3  FULL-LENGTH BEAM POWER        -- the load-bearing check.  Every plant-and-recover
     control in this repository was run at <= 400 runes.  B-04's Stage D read a decay from
     -6.654 to -7.239 over the full 12,956 runes as proof that the survivors were lucky.
     That reading is only sound if the beam can recover a CORRECT key at that length.
     Nobody has ever checked.

Run:  PYTHONUTF8=1 python3 b_drawcount.py
"""
import os, sys, json, math, time, random, hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fastbeam as fb                                   # noqa: E402
import filter_models as fm                              # noqa: E402
ROOT = fb.ROOT
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))
sys.path.insert(0, os.path.join(ROOT, "benchmark"))
import skipdecode as sk                                 # noqa: E402
import null as bnull                                    # noqa: E402

N = 29
Q = 1.0 / N
SUPP = 0.8129                     # PREREG s1: analytic s* from the real doublet rate
RHO = Q * SUPP / (1 - Q * SUPP)
NRUNE = 12956


def sha_ctr_ks(seed, n):
    """B-04 / G5 family: SHA-256 counter mode, reduced mod 29 (D3's exact expander)."""
    out, c = [], 0
    while len(out) < n:
        h = hashlib.sha256(seed + c.to_bytes(4, "big")).digest()
        out.extend(b % N for b in h)
        c += 1
    return out[:n]


# ===================================================================== B.1
def b1_drift_law(P, reps=200):
    """Analytic vs simulated draw consumption over the full book."""
    e_analytic = RHO * (NRUNE - 1)
    var_per = Q * SUPP / (1 - Q * SUPP) ** 2
    sd_analytic = math.sqrt((NRUNE - 1) * var_per)
    tot, curves = [], []
    for r in range(reps):
        rng = random.Random(90000 + r)     # a fresh uniform pad per replicate
        K = [rng.randrange(N) for _ in range(int(NRUNE * 1.2) + 512)]
        C, skips, used = sk.encipher_keyskip(P[:NRUNE], K, sign=-1, supp=SUPP,
                                             seed=90000 + r)
        tot.append(sum(skips))
        if r < 20:
            curves.append(np.cumsum(skips).tolist())
    tot = np.array(tot, dtype=float)
    lo, hi = float(np.percentile(tot, 2.5)), float(np.percentile(tot, 97.5))
    return {
        "rho": RHO, "supp": SUPP,
        "analytic_mean_extra_draws": e_analytic,
        "analytic_sd": sd_analytic,
        "sim_mean": float(tot.mean()), "sim_sd": float(tot.std(ddof=1)),
        "sim_ci95": [lo, hi],
        "analytic_inside_sim_ci95": lo <= e_analytic <= hi,
        "reps": reps,
        "keystream_symbols_consumed": NRUNE + float(tot.mean()),
        "drift_at_page52_start": {
            "rune_index": 12200,
            "mean": RHO * 12200,
            "sd": math.sqrt(12200 * var_per),
        },
        "mean_drift_curve_head": [float(np.mean([c[i] for c in curves]))
                                  for i in (0, 99, 499, 999, 4999, 9999, NRUNE - 2)],
    }


# ===================================================================== B.2
def b2_survival(P, K, lengths=(25, 50, 100, 120, 200, 400), plants=200, bar=-5.5):
    """Rigid vs beam detection of the CORRECT key, by window length, under the real filter.

    `p_driftfree` = (1-rho)^L is the probability the sampler consumed no extra draw inside
    the window, i.e. the probability a rigid screen is even looking at the right key.
    """
    rows = []
    for L in lengths:
        rig_hit = beam_hit = 0
        rig_sc, beam_sc, rig_rec, beam_rec, nsk = [], [], [], [], []
        for t in range(plants):
            st = (t * 137) % (len(P) - L - 2)
            Pl = P[st:st + L]
            C, skips, used = sk.encipher_keyskip(Pl, K, sign=-1, supp=SUPP,
                                                 seed=4000 + t)
            nsk.append(sum(skips))
            r = sk.rigid_decode(C, K, sign=-1, o=0)
            b = fb.beam_decode(C, K, sign=-1, o=0, beam_w=400, max_skip=3)
            rig_sc.append(r["score"]); beam_sc.append(b["score"])
            rig_rec.append(sum(1 for x, y in zip(r["plain_idx"], Pl) if x == y) / L)
            beam_rec.append(sum(1 for x, y in zip(b["plain_idx"], Pl) if x == y) / L)
            rig_hit += r["score"] >= bar
            beam_hit += b["score"] >= bar
        rows.append({
            "L": L, "plants": plants,
            "p_driftfree_analytic": (1 - RHO) ** L,
            "mean_true_skips": float(np.mean(nsk)),
            "frac_windows_with_zero_skips": float(np.mean([x == 0 for x in nsk])),
            "rigid_detect_power": rig_hit / plants,
            "beam_detect_power": beam_hit / plants,
            "rigid_mean_score": float(np.mean(rig_sc)),
            "beam_mean_score": float(np.mean(beam_sc)),
            "rigid_mean_recovery": float(np.mean(rig_rec)),
            "beam_mean_recovery": float(np.mean(beam_rec)),
        })
        print(f"  L={L:4d}  P(drift-free)={rows[-1]['p_driftfree_analytic']:.3f}  "
              f"rigid power={rows[-1]['rigid_detect_power']:.3f} "
              f"(score {rows[-1]['rigid_mean_score']:.2f})   "
              f"beam power={rows[-1]['beam_detect_power']:.3f} "
              f"(score {rows[-1]['beam_mean_score']:.2f})")
    return {"bar": bar, "rows": rows}


# ===================================================================== B.3
def b3_length_power(P, K, lengths=(120, 400, 1000, 3000, 6000, 12956), plants=3,
                    beam_w=400, max_skip=3):
    """THE load-bearing check. Bar (PREREG 3.B.3): score >= -5.5 AND recovery >= 0.90."""
    rows = []
    for L in lengths:
        sc, rec, sk_inf, sk_true, tm = [], [], [], [], []
        for t in range(plants):
            Pl = P[:L] if plants == 1 else P[t * 37: t * 37 + L]
            C, skips, used = sk.encipher_keyskip(Pl, K, sign=-1, supp=SUPP, seed=7000 + t)
            t0 = time.time()
            b = fb.beam_decode(C, K, sign=-1, o=0, beam_w=beam_w, max_skip=max_skip)
            tm.append(time.time() - t0)
            sc.append(b["score"])
            rec.append(sum(1 for x, y in zip(b["plain_idx"], Pl) if x == y) / L)
            sk_inf.append(b["n_skips"]); sk_true.append(sum(skips))
        row = {"L": L, "plants": plants, "beam_w": beam_w, "max_skip": max_skip,
               "mean_score": float(np.mean(sc)), "min_score": float(np.min(sc)),
               "mean_recovery": float(np.mean(rec)), "min_recovery": float(np.min(rec)),
               "mean_inferred_skips": float(np.mean(sk_inf)),
               "mean_true_skips": float(np.mean(sk_true)),
               "skip_recovery_exact": float(np.mean(
                   [a == b_ for a, b_ in zip(sk_inf, sk_true)])),
               "sec_per_decode": float(np.mean(tm)),
               "pass": bool(np.min(sc) >= -5.5 and np.min(rec) >= 0.90)}
        rows.append(row)
        print(f"  L={L:6d}  score {row['mean_score']:7.3f}  recovery "
              f"{row['mean_recovery']:.4f}  skips inferred/true "
              f"{row['mean_inferred_skips']:.0f}/{row['mean_true_skips']:.0f}  "
              f"{row['sec_per_decode']:.1f}s  -> {'PASS' if row['pass'] else 'FAIL'}")
    return rows


def main():
    t0 = time.time()
    P = fm.english_runes(NRUNE + 600)
    K = sha_ctr_ks(b"CICADA3301", int(NRUNE * 1.6) + 4096)

    print("=" * 78)
    print("B.1 -- the drift law")
    print("=" * 78)
    b1 = b1_drift_law(P)
    print(f"  analytic  E[extra draws] = {b1['analytic_mean_extra_draws']:.1f} "
          f"+/- {b1['analytic_sd']:.1f}")
    print(f"  simulated                = {b1['sim_mean']:.1f} +/- {b1['sim_sd']:.1f}  "
          f"95% CI {b1['sim_ci95'][0]:.0f}..{b1['sim_ci95'][1]:.0f}")
    print(f"  analytic inside simulated 95% CI: {b1['analytic_inside_sim_ci95']}")
    print(f"  keystream symbols consumed for 12,956 runes: "
          f"{b1['keystream_symbols_consumed']:.0f}")

    print("\n" + "=" * 78)
    print("B.2 -- rigid-window survival: what an aligned screen can still see")
    print("=" * 78)
    b2 = b2_survival(P, K)

    print("\n" + "=" * 78)
    print("B.3 -- FULL-LENGTH BEAM POWER (B-04 Stage D settings: beam_w=400, max_skip=3)")
    print("=" * 78)
    b3 = b3_length_power(P, K)
    failed = [r for r in b3 if not r["pass"]]
    b3_wide = None
    if failed:
        Lf = min(r["L"] for r in failed)
        print(f"\n  first failure at L={Lf}; re-testing that length at beam_w=4000")
        b3_wide = b3_length_power(P, K, lengths=(Lf,), plants=3, beam_w=4000)

    # negative control: a WRONG key at full length must stay in noise
    Cw, _, _ = sk.encipher_keyskip(P[:NRUNE], K, sign=-1, supp=SUPP, seed=7000)
    Kw = sha_ctr_ks(b"WELCOME", int(NRUNE * 1.6) + 4096)
    t1 = time.time()
    bw = fb.beam_decode(Cw, Kw, sign=-1, o=0, beam_w=400, max_skip=3)
    neg = {"wrong_key_full_length_score": bw["score"],
           "wrong_key_inferred_skips": bw["n_skips"],
           "sec": round(time.time() - t1, 1)}
    print(f"\n  negative control, WRONG key at L=12956: score {bw['score']:.3f}, "
          f"inferred skips {bw['n_skips']}")

    out = {"supp": SUPP, "rho": RHO, "B1": b1, "B2": b2, "B3": b3,
           "B3_wide_beam": b3_wide, "B3_negative_control": neg,
           "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "b_drawcount.json"), "w"), indent=1)
    print(f"\nelapsed {out['elapsed_s']}s -> b_drawcount.json")


if __name__ == "__main__":
    main()
