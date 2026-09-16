# Round 28 — SYNTHESIS (**INTERIM**): exhaust every runnable option, optimistically

_**INTERIM 2026-09-15 (2026-09-16T05:1xZ). This is NOT the final Round-28 synthesis.** The
round is deliberately left OPEN: R27-S2 is still sweeping (43.2% at writing) and the 25-cell
grind28 queue fires automatically when it exits. The final SYNTHESIS.md is written after the
queued sweeps complete and their crossers are adjudicated. Trust anchor
`python3 tests/validate.py` → **ALL VALIDATIONS PASSED (5/5)** before and after this closeout.
`validate_ledger.py` **Unsound negatives = 0** before and after. Ledger **157 → 162** entries
(R28-L1/L2/L5/R + the in-flight R28-L4 queue row)._

## The question this round asked

The owner's charter: **keep exhausting every remaining runnable option with current technical
abilities, optimistically** — treat every lane as if the key IS inside it, build so a hit
cannot be missed, and deliver, either way, a checked-off box future researchers can trust.
Each closed lane below is such a box: pre-registered (five Aiming-Test answers per PREREG),
plant-and-recover validated (≥0.90 recovery, HIT=True) *before* any null counted,
anti-repeat proven against `LEDGER.json` `coverage`/`not_covered` (never bare `status`),
coverage×power reported with the three conditionals of every negative, and every would-be
survivor FLAGGED-FOR-ORACLE rather than auto-certified. Standing verdict under test (not
re-derived): **LP2 0–54 is OTP-class**.

## Per-lane state — coverage × power (as of this interim)

| Lane | What it fired | Control (before any null) | Coverage | Best vs bar | Verdict so far |
|---|---|---|---|---|---|
| **L1** cicadaos-pads dense+pair | The 2 authoritative author pads as literal keystreams: dense offset grids (244+359 offsets, ×22/×45 denser than R12-A1) × 5 reductions × dir × sign × {exact, **pair**} — pair is the relation R18-L7-B proved the beam cannot represent, never before run on these pads | keyskip1 plant 1.000/HIT, skip_by_two plant 0.996/HIT on the REAL pad bytes at non-zero offset; beam-on-pair cross-check 0.071 proves the pair axis is new power | 24,080/24,080 planned rows (100%), SWEEPROW/1 persisted | best pmax **5.606** vs claim 7.384/7.634 (even true-N bars 6.379/6.567); 23 screeners ≥5.0 all stage-B adjudicated, all collapse | **NEGATIVE** — 0 claim-bar, 0 flagged |
| **L2** contested-bytes | (read) independent BLIND transcription of all 15 contested/unverified payload cells by an instrument built independent of L5/C1; (decode) 128 payload reading-variants × full `keytest.py` battery = **21,628,416 decodes** | reader gate 100/100 exact-token (min margin 0.0833); plant b0m37@160 top-1, recovery 1.000, HIT | 128 variants × 56 targets = 7,168 rows, no gaps | best **−6.350** vs family bar **−5.7923** — below the pooled null max −6.210; 0 ≥ bar, 0 near-bar | **read: canon stands (FINAL)** — 100% agreement with A-04 incl. all 3 byte flips; 186/209/210/211 first-verified. **decode: NEGATIVE** |
| **L3** string-seed dictionary (amd64) | Py2.7 `seed(str)` 64-bit-hash image over the ~390k-word dictionary, first true run of the R18-L1-promoted family (i386 image proven subsumed by R27-S1/S2 — verified empirically by lane R, 106/106 + 66/66 vs live CPython 2.7.18) | 5/5 cell gates PASS (controls_ok 2026-09-08T11:45, before first row) | tier-0 cells r29_pair/r29_exact/grbmod_pair/grbrej_pair/shuf_pair **complete-NULL**; tier-1 r29_pair in progress (~347k words done) | best so far 6.095 vs 7.384/7.634 | **IN-FLIGHT** (PID 689907, nice 15, single-thread, budget 345,600 s) |
| **L4** unswept generators | grind28 engine: PHP `mt_rand` both twists × both scalings (P-4 blocker gone — validated |Δ|=0 vs on-box PHP 8.5.4), glibc gen=0 (R19-G3-CORRECTION open row), R27-S3 cells — **25 gated 2³² cells** | 25/25 plants full-gate HIT=True recovery 1.000; 1600/1600 vectors |Δpmax|=0.0; 200/200 false-rejects below claim; gate REQUIRED by the engine, no override exists | **0 — zero coverage claimed.** Frozen in `queued_cells.json` / merged `sweep_plan_r28.json`, bars pair 9.638 / exact 10.031 at N=2³², family 25 disclosed | — | **QUEUED** post-S2 (≈15–19 days of 6-core wall) |
| **L5** payload-micro | The three never-run remainders: E-01w (432-bit 2013 modulus over 54-byte payload windows), E-02v (varint gap reads), H-03r (2012 P.S. rotate-90) | 25 plants recovery 1.00 on all fronts; H-03r's first negative-control FAILED 37/200 → bar recalibrated to 0.95 by dated amendment BEFORE real data | 100% of the amended enumerable grid (2,493 pow-tuples + 3,654 EM reads + 24 correlation cells + 10 readings) | 0 strict hits; max |ρ| 0.119 vs 0.5 | **NEGATIVE** — plus the community "3301 in the P.S. digits" claim RESOLVED as a layout artifact of the 5-char "P.S. " indent (p≈5%) |
| **R** red-team ×2 | Pass 1 (T1–T5): ledger hygiene, S1-closeout recompute, L3 subsumption, PREREG↔code drift, S2 non-interference. Pass 2 (`R-redteam/RESULTS.md`, 2026-09-16Z): full recompute of L1/L2/L4/L5/R + chainer safety | its own planted-defect controls (corrupted histogram bin → checker fails; planted bad rows → checker fails) | every lane headline recomputed from raw artifacts | — | Pass 1: **T2/T3/T4 NO-ERROR-FOUND, T1 + T5 FOUND-ERROR** (both process-class). Pass 2: **ERRORS-FOUND-NONE-SCIENTIFIC** — 6 defects D1–D6, 0 touching any negative, 0 dropped candidates |

**Power, both axes, per doctrine R2:** every closed negative above issues from an instrument
whose plant recovered at ≥0.996 through the *real* code path (L1 both relations; L2 both the
reader gate and the decode battery; L5 all three recognizers after the H-03r bar was fixed
by its own failing control). The register conditional stands everywhere: the I2 9-register
panel + quadgrams is the adjudicator of record, and R3 language-agnostic stats are persisted
on every row so all of these nulls are re-interpretable under future registers.

## What was genuinely un-run (anti-repeat, one line each)

- **L1:** R12-A1's own artifacts show 8–11 sampled offsets per pad and keyskip1-beam only;
  L1 swept ×22/×45 denser grids plus the pair relation and the N-scaled gate. The 40
  keyskip1 o=0 cells R12-A1 already covered were excluded — verified offset-exact by the
  second red-team from R12-A1's raw result files.
- **L2:** `A-04` resolved the conflict cells but its `reopens_if` explicitly named "an
  independent BLIND transcription" as the missing test; cells 186/209/210/211 had never been
  pixel-verified; the keytest battery had only ever seen 2 of the 128 reading variants.
- **L3:** the amd64 64-bit-hash image is `R21-L3` NC-2, never run; the i386 image is
  *subsumed* by R27-S1/S2 — a zero-compute closure verified empirically by lane R.
- **L4:** PHP was CENSUS §C's highest-prior generator "implemented nowhere"; glibc gen=0 is
  `R19-G3-CORRECTION.not_covered[0]`; the S3 cells are exactly what
  `R27-CPORT-MT32-FULLSWEEP.not_covered` deferred for lack of per-cell controls.
- **L5:** each front consumed the verbatim `not_covered`/never-run remainder named inside the
  E-01/E-02/H-03 ledger rows; nothing already measured was re-run.

## The optimistic-exhaustion framing

The charter's point is not that any single lane was likely to hold the key — it is that each
lane was run **as if it did**: plants in the actual hypothesized shape, gates that cannot be
bypassed (grind28 has no control-override env var at all), append-only candidate records, and
bars pre-frozen so a real signal cannot be argued away after the fact. The value of a clean
NULL built this way is that **no future researcher ever has to wonder** whether the author's
own pads at dense offsets (L1), a mis-read payload byte (L2), the Py2.7 string-seed family
(L3, in flight), PHP/glibc integer seeds (L4, queued), or the payload's micro-structure (L5)
secretly held the answer. Five more boxes checked or checking; the honest remainder of each
lives in its ledger row's `not_covered`, not in anyone's memory.

## Live state and the chain queue (what fires, and when)

- **R27-S2** (`grind27` PID **701083**, resumed 2026-09-16T05:02:53Z after a host outage
  killed PID 494140 at 41.7% — checkpoint continuity verified, no gap/double-count): 43.2%
  at writing, ~76k seeds/s under contention → **completes in roughly 9 h**.
- **Chainer** `chain_after_s2.sh` (PID **701073**, detached, log `chain.log`): polls
  `round27/sweep.pid` every 60 s; resumes grind27 if it dies mid-lane; on
  `lanes_completed ⊇ {S2}` writes `S2-COMPLETE.marker` FIRST, then launches the grind28
  25-cell queue (`sweep_plan_r28.json`, run dir `round28/run/` — physically separate from
  S2's), flagging any `HIT-CANDIDATE.json` FOR-ORACLE, never certifying.
- **Queue safety** was independently audited (second red-team): 25/25 cells re-validated
  from receipts (plant recovery 1.0 each, gate SHA-256s match disk), run-dir separation
  real, fallback plan set-identical, no override path in the engine.
- An out-of-band **premature grind28 launch** on 2026-09-15 was SIGTERM-stopped; its orphan
  partial output is marked non-authoritative (`L4/run/ORPHANED-PREMATURE-RUN.txt`) and was
  audited anyway: best pmax 6.765 vs claim 9.638 — nothing near a bar was lost. The
  sanctioned queue re-sweeps from seed 0.

## Red-team defects carried to final closeout (all process/records-class)

| id | severity | item | disposition |
|---|---|---|---|
| D1 | MEDIUM | chainer lacks a singleton `flock` + `launch_queue` lacks an already-running guard | patch text in `R-redteam/RESULTS.md`; apply at next chainer restart (not while PID 701073 executes the script) |
| D2 | LOW | incident narrative mis-dated (outage was 2026-09-16T04:52–05:02Z, not 09-11) | corrected of record here; chain.log is the primary record |
| D3 | LOW-MED | L3's sweep runs against R-T5's "no new compute until S2 exits" prescription | coordinator decision of record: L3 is **left running** (measured cost ~4%/thread at nice 15; T5's dominant steal was un-niced host dev processes); T5's prescription is hereby amended to "niced single-thread lanes tolerated" |
| D4 | MEDIUM | T1's `not_covered: null` hygiene defect: R12-A1 patch text unapplied; 8 more rows in the census | **R12-A1 patched in this closeout** (T1 §1 text applied verbatim to LEDGER.json); the remaining 8-row hygiene pass stays an open item |
| D5 | LOW | orphaned premature grind28 output | FIXED in-audit (marker file) |
| D6 | LOW | `flagged_survivors` hardcoded `[]` in grind27/grind28 STATUS (cosmetic; real record is HIT-CANDIDATE.json); S2's carried crosser 35563892 (pmax 7.6707 ≥ 7.6342) **owes its S2-lane oracle adjudication at S2 closeout** (S1 verdict NOISE-CROSSER, expectation NOISE — must be recorded, not inherited) | on the final-closeout checklist below |

## Final-closeout checklist (what converts this INTERIM into the final synthesis)

1. S2 completes → S2 planted-control validation + `candidates.jsonl` batch parity
   (`s1_batch_parity.py` pattern) + **S2-lane adjudication of crosser 35563892** →
   convert `R27-CPORT-MT32-FULLSWEEP` to its completed verdict.
2. grind28 queue runs (marker → 25 cells, ≈15–19 days) → per-cell `stage_a28.py` batch
   parity → hitfn20 + `oracle_crosser.py` on every claim-bar crosser → per-cell coverage
   rows → convert `R28-L4-UNSWEPT-GENERATORS-QUEUE` from in-flight.
3. L3 completes (or exhausts budget) → its own RESULTS.md + ledger row.
4. Apply D1's chainer lock at the next chainer restart; run the D4 8-row hygiene pass.
5. Final `SYNTHESIS.md`, ledger conversion, PICKUP-HERE refresh, commit.

## Bottom line (honest, one paragraph, interim)

Round 28 has so far **hardened** the OTP-class verdict for LP2 0–54 along four more
previously-unswept axes — the author's own pads at dense offsets under the
beam-unrepresentable pair relation (L1), the complete contested-byte reading-variant space
*and* a second independent blind transcription that says canon stands (L2), and the payload's
RSA-window/varint/rotate-90 micro-structure (L5) — while **building and control-freezing**,
but deliberately not yet firing, the 25-cell PHP/glibc/S3 generator queue (L4) and keeping
the string-seed dictionary sweep in flight (L3). Two red-team passes recomputed every
headline from raw artifacts: **zero scientific errors, zero dropped candidates**; all six
defects found are process/records-class and are dispositioned above. 0 certified hits,
0 flagged-for-oracle survivors among the closed lanes. The prior mass still sits on
"external or unseeded pad, no recoverable key"; the queue that could still move that within
current technical ability is armed and fires by itself. **Bounds, not verdicts** — each
closed lane's un-swept remainder is stated in its ledger row, and the /dev/urandom branch
remains untouchable by construction.
