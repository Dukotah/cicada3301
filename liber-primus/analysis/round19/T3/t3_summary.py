"""T3 — the summariser. Turns the four out_*.json files into the answers.

Computes, from the stored curves only (no new measurement):
  * k*(floor) for every pre-registered doublet floor x every perturbation model,
    by linear interpolation between grid points, for median / p95 / worst-case;
  * the flatness (IoC*N) crossing;
  * the expected-wrong-rune count under five estimators, including round19/C3's
    measured 95.56 % per-glyph reader precision on the LP2 typeface;
  * the margin ratio R = k*_min / E[W], and the pre-registered verdict sentence.

Run: python3 t3_summary.py         (writes out_summary.json)
"""
import json, os
import t3_lib as T

HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, f)))

N_PAIRS = 12955          # adjacent pairs in the 12,956-rune stream
BASE_DOUBLETS = 86

FLOORS = {
    "D-GER":   (0.972, "German — the BINDING register (round18/L7 §C.2); margin 1.46x"),
    "D-VNV":   (1.084, "vowel-dropped English (round18/L7 §C.2)"),
    "D-KJV":   (1.386, "KJV — lowest of D2's four English corpora (round18/L7 §C.2)"),
    "D-LAT":   (1.425, "Latin (round18/L7 §C.2)"),
    "D-ENHO":  (1.483, "held-out English (round18/L7 §C.2)"),
    "D-STALE": (1.500, "the stale figure still quoted at ELIMINATION-LEDGER.md:779"),
    "D-LP1":   (1.585, "LP1 solved-page register (round18/L7 §C.2)"),
    "D-MAX":   (2.339, "Welsh — the highest register floor (round18/L7 §C.2)"),
    "L2-CONTAIN": (100.0 * (BASE_DOUBLETS + 4 * BASE_DOUBLETS ** 0.5) / N_PAIRS,
                   "L2's 4-sd containment breach of M1_ct_keyskip"),
}


def interp_cross(rows, stat, target, key="doublet_rate_pct"):
    """Smallest k at which `stat` of `key` reaches `target`, linearly interpolated.
    Returns (k_star, bracket) or (None, reached_max) if never reached on the grid."""
    prev = None
    for r in rows:
        v = r["stats"][key][stat] if r["k"] else r["stats"][key]["median"]
        if v >= target:
            if prev is None:
                return float(r["k"]), (0, r["k"])
            k0, v0 = prev
            if v <= v0:
                return float(r["k"]), (k0, r["k"])
            return k0 + (r["k"] - k0) * (target - v0) / (v - v0), (k0, r["k"])
        prev = (r["k"], v)
    # never reached: report the MAX over the whole curve (these curves are not all
    # monotone -- P-OAEFAM peaks at k=800 and falls back as the family re-randomises)
    vals = [(r["stats"][key][stat] if r["k"] else r["stats"][key]["median"], r["k"])
            for r in rows]
    return None, max(vals)


def curve(rows, key="doublet_rate_pct"):
    return [{"k": r["k"],
             "median": round(r["stats"][key]["median"], 5),
             "p05": round(r["stats"][key]["p05"], 5),
             "p95": round(r["stats"][key]["p95"], 5),
             "sha_example": r.get("example_sha256")} for r in rows]


def main():
    base = J("out_baseline.json")
    rnd = J("out_random.json")
    tgt = J("out_targeted.json")
    d400 = J("out_decode_L400_LP1.json")
    d120 = J("out_decode_L120_LP1.json")
    dbook = J("out_decode_L12956_KJV.json")

    out = {
        "baseline_sha256": base["baseline_sha256"],
        "pinned_sha256_problem_json": T.PINNED_SHA,
        "sha_matches_pin": base["baseline_sha256"] == T.PINNED_SHA,
        "pc3_pass": base["pc3_pass"], "pc1_pass": base["pc1_pass"],
        "floors": {k: {"pct": v[0], "source": v[1],
                       "doublets_required": int(-(-v[0] / 100 * N_PAIRS // 1))}
                   for k, v in FLOORS.items()},
    }

    # ---------------- channel D: k*(floor) x model ----------------
    models = {
        "P-ADV": rnd["P-ADV"]["rows"],
        "P-RAND": rnd["P-RAND"]["rows"],
        "P-DENSE": rnd["P-DENSE"]["rows"],
        "P-OAE450": tgt["P-OAE450"]["rows"],
        "P-OAE450R": tgt["P-OAE450R"]["rows"],
        "P-OAEFAM": tgt["P-OAEFAM"]["rows"],
    }
    kstar = {}
    for mname, rows in models.items():
        kstar[mname] = {}
        for fid, (val, _src) in FLOORS.items():
            rec = {}
            for stat in ("median", "p95"):
                k, br = interp_cross(rows, stat, val)
                rec[f"k_{stat}"] = None if k is None else round(k, 1)
                rec[f"k_{stat}_bracket"] = br if k is not None else None
                if k is None:
                    rec[f"k_{stat}_max_reached"] = round(br[0], 5)
                    rec[f"k_{stat}_max_at_k"] = br[1]
            kstar[mname][fid] = rec
    out["k_star_doublet"] = kstar
    out["doublet_curves"] = {m: curve(r) for m, r in models.items()}

    # per-substitution doublet yield, measured
    rr = rnd["P-RAND"]["rows"]
    y = {}
    for r in rr:
        if r["k"]:
            y[r["k"]] = round((r["stats"]["doublets"]["median"] - BASE_DOUBLETS) / r["k"], 5)
    out["doublets_added_per_substitution"] = {
        "P-RAND_by_k": y,
        "P-RAND_asymptotic_analytic": round(2.0 / 28.0, 5),
        "P-ADV_worst_case": 2.0,
        "note": "random: each substitution touches 2 adjacent pairs and matches its new "
                "neighbour with prob ~1/28 each -> 2/28 = 0.0714 doublets per changed rune; "
                "adversarial: exactly 2 while +2 sites last (441 of them on this stream)",
    }

    # ---------------- channel I: flatness ----------------
    ioc_p99 = base["ioc_uniform_null"]["p99"]
    out["ioc_flatness"] = {
        "uniform_null_p99": ioc_p99,
        "uniform_null_mean": base["ioc_uniform_null"]["mean"],
        "baseline": base["baseline"]["ioc_norm"],
        "english_reference": 1.73,
        "curves": {m: curve(r, "ioc_norm") for m, r in models.items()},
        "crossings_p99": {m: (lambda kb: {"k_median": None if kb[0] is None else round(kb[0], 1)})(
            interp_cross(r, "median", ioc_p99, "ioc_norm")) for m, r in models.items()},
    }

    # ---------------- the targeted headline points ----------------
    out["targeted_exact_points"] = {
        "ALL450_clusterer_alternative": {
            k: tgt["ALL450_exact"][k] for k in
            ("sha256", "doublets", "doublet_rate_pct", "ioc_norm", "entropy_bits",
             "lag1_suppression_pct", "s_star", "draws_extra", "delta_chi2_over_df",
             "delta_max_abs_z", "line_break_doublets", "line_initial_chi2")},
        "ALL450_adversarial_within_family": {
            k: tgt["ALL450_adversarial_within_family"][k] for k in
            ("sha256", "doublets", "doublet_rate_pct", "ioc_norm", "lag1_suppression_pct",
             "delta_max_abs_z", "line_initial_chi2")},
        "ALLFAMILY_adversarial_within_family": {
            k: tgt["ALLFAMILY_adversarial_within_family"][k] for k in
            ("sha256", "doublets", "doublet_rate_pct", "ioc_norm", "lag1_suppression_pct",
             "delta_max_abs_z", "line_initial_chi2")},
        "P-COLLAPSE": {k: tgt["P-COLLAPSE"][k] for k in
                       ("sha256", "doublets", "doublet_rate_pct", "ioc_norm",
                        "lag1_suppression_pct")},
        "located_doublet_potential": tgt["located_doublet_potential"],
    }

    # ---------------- channel K: the decode ----------------
    def krow(d):
        return [{"k_book": r["k_book"], "eps": round(r["eps"], 5), "k_cell": r["k_cell"],
                 "score_correct_median": round(r["score_correct"]["median"], 3),
                 "score_correct_p05": round(r["score_correct"]["p05"], 3),
                 "recovery_median": round(r["recovery_correct"]["median"], 4),
                 "recovery_graceful_ideal": round(r["recovery_rigid_truekeyidx"]["median"], 4),
                 "derail_fraction": round(r["derail_fraction"], 3),
                 "nskip_error_median": r["skip_count_error"]["median"],
                 "nskip_error_p95": r["skip_count_error"]["p95"],
                 "score_wrong_median": round(r["score_wrong"]["median"], 3),
                 "separated": r["separated"]} for r in d["rows"]]

    out["decode"] = {
        "conditionals": d400["conditionals"],
        "gate_F0": d400["gate_F0"],
        "L120_LP1": {"rows": krow(d120), "K_REC": d120["K_REC_k_book"],
                     "K_SEP": d120["K_SEP_k_book"], "reps": d120["reps"]},
        "L400_LP1": {"rows": krow(d400), "K_REC": d400["K_REC_k_book"],
                     "K_SEP": d400["K_SEP_k_book"], "reps": d400["reps"]},
        "L12956_KJV": {"rows": krow(dbook), "K_REC": dbook["K_REC_k_book"],
                       "K_SEP": dbook["K_SEP_k_book"], "reps": dbook["reps"]},
    }

    # ---------------- channel S: n_skips, I1's language-independent discriminator ----
    bk = {r["k_book"]: r for r in dbook["rows"]}
    out["n_skips_channel"] = {
        "why": "round19/I1 §: n_skips is a language-independent discriminator — at full book "
               "the correct key infers 418/418 EXACTLY and a wrong key infers 1537. Its "
               "discriminating margin is 1537-418 = 1119 draws.",
        "analytic_form_is_stream_dependent": True,
        "analytic_draw_count_baseline": base["baseline"]["draws_extra"],
        "analytic_note": "round18/L2's 373.6 is rho*n with rho derived by INVERTING the "
                         "observed doublet rate, so it inherits the doublet curve exactly: "
                         "it is the 'draws_extra' series in doublet_curves' sibling keys.",
        "inferred_form_full_book": {
            str(k): {"nskip_error_median": bk[k]["skip_count_error"]["median"],
                     "nskip_error_p95": bk[k]["skip_count_error"]["p95"],
                     "margin_retained_pct": round(
                         100.0 * (1119 - bk[k]["skip_count_error"]["p95"]) / 1119, 2)}
            for k in sorted(bk)},
    }

    # ---------------- the decision number ----------------
    R9_AGREE, R9_N = 0.9693, 5207
    FB_AGREE = 0.980
    C3_READER = 0.9556           # round19/C3 G-A2, per-glyph precision on the LP2 typeface
    est = {
        "E_upper_R9": {
            "value": round((1 - R9_AGREE) * 12956),
            "how": "(1 - 0.9693) x 12,956 — EVERY R9 disagreement charged to canon",
            "source": "retranscribe/FINDINGS.md",
            "honest": "an upper bound the audit itself rejects; R9 attributes 0 of its 103 "
                      "loci to canon (15 DP edge artifacts, 3 high-cost misreads on SOLVED "
                      "pages, 85 whole-line read failures on 45-47)"},
        "E_upper_frontB": {
            "value": round((1 - FB_AGREE) * 12956),
            "how": "(1 - 0.980) x 12,956 — every frontB disagreement charged to canon",
            "source": "round12/frontB/RESULTS.md"},
        "E_located": {
            "value": 450,
            "how": "the located O/A/AE candidate set taken at face value",
            "source": "independent-read/oae_mismatch.json",
            "honest": "these are CANDIDATES; the clusterer, not canon, is the party FINDINGS "
                      "judges wrong ('no blatant single-glyph error')"},
        "E_attributed": {
            "value": 0,
            "how": "the audits' own bucket attribution",
            "source": "retranscribe/FINDINGS.md 'Zero disagreements are real, localized "
                      "rune-value errors in canon'"},
        "E_C3_corrected": {
            "value": 0,
            "how": ("round19/C3 measures an INDEPENDENT per-glyph reader at %.2f %% on the LP2 "
                    "typeface, i.e. a reader error rate of %.2f %%. R9's observed DISAGREEMENT "
                    "rate is only %.2f %% and frontB's %.2f %% — both BELOW the reader's own "
                    "error rate. Under p_disagree ~= p_reader + p_canon, p_canon <= "
                    "%.2f - %.2f < 0, i.e. the disagreements are fully explained by the "
                    "instrument and carry no evidence of canon error."
                    % (100 * C3_READER, 100 * (1 - C3_READER), 100 * (1 - R9_AGREE),
                       100 * (1 - FB_AGREE), 100 * (1 - R9_AGREE), 100 * (1 - C3_READER))),
            "reader_precision": C3_READER,
            "implied_canon_error_pct": round(100 * ((1 - R9_AGREE) - (1 - C3_READER)), 3),
            "source": "round19/C3/RESULTS.md gate G-A2 (95.56 %, 172/180 on the LP2 face)"},
    }
    out["expected_wrong_runes"] = est

    # margin: the smallest k* over every LOAD-BEARING channel
    binding = {
        "doublet D-GER worst case (P-ADV)": kstar["P-ADV"]["D-GER"]["k_median"],
        "doublet D-GER, realistic worst case (adversarial within the located 450)":
            "reached at 450 (1.0884 %) — see targeted_exact_points",
        "doublet D-GER median, uniform random": kstar["P-RAND"]["D-GER"]["k_median"],
        "doublet D-KJV worst case (P-ADV)": kstar["P-ADV"]["D-KJV"]["k_median"],
        "doublet D-KJV median, uniform random": kstar["P-RAND"]["D-KJV"]["k_median"],
        "doublet D-STALE (1.50 %) worst case (P-ADV)": kstar["P-ADV"]["D-STALE"]["k_median"],
        "doublet D-STALE median, uniform random": kstar["P-RAND"]["D-STALE"]["k_median"],
        "decode K-REC full book": dbook["K_REC_k_book"],
        "decode K-SEP full book": dbook["K_SEP_k_book"],
    }
    out["binding_k_star"] = binding

    E = est["E_upper_R9"]["value"]
    kmin_stat = kstar["P-RAND"]["D-GER"]["k_median"]
    out["verdict"] = {
        "E_W_used_for_the_ratio": E,
        "E_W_rationale": "the CRUDEST estimator, charging every audit disagreement to canon; "
                         "the audits' own attribution and C3's reader measurement both give 0",
        "k_star_random_median_D_GER": kmin_stat,
        "ratio_R_statistic_channel": round(kmin_stat / E, 2) if kmin_stat else None,
        "k_star_adversarial_D_GER": kstar["P-ADV"]["D-GER"]["k_median"],
        "decode_channel_K_REC_full_book": dbook["K_REC_k_book"],
    }
    json.dump(out, open(os.path.join(HERE, "out_summary.json"), "w"), indent=1)

    print(json.dumps(out["verdict"], indent=1))
    print("\n--- k*(floor) for the doublet deficit ---")
    for m in ("P-ADV", "P-RAND", "P-DENSE", "P-OAE450", "P-OAE450R", "P-OAEFAM"):
        for f in ("D-GER", "D-KJV", "D-STALE", "L2-CONTAIN"):
            r = kstar[m][f]
            print(f"  {m:10s} {f:11s} k_med={r['k_median']}  k_p95={r['k_p95']}"
                  f"{'  (NEVER reached; curve max ' + str(r.get('k_median_max_reached')) + ' at k=' + str(r.get('k_median_max_at_k')) + ')' if r['k_median'] is None else ''}")
    print("\n--- E[W] ---")
    for k, v in est.items():
        print(f"  {k:18s} {v['value']}")


if __name__ == "__main__":
    main()
