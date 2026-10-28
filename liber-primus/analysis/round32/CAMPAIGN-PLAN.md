# Round 32 — INSTRUMENT & RED-TEAM ARMADA (pre-registration / plan of record)

_Drafted 2026-10-28. Binding doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). This is a
pre-registration seed; each lane's own `PREREG.md` is authoritative once written. No lane runs until it
answers the five Aiming-Test questions in writing and its positive control recovers a planted signal._

## 0. Thesis — aim at the instrument, not the space

The doctrine's own evidence table is unambiguous: **every genuinely new result this project has produced
came from auditing a closure, an instrument, an artifact, or an input — zero came from a new key-space
sweep.** Rounds 22–23 read every Phase 1–5 roadmap lens (number channel, koans, self-embedded acrostic,
turtle/coordinate render, printed-line acrostic) — all clean negatives. The roadmap is exhausted at the
tested resolution. What is **not** exhausted is the instrument that produced those negatives, and it has
documented, load-bearing defects. Round 32 attacks those.

Three of these defects mean the repo's standing negatives are narrower than they read, and one means the
doctrine makes a claim about itself that is currently false:

1. **The beam cannot represent `skip_by_two`** — a one-character variant of a plausible 2013 rejection
   loop that *reproduces LP2's observed doublet rate* (0.84% vs 0.664%), scored at −6.903 / 25.8% recovery,
   and beam width 1000 + `max_skip` 8 change that by **exactly 0.000** (`round18/L7-redteam/RESULTS.md` §B.2;
   `ledger.json` line 119). If the true key enciphered under that loop, every sweep in this repo discarded it.
2. **Every historical negative is an English-only negative** (L7-A): measured power at L=120 is 0.33 Latin,
   0.58 OE, 0.42 DE, **0.00 Welsh**, **0.00 vowel-dropped English** under the legacy `src/lp/score.py`
   quadgram scorer. The Round-19 I2 nine-register panel fixes most of this (EN_NOVOWEL 0.00→0.92+, Welsh
   0.00→1.00) — **but no historical negative was ever re-adjudicated through it.**
3. **R3 is not actually CI-enforced.** `ARMADA-DOCTRINE.md` R3 says language-agnostic statistics are
   "CI-enforced (`analysis/handoff/validate_ledger.py`)". The validator checks `positive_control`, thresholds,
   evidence paths, schema, counts — it does **not** call `adjudicate.validate_store` and does not check that
   any sweep row carries the four R3 statistics (`SWEEPROW.md` §7 flags the wiring as a TODO that was never
   done). The doctrine's own load-bearing rule is unenforced.
4. **`threshold_for(segment_len=...)` accepts a `segment_len` argument and silently ignores it**
   (`benchmark/null.py` line 88); the Gumbel constants are a zero-degrees-of-freedom two-point solve with
   SE(β)=20.5%, and β actually scales as L^−0.583. The −5.5 bar was the wrong bar in **14 of 14** historical
   sweeps (`round19/I3/RESULTS.md` §8).

This is a target-rich round, and it is the kind of round that has historically paid off here.

## 1. Doctrine budget allocation (ARMADA-DOCTRINE §3)

| share | goes to | this round's lanes |
|---:|---|---|
| **≈35%** | instrument — power envelopes, adjudicator panels, null recalibration | I1, I2, I3, I4 |
| **≈35%** | high-prior **bounded** lanes (Q3 = enumerable) | B1, B2, B3 |
| **≈20%** | red-team / closure audit (R6) | X1 |
| **≈10%** | completeness rituals / closeout of prior rounds | C1 (folded into X1/B3) |

Instrument share is raised to ≈35% (from the default 30%) because this is explicitly an instrument round and
three defects above gate the trustworthiness of everything else. No new unbounded key space is opened.

## 2. Lane roster

| ID | Type | Title | Compute | Gates on |
|---|---|---|---|---|
| **I1** | instrument | `skip_by_two`/`keyskip2`/free-drift decoder + measured power envelope | light | — (flagship) |
| **I2** | instrument | Re-adjudicate the historical English-only negatives under the I2 nine-register panel | light | I2 panel rebuild |
| **I3** | instrument | Wire R3 into `validate_ledger.py`; implement `threshold_for(segment_len)`; re-derive the null curve | light | — |
| **I4** | instrument | Non-fold oracle-seal proxy; measure catch @ false-reject vs 0.90/0.10 | light | — |
| **B1** | bounded | bash `$RANDOM` full auto-seeded orbit (77.6M), under the repaired instrument | ~30 min | I1 (decoder), I2 (panel) |
| **B2** | bounded | PHP `mt_rand` prior-dense first-fire + stated-fraction tail (highest-prior open generator) | medium | I1, I2 |
| **B3** | closeout | Write up the finished-but-unrecorded R28-L3 sweep; file glibc `gen=0` open row | none/light | — |
| **X1** | red-team | Refute-by-default audit of the repo's own standing claims + bookkeeping fixes | light | — |

## 3. Lanes in detail

Each lane states the five Aiming-Test answers (Q1 recognizer, Q2 evidence prior, Q3 bounded?, Q4 the three
conditionals, Q5 kill-at-10%), then its instrument/control/null/threshold. **All sweep lanes MUST import
`analysis/round19/I2/adjudicate.py` and persist a full `SWEEPROW` per row** (R3). All lanes **write files;
no lane runs `git`** — the coordinator commits after review.

---

### I1 — The `skip_by_two` decoder and its power envelope  _(flagship instrument lane)_

**Why.** The single most consequential unrepresented construction in the repo. `round18/L7-redteam`
established that the beam (`analysis/campaign18_skip/skipdecode.py`, `beam_decode` L98–141) admits a key
skip only when every skipped key position would have reproduced the previous cipher rune — exact for
`encipher_keyskip` (key advances by 1 on rejection) and nothing else. `skip_by_two` (key advances by **2**),
free key drift at q≥0.05, and n≥5 unrepresentable advances per 240 runes are all invisible, and the failure
is a transition-relation failure, not a search-depth one (beam_w 1000 + max_skip 8 → Δ0.000).

- **Q1 (recognizer).** Build `beam_decode_v2` that carries the skip construction as an explicit parameter
  (`advance ∈ {1, 2, free}`). Plant ciphertext under `encipher_skip_by_two` at L=120/400/6000 and prove v2
  recovers ≥0.85 rune-index recovery and clears the register-aware bar. If v2 cannot recover its own planted
  `skip_by_two`, the lane is INVALID, not negative.
- **Q2 (prior).** `skip_by_two` reproduces the observed doublet rate 0.84% vs 0.664% (`ledger.json` line 119) —
  a measured structural match no other rejection loop in the panel achieves. This is a real, cited prior, not lore.
- **Q3 (bounded).** The decoder change is bounded and enumerable (3 advance-relations × existing key families).
  Power measurement is ~hundreds of decodes. No new key space is opened in I1 itself.
- **Q4 (three conditionals).** key space = none opened (instrument only); transition model = **the axis under
  repair**; adjudicator register = use the I2 nine-register panel (coupled to I2), not the English-only scorer.
- **Q5 (kill at 10%).** If the planted `skip_by_two` control does not recover above its L=120 bar with the v2
  decoder, stop — the construction is not beam-representable even with the explicit parameter, and that itself
  is the finding (record it; do not proceed to any re-sweep).
- **Instrument / control / null / threshold.** Decoder = new `beam_decode_v2`; adjudicator = I2 panel;
  null = seed-3301 shuffle at each L; threshold = `round19/I3` contract bar at the adjudicated N, per register.
- **Deliverable.** `round32/I1-skipbytwo-decoder/` — `beam_v2.py`, `PREREG.md`, `power_envelope.json`
  (recovery × score per advance-relation × L × register), `RESULTS.md`. **If and only if** the power envelope
  shows recovery, a *bounded* re-adjudication of the single highest-prior already-swept family (SHA256-CTR
  `seed=CICADA3301`, or the Py2.7-MT pair survivors) under v2 — stated coverage fraction, not exhaustion.

---

### I2 — Re-adjudicate the English-only negatives under the nine-register panel  _(closes L7-A)_

**Why.** The repaired adjudicator already exists (`round19/I2/adjudicate.py`: `adjudicate()`, `to_row()`,
`pmax_ne`, `pcon`; nine registers EN_MODERN/EN_KJV/LP1_REAL/LATIN/OE/DE/CY/EN_HALFVOWEL/EN_NOVOWEL) and the
I2 gate lifted power to ≥0.92 across all non-English registers — but **no prior negative was ever re-scored
through it.** Every published "NEGATIVE" still carries an unstated English-only conditional (L7-A §A.2).

- **Q1 (recognizer).** For each register, plant the correct key over a register-specific plaintext, confirm
  the panel's `pmax_ne` clears the contract bar (reproduce the I2 gate's ≥0.92). Fix the **missing Welsh
  corpus** first: `build_models.py` references `data/keys/welsh/welsh_mabinogion.txt`, which is absent — the
  panel cannot be rebuilt until this is restored or the register is dropped with cause.
- **Q2 (prior).** Direct: L7-A measured the legacy scorer blind to Latin/Welsh/vowel-dropped English; the I2
  panel demonstrably sees them. Re-adjudication is the measurement that converts "English-only negative" into
  a negative with a stated, powered register conditional.
- **Q3 (bounded).** Finite and enumerable: re-score the top-N survivors already stored for B-04, R16-KDF,
  R16-PRNG, R17-PUBLIC-PAD through the panel. No new decodes; this is adjudicator-only.
- **Q4 (three conditionals).** key space = unchanged (re-score existing survivors); transition model =
  unchanged; adjudicator register = **the axis under repair** (9 registers, measured power each).
- **Q5 (kill at 10%).** If the panel rebuild fails its own gate (any register below 0.90 power at L=120),
  fix the panel before re-adjudicating anything; do not report a re-adjudication through an unvalidated panel.
- **Stretch (register gaps).** The only genuine holes in the register axis are **Greek, Hebrew, Norse** (noted
  absent in L7 and R24/C1-ext). Add them if corpora are cheaply available; otherwise record them as the
  panel's stated `not_covered`.
- **Deliverable.** `round32/I2-multiregister-readjudication/` — rebuilt `panel.npz` + gate proof, a table of
  each historical negative's `pmax_ne`/`pcon` under the panel, and either confirmation (negative now carries a
  powered register conditional) or a FLAGGED survivor for the oracle. Updates each affected `LEDGER.json` entry's
  `restated_from`/`not_covered`.

---

### I3 — Make R3 real: CI enforcement + the `segment_len` null  _(instrument hygiene the doctrine already claims)_

**Why.** Two defects that make the repo's stated guarantees untrue. (a) `validate_ledger.py` does not enforce
R3 — `SWEEPROW.md` §7 says to wire `adjudicate.validate_store` in; it never happened. (b) `benchmark/null.py`
`threshold_for()` accepts `segment_len` and ignores it (L88), while β ∝ L^−0.583 and the −5.5 bar was wrong in
14/14 sweeps (`round19/I3`).

- **Q1 (recognizer).** A failing-then-passing test: construct a sweep store missing a required SWEEPROW field,
  prove the new `validate_store` hook in `validate_ledger.py` fails CI on it, then prove a compliant store
  passes. For the null: plant a known family-wise maximum at several L and prove `threshold_for(..., segment_len=L)`
  returns the L-scaled bar, not the L-blind one.
- **Q2 (prior).** Not a discovery lane — it is the enforcement of an existing, cited requirement. Labelled a
  completeness/instrument lane per the doctrine, queued accordingly, but it gates the trustworthiness of B1/B2.
- **Q3 (bounded).** Fully bounded — code + tests, no search.
- **Q4 (conditionals).** N/A (no decode sweep); the deliverable is that future lanes' conditionals become
  machine-checkable.
- **Q5 (kill).** If wiring `validate_store` would fail existing committed stores (pre-R19 rows that legitimately
  have no SWEEPROW), scope the check to lanes that declare a sweep from R19 onward — do not retro-break the
  historical ledger; record the scoping decision.
- **Deliverable.** `round32/I3-r3-enforcement/` — patch to `analysis/handoff/validate_ledger.py` (calls
  `validate_store` for sweep-declaring lanes), patch to `benchmark/null.py` implementing the L^−0.583 scaling,
  a re-derived null curve with >2 calibration points (killing the zero-DOF SE(β)=20.5% solve), `tests/` additions,
  and a note in `ARMADA-DOCTRINE.md` only if the enforcement location changes.

---

### I4 — A non-fold oracle-seal proxy  _(reopens round21/L1 KILL)_

**Why.** The no-oracle auto-certification seal is provably leaky: the disjoint-fold family tops out at 0.80
genuine-safe catch (held-out 0.818 catch / 0.167 false-reject), below the 0.90/0.10 bar (`round21/L1-seal-realmode-proxy/RESULTS.md`). The KILL is explicit that the **fold family alone** is bounded — a non-fold proxy
(longer decrypt head than the 24–32 runes that capped R20-P1, a per-register fold bar, or a learned
self-consistency gate) is untested and could clear 0.90.

- **Q1 (recognizer).** Plant EN_NOVOWEL correct-key overfits (the hallucinations the seal must catch) and
  genuine solved-page decodes (the signal it must not reject); prove the proxy's ROC before trusting it.
- **Q2 (prior).** Cited open door: `round21/L1/RESULTS.md` lines 110–118 names exactly these three non-fold
  families as unmeasured.
- **Q3 (bounded).** Bounded — a handful of proxy designs × the existing planted-hallucination set (45) and
  genuine set (20/66 surrogate).
- **Q4 (conditionals).** key space = N/A; the "register" conditional is explicit (the seal must hold across the
  I2 panel, not just English); transition model = whichever the survivor used.
- **Q5 (kill).** If the best non-fold proxy also fails to reach 0.90 catch at ≤0.10 held-out false-reject,
  record SEAL_PASS=false (unchanged) with the measured ceiling — a bounded negative, not a verdict.
- **Deliverable.** `round32/I4-nonfold-seal/` — proxy implementations, `catch_surface.json` (catch × false-reject
  per design, tuning + held-out surrogate), `RESULTS.md`. If a design clears, auto-certification of a future
  crosser becomes possible; until then every survivor stays flagged-for-oracle.

---

### B1 — bash `$RANDOM` full auto-seeded orbit  _(bounded, enumerable, genuinely never run)_

**Why.** The doctrine's #1 preferred object is an enumerable generator space, and `$RANDOM`'s 77.6M
auto-seeded orbit is enumerable in ~28 minutes and has never been swept (named open in `PICKUP-HERE.md`
§"remaining enumerable families"). It is the cheapest high-prior lane available and ideal for shaking out the
I1 decoder + I2 panel on real compute.

- **Q1 (recognizer).** Reuse I1's planted-key control under `$RANDOM` keystream; confirm recovery before trusting
  the null.
- **Q2 (prior).** A 2013-era `$RANDOM` rejection loop is period-era-plausible and enumerable; the toolchain prior
  (Ubuntu-era GnuPG 1.4.11 box) does not demote bash.
- **Q3 (bounded).** 77,600,000 auto-seeds — fully enumerable, stated coverage 1.00 achievable.
- **Q4 (conditionals).** key space = full `$RANDOM` orbit; transition model = run under **both** keyskip1 and
  (if I1 validates) `skip_by_two`/keyskip2; adjudicator = I2 nine-register panel.
- **Q5 (kill).** If the planted control fails to recover, fix the harness before claiming any coverage.
- **Threshold / null.** `round19/I3` contract bar at the adjudicated N; seed-3301 null; full SWEEPROW per row.
- **Deliverable.** `round32/B1-bash-random/` — `sweep.py`, `PREREG.md`, `sweep_rows.jsonl` (SWEEPROW),
  `RESULTS.md` with coverage × power over both register and construction axes. **RAM note:** fits this laptop
  (~7.35 GB); stream rows to disk, do not hold the orbit in memory.

---

### B2 — PHP `mt_rand` prior-dense first-fire + stated-fraction tail  _(highest-prior open generator)_

**Why.** `ELIMINATION-LEDGER.md` names PHP `mt_rand` "the single highest-prior open generator" (PHP's MT
deviates from reference MT19937 and is unreachable from generator 5); it is the top cell of the never-fired
R28-L4 queue. The **full** 25-cell 2³² sweep is 15–19 days of six-core wall — **out of scope for this laptop.**
B2 runs the bounded, honest subset.

- **Q1 (recognizer).** Plant a PHP-`mt_rand` keystream (both the canonical MT19937 twist and the pre-7.1 broken
  twist) and recover it; the broken twist is the whole point — prove the harness models it.
- **Q2 (prior).** Highest-prior open generator per the ledger; the ImageMagick/Ghostscript toolchain is
  PHP-era-plausible.
- **Q3 (bounded).** Two tiers: (a) prior-dense seeds (dates 2011–2015, 3301-lore, page hashes, semantic) —
  enumerable in minutes; (b) a **stated-fraction** random sample of each 2³² cell with the coverage fraction
  reported honestly (per R3/R7 — no silent truncation). The full tail is explicitly deferred to bigger hardware.
- **Q4 (conditionals).** key space = prior-dense + sampled fraction (stated); transition model = keyskip1 +
  keyskip2 (and skip_by_two if I1 validates); adjudicator = I2 panel.
- **Q5 (kill).** If the prior-dense tier returns nothing and the planted control recovers, proceed to the sampled
  tail only up to the declared fraction, then stop and report coverage — do not drift into an unbounded sweep.
- **Deliverable.** `round32/B2-php-mtrand/` — both-twist harness, control proof, `sweep_rows.jsonl`,
  `RESULTS.md` stating coverage fraction and the deferred remainder (feeds the R28-L4 queue for a future
  bigger-hardware run). **RAM/time note:** cap wall time; this is a first-fire, not the queue.

---

### B3 — Closeout: write up R28-L3; file the open glibc `gen=0` row  _(cheapest open items, little/no compute)_

**Why.** `R28-L3` (string-seed amd64 dictionary) **finished** — all 11 items, 2,500,207 seeds, best pmax
6.3148, no survivors — but has **no `RESULTS.md` and no ledger row**; `PICKUP-HERE.md` calls it "the cheapest
open item." And the glibc `gen=0` full-32 row (`R19-G3-CORRECTION`) is the one still-open glibc generator row
(R21-L4 never ran). These are closeout, not discovery.

- **Q1–Q5.** B3 runs no new sweep for L3 (write-up only); for any glibc `gen=0` first-fire it inherits B1/B2's
  controls and the I2 panel. Kill: if L3's on-disk artifacts are incomplete or its control recovery was not
  stored, downgrade to `inconclusive` rather than filing a negative.
- **Deliverable.** `round32/B3-closeout/` — `R28-L3/RESULTS.md` (control recovery, null, fixed threshold,
  coverage, not_covered) + a `LEDGER.json` entry; and either the glibc `gen=0` prior-dense first-fire or a
  precise `not_covered` statement if deferred.

---

### X1 — Red-team the repository's own claims  _(R6 standing lane; refute-by-default; reports FOUND-ERROR / NO-ERROR-FOUND, never "confirmed")_

**Why.** R6 requires at least one lane per round whose target is the repo's own current claims. The recon
surfaced several unaudited discrepancies. X1 attacks each refute-by-default and fixes the bookkeeping.

Targets (each a sub-finding, each FOUND-ERROR or NO-ERROR-FOUND with a file citation):

1. **Ghostscript version discrepancy.** `round18/L1-toolchain/RESULTS.md` measures the ICC match band as gs
   **9.04**–9.21 (publication-tightened to 9.04–9.14) and excludes 9.00–9.02 by profile size; but
   `round30/A3`, `PICKUP-HERE.md`, and `ELIMINATION-LEDGER.md` all propagate "GS **9.01**–9.15." Determine which
   lower bound the evidence supports and correct the three nav docs.
2. **R27 "coverage 1.00" false-closure read.** `ELIMINATION-LEDGER.md` lines 23–24 read as if the Py2.7-MT 2³²
   space is fully swept; S1 (`pair`) is complete-null but **S2 (`exact`/keyskip1) is at 44.14%** and parked, and
   R28-L4 has zero coverage. Restate the ledger language so S2's partial coverage is not read as closure.
3. **C-CANON-PAYLOAD-3BYTES downstream.** B-04 / R16-KDF / R17 coverage is stated against `canon_256.bin`, but
   the 3 T1/C1-corrected bytes (idx 45/50/246) live in `payload_resolved.bin` and were never promoted. Either
   promote + flag those lanes for re-check, or restate their `not_covered`. (Governance decision surfaced to the
   coordinator, not decided unilaterally.)
4. **Transcription-closed scope.** T1 FAILED its LP1 gate at 95.09% (bar 99%); the "transcription closed three
   ways" claim never says "LP2-typeface-only," and p27:93 (U→B, margin 5) was flagged for human review and never
   resolved. Scope the claim correctly and surface p27:93.
5. **`not_covered: null` hygiene.** Up to 9 ledger rows (R12-A1, E-02, H-03, B-05, B-16, R12-C1, R12-D2, A-03,
   F-01) still carry `not_covered: null` despite real uncovered mass; `R/T1-PATCH-PROPOSALS.md` has the texts,
   proposed but unapplied as of R28. Apply them.
6. **Seal reporting bug + the parked crosser.** The sweep engine's `STATUS.json` hardcodes `flagged_survivors: []`
   while `HIT-CANDIDATE.json` is the real record — a procedural gap where a crosser could go unnoticed. And seed
   **35563892** appears in `run/HIT-CANDIDATE.json` at pmax 7.6707 (above the S2 bar) while `STATUS.json` reads
   `n_claim_bar_hits: 0`. Re-screen seed 35563892 under the `exact` relation and reconcile the two records.
7. **Round 30 D1 bookkeeping.** Confirm the R29-L1 null (24,078 attempts, control passed) is linked and B-10 is
   marked superseded; flag if still a belief-vs-evidence mismatch.

- **Deliverable.** `round32/X1-redteam/RESULTS.md` (one sub-verdict per target, with citations), the applied
  `not_covered` / nav-doc / ledger fixes, and a FOUND-ERROR summary. X1 also runs the standing **completeness
  critic**: "which channel/instrument axis did this round still not read?" — its answer seeds Round 33.

---

## 4. Cross-lane verification (R6) and the hit protocol

- Every lane's positive control must recover its planted signal before its null counts — stated, with the
  measured recovery, in its `RESULTS.md`.
- Any bar-clearing survivor from B1/B2 (or an I1 re-adjudication) is **flagged-for-oracle, never auto-certified**
  (the seal is leaky until I4 clears it), and goes through ≥3 refute-by-default verifiers, each recomputing its
  own false-positive ceiling at its own N (the PA-2 caveat).
- No lane writes "exhausted / closed / solved" (R7). Lanes report coverage × power and `not_covered`.

## 5. Orchestration (how the armada runs)

Structured as a pipeline so instrument repairs flow into the bounded lanes without a global barrier:

- **Wave A (instrument, parallel):** I1, I2, I3, I4. These are independent and light. I2 and I3 touch the
  adjudicator/validator; I1 touches the decoder; I4 touches the seal. ~4 agents.
- **Wave B (bounded, after I1+I2 report):** B1 then B2 (sequential to respect the ~7.35 GB RAM ceiling and keep
  one CPU-bound sweep at a time), B3 in parallel (little compute). B1/B2 import the Wave-A decoder (`beam_v2.py`
  if I1 validated, else keyskip1) and the rebuilt I2 panel. ~3 agents.
- **Wave C (red-team + synthesis):** X1 audits this round's own lanes and the standing claims; a final
  coordinator writes `round32/SYNTHESIS.md`, updates the four nav docs
  (`README.md`, `ELIMINATION-LEDGER.md`, `analysis/README.md`, `PICKUP-HERE.md`) and `LEDGER.json`, and runs the
  pre-commit gate. ~2 agents.

**Agent discipline:** model = Sonnet (cost budget); lanes write files only, **never `git`**; each writes under
its own `round32/<lane>/` dir (no collisions); RAM-safe (stream sweeps to disk); the coordinator reviews
`git status` before any commit and commits **straight to `master`** (no branches — CLAUDE.md). Total ≈9 agents.

## 6. Guardrails — do NOT re-run (ARMADA-DOCTRINE R-mechanics #6)

Query `LEDGER.json` `coverage`/`not_covered` before any decode. Already measured — **off-limits** this round:
the number channel (round11/round22-C), turtle/coordinate render (round22-B), self-embedded & printed-line
acrostics (round22-A/round23), the Py2.7-MT `pair` 2³² space (R27-S1, complete-null), the semantic-seed zoo
(R24/R26-C, 323/323), keytexts rigid (round7), rigid-additive keys, stego/glyph-geometry (round30-A1/A2), hash
preimages, stylometry. Round 32 opens **no** new unbounded space; B1/B2 are enumerable/stated-fraction only.

## 7. Definition of a good Round 32

A good round here is measured by instrument repair and honest bounds, not by a solve:

- I1 delivers a measured power envelope for the `skip_by_two`/drift family (the answer to "would the true key
  have survived our sweeps?").
- I2 converts the repo's English-only negatives into negatives with a stated, powered register conditional (or
  flips one — which would be extraordinary and would go straight to the oracle).
- I3 makes R3 actually CI-enforced and the null segment-length-aware, so every future negative means what it says.
- I4 either opens auto-certification or records the seal's measured ceiling.
- B1 closes bash `$RANDOM` as an enumerable-complete null; B2 fires the highest-prior open generator honestly.
- X1 corrects every surfaced nav-doc/ledger discrepancy and names the next round's target.

All of that is achievable on this hardware except the full PHP/Py2.7 2³² tails, which are explicitly deferred
to bigger hardware as stated-fraction lanes with honest coverage.
