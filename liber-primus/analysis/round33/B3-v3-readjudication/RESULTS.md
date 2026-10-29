# Round 33 / B3 -- v3 re-adjudication of the Round 32 B1/B2 survivor rows: RESULTS

_2026-10-29. Pre-registered in `PREREG.md` (one dated addendum: null enlarged to 12,000 draws, run budget 1380 s, after a smoke timing). Decoder `beam_decode_v3` panel_max, hard max, lam_u=4, beam_w=400, keyskip1 = advance 1, keyskip2 = advance 2, L=120, sign -1, o=0; nine-register panel adjudicator. No `free`. Both stores' `sweep_rows.jsonl` were present (B1 192,066 rows, B2 212,218)._

## Headline
- **404,284 of 404,284 stored survivor rows (100%) re-decoded through v3** at ~174-181 decodes/s (wrong-key decodes are 3-5x faster than I1's planted-key speed). **0 rows clear the v3 bar; 0 flagged for oracle.** Best v3 pmax 7.068 (B1 keyskip2, seed 1354603465, LP1_REAL) against bars of 8.546 / 8.373. This says nothing about any key outside the sampled survivors.
- The best seeds are the same ones driftbeam surfaced in Round 32 (keyskip2 7.068): in the sampled survivors the register-aware search did not reveal a new high row.

## 1. Control (before any null counted; `control.json`)
Stage-2 path of B3 (v3 decode + panel), true key handed over, key = a stored survivor seed of the family, L=120, I2 held-out halves, 5 EN_MODERN + 5 EN_NOVOWEL per cell, recovery >= 0.90.

| store | family | relation | EN_MODERN recovered | EN_NOVOWEL recovered | min plant pmax |
|---|---|---|---|---|---|
| B1 | bash4.2 | keyskip1 | 5/5 | 5/5 | 15.3 |
| B1 | bash4.2 | keyskip2 | 5/5 | 5/5 | 15.7 |
| B1 | bash4.2_i32 | keyskip1 | 5/5 | 5/5 | 15.5 |
| B1 | bash4.2_i32 | keyskip2 | 5/5 | 5/5 | 16.5 |
| B2 | mt_scale | keyskip1 | 5/5 | 5/5 | 16.0 |
| B2 | mt_scale | keyskip2 | 5/5 | 5/5 | 16.1 |
| B2 | mt_mod | keyskip1 | 5/5 | 5/5 | 14.8 |
| B2 | mt_mod | keyskip2 | 5/5 | 5/5 | 16.1 |
| B2 | php_scale | keyskip1 | 5/5 | 5/5 | 16.5 |
| B2 | php_scale | keyskip2 | 5/5 | 5/5 | 15.5 |
| B2 | php_mod | keyskip1 | 5/5 | 5/5 | 13.7 |
| B2 | php_mod | keyskip2 | 5/5 | 5/5 | 16.3 |

**120/120 plants recovered (all 12 cells >= 3; EN_NOVOWEL 5/5 in every cell); every plant pmax exceeds both v3 bars (min 13.7).** Declared deviations: the R32 prefilter is outside B3's path (survivors are already past it), so this is not the 2^16-seed chunk control; and the key is handed over, so it is a decode-power test, not a search test.

## 2. v3 null and bar (`null_v3.json`)
Real LP2 stream, `Random(3301+k).shuffle`, first 120 runes, k=0..11999, keys round-robin over the six key families (stored survivor seeds), both relations, panel pmax. Legacy `en` max -6.54 / -6.46 (blind to NOVOWEL, per I1).

| relation | N_null | mean | p99 | empirical max | POT u90 / beta | N re-adjudicated | POT bar (alpha 0.01) | binds |
|---|---|---|---|---|---|---|---|---|
| keyskip1 | 12,000 | 2.20 | 4.005 | 5.239 | 3.135 / 0.387 | 119879 | 8.546 | pot |
| keyskip2 | 12,000 | 2.22 | 3.992 | 5.666 | 3.161 / 0.372 | 120003 | 8.373 | pot |

**Bars of record: keyskip1 8.546, keyskip2 8.373.** The POT bar binds (the empirical max at N=12,000 is far lower); it extrapolates the exponential tail ~10x past the null N, so it is a modelled bar, not an observed one. Diagnostic: the 120k re-adjudicated rows (survivors, not a pure null) have p99.99 = 6.05 / 6.19 and max 6.68 / 7.07, below the bar, so the extrapolation is not obviously too low. The hitfn20 driftbeam bars (6.8-7.6 at actual N) were not used.

## 3. Coverage and best pmax vs bar per store x relation (final, after the coordinator-ordered completion)

| store | relation | rows re-decoded | store rows | fraction | best pmax (register, seed) | bar | clears |
|---|---|---|---|---|---|---|---|
| B1 | keyskip1 | 96,033 | 96,033 | 1.000 | 6.679 (EN_HALFVOWEL, bash4.2_i32:1375265595) | 8.546 | no |
| B1 | keyskip2 | 96,033 | 96,033 | 1.000 | 7.068 (LP1_REAL, bash4.2:1354603465) | 8.373 | no |
| B2 | keyskip1 | 106,109 | 106,109 | 1.000 | 6.856 (EN_KJV, mt_scale:3941606801) | 8.546 | no |
| B2 | keyskip2 | 106,109 | 106,109 | 1.000 | 6.554 (EN_KJV, php_scale:562123959) | 8.373 | no |

The first pass (239,882 rows, 59.3%) was extended by `resume.py` over the rest of the same Random(3301) permutation, appended to `readjud_rows.jsonl` (404,284 SWEEPROW rows, kid prefixed `v3:`; `validate_store` passes on all rows, `check_r3_store` returns []). **The bars 8.546 / 8.373 remain the bars of record and are MODELLED**: a peaks-over-threshold exponential-tail fit to the 12,000-draw null, extrapolated about 10x past it (to N~1.2e5), deliberately not enlarged or refit at the final N=202,142 per relation (at that N the same fit would be a little higher, so the bars are slightly lenient by the modelling, not stricter). The 202k re-adjudicated rows themselves peak at 6.86 / 7.07 (p99.99 6.09 / 6.17). 0 rows clear; 0 flagged; no L=240 re-screen was triggered. All store cells now report coverage 1.00 of the STORED SURVIVORS; this is still survivors only, not the orbits.

## 4. v3's measured power per register at this bar
From the control (30 plants per register x relation, true key): EN_MODERN 30/30 recovered with pmax >= bar 30/30 (keyskip1 and keyskip2); EN_NOVOWEL 30/30 recovered with pmax >= bar 30/30 (both). Conditional on a stored survivor row being the correct key, v3 at L=120 finds EN_MODERN and EN_NOVOWEL with measured power ~1.0 (n=30 per cell; 95% lower bound ~0.90). The other seven registers: I1 envelope only (matched relations), not re-measured here. Survivor coverage is itself capped by the R32 prefilter: EN_NOVOWEL prefilter power 0.47 and EN 0.74, so the fraction of 'correct key anywhere in the store's stated seed set' reached for NOVOWEL is about 1.00 x 0.47 = 0.47 (EN about 0.74), before each store's own seed-space coverage (B1 1.00 of its set; B2 tier b 0.97% of 2^32 per twist). Value = coverage x power: the v3 gain applies to the survivors, not the dropped orbit.

## 5. Flagged rows
None. No row reached its bar, so no L=240 re-screen was triggered. Highest rows for the record (`readjud_summary.json` `top_keep`): keyskip2 7.068, keyskip1 6.679, 6.608, keyskip2 6.496, 6.476, keyskip1 6.439 ...

## 6. The three conditionals
1. **Key space:** only the Round 32 prefilter survivors of B1 (74 x 2^20 bash 4.2 auto-seeds x LP64/ILP32) and B2 (tier a prior-dense + tier b 0.97% of 2^32 x mt/php x scale/mod), keystreams regenerated by the R32 `ks()`; 100% of stored survivors (completed by resume.py).
2. **Transition model:** keyskip1 (advance 1) and keyskip2 (advance 2) only, beam_w 400, o=0, sign -1, L=120.
3. **Adjudicator register:** the nine-register trigram panel; v3's search objective is the same panel (circularity declared in I1 s6).

## 7. not_covered
- free relation (3.7 decodes/s at L=120 for v3; ~1e5 s for the store)
- the ORBITS: seeds the Round 32 prefilter dropped (26-55% of planted keys per R32 control; EN_NOVOWEL prefilter power 0.47) are never re-decoded -- v3 repairs the decoder, not the prefilter
- R32 I2 survivor lists (B-04 225, R16-KDF 48, R16-PRNG 20, R17 5,730): stored as decoded texts without ciphertext/key, not re-decodable by v3
- L=120 screen only (L=240 only for flagged rows; none)
- cross-relation, advance>=3, resets, interrupters, registers outside the nine-register panel
- bar is a POT exponential-tail extrapolation from N_null=12,000 to N~1.2e5 per relation (10x); the empirical-max bars are 5.24 / 5.67
- control is the stage-2 path with the true key handed over (not the 2^16-seed chunk; prefilter not re-run); 5 plants per register per cell

## 8. Decisions for the coordinator
1. The v3 bar remains a modelled extrapolation; an observed null at N~2e5 (about 2e5 draws, roughly 40 min) would replace it.
2. The prefilter, not the decoder, is now the limiting coverage factor (EN_NOVOWEL prefilter power 0.47): a NOVOWEL-aware re-prefilter of the orbits is the next lever.
3. The R32 I2 text-only survivor lists still need ciphertext/key regenerated per source to be v3-decoded.
