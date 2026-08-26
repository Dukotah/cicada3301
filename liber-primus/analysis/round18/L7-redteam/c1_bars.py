"""L7 / sub-attack C — re-derive the load-bearing numbers instead of trusting them.

Six independent audits, each writing its result into out_c1.json as it finishes so a stall
never loses work:

  C1  headline LP2 statistics, recomputed from the pinned runes
  C2  the G3 doublet-deficit floor, recomputed AND extended to registers it never covered
  C3  threshold_for()'s Gumbel constants: zero-DOF two-point solve, sampling error, and
      out-of-sample residuals against every recorded sweep maximum in the repo
  C4  segment-length / beam-width transfer of those constants (measured, not argued)
  C5  bar-at-own-N audit: what each sweep compared against, and where the -5.5 floor stops
  C6  the multiple-comparisons tally that RECON-B item B-17 flags as "frozen at 5"

    python3 c1_bars.py            # writes out_c1.json incrementally
    python3 c1_bars.py --skip-c4  # skip the only slow part (~1 min of beam nulls)
"""
import os, sys, json, math, random, collections, re, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
B6 = os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")
for p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round11"), B6):
    sys.path.insert(0, p)

from lp import gematria as gp                # noqa: E402
import skipdecode as sk                      # noqa: E402
import plant as PL                           # noqa: E402
import lib_numchannel as nc                  # noqa: E402
import null as NL                            # noqa: E402

N = gp.N
GAMMA = 0.5772156649015329
OUT = os.path.join(HERE, "out_c1.json")
RES = {}


def save(k, v):
    RES[k] = v
    json.dump(RES, open(OUT, "w"), indent=1)
    print(f"  [saved {k}]")


# ------------------------------------------------------------------ C1
def c1_headline():
    C = nc.unsolved()
    n = len(C)
    dbl = sum(1 for i in range(1, n) if C[i] == C[i - 1])
    rate = dbl / (n - 1)
    cnt = collections.Counter(C)
    ioc = sum(c * (c - 1) for c in cnt.values()) / (n * (n - 1))
    ent = -sum((c / n) * math.log2(c / n) for c in cnt.values())
    exp_dbl = ioc                     # E[doublet] under an order-destroying null == IoC
    supp_lag1 = 1 - rate / exp_dbl
    out = {
        "n_runes": n, "n_doublets": dbl, "doublet_rate_pct": 100 * rate,
        "published_doublet_rate_pct": 0.664,
        "ioc_times_N": ioc * N, "published_ioc_times_N": 0.9999,
        "entropy_bits": ent, "published_entropy_bits": 4.8565,
        "expected_doublet_rate_pct_under_own_histogram": 100 * exp_dbl,
        "lag1_suppression_pct": 100 * supp_lag1,
        "published_lag1_suppression_pct": 80.75,
        "note": ("Lag-1 suppression is 1 - observed/expected where expected is the stream's "
                 "OWN unigram collision rate (= IoC), not 1/29. The two agree here only "
                 "because IoC*N = 1.0000; on any stream with structure they differ."),
        "reproduces": None,
    }
    out["reproduces"] = (abs(out["doublet_rate_pct"] - 0.664) < 0.002 and
                         abs(out["ioc_times_N"] - 0.9999) < 0.002 and
                         abs(out["entropy_bits"] - 4.8565) < 0.002 and
                         abs(out["lag1_suppression_pct"] - 80.75) < 0.30)
    return out


# ------------------------------------------------------------------ C2
def _diff_min(idxs):
    c = collections.Counter((idxs[i] - idxs[i - 1]) % N for i in range(1, len(idxs)))
    n = len(idxs) - 1
    v = [c.get(d, 0) / n for d in range(N)]
    m = min(range(N), key=lambda d: v[d])
    return {"min_pct": 100 * v[m], "argmin_diff": m,
            "second_min_pct": 100 * sorted(v)[1], "p_doublet_pct": 100 * v[0], "n": n}


def c2_g3_floor():
    """min_d Pdp(d) is the floor on P(doublet) achievable by ANY plaintext-independent key.
    The published floor is measured on four MODERN ENGLISH corpora only."""
    import a1_scorer_language as A1
    panels = A1.build_panels()
    rows = {}
    for name, idxs in panels.items():
        if name == "RAND":
            continue
        rows[name] = _diff_min(idxs[:400000])
    # the four corpora the published floor actually used
    pub = {}
    for fn in ("kjv", "moby", "pride", "war"):
        p = os.path.join(LP, "data", fn + ".txt")
        if os.path.exists(p):
            t = re.sub(r"[^A-Za-z]", "", open(p, encoding="utf-8",
                                              errors="ignore").read().upper())
            pub[fn] = _diff_min(sk.eng_to_idx(t[20000:320000]))
    observed = 0.6638
    trigger = 0.80          # pre-registered in PREREG.md C-2
    breaches = {k: v["min_pct"] for k, v in rows.items() if v["min_pct"] <= trigger}
    return {"published_claim": ("min_d Pdp(d) = 1.38-1.83% over 4 English corpora; "
                               "'no natural-language plaintext' reaches 0.664%"),
            "published_corpora_recomputed": pub,
            "extension_registers": rows,
            "observed_LP2_doublet_pct": observed,
            "prereg_trigger_pct": trigger,
            "registers_at_or_below_trigger": breaches,
            "verdict": ("ENGLISH-CONDITIONAL" if breaches else
                        "HOLDS across every register tested")}


# ------------------------------------------------------------------ C3
def c3_gumbel():
    mu, beta = NL.DEFAULT_MU, NL.DEFAULT_BETA
    a1 = (200, -6.826)                    # round13/B04 PREREG s5
    a2 = (1385600, -6.185)                # round13/B04 results_A.json
    # exact two-point solve?
    b_solve = (a2[1] - a1[1]) / (math.log(a2[0]) - math.log(a1[0]))
    m_solve = a1[1] - b_solve * (math.log(a1[0]) + GAMMA)
    sd_gumbel = beta * math.pi / math.sqrt(6)
    lever = math.log(a2[0]) - math.log(a1[0])
    se_beta = math.sqrt(2) * sd_gumbel / lever
    se_mu = sd_gumbel * math.sqrt(1 + ((math.log(a1[0]) + GAMMA) / lever) ** 2 * 2)

    sweeps = [
        ("B-04 stage A", 1385600, -6.185, "round13/B04/results_A.json (FIT ANCHOR)"),
        ("B-04 stage B", 1290240, -6.129, "round13/B04 (null.py's own out-of-sample check)"),
        ("B-04 stage C", 3548160, -5.885, "round13/B04"),
        ("R16-KDF stage A", 692064, -6.259, "round16/KDF/results_A.json"),
        ("R16-PRNG", 52556, -6.347, "round16/prng/results.json"),
        ("R17 P0 dense", 3911819734, -6.769, "round17/SYNTHESIS.md"),
        ("R17 P1 bitcoin", 1389182016, -6.802, "round17/SYNTHESIS.md"),
        ("R17 P2 beacons", 3464597548, -6.811, "round17/SYNTHESIS.md"),
        ("R17 P3 tables", 5757316748, -5.679, "round17/SYNTHESIS.md (head window 31 runes)"),
    ]
    rows = []
    for name, n, obs, src in sweeps:
        pred = mu + beta * (math.log(n) + GAMMA)
        rows.append({"sweep": name, "n_trials": n, "observed_max": obs,
                     "predicted_E_max": pred, "residual": obs - pred,
                     "residual_in_gumbel_sd": (obs - pred) / sd_gumbel,
                     "source": src,
                     "fails_3sd": abs(obs - pred) / sd_gumbel > 3.0})
    return {"DEFAULT_MU": mu, "DEFAULT_BETA": beta,
            "two_point_solve_reproduces_constants": {
                "beta_from_anchors": b_solve, "mu_from_anchors": m_solve,
                "matches": abs(b_solve - beta) < 1e-3 and abs(m_solve - mu) < 1e-3},
            "degrees_of_freedom": 0,
            "note_on_the_fit": ("Two anchors, two parameters: this is an exact solve, not a "
                                "fit. It has no residual and therefore no internal check. "
                                "Both anchors are also SINGLE OBSERVED MAXIMA, each of which "
                                "is itself a Gumbel draw with sd = beta*pi/sqrt(6)."),
            "gumbel_sd_of_one_observed_max": sd_gumbel,
            "se_beta_from_two_single_maxima": se_beta,
            "se_beta_relative_pct": 100 * se_beta / beta,
            "se_mu_approx": se_mu,
            "circularity": ("both anchors come from B-04's own run, and threshold_for() was "
                            "then used to adjudicate B-04"),
            "out_of_sample": rows,
            "n_failing_3sd": sum(1 for r in rows if r["fails_3sd"])}


# ------------------------------------------------------------------ C4
def _tail_beta(vals, q=0.90):
    """Peaks-over-threshold scale estimate: for an exponential-tailed parent the mean
    excess over a high threshold is the MLE of the Gumbel scale of its maximum."""
    v = sorted(vals)
    u = v[int(q * len(v))]
    ex = [x - u for x in v if x > u]
    return (sum(ex) / len(ex)) if ex else float("nan"), u, len(ex)


def c4_transfer(n=400):
    """Measure mu and beta directly at the (segment length, beam width) combinations the
    repo's lanes actually ran at. null.py documents its constants as L~120, beam_w=400."""
    base = nc.unsolved()
    out = {}
    for (L, bw) in [(31, 120), (120, 400), (400, 120)]:
        K = PL.make_key("sha256_ctr", length=L * 5 + 4096, seed=b"L7-NULL-PAD")
        vals = []
        for k in range(n):
            r = random.Random(70000 + k)
            s = base[:L]
            s = list(s)
            r.shuffle(s)
            vals.append(sk.beam_decode(s, K, sign=-1, o=0, beam_w=bw,
                                       max_skip=3)["score"])
        beta, u, nex = _tail_beta(vals)
        mx = max(vals)
        mu = mx - beta * (math.log(n) + GAMMA)
        out[f"L{L}_bw{bw}"] = {
            "L": L, "beam_w": bw, "n_null": n,
            "mean": sum(vals) / n,
            "sd_bulk": (sum((x - sum(vals) / n) ** 2 for x in vals) / n) ** 0.5,
            "max": mx, "pot_threshold": u, "n_exceedances": nex,
            "beta_tail": beta, "mu_implied": mu,
            "beta_ratio_vs_DEFAULT": beta / NL.DEFAULT_BETA,
            "threshold_for_1e9_local": mu + beta * (math.log(1e9) -
                                                    math.log(-math.log(0.99))),
            "threshold_for_1e9_repo_constants": NL.threshold_for(10 ** 9),
        }
        print(f"    L={L:3d} bw={bw:4d}  mean {out[f'L{L}_bw{bw}']['mean']:.3f}  "
              f"beta_tail {beta:.4f}  (DEFAULT {NL.DEFAULT_BETA})  "
              f"ratio {beta / NL.DEFAULT_BETA:.2f}")
    ratios = [v["beta_ratio_vs_DEFAULT"] for v in out.values()]
    out["_verdict"] = ("TRANSFERS" if all(1 / 1.5 <= r <= 1.5 for r in ratios)
                       else "DOES NOT TRANSFER (pre-registered factor-1.5 trigger breached)")
    return out


# ------------------------------------------------------------------ C5
def c5_bar_audit():
    # where does the -5.5 floor stop binding?
    lo, hi = 2, 10 ** 15
    while hi / lo > 1.0001:
        mid = math.sqrt(lo * hi)
        if NL.threshold_for(mid) > -5.5 + 1e-12:
            hi = mid
        else:
            lo = mid
    nstar = hi
    sweeps = [
        ("Round 8 SEED", 2.52e9, "fixed bar (B-21 records the bar as statistically invalid at this scale)"),
        ("B-04", 6224300, "max(-5.5, null_max+0.5) with null_max measured at n=200, L=120"),
        ("B-05", 70680, "max(-5.5, null_max) with null at n=200"),
        ("R16-KDF", 692064, "-5.5 with a size-matched null per config"),
        ("R16-PRNG", 52556, "-5.5 with a size-matched null"),
        ("R17 P0", 3911819734, "-5.5 AND null_max+0.5; threshold_for(N) reported alongside"),
        ("R17 P1", 1389182016, "same"),
        ("R17 P2", 3464597548, "same"),
        ("R17 P3", 5757316748, "same"),
        ("R12-A1", 8 * 6 * 4 * 2 * 2, "-5.5; per-page null n=200"),
        ("F-01", 40, "-5.5 AND null_max+0.5"),
    ]
    rows = []
    for name, nt, used in sweeps:
        nt = int(nt)
        rows.append({"sweep": name, "n_trials": nt,
                     "threshold_for_own_N": NL.threshold_for(nt),
                     "floor_binds": NL.threshold_for(nt) <= -5.5 + 1e-12,
                     "bar_actually_used": used})
    return {"N_at_which_the_-5.5_floor_stops_binding": nstar,
            "interpretation": ("Below this N the historical -5.5 floor is the binding "
                               "constraint and the scale correction is cosmetic. Above it "
                               "the correction binds and a fixed bar is unsound."),
            "sweeps": rows,
            "sweeps_above_Nstar": [r["sweep"] for r in rows if not r["floor_binds"]]}


# ------------------------------------------------------------------ C6
def c6_tally():
    """RECON-B item B-17: 'Multiple-comparisons tally frozen at 5 across Rounds 8-9'."""
    led = json.load(open(os.path.join(LP, "LEDGER.json"), encoding="utf-8"))
    entries = led["entries"]
    with_threshold = [e for e in entries if e.get("threshold")]
    # documented trial counts, each traceable to a ledger entry or a round SYNTHESIS
    decodes = {
        "Round 8 SEED": 2_520_000_000,
        "Round 8 other tracks (GEOMETRY/PAYLOAD/POINTERS/SKELETON)": 8_200_000,
        "campaign12+13 keytext exhaustion (~200 texts)": 200,
        "R12-A1 CicadaOS pads": 8 * 6 * 4 * 2 * 2,
        "R12-C1 feedback/autokey": 21 * 55,
        "B-04 derived-key dictionary": 6_224_300,
        "B-05 payload-as-PRF-seed": 70_680,
        "R16-KDF": 692_064,
        "R16-PRNG": 52_556,
        "F-01 LP2-as-pad inversion": 40,
        "R17 P0-P3 public pads (offsets scored)": 14_522_916_046,
    }
    total = sum(decodes.values())
    eff = 8_380_000_000 + (total - 14_522_916_046)   # R17's own effective discount
    levels = {
        "level_1_preregistered_hypotheses": {
            "count": len(with_threshold),
            "basis": "LEDGER.json entries carrying an explicit threshold field",
            "bonferroni_alpha_at_0.01": 0.01 / max(1, len(with_threshold)),
            "family_wise_bar": NL.threshold_for(len(with_threshold))},
        "level_2_ledger_entries_total": {
            "count": len(entries),
            "family_wise_bar": NL.threshold_for(len(entries))},
        "level_3_decodes_and_offsets": {
            "count": total,
            "effective_after_R17_prefilter_discount": eff,
            "breakdown": decodes,
            "family_wise_bar": NL.threshold_for(total),
            "family_wise_bar_effective": NL.threshold_for(eff)},
    }
    return {"B-17_claim": "multiple-comparisons tally frozen at 5 across Rounds 8-9",
            "recomputed": levels,
            "the_number_that_matters": (
                "5 was never the right number at any level. The correct tally depends on "
                "which family you are controlling. Per-hypothesis it is now "
                f"{len(with_threshold)}; per ledger entry {len(entries)}; per decode "
                f"{total:,} ({eff:,} effective)."),
            "consequence": (
                "At the decode level the repo-wide family-wise bar is "
                f"{NL.threshold_for(total):.3f}, i.e. STRICTER than the -5.5 floor every "
                "sweep used. No published verdict flips - every best score in the repo is "
                "below both bars - but the -5.5 floor is not the repo-wide bar and should "
                "not be quoted as one."),
            "caveat": ("These counts are NOT independent tests: the same 12,956 runes are "
                       "re-decoded, so a Bonferroni/Gumbel correction over the union is "
                       "conservative. It is reported as an upper bound on the correction, "
                       "which is the honest direction for a negative.")}


def main():
    t0 = time.time()
    print("C1 headline statistics ...")
    save("C1_headline", c1_headline())
    print("C2 G3 doublet floor, extended beyond English ...")
    save("C2_g3_floor", c2_g3_floor())
    print("C3 threshold_for() Gumbel audit ...")
    save("C3_gumbel", c3_gumbel())
    if "--skip-c4" not in sys.argv:
        print("C4 segment-length / beam-width transfer (measuring nulls) ...")
        save("C4_transfer", c4_transfer())
    print("C5 bar-at-own-N audit ...")
    save("C5_bar_audit", c5_bar_audit())
    print("C6 multiple-comparisons tally (B-17) ...")
    save("C6_tally", c6_tally())
    save("elapsed_s", round(time.time() - t0, 1))
    print("wrote out_c1.json")


if __name__ == "__main__":
    main()
