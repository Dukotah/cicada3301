# L5 — Red-team the seal and enforce no-rerun — RESULTS

_Run 2026-08-29. Binding: `ARMADA-DOCTRINE.md` (R6: one lane per round red-teams THIS project's
own current claims; verdict is FOUND-ERROR / NO-ERROR-FOUND, never "confirmed"; R7: bounds not
verdicts). Trust anchor `tests/validate.py` = **ALL VALIDATIONS PASSED (5/5)** before this lane.
Harness `redteam21.py`; raw output `out_redteam21.json`. Deterministic across re-runs (all
populations fixed-seed)._

## Headline

**Overall: MIXED — one FOUND-ERROR-class finding (L1-KILL on sub-attack a), three NO-ERROR-FOUND.**

The mandatory positive control PASSED: the harness detects a known-leaky seal on fresh, unseen data
(single-cut ¼→¾ proxy caught only **0.289** of the fresh hallucination population, matching the
on-disk 33 % / 15-of-45 baseline). So every verdict below rests on a *validated* audit instrument —
a null from an unvalidated instrument is not a negative (doctrine mechanics §2), and this one is
validated.

## The four sub-attacks

| # | attack | verdict | one line |
|---|---|---|---|
| **(a)** | Is L1's disjoint-fold real-mode seal overfit / does it seal at all? | **L1-KILL** | **NO fold cell reaches ≥0.90 catch on the tuning-45 without false-reject >0.10.** The no-oracle seal is *provably leaky* on its own tuning population, before overfit is even reachable. Best cell k=5/min = 0.80 catch @ 0.20 false-reject; the freeze-eligible cells top out at ~0.42 catch. |
| **(b)** | Are the 4 named L3/L4 ledger cells genuinely un-measured AT POWER (no silent re-run)? | **NO-ERROR-FOUND** | All 6 checked cells are named un-measured-at-power in `coverage`/`not_covered` (0 decodes cleared / prior sweep was a RIGID −12.5 decoder = zero power). None is already power-covered. Cross-checked against `ELIMINATION-LEDGER.md:328–384`. |
| **(c)** | Does the fold machinery re-introduce the sieve×panel-max FP inflation (condition b, 2.5×10⁶)? | **NO-ERROR-FOUND** | Fold proxy feeds clause-3 recovery ONLY, never touches `pmax`/screening. Exactly **1** `AD.adjudicate` call per decode in `hitfn20.evaluate` regardless of `k_folds`. Sweeps run UNSCREENED (as S-G3). The 2.5e6 inflation is NOT re-introduced. |
| **(d)** | Can any L3/L4 row be a HIT on score/pmax alone (defect d re-opened)? | **NO-ERROR-FOUND** | Every row routes through `hitfn20.is_hit`, which requires `clears_null` AND `recovery≥0.90` AND `heldout≥0.90` (gate tokens `clears`/`rec_ok`/`ho_ok` all present in `evaluate`). `validate_row_v3` raises on a malformed/lying HIT row. Score alone can never be a HIT. |

## Populations (coverage of the audit)

| population | n kept | reps used | true-recovery extreme | role |
|---|---|---|---|---|
| tuning (S-RESCOPE recipe: `Random(5000+rep)`, encipher `seed=600+rep`, EN_NOVOWEL) | 45 | 60 | max **0.8875** (< 0.90 ⇒ genuine bar-clearing non-recoverers) | the set L1 tunes on |
| fresh (DISJOINT seeds `Random(8000+rep)`, encipher `seed=9000+rep`, seed-3301 order-preserving EN_NOVOWEL surrogate) | 45 | 74 | max **0.8958** (< 0.90) | unseen by L1's tuning |
| genuine panel (correct key, EN_MODERN, `Random(11000+rep)`) | 10 | — | min **1.000** | false-reject test |

Both hallucination populations clear the panel-max bar (`pmax ≥ BAR`) with true rune-index recovery
strictly under 0.90 — i.e. real hallucinations, not weak analogues. The genuine panel recovers 1.0.

## Coverage × power (what this negative/finding is worth)

- **Positive-control power (the audit's own measured power):** single-cut leaky proxy caught at
  **0.289** (fresh) / **0.333** (tuning) — the audit *can* separate a leaky seal from a genuine key
  on unseen data. Genuine decodes are accepted (false-reject 0.0–0.1 for the low-k cells). The audit
  instrument is therefore live, not a null-generator.
- **(a) coverage:** fold grid k∈{2,3,4,5} × rule∈{min,mean} over a 45+45 EN_NOVOWEL hallucination
  surface + a 10-decode genuine panel, on the `exact` (keyskip1) relation. **Not covered:** k=6 and
  the `frac_pass` rule from L1's grid (extending them cannot flip KILL — the highest-catch cell
  already present, k=5/min at 0.80, still fails the 0.90 bar and already carries 0.20 false-reject,
  so every catch-raising direction raises false-reject past 0.10); `drift_rec` relation; registers
  other than EN_NOVOWEL; screened sweeps.
- **(b)/(c)/(d) power:** structural/ledger checks — power is exactness, not a sample. (b) reads
  `coverage`/`not_covered` verbatim (never `status`); (c) counts `adjudicate` calls in source and
  proves the fold path never references `pmax`/`panelmax`/screening; (d) proves the three-clause gate
  and the row validator by construction.

## Language-agnostic statistics persisted

Per doctrine R3 the audit stores, at measurement time, the language-agnostic fold/held-out surface
rather than a bare English catch number: the full **catch-vs-(k, rule)** surface, per-hallucination
held-out recovery vectors (`single_cut_heldouts_fresh`, `fresh_heldouts`), true-recovery extrema of
each population, and the genuine-panel false-reject vectors — all in `out_redteam21.json` and
`ledger.json` here. These are register-independent reproduction fractions, not English LM scores.

## Verdict and consequences

1. **The sieve × panel-max FP inflation of 2.5×10⁶ is NOT re-introduced this round** (sub-attack c,
   NO-ERROR-FOUND). PICKUP open-item #2 stands exactly as R left it in Round 20: any *future*
   screened sieve must re-derive the null on the screened population or carry the correction; this
   round's L3/L4 sweeps are unscreened, so they do not trip it. The fold machinery is clean of it.

2. **No foreclosed lane is being silently re-run** (sub-attack b, NO-ERROR-FOUND, cross-checked
   against `ELIMINATION-LEDGER.md:328–384`). The foreclosed range forecloses PRNG re-runs *under the
   old rigid/flat/English-only instrument*; L3/L4 propose beam+panel adjudications of cells the
   ledger explicitly names un-measured-at-power (0 decodes cleared / RIGID −12.5 = zero power). New
   ground, not a re-run.

3. **The row gate is honest** (sub-attack d, NO-ERROR-FOUND): defect (d) — a HIT on score alone — is
   provably impossible; every row is recovery+held-out gated.

4. **FOUND-ERROR-class finding on the seal (sub-attack a → L1-KILL).** L1's no-oracle held-out gate,
   in its disjoint-fold strengthened form, does **not** seal to ≥0.90 catch on its own tuning
   population without unacceptable genuine-decode false-reject. This is *stronger* than the overfit
   verdict the PREREG anticipated: the seal fails before overfit is even testable. **Consequence
   (abort authority, exercised): Round 21 HIT auto-certification stays WITHHELD.** Any bar-clearing
   survivor from L3 (or any Round-21 sweep) is reported as **flagged-for-oracle**, never
   auto-certified as a solve. This is recorded here BEFORE any L3 negative is published as a
   "0.90-power" negative.

## Bounds, not verdicts (R7)

- What was measured: the fold seal's catch surface on 90 real EN_NOVOWEL hallucinations + a genuine
  panel; the ledger's coverage fields for 4 entries; the fold path's FP-neutrality; the row gate.
- What was NOT measured: the seal on `drift_rec` or non-EN_NOVOWEL registers; k=6/`frac_pass`;
  behaviour on screened sweeps; any LP2 decode (L5 scores none).
- Reopening condition for the seal: a fold/agree scheme (or a different held-out construction) that
  reaches ≥0.90 catch on a fresh hallucination population at ≤0.10 genuine false-reject would let
  auto-certification resume. Until then, survivors are oracle-flagged.
