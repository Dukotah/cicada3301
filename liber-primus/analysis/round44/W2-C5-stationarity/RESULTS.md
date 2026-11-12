# Round 44 / WAVE-2 CELL C5 — DOUBLET-RATE STATIONARITY AT REAL POWER — RESULTS

_Run 2026-11-09. PREREG.md preceded every output and is sha256-stamped in `run.log`
(a287d143…) before first execution. Pure python3 + numpy/scipy, no network. No decode, no
panel: this cell produces zero panel readings, so bars_v3/panel-R36 are N/A by charter
(stated in PREREG, not silently skipped); the fixed bars are the registered statistical α._

## Verdict

**NEGATIVE — no per-page heterogeneity of the residual doublet rate is detectable, at a
measured power that now actually means something.** None of the three registered tests came
anywhere near its bar (per-test bar 0.00333):

| test | statistic | observed | bootstrap p (D=10,000) | fired? |
|---|---|---|---|---|
| T1 | G-test (binomial LRT, 55 pages) | G = 67.94 | 0.2764 | no |
| T2 | Tarone overdispersion Z | +0.539 | 0.4890 (two-sided) | no |
| T3 | family-wise min-p (exact binomial per page) | 0.0208 | 0.4647 | no |

**And the five "elevated-doublet" pages (19/24/27/29/44) are a selection illusion.** Their
individual exact binomial tests, under the registered Bonferroni×55 control (the selection
was data-driven over all 55 pages):

| page | doublets/pairs | rate | exact p | ×55 | fires (bar 1.82e-4)? |
|---|---|---|---|---|---|
| 19 | 5/270 | 1.85 % | 0.0359 | 1.0 | no |
| 24 | 5/269 | 1.86 % | 0.0354 | 1.0 | no |
| 27 | 5/233 | 2.15 % | 0.0208 | 1.0 | no |
| 29 | 4/276 | 1.45 % | 0.1146 | 1.0 | no |
| 44 | 4/272 | 1.47 % | 0.1102 | 1.0 | no |

The family-wise calibration says it directly: a stationary book produces a top page at least
this extreme **46 % of the time** (T3 family p = 0.4647). "Pages 19/24/27/29/44 carry 4–5
doublets each" was never evidence of anything — it is what the maximum of 55 binomials looks
like.

## What this does to the cited rows (both outcomes the charter named, delivered)

1. **D-01 / R18-L2-A-LOCUS hardened.** The old disclaimer was "per-page rate constancy
   tested at power 0.075–0.195 only." The replacement, measured through this cell's own
   plants (400 reps per point, full pipeline):

   | 5-page elevation k (page rate) | power (any test fires) |
   |---|---|
   | 1.0 — pure H0 (0.67 %) | 0.0025 (specificity ✓) |
   | 1.5 (1.0 %) | 0.022 |
   | 2.0 (1.3 %) | 0.048 |
   | 2.5 (1.7 %) | 0.128 |
   | 3.0 (2.0 %) | 0.312 |
   | 4.0 (2.7 %) | 0.743 |
   | **5.173 (3.45 % = NO filter)** | **0.975** |

   So: **A4-H10's literal mechanism — five pages written "plain additive without the
   anti-doublet rule" — is EXCLUDED at measured power 0.975.** Any 5-page subset carrying
   an unfiltered (or ≥4×) residual rate would have fired and did not. The stationarity
   assumption behind every book-wide model (A-LOCUS M1/M2, the beam's filter model) now
   stands on power 0.97, not 0.075, against that alternative class.

2. **Method boundary localized.** The grid MDE at power 0.8 is k = 5.173 (interpolated
   ≈ 4.3, page rate ≈ 2.9 %); at power 0.5 it is k = 4.0 (interpolated ≈ 3.4). Milder
   5-page elevations — including the k ≈ 2–3 scale the flagged pages' raw rates suggested —
   are **below detectability at n = 12,956 with 55 pages**: power 0.05–0.31. That is not a
   failure, it is the measured resolution floor of ANY per-page count test on this book:
   expected count ~1.6 per page leaves nothing for a milder signal to be made of. A future
   lane needs a different observable (not per-page counts) to go below k ≈ 4.

## Instrument + controls (plants.json, gate passed BEFORE the real run)

- **Null model:** c_i ~ Binomial(m_i, r), exact for the pinned mechanism (memoryless base +
  flat ciphertext filter: the per-emission repeat probability is constant, so pair
  indicators are i.i.d.). Census cross-checked: 86 within-page doublets / 12,901 within-page
  pairs, per-page tuple identical to W2-B3's pinned `real_sites_U86` and R12-D2's numbers
  (halt condition, passed).
- **Plant:** synthetic books through the FULL glue (exact filtered-chain sampler at the
  calibrated p_keep = 0.1879 → same census → same statistics → same bootstrap decision),
  real page lengths, the real flagged pages' lengths elevated. Sampler verified unbiased
  (repeat rate within 1σ of target at n = 5 M, three seeds).
- **Specificity:** 400 pure-H0 books → false-fire rate 0.0025 (family α = 0.01 ✓).
- **Gate:** power 0.975 ≥ 0.8 at the unfiltered mechanism → PASS → real run authorized.
- Real-run bootstrap D = 10,000, add-one p, refit r̂ per draw (same estimator as observed).

## Coverage × not_covered (the three conditionals, PREREG Q4)

**Covered:** page-granularity heterogeneity of the residual doublet rate on the 55-segment
unsolved stream (D-01's object), in the binomial family, via G / Tarone / family-min-p at
family α = 0.01, with the measured power curve above (verdict-capable at k ≳ 4; power 0.975
at the unfiltered-pages mechanism). The five blind-flagged pages individually, exact tests
under ×55 control.

**not_covered:**
- *space:* sub-page drift and SERIAL/ordering structure across pages — G, Tarone and min-p
  are exchangeable-across-pages statistics and are blind to smooth regional trends by
  construction. **W2-B3's T7 flag (gap lag-1 autocorrelation, p = 0.0010, block-scale rate
  heterogeneity) is therefore neither confirmed nor retired by this cell** — the two results
  are compatible: smooth multi-page variation too mild to show as per-page overdispersion.
  The T7 follow-on still needs an ordering-sensitive registered test with its own plant.
  Elevations on other page-subset shapes (1 page, 20 pages) have different power curves;
  only the 5-page shape was planted.
- *transition model:* the binomial null is exact for the memoryless-base flat-filter model
  (A-LOCUS CIPHERTEXT, D-01 flat/unscoped/single-lag); a base stream with strong serial
  structure would violate pair independence (bounded, not erased, by IoC·N 0.9999 and
  D-01's zero lag-2..8 bleed).
- *register:* N/A — no plaintext channel exists in this cell; nothing here could certify or
  miss a decode.

## Flags

None. No bar-crosser; nothing for the oracle. The result is a hardening (D-01 stationarity
at page scale, power 0.075 → 0.975 vs the strong alternative) plus a localized boundary
(k ≲ 4 per-page elevations invisible to count-based tests at this n), plus the demotion of
the pages-19/24/27/29/44 observation to expected binomial extremes.

## Files

- `PREREG.md` — stamped in `run.log` before first execution (R44 X1 hygiene rule)
- `c5lib.py` — the single glue (census, statistics, bootstrap, plant sampler)
- `plant_gate.py` → `plants.json` — specificity + power curve + gate decision
- `run_real.py` → `results.json` — census cross-check + the three real tests + per-page table
- `ledger_rows.json` — draft row (LEDGER.json untouched)
