# Round 33 — THE REGISTER-AWARE BEAM (pre-registration / plan of record)

_Drafted 2026-10-29, the morning after Round 32 closed. Binding doctrine:
[`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Seeded by Round 32's completeness critic
([`../round32/SYNTHESIS.md`](../round32/SYNTHESIS.md) §6) and its lane results. This is a pre-registration seed; each
lane's own `PREREG.md` is authoritative once written, and it must be written **before** the lane's first run (Round 32
X1 caught two lanes whose PREREG post-dated their outputs — don't repeat that). No lane runs until it answers the five
Aiming-Test questions in writing and its positive control recovers a planted signal._

## 0. Thesis — the search is still English-only, even though the adjudicator no longer is

Round 32 left exactly one instrument defect with measured mass, and it is the one the doctrine was written about:

> **The panel sees nine registers. The beam searches with one.**

`analysis/round19/I1/driftbeam.py` steers its search by an English quadgram score (`driftbeam.py` L41: "the reported
`score` is the unpenalised quadgram"; the `lam` penalty only prices unexplained key advances). The Round 32 I1 power
envelope (`round32/I1-skipbytwo-decoder/RESULTS.md` §"Failed control") measured what that costs: with the correct
key, the matched relation, and a vowel-dropped-English plaintext, recovery is **0.72 at L=120 and 0.71 at L=400**
(`free`: 0.31 / 0.13). Latin, Old English and German recover at 0.93–1.00 only because their quadgram
statistics happen to overlap English enough to keep the beam on the rails. Abbreviated / vowel-dropped English — the
register Round 18 L7-A singled out as the one where the correct key ranks **below** a deliberately wrong one — still
cannot be searched for. Every negative in the ledger therefore still carries the construction×register hole
"EN_NOVOWEL under any rejection loop", and no key-space sweep can close it because the hole is in the search, not in
the space.

The fix is bounded: one decoder, planted-control gated, measured against the same envelope Round 32 built. That is
the flagship. Everything else in this round is either an input Round 32 flagged as never fed (payload bytes), a
finite human-checkable object (p27:93, the LP1 transcription), a construction axis nobody has planted (resets,
advance ≥3), or the off-repo rendering channel — all bounded, none a new unbounded key space.

**Not a target this round:** the full PHP `mt_rand` / Py2.7-MT 2³² tails (bigger hardware, `R28-L4` queue), any new
generator family, anything in ARMADA-DOCTRINE R-mechanics #6 / Round 32 §6.

## 1. Doctrine budget allocation (ARMADA-DOCTRINE §3)

| share | goes to | this round's lanes |
|---|---|---|
| **≈40%** | instrument — the register-aware beam and its envelope | I1 (flagship), I2 |
| **≈30%** | finite, human-checkable objects and never-fed inputs (R5 rank 1) | B1, B2, B3 |
| **≈20%** | red-team / closure audit (R6) | X1 |
| **≈10%** | closeout rituals carried from Round 32 | C1 (folded into X1) |

Instrument share is raised to ≈40% because the flagship gates the meaning of every bounded lane: a B-lane that
re-adjudicates through a beam that cannot search EN_NOVOWEL inherits the hole.

## 2. Lane roster

| ID | Type | Title | Compute | Gates on |
|---|---|---|---|---|
| **I1** | instrument | Register-aware beam (`beam_decode_v3`): panel-scored search, measured envelope over 9 registers × 3 relations | light–medium | — (flagship) |
| **I2** | instrument | Construction axis beyond {1, 2, free}: per-page / per-line key resets, advance ≥3 — plant, measure, decide representability | light | I1 (uses v3 if it validates, else driftbeam) |
| **B1** | bounded input | Feed `payload_resolved.bin` to the four rows that never saw it (B-04 payload seeds, R17 canon pad, E-01, E-02) | light | owner decision C-CANON (§5) |
| **B2** | finite object | p27:93 human read + LP1 transcription audit (the LP1_REAL register anchors every panel) | none / light | — |
| **B3** | bounded re-adjudication | Re-adjudicate the Round 32 B1/B2 SWEEPROW stores and the I2 survivor lists through v3 (stated coverage, not exhaustion) | medium | I1 validated |
| **X1** | red-team | Refute-by-default audit of this round + the Round 32 carry-overs (B2 unaudited, D5c replication, uncompiled C patch, drafted `not_covered` texts) | light | runs last |
| **O1** | off-repo channel (optional, owner-gated) | Build Ghostscript 9.04–9.14 and byte-compare renders against the 58 LP2 JPEGs | heavy, needs a build box | owner says go |

## 3. Lanes in detail

Each lane states the five Aiming-Test answers (Q1 recognizer, Q2 evidence prior, Q3 bounded?, Q4 the three
conditionals, Q5 kill-at-10%), then its instrument / control / null / threshold. **All sweep or re-adjudication lanes
MUST import the Round 32 I2 panel (`round32/I2-multiregister-readjudication/models/panel.npz`, rebuilt by its
`build_models.py`; corpora via `data/fetch_sources.py --welsh`) and persist a full `SWEEPROW` per row** — R3 is now a
hard validator check (`validate_ledger.py` check 7) and a non-compliant store fails CI. All lanes **write files; no
lane runs `git`** — the coordinator commits after review.

---

### I1 — The register-aware beam  _(flagship instrument lane)_

**Why.** Stated in §0. The beam's transition relation was repaired in Round 19 and measured in Round 32; its *scoring*
was never touched since Campaign XVIII. The adjudicator (`round19/I2/adjudicate.py`, `pmax_ne`) already scores every
register with measured ≥0.92 power; the search just never asks it.

- **Q1 (recognizer).** Build `beam_decode_v3` whose search score is register-aware. Three candidate designs, pre-registered
  in this order, each gated by the same plant:
  1. **panel-max search score** — at each beam step score the partial decode under all nine register LMs and take the
     max (or a soft-max with temperature τ); cheap if the LMs are n-gram tables, which they are.
  2. **register-conditioned beams** — run K parallel beams, one per register (or per register cluster
     {EN_MODERN+KJV+LP1, LATIN, OE, DE, CY, EN_HALFVOWEL, EN_NOVOWEL}), merge by the panel at the end.
  3. **language-agnostic search score** — IoC·N + min-distinct-symbols + compressibility as the beam heuristic (the
     four R3 statistics), with the panel only at the end. This is the design that would also cover an *unknown*
     register.
  Plant the correct key over **each** of the nine registers' held-out text (the I2 panel's `testhalves.npz`) under
  each of the three relations at L=120 / 400, 20 plants per cell (Round 32 I1's grid, so the envelopes are
  directly comparable). Required: EN_NOVOWEL recovery ≥0.90 at L=120 under its matched relation **and** no register
  drops below its Round 32 I1 recovery by more than 0.05. A design that buys NOVOWEL by losing English is not a fix.
- **Q2 (prior).** Measured, with file paths: `round32/I1-skipbytwo-decoder/RESULTS.md` (0.72 / 0.71 / 0.31 / 0.13);
  `round18/L7-redteam/RESULTS.md` §A (correct key ranks below a wrong one under the legacy scorer for vowel-dropped
  English); `round19/I2/RESULTS.md` (panel power ≥0.92 on the same register). The adjudicator can see what the
  search cannot find — that is a measured, not argued, gap.
- **Q3 (bounded).** Fully bounded: 3 designs × 9 registers × 3 relations × 2 lengths × 20 plants ≈ 3,240 decodes
  plus nulls. No key space opened in I1 itself.
- **Q4 (three conditionals).** key space = none (instrument only); transition model = the three Round 19 relations
  (unchanged); adjudicator register = the nine-register panel; **the axis under repair is the search heuristic's
  register** — write the envelope as recovery × score per (design, register, relation, L).
- **Q5 (kill at 10%).** After design 1 at L=120 on EN_MODERN + EN_NOVOWEL only (≈80 decodes): if NOVOWEL recovery
  is still <0.80 **and** design 1 costs more than 3× driftbeam's wall time per decode, drop design 1 and move to 2;
  if all three designs fail the NOVOWEL bar at L=120, STOP — record "EN_NOVOWEL is not beam-searchable with
  n-gram register LMs" as the finding and hand the hole to the ledger as a permanent `not_covered` on every row.
  That is a result, not a failure.
- **Instrument / control / null / threshold.** Decoder = `beam_v3.py`; adjudicator = Round 32 I2 panel; null =
  seed-3301 shuffle of the real LP2 stream at each L (100 decodes per design × L, as Round 32 I1 did); threshold =
  `benchmark/null.py` `threshold_for(N, segment_len=L)` (now L-aware) **and** the hitfn20 `panelmax_bar`, whichever
  binds — state both.
- **Deliverable.** `round33/I1-register-aware-beam/` — `PREREG.md` (dated before any output file), `beam_v3.py`,
  `power_envelope.json` (comparable cell-for-cell with `round32/I1-skipbytwo-decoder/power_envelope.json`),
  `speed.json` (decodes/s per design vs driftbeam — B3's budget depends on it), `RESULTS.md`, `ledger.json`.
  **No re-sweep inside I1.** Re-adjudication is B3's job and only runs if I1 validates.

---

### I2 — Construction axis beyond {1, 2, free}  _(plant it before anyone sweeps it)_

**Why.** Round 32 I1 established that each relation recovers its own construction and mostly only its own (the
diagonal pattern, `power_envelope.json`). Two constructions nobody has ever planted are period-plausible for a hand
or script enciphering across 58 pages: **a key reset per page or per line** (the pad restarts at a page boundary —
exactly what a `for page in pages:` loop does if the keystream object is re-seeded inside it), and **advance ≥3 on
rejection** (`skip_by_two` was a one-character variant; so is `skip_by_three`). The doublet-rate argument that
promoted `skip_by_two` (`round18/L7-redteam/ledger.json` line 119) can be re-run for advance 3–5 in minutes.

- **Q1.** Plant under `encipher_reset_per_page`, `encipher_reset_per_line`, `encipher_skip_by_k` (k=3,4,5) at L=120
  and at **page length** (resets are invisible at L=120 by construction — the plant must span ≥2 pages). Prove the
  existing relations + v3 either recover (≥0.85) or do not; measure the doublet rate of each construction against
  LP2's 0.84%.
- **Q2.** Measured structural prior from the doublet rate — a construction that reproduces 0.84% as well as
  `skip_by_two` does earns a decoder relation; one that does not goes to the queue as a labelled completeness ritual.
- **Q3.** Bounded: 5 constructions × 2 lengths × 20 plants × (existing relations + v3) ≈ 600 decodes.
- **Q4.** key space = none; transition model = **the axis under measurement**; register = EN_MODERN + EN_NOVOWEL
  (the two bracketing registers), full panel for adjudication.
- **Q5.** If no new construction reproduces the doublet rate within 2× of `skip_by_two`'s match, record the
  structural priors and stop — do not build relations for constructions with no evidence prior (R4).
- **Deliverable.** `round33/I2-construction-axis/` — `enciphers.py`, `doublet_priors.json`, `representability.json`
  (per construction: recovered-by {driftbeam relation, v3} or not), `RESULTS.md`, `ledger.json`. If a construction
  earns a relation, the relation ships as a patch proposal against `driftbeam.py` / `beam_v3.py` — **not applied in
  I2**; the coordinator merges after I1's envelope is re-run with it.

---

### B1 — Feed `payload_resolved.bin` to the four rows that never saw it  _(bounded input; owner-gated)_

**Why.** Round 32 X1 §3 (`round32/X1-redteam/RESULTS.md` lines 46–57): `canon_256.bin` and `payload_resolved.bin`
differ at idx 45 (81→107), 50 (21→47), 246 (224→198); R19-C1's independent instrument vouches for the corrected
bytes; B-04's payload-derived seeds, R17's canon pad, and the R16 zeroFP E-01/E-02 tests (`zerofp_tests.py:85,247`)
read `canon_256.bin` directly and E-02's permutation test is single-byte sensitive. Cost is "a handful of seeds, one
pad, two tests". **Runs only after the owner picks Option A** (promote); under Option B it collapses to confirming
X1's restated `not_covered` text is on all four rows.

- **Q1.** For each of the four, re-run the original lane's own harness with the corrected payload as input, with its
  original planted control re-run first; the recognizer is the lane's own, unchanged.
- **Q2.** Measured: three bytes differ and the corrected ones are vouched for by an instrument that was not the
  original transcription. Low probability of flipping anything; near-zero cost; removes a standing unvalidated-input
  caveat on four negatives.
- **Q3.** Enumerable: B-04's payload-derived seed subset (count it from `round8`/B-04 artifacts and state it), one R17
  pad, E-01, E-02.
- **Q4.** key space = the payload-derived subset only; transition model = whatever the original lane used **plus** v3
  if I1 validated (state both); register = Round 32 I2 panel.
- **Q5.** If a lane's original harness cannot be re-run from committed code (missing gitignored input), file that
  row's `not_covered` as "corrected payload: harness not re-runnable" and stop — do not rebuild the lane.
- **Deliverable.** `round33/B1-payload-resolved/` — per-row re-run outputs, `RESULTS.md`, `ledger_patches.json`
  (either `coverage` extended to the corrected payload, or the restated `not_covered`), promotion of
  `payload_resolved.bin` → canonical **only** by the coordinator with the owner's decision cited.

---

### B2 — p27:93 and the LP1 transcription audit  _(finite, human-checkable; R5 rank 1)_

**Why.** The LP1_REAL register anchors every panel (it is half of what "real Liber Primus text looks like" means to
the adjudicator), and T1's pooled read gate **failed** at 95.09% (bar 99%; LP1 recall 94.60%, undiagnosed —
`PICKUP-HERE.md` ~line 454). p27:93 (U→B, margin 5) was flagged for a human in Round 28 and is still unresolved. Both
are objects a person can settle at a desk.

- **Q1.** For p27:93: a render crop at 400 dpi, the two candidate glyphs side by side, the five-rune context, and the
  transcription's own confidence — the recognizer is a human eye, and the deliverable records what it saw. For the
  LP1 audit: re-run T1's read gate on LP1 only, bucket the 5.4% misses by page/glyph, and present the top-20 lowest
  margin cells the same way.
- **Q2.** Measured: a failed gate and an unresolved flag. The prior that this *changes a verdict* is low; the prior
  that it changes the panel's LP1_REAL model is non-trivial if the misses cluster.
- **Q3.** Finite: 1 + ≤20 cells.
- **Q4.** N/A — no decode sweep. If any LP1 cell changes, the lane re-fits LP1_REAL and re-runs the Round 32 I2 gate
  (`power.py`, L=120) to state the new power.
- **Q5.** If the T1 harness cannot reproduce the 95.09% figure from committed code, stop and file that — the audit
  cannot proceed on an unreproducible gate.
- **Deliverable.** `round33/B2-lp1-audit/` — `p27_93.md` (with crops), `lp1_misses.json`, `RESULTS.md`, and if the
  panel changed, a rebuilt `panel.npz` + gate proof.

---

### B3 — Re-adjudicate the Round 32 stores through v3  _(bounded; gates on I1)_

**Why.** Round 32 B1 (192,066 rows) and B2 (212,218 rows) persisted full SWEEPROW stores — the first bounded sweeps in
this repo that can be *re-interpreted* without re-running (R3's whole point). Their prefilter was a nine-register
trigram screen (power 0.47–0.74 on planted keys, **0.47 on EN_NOVOWEL**); their beam was driftbeam. If v3 validates,
re-decoding the stored survivors (not the orbits) through v3 is cheap and closes the NOVOWEL hole on those two
negatives at the survivor level. The Round 32 I2 survivor lists (B-04 225, R16-KDF 48, R16-PRNG 20, R17 5,730) get
the same treatment.

- **Q1.** Reuse I1's planted controls through the real B1/B2 chunk path with v3 substituted; ≥3 recoveries per cell
  before any null counts.
- **Q2.** Measured: the stores exist, the prefilter's NOVOWEL power is 0.47, and v3 (if validated) is the first beam
  that can search that register.
- **Q3.** Enumerable: the survivor rows already on disk (≈404k) — at v3's measured decodes/s (`I1/speed.json`), state
  the fraction that fits a 45-minute wall cap and sample uniformly (seed 3301) if it does not all fit. **Never the
  orbits.**
- **Q4.** key space = the stored survivors only (coverage stated as a fraction of the original store); transition
  model = keyskip1 + keyskip2 under v3; register = full panel, with v3's measured NOVOWEL power stated.
- **Q5.** If I1 did not validate, B3 does not run; file "v3 not validated — stores retain driftbeam-only search".
- **Deliverable.** `round33/B3-v3-readjudication/` — `readjud_rows.jsonl` (SWEEPROW), `RESULTS.md`, `ledger_patches.json`
  extending the R32-B1 / R32-B2 / I2-restated rows' `coverage` with the v3 construction×register cell.

---

### X1 — Red-team this round and the Round 32 carry-overs  _(R6 standing lane; refute-by-default)_

Targets, each FOUND-ERROR / NO-ERROR-FOUND with a file:line citation:

1. **Round 32 B2 was filed by the coordinator and never independently audited** (`round32/SYNTHESIS.md` §4). Re-check
   its `control.json` (48/48), its legacy-twist self-test (checked against php 8.5.4 `MT_RAND_PHP`, **not a PHP 5
   binary** — find or build a PHP 5.x reference value for `mt_srand(1); mt_rand()` and compare), and its 0.970%
   coverage arithmetic.
2. **I4's D5c seal candidate** (`round32/I4-nonfold-seal/RESULTS.md` lines 15–21, 97): replicate on a *third* clean key
   and a second length. It was frozen at `m_NV = 14.0128` for L=240 and rejects 92/92 correct decodes at L=120.
   Verdict stays SEAL_PASS=false unless ≥4 lengths calibrate; X1 only reports the replication.
3. **The uncompiled C patch** (`round27/P1-engine/grind27.c`, `round28/L4/grind28.c`): if a compiler is available on
   the run box, build and run the resume path against the parked S2 state; otherwise FOUND-ERROR stays "unbuilt" and S2
   must not resume.
4. **The eight `not_covered` texts tagged `[X1/R32 draft text]`** and the five Round 30 rows still `null`
   (R30-A1/A2/B1/B2/C1): confirm or rewrite, then make `validate_ledger.py` **warn** on `not_covered: null` for
   `negative` rows from Round 19 onward (a warning, not an error — the Q5 scoping decision from Round 32 I3 applies).
5. **This round's own lanes**, as Round 32 X1 did: PREREG dates vs output dates, RESULTS claims vs JSON, patches vs
   doctrine vocabulary, and — specifically — whether I1's envelope is *cell-for-cell comparable* with Round 32 I1's
   (same plants, same nulls, same bars) or merely looks it.
6. **Completeness critic** for Round 34.

- **Deliverable.** `round33/X1-redteam/RESULTS.md`, applied fixes, `ledger.json`, the validator patch (if #4 lands),
  and the Round-34 seed list.

---

### O1 — The rendering channel (optional; owner-gated; off this laptop)

`round18/L1-toolchain/RESULTS.md` §4 and line 201: the ICC profile is byte-identical across **gs 9.04–9.21**, and
Round 32 X1 corrected the nav docs to 9.04–9.14 (publication-tightened). Nobody has yet built those releases and
rendered the recovered PS/PDF chain to byte-compare against the 58 LP2 JPEGs. It is the one channel that could pin the
exact toolchain, and it needs a Linux build box with ~2 GB RAM per build and ghostpdl tags checked out — **not this
machine**. If the owner has a box: `round33/O1-gs-render-compare/` with a PREREG that names the recognizer (byte match
of the render pipeline output vs the JPEG's decoded planes at the measured quality factor) before any build. Otherwise
it stays queued with that PREREG written and no compute spent.

## 4. Cross-lane verification (R6) and the hit protocol

- Every lane's positive control must recover its planted signal before its null counts — stated, with the measured
  recovery, in its `RESULTS.md`.
- Any bar-clearing survivor from B1/B3 is **flagged-for-oracle, never auto-certified** (SEAL_PASS is false; D5c is a
  candidate, not a seal), and goes through ≥3 refute-by-default verifiers each recomputing its own false-positive
  ceiling at its own N.
- No lane writes "exhausted / closed / solved" (R7). Lanes report coverage × power and `not_covered`.
- I1's envelope and Round 32 I1's envelope must be **cell-for-cell comparable** (same plant texts, same seeds, same L,
  same null size). Any deviation is stated in I1's PREREG before the run.

## 5. Owner decisions that gate lanes (decide before launch, or the lane is skipped with cause)

1. **C-CANON-PAYLOAD-3BYTES** — Option A (promote `payload_resolved.bin`) runs B1 in full; Option B collapses B1 to a
   bookkeeping check. Both texts are in `round32/X1-redteam/RESULTS.md` §3.
2. **O1** — is there a build box? If not, O1 is PREREG-only.
3. **The drafted `not_covered` texts** — X1 #4 will confirm-or-rewrite; if you want to hand-edit any first, do it before
   X1 runs.

## 6. Orchestration

- **Wave A (parallel, ~3 agents):** I1 (flagship), I2, B2. All light; I2 and B2 touch nothing I1 touches.
- **Wave B (after I1 reports, ~2 agents):** B3 (only if I1 validated; one CPU-bound job at a time on this laptop),
  B1 (only if Option A; light). If I2 earned a new relation, I1 re-runs its envelope with it **before** B3 starts.
- **Wave C (~2 agents):** X1 audits everything above plus the Round 32 carry-overs; the coordinator writes
  `round33/SYNTHESIS.md`, applies ledger patches, updates the four nav docs, runs the gate
  (`tests/validate.py`, `pytest tests/ benchmark/`, `validate_ledger.py`), commits straight to `master`.

**Agent discipline (unchanged from Round 32, with two additions):** model = Sonnet; lanes write files only, never
`git`; each under its own `round33/<lane>/`; RAM-safe — this laptop has ~7 GB with well under 1 GB free, one Python
process per lane, `nproc=1`, stream to disk, **no filesystem-wide `find`** (three Round 32 lanes had whole-disk
searches killed by memory pressure); **PREREG.md is written and dated before the first output file exists**. Total ≈7
agents.

## 7. Guardrails — do NOT re-run (ARMADA-DOCTRINE R-mechanics #6)

Query `LEDGER.json` `coverage`/`not_covered` before any decode. Off-limits this round: everything in Round 32 §6; the
bash `$RANDOM` orbit and PHP `mt_rand` tiers as swept (R32-B1/B2 — B3 re-adjudicates their *stores*, it does not
re-sweep); the Round 32 I2 survivor re-score under driftbeam (done — B3 re-does it under v3 only); the full Py2.7-MT
S2 tail (parked at 44.14%, and the engine patch is unbuilt). Round 33 opens **no** new key space.

## 8. Definition of a good Round 33

- I1 either delivers a beam whose EN_NOVOWEL recovery is ≥0.90 at L=120 with no register losing more than 0.05, **or**
  records that the register is not beam-searchable with n-gram LMs — either way the construction×register table in
  every negative becomes a measured cell instead of a hole.
- I2 states a measured structural prior (doublet rate) for resets and advance ≥3, and the repo knows which of them its
  decoders can represent.
- B1/B2 retire two standing caveats (unfed corrected payload; failed LP1 read gate) with finite work.
- B3 converts the two best-instrumented negatives in the repo into negatives with a stated NOVOWEL-searchable cell.
- X1 closes the Round 32 carry-overs or says precisely why each stays open.

A survivor would be extraordinary and goes straight to the oracle protocol. The round is a success without one.
