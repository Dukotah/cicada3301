# Round 34 — CLOSE THE LOOP: v3 at sweep scale, the build box, and the two promotions (pre-registration / plan of record)

_Drafted 2026-10-29, as Round 33 closed. Binding doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md).
Seeded by Round 33 X1's completeness critic ([`../round33/X1-redteam/RESULTS.md`](../round33/X1-redteam/RESULTS.md))
and the Round 33 synthesis. Pre-registration seed; each lane's `PREREG.md` is authoritative once written and
**must be dated before its first output file** (X1 checks mtimes)._

## 0. Thesis — the instrument is repaired; now run the repaired instrument where the holes were

Rounds 32–33 did what the doctrine asked: the beam now searches all nine registers (Round 33 I1: EN_NOVOWEL recovery
0.72 → 1.000 with no register losing >0.012), R3 is CI-enforced, the null is segment-length-aware, and the two
best-instrumented negatives in the repo (R32-B1 bash `$RANDOM`, R32-B2 PHP `mt_rand`) were re-adjudicated through v3
at the survivor level with nothing flagged (Round 33 B3). But three measured gaps remain, and each is a bounded job:

1. **The orbits were never searched for vowel-dropped English.** R32-B1/B2's prefilter had EN_NOVOWEL power 0.47
   (`round32/B1-bash-random/prefilter_power_trigram.json`), so end-to-end NOVOWEL reach on those two negatives is
   ≈0.28–0.47 even after B3 (`round33/B3-v3-readjudication/RESULTS.md` §"v3 power"). The register the whole repair
   was for is still the register those two sweeps are weakest on. A NOVOWEL-aware prefilter + v3 over the *orbits*
   closes that, and it is enumerable (77.6M + 41.7M seeds already enumerated once).
2. **v3 has no null of record.** B3's 8.55 / 8.37 bars are a peaks-over-threshold fit extrapolated ~10× past a
   12,000-draw null (`null_v3.json`); the hitfn20 bars do not transfer (Round 33 I1 §"Bars and null"). Every future
   v3 sweep needs an observed, register-matched null at its N, with a Gumbel fit over ≥4 lengths.
3. **Three things cannot be built on this laptop** and have been "unbuilt" for two rounds: the fixed `grind27.c` /
   `grind28.c` resume path (S2 is parked at 44.14 % behind it), a PHP 5 binary to verify the legacy-twist reference
   value, and Ghostscript 9.04–9.14 for the render byte-compare (O1). A Linux sandbox solves all three in one lane.

Plus two promotions that were decided and then correctly stopped: `payload_resolved.bin` (owner chose Option A
2026-10-29; Round 33 X1 found five more readers of `canon_256.bin` and the capsule manifest hash) and the D5c seal
candidate (holds at L=240 on three clean keys, fails at L=120 — needs `m_NV(L)` over ≥4 lengths).

**Not a target this round:** any new generator family or key space; the Py2.7-MT S2 resume itself (the engine must
be built and tested first — that is this round's S1 lane, the resume is Round 35's if S1 passes).

## 1. Doctrine budget allocation (ARMADA-DOCTRINE §3)

| share | goes to | lanes |
|---|---|---|
| **≈35%** | instrument — v3 null of record, NOVOWEL-aware prefilter envelope, D5c calibration | I1, I2 |
| **≈35%** | bounded, enumerable — the two orbits under v3 (flagship compute) | B1 |
| **≈15%** | build box — compile, test, cross-check what the laptop cannot | S1 |
| **≈15%** | promotions + red-team | P1, X1 |

## 2. Lane roster

| ID | Type | Title | Compute | Gates on |
|---|---|---|---|---|
| **I1** | instrument | v3 null of record: observed, register-matched, Gumbel over L ∈ {31, 120, 240, 400}, both relations | medium | — |
| **I2** | instrument | NOVOWEL-aware prefilter (panel-max trigram screen) + its measured power envelope per register | light | — |
| **B1** | bounded (flagship compute) | R32-B1 bash orbit + R32-B2 PHP tiers re-screened with the I2 prefilter, survivors through v3, under the I1 null | heavy for this laptop — stated-fraction with a hard cap | I1, I2 |
| **S1** | build box | Linux sandbox: build + test fixed grind27/28 resume path against the parked S2 state; PHP 5.x `mt_srand(1); mt_rand()` reference; gs 9.04 + 9.14 render of page 0 (O1's Q5 kill test) | sandbox | sandbox available |
| **P1** | promotion | Re-feed `payload_resolved.bin` to R16-KDF (via B-04 seeds), R30-B1, R30-B2, recon `h1_index`, campaign18 payload scripts; regenerate capsule `MANIFEST.json`; then promote with `canon_256_superseded.bin` kept | light | — |
| **I3** | instrument (small) | D5c `m_NV(L)` calibration on ≥4 lengths × 2 recipes; SEAL verdict stays false unless all four calibrate | light | — |
| **X1** | red-team | Refute-by-default on this round + carry-overs (B3 audit, I2's queued relations, the 13 capsule INTACT-FAIL items) | light | last |

## 3. Lanes in detail

All sweep lanes import v3 (`round33/I1-register-aware-beam/beam_v3.py`, design `panel_max`, `lam_u=4`) and the Round
32 I2 panel, persist SWEEPROW rows (check 7 fails CI otherwise), and write files only — **no lane runs `git`**.

---

### I1 — v3 null of record  _(instrument; everything v3 reports a bar against)_

- **Q1.** Recognizer = a planted correct key at each L clears the fitted family-wise bar at N = 10⁶ in ≥19/20 seeds
  for every register (the Round 33 I1 envelope already shows planted `pmax` clearing B3's provisional bars 20/20;
  this lane makes the bar observed rather than modelled).
- **Q2.** Measured: `round33/B3-v3-readjudication/null_v3.json` — 12,000 draws, tail extrapolated ~10×; Round 33 I1
  shows v3's null max rises because the search optimises the statistic the adjudicator reads (free/L=400: 8.60 →
  13.03 at N=100). An instrument whose bar is modelled, not observed, is the Round 19 I3 defect again.
- **Q3.** Bounded: 4 lengths × 2 relations (keyskip1, keyskip2; `free` at L=120 only, it is 30× slower) × ≥40,000
  shuffled-LP2 draws, keys drawn round-robin from the six families B3 used **plus** register-matched shuffles (shuffle
  a NOVOWEL / Latin / OE held-out text, not only LP2) so the null is matched to the register the panel argmaxes.
  Wrong-key v3 runs ~180 decodes/s at L=120 → ≈4 min per 40k cell at L=120, ~15× that at L=400. Cap: 90 min total;
  if L=400 does not fit, state the L=400 bar as fitted-from-three and say so.
- **Q4.** N/A (no sweep); the deliverable is that every future v3 negative's bar is observed at its L and N.
- **Q5.** If the Gumbel fit's β exponent across L disagrees with Round 32 I3's −0.55 ± 0.04 by more than 3 SE,
  stop and report — the v3 statistic may not be Gumbel-tailed and B1 must use the empirical quantile instead.
- **Deliverable.** `round34/I1-v3-null/` — `null_cells.json`, `fit.json` (mu(L), beta(L), exponent ± SE, both
  relations), a `bar_v3(N, L, relation)` function in `bars_v3.py` that B1 imports, `RESULTS.md`, `ledger.json`.

---

### I2 — NOVOWEL-aware prefilter  _(instrument; the gate B1 screens through)_

- **Q1.** Replace R32-B1's nine-register *trigram* screen on the first 16 decoded runes (NOVOWEL power 0.47) with a
  screen that uses v3's panel-max statistic on a short head (16–24 runes, both relations decode identically before
  the first skip). Plant 40 keys per register through it; required: ≥0.85 power on EN_NOVOWEL and ≥0.90 on every
  other register at FPR ≤ 1e-3 (R32-B1's was 6e-4). Measure the ROC, not a point.
- **Q2.** Measured: `round32/B1-bash-random/prefilter_power_trigram.json` (0.72 EN, 0.70 LA, 0.74 DE, **0.47
  NOVOWEL**); Round 33 I1 shows panel-max is what makes NOVOWEL searchable.
- **Q3.** Bounded: ≤ 9 × 40 plants × a few head lengths × a null of 10⁵ random heads for FPR.
- **Q4.** N/A; conditional carried = the prefilter's measured power per register, stated in every B1 row.
- **Q5.** If no head length ≤ 24 reaches 0.85 NOVOWEL power at FPR 1e-3, report the best (power, FPR) curve and let
  B1 run at a stated higher FPR with a stated smaller fraction — never silently.
- **Deliverable.** `round34/I2-novowel-prefilter/` — `pf_v3.py`, `roc.json`, `power_per_register.json`,
  `RESULTS.md`, `ledger.json`.

---

### B1 — The two orbits under v3  _(bounded, enumerable; the round's compute)_

- **Q1.** R32-B1's planted end-to-end controls (10 per ABI × relation) **plus** an EN_NOVOWEL plant per cell pushed
  through the real chunk path (prefilter → v3 → panel). ≥3 recoveries per cell before any null counts; the NOVOWEL
  plant must recover.
- **Q2.** Measured: both orbits are enumerated (77,594,624 bash seeds × 2 ABIs; PHP prior-dense 48,036 + the 0.97 %
  uniform sample of 41.7M per twist), both negatives have stated NOVOWEL reach ≈0.28–0.47, and the instrument that
  fixes that now exists. This is the doctrine's "re-adjudicate a closure with a repaired instrument", on the two
  closures with the best stores.
- **Q3.** Enumerable but heavy here: screening 77.6M heads took R32-B1 ~2,000 s with the trigram screen; the panel-max
  head screen is 1.4–2.3× that. Budget: bash LP64 full (cap 60 min), bash ILP32 and the PHP tiers as **stated
  fractions** of whatever fits in a further 60 min, uniform seed-3301 samples, coverage reported per cell. The
  remainder is deferred with its fraction stated (R7).
- **Q4.** key space = the stored orbit cells (fractions stated); transition model = keyskip1 + keyskip2 under v3
  (`free` not covered); register = nine-register panel with I2's per-register prefilter power and v3's envelope
  stated per row.
- **Q5.** If the NOVOWEL plant fails the chunk path in any cell, fix the harness; no coverage claim through a failing
  control. If I1's bar is not observed at B1's N, use the empirical quantile and say so.
- **Deliverable.** `round34/B1-orbits-v3/` — `sweep.py`, `control.json`, `sweep_rows.jsonl` (SWEEPROW), summary,
  `RESULTS.md` (coverage × power per register per cell; any crosser → flagged-for-oracle + L=240 re-screen + ≥3
  verifiers), `ledger_patches.json` extending R32-B1 / R32-B2.

---

### S1 — The build box  _(Linux sandbox; three unbuildable items in one lane)_

Use a Vercel sandbox (the session has `create_sandboxes` / `run_session_command` / `write_session_files` /
`read_session_file`) or any Linux box with `gcc`, `php5`-era source, and `ghostscript` buildable from ghostpdl
tags. If no sandbox can be created, the lane writes its PREREG and the exact command script and stops — that is a
recorded outcome.

1. **C engine.** Upload `round27/P1-engine/grind27.c`, `round28/L4/grind28.c` + their inputs; `gcc -O2 -Wall`; run the
   resume path against a copy of the parked S2 state (`run/STATUS.json`, `HIT-CANDIDATE.json`) and prove: hits are
   restored on resume, seed 35563892 is deduplicated, `flagged_survivors` is emitted from the real hit list. Then a
   planted-hit resume test. **Do not resume S2 itself.** Deliverable: build log, test log, a `BUILD.md` with the
   exact commands, and — only if every test passes — a one-line change to `PICKUP-HERE.md` lifting "do-not-resume"
   to "resume-ready, Round 35".
2. **PHP 5 reference.** Build or fetch PHP 5.6 (or 7.0, same legacy twist) and record `mt_srand(1); mt_rand()` and the
   first 20 draws; compare to `round32/B2-php-mtrand/php_mt.py` legacy mode (expected 1244335972). FOUND/NO-ERROR.
3. **O1 Q5 kill test.** Build gs 9.04 and gs 9.14 from ghostpdl tags; render LP2 page 0 through both at the R18-L1
   measured parameters; byte-compare the two renders. Identical → "band not resolvable at render level" (O1 KILL, two
   builds spent); different → O1 is live for Round 35 with the comparator's measured sensitivity recorded.

- **Q1–Q5.** Each item has a binary recognizer (compiles+passes / value matches / renders differ) and a kill
  (no sandbox → PREREG + script only). No key space; no decode. Sandbox cost and wall time are logged.
- **Deliverable.** `round34/S1-build-box/` — `BUILD.md`, `engine_tests.json`, `php5_reference.json`,
  `gs_render_compare.json`, `RESULTS.md`, `ledger.json`.

---

### P1 — Finish the payload promotion  _(bounded input; the owner's Option A, done safely)_

- **Q1.** Each unfed reader re-run with `payload_resolved.bin`: R16-KDF (its 7 B-04-derived secrets of 504), R30-B1
  blob-crypto, R30-B2 RSA/GPG, recon `h1_index`, the campaign18 payload scripts — each with its original control
  first, each result compared to its canon run. Then regenerate capsule `MANIFEST.json`, verify with
  `verify_capsule.py`, and only then rename: `canon_256.bin` → `canon_256_superseded.bin`, `payload_resolved.bin`
  copied to `canon_256.bin`, with a `PROVENANCE` line citing R19-C1, Round 33 B1/X1 and the owner's 2026-10-29
  decision.
- **Q2.** Measured: Round 33 B1 (B-04/E-01/E-02 unchanged), Round 33 X1 §5c (the five missed readers listed with
  file:line).
- **Q3.** Enumerable: five readers + one manifest.
- **Q4.** Each reader's own conditionals, restated with "input = payload_resolved".
- **Q5.** Any reader whose result *changes* under the corrected bytes → stop the promotion, flag the reader's row
  for re-adjudication, report; the promotion waits for Round 35.
- **Deliverable.** `round34/P1-payload-promotion/` — per-reader outputs, `manifest_regen.log`, `RESULTS.md`,
  `ledger_patches.json` (C-CANON-PAYLOAD-3BYTES → resolved, with every reader listed). The rename itself is done by
  the **coordinator** after X1 audits P1.

---

### I3 — D5c `m_NV(L)` calibration  _(small instrument lane)_

- **Q1.** On the three clean keys already used (Round 32 I4 + Round 33 X1's `CICADA-X1R33`) plus one new one, fit
  `m_NV(L)` at L ∈ {120, 180, 240, 400} with two recipes (per-register margin as D5c; margin normalised by the I1
  null's beta(L)). Required: ≥0.90 catch at ≤0.10 held-out false-reject **at every L** on the pooled and the
  NOVOWEL-only genuine sets (Wilson upper ≤ 0.10 for NOVOWEL — the clause Round 32 X1 flagged).
- **Q2.** Measured: `round33/X1-redteam/d5c_replication.json` (L=240 0.971 / 0 FR; L=120 0.994 catch but 53/53
  NOVOWEL genuine rejected).
- **Q3.** Bounded: 4 L × 2 recipes × the existing hallucination/genuine sets.
- **Q5.** If either recipe fails at any L, SEAL_PASS stays false with the measured ceiling per L; survivors stay
  flagged-for-oracle.
- **Deliverable.** `round34/I3-d5c-calibration/` — `m_nv_curve.json`, `RESULTS.md`, `ledger.json`.

---

### X1 — Red-team  _(R6; last)_

Targets: (1) Round 33 B3 (audit it — X1 R33 closed before it landed): control path deviation (stage-2 with the key
handed over, not through the prefilter), the fitted bars, the sample fraction; (2) Round 33 I2's "earned" relations —
strike or keep, given its own §1 says the doublet prior cannot discriminate; (3) the 13 `verify_capsule.py`
INTACT-FAIL items (CRLF noise or real?) — settle it and fix the manifest or the checker; (4) this round's lanes (PREREG
mtimes, RESULTS vs JSON, vocabulary, S1's sandbox logs); (5) apply the audited ledger patches, run the gate, Round-35
critic list.

## 4. Cross-lane verification and the hit protocol
As Rounds 32–33: controls before nulls; any crosser is flagged-for-oracle (SEAL_PASS=false), re-screened at L=240,
and sent to ≥3 refute-by-default verifiers each recomputing its ceiling at its own N; no lane writes
"exhausted / closed / solved".

## 5. Owner-only items (recorded, not blocking)
- The final `canon_256.bin` rename happens only after P1 + X1; it is reversible (`canon_256_superseded.bin` kept).
- S2 resume is Round 35 at the earliest, and only if S1's engine tests pass.
- Four stale open PRs (#7–#10) predate the 2026-08-11 merge; closing them is the owner's call.

## 6. Orchestration
- **Wave A (parallel, ~4 agents):** I1, I2, S1, I3. P1 also starts (light, touches only its readers' outputs).
- **Wave B (after I1 + I2, 1 agent):** B1 — one CPU-bound job at a time on this laptop.
- **Wave C (1–2 agents):** X1, then the coordinator: SYNTHESIS, ledger, nav docs, gate, commit to master, push.
Discipline unchanged: Sonnet; no `git` in lanes; own `round34/<lane>/` dir; nproc=1; stream to disk; no
filesystem-wide `find`; PREREG dated before first output; ~7 GB RAM laptop with <1 GB free.

## 7. Guardrails — do NOT re-run
Everything in Rounds 32–33 §6/§7; the Round 33 B3 survivor re-adjudication (done at 1.00 of stored survivors — B1
goes to the *orbits*, not the survivors); the Round 33 I2 doublet priors; Round 33 B2's LP1 gate (reproduced).

## 8. Definition of a good Round 34
v3 has an observed null of record; the two best stores in the repo have a stated NOVOWEL reach that is no longer the
weakest cell; the C engine is either proven resume-safe or proven still broken, on a real compiler; the payload canon
is promoted with every reader re-fed or the promotion is stopped by a measured change; D5c either calibrates across
L or records its ceiling per L. A survivor would be extraordinary. The round succeeds without one.
