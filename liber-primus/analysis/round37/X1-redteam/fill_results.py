import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "RESULTS.md")
s = open(p, encoding="utf-8").read()

s = s.replace("__I1_I2_STATUS__", "**I1 (`I1-free-null/`, RESULTS.md 14:54) and I2 (`I2-pfv4-12reg/`, RESULTS.md 15:15) existed when audited (done last, sections 6b/6c).**")

s = s.replace("| 8 | C2-U7 null and control B; C2-U8 label | NO-ERROR-FOUND | section 3 |",
 "| 8 | C2-U7 null and control B; C2-U8 label | NO-ERROR-FOUND | section 3 |\n"
 "| 7b | I1 RESULTS.md vs addendum / ledger / stream | **FOUND-ERROR (documentation)** | RESULTS.md headline and section 2 (5/5 and 3/3 plants; \"no register is passed at L=400 and L=729\") predate the coordinator-ordered completion (`ADDENDUM-2026-10-30-b.md`: 20 plants x 12 registers at L=400 and L=729). `control_free_stream.jsonl` has 720 plants; recounted: L=400 12/12 registers >= 19/20 (OE 19/20), L=729 12/12 at 20/20, L=240 unchanged (OE 3/20, HALFVOWEL 7/20, CY 19/20). The addendum and ledger.json are the claim of record. Also `bar_v3(1e6,120,'free')` = 17.43 (R34 9-register node) while L>=240 return 12-register nodes (the L=120 12-register node, 15.30, needs `panel='r36'`) |\n"
 "| 7c | I1 numbers, I2 numbers | NO-ERROR-FOUND | sections 6b/6c |")
s = s.replace("| 12 | Ledger / gates | applied | section 7 |", "| 12 | Ledger / gates | applied | section 7 (244 entries) |")

ledger = (
 "`LEDGER.json` 220 -> **244 entries** (pre-edit copy `LEDGER.pre-x1.json`; `apply_ledger.py` is idempotent). Added: R37-T1-12REG-PLUMBING; R37-C1-U1/U2/U3 (negative); R10-L2-MAP and R10-L3-ROAD (retro-rows from C1, `measured`, English-only conditionals); "
 "R37-C2-U4 (measured, with X1's alignment correction), R37-C2-U7-BOOK-CODE (negative), R37-C2-U7-BOOK-CODE-W (inconclusive), R37-C2-U8-GEOMETRY (inconclusive); 11 R37-C3-* rows (10 negative, N3 inconclusive; four with `threshold_fixed_in_advance=false`); "
 "R37-I1-FREE-NULL-LMATCHED (measured; the lane's free-form ledger.json had no id/hypothesis, normalised, raw kept in `lane_ledger_raw`); R37-I2-PFV4-12REG-ORBIT (negative); R37-X1-REDTEAM (audit). "
 "Patches: F-02 -> `partially-run` (X1 override of C1's `measured`: the semantic reading and several literal alternatives are untested), `restated_from` kept; R11-N1..N5, R11-S1, R11-S2, R22-C-LITERAL-IMPERATIVES, R10-L2-MAP, R10-L3-ROAD each get C3's coverage_add / not_covered_add plus `three_conditionals_r37_c3` "
 "(the 12-register conditional is ADDED; the original English-only result is kept and the status is unchanged, so the R11-* rows stay `measured`, reconciling with the rows the Round 36 audit added). "
 "Normalisation: bare evidence names -> full paths; `artifacts` -> `evidence`; `conditionals` list -> `three_conditionals` dict; U7/U8/U4 `not_covered` lists -> strings; an `x1_r37` note on every R37 row. "
 "Nav docs edited for the new count and a Round 37 entry (root README.md, ELIMINATION-LEDGER.md, analysis/README.md, PICKUP-HERE.md; PAPER.md counts 220 -> 244). `liber-primus/README.md` has no round-specific text and was not changed.\n\n"
 "Gate output (all from `liber-primus/`, after the final edit):\n\n```\n"
 "validate_ledger.py : ERRORS: 0 ; Unsound negatives: 0 ; 244 entries (76 measured, 74 negative, 38 audit, 18 open, 18 partially-run, 8 never-run, 5 eliminated, 4 inconclusive, 3 superseded)\n"
 "tests/validate.py  : ALL VALIDATIONS PASSED\n"
 "pytest tests/ benchmark/ -q : 34 passed\n"
 "verify_capsule.py  : OK 89, ABSENT 14, SKIP 1 -> PASS\n"
 "build_index / build_knowledge / build_problem / build_solved_pages : wrote cleanly, paths resolve (n=12956 sha 023312066d.., 86 doublets)\n"
 "check_consistency.py: all checks ok incl. 'ledger counts in nav docs match LEDGER.json' -> 'All entry points agree. No document drift detected.'\n```\n\n"
 "Interim failure, fixed: `check_consistency` failed once (PAPER.md:282, 443 said 220) until the counts were updated.")
s = s.replace("__LEDGER_SECTION__", ledger)

sec6 = (
 "## 6b. I1 (audited last)\n\n"
 "Numbers: the exponential-POT fit (u, beta, mu) and the N=1e3 / N=1e6 bars at L=120/240/400/729 are reproduced exactly from the raw `null_free_stream.jsonl` (`rerun_i1_fit.json`: 20.589 / 21.67 / 24.865 at N=1e6); `bars_v3` returns the same and raises at other L. "
 "Control recounted from `control_free_stream.jsonl` (720 plants). O3 ILP32 cell: 15.157 vs null max 15.54 of 562, empirical quantile 0.9964, family-wise p ~0.95 -- NOISE, consistent with the Round 36 O3 verdict. "
 "The planted control is SHA-CTR with `free_q05` only (stated); 562-1,335 null draws, not 2,000 (stated). Verdict: NO-ERROR-FOUND on the measurement; FOUND-ERROR (documentation) row 7b.\n\n"
 "## 6c. I2 (audited last)\n\n"
 "Recomputed from `_null_scores.npz` / `_plant_scores.npz` / `sweep_rows.jsonl`: thresholds 7.4155 / 7.4412 give total FPR 8.81e-4 (calibration half) / 8.89e-4 (held-out), per-relation 5.0e-4; per-register plant power 0.952-0.994 (EN_HALFVOWEL the minimum); "
 "store 263,572 rows (131,630 + 131,942), stock `validate_store` ok at 12 registers, `check_r3_store` `[]`; survivors 65,815 + 65,971; actual-N bars 8.113 / 8.027 recomputed from `round36/B1-orbit-12reg/null12.json`; best ks1 6.506, ks2 7.065 (seed 1354603465, LP1_REAL). NO-ERROR-FOUND. "
 "Limits (all stated by the lane): the same 77.6 M-seed x 2 orbit as Round 35/36 B1 (no new seed coverage; new screen power on GREEK/HEBREW/NORSE), PHP FPR not re-measured, recovery assumed 1.00 for seven registers, control n=10 per cell.\n\n"
 "## 7. Ledger and gates (target 7)")
s = s.replace("## 7. Ledger and gates (target 7)", sec6, 1)

s = s.replace("| C1 U1 (H1-H5 x F4 re-run under panel-R36: -5 T-LEG) and C3 (H2 x F3, H4 x F2, L2 x F2, S1 x F2: -1 T-EN... -4 total) | 60 | 21 | 25 | 31 | 3 |",
              "| C1 U1 (H1-H5 x F4: 5 -> T) and C3 (H2 x F3, H4 x F2, L2 x F2, S1 x F2: 4 -> T) | 60 | 21 | 25 | 31 | 3 |")

s = s.replace("__ITEM6__",
 "**I1/I2 leftovers:** (a) PHP-tier FPR and re-screen under the 12-register pf_v4 point (I2 not_covered); (b) now that `free` is licensed at L=240 (10 registers) and L=400/729 (12), a `free` decode of the ~1-2 k highest L=120 survivors of the I2 store at L=240 (about 35 min at ~1 decode/s); "
 "(c) 2,000-draw nulls and a real-structure null for `free` (I1 not_covered). Priors flat-low (the one recurring top seed was shown NOISE under `free` at L=729)")

files = ("| File | Change |\n|---|---|\n"
 "| `LEDGER.json` | 220 -> 244 entries; section 7. Pre-edit copy `X1-redteam/LEDGER.pre-x1.json` |\n"
 "| `../README.md` (repo root) | status line: Round 37 filed/X1-audited sentence prepended |\n"
 "| `ELIMINATION-LEDGER.md` | new section \"Round 37\" above Round 36 |\n"
 "| `analysis/README.md` | new table row for `round37/` |\n"
 "| `PICKUP-HERE.md` | Round 37 X1 block above the Round 36 closeout; ledger counts 220 -> 244 (two lines) |\n"
 "| `../PAPER.md` | lines 282, 443: 220 -> 244 entries |\n"
 "| `analysis/round37/X1-redteam/` | this RESULTS.md; rerun_*.py/.json, o4_recount.py/.json, apply_ledger.py, apply_nav.py, fill_results.py, x1_row.json, LEDGER.pre-x1.json |\n\n"
 "Not edited (outside the X1 edit set; flagged in section 10): `round36/O4-clue-coverage/matrix.md`, `untried.md`, `counts.json`; `round37/I1-free-null/RESULTS.md`; the `round37/C*/` lane documents. `liber-primus/README.md` unchanged (no round-specific text).")
s = s.replace("__FILES__", files)

s = s.replace("6. Fix `PAPER.md`-style nav counts after I1/I2 rows are added (done here to the final count).",
 "6. I1: update `I1-free-null/RESULTS.md` headline to the addendum (20 plants x 12 at L=400/729) so the lane document and the ledger agree; decide whether `bar_v3(..,120,'free')` should default to the 12-register node.\n7. Nav-doc counts are now 244 (done here).")
open(p, "w", encoding="utf-8").write(s)
import re
print(re.findall(r"__[A-Z0-9_]+__", s))
