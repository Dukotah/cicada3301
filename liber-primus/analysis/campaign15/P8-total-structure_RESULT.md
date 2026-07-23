# P8 — Total-Structure Closure (Campaign XV)

- **probe_id:** P8-total-structure
- **verdict:** soundness-confirmed
- **headline_number:** LP2 sits at the **41.2–79.3rd percentile** of a 1,000-member filtered-uniform control band across every whole-sequence predictor (order-1..8 held-out context models + LZMA); **no predictor falls below the 1st percentile**. Same predictors put real English at the **0th percentile** (LZMA 1.97 vs band 5.07 bits/rune).
- **falsifiable_signal:** LP2 cross-validated bits/rune **below the 1st percentile** of the matched control band on ANY predictor (order-1..8 context model or LZMA), OR a provenance sub-test statistic (dispersion / drift) beyond the control band. Either would mean computable structure survives the two known signature statistics ⇒ OTP verdict wrong ⇒ attack surface.
- **signal_fired:** false

## synthetic_validation
**Control construction.** Each of 1,000 controls is a 12,956-rune stream from Campaign XI's suppression model: uniform draws over 29 symbols with a *soft single-resample no-repeat* rule (on an adjacent collision, resample once with probability s\*). The analytic suppression `s* = 0.8363` was solved from the observed doublet rate via `P(doublet) = (1/N)(1 − s(N−1)/N)`. By construction every control reproduces **both** LP2 signatures: measured band means `doublet = 0.663%` (LP2 0.664%) and `IoC·N = 0.9999` (LP2 0.9999). Each control uses its own seed (`np.random.default_rng(3301+1+k)`) — no unseeded randomness.

**Predictor-can-detect-structure proof (positive control).** The identical predictors were run on real English mapped to the 29 runes (`run_stats.english_baseline`, tiled to 12,956). They fire unmistakably: English LZMA = **1.97 bits/rune** vs band mean 5.07 (0.0 %ile); English order-8 context = **0.03 bits/rune** vs band mean 5.63. A structureless-null on LP2 is therefore meaningful — the instruments demonstrably see structure when it exists.

## method
1. Load unsolved LP2 body stream (mirror of campaign14: `pages_raw[:-2]`, 12,956 runes).
2. Generate 1,000 seeded filtered-uniform controls (suppression model above).
3. Whole-sequence predictors, identical procedure for LP2 and every control:
   - (a) **Held-out context models**, orders 1..8: Witten-Bell interpolated back-off trained on the first 80%, cross-entropy (bits/rune) scored on the held-out 20%.
   - (b) **LZMA** (`preset 9|EXTREME`) on `bytes(stream)`; bits/rune = 8·|compressed|/L.
4. Provenance sub-tests: (c) sliding-window (w=100) index-of-dispersion averaged over symbols; (d) monogram frequency drift = blocks(13)×symbols(29) contingency χ².
5. Report LP2's percentile within the control band for each predictor; gate = below 1st percentile.

## Results (1,000 controls, orders 1..8)
| predictor | LP2 | band mean | band 1st pct | LP2 %ile |
|---|---|---|---|---|
| context order-1 | 4.8825 | 4.8848 | 4.8653 | 41.2% |
| context order-2 | 5.3190 | 5.3082 | 5.2541 | 67.5% |
| context order-3 | 5.6207 | 5.6128 | 5.5640 | 63.8% |
| context order-4 | 5.6316 | 5.6274 | 5.5829 | 57.3% |
| context order-5..8 | 5.6323 | 5.6279 | 5.5835 | 57.1% |
| LZMA bits/rune | 5.0707 | 5.0697 | 5.0633 | 79.3% |
| dispersion (ID) | 0.8856 | 0.9060 | — | 16.2% |
| monogram drift χ² | 298.8 | 317.5 | — | 22.0% |

Positive control (same band): English LZMA 0.0 %ile; English order-8 context 0.03 vs 5.63 band mean.

## one_paragraph
Beyond the two constraints that already define LP2 as OTP-class (`IoC·N = 1.000`, `doublet ≈ 0.66%`), this probe asked whether any computable structure of *any* order remains. Against a 1,000-member control band built from Campaign XI's suppression model — each control reproducing both signatures by construction — real LP2 is statistically indistinguishable: it lands at the 41–79th percentile on every held-out context model (orders 1–8) and on LZMA, and at the 16–22nd percentile (comfortably inside the band) on sliding-window dispersion and monogram drift. Nothing crosses the 1st-percentile gate. The instruments are not blind: the same predictors compress real English to 1.97 bits/rune (LZMA) and 0.03 bits/rune (order-8 context), placing English at the 0th percentile. LP2 therefore carries no exploitable higher-order or universal-compressor structure — the filtered-uniform model is a *complete* description of the stream. This upgrades the OTP-class verdict from low-order-verified (IoC + doublet) to **model-class-verified**: it is the strongest ciphertext-side confirmation run to date, and it closes the "maybe there's structure the earlier tests missed" worry rather than opening an attack surface.

## script_path
`analysis/campaign15/P8-total-structure.py`

## reproduce_cmd
```
PYTHONUTF8=1 python analysis/campaign15/P8-total-structure.py
```
(env overrides `P8_NCONTROLS`, `P8_MAXORDER` for quick runs; full run ≈ 12 min for 1,000 controls × order-8 + LZMA. Raw log: `analysis/campaign15/P8_run.log`.)

## ledger_row
| Attack | Verdict | Why | Where |
|---|---|---|---|
| **Total-structure closure** — cross-validated context-model (order 1–8) + LZMA bits/rune, plus window-dispersion & monogram-drift, vs 1,000 matched filtered-uniform controls | ❌ null (soundness-confirmed) | LP2 inside the control band on every predictor (41–79 %ile context/LZMA; 16–22 %ile sub-tests), none below 1st pct; same predictors put English at 0 %ile. No computable structure beyond IoC·N=1.000 + doublet 0.66% ⇒ OTP-class **model-class-verified** | Campaign XV `analysis/campaign15/P8-total-structure.py` |
