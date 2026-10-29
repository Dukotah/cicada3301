# Round 33 / I1 -- register-aware beam (`beam_decode_v3`): RESULTS

_2026-10-29. Pre-registered in `PREREG.md` (written before any output file existed). Raw: `power_envelope.json`,
`speed.json`, `out_*.json`, `table.json`, `analysis_out.txt`. This is a measurement of an instrument with the correct
key handed over; it says nothing about any key._

## 0. Headline

* **Design 1 (panel-max search score: hard max over the nine I2 register trigram LMs) won.** Designs 2 and 3 were not
  needed for the gate; they were measured as a supplement only (s5).
* **Q5 kill rule did NOT fire.** Checkpoint (80 decodes, L=120, EN_MODERN + EN_NOVOWEL, keyskip1/1 + skip_by_two/2):
  EN_NOVOWEL skip_by_two/advance 2 median recovery **1.000**; driftbeam on the same plants **0.721** (reproduces Round 32
  I1's 0.721 failure). Design-1 cost 1.4-2.3x driftbeam wall time per decode (< 3x).
* **VALID per PREREG s4:** V1 EN_NOVOWEL L=120 skip_by_two/2 = **1.000** (>= 0.90). V2: **0 violations** over
  9 registers x 3 relations x 2 L = 54 cells (no v3 median below same-plant driftbeam - 0.05, none below a Round 32 I1 published
  median - 0.05). Worst v3-minus-driftbeam delta: EN_MODERN free L=120, 0.967 vs 0.979 (-0.012).
* **Price, stated:** the wrong-key (shuffle-null) `pmax` distribution rises because the search now optimizes the statistic the
  adjudicator reads (s3). Plants stay above it (20/20 seeds over the v3 null max in every cell), but the hitfn20 panel-max
  bars, fitted on driftbeam decodes, are not valid for v3 and the null needs a refit before B3 uses it at sweep scale.

## 1. Setup (as pre-registered)
Correct key + offset 0 handed over (power test); key SHA-256-CTR mod 29; enciphers keyskip1 / skip_by_two / free_q05
(supp 0.83, seed 3301+s); L = 120, 400; 20 plants per cell (s = 0..19); window start Random(9000+s). Plant text = I2
`testhalves.npz` held-out halves for all nine registers. **Matched relations only** (keyskip1 with advance 1, skip_by_two
with advance 2, free_q05 with free); cross-relation cells were NOT re-measured. beam_w 400. v3 parameters: tau = hard max
(tuning tie with tau=5, rule picks hard max), lam_u = 4 for free (tuning seeds 500-509, lam 2/4/8: NOVOWEL mean 0.977/0.979/0.932,
MODERN 0.959/0.972/0.936). Adjudicator = `round32/I2 adjudicate`, nine-register panel.
**Declared deviation:** R32 I1's EN_MODERN / EN_HALFVOWEL / EN_NOVOWEL plants came from its 7-register lite test halves; I used the
I2 halves (the lite EN halves may lie inside the I2 training text), so the binding baseline is driftbeam re-run on identical plants
("driftbeam" column). R32 I1 published medians are shown where a cell exists. Where the plants differ the numbers differ
(R32 NOVOWEL keyskip1 / free 0.946 / 0.567 vs same-plant 0.783 / 0.275); the skip_by_two 0.721 agreement is a median coincidence.

## 2. Envelope -- median rune-index recovery (v3 in bold; v3 mean, min in brackets)
Columns per L: driftbeam on identical plants / Round 32 I1 published / v3.

| register | relation | L=120: driftbeam / R32 I1 pub. / **v3** (mean, min) | L=400: driftbeam / R32 I1 pub. / **v3** (mean, min) |
|---|---|---|---|
| EN_MODERN | keyskip1 | 1.000 / 1.000 / **1.000** (1.000, 0.992) | 1.000 / 1.000 / **1.000** (1.000, 0.995) |
| EN_MODERN | skip_by_two | 1.000 / 1.000 / **1.000** (0.998, 0.958) | 1.000 / 1.000 / **1.000** (0.999, 0.988) |
| EN_MODERN | free_q05 | 0.979 / 0.992 / **0.967** (0.969, 0.875) | 0.975 / 0.982 / **0.974** (0.971, 0.900) |
| EN_KJV | keyskip1 | 1.000 / -- / **1.000** (1.000, 1.000) | 1.000 / -- / **1.000** (1.000, 0.993) |
| EN_KJV | skip_by_two | 1.000 / -- / **1.000** (1.000, 1.000) | 1.000 / -- / **1.000** (0.999, 0.993) |
| EN_KJV | free_q05 | 0.992 / -- / **0.988** (0.979, 0.942) | 0.985 / -- / **0.985** (0.982, 0.958) |
| LP1_REAL | keyskip1 | 1.000 / -- / **1.000** (1.000, 1.000) | 1.000 / -- / **1.000** (1.000, 1.000) |
| LP1_REAL | skip_by_two | 1.000 / -- / **1.000** (1.000, 1.000) | 1.000 / -- / **1.000** (1.000, 0.998) |
| LP1_REAL | free_q05 | 0.983 / -- / **1.000** (0.999, 0.992) | 0.976 / -- / **0.998** (0.997, 0.988) |
| LATIN | keyskip1 | 1.000 / 1.000 / **1.000** (0.998, 0.958) | 1.000 / 1.000 / **1.000** (0.999, 0.988) |
| LATIN | skip_by_two | 1.000 / 1.000 / **1.000** (1.000, 0.992) | 1.000 / 0.998 / **1.000** (0.998, 0.980) |
| LATIN | free_q05 | 0.950 / 0.950 / **0.988** (0.982, 0.892) | 0.941 / 0.930 / **0.989** (0.982, 0.943) |
| OE | keyskip1 | 1.000 / 1.000 / **1.000** (0.998, 0.958) | 1.000 / 0.995 / **1.000** (0.998, 0.988) |
| OE | skip_by_two | 1.000 / 1.000 / **1.000** (0.999, 0.983) | 1.000 / 0.996 / **1.000** (0.999, 0.993) |
| OE | free_q05 | 0.954 / 0.954 / **0.967** (0.953, 0.783) | 0.909 / 0.933 / **0.961** (0.943, 0.698) |
| DE | keyskip1 | 1.000 / 1.000 / **1.000** (1.000, 1.000) | 1.000 / 1.000 / **1.000** (0.999, 0.990) |
| DE | skip_by_two | 1.000 / 1.000 / **1.000** (1.000, 1.000) | 1.000 / 1.000 / **1.000** (1.000, 0.995) |
| DE | free_q05 | 0.958 / 0.958 / **0.992** (0.984, 0.942) | 0.950 / 0.945 / **0.986** (0.983, 0.902) |
| CY | keyskip1 | 1.000 / -- / **1.000** (1.000, 1.000) | 0.993 / -- / **1.000** (1.000, 0.993) |
| CY | skip_by_two | 1.000 / -- / **1.000** (1.000, 1.000) | 0.999 / -- / **1.000** (1.000, 0.990) |
| CY | free_q05 | 0.875 / -- / **0.988** (0.981, 0.942) | 0.892 / -- / **0.971** (0.952, 0.757) |
| EN_HALFVOWEL | keyskip1 | 1.000 / -- / **1.000** (0.993, 0.892) | 1.000 / -- / **1.000** (0.997, 0.980) |
| EN_HALFVOWEL | skip_by_two | 1.000 / -- / **1.000** (1.000, 1.000) | 1.000 / -- / **1.000** (0.996, 0.932) |
| EN_HALFVOWEL | free_q05 | 0.954 / -- / **0.975** (0.967, 0.908) | 0.904 / -- / **0.942** (0.938, 0.873) |
| EN_NOVOWEL | keyskip1 | 0.783 / 0.946 / **1.000** (0.998, 0.975) | 0.734 / 0.867 / **1.000** (0.999, 0.993) |
| EN_NOVOWEL | skip_by_two | 0.721 / 0.721 / **1.000** (1.000, 0.992) | 0.655 / 0.705 / **1.000** (1.000, 1.000) |
| EN_NOVOWEL | free_q05 | 0.275 / 0.567 / **0.979** (0.978, 0.950) | 0.237 / 0.416 / **0.981** (0.981, 0.963) |

R32 RECOVERED rule (median >= 0.85 AND >= 80 % of seeds with `pmax` over the same decoder's own null max): v3 passes **54/54**
cells; driftbeam passes 48/54, the six failures being exactly EN_NOVOWEL x 3 relations x 2 L. v3's weakest cells are free-relation
at L=400: OE 0.961 (min 0.698), CY 0.971 (min 0.757), EN_HALFVOWEL 0.942; each is still >= its same-plant driftbeam median.

## 3. Null and bars (which binds)
Shuffle null, 100 decodes per (decoder, relation, L), the R32 I1 null ciphertexts, panel-adjudicated. Max `pmax`, driftbeam -> v3:
advance 1: L120 4.05 -> 4.08, L400 4.45 -> 6.33; advance 2: L120 4.17 -> 4.32, L400 4.83 -> 5.36; free: L120 6.20 -> 7.62,
L400 8.60 -> **13.03**. v3 max legacy `en`: -6.69 / -6.86 / -6.34 (L120), -7.14 / -7.12 / -6.81 (L400).
* `threshold_for(N, segment_len=L)`: **-5.5** for N = 100 and 1e6 at both L (the floor binds). No v3 null `en` clears it, but the
  `en` bar is **blind to the repaired register**: planted EN_NOVOWEL decodes have median `en` about -7.9, so it can never flag them.
* hitfn20 `panelmax_bar` (advance 1 -> preset exact, 2 -> pair, free -> drift; the L=120 cell, applied to L=400 too): N=100:
  4.995 / 4.901 / 9.870; N=1e6: 7.634 / 7.384 / 13.842. Fitted on driftbeam wrong-key decodes, so **not applicable to v3**: v3's own
  free/L=400 null max (13.03 at only N=100) is already near the driftbeam N=1e6 bar. Planted `pmax` still clears the N=1e6 bars in
  100 % of EN_MODERN and EN_NOVOWEL seeds in every matched cell.
* **Binding bar of record: v3's own shuffle-null max `pmax`**; for any sweep at N >> 100 a Gumbel refit of v3 wrong-key `pmax`
  (round19/I3 style) is required first. That refit is NOT done in this lane.

## 4. Speed (`speed.json`; mean of 4 decodes, EN_MODERN plants, one process, noisy laptop)
panel_max / driftbeam wall-time ratio 1.4-2.3x. panel_max decodes/s: L120 adv1 73, adv2 121, free 3.7; L400 adv1 4.0, adv2 3.4, free 1.1.
register_cond: 8.6-11x (0.2-19 decodes/s). agnostic: 1.4-3.1x. B3's budget should use the panel_max numbers.

## 5. Designs 2 and 3 (supplementary, L=120, 20 plants, not used for the gate)
register_cond: NOVOWEL 1.000 / 1.000 / 0.979 (keyskip1 / skip_by_two / free), MODERN 1.000 / 1.000 / 0.967 -- same recovery as design 1
at about 9-11x the cost. agnostic (no language model; adaptive order-0/1 code length): NOVOWEL 1.000 / 1.000 / 0.950, but MODERN free
0.896 (mean 0.78) -- a drop of > 0.05 from driftbeam's 0.979 that would fail V2 on its own grid. So a language-free search score
also repairs NOVOWEL, which locates the old defect in the English-quadgram bias of the search, not in a missing NOVOWEL model.
Neither design was run on the full grid (no gate need).

## 6. Positive control and caveats
Control passed: EN_MODERN matched cells 1.000 at both L; the driftbeam baseline reproduces the NOVOWEL failure on the same plants.
**Circularity (Q4):** the search LMs are the adjudicator's LMs, and plants come from the held-out halves of the corpora those LMs were
trained on (same register, different text). v3's higher null `pmax` is the same effect. Design 3's NOVOWEL recovery with no LM is the
evidence that the NOVOWEL gain is not an artifact of it.

## 7. The three conditionals (Q4)
1. **Key space:** none opened; correct key handed over (power test). No claim about any LP2 key.
2. **Transition model:** keyskip1 / keyskip2 / permissive (max_skip 8/8/40, max_free 0/0/2, start_slack 0/0/2), beam_w 400. Not
   represented: resets, advance >= 3, interrupters, rewrite/keyside/plainside constructions, > 2 unexplained advances per rune.
3. **Adjudicator register:** the nine-register trigram panel (EN_MODERN EN_KJV LP1_REAL LATIN OE DE CY EN_HALFVOWEL EN_NOVOWEL). Anything
   outside it (Greek, Hebrew, Norse, mixed or unknown-register text) is not covered; design 3 hints at but did not measure that coverage.

## 8. not_covered
Cross-relation (mismatched decoder) cells for all nine registers; L = 6000; any plant other than correct key + offset 0; sign +1; a null
on the real shuffled LP2 stream (R32 I1's planted-shuffle null reused for cell-for-cell comparability); a v3 wrong-key Gumbel refit at
large N; designs 2 and 3 on the full 9x3x2 grid; supp values other than 0.83; non-SHA-256-CTR keystreams (a low-entropy pad may change
speed); real, non-planted text (all plants are clean corpus windows).

## 9. Coordinator decisions
1. Adopt panel_max (hard max, lam_u = 4) as the decoder for B3? Condition: B3 uses a v3-specific null (refit), not the hitfn20 driftbeam bars.
2. Commission the v3 null refit (free relation costs 1-4 decodes/s, so large N is hours)?
3. Whether the free-relation L=400 OE / CY / HALFVOWEL per-seed minima (0.70-0.76) are acceptable.

## 10. Files
`PREREG.md`, `beam_v3.py`, `run_envelope.py`, `supp.py`, `analyze.py`, `build_deliverables.py`, `power_envelope.json`, `speed.json`,
`table.json`, `envelope_table.md`, `analysis_out.txt`, `out_ckpt.json`, `out_tune.json`, `out_grid_base.json`, `out_grid_panel_max.json`,
`out_null_base.json`, `out_null_panel_max.json`, `out_supp_designs23.json`, `speed_raw.json`, `chain1.sh`, `chain1.log`, `ledger.json`.
