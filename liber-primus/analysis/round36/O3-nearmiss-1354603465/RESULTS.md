# R36 / O3 - autopsy of the recurring near-miss, bash 4.2 seed 1354603465 (RESULTS)

Pre-registration: `PREREG.md` (dated first). Code: `autopsy.py` (decodes/nulls), `report.py` (aggregation). Data: `cells.json`, `nulls.json`, `plant.json`, `verif_raw.json`, `repro.json`, `verifiers.json`, `decode_text.md`, `ledger.json`.

## Verdict
**NOISE (negative, bounded). Not escalated.** All three verifiers kill; the positive control passed. Nothing here is "solved" or "confirmed", and nothing is flagged for the oracle.

## 1. Reproduction (`repro.json`) - PASSED
Seed 1354603465, bash 4.2, `$RANDOM%29`, sign -1, key offset 0, beam_v3 panel_max, beam_w 400, L=120:

| ABI | keyskip2 | keyskip1 | free |
|---|---|---|---|
| LP64 | **7.068 (LP1_REAL)**, identical to R33 to 15 digits | 4.273 (R33 at beam_w 64: 2.800) | 9.696 |
| ILP32 | **6.762 (LP1_REAL)**, identical | 4.192 (R33: 2.863) | 8.723 |

The 12-register panel changes nothing (same decode, pmax12 = pmax9 to 1e-7, LP1_REAL argmax). keyskip1 differs from R33 only through beam width (400 vs 64). Bars (bar_v3 lp2 keyskip2 L=120): 8.058 at actual N (69,017), 9.034 declared 1e6.

## 2. pmax vs L, best cell (LP64 keyskip2 sign -1, o=0, c0=0) - the curve FALLS
Null columns are verifier A's random in-orbit seeds (2000 / 1000 / 400) in the identical cell.

| L | pmax9 (argmax) | pmax12 | null median | null q99.9 | null max | excess over null median | bar_v3 N_act (N_decl) |
|---|---|---|---|---|---|---|---|
| 120 | 7.068 (LP1_REAL) | 7.068 | 2.22 | 4.52 | 4.78 | **4.85** | 8.06 (9.03) |
| 240 | 6.537 (LP1_REAL) | 6.537 | - | - | - | - | 8.26 (9.15) |
| 262 (page 0) | 6.638 (LP1_REAL) | 6.638 | 3.06 | 5.19 | 5.44 | **3.58** | 8.33 (9.20)* |
| 400 | 6.010 (LP1_REAL) | 6.010 | - | - | - | - | 8.65 (9.48) |
| 729 (pages 0-2) | 5.755 (LP1_REAL) | 5.755 | 4.67 | 6.75 | 6.83 | **1.08** | 8.27* |

\*interpolated / clamped beyond the fit nodes; verifier A's null is the bar of record at 262 and 729. ILP32 keyskip2: 6.76, 6.11, 6.29, 6.08, 6.66 (argmax wanders LP1_REAL / EN_KJV / LP1_REAL / EN_KJV / EN_KJV).

**PREREG correction (disclosed):** I wrote that a wrong key's pmax is L-independent. It is not: the beam's panel_max search over-fits the panel more at larger L, so the null median rises 2.2 -> 3.1 -> 4.7. The right comparison is the excess over the size-matched null, which shrinks 4.85 -> 3.58 -> 1.08. A true key's pmax rises with L (plants below: 13.8-27.5 at L=120 to 36-71 at L=729). Raw pmax also falls (7.07 -> 5.75), failing the PREREG TRUE-KEY-LIKE rule (pmax(729) >= 1.5 x pmax(120)) on either reading. Best over the 57 offset cells at L=729 (LP64 ks2 -1): 6.670 (o=7, argmax OE), inside the null (null max 6.83; P(best of 57 cells) ~ 0.09).

Other relations at o=0 (full table in `verifiers.json: curve_o0c0`): keyskip1 -1: 4.27, 4.97, 5.32, 4.98, 6.06. `free` -1 LP64: 9.70, 9.73, 9.87, 10.70, 13.36, but `free` is an over-fitting relation whose null rises just as fast (null medians 5.16 at L120, 7.47 at L262, 11.24 at L729). The seed's rank in the free null decays with L: 0/300 exceed, then 2% (n=150), then 7% (n=100). ILP32 free -1 gives 15.15 at L=729 against a null max of 14.33 (n=100): one cell of ~460 free cells in the grid (a few such are expected); its excess over the null median is not growing (3.6, 3.0, 3.0, 3.9). Flagged below, not treated as a signal.

## 3. Grid coverage (`cells.json`, 2,383 of 2,972 planned cells; each with 9- and 12-panel pmax and argmax)
Fully covered (both ABIs, 3 relations, both signs, o = 0..28 and c0 = 0..28; the o axis contains key-phase offsets 0..7): L = 120, 240, 262. L=400: LP64 keyskip2 (both signs) and LP64 keyskip1 complete; ILP32 only o=0,c0=0 plus 28 of the 57 ks2 sign -1 cells. L=729: o=0,c0=0 for everything; offset axes only for LP64 keyskip2 sign -1 (added by `extra729`). **Not covered (589 cells, compute cap):** L=400 ILP32 offset axes (except 28 ks2 -1 cells); L=729 offset axes for every cell other than LP64 ks2 -1. `free` at L>262 only at o=0,c0=0 by design. Offset axes were swept one at a time (o with c0=0, c0 with o=0), never as a 29x29 product.
Best raw cell anywhere is a `free` cell (ILP32 free -1 L=729, 15.15). Among the screened relations (keyskip1/2) the best raw cell is the original (LP64 ks2 -1, L=120, 7.068); no offset shift improves on o=0.

## 4. Verifier A - size-matched null (`verifiers.json: A_size_matched_null`)
Random in-orbit bash 4.2 seeds (same 74-prefix draw as R35), identical cell, 9-panel pmax (the 12-panel is nearly identical).

| quantity | value |
|---|---|
| 7.068 vs 2000 LP64 ks2 L=120 nulls | 0/2000 exceed (null max 4.78, q99.9 4.52, median 2.22); empirical quantile 1.000 |
| family-wise P(best of N_actual=69,017 draws >= 7.068), exp-POT tail above q90 | **0.199** (N_declared 1e6: 0.960) |
| POT 99% bar at N_actual / N_declared | 8.24 / 9.25 (bar_v3: 8.06 / 9.03) |
| ILP32 6.762 vs 1000 ILP32 nulls | 0/1000; family-wise P at N_actual = 0.559 |
| L=262, o=0: 6.638 vs 1000 nulls | 0/1000 per draw; family-wise (N_actual) P = 0.76; best of 57 offset cells at L=262: per-cell POT P(best of 57) = 0.0012, conditioned on THIS seed (see below) |
| L=729, o=0: 5.755 vs 400 nulls | 10/400 exceed (2.5%), quantile 0.975, an ordinary draw |
| grid-matched L=120 (keyskip1+2, both signs, o=0..28) vs 30 random seeds | seed's best 7.068 vs null best-of-grid median 4.09, max 5.26; 0/30 at or above |

Reading: 7.068 is unusual for one seed (0/2000) but is exactly what the maximum of ~7e4 decodes looks like: family-wise exceedance 0.20 at actual N (0.56 for ILP32). The L=262 and L=729 numbers are post-selection (the seed was picked as the sweep's max on its first 120 runes, and longer windows contain those runes), so the per-seed quantiles at 262 overstate; the selection-free test is verifier B's held-out windows. Kill condition (observed below the actual-N family-wise bar and no growth -> NOISE): **fired**.

## 5. Verifier B - register consistency (`verifiers.json: B_register_consistency`)
One 729-rune decode cut into six non-overlapping 120-windows (9- and 12-panel identical):

| window | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| pmax | 7.07 | 2.42 | 2.01 | 0.91 | 1.12 | 2.18 |
| argmax | LP1_REAL | EN_KJV | LP1_REAL | LATIN | EN_NOVOWEL | EN_MODERN |

Chained independent decodes (o = previous ptr_end + 1): 7.07 LP1_REAL / 2.55 EN_NOVOWEL / 2.01 LP1_REAL / 1.66 LATIN / 2.38 EN_NOVOWEL / 1.82 EN_NOVOWEL. The argmax wanders over five registers; LP1_REAL holds 2 of 6. Held-out windows 1-5 average pmax 1.73 against a null median of 2.19 (94.5% of null seeds average at least that high): the text after the selected window carries no signal at all, even slightly below null. All the signal is the first window, i.e. the selection. Null baseline: LP1_REAL wins 11.9% of null segments; the candidate's modal-register share 0.33 is below the null mean 0.59. Kill (LP1_REAL in <= 50% of segments, or segments not above null): **fired**.

## 6. Verifier C - the decoded text (`decode_text.md`)
L=120 head: `eaoeeahewasedorowosbymoengngeoellraeaimfwgodyoathonerahmonleahriaoaeeobjtherahmaengntingsuhlburffhdg...` with no words beyond chance fragments ("was", "by", "of the", "ther"). IoC*N 0.99-1.02 (null L=262 central 95%: 0.95-1.10), mds 16-17 (null median 16, q01 13), common-English-word substring hits at L=262: 3 vs null median 1, q99 5 (19.8% of nulls match or beat it). The "th/ng/ea/eo" texture is what a trigram-panel optimiser produces from nothing. It reads as nothing at L=240/262/729 either (word hits 3, 3, 5).
Calibration plants (same seed as key, enc_pair 0.83, held-out English/LP1 text, identical pipeline; `plant.json`): the decode reads as English verbatim ("rysthesonofbryssethachfromthehilloftheblaccfernbrace..."), recovery 0.992-1.000; pmax 13.8 / 20.4 / 27.5 at L=120 rising to 36.3 / 47.7 / 70.8 at L=729, word hits 8 -> 57-82; every plant exceeds the null q99.9 and null max at every L. Kill (no word-level structure): **fired**.

## 7. Positive control
PASSED: 3 planted texts x 5 lengths, all recovered >= 0.99, all above every null quantile, monotone-growing in L, and legible. The pipeline recognises a true key of this construction in this register family at all five lengths. Residual power caveat (R35 conditionals unchanged): plants use English/LP1-style text under keyskip2 at supp 0.83; a key with different skip behaviour, an unpanelled register, or an offset outside those tested is not covered.

## 8. Conditionals (doctrine Q4)
1. Key space: ONE seed x {bash 4.2 LP64, ILP32} `%29`, sign +-1, offsets as in section 3. 2. Transition model: keyskip1/keyskip2/free under beam_v3 panel_max, beam_w 400, lam_u 4. 3. Adjudicator: R32 9-register and R36 12-register trigram panels; nulls are unfiltered random in-orbit seeds (the real sweep's pf_v4 prefilter selects, so its null sits slightly above these; the POT bar 8.24 and bar_v3 8.06 agree within 0.2).

## 9. For the coordinator
- Nothing escalated. The recurring near-miss is the order statistic of the sweep (family-wise P ~ 0.2 at N=69k; it recurs because the sweep and every re-screen are deterministic and it is the same top draw each time).
- `free` relation: its pmax rises with L for every seed (null median 5.2 -> 7.5 -> 11.2); it is not usable as evidence without an L-matched null, and `bars_v3` has `free` at L=120 only. One ILP32 free cell at L=729 (15.15) exceeds the n=100 null max (14.33). Decision for you: buy a larger free null (~2.5 s per L=729 draw) before the ledger says anything about free. It is not the near-miss ABI and its excess does not grow.
- Unrun: the 589 cells above, the offset product grid, a pf_v4-filtered null. None can rescue a seed whose held-out windows score at null level, so they were left.
- Prereg wording error (null L-independence) corrected in section 2; no threshold was moved.
- Compute: ~15 min grid + ~20 min nulls/plants/verifiers at nproc 1; free RAM stayed above 0.4 GB.
