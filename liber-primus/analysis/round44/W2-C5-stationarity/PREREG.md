# Round 44 / WAVE-2 CELL C5 — DOUBLET-RATE STATIONARITY AT REAL POWER — PREREG

_Dated 2026-11-09, written and sha256-stamped into `run.log` BEFORE any execution._

## Cited ledger rows (verified wording before registration)

- **R18-L2-A-LOCUS** (`LEDGER.json` entries[62]) — `not_covered`: "loci that vary along the
  book (all models here are stationary; P4 already showed the rate is constant across the 55
  pages at power 0.075, i.e. underpowered)". This cell runs inside that named gap.
- **D-01** (entries[13]) — `coverage`: "Tests of drift, fatigue, per-page rate constancy and
  off-diagonal bigram structure are underpowered at n=12,956 (0.075-0.195) and are reported
  as such, not as evidence."
- **R43 X0 ADJUDICATION item 22** (`analysis/round43/X0-firewall/ADJUDICATION.md`) — REOPEN:
  "a per-page-heterogeneity test with a real positive control is the named gap."
- **R44 W2-B3** (`analysis/round44/W2-B3-doublet-sites/RESULTS.md`) — T6 (per-page binomial
  dispersion) did not fire (p=0.59) but carried **no heterogeneity plant and no measured
  power**; T7 (gap lag-1 autocorrelation) FIRED (p=0.0010), direct evidence of multi-hundred-
  rune-scale rate heterogeneity. B3's `results.json real_sites_U86` pins the site tuple
  (per-page counts: pages 19/24/27/29/44 hold 5,5,5,4,4 of 86). This cell does NOT re-run
  B3's channel reads or its 7-statistic battery; it builds the POWERED per-page instrument
  that B3 and X0 item 22 both name as the follow-on.
- **R12-D2** (entries[9]) — headline counts (n=12,956; 86 doublets; per-page rate 0.667%)
  independently reproduced; my census must match these or the run halts.
- **R43 F1-blind A4-H10** (`analysis/round43/F1-blind/hypothesis_lists.json`) — the
  alternative under test: "The five elevated-doublet pages (19, 24, 27, 29, 44) use a
  different, older scheme… possibly plain additive without the anti-doublet rule."

## Hypothesis

- **H0 (D-01's stationary soft-filter model):** within-page adjacent-pair doublet indicators
  are i.i.d. Bernoulli(r) with ONE book-wide r (machine rejection filter, flat, unscoped,
  single-lag — D-01; acting on the ciphertext — A-LOCUS). Per-page counts c_i ~
  Binomial(m_i, r), m_i = within-page adjacent pairs. (For a memoryless uniform base with a
  flat keep-probability filter this binomial model is EXACT: the repeat probability per
  emission is a constant r independent of history.)
- **H1 (A4-H10 class):** a subset of pages carries a different p_keep (elevated residual
  doublet rate), i.e. the filter parameter is non-stationary at page granularity.

## Instrument (all code in `c5lib.py`, ONE code path for plants, nulls and the real run)

Census: `data/krisyotam_runes.txt` split on `%`, 57 segments, first 55 = the unsolved stream
(12,956 runes; the D-01 object). Doublet = adjacent equal rune pair; counted only at
within-page pairs (Σm_i = 12,956 − 55 = 12,901; the 54 cross-page joins hold 0 doublets per
R12-D2 and are excluded, matching B3's T6 convention). Cross-check gate: my census must
reproduce exactly 86 sites and B3's persisted per-page counts, else HALT.

Three registered statistics, p-values by parametric bootstrap under H0
(c*_i ~ Binom(m_i, r̂), r̂ refit per draw, D = 10,000, add-one):

- **T1 — G-test (binomial LRT, saturated per-page rates vs common rate):**
  G = 2·Σ_i [c_i ln(c_i/e_i) + (m_i−c_i) ln((m_i−c_i)/(m_i−e_i))], e_i = m_i·r̂. Upper tail.
- **T2 — Tarone's standardized overdispersion score:**
  Z = (S − Σm_i)/√(2·Σ m_i(m_i−1)), S = Σ (c_i − m_i r̂)²/(r̂(1−r̂)). TWO-sided
  (overdispersion = heterogeneity; underdispersion = quota-like violation; both break H0).
- **T3 — family-wise min-p:** p_i = exact binomial upper tail P(Bin(m_i, r̂) ≥ c_i);
  statistic = min_i p_i, calibrated family-wise by the same bootstrap. Additionally the five
  flagged pages (19/24/27/29/44) are reported individually at Bonferroni×55 (the selection
  was data-driven over all 55 pages, so the correction is over 55, not 5).

## Thresholds — FIXED IN ADVANCE

- Family α = **0.01**, Bonferroni over the 3 registered tests → per-test bar **p ≤ 1/300 =
  0.0033333…** (attainable: add-one minimum at D=10,000 is ≈1.0e-4).
- ANY registered test at or under its bar → **NONSTATIONARY — LOUD FLAG** (a falsifier flag
  like B3's T7, i.e. a ledger row + RESULTS, not a plaintext candidate; no HUMAN-ORACLE
  decode bundle exists because nothing decodes).
- No test fires → **negative, conditioned on the measured power curve below** (hardens D-01
  to the stated resolution).
- Individual flagged page: p_i ≤ 0.01/55 = 1.818e-4 → that page individually flagged.

**bars_v3 / panel-R36 statement:** this cell produces ZERO panel readings — no decode
stream, no English adjudication (cell charter: "No decode; no panel needed"). `bars_v3.py`
calibrates panel pmax bars at N readings; at N_panel_readings = 0 it has no object here. The
fixed bars of this cell are the statistical α above, registered before execution. The
standing adjudicator is cited as NOT APPLICABLE, loudly, rather than ritually invoked.

## Positive control — REAL plant through the full glue, BEFORE any real-data run

Plant = a synthetic book with the REAL page lengths: 50 pages generated from the exact
filtered-chain sampler at the global rate r (calibrated so the book-wide doublet rate equals
the real r̂ = 86/12,901 = 0.0066662; equivalent p_keep = r(1−q)/(q(1−r)) = 0.1879 at
q = 1/29), and the 5 pages with the real lengths of pages 19/24/27/29/44 at elevated rate
k·r — the actual shape of the A4-H10 alternative. Sampler: x_t = x_{t−1} w.p. r_page, else
uniform over the other 28 (the exact emitted-chain law of a flat rejection filter over a
uniform base). Each replicate runs the ENTIRE pipeline: stream → site extraction →
within-page counts → T1/T2/T3 → its own D = 2,000 parametric bootstrap p-values → the
registered decision rule.

- Effect grid: k ∈ {1.5, 2, 2.5, 3, 4, 5.173}, where k = 5.173 is p_keep = 1, i.e. the five
  pages carry NO anti-doublet filter at all — A4-H10's literal mechanism. (Observed flagged-
  page rates 1.4–2.1% correspond to k ≈ 2.1–3.2.)
- R = 400 replicates per k. Power = fraction of replicates where ANY registered test fires
  at its per-test bar. Specificity arm: 400 replicates at k = 1 (pure H0); false-fire rate
  must be ≈ family α (report; alarm if > 0.03).
- **GATE (must pass before the real run):** power ≥ 0.8 at k = 5.173. If the instrument
  cannot detect five fully-unfiltered pages, it cannot adjudicate A4-H10 →
  INSTRUMENT-INCOMPLETE, stop, report honestly.
- **Deliverable either way:** the minimal detectable effect k* at power 0.8 (and 0.5) at
  n = 12,956 — this number is the resolution to which D-01 gets hardened, or the method
  boundary that gets localized.

## The five Aiming-Test answers

**Q1 — What would a hit look like, and would this instrument recognise it?** A hit = per-page
doublet-rate heterogeneity. The recognizer (T1/T2/T3 + bootstrap) is proven on a plant that
has EXACTLY the hypothesised shape — the five real flagged pages' lengths carrying an
elevated/unfiltered p_keep — pushed through the same census, statistics and bootstrap as the
real book. Not a friendly analogue.

**Q2 — What measured fact raises the prior above flat?** (a) W2-B3's T7 fired at p = 0.0010
on this exact object (`analysis/round44/W2-B3-doublet-sites/battery_ext.json`): measured
rate heterogeneity at block scale. (b) The cited rows themselves disclaim the stationarity
assumption at power 0.075–0.195 (R18-L2-A-LOCUS not_covered; D-01 coverage). (c) X0 item 22
adjudicated REOPEN with this cell's design as the named gap.

**Q3 — Is the space bounded?** Yes — fully. One object (55 per-page counts), one parametric
null family, three statistics, one effect-size axis sampled at 6 points. Everything
enumerable in one run; no sweep.

**Q4 — The three conditionals of a negative:**
1. *space:* per-page (segment-granularity) heterogeneity of the residual doublet rate in the
   binomial family, down to the measured k*; NOT finer-than-page drift, NOT cross-page
   block structure as such (B3-T7's scale; pages ≈ 235 runes partially alias it, unmeasured
   here), NOT heterogeneity in doublet VALUES or positions-within-page (B3 covered values/
   positions book-wide).
2. *transition model:* binomial null is exact for the memoryless-base flat-filter model
   (A-LOCUS: ciphertext locus; D-01: flat, unscoped, single-lag). A base stream with strong
   serial structure would perturb m_i→c_i independence; the real stream's IoC·N 0.9999 and
   D-01's zero lag-2..8 bleed bound that risk but do not erase it.
3. *adjudicator register:* N/A — statistical tests, no language register; nothing here can
   produce or miss a plaintext.

**Q5 — Kill condition at 10% of budget:** the plant gate. If power < 0.8 at k = 5.173
(five unfiltered pages) the instrument cannot reach even the strongest version of the
alternative → report INSTRUMENT-INCOMPLETE with the measured curve and stop; no real-data
verdict is issued.

## Order of operations (binding)

1. sha256-stamp this file into `run.log` (dated) — before any execution.
2. `plant_gate.py` → `plants.json` (specificity + power curve + gate decision).
3. Gate passed → `run_real.py` → `results.json` (census cross-check vs B3/R12-D2, then the
   three tests at D = 10,000).
4. `RESULTS.md` + `ledger_rows.json`. LEDGER.json untouched.

Seed: 3301 (plants), 3302 (real-run bootstrap). Pure python3 + numpy/scipy, no network.
