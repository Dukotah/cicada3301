# Round 41 / I1 -- the refit: a bar fitted on the population it is applied to -- RESULTS

_2026-10-31. `PREREG.md` was written first. No `git` run. One Python process at a time; RAM check before each heavy stage. No discovery claim. Everything below is conditional on (the six-family wrong-key survivor population) x (keyskip1 / keyskip2 under beam_v3 `panel_max`, after `pf_v4_12` at its frozen point) x (panel-R36, 12 registers, L=120 and L=240). Paths relative to `liber-primus/analysis/round41/I1-null-refit/` unless stated._

## 0. Headline

1. **The refit works as a recognizer of the sweeps' own population.** Wrong-key survivors of `pf_v4_12` on the REAL LP2 head, drawn from six generator families, have median pmax **2.809 / 2.828** (keyskip1 / keyskip2) and q99 **4.763 / 4.778**; the real sweeps' 307,377 survivor rows (R37-I2 + R40-B1 + R40-B3) have **2.796 / 2.815** and **4.761 / 4.776**. The old `null12` cells (no prefilter) had 2.334 / 2.339 and 4.06 / 4.04. The Round 40 X1 finding is confirmed and located: the missing prefilter, not the generator, is the whole difference (per-family medians are 2.80-2.84 in every family).
2. **Bars of record (L=120):** N=131,786 **9.6325 / 9.6549**; N=1e5 **9.5192 / 9.5417**; N=1e6 **10.4645 / 10.4856**; N=1e9 **13.3004 / 13.3173** (keyskip1 / keyskip2). At L=240 (N=1e6) **10.0529 / 10.3539**. `null12` gave 8.365 / 8.275 (N=131,786) and 9.102 / 8.999 (N=1e6): the stored bars were low by **1.3 at the sweeps' N and 1.4-1.5 at N=1e6**.
3. **No Round 36-40 best row crosses** the bar of record, at its actual N or at N=1e6: 34 rows, 0 cross, smallest gap 0.91 (the withdrawn KDF flag: 6.528 vs 7.435 at N=591). Nothing goes to L=240 or to the oracle bundle.
4. **Two pre-registered gates were met only partly, stated plainly:** (a) Q1a strict (refit Gumbel bar at N=131,786 >= the pooled real-sweep POT bar) holds for keyskip2 (9.6549 vs 9.6125) and fails for keyskip1 by 0.047 (9.5852 vs 9.6325; SEs 0.077 and 0.030, i.e. 0.6 SE); (b) Q1b strict (>=19/20 in every register x relation cell) fails in two cells (LATIN keyskip1 and OE keyskip2, 18/20) -- every loss is a `pf_v4_12` screen miss, and all 470 plants that passed the screen cleared the bar of record at both lengths. Consequences: the bar of record is the HIGHER of the Gumbel refit and the pooled real-sweep POT line (so Q1a holds by construction), and the control failure is recorded as `failed` in the ledger row.
5. **Q5 fired -- in the conservative direction.** The Gumbel (exponential-tail) fit sits ABOVE the data: see section 4. It is kept (higher) as the bar of record because the empirical alternatives are not usable at N~1e5 (section 4).

## 1. Population (what was drawn)

Wrong-key seeds uniform over six families (bash 4.2 LP64 and ILP32 on the 74-prefix orbit domain; PHP `mt_scale`, `mt_mod`, `php_scale`, `php_mod` on 2^32), blocks of 2^16 per family in round-robin, RNG `default_rng([4101, block, family])`, the REAL `LP2[:24]` head through `pf_v4_12` (frozen point), each survivor decoded by beam_v3 `panel_max` under panel-R36 on `LP2[:120]` (both relations) and, for the first survivors in draw order, on `LP2[:240]`. Every draw records its family and seed (`null_stream.jsonl`, `null_stream240.jsonl`).

| family | heads screened | survivor draws | distinct keys (fit) | L=240 distinct |
|---|---|---|---|---|
| bash 4.2 LP64 | 8,126,464 | 6,812 | 6,484 | 828 |
| bash 4.2 ILP32 | 8,126,464 | 6,914 | 6,596 | 864 |
| PHP mt_scale | 8,126,464 | 6,843 | 6,837 | 854 |
| PHP mt_mod | 8,126,464 | 6,919 | 6,914 | 935 |
| PHP php_scale | 8,126,464 | 6,791 | 6,782 | 843 |
| PHP php_mod | 8,126,464 | 6,870 | 6,869 | 870 |
| **total** | **48,758,784** | **41,149** (rate 8.44e-4) | **40,482** | **5,194** |

Draws per relation x L: **40,482 distinct at L=120 (both relations), 5,194 distinct at L=240 (both relations)** (floors 40,000 / 5,000 met on DISTINCT keys; draws are with replacement, so 667 repeats -- almost all in the bash domain, 77.6 M seeds -- were deduplicated for the fit). Degenerate decodes: 0.0 % at both lengths (kept in the fit regardless).

## 2. Fit and bars

POT above the empirical 90th percentile, `bar(N) = mu + beta ln(N / -ln 0.99)` (round-34 recipe). Bootstrap SEs (200 resamples).

| cell | n | u | mu | beta (SE) | median | q99 | bar N=69,017 | N=1e5 | N=131,786 | N=1e6 | N=1e9 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L120 keyskip1 | 40,482 | 3.865 | 2.9298 | 0.4061 (0.006) | 2.809 | 4.763 | 9.323 | 9.473 | 9.585 (SE 0.077) | 10.408 | 13.213 |
| L120 keyskip2 | 40,482 | 3.880 | 2.9366 | 0.4099 (0.006) | 2.828 | 4.778 | 9.390 | 9.542 | 9.655 (SE 0.081) | 10.486 | 13.317 |
| L240 keyskip1 | 5,194 | 4.314 | 3.4940 | 0.3562 (0.015) | 3.389 | 5.128 | 9.101 | 9.233 | 9.331 (SE 0.21) | 10.053 | 12.513 |
| L240 keyskip2 | 5,194 | 4.373 | 3.5185 | 0.3712 (0.016) | 3.407 | 5.212 | 9.362 | 9.499 | 9.602 (SE 0.19) | 10.354 | 12.918 |

**Bar of record** (`fit.json` `bar_of_record`, served by `bars_v3.bar_v3(N, L, rel, family="survivor12")`): L=120 = max(Gumbel refit, pooled real-sweep survivor POT line), L=240 = Gumbel refit (no real L=240 survivor rows exist); 120 < L < 240 interpolated in ln L; no extrapolation.

| L=120 | N=69,017 | N=1e5 | N=131,786 | N=1e6 | N=1e9 |
|---|---|---|---|---|---|
| keyskip1 | 9.367 | 9.5192 | **9.6325** | **10.4645** | 13.3004 |
| keyskip2 | 9.3897 | 9.5417 | **9.6549** | **10.4856** | 13.3173 |
| null12 keyskip1 (stored) | 8.130 | 8.265 | 8.365 | 9.102 | 11.613 |
| null12 keyskip2 (stored) | 8.044 | 8.176 | 8.275 | 8.999 | 11.468 |
| X1 empirical POT (R37-I2 only, N=131,786) | | | 9.644 / 9.625 | | |
| pooled real-sweep POT (this lane, 307,377 rows) | 9.367 / 9.349 | 9.519 / 9.500 | 9.6325 / 9.6125 | 10.4645 / 10.439 | 13.300 / 13.256 |

The refit at N=131,786 is within 0.06 of X1's empirical 9.6 in both relations (L=120). The null12 cells are 1.2-1.3 below at that N.

## 3. Heterogeneity by generator family

L=120 (n about 6,500-6,900 per family): medians 2.798-2.839, q99 4.69-4.82; bar at N=1e6 by family (keyskip1): bash LP64 10.23, ILP32 10.66, mt_scale 10.53, mt_mod 10.64, php_scale 10.46, php_mod 10.08 (spread 0.58); keyskip2: 10.41 / 10.51 / 10.37 / 10.59 / 10.53 / 10.33 (spread 0.27). A per-family bar SE is about 0.17, so a six-family spread of 0.3-0.6 is what homogeneity predicts. Two-sample KS of each family against the rest: smallest p 0.055 (bash LP64 keyskip1) of 12 tests -- no heterogeneity. **The pooled bar is the record; the largest family bars at 1e6 (ILP32 10.66 for keyskip1, mt_mod 10.59 for keyskip2) are +0.2 / +0.1 above it.** L=240 (n 830-935 per family): bar spread 1.07 / 0.87 (per-family SE about 0.4-0.5); KS nominal p 0.017 (php_scale keyskip1) and 0.033 (mt_scale keyskip1) among 12 tests -- Bonferroni-corrected both > 0.19. Per-family table: `fit.json` `per_family`, `heterogeneity`.

## 4. Q5 -- Gumbel vs the empirical tail (fired, conservative direction)

PREREG tests: (a) the observed maxima of the real stores against the fit-implied Gumbel mean `mu + beta ln N + 0.577 beta` with SE 1.28 beta (about 0.52); (b) the null's own tail counts against the fit at q99 / q99.9 / q99.97.
- (a) 11 of 12 store x relation cells have the observed max BELOW the fitted mean (z = -0.68 ... -2.80; R37-I2 keyskip1 **-2.78** at N=131,786 and R40-B1 keyskip2 **-2.80** at N=142,283; R17PAD -2.2 / -2.1 and COSPAD -2.0 / -2.3 at N=9,908 / 16,940; all in `fit.json` `Q5_realstore_max_vs_fit`); one above (the KDF cell, +1.41 SE).
- (b) observed / expected exceedances: q99 405 / 443 (z -1.8) and 405 / 453 (-2.3); q99.9 41 / 78 (**-4.2**) and 41 / 75 (**-3.9**); q99.97 13 / 33 (-3.5) and 13 / 37 (-4.0). The tail is lighter than exponential (GPD xi about -0.13).
So the exponential extrapolation OVER-predicts, by more than 2 SE: the pre-registered kill fires. What is the "empirical quantile of record" at N~1.3e5? None can be measured: a 1 % family-wise level needs about 100 independent sweeps of that size (we have 4 per relation, whose maxima are 6.5-7.1). The two non-exponential alternatives fail: a GPD (xi<0) fit gives bars of 6.84 / 6.85 at N=131,786 -- BELOW the real stores' own maxima (7.098, 7.065), so it would flag ordinary survivors at a rate far above 1 %; the raw tail quantiles stop at q99.97 (5.8). Therefore the bar of record is the exponential line (R34's conservative choice), taken as the higher of the null refit and the pooled real-sweep POT line, with the lighter-tail evidence reported and never used to lower the bar. Direction of consequence: every best row is 0.9-3.1 under the Gumbel-based bar of record, so no verdict depends on the choice. Honest reading: the true 1 % level at N=131,786 lies between about 7.1 and 9.6; the number 9.6 is an upper bracket, not a measured quantile.

## 5. Q1b -- planted keys through the real chunk path (`control.json`)

20 plants x 12 registers x 2 relations = 480 (bash 4.2 LP64 / ILP32 alternating), `enc_exact` / `enc_pair` of `testhalves-r36` text, only filter = realised C[:40] doublet-free, a 4096-seed chunk holding the key -> `pf_v4_12` frozen -> v3 L=120 -> v3 L=240; judged against the bar of record at N=1e6 (L=120: 10.4645 / 10.4856; L=240: 10.0529 / 10.3539; the Gumbel-refit-only bars give identical counts).
- Screen: 470 / 480 pass (OE 38/40, LATIN 38/40, the other ten registers 39-40/40); 7 of the 10 lost have a skip inside the 24-rune head.
- Bar: **470 / 470 screen-passers clear the bar of record at BOTH lengths**; 470/470 recover >= 0.90 at L=240. Smallest plant pmax: 12.35 (L=120, EN_HALFVOWEL), 17.71 (L=240, OE); per-register minima 12.3-26.7 (L=120) and 17.7-38.7 (L=240) against bars of about 10.5 / 10.05-10.35.
- **Gate (>=19/20 in every register x relation x L cell, path including the screen): FAILS in LATIN keyskip1 and OE keyskip2 (18/20, both L).** The shortfall is the screen's known power (pf_v4_12 0.95-0.99 per register), not the bar. Recorded as `positive_control: failed` in the lane row with this detail.

## 6. Re-judgement of Rounds 36-40 (`rejudged_rounds36_40.json`; N = survivors / decodes as each lane counted)

34 rows (one per cell x relation): R36-B1 (4), R37-I2 (4), R40-B1 3.2 and 5.1 (4; 4.0 and 4.1 are carried by identity with the 4.2 orbit), R40-B3 B04 / KDF / R17PAD / COSPAD (8), R40-C1 screened and beam families C18, R30, R32-lp, R32-slogan, R33 zoo, R43, R47 (14). **0 cross at actual N, 0 cross at N=1e6.** Closest rows:

| row | N | best pmax | stored bar | bar of record at N | gap | bar of record at 1e6 |
|---|---|---|---|---|---|---|
| R40-B3 KDF keyskip2 (the flagged cell) | 591 | 6.528 | 6.342 | 7.435 | -0.91 | 10.486 |
| R40-C1 R43 composed keys / C18 / R32-lp / R30 (keyskip2) | 114-1,291 | 4.8-5.96 | 5.75-6.68 | 6.76-7.76 | -1.7 to -1.9 | 10.486 |
| R40-B3 B04 keyskip1 | 6,041 | 6.336 | 7.244 | 8.367 | -2.03 | 10.465 |
| R36-B1 / R37-I2 / R40-B1 best (7.065 keyskip2; 7.098 3.2 keyskip1) | 64.5k-77.8k | 6.35-7.10 | 8.0-8.2 | 9.30-9.44 | -2.2 to -3.0 | 10.465 / 10.486 |
| R40-C1 R33 zoo / R47 LP2-as-pad (best 4.81 / 4.46) | 2,137 / 112 | 4.2-4.9 | 5.75-6.87 | 6.73-7.96 | -2.3 to -3.1 | 10.486 |

The KDF cell, which cleared its stored actual-N bar (6.528 vs 6.342) and was flagged then judged a noise-crosser by X1, is **0.91 below the bar of record at its own N** (and 3.96 below at 1e6): the flag is withdrawn on the bar, as X1 had concluded on the score-vs-length and word evidence. Where a lane used heads screened as N (B3, C1), the screened-N sensitivity bar is higher still (e.g. KDF 10.33); every row is below that too. R38-B2: no such lane exists in `round38/` (lanes C1, C2, I1, I2, S1, S2, X1; S2-PHP persisted zero rows). R40-B2 (key offsets) was still running at the Round 40 close and is not re-judged here. Direct families (R04, R06, R13, R27, R28) are not judged by the survivor bar; R13 is in section 7.

## 7. Matched nulls for direct families (`benchmark/bars_matched.py`)

`matched_shuffle(stream, block, rng, mode="blockperm"|"within", interrupter=0)` and `bar_matched(stream, block_sizes=(100,250,1000), draws, stat_fn)`: X1's construction (permute the order of contiguous blocks, `Random(60000+j)`; interrupters travel with their block), plus a `within` mode that shuffles the non-interrupter runes inside each block with the interrupters (rune 0) fixed. **Fixture:** the R13 DIRECTION family driven through the standing function (`fixture_r13.py`, the round40 C1 machinery imported unchanged, 500 draws): Z-statistic family p **0.00399 (1 exceed) / 0.01796 (8) / 0.06986 (34)** at blocks 100 / 250 / 1000 -- identical to X1's 0.004 / 0.018 / 0.070 (`fixture_r13.json`). The near-miss therefore does not survive page- or region-scale structure; this lane does not change its status.

## 8. Deviations and limits (R6/R7)

- **Restart of the draw.** The first launch decoded L=240 on each survivor as it was drawn (about 1 survivor/s). It was stopped after 4 complete blocks (1,308 survivors with L=240; partial-block rows removed), and resumed as an L=120-only draw to 41,149 survivors (blocks 4-124), followed by an L=240 phase for the first survivors in draw order lacking one (5,200 decodes -> 5,194 distinct). No selection on pmax was involved (decode order is draw order).
- **Draws are with replacement**; 667 repeat keys are one decode each in the fit. Seeds: bash from the orbit domain the sweeps use, PHP uniform on 2^32 (R32-B2 tier b); the six-family mixture is the declared population and per-family bars are in `fit.json`.
- **Q1a strict failure (keyskip1, -0.047)** is inside the SEs; the pre-registered inequality is met by the max rule, not by the Gumbel fit alone. **Q1b strict failure** (two cells) is the screen's power.
- Real-sweep comparison pools R37-I2, R40-B1 and R40-B3 rows; R40-B1's 4.0 and 4.1 cells re-decode seeds shared with R37-I2 (identity), so the pooled rows are not fully independent -- the R37-I2-only POT line (9.644 / 9.625) is also reported and is within 0.02 of the pooled one.
- The `bars_v3` survivor12 family exists at L=120 and L=240 only; the `free` relation and other lengths are not covered. Direct and unscreened populations keep their own nulls.
- Importing the round40 C1 machinery appends lines to `round40/C1-rescore-46/c1.log` (unavoidable side effect, as X1 noted); the fixture's first output file landed in that directory by a variable shadowing bug and was moved here (`fixture_r13.json`) -- nothing else was written outside this lane except the authorised edits.

## 9. Files

Lane: `PREREG.md`, `RESULTS.md`, `i1lib.py`, `run_null.py`, `run_null240.py`, `run_control.py`, `judge_control.py`, `fit.py`, `rejudge.py`, `fixture_r13.py`, `mk_ledger.py`; data `null_stream.jsonl` (41,149 survivor rows with family, seed, both relations at L=120), `null_stream240.jsonl`, `control_raw.jsonl`; results `null_survivor12.json`, `fit.json`, `control.json`, `rejudged_rounds36_40.json`, `fixture_r13.json`, `ledger.json`, `ledger_patches.json`, `measured_ceiling_replacement.md`; logs `run.log`, `run_state.json`. Authorised edits: `analysis/round34/I1-v3-null/bars_v3.py` (`family="survivor12"`, doctests; default family unchanged), `benchmark/bars_matched.py` (new, doctests), `tests/test_null_refit.py` (new, 8 tests), `.github/workflows/ci.yml` (root; the test added to the pytest step). Gates run here: `python -m pytest tests/test_standing_nulls.py tests/test_null_refit.py benchmark -q` 24 passed; `bars_v3.py` doctests 11/11; `validate_ledger.py` unsound negatives 0; `check_ceiling.py` PASS on the unedited page.

## 10. For the coordinator

1. File `ledger.json` (id `R41-I1-NULL-REFIT-SURVIVOR12`), apply `ledger_patches.json`, replace the MEASURED-CEILING section-1 clause with `measured_ceiling_replacement.md` (pins included), run `check_ceiling.py`.
2. Decide the bar-of-record rule: this lane uses max(Gumbel refit, pooled real-sweep POT) at L=120 -- conservative in the flagging sense. The alternative (Gumbel refit alone) is 0.05 lower for keyskip1 and equal for keyskip2; nothing moves either way.
3. The Q1b gate failed in two cells for screen reasons; whether to treat that as a defect to be repaired in the screen (OE, LATIN) or as the known power limit already on the page (0.952-0.994) is a policy call.
4. The N=1e6 bar of record is now 10.46 / 10.49 (L=120), 10.05 / 10.35 (L=240), replacing 9.10 / 9.00 as the flag gate for survivor-population sweeps. Rows that quote bar12 for UNSCREENED direct decodes (R37-C1/C3, R38-C1, R39-C1) were not patched: their population is the unscreened null12.
