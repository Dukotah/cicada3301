# Round 40 / C1 - re-score of the 46 English-only / legacy-beam matrix cells under panel-R36 + beam_v3: RESULTS
Dated 2026-10-31. `PREREG.md` was written first. No discovery claim: 0 flagged-for-oracle, 0 beam row within reach of an actual-N bar; 1 direct near-miss (R13 DIRECTION, section "Flagged / near-miss"). Nothing here is "solved/closed/exhausted": every row is negative **conditional on** (key space regenerated here) x (keyskip1/2 after the pf_v4_12 head screen, or skip-free for direct streams) x (panel-R36, 12 registers).

## Headline
- 46 cells = 21 TRIED-EN + 25 TRIED-LEG (matches `round38/X1-redteam/o4_recount_r38.json`; list in `cells_raw.json`).
- Readings in the 46 cells records: 23 distinct (`R04 R05 R06 R08 R09 R10b/c18 R13 R14 R15 R21 R23 R24 R27 R28 R30 R31 R32 R33 R35 R36 R43 R44 R47`). Re-scored here: **11 readings** (R04, R06, R13, R27, R28, R30, R10b/c18 numerics, R32, R33, R43, R47) as **15 family parts incl. nulls/replicates**, 28,236 SWEEPROW rows (12-wide, 14th `degenerate` field), stock `AD.validate_store` ok and `check_r3_store` []. **Skipped as already done** in R37 C3: R05, R09 (U5-L2 M5/M9), R21 (U6a-S1), R23, R24 (U6b) - five readings, which fully resolve four cells (L1xF7, L8xF1, L10xF7, S2xF10) that the O4 recount had not updated. **Not re-scorable**: R08 (no adjudicator). **Inconclusive** (artefact not regenerable from committed code): R14, R15, R31, R35, R36, R44.
- Cell outcome: **35 cells -> TRIED (panel-R36)**, **3 -> PARTIAL-RESCORED** (H2xF7, H7xF4, H8xF4: another reading in the record is inconclusive), **8 unchanged** (H4xF3, H7xF9, H12xF7, L2xF3, L12xF5, L13xF5, L15xF2, S1xF5: their only readings are inconclusive). Proposed matrix after this lane: English-only/legacy cells 46 -> 8.
- Flagged-for-oracle: **none**. Near-miss (beam, clears actual-N): **none**. Closest beam rows: R43 5.96 vs 9.24 (actual-N), R32 slogan 5.88 vs 9.66, R30 5.31 vs 8.61. One direct near-miss: R13.

## Method deviations from PREREG (each forced by a measured fact; none chosen after seeing a hit)
1. **Head-screened families use pf_v4_12 (frozen point) before beam_v3**: the key spaces are 1e5-1e6 heads; at 7 ms/decode a full decode of 4.6 M slogan heads would not fit. The screen's measured power (>= 0.95 per register) is a stated limit of the negative, not hidden.
2. **N for head-screened bars = heads screened** (the key-space size; bar at survivor-N also reported and no family reached it either). Bars: `null12.json` POT, L=120.
3. **R30 key set is 125 alpha + 16 numeric, not 168 + 16**: `b1_keys.build()` needs `armada_osint/artifacts/raw/*.md`, which is not in the repo (43 auto-extracted keys missing). Recorded in `not_covered`.
4. **R04 (M4) null defect**: the first (only) run used the lane's `null_A` (rune content shuffled, word boundaries held). The `len` and `len-1` pointer families depend only on word lengths, so their null sd is 0 and their per-stream Z is 5784 / p(Z)=0.0033. That statistic is invalid for this family; the raw best-of-family statistic is not (obs 224.98 vs null best mean 226.1, p 0.72). By the two-statistic rule the family is negative. The stream is English by construction (words copied from the solved book), which is why pmax ~225 whatever LP2 does.
5. **R28 (A2) second null + natural baseline**: the lane's null (order-shuffled letter pool) flags `06|word_last|rev` and `CONCAT|word_last|rev` (p 0.0033 on both statistics). The word-last/first letters of any English running text carry the same skew and suffix structure, so a pool shuffle is a mismatched null. Re-run with each read's own letters shuffled (matched histogram): raw p 0.103 (negative); and a natural-English baseline from the solved word list (`a2base.py`, `a2_natural_baseline.json`): CONCAT|word_last|rev obs 17.1 vs natural windows mean 17.4 (67% of windows >= obs). Both runs are kept in the store, labelled.
6. **R13 DIRECTION run three times** (D=150, then D=800 and D=500 on independent null seeds) because the D=150 pass had min-possible p=0.0066 on both statistics.
7. 24 of the 48 A2 reads, 168 of 420 M6 streams and (in R47) 6 rows per relation are degenerate or below the 32-rune panel floor; they are counted and excluded from "best".
8. No stored top-N sets exist for any of these families: **all candidate sets were regenerated** from committed code (`keysets.py`, `direct.py`, unchanged lane modules imported via `importlib`).

## Controls (all passed before counting; `controls/*.json`, `parts/*.done`)
- Beam / screened families (R30, c18, R32 slogan, R32 lp, R33, R43, R47): 6 plants per relation (EN_MODERN, LATIN, GREEK x 2) enciphered with the family's own real keys (random entries) via `enc_exact` / `enc_pair`, L=240; **6/6 recovered per relation in every family** (recovered = pf_v4_12 screen passes AND L=120 pmax >= declared-N bar AND L=240 pmax >= bar AND recovery240 >= 0.90). Typical plants: pmax120 14-22, pmax240 23-30, recovery 1.000.
- Direct families (R04, R06, R13, R27, R28): held-out EN_MODERN / LATIN / GREEK text at the family's stream length beats the family-null max-Z q99 by > 1 in all three registers (Z 6-75 depending on length). Not planted through the family's own inverse op (walk / selection) except as C3 did: stated, not claimed.
- The original lanes' English-scorer controls are restated, not re-run.


## Per-family table (what was run)

| family | artefact / route | control | N | best (non-degenerate; ks1 / ks2 for beam) | bars | verdict |
|---|---|---|---|---|---|---|
| R30_B1_artifact_keys | pf_v4_12 -> beam_v3 ks1+ks2 (regen) | pass 6/6 per rel | 338,832 heads, 259 decoded | 4.829 / 5.310 | actual-N 8.71 / 8.61; declared 9.10 / 9.00 | negative |
| C18_numeric_PS_tweet_mayan | pf_v4_12 -> beam_v3 ks1+ks2 (regen) | pass 6/6 per rel | 139,152 heads, 114 decoded | 5.011 / 4.818 | actual-N 8.38 / 8.29; declared 9.10 / 9.00 | negative |
| R32_B04_slogan_seeds | pf_v4_12 -> beam_v3 ks1+ks2 (regen) | pass 6/6 per rel | 4,625,920 heads, 3903 decoded | 5.882 / 5.881 | actual-N 9.66 / 9.55; declared 9.10 / 9.00 | negative |
| R32_B04_lp_seeds_stageA | pf_v4_12 -> beam_v3 ks1+ks2 (regen) | pass 6/6 per rel | 803,840 heads, 678 decoded | 5.328 / 5.749 | actual-N 9.02 / 8.92; declared 9.10 / 9.00 | negative |
| R33_R26C_semantic_seed_zoo | pf_v4_12 -> beam_v3 ks1+ks2 (regen) | pass 6/6 per rel | 2137 rows/rel | 4.812 / 4.901 | actual-N 6.87 / 6.80; declared 9.10 / 9.00 | negative |
| R43_B5_composed_keys | pf_v4_12 -> beam_v3 ks1+ks2 (regen) | pass 6/6 per rel | 1,446,720 heads, 1291 decoded | 5.964 / 5.964 | actual-N 9.24 / 9.13; declared 9.10 / 9.00 | negative |
| R47_F01_LP2_as_pad | pf_v4_12 -> beam_v3 ks1+ks2 (regen) | pass 6/6 per rel | 112 rows/rel | 4.184 / 4.464 | actual-N 5.79 / 5.75; declared 9.10 / 9.00 | negative |

| family | artefact / route | control | N | best | null | verdict |
|---|---|---|---|---|---|---|
| R04_M4_LP1_pointer | regen, direct | pass | 16 streams (0 below floor/degenerate excluded or counted), D=300 | pmax 224.78, Z 5784.46 | p(Z) 0.0033, raw 0.7243 | negative on the raw statistic (Z invalid: null sd 0 for length pointers) |
| R06_M6_structural_counts | regen, direct | pass | 420 streams (0 below floor/degenerate excluded or counted), D=300 | pmax 7.06, Z 3.36 | p(Z) 0.3090, raw 0.5748 | negative |
| R13_R9_DIRECTION_walks_D800 | regen, direct | pass | 2274 streams (396 below floor/degenerate excluded or counted), D=800 | pmax 4.73, Z 4.68 | p(Z) 0.0062, raw 0.0062 | NEAR-MISS (see below), not flagged |
| R13_R9_DIRECTION_walks | regen, direct | pass | 2274 streams (396 below floor/degenerate excluded or counted), D=150 | pmax 4.73, Z 5.43 | p(Z) 0.0066, raw 0.0066 | first pass D=150 (superseded by D=800 / D=500) |
| R13_R9_DIRECTION_walks_D500_seed50000 | regen, direct | pass | 2274 streams (396 below floor/degenerate excluded or counted), D=500 | pmax 4.73, Z 4.87 | p(Z) 0.0040, raw 0.0040 | replicate, other null seeds |
| R27_R22A_selfembedded | regen, direct | pass | 1718 streams (36 below floor/degenerate excluded or counted), D=200 | pmax 8.99, Z 4.33 | p(Z) 0.0945, raw 0.8706 | negative |
| R28_R23A2_line_acrostic | regen, direct | pass | 24 streams (0 below floor/degenerate excluded or counted), D=300 | pmax 13.46, Z 4.12 | p(Z) 0.0033, raw 0.0033 | lane null (order-shuffled letter pool): excess explained by natural English baseline |
| R28_R23A2_line_acrostic_ownhist | regen, direct | pass | 24 streams (0 below floor/degenerate excluded or counted), D=300 | pmax 13.46, Z 3.81 | p(Z) 0.0066, raw 0.1030 | matched null: raw p 0.10, negative |

## Per-cell table (46 cells)

Verdict column: TRIED = every re-scorable reading in the cell's record re-scored (here or in R37-C3) with a passed control and no clearing row; PARTIAL = some reading inconclusive; UNCHANGED = nothing re-scorable. All re-scored readings are negative conditional on the three conditionals below.

| cell | was | reading -> artefact (control, N, best vs bars) | verdict |
|---|---|---|---|
| H2 x F6 | T-EN | R05: R37-C3 U5-L2 M5 (p(Z) 0.327, raw p 0.64)<br>R06: R06_M6_structural_counts: n=420 streams, D=300; best M6:runes-per-page:letters26+7 pmax 7.06, Z 3.36, p(Z) 0.3090, raw p 0.5748<br>R09: R37-C3 U5-L2 M9 (p(Z) 0.392, raw p 0.156) | TRIED |
| H2 x F7 | T-EN | R04: R04_M4_LP1_pointer: n=16 streams, D=300; best M4:len:base1 pmax 224.78, Z 5784.46, p(Z) 0.0033, raw p 0.7243<br>R08: not re-scorable (no adjudicator involved (longest word-length run statistic))<br>R44: INCONCLUSIVE (2012-14 book texts not committed as streams; English word-salad test only, no rune adjudicator) | PARTIAL-RESCORED |
| H3 x F7 | T-LEG | R04: R04_M4_LP1_pointer: n=16 streams, D=300; best M4:len:base1 pmax 224.78, Z 5784.46, p(Z) 0.0033, raw p 0.7243<br>R08: not re-scorable (no adjudicator involved (longest word-length run statistic))<br>R24: R37-C3 U6b R22-C X3 keyed (5.46 vs 6.04, ks1) | TRIED |
| H4 x F3 | T-EN | R14: INCONCLUSIVE (campaign7 wordsum_selfkey code not committed) | UNCHANGED-T-EN |
| H4 x F6 | T-EN | R05: R37-C3 U5-L2 M5 (p(Z) 0.327, raw p 0.64)<br>R09: R37-C3 U5-L2 M9 (p(Z) 0.392, raw p 0.156)<br>R13: R13_R9_DIRECTION_walks_D800: n=2274 streams, D=800; best A:idx:s60:b1:f1 pmax 4.73, Z 4.68, p(Z) 0.0062, raw p 0.0062 | TRIED (R13 near-miss caveat) |
| H6 x F4 | T-LEG | R30: R30_B1_artifact_keys: N=338832 heads; best 4.83/5.31 vs actual-N 8.71/8.61, declared 9.10/9.00<br>R32: R32_B04_slogan_seeds: N=4625920 heads; best 5.88/5.88 vs actual-N 9.66/9.55, declared 9.10/9.00<br>R32: R32_B04_lp_seeds_stageA: N=803840 heads; best 5.33/5.75 vs actual-N 9.02/8.92, declared 9.10/9.00 | TRIED |
| H7 x F2 | T-LEG | R10b: R30_B1_artifact_keys: N=338832 heads; best 4.83/5.31 vs actual-N 8.71/8.61, declared 9.10/9.00<br>R10b: C18_numeric_PS_tweet_mayan: N=139152 heads; best 5.01/4.82 vs actual-N 8.38/8.29, declared 9.10/9.00 | TRIED |
| H7 x F4 | T-LEG | R30: R30_B1_artifact_keys: N=338832 heads; best 4.83/5.31 vs actual-N 8.71/8.61, declared 9.10/9.00<br>R35: INCONCLUSIVE (round12/C2/texts (33 key texts) not in repo; fetch.sh needs network) | PARTIAL-RESCORED |
| H7 x F9 | T-EN | R36: INCONCLUSIVE (dated public-pad data (NIST beacon / blocks) not committed; fetch needs network) | UNCHANGED-T-EN |
| H8 x F4 | T-LEG | R30: R30_B1_artifact_keys: N=338832 heads; best 4.83/5.31 vs actual-N 8.71/8.61, declared 9.10/9.00<br>R35: INCONCLUSIVE (round12/C2/texts (33 key texts) not in repo; fetch.sh needs network) | PARTIAL-RESCORED |
| H8 x F10 | T-EN | R28: R28_R23A2_line_acrostic_ownhist: n=24 streams, D=300; best 06|word_last|rev pmax 13.46, Z 3.81, p(Z) 0.0066, raw p 0.1030 | TRIED |
| H12 x F2 | T-LEG | R10b: R30_B1_artifact_keys: N=338832 heads; best 4.83/5.31 vs actual-N 8.71/8.61, declared 9.10/9.00<br>R10b: C18_numeric_PS_tweet_mayan: N=139152 heads; best 5.01/4.82 vs actual-N 8.38/8.29, declared 9.10/9.00 | TRIED |
| H12 x F4 | T-LEG | R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| H12 x F7 | T-EN | R44: INCONCLUSIVE (2012-14 book texts not committed as streams; English word-salad test only, no rune adjudicator) | UNCHANGED-T-EN |
| L1 x F4 | T-EN | R32: R32_B04_slogan_seeds: N=4625920 heads; best 5.88/5.88 vs actual-N 9.66/9.55, declared 9.10/9.00<br>R32: R32_B04_lp_seeds_stageA: N=803840 heads; best 5.33/5.75 vs actual-N 9.02/8.92, declared 9.10/9.00 | TRIED |
| L1 x F7 | T-LEG | R24: R37-C3 U6b R22-C X3 keyed (5.46 vs 6.04, ks1) | TRIED |
| L2 x F3 | T-EN | R14: INCONCLUSIVE (campaign7 wordsum_selfkey code not committed) | UNCHANGED-T-EN |
| L2 x F4 | T-LEG | R32: R32_B04_slogan_seeds: N=4625920 heads; best 5.88/5.88 vs actual-N 9.66/9.55, declared 9.10/9.00<br>R32: R32_B04_lp_seeds_stageA: N=803840 heads; best 5.33/5.75 vs actual-N 9.02/8.92, declared 9.10/9.00<br>R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00<br>R43: R43_B5_composed_keys: N=1446720 heads; best 5.96/5.96 vs actual-N 9.24/9.13, declared 9.10/9.00 | TRIED |
| L2 x F9 | T-LEG | R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L4 x F4 | T-LEG | R32: R32_B04_slogan_seeds: N=4625920 heads; best 5.88/5.88 vs actual-N 9.66/9.55, declared 9.10/9.00<br>R32: R32_B04_lp_seeds_stageA: N=803840 heads; best 5.33/5.75 vs actual-N 9.02/8.92, declared 9.10/9.00<br>R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L4 x F9 | T-LEG | R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L5 x F4 | T-LEG | R32: R32_B04_slogan_seeds: N=4625920 heads; best 5.88/5.88 vs actual-N 9.66/9.55, declared 9.10/9.00<br>R32: R32_B04_lp_seeds_stageA: N=803840 heads; best 5.33/5.75 vs actual-N 9.02/8.92, declared 9.10/9.00<br>R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L5 x F9 | T-LEG | R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L7 x F4 | T-EN | R32: R32_B04_slogan_seeds: N=4625920 heads; best 5.88/5.88 vs actual-N 9.66/9.55, declared 9.10/9.00<br>R32: R32_B04_lp_seeds_stageA: N=803840 heads; best 5.33/5.75 vs actual-N 9.02/8.92, declared 9.10/9.00 | TRIED |
| L8 x F1 | T-LEG | R23: R37-C3 U6b R22-C structural (p(Z) 0.75, raw 0.60) | TRIED |
| L8 x F4 | T-LEG | R32: R32_B04_slogan_seeds: N=4625920 heads; best 5.88/5.88 vs actual-N 9.66/9.55, declared 9.10/9.00<br>R32: R32_B04_lp_seeds_stageA: N=803840 heads; best 5.33/5.75 vs actual-N 9.02/8.92, declared 9.10/9.00<br>R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L8 x F9 | T-LEG | R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L10 x F7 | T-LEG | R24: R37-C3 U6b R22-C X3 keyed (5.46 vs 6.04, ks1) | TRIED |
| L10 x F10 | T-EN | R27: R27_R22A_selfembedded: n=1718 streams, D=200; best everyk_k34_o12 pmax 8.99, Z 4.33, p(Z) 0.0945, raw p 0.8706<br>R28: R28_R23A2_line_acrostic_ownhist: n=24 streams, D=300; best 06|word_last|rev pmax 13.46, Z 3.81, p(Z) 0.0066, raw p 0.1030 | TRIED |
| L11 x F4 | T-EN | R32: R32_B04_slogan_seeds: N=4625920 heads; best 5.88/5.88 vs actual-N 9.66/9.55, declared 9.10/9.00<br>R32: R32_B04_lp_seeds_stageA: N=803840 heads; best 5.33/5.75 vs actual-N 9.02/8.92, declared 9.10/9.00 | TRIED |
| L11 x F10 | T-EN | R27: R27_R22A_selfembedded: n=1718 streams, D=200; best everyk_k34_o12 pmax 8.99, Z 4.33, p(Z) 0.0945, raw p 0.8706<br>R28: R28_R23A2_line_acrostic_ownhist: n=24 streams, D=300; best 06|word_last|rev pmax 13.46, Z 3.81, p(Z) 0.0066, raw p 0.1030 | TRIED |
| L12 x F4 | T-LEG | R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L12 x F5 | T-EN | R31: INCONCLUSIVE (crib readouts are 5-9 runes (< panel floor); stored top-N absent; own T1 INCONCLUSIVE) | UNCHANGED-T-EN |
| L12 x F9 | T-LEG | R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L13 x F4 | T-LEG | R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L13 x F5 | T-EN | R31: INCONCLUSIVE (crib readouts are 5-9 runes (< panel floor); stored top-N absent; own T1 INCONCLUSIVE) | UNCHANGED-T-EN |
| L13 x F9 | T-LEG | R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L15 x F2 | T-EN | R15: INCONCLUSIVE (campaign7 hill5_magic code not committed) | UNCHANGED-T-EN |
| L16 x F4 | T-LEG | R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L16 x F9 | T-LEG | R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |
| L17 x F4 | T-EN | R32: R32_B04_slogan_seeds: N=4625920 heads; best 5.88/5.88 vs actual-N 9.66/9.55, declared 9.10/9.00<br>R32: R32_B04_lp_seeds_stageA: N=803840 heads; best 5.33/5.75 vs actual-N 9.02/8.92, declared 9.10/9.00 | TRIED |
| L18 x F4 | T-EN | R32: R32_B04_slogan_seeds: N=4625920 heads; best 5.88/5.88 vs actual-N 9.66/9.55, declared 9.10/9.00<br>R32: R32_B04_lp_seeds_stageA: N=803840 heads; best 5.33/5.75 vs actual-N 9.02/8.92, declared 9.10/9.00 | TRIED |
| S1 x F5 | T-EN | R31: INCONCLUSIVE (crib readouts are 5-9 runes (< panel floor); stored top-N absent; own T1 INCONCLUSIVE) | UNCHANGED-T-EN |
| S2 x F7 | T-EN | R47: R47_F01_LP2_as_pad: N=112 rows/rel; best 4.18/4.46 vs actual-N 5.79/5.75, declared 9.10/9.00 | TRIED |
| S2 x F10 | T-EN | R21: R37-C3 U6a-S1 (p(Z) 0.48) | TRIED |
| S5 x F4 | T-LEG | R33: R33_R26C_semantic_seed_zoo: N=2137 rows/rel; best 4.81/4.90 vs actual-N 6.87/6.80, declared 9.10/9.00 | TRIED |

## Flagged / near-miss
- **Flagged-for-oracle (clears actual-N, beam): none.** No family proceeded to L=240 or to an oracle bundle (nothing cleared). R47's top row (8.70) is degenerate (T6 self-key, constant output) and excluded.
- **R13 DIRECTION (direct near-miss, not flagged).** Best `A:idx:s60:b1:f1` / `s61` (a backward self-indexing walk: p <- p - idx(c[p]), F skipped; both starts reach the same 400-rune path): pmax 4.733 (EN_MODERN-class register argmax per rows), non-degenerate (IoC*N 1.01, mds 16). Against doublet-matched shuffled-LP2 nulls: D=150 p(Z)=raw=0.0066; D=800 p(Z)=raw=0.0062; D=500 on other seeds p(Z)=raw=0.0040 (pooled about 5 of 1,450 null draws reach it; Wilson upper bound ~0.013). By the pre-registered two-statistic rule this is a near-miss. Why it is not flagged: (a) amplitude - a readable 400-rune stream in a panel register scores pmax in the tens (planted controls Z 11-18; contiguous 400-windows of LP2 itself sit at pmax 1.3, max 2.99), 4.7 is the random-level scale for the best of ~2,300 correlated reads; (b) the transliteration of the stream (`GDINCIAESRBAEBXLAJNGXOWHUJOEAIMROCODHWMNEAELGEUYOBLEAOBX...`) reads as noise; (c) there is no key or relation to re-test or to take to L=240. Listed for the red team and for the coordinator: a human read is cheap if wanted.
- **R28 06|word_last|rev** (pmax 13.46): 0.37 above the max of 12 natural English word-final windows of the same length; the larger CONCAT streams are at the natural level. Listed for the red team, not a near-miss under the matched null (raw p 0.103).
- Closest beam rows (all far below actual-N): R43 5.964 (ks1/ks2) vs 9.24 / 9.13; R32 slogan 5.882 / 5.881 vs 9.66 / 9.55; R32 lp 5.749 (ks2) vs 8.92; R30 5.310 (ks2) vs 8.61; c18 5.011 (ks1) vs 8.39; R33 4.901 vs 6.80; R47 4.464 vs 5.75.

## Conditionals now carried (Aiming Test Q4)
(1) key space = exactly what was regenerated: R30 125 alpha + 16 numeric keys (<= 12 phases, sign, atbash, 52 page starts); c18 P.S./tweet-handle/Mayan streams (all phases); R32 139 slogan seeds x 16 generators x 5 reductions x dir x sign x atbash (stage A + per-page restarts) and 1,256 lp seeds (stage A); R33 2,137 keystreams at offset 0; R43 289,344 composed configs on pages 0,1,2,5,20; R47 4 LP2 variants x 2 signs on T1/T2/T3/T6; direct families as listed. (2) transition model = keyskip1 + keyskip2 under beam_v3 (head-screened by pf_v4_12 at its frozen point where used, per-relation FPR 5e-4, min power 0.952), skip-free for direct streams. (3) adjudicator = panel-R36, 12 registers.

## not_covered (collected; also in `ledger.json` per row)
43 auto-extracted B1 alpha keys (raw archive not committed); the B1 interrupter-beam arm; pages < 120 runes (all page-start heads need L=120; page 54 for B5); B04 stage B offsets and non-slogan/lp seed groups; R33 offsets != 0; R43 atbash arm, goff > 63, the other 49 pages; R47 T4 (63 values), T5, all-pairs page XOR, canon-as-key; R04 decoded-word / lagged pointers; R06 other count sequences; R13 walks beyond direction.py's grid and the keyed layer; R27 keyword-cued selections; R28 24 of 48 reads below the panel floor; HEBREW / NORSE not planted in the beam controls (EN_MODERN / LATIN / GREEK only, as C3). The pf_v4_12 screen can drop up to ~5% of true-key heads.

## Could not be re-run (inconclusive, with what is missing)
- R14 wordsum_selfkey, R15 hill5_magic (cells H4xF3, L2xF3, L15xF2): the campaign7 code is not committed.
- R31 B3 crib readouts (L12xF5, L13xF5, S1xF5): 5-9-rune readouts are below the panel's 32-rune floor and the original T1 was INCONCLUSIVE by its own control.
- R35 keytexts (H7xF4, H8xF4 partial): `round12/C2/texts/` is not in the repo; `fetch.sh` needs network and the texts are not hash-pinned.
- R36 public pad (H7xF9): dated pad data not committed (network fetch).
- R44 bookcipher (H12xF7; H2xF7 partial): the 2012-14 book texts are not committed as inputs; the original test had no rune adjudicator.
- R08 (M8 word-length run) involves no adjudicator and is not affected by the English-only conditional.

## Coordinator decisions
1. Apply `ledger.json` (18 rows: 12 re-scored families incl. R13 as `open`, 6 inconclusive) and `ledger_patches.json` (matrix: 35 cells -> TRIED, 3 -> PARTIAL, 8 unchanged; `not_covered` narrowed on B-04, R16-KDF, R26-C, R22-A, R23-A2, F-01, R10-L2-MAP, R10b rows)? Note R13 is proposed as `open` (not `negative`) because of the replicated direct near-miss.
2. R13: want a human read of the 400-rune stream / a stronger positional-structure-matched null? (Cheap; the stream is in `parts/R13_R9_DIRECTION_walks_D800.jsonl` and regenerable from `direction.py`.)
3. Supply or commit the missing artefacts if these readings matter: campaign7 code (R14/R15), `round12/C2/texts` (R35), dated pads (R36), 2012-14 book texts (R44), `armada_osint/artifacts/raw` (43 B1 keys).
4. The R04 M4 Z statistic is invalid for any pointer family that depends only on word lengths under `null_A`; recommend recording that for the next direct-family lane.

## Files
PREREG.md, RESULTS.md, ledger.json, ledger_patches.json, rescore_summary.json, rescore_rows.jsonl (28,236 SWEEPROW rows, 12-wide + degenerate; header sweep `round40/C1/rescore-all`), cell_table.json / cell_table.md / cell_counts.json, cells46.py / cells_raw.json (the 46 cells), controls/*.json, parts/ (per-family rows + `.done` metadata), a2_natural_baseline.json, c1.log, d_*.out; code: lib.py (C3 machinery repointed), c1common.py, engine.py, keysets.py, run_screened.py, run_beam.py, direct.py, a2base.py, final.py, build_deliverables.py, ledger_build.py, build_results.py. Reproduce: `python run_screened.py {r30|c18|r43|r32|r32lp}; python run_beam.py {r33|r47}; python direct.py {m6|m4|a2|self|dir}` (`DIR_D=800`, `DIR_D=500 DIR_SEED=50000`, `A2_NULL=own`), `python a2base.py`, `python final.py`, `python build_deliverables.py`, `python build_results.py`.
