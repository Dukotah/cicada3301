# Round 37 / X1 -- red-team (R6) -- RESULTS

_2026-10-30. Refute-by-default. Each target is FOUND-ERROR or NO-ERROR-FOUND with citations; a NO-ERROR-FOUND says what was checked. No git run. Paths relative to `liber-primus/`. One Python process at a time, nproc=1, free RAM >= 0.4 GB before each re-run (it fell to 0.25 GB late in the audit while I1/I2 were running; no re-run was started then). Re-run artefacts in this directory: `rerun_c1.py/.json`, `rerun_u4.py/.json`, `rerun_u7_controlB.py/.json`, `rerun_z694.py/.json`, `rerun_t1.py/.json`, `o4_recount.py/.json`; ledger application `apply_ledger.py` (pre-edit copy `LEDGER.pre-x1.json`, X1 row `x1_row.json`)._

**I1 (`I1-free-null/`, RESULTS.md 14:54) and I2 (`I2-pfv4-12reg/`, RESULTS.md 15:15) existed when audited (done last, sections 6b/6c).**

## 0. FOUND-ERROR summary

| # | Target | Sub-verdict | One line |
|---|---|---|---|
| 1a | C1 U1 candidate list completeness | **FOUND-ERROR** | `candidates.json` (83 strings, sources C-2016-1..5 only) omits **C-2016-6 "Seek and you will be found."** and **C-2016-7 "Beware false paths.  Verify OpenPGP 7A35090F."** that O4 `clues.json` carries; PREREG sec. 1 says "5 clauses". "The 2016 clauses" in the C1 ledger rows is 5 of 7 (the other two are covered only by R10b B1's legacy Vigenere keywords, O4 H6 x F4). All LP1 imperative ids are present; casings (UPPER + as-written) are consistent with `clues.json` |
| 1b | C1 U2 "line" sequence and its stated reason | **FOUND-ERROR** | PREREG sec. 2 and RESULTS call per-line sums CONVENIENT because "the printed LP1 line breaks are not otherwise recorded in the repo". They are: `data/scream314_lp.md` (parsed by `src/lp/corpus.py`, used by C2-U4). `rerun_u4.json`: C1's `LINES` (koans file, `enciphers_u2_u3.py:44`) equals the printed lines only for A WARNING (10/10); 05/06/03/14/73 differ (values present 4/10, 17/20, 1/8, 2/8, 1/4). The literal printed-line sequence (60 lines, 6 pages) was never run; the 4 `line` variants of U2 (prime/index x mod 29/28) are the convenient ones. U2's best row was one of them (4.793), so this is a coverage gap, not a hidden hit |
| 1c | C1 U3 "most literal composition" label | **FOUND-ERROR (labelling)** | the composition rho1 x A3 (map = LP1 word list, road = position, direction = entry number through the LP1 rune stream) is C1's operationalization; "its words" may be LP2's own words (R10 L2-map read them that way). Literal alternatives skipped: a cipher-word gematria pointer **lagged by one word** (well-formed, no fixed point -- C1 excluded only the same-word version), the O4 `untried.md` U3 seed (4 value types x 6 composition orders x atbash x 29 starts, segmentation also on `&` `$`), direction-then-road. "Meaning" as semantics is not operationalized (C1 admits it). The label should read "C1's most direct operationalization" |
| 2a | C2-U4 plaintext line sums | **FOUND-ERROR** | `measure.py:195-196` (`pl` = count of runes with `x >= 0`; `bnd(plens)`; `np.add.reduceat(vals, b)`) cuts the position array (which still holds a 0 slot per interrupter) with boundaries computed from interrupter-free counts, so lines are misaligned on pages with interrupters (03: 7, 14: 2, 73: 1). `rerun_u4.json`, re-aligned on full physical lengths: **03 = 3/8 (reported 4/8), p(shuffle) 0.090-0.132 (reported 0.025); pooled 21/60 (reported 22/60), p 5e-4; pages p < 0.05 = 1 (reported 2)**. 01/05/06 unchanged. Verdict NO-SEPARATION unchanged (stronger). The WELCOME "3/5" prior is not supported either |
| 3 | C3 PREREG departures | **FOUND-ERROR (process)** | the doublet-matched null (and for N1-PT the two-statistic rule) replaced the first-pass plain-shuffle null AFTER real-data results existed: first-pass p(Z) 0.0066 (N1-PT), 0.0050 (N2), 0.0033 (N4-read) -- all < 0.01 -- in `superseded_plain_shuffle_null/*.done.json` (written 13:5x-14:10; PREREG 13:30). Justified mechanically, in the hit-removing direction, disclosed; but a post-data change to the test. Ledger: `threshold_fixed_in_advance=false` on N1-PT, N2, N4, R22-C. Also: the raw-pmax statistic has marginal planted power in N2 (LATIN plant 111.31 vs null q99 111.12) |
| 4 | C3 ledger-patch wording | **FOUND-ERROR (minor)** | patches say "English-only/legacy conditional replaced by the 12-register conditional; remains negative". The R11-* rows are `measured`, the old result is still an English-only result, and N1-PT / structural streams are skip-free only. Applied as an ADDED second result (`three_conditionals_r37_c3`) with status unchanged |
| 5 | Carry-over: O4 count correction | **FOUND-ERROR (partial application)** | O4 `RESULTS.md` has the 68 -> 66 correction, but `matrix.md` lines 15, 20, 54-56 still show H7 x F2 and H12 x F2 as NEVER and "NEVER: 68"; `untried.md:3`, `counts.json` (`never: 68`) too. Not edited (outside the X1 edit set); recount below |
| 6 | C1 re-runs, append mode, controls-conditional | NO-ERROR-FOUND | sections 1.4-1.6 |
| 7 | C2-U4 shuffle null / decision rule / title | NO-ERROR-FOUND (apart from 2a) | section 2 |
| 8 | C2-U7 null and control B; C2-U8 label | NO-ERROR-FOUND | section 3 |
| 7b | I1 RESULTS.md vs addendum / ledger / stream | **FOUND-ERROR (documentation)** | RESULTS.md headline and section 2 (5/5 and 3/3 plants; "no register is passed at L=400 and L=729") predate the coordinator-ordered completion (`ADDENDUM-2026-10-30-b.md`: 20 plants x 12 registers at L=400 and L=729). `control_free_stream.jsonl` has 720 plants; recounted: L=400 12/12 registers >= 19/20 (OE 19/20), L=729 12/12 at 20/20, L=240 unchanged (OE 3/20, HALFVOWEL 7/20, CY 19/20). The addendum and ledger.json are the claim of record. Also `bar_v3(1e6,120,'free')` = 17.43 (R34 9-register node) while L>=240 return 12-register nodes (the L=120 12-register node, 15.30, needs `panel='r36'`) |
| 7c | I1 numbers, I2 numbers | NO-ERROR-FOUND | sections 6b/6c |
| 9 | C3 filter, z=6.94, N5 | NO-ERROR-FOUND (+ note) | section 4 |
| 10 | T1 backward compatibility | NO-ERROR-FOUND | section 5 |
| 11 | Carry-overs I1 docs, B2/S1, capsule, snapshot | NO-ERROR-FOUND / status | section 6 |
| 12 | Ledger / gates | applied | section 7 (244 entries) |

## 1. C1 (target 1)

**1.1 Candidate completeness vs `round36/O4-clue-coverage/clues.json`.** clues.json holds C-2016-0 (whole message), C-2016-1..7. `candidates.json` sources: C-2016-1..5 and their compositions/noun phrases, plus 33 LP1 ids/fragments. Missing: C-2016-6, C-2016-7 (and the trivial "Hello"). LP1: all imperatives are present (0.0.0.1-9, 0.1.0.1/6, 0.1.1.5, 0.1.2.3, 0.1.3.0, 0.13.0.1/2, 0.14.0.2/3, 0.2.1.1, 0.3.1.1-3, 0.3.2.1/2, 0.4.1.1-4); the descriptive LP1 sentences are not imperatives. See 0/1a.

**1.2 Convenient choices C1 itself admits (RESULTS "What was literal and what was convenient") and whether a literal alternative was skipped.**

| C1-admitted convenient choice | literal alternative skipped? |
|---|---|
| per-line sums from the koans file | **yes** -- printed lines exist in `data/scream314_lp.md` (0/1b) |
| `index` channel (U2) | no (it is an extra, not a replacement) |
| LP1 rune stream as the base key K0 (U2b, U3 A3) | the clue names no base key; alternatives (LP2's own runes, solved plaintext) not run; `not_covered` says so |
| mod 28; start s; rho2/rho3 pointers; k restart per page | extras |
| a single PBKDF2 configuration, UPPER / as-written hash forms | other forms stated in `not_covered` |
| "meaning" not operationalized | the biggest gap; no bounded definition attempted (Round-38 item 1) |
| NOT admitted by C1: the label "literal" for rho1 x A3; the exclusion of a cipher-word gematria pointer | yes: lagged pointer; O4 U3 seed orders (0/1c) |

**1.3 PREREG timeline.** `PREREG.md` mtime 13:20:08 is after `control.json` 13:19:31 and before `sweep.log` 13:22:35: PREREG was edited once after the control (C1 discloses the n=728 -> 726 word-count fix). I cannot diff its earlier text (no git); the fix is arithmetic prose and the sweep grid is unchanged. NO-ERROR-FOUND, noted.

**1.4 Re-runs (`rerun_c1.json`, fresh RNG seed 910301, independent of C1's seed).** U1 controls: direct / keyskip2 plant of "ITS WORDS ARE THE MAP" ranks **1/83** (pmax120 19.77, runner-up 9.69 -- another candidate containing the planted string's words clears the N=1e6 bar of 9.03, harmless but notable), pmax240 28.72, recovery 1.000; sha256ctr / keyskip1 plant ranks **1/76** (22.16 vs 5.08), recovery 0.9958. U3 cells (independent encipherer, random s/sigma): rho1-M29-A3 keyskip1 20.46 / recovery 1.000 (wrong-s control 1.54), rho1-M29-A3 keyskip2 21.49 / 1.000 (wrong-s 3.48), rho3-M28-A2 direct 21.65 / 1.000 (wrong-s 0.93). All pass the N=1e6 bars (9.23/9.03). The controls exercise EN_MODERN only.

**1.5 Addendum in APPEND mode.** `sweep_rows.jsonl` = 17,393 lines = 1 header + 17,392 rows (4,416x2 + 1,536x2 + 2,088 + 1,044x2 + 1,312 = 17,392 arithmetically: U1 8,832 + 1,312, U2 3,072, U3 4,176); stock `validate_store` -> 17,392 rows validated, 12 registers; header unchanged (its `n_planned` still lists the pre-addendum U1 count, C1 notes this); `ADDENDUM-2026-10-30.md` mtime 13:26:28 precedes the append (13:27:44).

**1.6 "Controls EN_MODERN only" on the ledger rows.** Present as a conditional in `three_conditionals.adjudicator_register` of all three C1 rows (U1 explicit; U2/U3 "control EN_MODERN only"); the two retro-rows (R10-L2-MAP, R10-L3-ROAD) carry "ENGLISH ONLY" adjudicator conditionals and `measured` status. Kept; one sentence added to U3's `key_space` for 1c.

## 2. C2-U4 (target 2)

* Shuffle null keeps line lengths: yes, by construction (`nulls()`, `bnd(lens)` with the same boundaries as the observation), **but** the plaintext boundaries are misaligned (0/2a); the null permutes all positions, including the interrupter zeros, over the (misaligned) cuts. With true alignment, both a null that shuffles all positions and one that shuffles only the runes give p 0.09-0.13 on page 03 (`rerun_u4.json`).
* Decision rule fixed before data: PREREG.md 13:02:29, `measure.py` 13:03:47, `results.json` 13:03:51. The PREREG rule (pooled p(shuffle) < 0.01 AND >= 4/6 pages p < 0.05) is as applied.
* Recomputed (10,000 draws, own seed 910304): page 01 9/10, p 1.0e-4 (reported 9.999e-5); 05 4/10, p 0.097-0.100 (0.0994); 06 2/20, p 0.81 (0.8134); 14 2/8, p 0.48-0.61; 73 1/4, p 0.51. Pooled (true alignment) 21/60, p 5e-4. Pooled significance is the single page 01.
* Title line: included (PREREG); excluding it makes 01 9/9 and does not create a second significant page (05 4/9). Not a decision point for the verdict. Positive control and the ciphertext side are unaffected (ciphertext has no interrupter slots).

## 3. C2-U7 / U8 (target 3)

* **U7 null.** Drawing index VALUES uniformly over the scheme's own alphabet (0-9, 0-99, 0-999) is the right null for a book code: a real digit string can only address that range, so a null over the whole target is wrong (Run 1, correctly replaced; Addendum 1 documents it, 0 flagged in both runs). The order-shuffle null is the second guard; `p_gate = max` of the two is conservative. Residual: the digits of S1/S2/LOC are assumed exchangeable by the order-shuffle only. NO-ERROR-FOUND.
* **U7 control B.** Reproduced (`rerun_u7_controlB.json`): the real sentence has pmax_ne 14.530 (= lane's 14.53); 400 random bags of 8-ish LP1 words trimmed to the same 42 runes have mean 12.16, q95 14.03, max 15.04, and 1.25 % are >= the real sentence; uniform random runes: mean 1.26. The LP1_REAL register contains LP1's words, so a bag of LP1 words is indistinguishable from the sentence; the 80 W cells are correctly `inconclusive`. NO-ERROR-FOUND.
* **U8.** Planted-glyph control failed on 5/5 plants under two recognizers (best V3-T 4.09 vs 4.21). `inconclusive` is the right label (Q5: a failed control makes the family unpowered). The 232-render sweep is labelled "diagnostic only" in RESULTS ("Variant table (diagnostic; control failed)", "not a clean negative"), in the ledger row (`coverage`: "diagnostic only"; `result`: "inconclusive"). One process note: PREREG kill rule says stop at a failed control; the lane ran the diagnostic sweep (395 s) anyway and said so. NO-ERROR-FOUND.

## 4. C3 (target 4)

* **Timeline.** PREREG 13:30:23. First-pass real-data parts: N1-CT 13:37, N4-ks 13:37, N5 13:50, S1/S2 13:52, U6b keyed 13:53; the plain-shuffle first-pass results for N1-PT / N2 / N4-read / structural were produced by that pass and moved into `superseded_plain_shuffle_null/` at 14:10:55; the final parts for those families are 14:12-14:13. So the three PREREG departures were all decided after the data: (i) the degenerate-decode filter (after the U6b keyed pass found the constant-output X4 row), (ii) the doublet-matched null (after the first-pass p(Z) < 0.01 on three families), (iii) the two-statistic rule (after N1-PT p(Z) 0.0066 with raw p 0.50). Direction in every case: toward fewer hits. 0/3 disclosed in ledger form before X1; now `threshold_fixed_in_advance=false`.
* **Does the filter remove a real-data row that would otherwise clear?** Yes, and only constant outputs: 24 U6b rows per relation (12 at L=120, 12 at L=240; X4 `v_prime_index` with `atbash_pre`/`none`, windows 0-12114) have mds = 1 and IoC*N 27.6-29.0; e.g. 8.70 (L=120) and 12.40 (L=240) vs bars 5.69 / 6.04. The decode is the constant stream (the key equals the ciphertext word-by-word), i.e. the construction is degenerate, not a language hit. No row with mds in 2-6 or IoC*N in 4.24-27 exists in any beam family (N1-CT, N4-ks, N5: 0 degenerate rows). Direct families (pmax 90-109 on 12,956-rune digit streams) are scored by Z against their own null, not by the filter. NO-ERROR-FOUND on effect; the thresholds are looser than needed (a single rule "constant output" would do).
* **z=6.94 re-scored (`rerun_z694.json`, own code, own nulls, 300 draws each).** Reading `first/noF atbash/rev/+28` (2,928 runes): panel-R36 pmax **3.942** (EN_MODERN; HEBREW 3.30, EN_KJV 2.93) = C3's 3.94. Single-reading null: plain shuffle mean 2.67-2.76, q99 4.4-4.6, p 0.066-0.073; doublet-matched (59 +/- doublets vs real 86) p 0.056-0.070. A single pre-named reading at p ~ 0.07 and, within the 464-reading family, p 0.74-0.95 (C3). The Round 10 near-flag is an English-gated artefact. NO-ERROR-FOUND. (My first doublet-repair draft overshoot to 0 doublets and gave the same p; the final one stops at the target.)
* **N5 6.30 vs 6.90.** Bar recomputed from `round36/B1-orbit-12reg/null12.json` (`u + beta ln p_u + beta ln(N / -ln 0.99)`, N = 2,320, L=120, ks1): **6.897** (ks2 6.831), = C3's. Best 6.304 (CY) and the next 6.244 are the SAME generator (`phi_phi_prime_RI_s-1`, windows 0 / 9600), and ks1 = ks2 exactly on 145 of the 2,320 (key, window) pairs (no-skip best decodes). Under the transferred GPD tail P(max of 2,320 >= 6.304) ~ 0.05 and 6.244 ~ 0.06 -- "closest row, 0.59 below the bar" is right, "noise-level by construction" is not. Neither is a clearer, no L=240 run was owed. Cheap follow-up listed in Round 38.
* **Other.** N5 is the only family whose control includes a real keyed page (AN END under phi(prime): 1.00 / 0.93). The U6b structural family is key-free, so "x keyskip1/2" is vacuous there (C3 says so).

## 5. T1 (target 5)

`rerun_t1.json`: stock `validate_store` on the full R35 B1 9-wide store (276,242 rows, header 9 registers) and the full R36 B1 12-wide store `readjud_rows.jsonl` (276,242 rows, 12 registers): both ok (2.0 s / 2.6 s); `check_r3_store` `[]` on both. `derive_clusters(panel-R36)` = 10 clusters (EN = EN_MODERN+EN_KJV+LP1_REAL, 9 singletons); on the Round 32 9-register panel (`round32/B3-closeout/models/panel.npz`, sha 36a01dcb...) = the old 7 clusters. `panelmax_bar` / `panelmax_contract` with panel-R36 raise `ValueError: REFUSED: the Round 19 panel-max bar constants were fitted on a 9-register panel (sha 36a01dcb5083...); the supplied panel has 12 registers and sha a0682f0c3997. Compute a bar for the supplied panel (e.g. round34/I1-v3-null/bars_v3.py) instead of reusing this one.`; `hitfn20.evaluate` calls the same check first (`hitfn20.py:170`); the 9-register Round 32 panel is accepted (`panelmax_bar('exact', 120, panel=pan9)` = 5.047). CI: `../.github/workflows/ci.yml:53` runs `tests/test_12reg_plumbing.py` (not `test_provenance` / `test_verify_solution`, which were never on that line). Local: `pytest tests/ benchmark/ -q` 34 passed. NO-ERROR-FOUND. Caveat kept: `FITTED_PANEL_SHA256` pins the Round 32 rebuild because the Round 19 file is lost.

## 6. Carry-overs (target 6)

* I1-R36 doc corrections: applied -- `round36/I1-new-registers/mappings.md:3` carries the SUPERSEDED banner; RESULTS "Correction" (lines ~64-67) states the hash-seed nondeterminism. NO-ERROR-FOUND.
* O4 counts: **partially applied** (row 5 above). RESULTS has the correction; `matrix.md`, `untried.md`, `counts.json` do not.
* B2 / S1 patches marked superseded: yes (`round36/B2-php-awake/ledger_patches.json` `$superseded`; `S1-s2-window/ledger_patches.json`). NO-ERROR-FOUND.
* Capsule: `handoff/capsule/verify_capsule.py` -> OK 89, ABSENT 14, SKIP 1, **PASS** (same as Round 36).
* Sandbox snapshot export (status only): no Round 37 lane exported the S2 window's top list / histogram (`round36/S1-s2-window/state_after/` holds STATUS.json + HIT-CANDIDATE.json only; `snap_fWma12lA...` expires ~2026-11-06, 7 days). **Not exported.** Coordinator action.

## 6b. I1 (audited last)

Numbers: the exponential-POT fit (u, beta, mu) and the N=1e3 / N=1e6 bars at L=120/240/400/729 are reproduced exactly from the raw `null_free_stream.jsonl` (`rerun_i1_fit.json`: 20.589 / 21.67 / 24.865 at N=1e6); `bars_v3` returns the same and raises at other L. Control recounted from `control_free_stream.jsonl` (720 plants). O3 ILP32 cell: 15.157 vs null max 15.54 of 562, empirical quantile 0.9964, family-wise p ~0.95 -- NOISE, consistent with the Round 36 O3 verdict. The planted control is SHA-CTR with `free_q05` only (stated); 562-1,335 null draws, not 2,000 (stated). Verdict: NO-ERROR-FOUND on the measurement; FOUND-ERROR (documentation) row 7b.

## 6c. I2 (audited last)

Recomputed from `_null_scores.npz` / `_plant_scores.npz` / `sweep_rows.jsonl`: thresholds 7.4155 / 7.4412 give total FPR 8.81e-4 (calibration half) / 8.89e-4 (held-out), per-relation 5.0e-4; per-register plant power 0.952-0.994 (EN_HALFVOWEL the minimum); store 263,572 rows (131,630 + 131,942), stock `validate_store` ok at 12 registers, `check_r3_store` `[]`; survivors 65,815 + 65,971; actual-N bars 8.113 / 8.027 recomputed from `round36/B1-orbit-12reg/null12.json`; best ks1 6.506, ks2 7.065 (seed 1354603465, LP1_REAL). NO-ERROR-FOUND. Limits (all stated by the lane): the same 77.6 M-seed x 2 orbit as Round 35/36 B1 (no new seed coverage; new screen power on GREEK/HEBREW/NORSE), PHP FPR not re-measured, recovery assumed 1.00 for seven registers, control n=10 per cell.

## 7. Ledger and gates (target 7)

`LEDGER.json` 220 -> **244 entries** (pre-edit copy `LEDGER.pre-x1.json`; `apply_ledger.py` is idempotent). Added: R37-T1-12REG-PLUMBING; R37-C1-U1/U2/U3 (negative); R10-L2-MAP and R10-L3-ROAD (retro-rows from C1, `measured`, English-only conditionals); R37-C2-U4 (measured, with X1's alignment correction), R37-C2-U7-BOOK-CODE (negative), R37-C2-U7-BOOK-CODE-W (inconclusive), R37-C2-U8-GEOMETRY (inconclusive); 11 R37-C3-* rows (10 negative, N3 inconclusive; four with `threshold_fixed_in_advance=false`); R37-I1-FREE-NULL-LMATCHED (measured; the lane's free-form ledger.json had no id/hypothesis, normalised, raw kept in `lane_ledger_raw`); R37-I2-PFV4-12REG-ORBIT (negative); R37-X1-REDTEAM (audit). Patches: F-02 -> `partially-run` (X1 override of C1's `measured`: the semantic reading and several literal alternatives are untested), `restated_from` kept; R11-N1..N5, R11-S1, R11-S2, R22-C-LITERAL-IMPERATIVES, R10-L2-MAP, R10-L3-ROAD each get C3's coverage_add / not_covered_add plus `three_conditionals_r37_c3` (the 12-register conditional is ADDED; the original English-only result is kept and the status is unchanged, so the R11-* rows stay `measured`, reconciling with the rows the Round 36 audit added). Normalisation: bare evidence names -> full paths; `artifacts` -> `evidence`; `conditionals` list -> `three_conditionals` dict; U7/U8/U4 `not_covered` lists -> strings; an `x1_r37` note on every R37 row. Nav docs edited for the new count and a Round 37 entry (root README.md, ELIMINATION-LEDGER.md, analysis/README.md, PICKUP-HERE.md; PAPER.md counts 220 -> 244). `liber-primus/README.md` has no round-specific text and was not changed.

Gate output (all from `liber-primus/`, after the final edit):

```
validate_ledger.py : ERRORS: 0 ; Unsound negatives: 0 ; 244 entries (76 measured, 74 negative, 38 audit, 18 open, 18 partially-run, 8 never-run, 5 eliminated, 4 inconclusive, 3 superseded)
tests/validate.py  : ALL VALIDATIONS PASSED
pytest tests/ benchmark/ -q : 34 passed
verify_capsule.py  : OK 89, ABSENT 14, SKIP 1 -> PASS
build_index / build_knowledge / build_problem / build_solved_pages : wrote cleanly, paths resolve (n=12956 sha 023312066d.., 86 doublets)
check_consistency.py: all checks ok incl. 'ledger counts in nav docs match LEDGER.json' -> 'All entry points agree. No document drift detected.'
```

Interim failure, fixed: `check_consistency` failed once (PAPER.md:282, 443 said 220) until the counts were updated.

## 8. O4 recount (`o4_recount.py` / `.json`)

| step | NEVER | TRIED-EN | TRIED-LEG | TRIED | PARTIAL |
|---|---:|---:|---:|---:|---:|
| matrix.md as filed | 68 | 24 | 29 | 16 | 3 |
| after R36 X1 (H7 x F2, H12 x F2 -> T-LEG) | 66 | 24 | 31 | 16 | 3 |
| C1 U3 (H2, H3, H4 x F1: literal composed instruction) | 63 | | | | |
| C1 U2 (H4 x F7: LP1 numbers as cross-document key schedule) | 62 | | | | |
| C2 U7 (H12 x F6: numeric strings as positional indices) | 61 | | | | |
| C2 U4 (L16 x F2: prime line sums as number channel) | 60 | | | | |
| C1 U1 (H1-H5 x F4: 5 -> T) and C3 (H2 x F3, H4 x F2, L2 x F2, S1 x F2: 4 -> T) | 60 | 21 | 25 | 31 | 3 |

**NEVER 60; English-only/legacy 46 (21 + 25); TRIED 31; PARTIAL 3 (sum 140).** Remaining NEVER by family: F5 semantic 19, F1 literal instruction 16 (many with no stated operation), F7 8, F10 5, F3 3, F8 3, F2 2, F6 2, F11 2. Judgement calls (the coordinator may move them): U3 counted for F1 on H2/H3/H4 only; U4 counted on L16 x F2 only (L17 x F3 left NEVER); U8 counted nowhere (control failed); a cell is moved from T-EN/T-LEG to T only if every English-only/legacy reading in it was re-run (C3 cells H2 x F3 (R02), H4 x F2 (R16), L2 x F2 (R16, R25), S1 x F2 (R20); U1 cells H1-H5 x F4). Every moved cell carries the EN_MODERN-only (C1) or EN/LATIN/GREEK-only (C3) control conditional. Not touched: F5 (the semantic family) -- no Round 37 lane operationalized it.

## 9. Round-38 candidates (<= 6, ranked)

| # | Candidate | Evidence prior | Cost | Citations / why this rank |
|---|---|---|---|---|
| 1 | **Close C1's skipped literal alternatives, with a bounded definition of "meaning"**: (a) lagged cipher-word and lagged DECODED-word gematria as pointer/skip count (well-formed, no fixed point); (b) the O4 U3 seed orders x 4 value types x atbash; (c) printed-line sums for U2; (d) C-2016-6/7 as U1 seeds. Define "meaning" non-lore as the decoded word's own value at the previous boundary (word-level plaintext feedback), and FIRST measure on the five solved pages (finite object, R5 rank 1) whether their keys carry any dependence on previous plaintext-word values | low (~1-2 %) but measured text support: three clauses, one subject; coverage holes 1a/1b/1c; F5 = 19 of 60 remaining NEVER cells; `round36/O4-clue-coverage/untried.md` U3 seed; C1 RESULTS "biggest gap"; R11 N1 PT-feedback was rune-level, skip-free only | solved-page test minutes; decode grid ~3-5 k decodes, ~10 ms each | cheapest route to turn F5 from "untested" into a bound; includes the cheap U1 omission |
| 2 | **N5/N4 top rows to L=240 + the X4 bespoke null** (C3 coordinator decision 3): top-5 of N5 (6.30, 6.24, 5.95 ...) and N4 (5.56) at L=240 with the dfshuffled-C-with-K-re-derived null for data-dependent keys | modest: the closest beam row of the round, one generator (`phi_phi_prime_RI s-1`), the same generator family that decodes AN END (control 1.00/0.93); tail p ~ 0.05 within family (section 4) | < 1 h | cheap, bounded, and resolves whether the nearest row is an outlier |
| 3 | **Power-adequate U8 glyph recognizer** (stroke-aware: closure + rotation-invariant moments + template, trained on turtle-drawn glyph strokes) with a 5/5 plant gate BEFORE any page is read; then re-read the 232 existing renders | low-moderate: "numbers are the direction" is the only direction/geometry clue; R22-B covered global shape only; the contact sheets already exist | recognizer ~half a day, no CPU | C2 U8 RESULTS "Coordinator decision"; 0 of 232 above null max is uninformative without it |
| 4 | **Remaining NEVER cells after recount** (60): F1 operational ones not yet run (H6, H8 "key in front of your eyes", L1 "test the knowledge", L5, L11 ...); F7 8 (H4/H11/L12/L13/L15/L17/S1/S3 joins); F10 acrostics (H5, H9, L3, L18, S4) | flat-low; ranked last because R3 requires a stated operation per cell and 16 F1 cells have none (O4 RESULTS) | each cell hours | do only with item 1's lagged pointer so cells are not double-counted |
| 5 | **S2 windows** -- conditional on (a) the sandbox top list / histogram exported before 2026-11-06 (NOT yet), (b) the lane's planted exact-relation control independently validated (not done by any Round 37 lane), (c) `top_S2.json` (1,024 old entries) re-scored under panel-R36 | flat over 2^32; panel-R36 coverage 1.28 % | (a) is minutes and time-critical, (b) hours, windows ~25 h sandbox | (a) is the only deadline in the whole programme |
| 6 | **I1/I2 leftovers:** (a) PHP-tier FPR and re-screen under the 12-register pf_v4 point (I2 not_covered); (b) now that `free` is licensed at L=240 (10 registers) and L=400/729 (12), a `free` decode of the ~1-2 k highest L=120 survivors of the I2 store at L=240 (about 35 min at ~1 decode/s); (c) 2,000-draw nulls and a real-structure null for `free` (I1 not_covered). Priors flat-low (the one recurring top seed was shown NOISE under `free` at L=729) | | | |

## 10. What the coordinator must decide

1. O4: edit `matrix.md` / `untried.md` / `counts.json` (H7 x F2, H12 x F2 -> T-LEG; and apply the section-8 moves) or accept RESULTS-only correction.
2. Export the S2 window lists from the sandbox before ~2026-11-06, or accept their loss.
3. Whether C1's U1 grid is extended to C-2016-6/7 and the printed-line U2 variant now (small) or inside Round-38 item 1.
4. F-02: X1 set `partially-run` (not C1's `measured`) because the semantic reading is untested -- confirm.
5. C3: accept the four `threshold_fixed_in_advance=false` flags (verdicts stand; the null swap is disclosed).
6. I1: update `I1-free-null/RESULTS.md` headline to the addendum (20 plants x 12 at L=400/729) so the lane document and the ledger agree; decide whether `bar_v3(..,120,'free')` should default to the 12-register node.
7. Nav-doc counts are now 244 (done here).

## 11. Files edited by X1

| File | Change |
|---|---|
| `LEDGER.json` | 220 -> 244 entries; section 7. Pre-edit copy `X1-redteam/LEDGER.pre-x1.json` |
| `../README.md` (repo root) | status line: Round 37 filed/X1-audited sentence prepended |
| `ELIMINATION-LEDGER.md` | new section "Round 37" above Round 36 |
| `analysis/README.md` | new table row for `round37/` |
| `PICKUP-HERE.md` | Round 37 X1 block above the Round 36 closeout; ledger counts 220 -> 244 (two lines) |
| `../PAPER.md` | lines 282, 443: 220 -> 244 entries |
| `analysis/round37/X1-redteam/` | this RESULTS.md; rerun_*.py/.json, o4_recount.py/.json, apply_ledger.py, apply_nav.py, fill_results.py, x1_row.json, LEDGER.pre-x1.json |

Not edited (outside the X1 edit set; flagged in section 10): `round36/O4-clue-coverage/matrix.md`, `untried.md`, `counts.json`; `round37/I1-free-null/RESULTS.md`; the `round37/C*/` lane documents. `liber-primus/README.md` unchanged (no round-specific text).
