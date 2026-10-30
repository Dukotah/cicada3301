# Round 34 / I1 -- v3 null of record: RESULTS

_2026-10-29. PREREG.md written first. Raw: `null_stream.jsonl` (every null pmax), `control_plants.jsonl`. Derived: `null_cells.json`, `fit.json`, `control.json`. Code: `common34.py`, `run_null.py`, `run_control.py`, `fit.py`, `finalize.py`, `bars_v3.py` (doctest passes). One Python process at a time; nothing outside this directory written. Wall: null 3427 s + control 172 s + fits, about 62 min of the 90-min cap, plus the speed probe and reading._

## 0. Headline
* **Q5 FIRED.** The Gumbel scale beta(L) of v3's panel-pmax null falls as L^-0.10 to L^-0.14 (lp2 family), not Round 32 I3's L^-0.55 +/- 0.04: 8 to 11 combined SE apart. Per the plan: stop and report. A likely reason is that the two exponents are for different statistics (R32 I3 fit the raw legacy `en` score of an exact keyskip1 beam; v3's pmax is a per-length z-normalised max over nine registers, so it need not shrink like raw likelihood), but this lane did not separate that from a non-Gumbel tail. B1 should treat the R32 exponent as NOT transferable and the Gumbel bar as a conservative model rather than an observed quantile.
* **The tail is Gumbel-or-lighter, not heavier.** GPD shape (moments) xi is about -0.12 for the large cells (L31/L120/L240) and about 0 within noise at L=400. The exponential POT bar therefore over-predicts: at N = 40,000 (L=120) it predicts a median max of 6.33 but the observed max is 5.51 (keyskip1) / 5.48 (keyskip2). The Gumbel bar is conservative; a GPD (xi<0) bar, shown for sensitivity only, is far lower (about 5.9 to 6.0 at N=2e5, L=120).
* **B3's bars were not lenient** (s4).
* **Positive control: FAILED by the strict pre-registered rule, cleanly separable.** PASS at all 9 registers for L in {120, 240, 400} x {keyskip1, keyskip2} (20/20, both families). FAIL at L=31 (31-rune windows cannot reach the N=1e6 bar for most registers) and FAIL for `free` at L=120.
* L=400 was NOT fitted-from-three: it has its own sample (960 draws family a, 695 pooled family b). The exponent without L=400 is nearly unchanged (table s3).

## 1. Draws obtained vs targets (shortfall stated)
Targets (>=40,000 per cell family a; >=10,000 per register family b) were met ONLY for family a at L=31 and L=120. Measured wrong-key v3 cost on this shared laptop: L31 189/316 dec/s (adv1/adv2), L120 108/141, L240 20/15, L400 6.3/4.6; the targeted L=400 cell alone would be about 19,000 s, so draws were budgeted to the 90-min cap (PREREG). Both relations are decoded on the same C and K for each draw. Keys: round-robin over B3's six families, seeds from the stored survivor seeds (B3 null recipe), key length max(1024, 6L+64). Family b = held-out `testhalves.npz` EN_NOVOWEL / LATIN / OE / DE text, a random L-subset in random order is the ciphertext, wrong keys; 3000 per register at L31/L120 (not 10,000), 415-500 at L240, 141-200 at L400. `free` at L=120: 1000 draws. Statistic: panel pmax via `adjudicate_batch` (checked equal to `adjudicate` on 3 samples).

## 2. Cell table (draws, max, 99th percentile; POT above the 90th percentile u)
| family | source | L | rel | draws | max | p99 | u90 | beta (+-SE) | mu | xi(GPD) |
|---|---|--:|---|--:|--:|--:|--:|--:|--:|--:|
| lp2 | LP2 | 31 | keyskip1 | 40000 | 5.12 | 3.51 | 2.53 | 0.440 (0.007) | 1.52 | -0.14 |
| lp2 | LP2 | 31 | keyskip2 | 40000 | 5.72 | 3.53 | 2.55 | 0.432 (0.007) | 1.55 | -0.09 |
| lp2 | LP2 | 120 | free | 1000 | 9.91 | 8.06 | 6.65 | 0.669 (0.067) | 5.11 | -0.11 |
| lp2 | LP2 | 120 | keyskip1 | 40000 | 5.51 | 3.95 | 3.12 | 0.371 (0.006) | 2.27 | -0.12 |
| lp2 | LP2 | 120 | keyskip2 | 40000 | 5.48 | 4.00 | 3.15 | 0.377 (0.006) | 2.29 | -0.12 |
| lp2 | LP2 | 240 | keyskip1 | 4679 | 5.56 | 4.67 | 3.83 | 0.360 (0.017) | 3.01 | -0.13 |
| lp2 | LP2 | 240 | keyskip2 | 4679 | 5.49 | 4.49 | 3.80 | 0.330 (0.015) | 3.04 | -0.13 |
| lp2 | LP2 | 400 | keyskip1 | 960 | 6.07 | 5.18 | 4.42 | 0.333 (0.034) | 3.66 | -0.03 |
| lp2 | LP2 | 400 | keyskip2 | 960 | 5.82 | 5.21 | 4.48 | 0.307 (0.031) | 3.78 | -0.05 |
| register | DE | 31 | keyskip1 | 3000 | 4.31 | 3.39 | 2.50 | 0.408 (0.024) | 1.56 | -0.13 |
| register | DE | 31 | keyskip2 | 3000 | 5.51 | 3.37 | 2.53 | 0.405 (0.023) | 1.60 | -0.06 |
| register | DE | 120 | keyskip1 | 3000 | 5.14 | 3.92 | 3.12 | 0.359 (0.021) | 2.29 | -0.10 |
| register | DE | 120 | keyskip2 | 3000 | 5.57 | 3.95 | 3.14 | 0.373 (0.022) | 2.28 | -0.05 |
| register | DE | 240 | keyskip1 | 415 | 4.74 | 4.40 | 3.75 | 0.345 (0.053) | 2.96 | -0.45 |
| register | DE | 240 | keyskip2 | 415 | 5.15 | 4.56 | 3.82 | 0.296 (0.046) | 3.15 | 0.00 |
| register | DE | 400 | keyskip1 | 200 | 6.59 | 5.21 | 4.31 | 0.447 (0.100) | 3.28 | 0.14 |
| register | DE | 400 | keyskip2 | 200 | 6.05 | 5.21 | 4.50 | 0.402 (0.090) | 3.58 | -0.18 |
| register | EN_NOVOWEL | 31 | keyskip1 | 3000 | 4.62 | 3.48 | 2.56 | 0.409 (0.024) | 1.61 | -0.13 |
| register | EN_NOVOWEL | 31 | keyskip2 | 3000 | 4.94 | 3.59 | 2.61 | 0.421 (0.024) | 1.64 | -0.01 |
| register | EN_NOVOWEL | 120 | keyskip1 | 3000 | 4.79 | 3.95 | 3.20 | 0.331 (0.019) | 2.44 | -0.22 |
| register | EN_NOVOWEL | 120 | keyskip2 | 3000 | 5.19 | 3.90 | 3.12 | 0.360 (0.021) | 2.29 | -0.09 |
| register | EN_NOVOWEL | 240 | keyskip1 | 500 | 5.59 | 4.63 | 3.81 | 0.390 (0.055) | 2.91 | -0.11 |
| register | EN_NOVOWEL | 240 | keyskip2 | 500 | 4.93 | 4.52 | 3.86 | 0.290 (0.041) | 3.19 | -0.03 |
| register | EN_NOVOWEL | 400 | keyskip1 | 141 | 5.56 | 5.35 | 4.50 | 0.346 (0.093) | 3.70 | 0.00 |
| register | EN_NOVOWEL | 400 | keyskip2 | 141 | 5.14 | 4.87 | 4.46 | 0.259 (0.069) | 3.86 | -0.75 |
| register | LATIN | 31 | keyskip1 | 3000 | 4.90 | 3.48 | 2.55 | 0.457 (0.026) | 1.50 | -0.23 |
| register | LATIN | 31 | keyskip2 | 3000 | 4.92 | 3.52 | 2.55 | 0.457 (0.026) | 1.49 | -0.24 |
| register | LATIN | 120 | keyskip1 | 3000 | 5.18 | 3.94 | 3.08 | 0.384 (0.022) | 2.20 | -0.05 |
| register | LATIN | 120 | keyskip2 | 3000 | 5.17 | 4.05 | 3.14 | 0.383 (0.022) | 2.26 | -0.06 |
| register | LATIN | 240 | keyskip1 | 440 | 4.95 | 4.58 | 3.81 | 0.355 (0.054) | 2.98 | -0.27 |
| register | LATIN | 240 | keyskip2 | 440 | 5.10 | 4.60 | 3.80 | 0.398 (0.060) | 2.88 | -0.25 |
| register | LATIN | 400 | keyskip1 | 154 | 6.28 | 5.38 | 4.39 | 0.473 (0.118) | 3.32 | 0.07 |
| register | LATIN | 400 | keyskip2 | 154 | 5.12 | 4.92 | 4.30 | 0.266 (0.067) | 3.70 | -0.11 |
| register | OE | 31 | keyskip1 | 3000 | 4.72 | 3.52 | 2.57 | 0.444 (0.026) | 1.54 | -0.20 |
| register | OE | 31 | keyskip2 | 3000 | 4.73 | 3.53 | 2.56 | 0.440 (0.025) | 1.55 | -0.11 |
| register | OE | 120 | keyskip1 | 3000 | 4.99 | 3.99 | 3.11 | 0.407 (0.023) | 2.17 | -0.19 |
| register | OE | 120 | keyskip2 | 3000 | 5.16 | 4.01 | 3.15 | 0.375 (0.022) | 2.28 | -0.07 |
| register | OE | 240 | keyskip1 | 449 | 4.78 | 4.41 | 3.74 | 0.310 (0.046) | 3.03 | -0.18 |
| register | OE | 240 | keyskip2 | 449 | 5.08 | 4.45 | 3.74 | 0.356 (0.053) | 2.92 | -0.24 |
| register | OE | 400 | keyskip1 | 200 | 6.04 | 5.32 | 4.54 | 0.435 (0.097) | 3.54 | -0.15 |
| register | OE | 400 | keyskip2 | 200 | 5.83 | 5.28 | 4.45 | 0.392 (0.088) | 3.55 | 0.00 |

(`xi(GPD)` is noisy in the small cells; k = 10% of the draws.)

## 3. Fit and exponent (ln beta ~ ln L, 4 points, 2 DOF; "lp2" = family a, "register" = family b pooled over the 4 registers)
| series | exponent | OLS SE | w/o L=400 | WLS | diff vs -0.55 | n SE (combined) |
|---|--:|--:|--:|--:|--:|--:|
| lp2 / keyskip1 | -0.105 | 0.012 | -0.103 | -0.119 | 0.445 | 10.7 |
| lp2 / keyskip2 | -0.136 | 0.014 | -0.128 | -0.112 | 0.414 | 9.8 |
| register / keyskip1 | -0.036 | 0.047 | -0.091 | -0.085 | 0.514 | 8.3 |
| register / keyskip2 | -0.118 | 0.016 | -0.132 | -0.115 | 0.432 | 10.0 |

beta nodes, lp2 keyskip1: L31 0.440, L120 0.371, L240 0.360, L400 0.333; keyskip2: 0.432, 0.377, 0.330, 0.307. The register-pooled keyskip1 series is non-monotone at L=400 (0.409 from only 695 draws), hence its large SE. `free` L=120: beta 0.669 (+-0.067), mu 5.115 (one L, no exponent). mu(L) rises with L (lp2 keyskip1: 1.52, 2.27, 3.01, 3.66) while beta barely falls, so the bar RISES with L.

## 4. Bar table (alpha = 0.01, Gumbel POT, `bars_v3.bar_v3`)
| family | rel | L | N=1e5 | N=2e5 | N=1e6 | N=1e9 |
|---|---|--:|--:|--:|--:|--:|
| lp2 | keyskip1 | L31 | 8.57 | 8.88 | 9.58 | 12.6 |
| lp2 | keyskip1 | L120 | 8.36 | 8.62 | 9.24 | 11.86 |
| lp2 | keyskip1 | L240 | 8.7 | 8.95 | 9.51 | 11.95 |
| lp2 | keyskip1 | L400 | 9.04 | 9.27 | 9.81 | 12.11 |
| lp2 | keyskip2 | L31 | 8.6 | 8.91 | 9.61 | 12.64 |
| lp2 | keyskip2 | L120 | 8.19 | 8.45 | 9.03 | 11.55 |
| lp2 | keyskip2 | L240 | 8.38 | 8.61 | 9.15 | 11.44 |
| lp2 | keyskip2 | L400 | 8.77 | 8.98 | 9.48 | 11.62 |
| register | keyskip1 | L31 | 8.24 | 8.52 | 9.19 | 12.03 |
| register | keyskip1 | L120 | 8.55 | 8.82 | 9.46 | 12.17 |
| register | keyskip1 | L240 | 9.06 | 9.33 | 9.94 | 12.59 |
| register | keyskip1 | L400 | 9.66 | 9.92 | 10.53 | 13.12 |
| register | keyskip2 | L31 | 8.51 | 8.81 | 9.51 | 12.48 |
| register | keyskip2 | L120 | 8.21 | 8.46 | 9.05 | 11.59 |
| register | keyskip2 | L240 | 8.49 | 8.73 | 9.27 | 11.61 |
| register | keyskip2 | L400 | 8.86 | 9.08 | 9.59 | 11.79 |
| free | free | L120 | 15.89 | 16.36 | 17.43 | 22.05 |

GPD (xi<0) sensitivity is in `control.json: gpd_sensitivity_table` (L=120 keyskip1, N=2e5: 5.9); NOT bars of record.

**B3 comparison (N = 2e5, L = 120).** This lane's Gumbel bar: keyskip1 8.62 (raw per-cell beta: 8.50), keyskip2 8.45 (raw: 8.62), against B3's modelled 8.546 / 8.373. B3 is within about +/-0.1 (keyskip2 roughly 0.1 to 0.25 lower, i.e. marginally lenient against this lane's Gumbel fit; keyskip1 about equal), so not materially lenient under the same model. Against the observed data both are conservative by roughly 2.5: not one of 40,000 L=120 null draws exceeded 5.51. B3's survivor result (best 7.07, not a null) is unchanged.

## 5. Positive control (planted correct key, SHA-256-CTR, supp 0.83, 20 seeds x 9 registers, window Random(9000+s), bar at N=1e6, alpha 0.01)
Matched relations (keyskip1 with advance 1; skip_by_two enciphering with advance 2; free_q05 with free). L=120/240/400 keyskip1+keyskip2: 20/20 in all 9 registers, families lp2 and register; median pmax >= 13.8 against bars 9.0 to 10.5. L=31: 0/20 for CY, OE, EN_HALFVOWEL, EN_NOVOWEL; 2/20 LATIN; 12-14/20 EN_MODERN, EN_KJV, DE; 20/20 LP1_REAL. free L=120: bar 17.43 (N=1e6); clears 20/20 for LP1_REAL and DE only (EN_KJV 19, EN_MODERN 17, LATIN 13, EN_NOVOWEL 4, OE/CY/EN_HALFVOWEL 0). The free bar rests on 1000 draws and is the least certain number here. Per-cell counts in `control.json`.

## 6. not_covered
* Empirical quantiles beyond n_draws: bars at N=1e5..1e9 are model extrapolation, and Q5 says the model's L-exponent is not corroborated.
* Family b at 10,000 per register; family a at 40,000 for L=240/400; `free` at L != 120 and with more than 1000 draws.
* A null with real (non-shuffled) LP2 structure; decoders other than panel_max hard-max lam_u=4 beam_w=400; relations other than keyskip1/keyskip2/free; keystreams other than the six B1/B2 families (null) and SHA-CTR (plants).
* L between nodes is interpolated in ln L; flat outside 31..400.
* The cause of the exponent mismatch (different statistic vs non-Gumbel tail) is not separated.

## 7. Coordinator decisions
1. Q5 fired. Accept the Gumbel bars as conservative bars of record for B1 (above every observed null value; lenient only if the true tail were heavier than exponential, which xi<0 argues against), or require an empirical-quantile bar (not available at B1's N without about 1e5 to 1e6 more null draws at L=240/400)?
2. L=31 and `free` have a failed control: B1 should use L >= 120 with keyskip1/keyskip2 and not claim L=31 or free reach.
3. If more null is wanted, spend it on lp2 L=240/400 (4,679 and 960 draws) and `free` (1000).

---

## X1/R34 addendum (2026-10-29) -- appended by the red-team lane; text above unchanged

* **Q5 comparator.** The -0.55 +/- 0.04 exponent is for R32 I3's raw legacy EN quadgram score (`round32/I3-r3-enforcement/RESULTS.md:71`); this lane's `pmax` is a per-length z-score (`round32/I2-multiregister-readjudication/adjudicate.py:111`, sd ~ n^-1/2), which adds about +0.5 to the exponent: like-for-like prediction ~ -0.05, observed -0.105 +/- 0.012 / -0.136 +/- 0.014 (1.4 / 2.1 combined SE). Q5 "fired" on a mis-specified comparator; it is not evidence of a non-Gumbel tail.
* **"Gumbel conservative"** holds at L = 31-240 (observed max below the predicted median in 13 of 16 cells; X1 `rerun_i1_gumbel_conservative.json`); at L = 400 (n = 960 / 695) the observed max meets or exceeds the predicted median in 3 of 4 cells, so conservatism is not demonstrated there.
* **B3 comparison.** At N = 202,142, L = 120, B3's 8.546 / 8.373 are 0.08 / 0.08 (lp2) and 0.28 / 0.09 (register) below this lane's bars: marginally lenient, not material (B3's best row 7.068). Bars re-derived from `fit.json`: N = 1e6, L = 120 = 9.235 / 9.034 (lp2), 9.456 / 9.053 (register); `bars_v3.py` returns them.

## Addendum 2026-10-30 (Round 37 I1): `free` nulls at L = 240 / 400 / 729 under panel-R36
`bar_v3(N, L, "free")` now returns fitted bars at L in {240, 400, 729} (and `panel="r36"` gives a 12-register L=120 node); the default L=120 call is unchanged (R34, 9-register).
The new nodes are 12-register (panel-R36) numbers from 1335 / 726 / 562 shuffled-LP2 wrong-key draws (below the 2,000 target at L=400/729), N=1e6 bars 20.6 / 21.7 / 24.9.
The `free` planted control FAILS at L=240 for OE (3/20) and EN_HALFVOWEL (7/20). See `analysis/round37/I1-free-null/RESULTS.md`. `method="gpd"` for `free` is now restricted to L=120 (it previously silently used the L=120 node).
