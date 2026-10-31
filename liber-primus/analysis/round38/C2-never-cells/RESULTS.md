# Round 38 / C2 - NEVER cells and C1-R37 gaps: RESULTS
PREREG.md dated 2026-10-30T15:27 before any output. Panel-R36 (sha a0682f0c...), beam_v3 panel_max, ks1+ks2, bars_v3 at actual N and N=1e6, bar12 cross-check. 12-wide rows; `AD.validate_store` ok and `check_r3_store` [] on every store. No git. The session stalled overnight; resumed 2026-10-31 from the on-disk outputs and the N5/N4 matched null was topped up (D 30 / 22).
Declared amendments to PREREG: G1 adds a digits-kept form of clause 7 (384 decodes, not 320); G2 = 768 decodes (target ~300); the A3/cw planted control is skip-free (the cw pointer is circular under skips; a first fixed-point encipherer did not converge and was replaced by a causal skip-free one); L8xF6 = 841 decodes, ks1; N5/N4 bars are also reported at the SCREEN N.

## Verdict
NEGATIVE (bounded, construction-conditional) for G1, G2, G3 and all six (a)-cell lanes. The only rows above a bar are the L=240 N5/N4 re-runs (table B): above bars_v3 at the screen N, but inside the matched cipher-derived-key null (p 0.16 N4, 0.74-0.78 N5), below the N=1e6 bar, and decoding to non-language. Flagged-for-oracle anyway (bundle written) because the preregistered rule was pmax >= bar.

## Table A - C1-R37 gaps (L=120, 1,728 decodes)
| gap | control (planted) | N per rel | best (register) | bar_v3 actual N / N=1e6 |
|---|---|---|---|---|
| G1 clauses 6/7, direct + SHA-CTR + PBKDF2 | 6/6 plants rank #1 of 32-35 keys; L120 16.0-21.4, L240 22.7-28.6, rec 1.0; runner-up 4.3-5.2 | 192 | ks1 4.259 (HEBREW, sha256ctr C7 as-written); ks2 4.323 (LP1_REAL, direct C7) | ks1 5.990 / 9.235; ks2 5.911 / 9.034 |
| G2 printed-line sums (60 lines, 6 pages) as U2 | 16/16 plants (8 variants x 2 rel); min L120 15.8, min rec 0.996 | 384 | ks1 4.567 (NORSE, prime/m29/additive, page 1); ks2 4.537 (EN_KJV, index/m28/pointer) | ks1 6.252 / 9.235; ks2 6.164 / 9.034 |
| G3 lag-1 cipher-word (cw) / decoded-word (dw) pointers | 80/80 plants (40 cells x 2); A1/A2 min L120 14.2; A3/cw (skip-free plant) min 16.5 | A3: 96; direct: 384 | ks1 4.911 / ks2 4.700 (LP1_REAL, cw prime M28 self A3); direct 4.038 (GREEK, dw index M29 A2) | 5.727 / 5.658; direct 6.252 (ks1 bar) / 9.235 |

0 gate runs, 0 flagged, 0 near-miss. Printed-line parse: the physical rune lines of pages 01, 03, 05, 06, 14, 73 (10, 8, 10, 20, 8, 4 lines = 60) from data/scream314_lp.md; plaintext via the C2-R37 decode_pos path; value = sum of the line's plaintext Gematria primes (or rune indices), F interrupters = 0; ascending page-label order. First sums 332, 757, 1009, 691, 353 reproduce the published line primes.

## Table B - N5 / N4 at L=240 (top 50 of each from C3-R37, both relations; L=120 reproduction 200/200 exact)
| family | control | best L=240 (register) | bar_v3 N=50 / screen N / N=1e6 | rows over screen-N bar | matched cipher-derived-key null (fixed configs, doublet-matched shuffles; family max) |
|---|---|---|---|---|---|
| N5 (screen N 2,320) | 12/12 plants (EN/LATIN/GREEK x 2 rel x 2 keys), min L240 22.0, rec >= 0.983; AN END (85 runes) under phi(prime) decodes, rec 1.0 / 0.93 | ks1 7.446, ks2 7.446 (LATIN, phi_phi_prime_RI s-1 o11 w0) | ks1 6.023 / 7.376 / 9.514; ks2 5.860 / 7.135 / 9.150 | 1 and 1 (of 50) | D=22: null mean 8.05, max 9.37; 16 (ks1) / 17 (ks2) draws exceed observed, p 0.74 / 0.78 |
| N4 keystream (screen N 168) | 12/12 plants, same | ks1 8.553, ks2 8.572 (EN_HALFVOWEL, b5 p1 ks-1 w10000) | ks1 6.023 / 6.450 / 9.514; ks2 5.860 / 6.263 / 9.150 | 5 and 5 | D=30: null mean 7.82, max 9.56; 4 draws exceed observed, p 0.16 |

Reading: the bars_v3 null shuffles the ciphertext but keeps the key fixed; these keys are functions of the ciphertext (digit planes of its own prime magnitudes; generators of it), so that null is not matched. The matched null puts the family maximum at ~7.8-8.1 at L=240, so the observed rows are ordinary; the C3 N5 row (6.304 at L=120) sits at 6.5-7.0 at L=240, inside it too. Decoded text (N4: UTHSOYIASRTRINISTNTHYLSSAETHIAINGYSAESS...) is high-frequency-letter salad scored by EN_HALFVOWEL, not prose. Caveats: the matched null is fixed-config (anti-conservative: the 50 were chosen on real L=120 scores) and D is small. `n5n4/oracle/bundle.json`: single window per row, no second independent page, no held-out clause; expected NOISE-CROSSER, owner decision. This also shows the "clearer" criterion needs a matched null for N4/N5-class keys.

## Table C - the 60 NEVER cells
| outcome | cells | n |
|---|---|---|
| run, all below bar/null, controls passed | H5xF1 (348 direct; best 3.425 HEBREW vs ks1 bar 6.707; shuffled-family-null p 0.78); H6xF2 (160; ks1 4.357 CY vs 5.657, ks2 3.554 vs 5.591); L8xF6 (841 ks1; 5.007 CY vs 6.550); L15xF6 + L15xF7 (384; ks1 3.596 vs 5.990, ks2 4.097 vs 5.911); L17xF7 (5,760 hashes: 160 units x 12 reps x SHA-512/BLAKE2b/SHA3-512, 0 matches, control found); L4xF3 (word primality: LP2 619/2928 vs null 615+-19, p 0.43; LP1 135/726 vs 147+-9, p_lower 0.085; plant detected) | 7 |
| no operation stated | `closed_no_operation.md` | 34 |
| C1-R38 (semantic F5), deferred | H1,H2,H3,H4,H5,H8,H9,H10,L1,L2,L4,L5,L7,L8,L9,L10,L11,L14,L18 x F5 | 19 |

No (a)-cell was left unrun. Final matrix after this lane (140 applicable cells): NEVER-open 19 (all C1-R38), TRIED 38 (31 + 7; EN_MODERN-only control conditional), T-EN 21, T-LEG 25, PART 3, NO-OPERATION-STATED 34 (19+38+21+25+3+34 = 140).
Cell conditionals: L8xF6 covers only the arithmetic-progression period-4 subfamily (convenient) and no per-page restart; L15 covers the held 5x5 only (page-5 square and the 4x4 are not held); L17xF7 hashed the md-file pages (25 with runes) and the 55 stream pages, not archived web objects.

## Files
PREREG.md, prereg_time.txt, lib.py, closed_no_operation.md, ledger.json, ledger_patches.json; gaps/ (run_gaps.py, make_printed_lines.py, printed_lines.json, control.json, sweep_rows.jsonl, sweep_summary.json, summary_final.json); n5n4/ (run_b.py, run_null.py, make_bundle.py, control.json, rows_L240.jsonl, summary.json, summary_final.json, null_N4/N5.jsonl, null_summary.json, oracle/); cells/ (run_cells.py, one subdir per cell with results.json, rows.jsonl).

## Decisions for the coordinator
1. N5/N4 oracle bundle: recommend logging NOISE-CROSSER (matched null + non-language text). 2. Apply ledger_patches.json. 3. A matched (cipher-derived-key) null should be standard for N4/N5/X4-class keys; bars_v3 over-flags them (ties to I2-R38). 4. Round-39 critic: do any of the 34 no-operation closures hide a literal rule (H8xF1, L11xF1, L18xF1 likeliest)?
