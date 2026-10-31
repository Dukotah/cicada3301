# Round 40 / I1 - replant controls: RESULTS
PREREG.md was written first (before `results_raw.jsonl`). One small Python process at a time (free RAM 0.46-0.92 GB at launch, >= 0.4 GB each time); a few minutes of decode in total plus import time. No `git`. Plant plaintext: `data/panels/testhalves-r36.npz`.

## Outcome
The original control harnesses, re-planted with LATIN, GREEK, EN_NOVOWEL and HEBREW held-out text through their own decode paths, recover every plant for the R37 C1 (U1, U2, U3), R38 C1 (x2 rows), R39 C1 and R38 C2 (G1, G2, G3) rows (100 % in every register; n 12-80 per register) and for the R37-C3 beam families (N1ct, N4ks, N5, X3b, X4: 10/10 each, every register). The R37-C3 direct (Z versus shuffle) families pass in every register except the per-page M1 family (`U5_L2_M1_perpage`, n=53 runes): EN_MODERN 8/10, LATIN 10/10, GREEK 10/10, HEBREW 9/10, **EN_NOVOWEL 1/10**. The EN_MODERN reproduction of the original controls holds everywhere else (U3 24/24, U2 32/32, R38-C1 36/36, R39-C1 18/18, G3 80/80, C3 beam 10/10 per family).

## Per-row table (row power = the minimum over the row's harness groups; [Wilson 95 %])
| row | harness | n (min) | EN_MODERN | LATIN | GREEK | EN_NOVOWEL | HEBREW | page tag extended |
|---|---|---|---|---|---|---|---|---|
| R37-C1-U1-CLUE-STRINGS | R37 C1 sweep.py u1_key + v3dec (plant at true key; rank test NOT re-run) | 12 | 1.00 [0.757,1.0] | 1.00 [0.757,1.0] | 1.00 [0.757,1.0] | 1.00 [0.757,1.0] | 1.00 [0.757,1.0] | yes (line 73) |
| R37-C1-U2-LP1-NUMBER-SCHEDULES | R37 C1 plant_run/run_job + enciphers_u2_u3 | 32 | 1.00 [0.893,1.0] | 1.00 [0.893,1.0] | 1.00 [0.893,1.0] | 1.00 [0.893,1.0] | 1.00 [0.893,1.0] | yes (line 72) |
| R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION | R37 C1 plant_run + E.enc_u3 | 24 | 1.00 [0.862,1.0] | 1.00 [0.862,1.0] | 1.00 [0.862,1.0] | 1.00 [0.862,1.0] | 1.00 [0.862,1.0] | yes (line 71) |
| R38-C1-SEMANTIC-WORDNET | R38 C1 control path | 36 | 1.00 [0.904,1.0] | 1.00 [0.904,1.0] | 1.00 [0.904,1.0] | 1.00 [0.904,1.0] | 1.00 [0.904,1.0] | yes (line 77) |
| R38-C1-SEMANTIC-FREQRANK | R38 C1 control path (same plants) | 36 | 1.00 [0.904,1.0] | 1.00 [0.904,1.0] | 1.00 [0.904,1.0] | 1.00 [0.904,1.0] | 1.00 [0.904,1.0] | yes (line 77) |
| R39-C1-SENSE-SIMILARITY | R39 C1 control path | 18 | 1.00 [0.824,1.0] | 1.00 [0.824,1.0] | 1.00 [0.824,1.0] | 1.00 [0.824,1.0] | 1.00 [0.824,1.0] | yes (line 77) |
| R38-C2-G1-CLAUSES-6-7 | run_gaps.py G1 (plant at true key; rank test NOT re-run) | 12 | 1.00 [0.757,1.0] | 1.00 [0.757,1.0] | 1.00 [0.757,1.0] | 1.00 [0.757,1.0] | 1.00 [0.757,1.0] | yes (line 73) |
| R38-C2-G2-PRINTED-LINE-SUMS | run_gaps.py G2 via C1 plant_run | 16 | 1.00 [0.806,1.0] | 1.00 [0.806,1.0] | 1.00 [0.806,1.0] | 1.00 [0.806,1.0] | 1.00 [0.806,1.0] | yes (line 72) |
| R38-C2-G3-LAGGED-POINTERS | run_gaps.py G3 (A3 skip-free as original) | 80 | 1.00 [0.954,1.0] | 1.00 [0.954,1.0] | 1.00 [0.954,1.0] | 1.00 [0.954,1.0] | 1.00 [0.954,1.0] | yes (line 78) |
| R37-C3-U5-L2-MAP | rescore.py plant_stream/pm_many direct Z (6 families) | 10 | 0.80 [0.49,0.943] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 0.10 [0.018,0.404] | 0.90 [0.596,0.982] | no |
| R37-C3-U5-L3-ROAD | rescore.py direct Z (2 families) | 10 | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | no |
| R37-C3-U6A-N1-CT | rescore.py beam N1ct + direct N1_pt | 10 | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | no |
| R37-C3-U6A-N2 | rescore.py direct | 10 | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | no |
| R37-C3-U6A-N4 | rescore.py beam N4ks + direct N4_read | 10 | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | no |
| R37-C3-U6A-N5 | rescore.py beam N5 | 10 | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | no |
| R37-C3-U6A-S1 | rescore.py direct | 10 | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | no |
| R37-C3-U6A-S2 | rescore.py direct | 10 | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | no |
| R37-C3-U6B-R22C | rescore.py beam X3b+X4 (structural direct control NOT re-planted) | 10 | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | 1.00 [0.722,1.0] | no |

Power here is the harness's own recovery criterion (pmax120 >= bar_v3 at N=1e6 L=120, pmax240 >= bar at N=1e6 L=240, recovery240 >= 0.90; C3 beam families the same with bar12; C3 direct families Z_plant > family null-max-Z q99 + 1), i.e. control recovery at that bar, not a new sweep bar. The N=1e6 bars are above the actual-N bars the rows use, so each recovered plant also clears the row's actual-N bar.

## Tag changes on MEASURED-CEILING.md (5 lines, authorised)
Lines 71 (U3), 72 (U2 + G2), 73 (U1 + G1), 77 (WORDNET, FREQRANK, SENSE-SIMILARITY), 78 (G3): `[plants: EN_MODERN only]` -> `[plants: EN_MODERN / LATIN / GREEK / EN_NOVOWEL / HEBREW only (R40-I1-REPLANT-CONTROLS ...; CY, OE, DE, NORSE, EN_KJV, EN_HALFVOWEL, LP1 still unplanted)]`. The tag is extended, not removed: seven registers are still unplanted. The lane id is cited as plain text (it is not in `LEDGER.json` until the coordinator merges `ledger.json`; a double-bracket cite would fail the checker).
Unchanged: line 79 (7 NEVER cells; harness not importable, below); line 80 (R10/R11 re-scores: `U5-L2-MAP` fails the EN_NOVOWEL re-plant at 1/10 and does not reproduce at EN_MODERN in the per-page M1 family at 8/10); line 82 (R22C: the structural direct control X1a/X1c/X3a and the Round 22 original harness were not re-planted, so the line's rows are not all covered even though the U6B beam families passed in all 5 registers).
Checker: `python analysis/round39/P1-measured-ceiling/check_ceiling.py` -> PASS (262 rows, 53 claim lines, 24 strong-verdict lines, 75 pins; no pin moved).

## Rows not re-planted, and why
- **R38-C2-NEVER-CELLS-RUN**: `round38/C2-never-cells/cells/run_cells.py` is a monolithic main script that writes into its own directory and re-runs sweeps; it has no importable control function, and several of its controls (hash match, word-prime test, magic-square key rank) are not plaintext-register controls in the same sense. Tag stays.
- **R22-C-LITERAL-IMPERATIVES** (Round 22 original harness) and the structural direct control of **U6B-R22C** (X1a decimation, X1c deinterleave4, X3a reversal): not re-planted. Tag on line 82 stays.
- **The non-tagged English-era harnesses named in the brief** (SHA-256-CTR / PBKDF2 seed lists R13 B-04 / R16-KDF, public pads R17, CicadaOS pads R12/R28-L1, Py2.7 `pair` R19/R20, PHP prior-dense R32-B2, glibc gen=0 R32-B3): none is on a `[plants: ...]`-tagged line; they need their own generators (C engine, PHP, glibc) or belong to the B3 / S3 assignments (skip_by_two re-decode, Py2.7 per-register power). Not touched; their page text is unchanged.

## Caveats
1. **Rank test substituted.** The original U1 and G1 controls demanded that the planted string rank #1 in the full 83-117-key grid. This lane plants the clue string and decodes at its true setting (route, relation, sign, offset) and judges recovery at the bar; rank-#1 is not re-measured (12 plants per register; Wilson lower bound 0.757). Line 73 was extended on that footing; the coordinator may prefer to hold it.
2. **n is small for several rows.** All point estimates are 1.00, but Wilson lower bounds are 0.72 (C3, n=10), 0.76 (U1 and G1, n=12), 0.81-0.95 (others). The pre-registered rule gated on the point estimate >= 0.90 with n >= 10; the lower bound is reported, not gated.
3. **G3 A3 cells** keep the original skip-free planted encipherer (the original lane's stated conditional); the lagged-pointer row's coverage of skip-bearing A3 forms is unchanged.
4. **C3 direct families** used D=150 shuffle draws and 10 seeds per register (originals: D=100-300 and a single plant), so the original single-plant pass was marginal for `U5_L2_M1_perpage` (EN_MODERN 8/10). That is a finding about the L2-MAP row, not about the new registers.
5. Plants are random 240-rune windows from the held-out R36 test halves, not LP1.
6. The committed `control_stage` draws a key start `s0 < 4000`; the X3b key list is shorter, and one EN_NOVOWEL draw crashed. The driver caps `s0` at `len(K) - 1024` (new draws, same criterion).
7. Planting at the true key and setting measures recovery, not search power over a grid; the rows' grid bars (N up to 1e6) convert recovery into an exclusion.

## Files
`PREREG.md`, `drv_c1.py` (R37 C1, R38 C1, R39 C1), `drv_gaps.py` (R38 C2 G1-G3), `drv_c3.py` (R37 C3 beam + direct), `aggregate.py`, `mk_final.py`, `results_raw.jsonl` (2050 plants), `replant_results.json`, `table.md`, `ledger.json`, `ledger_patches.json`, `run_*.log`.
Reproduce: `python -I drv_c1.py r38 EN_MODERN LATIN GREEK EN_NOVOWEL HEBREW` (then `r39`, `c1`), `python -I drv_gaps.py <regs>`, `python -I drv_c3.py beam <regs>`, `NP=10 DN=150 python -I drv_c3.py direct <regs>`, `python aggregate.py`.
