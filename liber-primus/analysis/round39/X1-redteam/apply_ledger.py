#!/usr/bin/env python3
"""Round 39 X1: apply audited lane rows/patches to LEDGER.json. Idempotent: rebuilds from LEDGER.pre-x1.json."""
import json, os, copy, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); R39 = os.path.dirname(HERE)
LP = os.path.abspath(os.path.join(R39, "..", ".."))
doc = json.load(open(os.path.join(HERE, "LEDGER.pre-x1.json"), encoding="utf-8")); E = doc["entries"]; byid = {e["id"]: e for e in E}
PFX = "liber-primus/analysis/round39/"
jl = lambda p: json.load(open(os.path.join(R39, p), encoding="utf-8"))


def add(e):
    assert e["id"] not in byid, e["id"]
    E.append(e); byid[e["id"]] = e


# ---- P1 (audit row as filed; X1 annotation)
p1 = jl("P1-measured-ceiling/ledger.json")["entries"][0]
p1["evidence"] = [PFX + "P1-measured-ceiling/" + x for x in ("RESULTS.md", "PREREG.md", "check_ceiling.py", "checker_output.txt")] + ["liber-primus/MEASURED-CEILING.md"]
p1["x1_r39"] = ("X1/R39 FOUND-ERROR on the page (register scope of 14 controls, post-data null on 3 rows, Py2.7 pair / SHA-KDF / PHP power scope, public-pad power omitted, N5/N4 pending, section-3 omissions, rebuild command flags) and 3 in the checker "
                "(prefix admissibility, no threshold_fixed_in_advance or register-scope check, forbidden list missing R7's 'unsolvable'/'frontier is complete'). Page and checker edited; check_ceiling.py PASS after. See analysis/round39/X1-redteam/RESULTS.md.")
add(p1)

# ---- T1 (normalised: lane file had no hypothesis/coverage; positive_control prose)
raw = jl("T1-standing-nulls/ledger.json")
raw = raw["entries"][0] if "entries" in raw else raw
t1 = {"id": "R39-T1-STANDING-NULLS", "round": 39, "lane": "T1", "lane_dir": "T1-standing-nulls", "date": "2026-10-31", "status": "measured",
      "hypothesis": "Two standing defects of the null instrument can be repaired without changing any stored verdict: (a) a degenerate-decode flag (mds <= 6 or IoC*N >= 4.24) as an optional header-driven SWEEPROW field plus pmax_nondegenerate; (b) a generic key-matched null benchmark that reproduces the I2-R38 X4 L=120 bar 6.994 from stored rows; and bar_v3 'free' at L=120 should use the 12-register node.",
      "positive_control": "passed",
      "control_detail": "tests/test_standing_nulls.py (7 tests): constant decode flagged degenerate vs random decode not; header-driven 13/14-field validation; key-matched fixture 6.994 (X1 recomputed 6.99419 for keyskip1 and keyskip2 from null_rows_L120.jsonl); free L=120 node 15.30. X1: both adjudicate.py copies byte-identical; Round 35 and Round 36 stores validate with the stock function; bar_v3(1e6,120,'free')=15.30, panel='r32'=17.43. Fail-then-pass on pre-patch code is by construction (no git to run the old code).",
      "coverage": "Tooling only: adjudicate.py x2 copies (round19/I2, round32/I2), SWEEPROW.md field 13 (optional), benchmark/bars_keymatched.py, bars_v3.py free L=120 node, tests/test_standing_nulls.py (7), ci.yml pytest step. No decodes.",
      "result": "all green; key-matched fixture 6.99419 (ks1 and ks2); free L=120 N=1e6 bar 17.43 -> 15.30 (N=1e5 15.89 -> 14.08). No cipher claim.",
      "not_covered": "bar_keymatched full beam_v3 path is exercised only by a toy family in CI; to_row does not emit the degenerate field by default (lanes opt in; SWEEPROW/2 bump undecided); any earlier verdict used the higher free L=120 bar (conservative).",
      "reopens_if": "a sweep needs a key-matched bar for a ciphertext-derived key family (run bars_keymatched end-to-end against beam_v3); the coordinator makes with_degenerate the default (SWEEPROW/2).",
      "evidence": [PFX + "T1-standing-nulls/RESULTS.md", PFX + "T1-standing-nulls/PREREG.md", "liber-primus/tests/test_standing_nulls.py", "liber-primus/benchmark/bars_keymatched.py"],
      "lane_ledger_raw": raw,
      "x1_r39": "X1/R39: NO-ERROR-FOUND on the code; lane row normalised (hypothesis/coverage added, positive_control prose -> passed + control_detail)."}
add(t1)
byid["R34-I1-V3-NULL-OF-RECORD"]["r39_t1"] = "Round 39 T1: bar_v3(N, 120, 'free') now returns the 12-register node (15.30 at N=1e6 vs the R34 nine-register 17.43); panel='r32' restores the old node. Earlier free L=120 verdicts used the higher bar (conservative)."

# ---- C1 (normalised) + the 18 F5 cells
raw = jl("C1-sense-similarity/ledger.json")["entries"][0]
c1 = copy.deepcopy(raw); c1["lane_dir"] = "C1-sense-similarity"
c1["sweep_store"] = "liber-primus/analysis/round39/C1-sense-similarity/sweep_rows.jsonl"
c1["evidence"] = ["liber-primus/" + x if x.startswith("analysis/") else x for x in c1["evidence"]]
c1["positive_control"] = "passed"
c1["control_detail"] = ("control.json: 18/18 plants over 9/9 variant-mode cells (2 plants each, sigma +-1), recovery >= 0.90, pmax120 >= bar_v3(1e6,120)=9.235, pmax240 >= 9.514. "
                        "X1 re-ran 4 plants in 2 cells with a fresh seed (D-R29/A3, L-R28/A2; rerun_c1_controls.json): pmax120 20.81/19.43/20.39/18.78, recovery 0.996-1.0, wrong-s decodes 0.31-4.39.")
c1["three_conditionals"] = {"key_space": "WordNet 3.1 first-synset hypernym depth (D) and lexicographer-file index (L), mod 29/28, of LP1 codebook words, rho=1, pages 0-2, start s",
                            "transition_model": "keyskip1 only (A3); A1/A2 direct shifts judged vs the keyskip1 bar; no keyskip2/free",
                            "adjudicator_register": "panel-R36 12 registers; plants EN_MODERN only"}
c1["reopens_if"] = "a pairwise similarity (path/Lin/embedding), non-first-sense, other-lexicon or clue-specific F5 reading is stated with a control; or the 18 F5 cells' own clue content is operationalized."
c1["x1_r39"] = ("X1/R39: PREREG mtime 10:06:50 precedes build_index 10:07:01 / index 10:07:02 / control 10:07:18 / sweep 10:10:51 (weak evidence, no external timestamp). 5 words and all 468 covered rows re-derived from the WordNet files by independent code: 0 mismatches. "
                "Inherited R38 lemma-rule defects are not disclosed in RESULTS (22 'is' tokens -> noun 'i' depth 5 lex 27; 'lives' -> adj 'liv' 0/0); uncovered words and root/adj.all both map to 0. "
                "The lane's patch (id O4-MATRIX-H-F5, status 'measured (bounded)') names no cell and repeats the Round 38 X1 row-9 schema errors; replaced by x1_r39_cell_moves on R36-O4-CLUE-COVERAGE.")
add(c1)
F5 = ["H10xF5", "H1xF5", "H2xF5", "H4xF5", "H5xF5", "H8xF5", "H9xF5", "L10xF5", "L11xF5", "L14xF5", "L18xF5", "L1xF5", "L2xF5", "L4xF5", "L5xF5", "L7xF5", "L8xF5", "L9xF5"]
r38 = json.load(open(os.path.join(R39, "..", "round38", "X1-redteam", "o4_recount_r38.json"), encoding="utf-8"))
assert len(F5) == 18 and set(F5) == set(r38["NEVER_cells"])
o4 = byid["R36-O4-CLUE-COVERAGE"]
o4["x1_r39_cell_moves"] = {"NEVER_to_PARTIAL": F5,
                           "reason": ("Round 39 C1 operationalized the semantic (F5) family once, as sense POSITION of the LP1 codebook words (WordNet 3.1 first-synset hypernym depth and lexicographer-file index) used as a key/direction. "
                                      "That is one generic reading of the family, not each clue's own semantic content (e.g. L9 'program your mind', L1 'test the knowledge'), so the 18 cells move NEVER -> PARTIAL, not TRIED."),
                           "counts_after_R39_C1": {"NEVER": 0, "TRIED": 35, "TRIED-ENGLISH-ONLY": 21, "TRIED-LEGACY-BEAM": 25, "PARTIAL": 25, "NO-OPERATION-STATED": 34, "sum": 140},
                           "evidence": PFX + "X1-redteam/RESULTS.md"}
f02 = byid["F-02"]
f02["r39_c1"] = "Round 39 C1: 'meaning' as first-synset hypernym depth and lexicographer-file index (WordNet 3.1), mod 29/28, A1/A2/A3, pages 0-2, keyskip1: N=14,112, best 5.351 vs actual-N bar 7.59 (A3) / 4.004 vs 6.63 (shift); negative (R39-C1-SENSE-SIMILARITY). F-02 stays partially-run: pairwise similarity, other senses and lexicons, clue-specific readings untested."
if "Round 39 C1" not in f02["coverage"]:
    f02["coverage"] = f02["coverage"] + " | Round 39 C1: 'meaning' as WordNet 3.1 first-synset hypernym depth and lexicographer-file index (not a similarity metric), 14,112 decodes, all below bars (best 5.35 vs 7.59)."

# ---- S1/S2 not run
add({"id": "R39-S1-S2-WINDOWS", "round": 39, "lane": "S1/S2", "date": "2026-10-31", "status": "never-run",
     "hypothesis": "Round 39 sandbox lanes S1 (S2 window 2 recovery and further Py2.7-MT exact windows) and S2 (PHP retry with persisted control and FPR) run after the 2026-11-01 00:00 UTC quota reset.",
     "coverage": "ZERO. Not run in Round 39; moved to Round 40 (the Vercel quota was locked until 2026-11-01 00:00 UTC and the laptop cannot run the sweeps). No window, seed or PHP row was added.",
     "positive_control": "n/a (not run)",
     "not_covered": "S2 window 2 (snap_ff0SWU76EW32OqbWJvp00fnORypR, expires about 2026-11-07), the remaining ~52 % of the Py2.7-MT exact cursor, the PHP uniform tier beyond 0.607 %, persisted PHP-cell FPR.",
     "reopens_if": "after 2026-11-01 00:00 UTC and before about 2026-11-07: recover window 2 from the snapshot, then persistent-session windows; the PHP retry harness persists control and FPR first.",
     "evidence": [PFX + "CAMPAIGN-PLAN.md"]})

# ---- X1 row
x1 = {"id": "R39-X1-REDTEAM", "round": 39, "lane": "X1", "lane_dir": "X1-redteam", "date": "2026-10-31", "status": "audit",
      "hypothesis": "Round 39's own claims (the MEASURED-CEILING page and its checker, T1 standing nulls, C1 sense similarity, I1 page-matched V2 null) and the Round 38 X1 carry-overs survive a refute-by-default audit.",
      "result": ("FOUND-ERROR (all bounded; no stored verdict flips). MEASURED-CEILING.md: 14 strong-verdict lines presented 'panel-R36, 12 registers' while the cited controls were EN_MODERN-only (or EN/LATIN/GREEK) plants; 3 cited rows (U6A-N2, U6A-N4, U6B-R22C) used a post-data null (threshold_fixed_in_advance false) undisclosed; "
                 "Py2.7 'pair' power 1.00 is an English plant on a partially-run row; SHA/KDF power 1.00 holds for the one-symbol-per-rejection relation only (skip_by_two plant recovery 0.258); PHP prior-dense 0.98 was the top of a 0.95-0.99 range with 2 of 9 registers planted; public-pad power (prefilter 5/8, 0.375-0.875) omitted; "
                 "N5/N4 carried 'measured negative' with the owner read pending; section 3 omitted the partial Marsaglia sweep (77/756 units), the transcription input assumption, non-additive cipher classes and four section-1 limits; section 5 step 1 lacked --r19 --welsh --r36. "
                 "check_ceiling.py: prefix admissibility, no threshold/register-scope check, forbidden list missing R7's 'unsolvable' and 'frontier is complete' (all fixed). C1: lane patch named a nonexistent id with a non-vocabulary status and no cell (repeat of R38 row 9); inherits the R38 lemma defect undisclosed; the 18 F5 cells move NEVER -> PARTIAL (one generic operationalization). "
                 "I1: status negative with a failed control (validator error) filed inconclusive; the 50 FPR windows are page 0 only with 24-31 distinct scores (CI invalid); the R38-promised pre-registered D2 revision was not run; the doublet-mismatch hypothesis tested and refuted (FPR 13/50 either way). T1: NO-ERROR-FOUND (tests 7/7, adjudicate copies byte-identical, R35/R36 stores validate, 15.30 / 17.43 / 6.994 reproduced). Carry-overs: O4 count files still carry 68/66 in table bodies (banners only); I1-R38 correction and capsule PASS present; N5/N4 logged in SYNTHESIS only."),
      "not_covered": "S1/S2 were not run in Round 39 (moved to Round 40); the I1 FPR windows are page 0 only; the claims of cited rows were checked against row fields, not re-run, except the C1 controls and index.",
      "reopens_if": "S2 window 2 is recovered (snap_ff0SWU76EW32OqbWJvp00fnORypR, after 2026-11-01 and before about 2026-11-07); the owner reads the N5/N4 bundle; the 18 F5 cells' clue-specific readings are run; X1's page scope edits are overruled.",
      "evidence": [PFX + "X1-redteam/RESULTS.md", PFX + "X1-redteam/rerun_c1_controls.json", PFX + "X1-redteam/rerun_c1_index.txt", PFX + "X1-redteam/rerun_i1_doublet.json", PFX + "X1-redteam/apply_ledger.py", "liber-primus/MEASURED-CEILING.md"]}
add(x1)

# ---- I1 (normalised: status negative + positive_control failed is an error under validate_ledger)
i1d = os.path.join(R39, "I1-v2-page-null")
if os.path.exists(os.path.join(i1d, "RESULTS.md")) and os.path.exists(os.path.join(i1d, "ledger.json")):
    raw = json.load(open(os.path.join(i1d, "ledger.json"), encoding="utf-8"))["entries"][0]
    i1 = {k: v for k, v in raw.items() if k not in ("conditionals", "artifacts", "power")}
    i1["raw_status"] = raw["status"]; i1["status"] = "inconclusive"; i1["lane_dir"] = "I1-v2-page-null"
    i1["three_conditionals"] = {"key_space": "V2 render (U8 V2_idx_rel_29) of LP2 pages; five V2-quantised planted glyphs; no key space swept",
                                "transition_model": "n/a (geometry recognizer, not a decoder)",
                                "adjudicator_register": "n/a; R38 D2 recognizer (corner count, closure, turning histogram, Hu 1-4) vs a within-line (A) or within-word (B) shuffle null, 200 draws per page"}
    i1["threshold_fixed_in_advance"] = True
    i1["reopens_if"] = ("a different recognizer family, or a null preserving local rune-pair statistics, brings V2 FPR to <= 0.05 on windows drawn from many pages (the Round 39 FPR windows are 50 draws from page 0, 24-31 distinct); "
                        "or the R38 pre-registered D2 revision (reweight plus turning-function term; Round 39 did not run it) is run.")
    i1["evidence"] = [PFX + "I1-v2-page-null/" + x for x in ("PREREG.md", "RESULTS.md", "run.py", "power_v2_A_B.json", "run.log", "rescore_v2.json")] + [PFX + "X1-redteam/rerun_i1_doublet.json"]
    i1["x1_r39"] = ("X1/R39: status negative + positive_control failed is a validator error; filed inconclusive. FPR 'on 50 clean pages' is 50 windows of page 0 only, of which 31 (A) and 24 (B) have distinct scores, so the Wilson interval assumes an independence that is absent. "
                    "The doublet hypothesis was tested and REFUTED: page-0 real adjacent-equal pairs 2 of 262 vs 9.4 under null A, but a doublet-matched null A leaves FPR unchanged (13/50 vs 13/50; rerun_i1_doublet.json). "
                    "The R38 X1 promise that Round 39 I1 would run the pre-registered D2 revision (reweight plus turning-function term) was not kept: weights are unchanged and the kill rule closes V2 as unmeasurable.")
    add(i1)

# ---- counts + note
rec = {}
for e in E:
    rec[e["status"]] = rec.get(e["status"], 0) + 1
doc["counts"]["total"] = len(E); doc["counts"]["by_status"] = rec
doc["counts"]["note"] = doc["counts"]["note"] + (" | Round 39 X1 merged 2026-10-31: lanes P1 (MEASURED-CEILING audit row; page and checker corrected), T1 (standing nulls, measured), C1 (sense similarity, negative; the 18 NEVER F5 cells -> PARTIAL on R36-O4-CLUE-COVERAGE), "
                                                 "I1 (if filed), R39-S1-S2-WINDOWS (never-run: sandbox lanes S1/S2 moved to Round 40) and X1 filed after refute-by-default audit.")
json.dump(doc, open(os.path.join(LP, "LEDGER.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(len(E), rec)
