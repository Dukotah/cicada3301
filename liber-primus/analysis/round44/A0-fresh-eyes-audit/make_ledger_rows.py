"""Write this lane's ledger rows (ledger_rows.json) and merge them into liber-primus/LEDGER.json.

Idempotent: a row whose id is already in the ledger is replaced, counts are recomputed.
"""
import collections
import json
import os

import lp2

HERE = os.path.dirname(os.path.abspath(__file__))
A0 = "liber-primus/analysis/round44/A0-fresh-eyes-audit/"
D1 = "liber-primus/analysis/round44/D1-depth-28-42/"
J = lambda f: json.load(open(os.path.join(HERE, f)))
fo, rp, rk, wl, dp = J("foundation.json"), J("repeats.json"), J("running_key_gate.json"), J("wordlen.json"), J("depth_pairs.json")
d1 = json.load(open(os.path.join(HERE, "..", "D1-depth-28-42", "results.json")))
pw = J("instrument_power_letterwise.json")
DATE = "2026-11-12"


def base(i, lane, hyp, status, **kw):
    r = {"id": i, "lane": lane, "hypothesis": hyp, "status": status, "round": "44/A0", "date": DATE,
         "supersedes": [], "superseded_by": None}
    r.update(kw)
    return r


rows = [
    base("R44-A0-FRESH-EYES-AUDIT", "A0-fresh-eyes-audit",
         "Something in Rounds 1-43 or in the repository was left over: a dropped lead, a closure wider than its "
         "measurement, an instrument or loader defect, an unexamined input, or a premise every lane shares.",
         "audit", threshold="FOUND-ERROR / NO-ERROR-FOUND per item (doctrine R6); every item cited to file and line",
         threshold_fixed_in_advance=True, positive_control="n/a (audit)",
         result="FOUND-ERROR, many. Thirteen partition readers plus coordinator re-verification. Headline items: the oracle "
                "failed a correct continuous key (fixed); corpus.parse() flagged the book head and tail as solved and two "
                "Round 26 lanes were aimed mid-book (fixed); the plaintext is spelled one rune per letter by the cleartext "
                "word lengths; natural-language running keys are excluded key-free by monogram flatness; the 'repeated "
                "7-gram' is a mis-recorded 6-rune two-word repeat; pages 28/42 are position-wise related; four finite "
                "high-prior key spaces were never swept at power; seven shared decoder premises are unrepresented. "
                "See AUDIT.md sections 1-6.",
         coverage="All round folders 10-43, the campaign-era folders, research/ Rounds 1-9, corpus/, the ledger, ceiling, "
                  "pickup and oracle layers. Reader claims marked [R] in AUDIT.md were not independently re-run.",
         not_covered="Image-level checks (the page renders are gitignored and absent from the audit checkout); any network "
                     "source; the stale ledger rows listed in AUDIT.md section 6 were not edited.",
         evidence=[A0 + "AUDIT.md", A0 + "readers/"], reproduce="see AUDIT.md section 8",
         reopens_if="n/a (audit; each item carries its own)"),
    base("R44-A0-ORTHOGRAPHY-LETTERWISE", "A0-fresh-eyes-audit",
         "The plaintext of pages 0-54 is spelled in the solved pages' multigraph orthography (THE = two runes).",
         "measured", threshold="descriptive: KS and chi-square of the LP2 word-length histogram against each English text "
                               "spelled letter-wise and multigraph; no decision threshold was fixed in advance",
         threshold_fixed_in_advance=False, positive_control="n/a (cleartext statistic); instrument-power plant passed 24/24",
         result={"lp2": wl["lp2"], "texts": wl["n_texts"], "letterwise_better_by_ks": wl["letterwise_fits_better_by_ks"],
                 "letterwise_better_by_chi2": wl["letterwise_fits_better_by_chi2"],
                 "best_letterwise": {k: wl["texts"][0][k] for k in ("text", "ks_letterwise", "chi2_letterwise")},
                 "best_multigraph_ks": wl["best_multigraph_ks"], "best_multigraph_chi2": wl["best_multigraph_chi2"],
                 "ks_critical_05": wl["ks_critical_05"],
                 "instrument_power_letterwise_L120": "correct-key pmax 13.5-18.8, 24/24 clear, recovery 0.999 (beam_v3 + panel-R36)",
                 "verdict": "REFUTED as the default: the histogram fits letter-wise English (THE = three runes) and not the "
                            "solved-page spelling. The instrument recovers letter-wise plants, so no sweep negative is voided."},
         coverage="61 committed English texts (data/keys), middle 70 % of each file; two spellings; LP2's 2,928 words. "
                  "Readers B and I add the solved pages (two-rune words 24.3 % vs 15.9 %, z = 4.9) and 21,698 windows.",
         not_covered="A non-English or article-free register that happens to match; partial unfolding (TH only) versus full "
                     "letter-wise is not separated; pf_v4_12 head-screen power for letter-wise text is a reader probe "
                     "(0.975-0.983), not a lane result.",
         evidence=[A0 + "wordlen.py", A0 + "wordlen.json", A0 + "instrument_power_letterwise.py", A0 + "readers/B-rounds-1-10b.md",
                   A0 + "readers/I-rounds-36-38.md"],
         reproduce="python3 " + A0 + "wordlen.py", supersedes=["B-19"],
         reopens_if="a natural English text in multigraph spelling is shown to fit the LP2 histogram; or a solved page of "
                    "LP2 0-54 shows a digraph rune in its plaintext"),
    base("R44-A0-RUNNINGKEY-MONOGRAM-GATE", "A0-fresh-eyes-audit",
         "The LP2 key is a natural-language running key (any text, any offset, either sign, any skip relation) over an "
         "English plaintext.", "negative",
         threshold="family excluded if the predicted and planted monogram chi-square of such a ciphertext exceeds the "
                   "observed value by more than 10x at N = 12,956 (fixed before the plants were run)",
         threshold_fixed_in_advance=True, positive_control="passed",
         control_detail=f"12 planted running-key ciphertexts (English on English, both spellings, both signs, anti-repeat "
                        f"key-skip filter on): monogram chi2 {rk['plant_min_chi2']:.0f} to "
                        f"{max(x['monogram_chi2'] for x in rk['planted_running_key_ciphertexts']):.0f}; "
                        f"LP2 observed {rk['observed_monogram_chi2_28df']:.1f} on 28 df.",
         result={"observed_monogram_chi2_28df": rk["observed_monogram_chi2_28df"],
                 "predicted": {k: v["predicted_monogram_chi2"] for k, v in rk["cells"].items()},
                 "key_marginal_bound": "the key's own monogram distribution must be uniform to within about a 15 % English admixture",
                 "verdict": "NEGATIVE at the family level, key-free. Discharges R12-C2, the remainder of "
                            "R26-B-KEYTEXT-RUNNINGKEY-SKIPAWARE and the Round 42 10-keytext refetch without a decode."},
         coverage="Any additive combination of an English plaintext with a key whose symbols are natural-language letters used "
                  "one per rune, at any offset, with or without the anti-repeat filter.",
         not_covered="Keys derived from a text by hashing or any transform that flattens the monogram distribution; a text key "
                     "over a non-language plaintext; non-additive combination.",
         null="analytic (convolution of two measured English distributions) plus 12 plants",
         evidence=[A0 + "running_key_gate.py", A0 + "running_key_gate.json"],
         reproduce="python3 " + A0 + "running_key_gate.py",
         reopens_if="the canonical ciphertext's monogram distribution is shown to be mis-transcribed at the 20x level (it is not)"),
    base("R44-A0-DJUBEI-REPEAT", "A0-fresh-eyes-audit",
         "The repeated n-gram at page 27 offset 28 and page 54 offset 70 is a chance event at the 13 % level "
         "(ARMADA-20-FINDINGS) / a 7-gram at 0.5 % (round43 F3).", "measured",
         threshold="descriptive; three expectations reported so the choice of statistic is visible",
         threshold_fixed_in_advance=False, positive_control="n/a (counting statistic); Monte Carlo cross-check 0/3000",
         result={"the_repeat": rp["the_repeat"], "expected_counts": rp["expected_counts_under_uniform_runes"],
                 "observed_closed_word_repeats_ge4_runes": rp["observed_closed_word_repeats_ge4_runes"],
                 "monte_carlo": rp["monte_carlo"], "offsets_of_the_two_sites": rp["offsets_of_the_two_sites"],
                 "rigid_lag_6395_z": fo["lag_scan_rigid"]["z_at_6395"],
                 "verdict": "Both prior records are wrong. It is a 6-rune repeat of two whole words (3+3), the last two words "
                            "of the unsolved book; the '7th rune' is the first rune of the solved page AN END. Word-aware "
                            "expectation 9.2e-5 (closed whole-word repeat) to 5.9e-3 (identical boundary pattern)."},
         coverage="All repeated n-grams, n >= 5, in the 12,956-rune stream; word-aware nulls with the cleartext skeleton fixed.",
         not_covered="Why it is there. No reset at a visible boundary puts the two sites at one key position; the page images "
                     "of both sites were not inspected (renders absent from the audit checkout).",
         evidence=[A0 + "repeats.py", A0 + "repeats.json"], reproduce="python3 " + A0 + "repeats.py",
         reopens_if="n/a (measurement); use it as a free constraint on any generator hypothesis that reaches both sites"),
    base("R44-A0-PAGEPAIR-28-42", "A0-fresh-eyes-audit",
         "No two unsolved pages are related position by position (no depth anywhere; 'never rewound').", "measured",
         threshold="descriptive; chi-square of (a_i - b_i) mod 29 on 28 df over all aligned page pairs, statistic fixed before "
                   "its symmetric/antisymmetric split was looked at",
         threshold_fixed_in_advance=False, positive_control="n/a here; the depth reading has its own controlled lane (R44-D1-DEPTH-28-42)",
         result={"pairs_tested": dp["pairs_tested"], "pair": [28, 42],
                 "chi2_28df": dp["pair_28_42"]["chi2_28df"], "sym_chi2_14df": dp["pair_28_42"]["sym_chi2_14df"],
                 "antisym_chi2_14df": dp["pair_28_42"]["antisym_chi2_14df"], "kappa": dp["pair_28_42"]["kappa"],
                 "sym_chi2_by_offset": dp["pair_28_42"]["offsets"], "next_best_pair_chi2": dp["top_by_chi2"][1]["chi2_28df"],
                 "family_wise_p": dp["family_wise"]["x_pairs"],
                 "verdict": "One pair stands out: chi2 74.1 (p 4.8e-6), almost wholly symmetric, exact alignment only, in every "
                            "45-rune block. Family-wise about 0.006 on the a-priori statistic; suggestive, not established."},
         coverage="1,326 offset-0 pairs of unsolved pages with >= 100 runes; offsets +-4 for the outlier.",
         not_covered="Pair x offset cells beyond the outlier (a reader scanned 331,908 and found nothing else); sections as "
                     "units; what the relation is.",
         evidence=[A0 + "depth_pairs.py", A0 + "depth_pairs.json", A0 + "readers/K-primary-artifacts.md"],
         reproduce="python3 " + A0 + "depth_pairs.py",
         reopens_if="a second pair shows the same statistic, or a plaintext numbering reproduces the difference spectrum"),
    base("R44-D1-DEPTH-28-42", "D1-depth-28-42",
         "Pages 28 and 42 were enciphered additively with the same key values at the same page offsets, both plaintexts "
         "English (letter-wise or multigraph in Gematria order, or letter-wise in alphabet order).", "negative",
         round="44/D1", threshold="PREREG.md section 5: FLAGGED if S_real >= (S_null_max + S_plant_min)/2; NEGATIVE if "
                                  "S_real <= S_null_max with the control passed",
         threshold_fixed_in_advance=True, positive_control="passed",
         control_detail="12 planted depth pairs per cell from held-out texts, 5 % of positions overwritten: recovery "
                        + "; ".join(f"{c} {min(x['recovery'] for x in v['plants']):.2f}-{max(x['recovery'] for x in v['plants']):.2f} "
                                    f"({v['plants_at_0.70']}/12 at >= 0.70)" for c, v in d1["cells"].items()),
         result={c: {"S_real": v["real"]["S"], "S_null_max": v["S_null_max"], "S_null_mean": v["S_null_mean"],
                     "S_null_sd": v["S_null_sd"], "S_plant_min": v["S_plant_min"], "verdict": v["verdict"]}
                 for c, v in d1["cells"].items()},
         coverage="One page pair, three encodings, 40 nulls per cell (30 other aligned pairs, 10 shifted alignments of the "
                  "real pair). Key-free.",
         not_covered="Any other numbering of the plaintext symbols; a non-English plaintext; key-consuming desync on either "
                     "page; a relation that is not depth.",
         null="40 real-ciphertext nulls per cell, decoded by the same code path",
         evidence=[D1 + "PREREG.md", D1 + "RESULTS.md", D1 + "results.json", D1 + "depth2.py", D1 + "run_d1.py"],
         reproduce="python3 " + D1 + "run_d1.py",
         reopens_if="a numbering other than the three is proposed; or the statistic recurs on a second pair"),
    base("R44-A0-ORACLE-PAGE-MODEL", "A0-fresh-eyes-audit",
         "verify_solution.py accepts a correct key of the kind the sweeps hunt (one continuous stream from rune 0 of page 0).",
         "audit", threshold="the oracle's own PASS rule on a planted continuous key", threshold_fixed_in_advance=True,
         positive_control="passed (after the fix): 8/8 plants in four registers recovered under both page models, 8/8 wrong keys rejected",
         result="FOUND-ERROR, fixed. judge_register() decoded every page from K[0] and the self-test planted only that, so a "
                "correct continuous key cleared page 0, failed page 1 and returned FAIL. judge_continuous() now decodes page 1 "
                "from where the stream had reached (window of key offsets, bar at N = window size); the old judge alone still "
                "fails the continuous plant, which the self-test prints.",
         coverage="keyskip1 plants at L=120 in EN_MODERN, LATIN, EN_NOVOWEL, GREEK; pages 0-1.",
         not_covered="Continuity beyond page 1; a stream that starts at a section head; keyskip2/free plants; a combiner constant.",
         evidence=["liber-primus/verify_solution.py", "liber-primus/tests/test_verify_solution.py", A0 + "readers/H-rounds-32-35.md",
                   A0 + "readers/L-ledger-health.md"],
         reproduce="python3 liber-primus/verify_solution.py --selftest", reopens_if="n/a"),
    base("R44-A0-LOADER-CORPUS-PARSE", "A0-fresh-eyes-audit",
         "src/lp/corpus.py parse() hands a lane the unsolved pages of LP2.", "audit",
         threshold="every section mapped onto the SHA-pinned canonical stream", threshold_fixed_in_advance=True,
         positive_control="n/a (audit)",
         result="FOUND-ERROR, fixed in part. An OutGuess note was taken for a plaintext, flagging canonical pages 0-2, the "
                "first 119 runes of page 3 and pages 53-54 as solved (11,107 of 12,956 runes flagged unsolved; now 12,263). The "
                "loader also keeps only the first rune block per section (documented, unchanged) and its sections are not "
                "pages. Affected: R26-A-GEN-SWEEP-FIRST-FIRE (decoded section 19 = page 6 rune 71 .. page 7, at key offset 0), "
                "R26-B-KEYTEXT-RUNNINGKEY-SKIPAWARE (545 runes of three sections), r6_sieve_windows.py, the R38-C2 L17xF7 hash "
                "cell, round10/L3 t6.",
         coverage="All 41 scream314 sections; all callers of corpus.parse() in the tree.",
         not_covered="Re-running the affected lanes (R26-A's prior-dense Perl/TeX/Py2.7-reducer set against the book head is "
                     "still owed).",
         evidence=[A0 + "loader_map.py", "liber-primus/src/lp/corpus.py", A0 + "readers/G-rounds-25-30.md"],
         reproduce="python3 " + A0 + "loader_map.py", reopens_if="n/a"),
    base("R44-A0-PERIODIC-KEY-DRIFT", "A0-fresh-eyes-audit",
         "The LP2 key is periodic (any period from 2 to about 12,000), with or without key-consuming rejections.", "measured",
         threshold="descriptive: z of the lag-L coincidence count for every L, rigid, and a Poisson-smeared matched filter "
                   "for key-consuming skips; no threshold fixed in advance",
         threshold_fixed_in_advance=False,
         positive_control="reader plants only (unregistered): drift-aware detectors recovered periods up to about 1,000-1,500 "
                          "(readers A1, B, F); the coordinator's own scan carries no plant",
         result={"rigid": fo["lag_scan_rigid"], "drift_smeared_lam0.0288": fo["lag_scan_drift_smeared_lam0.0288"],
                 "drift_smeared_lam0.0576": fo["lag_scan_drift_smeared_lam0.0576"],
                 "verdict": "Flat at every lag, rigid and drift-smeared. With the readers' plants this is a measured negative "
                            "for periods up to about 1,000-1,500 under key-skip and for any period under a non-consuming "
                            "filter; it is unpowered above that under key-skip."},
         coverage="Lags 2..12,454 on the flat stream; smeared periods 3..12,355 at two skip rates.",
         not_covered="A pre-registered lane with its own plant; periods above about 1,500 under key-consuming skips; "
                     "non-English plaintext with low coincidence rate.",
         evidence=[A0 + "foundation.py", A0 + "foundation.json", A0 + "readers/A1-campaign-structure.md",
                   A0 + "readers/B-rounds-1-10b.md", A0 + "readers/F-rounds-20-24.md"],
         reproduce="python3 " + A0 + "foundation.py",
         reopens_if="an alignment-EM test (hours) shows structure at periods the smeared filter cannot reach"),
    base("R44-A0-P15-GRID-RULE", "A0-fresh-eyes-audit",
         "The page-15 4x4 number grid carries free numeric information (14/16 cells = 3301 - prime; a key schedule).",
         "measured", threshold="all sixteen cells reproduced by one rule", threshold_fixed_in_advance=True,
         positive_control="n/a (identity check)",
         result="REFUTED: all 16 cells equal |3301 - p_F| with p_0 = 2 and F over the Fibonacci numbers 0, 1, 2, 3, 5, ..., 987 "
                "(primes 2, 3, 5, 7, 13, 23, 43, 79, 149, 263, 463, 829, 1481, 2593, 4507, 7817). No free information; Round 44 "
                "lane P2 as written tests a determined object.",
         coverage="The 16 values as transcribed in round43/F2-inventory/image-channels.md.",
         not_covered="The rule itself as a hint (Fibonacci-indexed primes) for a keystream; the cell order (a reader reports a "
                     "clockwise spiral from the red cell).",
         evidence=[A0 + "p15_grid.py", A0 + "readers/J-rounds-39-43.md"], reproduce="python3 " + A0 + "p15_grid.py",
         reopens_if="the image shows a cell value different from the transcription"),
    base("R44-A0-UNREPRESENTED-PREMISES", "A0-fresh-eyes-audit",
         "A correct key would be recognised by the instrument of record whatever the combiner constant, reflection, stream "
         "start, key stall, rejection style or plaintext numbering.", "open",
         threshold="per premise: plant the correct key through pf_v4_12 + beam_v3 and read the score", threshold_fixed_in_advance=False,
         positive_control="reader probes (unregistered) hand the instrument a correct key and get noise for: C=P+K+1, Beaufort, "
                          "Atbash-then-add, key burned at word boundaries, deletion-type avoidance under keyskip1/2",
         result="OPEN. Seven shared premises are unrepresented (AUDIT.md 1.7). Proposed remedy: a language-model-free "
                "'blind' adjudicator, possible because a key-skip at (i, j) is admissible only if K[j+1]-K[j] = C[i]-C[i-1], "
                "so the key can be tracked without a language model and paths scored by index of coincidence, which is "
                "invariant to language, orthography, plaintext numbering, a combiner constant, Atbash and Beaufort. "
                "Feasibility measured on plants (blind_adjudicator_poc.py): at L=120, 480/480 plants above the maximum of "
                "400 wrong keys (null IoC x29 1.14 +- 0.06, max 1.41; plant minimum 1.43), across English letter-wise, "
                "English multigraph and Latin, as written / randomly relabelled / +7 constant / Beaufort.",
         coverage="none (queue item)", not_covered="everything; this row exists so the premises are queryable",
         evidence=[A0 + "AUDIT.md", A0 + "readers/H-rounds-32-35.md", A0 + "readers/E-round-19.md", A0 + "readers/F-rounds-20-24.md",
                   A0 + "readers/D-round-18.md"],
         reproduce="python3 " + A0 + "blind_adjudicator_poc.py ; see also readers/probes/H_plant_probe.py, f_constructions.py", priority="high",
         reopens_if="n/a (open)"),
    base("R44-A0-UNSWEPT-FINITE-SPACES", "A0-fresh-eyes-audit",
         "The enumerable high-prior seed spaces have been swept at power: the 2012-2014 clock-second band for glibc, Perl and "
         "PHP; Perl rand's whole 2^32; the whole bash 4.2 state cycle; TeX's default seeds.", "partially-run",
         threshold="n/a", threshold_fixed_in_advance=False, positive_control="n/a",
         notes="Two of these were run the same day through the blind adjudicator: Perl's whole 2^32 (R44-S1-BLIND-PERL-2E32) and the "
               "glibc clock-second band in two reductions (R44-S2-BLIND-GLIBC-CLOCK). Still unswept at power: PHP mt_rand's clock band, "
               "the rest of glibc's 2^32, the bash 4.2 state cycle, TeX's 8,627 default seeds, and every stream start other than rune 0 "
               "of page 0.",
         result="As found by the audit: NEVER RUN at power. Clock seconds: only bash 3.2 and Py2.7 integer seeds cover every second under the "
                "repaired instrument (Round 8's per-second sweep was a rigid 48-rune English kernel). Perl: the only generator "
                "with signed first-party evidence (round19/C3 section 2c'), family exactly 2^32, about 25k seeds decoded, the "
                "one prior-dense run mis-targeted (R44-A0-LOADER-CORPUS-PARSE). bash 4.2: the swept 'full orbit' is 3.6 % of the "
                "single 2,147,483,646-state LP64 cycle (ILP32 cycle 343,896), and seed = offset on that cycle (round19/G1). "
                "TeX pgf: 8,627 default seeds, pilot only. Two server timestamps (1396427599, 1389478032) recorded by "
                "round43/F5b are absent from the seed prior.",
         coverage="Perl 2^32 and the glibc clock-second band (see the two R44-S rows); nothing else",
         not_covered="PHP clock band; glibc beyond the clock band; bash 4.2 cycle; TeX default seeds; other stream starts",
         evidence=[A0 + "AUDIT.md", A0 + "readers/E-round-19.md", A0 + "readers/L-ledger-health.md", A0 + "readers/D-round-18.md",
                   A0 + "readers/B-rounds-1-10b.md"],
         reproduce="n/a", priority="high", reopens_if="n/a (partially-run: the remainder is listed in not_covered)"),
]

json.dump(rows, open(os.path.join(HERE, "ledger_rows.json"), "w"), indent=1, ensure_ascii=False)
led_path = os.path.join(lp2.LP, "LEDGER.json")
led = json.load(open(led_path, encoding="utf-8"))
ids = {r["id"] for r in rows}
led["entries"] = [e for e in led["entries"] if e["id"] not in ids] + rows
c = collections.Counter(e["status"] for e in led["entries"])
led["counts"] = {"total": len(led["entries"]), "by_status": dict(sorted(c.items()))}
with open(led_path, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(led, indent=1, ensure_ascii=False) + "\n")
print("ledger rows:", led["counts"])
