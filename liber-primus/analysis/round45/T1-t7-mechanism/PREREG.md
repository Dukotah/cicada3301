# Round 45 / LANE T1 — T7 MECHANISM, HONEST NULLS — PREREG

_Dated 2026-11-23. Written and sha256-stamped into `run.log` BEFORE any script in this
directory produced an output. Thresholds below are frozen; any change is a dated addendum
appended at the bottom with its reason, never an edit._

## 0. Cited facts (what this lane consumes)

- `analysis/round44/W2-B3-doublet-sites/RESULTS.md` §3 + row `R44-W2B3-D01-FALSIFIER`: the 86
  surviving doublets of the 12,956-rune unsolved stream; T7 (lag-1 Pearson AC of the 85
  inter-site gaps) = +0.380, p = 0.0010 (D = 10,000 site-matched null), X1's own gap-permutation
  null p = 0.00025; the other six battery statistics null (p ≥ 0.23). Caveat recorded there:
  **no plant exercised smooth rate heterogeneity** — T7's power against its own alternative is
  unmeasured.
- `analysis/round44/W2-C5-stationarity/RESULTS.md`: per-page count tests are structurally blind
  below a ~4x five-page elevation (power 0.05–0.31 at k = 2–3).
- `analysis/fable52/OUTPUTS.txt` (t3_t7_anatomy): rank AC +0.268 (p = 0.003), log-gap AC +0.229
  (p = 0.010); before/after the 3140 void both halves ≈ +0.21 → distributed heterogeneity, not
  one void; the line-occupancy null is saturated (power 0.04). T5: a plaintext-letter marker
  model reaches +0.38 in 0.8 % of English windows, a flat Bernoulli in 0.6 % — not favoured over
  a machine leak.
- Structure (read from `data/krisyotam_runes.txt`, the canonical rtkd-lineage transcription the
  dataset is built from; page split `%`): `$` (chapter end) after unsolved runes
  729, 1874, 3612, 5506, 6527, 7960, 9640 (and 12956 = stream end); `&` (section end, the
  transcription's mark for the dot-diamond section separators) after runes 729, 848, 1541, 1860,
  1874, 3603, 3612, 5506, 6527, 7960, 8051, 9358, 9519, 9640, 12114, 12648 (and 12956).
  Physical dot diamonds (`round44/P1-red-ink/census.json`): 27 × 13-dot + 3 × 10-dot; the 10-dot
  ones on images 36, 38, 49 (= segments 36, 38, 49). Diamonds are image-located only (bbox), not
  rune-located; this lane maps them to rune positions **approximately** (page start + vertical
  fraction × page length) and uses that mapping **descriptively only**.

## 1. Object

x = the 12,956-rune unsolved stream (segments 0–54 of `krisyotam_runes.txt`). Pair index
t = 0 … 12,954 (T = 12,955 pairs, pair t = (x[t], x[t+1])). Event set E = {t : x[t] = x[t+1]}.
**Halt gate:** |E| must equal 86 and equal B3's persisted `real_sites_U86` positions; else HALT.

All models are point processes on the pair axis [0, T) with intensity λ(t) (events per pair).
Likelihood = Σ_i log λ(t_i) − ∫λ (inhomogeneous-Poisson form; at λ ≈ 0.0066 the Bernoulli/
Poisson difference is negligible and identical across models, so model comparisons are exact
in this form).

## 2. Pre-registered covariates (four, no more)

- **Z1 chapter** — the 8 `$`-delimited chapters (categorical).
- **Z2 section** — the 17 `&`∪`$`-delimited sections (categorical; = the dot-diamond-separated
  intervals as transcribed).
- **Z3 position-within-section** — (t − section start)/(section length), in [0,1) (continuous).
- **Z4 position-within-page** — (t − page start)/(page length), in [0,1) (continuous;
  a page = one physical sheet = a plausible "sitting").

Page as a 55-level categorical is NOT a covariate here: C5 already measured that observable's
power floor; it is reported descriptively only.

## 3. Mechanism models (the candidate set used by the classifier — fixed)

| id | mechanism | intensity | free params k |
|---|---|---|---|
| M0 | stationary Bernoulli leak (D-01) | λ = c | 1 |
| M1a | sessioned generation, sessions = chapters | piecewise constant on Z1 | 8 |
| M1b | sessioned generation, sessions = sections | piecewise constant on Z2 | 17 |
| M1c | sessioned generation, sessions NOT aligned with marked structure | piecewise constant, K ∈ {1..6} free change points (grid step 25 pairs), K chosen by BIC | 2K+1 |
| M2 | smoothly drifting filter slip rate | log λ = Gaussian random walk over 25-pair bins (discretised HMM, 48 log-rate levels in [log 5e-4, log 4e-2], step sd σ ∈ grid of 12 values incl. 0), uniform initial prior over levels | 2 |
| M3a | rate driven by Z3 | log λ = a + b·Z3 | 2 |
| M3b | rate driven by Z4 | log λ = a + b·Z4 | 2 |
| M4 | stateful rejection loop, rate depends only on time since last slip | renewal process, gamma gaps (shape κ, scale θ); first gap from t=0 treated as a full gap, last gap censored | 2 |

M2's maximised log-likelihood is defined as L0_max + [L2(σ̂) − L2(σ=0)] (both L2 terms under the
same uniform initial prior, so the bracket is a proper LRT increment and σ = 0 reproduces M0).
Analytic prediction recorded in advance: a pure renewal M4 has i.i.d. gaps, so E[T7] ≈ 0 under
M4 at any κ; M4 can explain gap-shape anomalies (T2), not gap serial correlation. A
self-exciting (Hawkes-type) loop — state persisting over several slips — is **not** in the
candidate set (stated not-covered; it is observationally close to M2/M1c at this n).

## 4. Statistics

Detection of non-stationarity (each p-value from D_null = 2,000 M0 draws = 86 positions uniform
without replacement on [0,T), add-one, upper tail unless stated):

- **S1** T7 (Pearson lag-1 gap AC) — continuity with B3 (two-sided).
- **S2** rank lag-1 gap AC (two-sided).
- **S3 (PRIMARY, the registered ordering-sensitive smooth-heterogeneity statistic)**
  LRT_M2 = L2(σ̂) − L2(0).
- **S4** multi-scale Fano: max over W ∈ {250, 500, 1000, 2000} of the null-standardised
  Fano factor of counts in contiguous W-pair windows.
- **S5** free change-point LRT: max over K ∈ 1..6 of [L_M1c(K) − L0 − penalty-free], i.e.
  max_K of the BIC-improvement of M1c over M0 (look-elsewhere is in the null: the null draws
  run the same search).

Mechanism discrimination: **classifier = argmin BIC over {M0, M1a, M1b, M1c, M2, M3a, M3b, M4}**
(BIC = −2L + k ln 86). Secondary check on real data only: 2-fold held-out log-likelihood with
interleaved 500-pair blocks (fit on one fold, score the other; M2 predicts masked bins by HMM
smoothing; M4 scores held-out events with the full past as history).

## 5. Plants (positive controls; ALL through the same fit/classify code as the real data)

Stage A — fixed-parameter plants, 86 events exactly (positions drawn without replacement with
weights ∝ λ(t); M4 by 87 gamma gaps normalised to span T), 200 draws each, at two strengths
σ_L ∈ {0.5, 0.8} = target sd of log λ(t) along the stream:

- P-M1a: chapter log-rates i.i.d. N(0, σ_L²). P-M1b: section log-rates i.i.d. N(0, σ_L²).
- P-M1c: K = 4 change points uniform on [0,T), segment log-rates i.i.d. N(0, σ_L²).
- P-M2: Gaussian random walk on 25-pair bins, step sd s = σ_L·√(6/n_bins), re-centred.
- P-M3a: log λ = b·Z3 with b = σ_L/0.2887 (sign random). P-M3b: same on Z4.
- P-M4: gamma gaps, κ = 0.6 (σ_L = 0.5 arm) and κ = 0.4 (σ_L = 0.8 arm) (over-dispersed loop).
- P-M0: 200 M0 draws (specificity; the classifier's false-heterogeneity rate).

Stage B — parametric bootstrap at the REAL-DATA best-fit parameters of each heterogeneity
model (M1a, M1b, M1c, M2, M3a, M3b, M4; 200 draws each): confusion matrix at the effect size
the data actually supports. Stage B necessarily follows the real fits; its protocol is fixed here.

Reported: (a) power of S1–S5 at α = 0.05 and α = 0.01 per plant; (b) the 8 × 8 confusion matrix
(rows = planted, cols = BIC choice) for Stage A (both strengths) and Stage B; recall and the
calibrated precision P(planted = k | chose k) under a uniform prior over the plant rows.

## 6. Thresholds — FIXED IN ADVANCE

1. **Gate (before the real verdict is read):** S3 power at α = 0.01 against the P-M2 σ_L = 0.8
   plant must be ≥ 0.5, and M0 specificity: S3 false-fire rate on P-M0 ≤ 0.02 at α = 0.01. If
   the gate fails, S3 on the real data is reported "uninformative" and the lane falls back to S1
   (with its own measured power) — no verdict upgrade.
2. **Non-stationarity confirmed** (independently of B3) iff real S3 p ≤ 0.01.
3. **A mechanism is "favoured"** iff it has the lowest real BIC AND its Stage-B recall ≥ 0.5 AND
   calibrated precision ≥ 0.6. **"Decisive"** additionally needs ΔBIC ≥ 6 to the runner-up and
   precision ≥ 0.8. A mechanism is **"disfavoured"** iff ΔBIC ≥ 10 vs the best AND its Stage-B
   recall ≥ 0.5 (i.e. it would usually have won had it been true). Anything else:
   **"not separable at n = 86"**.
4. **Change-point coincidence with structure:** for the real M1c fit (and, descriptively, the
   M2 posterior-mean rate profile's extrema), statistic = mean distance from each change point
   to the nearest boundary of a structure set; null = K uniform points, 10,000 draws; family of
   4 sets (chapter ends, section ends, page starts, the three 10-dot pages' starts) at
   α = 0.01/4 = 0.0025 per set.
5. M4 is "excluded as the T7 mechanism" iff the M4 plants' T7 95th percentile < observed 0.380
   (analytic prediction above, now measured).

## 7. Aiming Test

- **Q1 — what would a hit look like, and would this instrument recognise it?** A hit is a
  mechanism whose BIC wins on the real data AND that the classifier recovers ≥ 50 % of the time
  when it is planted at the real-data effect size (Stage B), with ≥ 60 % calibrated precision.
  Plants of every mechanism go through the identical fit/classify code (Stage A + B). If 86
  events cannot separate the mechanisms, the confusion matrix says so and that is the result.
- **Q2 — what measured fact raises the prior?** T7 (B3, p = 0.0010; X1 p = 0.00025; njloof
  replicate p = 0.0006; external chapter-conditioned p ≈ 5e-5) and Fable52's rank-AC/void
  anatomy (`analysis/fable52/OUTPUTS.txt`). This is a measured-anomaly lane, not a sweep.
- **Q3 — is the space bounded?** Yes: 8 named models, ≤ 17 parameters each, 4 covariates, one
  86-event object. Enumerable; total ≈ 6,000 simulated data sets.
- **Q4 — three conditionals of a negative.** (1) *Model space:* the 8 models above (no Hawkes /
  self-exciting state, no AR(1) mean-reverting drift distinct from the RW, no plaintext-letter
  coupling, no per-rune-value rates). (2) *Transition/generation model:* the leak is a point
  process on the pair axis of the unsolved stream as transcribed (krisyotam/rtkd lineage; S1 is
  auditing the transcription); doublets only (lag-1 equality). (3) *Register:* N/A for decoding
  — no plaintext adjudicator is used; the "register" analogue is the covariate set Z1–Z4.
- **Q5 — kill condition at 10 % budget.** After Stage-A plants for P-M2 and P-M1c only: if every
  statistic S1–S5 has power < 0.2 at α = 0.05 against BOTH at σ_L = 0.8, the instrument cannot
  see heterogeneity of this kind at n = 86 → stop, report "uninformative", no real-data mechanism
  claim.

## 8. Not doing

No decodes, no key sweeps, no edits outside this directory, no git commit, no LEDGER.json edit.

---

## Addendum 1 — 2026-11-23 (written after the real detection line was seen; EXPLORATORY ONLY)

**Reason.** The real-data detection line came back discordant: S1 (T7) p = 0.0010 and S2 p = 0.006
replicate B3, but the registered smooth-heterogeneity statistic S3 is exactly 0 (σ̂ = 0, p = 1.0)
and S4 (p = 0.38) / S5 (p = 0.62) are null — although Stage A measured S3/S4/S5 as *more*
powerful than S1 against every rate-heterogeneity plant (e.g. P-M2 σ_L = 0.8: S3 0.865 vs S1 0.295
at α = 0.01). Nothing registered above is changed; no verdict in §6 may be upgraded or downgraded
by this addendum. Two post-hoc analyses, labelled exploratory in RESULTS:

- **E1 discordance likelihood.** Estimate P(S1 ≥ 0.380 AND S3 ≤ 1e-9) under M0 (10,000 draws) and
  under the Stage-A heterogeneity plants P-M1a/M1c/M2 at σ_L ∈ {0.5, 0.8} plus the E2 plant (500
  draws each). Report each as a likelihood ratio vs M0 for the *joint* observed pattern (does any
  rate-heterogeneity mechanism make "T7 fires but the rate profile is flat" more likely than M0?).
- **E2 fast-switching two-state rate model** (not in the §3 set): 25-pair bins, two rates with
  ratio ρ ∈ {1.5, 2, 3, 4, 6, 10}, fraction-high π ∈ {0.3, 0.5, 0.7}, mean dwell d ∈ {2, 4, 8, 16, 32}
  bins, mean rate fixed at n/T; statistic = max LRT vs M0; null 2,000 M0 draws; positive control =
  500 plants at ρ = 4, π = 0.5, d = 12 bins (300 pairs). Reported p ≤ 0.01 is "exploratory signal",
  never a registered verdict.
- **E0 (descriptive):** per-gap-pair contributions to the T7 Pearson sum, to show which gap pairs
  carry the statistic.

## Addendum 2 — 2026-11-23 (after Addendum 1 results; DESCRIPTIVE ONLY)

E0 showed two gap pairs inside the 2739–4388 void carry 0.21 of T7's 0.38. Added descriptive
**E0b fragility**: insert ONE extra doublet event at every 5th pair position (one at a time) and
report the minimum resulting T7 and its p against the run_plants.py S1 null, plus the positions
whose insertion pushes T7's p above 0.01. Purpose: tell lane S1 (transcription audit) which
positions would matter. No verdict depends on it.
