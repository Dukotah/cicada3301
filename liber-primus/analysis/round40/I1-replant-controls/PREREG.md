# Round 40 / I1 replant controls - PREREG
Written 2026-10-31 (Pacific), BEFORE any driver output (no results file exists in this directory when this is written).

## Question
The `[plants: ...]` tags on `MEASURED-CEILING.md` mark strong-verdict lines whose positive controls planted only EN_MODERN (or EN_MODERN/LATIN/GREEK).
Does the same control, re-planted with LATIN, GREEK, EN_NOVOWEL and HEBREW held-out plaintext, recover at power >= 0.90 through the same decode path?

## Rows (ledger ids on the tagged lines) and harness used
Plant plaintext: `data/panels/testhalves-r36.npz` (held-out halves), registers LATIN, GREEK, EN_NOVOWEL, HEBREW; EN_MODERN re-run as the reproduction check.
Decode path: the ORIGINAL harness code, imported unmodified (import only; outputs redirected to this directory), plants swapped in through each harness's own `plant_run` / `S.U` page-0 swap / `plant_beam`.
Recover = the harness's own `judge`: pmax120 >= bar_v3(N=1e6, L=120), pmax240 >= bar_v3(N=1e6, L=240), recovery240 >= 0.90 (bars at N=1e6 are >= the actual-N bars used by the rows, so this is the stricter test). Power = recovered / planted; Wilson 95% interval reported; the tag changes only if the Wilson LOWER bound is... see rule below.

| # | ledger row(s) | harness (committed code) | plant plan per register |
|---|---|---|---|
| 1 | R37-C1-U1-CLUE-STRINGS | `round37/C1-composed-clue-readings/sweep.py` key builders `u1_key` (direct / sha256ctr / pbkdf2), `v3dec` | 3 routes x 2 relations x 2 reps = 12 plants at L=120 and 240. SUBSTITUTION: planted key decoded at its true setting; the original rank-#1-in-grid test is NOT re-run (cost) |
| 2 | R37-C1-U2-LP1-NUMBER-SCHEDULES | same file, `plant_run` / `run_job`, `enciphers_u2_u3` | all 32 variants (16 x a/b), 1 plant each |
| 3 | R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION | same, `E.enc_u3` | all 24 cells (rho x M x A1/A2/A3 x rel), 1 plant each |
| 4,5 | R38-C1-SEMANTIC-WORDNET, R38-C1-SEMANTIC-FREQRANK | `round38/C1-semantic-road/sweep.py` control path (`EN.enc`, `run`) | 6 variants x 3 modes x 2 reps = 36 plants |
| 6 | R39-C1-SENSE-SIMILARITY | `round39/C1-sense-similarity/sweep.py` control path | 36 plants |
| 7 | R38-C2-G1-CLAUSES-6-7 | `round38/C2-never-cells/gaps/run_gaps.py` (`g1_jobs`, `S.u1_key`) | 3 routes x 2 rel x 2 reps = 12; same rank-test substitution as row 1 |
| 8 | R38-C2-G2-PRINTED-LINE-SUMS | `run_gaps.py` G2 control (C1 `plant_run`, sequence `pline`) | 16 plants |
| 9 | R38-C2-G3-LAGGED-POINTERS | `run_gaps.py` G3 control (`g3_enc_*`, `g3_run`) | all G3 cells x 2 reps |
| 10 | R38-C2-NEVER-CELLS-RUN | `round38/C2-never-cells/cells/run_cells.py` | not run unless budget remains: the cell scripts are monolithic main-scripts that write their own directories and re-run sweeps; a clean import is not possible. Tag stays (kill clause) |
| 11 | R37-C3-U5-L2-MAP, U5-L3-ROAD, U6A-N2, N4, S1, S2 | `round37/C3-rescore-reopened/rescore.py` `plant_stream`, `pm_many` (direct Z test) | per family: its own n and committed `null_max_Z_q99` (from `rescore_summary.json`); 10 plants (seeds 7..16), D=60 shuffle null each; pass = Z_plant > q99 + 1 (the harness's own rule). SUBSTITUTION: D=60 not 300/200/150/100 |
| 12 | R37-C3-U6A-N1-CT, U6A-N5 (beam) | `rescore.py` `control_stage` machinery (`plant_beam`, `v3dec`, families N1ct, N4ks, N5, X3b, X4) | per family 2 rel x 5 reps = 10 plants |
| 13 | R37-C3-U6B-R22C (+R22-C-LITERAL-IMPERATIVES cite) | `rescore.py` X3b / X4 beam families (item 12) + structural direct (item 11 style) | as items 11 and 12 |
| 14 | the non-tagged English-era harnesses listed in X1 (SHA-256-CTR/PBKDF2 seed lists, public pads, CicadaOS pads, Py2.7 `pair`, PHP prior-dense, glibc gen=0) | R13 B-04, R16-KDF, R17, R28-L1, R19/R20, R32-B2/B3 controls | NOT in this lane's tagged set; skip. B3 (Round 40) re-decodes the grids with keyskip1+keyskip2; Py2.7 is S3 (list item 5); PHP/glibc need their C/PHP generators. Their page text is unchanged by this lane |

## Rules
- Tag change rule (pre-registered): a line's `[plants: ...]` tag is extended to name the extra registers ONLY when EVERY ledger row on that line has, in that register, power >= 0.90 point estimate with n >= 10 and Wilson lower bound reported (lower bound stated, not gated). A register below 0.90 stays out of the tag and the measured power is written in RESULTS. If a row's harness is not runnable, its line keeps its tag.
- Kill: an import that writes into another lane's directory, or fails, kills that row's re-plant (tag stays).
- EN_MODERN reproduction: the EN_MODERN plants must recover at the original rate (>= 0.90) or the harness is judged not reproduced and no tag moves.
- One small Python process at a time; RAM check >= 0.4 GB before each; no `git`; no foreclosure vocabulary.
