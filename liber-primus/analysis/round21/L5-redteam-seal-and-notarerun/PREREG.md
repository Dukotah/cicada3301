# L5 — Red-team THIS round's own reasoning (seal + not-a-re-run)

_Pre-registered 2026-08-29, BEFORE L1/L3/L4 land and BEFORE any L5 measurement. Binding:
`ARMADA-DOCTRINE.md` (R6: at least one lane per round red-teams THIS project's OWN current claims;
verdict is FOUND-ERROR / NO-ERROR-FOUND, never "confirmed"). This lane has abort authority: if it
finds L1's seal overfit on a held-out population, or any L3/L4 cell already power-covered, that
certification/cell is WITHDRAWN before the negative is published._

## What this lane attacks (this round's own, un-auditable-by-any-prior-red-team claims)

1. **L1's fresh-this-round seal** — the disjoint-fold real-mode held-out proxy (`hitfn21_folds`),
   whose stated risk is being OVERFIT to the 45 EN_NOVOWEL hallucinations it is tuned on
   (`L1-seal-realmode-proxy/PREREG.md` Q3/Q5, P-b).
2. **This round's OWN not-a-re-run justification** for the four new sweep cells (L3 three Py2.7
   reducers + 64-bit ABI map; L4 glibc `gen=0` full-32 + `gen=7`/`gen=8` re-adjudication) — the claim
   that the ledger's `not_covered` fields say they are un-measured AT POWER (`CAMPAIGN-PLAN` §4, §6).

Neither claim existed before this round, so no prior red-team could have audited them. That is why
this lane is new ground (doctrine R6) and is NOT a re-run of R19/R20 red-teams.

---

## The five Aiming-Test answers

### Q1 — What would a hit (a found error) look like, and would THIS instrument recognise it?

A "hit" for a red-team lane is a **FOUND-ERROR**: a demonstration that a Round-21 claim is false at
its own operating point. Four named sub-attacks, each with a concrete recogniser:

- **(a) Overfit seal.** Re-implement L1's disjoint-fold proxy exactly per `L1/PREREG.md` Q1 (k
  contiguous folds, attribute phase on fold-k, re-decode complement, MIN-across-folds), pick the cell
  L1 would freeze on the tuning-45, then re-measure its catch on a **FRESH** order-preserving
  surrogate hallucination population generated with seeds DISJOINT from the tuning seeds
  (tuning uses `Random(5000+rep)` window + `encipher(...,seed=600+rep)`; fresh uses a disjoint block
  `Random(8000+rep)` window + `encipher(...,seed=9000+rep)`, plus a seed-3301 order-preserving
  surrogate register variant). Recogniser: if fresh-population catch < 0.90 while tuning-45 catch
  >= 0.90, the seal is **overfit → FOUND-ERROR** and HIT auto-certification stays withheld.
- **(b) Already-covered cell.** For each of the 4 ledger entries (`R19-G3`, `R16-PRNG`,
  `R19-G3-CORRECTION`, `B-13-MARSAGLIA`), read `coverage`/`not_covered` (NOT `status`) and confirm the
  specific L3/L4 cell is named as un-measured at power (prior sweep was rigid + English-4gram + fixed
  invalid bar = zero power, per R19-G3-CORRECTION's own text). Recogniser: if any cell is already
  power-covered (a beam+panel+valid-bar adjudication exists), that cell is **already a re-run →
  FOUND-ERROR**, dropped.
- **(c) Fold machinery re-inflates panel-max FP.** The panel-max null has a known latent condition
  (b): screened-survivor double-max FP 0.025/decode vs nominal 1e-8 = 2.5e6 inflation. Recogniser:
  the fold proxy touches only clause-3 recovery, NOT the pmax bar or its screening; confirm L3/L4
  sweep UNSCREENED (as S-G3 did) so condition (b) is not triggered, AND confirm the fold count does
  not change the number of pmax evaluations per decode (one adjudicate call per decode, unchanged).
  If the fold machinery silently multiplies pmax draws or re-enables screening → FOUND-ERROR.
- **(d) Row scores, not recovers.** Confirm every L3/L4 row is a `SWEEPROW/3` gated through
  `hitfn` (clears_null AND recovery AND held-out), never `pmax >= bar` alone. Recogniser: a HIT with
  `clears_null=False` or `heldout_recovery < 0.90` in any row → FOUND-ERROR (the original defect d).

The instrument recognises its own planted error via the **mandatory positive control** below.

### Q2 — What measured fact raises this above the flat rate?

This is a closure/instrument audit (doctrine §0: every genuinely-new finding here came from auditing
a closure/instrument, never a flat-prior sweep). The measured foothold is
`round20/S-RESCOPE/out_heldout_proxy_audit.json`: the 45 hallucinations' single-cut held-out
recoveries are ON DISK (30 of 45 >= 0.90 = the misses that make the single-cut proxy leak at 33%).
That file is the exact object whose fold-strengthened successor this lane re-audits on FRESH data.

### Q3 — Is the space bounded, and by what?

Bounded and enumerable:
- 4 named sub-attacks over a **fixed cell list of exactly 4 ledger entries** (b/d are reads +
  assertions; c is a structural check).
- A **fresh finite surrogate hallucination set matched in size to L1's 45** (target n>=45 kept,
  drawn from disjoint seeds), plus a seed-3301 order-preserving surrogate register variant. Fully
  reproducible from a fixed recipe.
- The fold-proxy re-implementation reuses the same `driftbeam`/`adjudicate`/`panelmax20` instruments
  already validated; L5 adds no new key space and scores no LP2 decode.

### Q4 — The three conditionals THIS lane's negative (a NO-ERROR-FOUND) will carry

If L5 returns NO-ERROR-FOUND for sub-attack (a), it means: the fold seal generalises to a fresh
EN_NOVOWEL hallucination population **conditional on** (1) key space = the correct `sha256_ctr+mod29`
key (the hardest case, a genuine bar-clearing hallucination), (2) decoder relation = the `exact`
(keyskip1) preset the leak was localised on, (3) adjudicator register = EN_NOVOWEL argmax (the
detection-only register where hallucinations live). A pass does NOT certify the seal on `drift_rec`,
on other registers, or on screened sweeps — those are named as not-covered.

### Q5 — What single observation abandons this lane at <=10% of budget?

Kill the whole L5 fold-audit if the **mandatory positive control fails**: plant the KNOWN-leaky
single-cut R20 proxy (the exact `hitfn20._heldout_recovery` ¼->¾ mechanism) and require the L5
fresh-population re-audit to FLAG it as < 0.90 catch. If the audit CANNOT detect the leaky proxy it
already knows leaks (33% on disk), the audit instrument is broken and no verdict on L1's seal is
trustworthy — stop and fix the harness before reporting any (a) result. Checkpoint: the very first
positive-control run (single-cut proxy on the fresh population, ~1-2 min).

Sub-attacks (b), (c), (d) are cheap ledger reads / structural checks and run regardless.

---

## Mandatory positive control (plant-prove-recover)

**Plant a known-overfit / leaky proxy = the single-cut ¼->¾ R20 mechanism** (`hitfn20._heldout_
recovery`, the proven-33%-catch instrument). Run it as the "proxy under audit" on the FRESH surrogate
hallucination population. **PASS the control iff the L5 audit flags this planted leaky proxy at
< 0.90 catch on the fresh population** — proving the audit can detect a leaky seal on unseen data
BEFORE it is trusted to clear (or fail) L1's fold seal. Measured catch of the single-cut proxy is
reported as the control's recovery number (doctrine: a null from an unvalidated instrument is not a
negative; state the control's measured recovery).

A second (negative-direction) control: a genuine decode (correct key, English plaintext, true
recovery 1.0) must be ACCEPTED (held-out recovery >= 0.90) by BOTH the single-cut and the fold proxy,
so the audit does not simply reject everything.

---

## Pass / fail thresholds (SET IN ADVANCE, not editable after results)

- **PC (positive control):** single-cut ¼->¾ proxy flagged at **< 0.90 catch** on the fresh
  population (expected ~0.33, matching the on-disk 15/45). If >= 0.90, the fresh population is not a
  valid hallucination population — abort and fix (Q5 kill).
- **(a) verdict FOUND-ERROR** iff L1's frozen fold cell reaches >= 0.90 catch on the tuning-45 but
  **< 0.90 catch on the fresh surrogate population** (overfit). **NO-ERROR-FOUND** iff it holds
  >= 0.90 on BOTH the tuning-45 and the fresh population AND still accepts the genuine decode
  (false-reject <= 0.10). If it fails >= 0.90 on the tuning-45 itself, that is L1's own KILL path,
  reported as such (the seal never sealed).
- **(b) FOUND-ERROR** iff any of the 4 L3/L4 cells is already power-covered per `coverage`;
  **NO-ERROR-FOUND** iff all 4 are named un-measured-at-power in `not_covered`/`coverage`.
- **(c) FOUND-ERROR** iff the fold machinery re-enables screening or multiplies pmax draws or the
  sweeps are screened; **NO-ERROR-FOUND** iff sweeps are unscreened and pmax evaluation per decode is
  unchanged (condition b's 2.5e6 inflation not re-introduced).
- **(d) FOUND-ERROR** iff any L3/L4 row can be a HIT on score/pmax alone (no recovery+held-out gate);
  **NO-ERROR-FOUND** iff every row routes through the recovery-gated `is_hit`.

## Abort authority

If (a) returns FOUND-ERROR (seal overfit), L5 rules that Round 21 HIT auto-certification stays
WITHHELD (survivors flagged-for-oracle, per L1 Q5), and this is recorded BEFORE any L3/L4 negative is
published as a "0.90-power" negative. If (b) finds any cell already power-covered, that cell is
dropped from L3/L4 before its null is reported. Bounds, not verdicts (R7): every result names what
was measured, what was NOT, and the concrete reopening condition.

## Deliverables

- `redteam21.py` — the audit harness (fresh surrogate generator + fold-proxy re-impl + single-cut
  control + the 4 sub-attack checks).
- `out_redteam21.json` — PC recovery, (a) tuning-vs-fresh catch surface, (b) per-cell ledger reads,
  (c) structural FP check, (d) row-gate check, and the four FOUND-ERROR / NO-ERROR-FOUND verdicts.
