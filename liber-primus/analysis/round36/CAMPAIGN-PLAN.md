# Round 36 — THE MISSING REGISTERS, THE NEW GATE, AND THE PARKED SWEEP (pre-registration / plan of record)

_Drafted 2026-10-30 as Round 35 closed. Binding doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Seeded
by Round 35 X1's completeness critic and [`../round35/SYNTHESIS.md`](../round35/SYNTHESIS.md) §6. Each lane's
`PREREG.md` is authoritative once written and is dated before its first output (addenda in a separate dated file)._

## 0. Thesis — the last unmeasured register axis, and the one sweep that has an engine but no gate

After Round 35 the bash orbit is a negative at reach 0.95–0.99 *across the nine registers the panel has*. Round 18 L7-A's
lesson is that every register the panel lacks is a silent hole in every negative, and three plausible registers have
been absent since Round 32 flagged them: **Greek, Hebrew and Norse** (`round32/I2-multiregister-readjudication/
RESULTS.md` "Not covered"; `round35/X1-redteam/RESULTS.md` Round-36 #1). Adding them is bounded (corpora are public
domain, the build and gate machinery exist, power is measured by planting), and because Round 35 B1 persisted its
276,242 survivor rows, re-adjudicating the whole orbit under a 12-register panel is a re-score, not a re-sweep.

The second item is governance with a measured recognizer. The Py2.7-MT S2 sweep (`exact` relation, 44.14 % of 2³²)
has a verified engine (Round 34 S1: compiles clean, 4/4 resume tests) and an unrebuildable gate (Round 35 P1: the Welsh
corpus is lost). The honest route is to **re-gate the engine on a new panel whose build is recorded end to end** —
corpus URLs, hashes, build parameters, panel hash — so that the gate is reproducible from a fresh clone, which the
original never was. That is a change to what "the panel" means and is recorded as such in the ledger; it is not a
substitution smuggled in. If the self-test passes on the new gate, S2 advances for a capped window on the sandbox.

Two smaller bounded items close Round 35 gaps: pf_v4's power was measured on bash LP64 keystreams only (ILP32 and PHP
unmeasured), and the PHP uniform tier never ran awake with rows persisted; and the seal needs its one remaining
candidate (separate NOVOWEL / HALFVOWEL margins) tested under pre-registration on independent keys.

**Not a target this round:** new generator families; PHP 2³² tails beyond the awake ~1 % tier; ≥3-skip heads (≈3 %
of mass); the O1 text-page bisect (no page-0 source).

## 1. Doctrine budget allocation

| share | goes to | lanes |
|---|---|---|
| **≈35%** | instrument — three new registers + 12-register panel power; pf_v4 power on the other keystreams | I1, I2 |
| **≈35%** | bounded — re-adjudicate the persisted orbit under 12 registers; PHP tier awake; S2 window | B1, B2, S1 |
| **≈15%** | the recorded gate (governance + build) | P1 |
| **≈15%** | seal successor + red-team | I3, X1 |

## 2. Lane roster

| ID | Type | Title | Compute | Gates on |
|---|---|---|---|---|
| **I1** | instrument (flagship) | Greek / Hebrew / Norse registers: corpora with recorded hashes, 12-register panel, power gate ≥0.90 per register at L=120/240 | light–medium | — |
| **B1** | bounded re-score | Re-adjudicate the 276,242 persisted R35-B1 rows through the 12-register panel (pmax_ne per register; bars from a 12-register null) | medium | I1 |
| **I2** | instrument | pf_v4 power on ILP32 and PHP keystream plants (natural rate); frozen thresholds unchanged | light | — |
| **B2** | bounded | PHP `mt_rand` uniform tier re-run AWAKE under pf_v4 + v3, ~1 % of 2³² per cell, rows persisted; prior-dense tier unfiltered this time | ~40 min | I2 |
| **P1** | gate (governance) | Build "panel-R36": the nine current registers + I1's three, every input hash recorded, build script + parameters + panel hash committed; re-point the engine's `engine.dat` gate at it in a COPY; document the governance change | light | I1 |
| **S1** | build box | Sandbox: build the fixed engine, self-test against panel-R36 (V1 64/64, V2 to 4 dp), resume-restore test on a copy, then resume the live S2 for ≤60 min sandbox wall; leave it resumable | sandbox | P1 |
| **I3** | instrument (small) | D5c successor: separate NOVOWEL and HALFVOWEL margins, each a frozen per-L table from Round 34/35 feature files, tested on two INDEPENDENT new keys (different sum(key) mod 997 classes) at L ∈ {150, 240, 300} | light | — |
| **X1** | red-team | This round + carry-overs; last | light | — |

## 3. Lanes in detail

All adjudication uses the panel named per lane; all stores are SWEEPROW; no lane runs `git`.

---

### I1 — Greek, Hebrew, Norse  _(flagship instrument lane)_

- **Q1.** For each new register: a public-domain corpus (e.g. Perseus/Gutenberg Greek NT or LXX in a romanised or
  rune-mappable form, Hebrew Tanakh transliterated, Old Norse sagas from heimskringla.no / Gutenberg) with URL and
  sha256 recorded in `fetch_log.json`; a stated, deterministic mapping from the corpus alphabet onto the 29-rune
  Gematria Primus alphabet (this mapping IS the register — document it; Round 32 I2's `build_models.py` shows how the
  existing registers map); trigram LM built with `build_models.py`'s machinery; held-out halves. Power gate exactly as
  Round 32 I2 (`power.py`, nproc=1, reduced null): planted correct key over held-out text at L=120 and L=240, required
  ≥0.90 `pmax` power per register (target 0.92), and **no existing register loses >0.02 power** when the panel grows
  to 12 (the panel-max statistic changes with more registers — measure the nine again).
- **Q2.** `round18/L7-redteam/RESULTS.md` §A: every uncovered register is a silent hole; Round 32 I2 and Round 35 X1
  name these three as the only plausible ones still missing. Prior for the plaintext being Greek/Hebrew/Norse is low
  but non-zero (Cicada's own corpus quotes all three traditions); the cost is one lane.
- **Q3.** Bounded: 3 corpora, one build, 12 × 2 power cells.
- **Q5.** A register that cannot reach 0.90 at L=120 after one mapping revision is recorded at its measured power and
  kept **out** of the panel (do not weaken the gate); say which mapping was tried.
- **Deliverable.** `round36/I1-new-registers/` — `fetch_log.json`, `mappings.md`, `build_models_r36.py` (or a patch to
  the Round 32 copy), `models/panel12.npz` (gitignored; build reproducible), `gate_proof.json` (12 registers × 2 L),
  `RESULTS.md`, `ledger.json`.

---

### B1 — The persisted orbit under 12 registers  _(bounded re-score)_

- **Q1.** Planted-key controls per new register through the stage-2 path (v3 decode with the key handed over + 12-panel)
  at L=120, ≥5 plants each, plus the Round 35 B1 natural-rate control re-scored under the 12-panel (must still pass).
- **Q2.** The rows exist (`round35/B1-bash-orbit-pfv4/sweep_rows.jsonl`, 276,242) and were adjudicated by nine
  registers; the three new ones were not read.
- **Q3.** Enumerable: 276,242 rows; re-scoring the stored decodes needs the stored texts — if the rows hold only
  statistics (SWEEPROW does not store the decode), re-decode the survivor seeds under v3 (two relations, ~140 k decodes,
  ≈25 min) and adjudicate with the 12-panel. State which.
- **Null / bar.** A 12-register shuffled-LP2 null at L=120 for both relations (≥20,000 draws; `bars_v3` machinery
  refit — the panel-max statistic's null shifts with 12 registers); report the bar at actual N and N=1e6.
- **Q5.** Any row clearing the 12-register bar → L=240 re-screen → flagged-for-oracle; near-misses listed.
- **Deliverable.** `round36/B1-orbit-12reg/` — `readjud_rows.jsonl`, `null12.json`, `control.json`, `RESULTS.md`
  (per-register reach incl. the three new ones), `ledger_patches.json` (R35-B1 extension).

---

### I2 — pf_v4 power on the other keystreams  _(small instrument lane)_

- **Q1.** Natural-rate plants (real encipherer, no selection) under bash ILP32 and each PHP cell (mt_scale, mt_mod,
  php_scale, php_mod), 500 per register for EN_MODERN, EN_NOVOWEL, EN_HALFVOWEL, LATIN; frozen pf_v4 thresholds
  (`round35/I1-skip-tolerant-screen/frozen_op.json`); report power per (generator, register, relation) and the
  skip-free / with-skip split.
- **Q5.** Any (generator, register) under 0.85 → B2 states that cell's reach honestly; thresholds are NOT re-tuned.
- **Deliverable.** `round36/I2-pfv4-keystreams/` — `power_by_generator.json`, `RESULTS.md`, `ledger.json`.

---

### B2 — PHP tier, awake, rows persisted  _(bounded)_

- **Q1.** Round 35 B1's natural-rate control pattern per PHP cell × relation (≥10 EN_MODERN + ≥10 EN_NOVOWEL).
- **Q2.** Round 34 B1's PHP uniform tier was cut to 0.061 % by a laptop sleep and its rows were lost (R35 X1 1b/1c).
- **Q3.** Prior-dense 48,036 seeds decoded **unfiltered** (so reach = v3 recovery) + uniform `default_rng(3301)` sample
  of ≥1 % of 2³² per cell (≈43 M seeds, pf_v4 at 56.6 k heads/s ≈ 13 min per cell) — cap 60 min total, stated fraction.
- **Deliverable.** `round36/B2-php-awake/` — `sweep_rows.jsonl` (persisted; opened in APPEND mode on any resume),
  `RESULTS.md`, `ledger_patches.json` (R32-B2 / R34-B1 extension).

---

### P1 — panel-R36: the recorded gate  _(governance + build)_

- **Q1.** Recognizer: a fresh clone can run `build_models_r36.py` and reproduce `panel12.npz` byte-exact from the
  recorded corpus hashes (prove it by building twice into separate dirs and comparing). Then, in a COPY of the engine's
  input set, re-point `engine.dat`'s panel hash at panel-R36 and record the diff.
- **Q2.** Round 34 S1 (engine verified, gate unrebuildable); Round 35 P1 (Welsh lost). The original gate was never
  reproducible from a clone; this one is.
- **Q3.** Bounded: one build, one config diff.
- **Governance record.** `GATE-CHANGE.md`: what the Round 19 panel was, why it cannot be rebuilt, what panel-R36 is,
  how to reproduce it, and the explicit statement that S2 results after the re-gate are adjudicated by panel-R36, not
  the Round 19 panel. Ledger: a new row `R36-P1-PANEL-R36-GATE` and a note on `R27-CPORT-MT32-FULLSWEEP`.
- **Deliverable.** `round36/P1-panel-r36/` — `GATE-CHANGE.md`, `build_twice.json`, `engine_config_diff.txt`,
  `RESULTS.md`, `ledger.json`. The live engine inputs are **not** modified on the laptop; S1 applies the diff on the
  sandbox copy.

---

### S1 — S2 window on the sandbox  _(gates on P1)_

- **Q1.** Build the fixed `grind27.c` (`round34/S1-build-box/BUILD.md`), upload panel-R36 + the re-pointed
  `engine.dat`, run `--self-test`: must pass V1 64/64 and V2 to 4 dp. Resume-restore test on a copy (Round 34 S1's
  (a)/(a2)/(b)). Then resume the **live** S2 state for ≤60 min sandbox wall, snapshot STATUS/HIT-CANDIDATE before and
  after, report the new coverage fraction from 44.14 %, any claim-bar hits (→ flagged-for-oracle, re-screened under v3
  at L=240 locally with the 12-panel), and leave the state resumable. Download the updated state files to
  `round36/S1-s2-window/state_after/` so the next resume has them.
- **Q5.** Self-test fails → stop; record both panel hashes and the V1/V2 numbers; S2 stays parked.
- **Deliverable.** `round36/S1-s2-window/` — `BUILD.md`, `selftest.json`, `resume_window.json`, `state_before/`,
  `state_after/`, `RESULTS.md`, `ledger_patches.json`.

---

### I3 — D5c successor  _(small; pre-registered)_

- **Q1.** Freeze in PREREG, before any decode: two margin tables read from the Round 34/35 feature files — `m_NV(L)`
  and `m_HV(L)` at L ∈ {150, 240, 300} as the per-L value that gave ≥0.90 catch at ≤0.10 FR on the *existing* data
  (state the numbers) — then test on two NEW keys in different `sum(key) mod 997` classes (state the classes),
  sample sizes fixed from Round 35 yields. Pass: at every L, ≥0.90 catch per hallucination class, pooled FR ≤0.10,
  Wilson upper ≤0.10 on NV-only and HV-only genuine.
- **Q5.** Any failure → SEAL_PASS stays false, ceiling recorded, the lane recommends stopping seal work for a round.
- **Deliverable.** `round36/I3-d5c-two-margin/` — `PREREG.md`, `results.json`, `RESULTS.md`, `ledger.json`.

---

### X1 — Red-team  _(last)_

Targets: (1) I1's alphabet mappings (are they deterministic and documented? does the panel-max statistic's change
shift the nine existing registers' power?); (2) B1's re-score path (stored stats vs re-decode) and its 12-register
null; (3) P1's build-twice proof and the governance record; (4) S1's self-test numbers, window arithmetic, and that the
live S2 state is left resumable with the after-state saved; (5) B2's append-mode store (the Round 34 failure); (6)
I3's PREREG mtime and key independence; (7) apply audited patches, run the gate, Round 37 critic list.

## 4. Verification and hit protocol
As Rounds 32–35. Any crosser (B1, B2, S1) is flagged-for-oracle (SEAL_PASS=false), re-screened at L=240 under v3 with
the 12-panel, and sent to ≥3 refute-by-default verifiers each recomputing its own ceiling.

## 5. Owner-only items (recorded, not blocking)
- The S2 re-gate is a governance change. It is recorded in `GATE-CHANGE.md` and the ledger before any resume; the
  window is capped and the state left resumable. If the owner would rather keep S2 parked under the lost gate, delete
  the S1 lane; P1 and I1 stand on their own.
- Sandbox snapshot; stale PRs #7–#10; the stray `round29/L4-image-forensics/fingerprints.json`.

## 6. Orchestration
- **Wave A (parallel, ~4 agents):** I1, I2, I3, and P1's governance doc + build harness (P1 completes after I1).
- **Wave B:** B1 (after I1), B2 (after I2), P1 build (after I1), then S1 (after P1). One laptop process at a time
  for B1/B2; S1 is remote.
- **Wave C:** X1; coordinator closeout.
Discipline unchanged: Sonnet; no `git` in lanes; own `round36/<lane>/` dir; nproc=1; stream to disk; stores opened in
APPEND mode on resume; no `find /`; PREREG dated before first output; write RESULTS.md and ledger.json before replying.

## 7. Guardrails — do NOT re-run
Everything in Rounds 32–35 §6/§7; the bash orbit under nine registers (R35-B1 — B1 here re-scores under 12, it does
not re-sweep); the Round 34 I1 null cells (B1 refits a 12-register null only).

## 8. Definition of a good Round 36
The panel reads twelve registers with measured power and the bash orbit's negative carries all twelve; S2 either
advances under a gate a stranger can rebuild, or the repo states exactly why not; pf_v4's power is known on every
keystream it screens; the PHP tier has persisted rows at a stated awake fraction; the seal's last candidate is tested
under pre-registration. A survivor would be extraordinary; the round succeeds without one.
