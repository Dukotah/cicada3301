# Round 35 — THE SKIP-TOLERANT SCREEN, THE RESTORED PANEL, AND THE PARKED SWEEP (pre-registration / plan of record)

_Drafted 2026-10-30 as Round 34 closed. Binding doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md).
Seeded by Round 34 X1's completeness critic and [`../round34/SYNTHESIS.md`](../round34/SYNTHESIS.md) §6. Each lane's
`PREREG.md` is authoritative once written and is dated before its first output file._

## 0. Thesis — one measured hole, one missing file, one parked sweep

Round 34 left the repo with a precise statement of where its best two negatives are still blind: **the head screen.**
Round 33's beam searches all nine registers (EN_NOVOWEL 1.000 with the correct key); Round 34's observed null makes its
bar honest; but the prefilter that decides which of 77.6 M bash seeds reach the beam scores the first 20 decoded runes
*assuming no key skip*, and Round 34 X1 measured that 37–51 % of true-key heads contain a skip and pass at only
0.19–0.34 (`round34/X1-redteam/rerun_i2_skipfree.json`). Reach at the orbit level is therefore ≈0.65–0.70, not the
0.98–1.00 the decoder would give. A screen that tolerates one or two skips in the head is a small dynamic program
over advance ∈ {1, 2}; it is bounded, planted-control-gated, and once it exists the bash orbit is a 15-minute
re-screen. That is the flagship.

Two bounded items sit beside it. **The Round 19 panel** (`round19/I2/models/panel.npz`, sha 14a23d36…) gates the
Py2.7-MT S2 engine's self-test and exists nowhere on this checkout or on GitHub; Round 34 S1 proved the fixed engine
compiles and resumes correctly on copies, so the panel is the only thing between the repo and resuming the 44.14 %-
parked S2 sweep (`ELIMINATION-LEDGER.md` line ~26). It was built by `round19/I2/build_models.py` from corpora this
checkout has only as Round 32 substitutes (`round34/X1-redteam/manifest_decision.md` §3); fetching the originals
(`data/fetch_sources.py`) and rebuilding is enumerable and has a byte-exact recognizer. **D5c** calibrated at four
lengths with a post-hoc `m_NV ≈ 0.055·L`; pre-registering that rule and testing it on new keys and lengths is the
cheapest remaining step toward auto-certification.

**Not a target this round:** any new generator family; the PHP 2³² tails (R28-L4 queue); the Round 33 I2 struck
relations; O1 beyond its PREREG (no real page-0 source).

## 1. Doctrine budget allocation

| share | goes to | lanes |
|---|---|---|
| **≈35%** | instrument — skip-tolerant screen + envelope; D5c validation | I1, I3 |
| **≈35%** | bounded, enumerable — the bash orbit re-screened; S2 window | B1, S1 |
| **≈15%** | restore the input the parked sweep is gated on | P1 |
| **≈15%** | red-team + closeout | X1, B2 |

## 2. Lane roster

| ID | Type | Title | Compute | Gates on |
|---|---|---|---|---|
| **I1** | instrument (flagship) | Skip-tolerant head screen: DP over advance {1,2} on the first 20–24 runes; ROC and per-register power on plants *with* skips | light | — |
| **B1** | bounded | bash 4.2 orbit (LP64 + ILP32, full) re-screened with I1's screen, survivors through v3 under the Round 34 null | ~30–60 min | I1 |
| **P1** | restore input | Fetch the original KJV / Mabinogion / Welsh corpora, rebuild `round19/I2/models/panel.npz`, match sha 14a23d36…; refresh the capsule entries | light, network | — |
| **S1** | build box | If P1 matches: build the fixed engine in the sandbox, pass `--self-test` on the restored panel, resume S2 for a **stated window** (cap 60 min sandbox), report new coverage fraction and crossers | sandbox | P1 |
| **I3** | instrument (small) | Pre-registered D5c: `m_NV = 0.055·L` frozen, tested on 2 new keys × L ∈ {150, 300, 400}; EN_HALFVOWEL-argmax hallucinations added to the catch set | light | — |
| **B2** | closeout | R30-B1 canon-as-key over T2/folly and R30-B2 folly/2.jpg legs — regenerate the inputs from committed code if possible, run with the promoted canon, else file `not_covered` precisely | light | — |
| **X1** | red-team | This round + carry-overs (B1 R34 control-by-construction; D5c post-hoc rule; capsule after P1) | light | last |

## 3. Lanes in detail

All sweep lanes use `round33/I1-register-aware-beam/beam_v3.py` (panel_max, lam_u=4), the Round 32 I2 panel, and
`round34/I1-v3-null/bars_v3.py` as the bar of record (L≥120, keyskip1/2 only); SWEEPROW stores (check 7); no `git`.

---

### I1 — The skip-tolerant head screen  _(flagship instrument lane)_

- **Q1.** Build `pf_v4`: for a head of m runes (m ∈ {20, 24}), run a small Viterbi/DP over per-position key advance
  ∈ {1, 2} (at most k skips, k ∈ {1, 2}) and score the best path under the same `lse` nine-register statistic as
  `round34/I2-novowel-prefilter/pf_v3.py`. Plant 2,000 keys per register **through the real encipherer** (so heads
  contain skips at the natural rate — Round 34 X1's `rerun_i2_skipfree.py` is the harness; do not select skip-free
  windows) under keyskip1 and keyskip2. Required: EN_NOVOWEL power ≥0.85 and every other register ≥0.90 on the
  natural-rate plants at FPR ≤1e-3 (10⁵ wrong-key heads per generator). Report the ROC per (m, k), the power split
  by skip-free vs with-skip heads, and throughput vs `pf_v3`.
- **Q2.** Measured: pf_v3 passes with-skip heads at 0.19–0.34 (`rerun_i2_skipfree.json`), those are 37–51 % of
  true-key heads, so reach is capped at ≈0.65–0.70 on an orbit the beam could otherwise read at 0.98–1.00.
- **Q3.** Bounded: 2 m × 2 k × 9 registers × 2,000 plants + FPR nulls. Throughput is the cost to watch: the DP is
  O(m·k) per head; at ≤3× pf_v3's cost the orbit re-screen is still ≈45 min.
- **Q4.** N/A; the conditional carried into B1 is the screen's measured per-register power on natural-rate heads.
- **Q5.** If no (m, k) reaches 0.85 NOVOWEL at FPR 1e-3, report the best curve and the operating point B1 should use at
  a stated higher FPR; if even FPR 1e-2 fails, stop — the finding is "skips in the head are not screenable at m≤24"
  and B1 runs as a stated-fraction un-prefiltered sample instead.
- **Deliverable.** `round35/I1-skip-tolerant-screen/` — `pf_v4.py` (same signature as `pf_v3.prefilter_mask`),
  `roc.json`, `power_per_register.json` (skip-free / with-skip / natural split), `throughput.json`, `RESULTS.md`,
  `ledger.json`.

---

### B1 — The bash orbit re-screened  _(bounded, enumerable; the round's compute)_

- **Q1.** Positive control through the real chunk path with **natural-rate plants** (not skip-free-selected — the
  Round 34 B1 control was by construction): ≥5 EN_MODERN + ≥5 EN_NOVOWEL per (ABI × relation), ≥3 recoveries each,
  with the pass/fail split by skip-free vs with-skip plants reported.
- **Q2.** The orbit is enumerated (Round 32 B1, Round 34 B1); its measured reach is ≈0.65–0.70; the instrument that
  lifts it is I1's.
- **Q3.** Enumerable: 77,594,624 × 2 ABIs; cap 60 min screening + decoding; both relations.
- **Q4.** key space = full orbit, `%29`, offset 0, sign −1; transition model = keyskip1 + keyskip2 under v3; register =
  nine-register panel with I1's measured per-register natural-rate power stated per row.
- **Q5.** NOVOWEL with-skip plants failing the chunk path → fix the harness; no coverage claim through a failing control.
- **Deliverable.** `round35/B1-bash-orbit-pfv4/` — `sweep.py`, `control.json`, `sweep_rows.jsonl`, summary,
  `RESULTS.md` (coverage × power per register, best vs actual-N and declared-N bars, flagged / near-miss, three
  conditionals, not_covered), `ledger_patches.json` (R32-B1 / R34-B1 extension).

---

### P1 — Restore the Round 19 panel byte-exact  _(bounded input)_

- **Q1.** Recognizer is binary: `sha256(round19/I2/models/panel.npz) == 14a23d36…` (full hash in
  `round34/S1-build-box/engine_tests.json` / `RESULTS.md`). Steps: read `round19/I2/build_models.py` and its
  `out_build.json` for the corpus hashes it recorded; fetch those exact texts with `data/fetch_sources.py` (and
  `--welsh`); verify each corpus hash against `out_build.json`; rebuild; compare. Record every hash at every step.
- **Q2.** Measured: the engine self-test fails on any other panel (V1 26/64, V2 17.9333 vs 17.9312 — Round 34 S1);
  the panel is the single blocker on a 44.14 %-parked enumerable sweep.
- **Q3.** Enumerable: ≤5 corpus files, one build.
- **Q5.** If a corpus cannot be fetched at the recorded hash (mirror re-issued), stop and record which, with the
  mirror's current hash — S2 then stays parked and the ledger says exactly why. Do **not** substitute.
- **Deliverable.** `round35/P1-restore-r19-panel/` — `fetch_log.json` (url, bytes, sha per corpus), `build_log.txt`,
  `panel_sha.json`, `RESULTS.md`, `ledger.json`; if matched, `round19/I2/models/panel.npz` restored in place (it is
  gitignored — say so) and the capsule `corpus.kjv` / `keytext.mabinogion` entries re-verified (coordinator applies
  the manifest change).

---

### S1 — Resume S2 for a stated window  _(build box; gates on P1)_

- **Q1.** On the sandbox: build the fixed `grind27.c` (Round 34 S1 `BUILD.md`), upload the restored panel, run
  `--self-test` — it must pass V1 64/64 and V2 to 4 decimals (the recognizer). Then resume the **real** S2 state from
  its parked cursor for a capped window (≤60 min sandbox wall; the engine streams its own STATUS/HIT-CANDIDATE), with
  the resume-restore test from Round 34 repeated on a copy first. Report the new coverage fraction (from 44.14 %),
  any new claim-bar hits (→ flagged-for-oracle, re-screened under v3 at L=240 locally), and the engine's own rows.
- **Q2.** The S2 (`exact`/keyskip1) Py2.7-MT 2³² space is the highest-prior parked sweep in the repo and its engine
  is now verified.
- **Q3.** Enumerable (2³²); this lane covers a stated window only; the remainder stays parked with its fraction.
- **Q5.** Self-test fails on the restored panel → stop; the panel is not the Round 19 panel after all; record both
  hashes.
- **Deliverable.** `round35/S1-s2-window/` — `BUILD.md`, `selftest.json`, `resume_window.json`, the engine's
  STATUS/HIT-CANDIDATE snapshots before and after, `RESULTS.md`, `ledger_patches.json` (R27-S2 coverage update).
  **Owner-only:** the resumed S2 state is the live one; the lane leaves it in a resumable condition and says where.

---

### I3 — D5c, pre-registered this time  _(small instrument lane)_

- **Q1.** Freeze `m_NV(L) = 0.055·L` (and the four fitted nodes) in PREREG before any decode. Two new clean keys
  (`CICADA-R35I3a/b`), L ∈ {150, 300, 400}, hallucination set = EN_NOVOWEL **and EN_HALFVOWEL** correct-key
  overfits (the unprotected class), genuine sets as Round 32 I4. Required at every L: ≥0.90 catch at ≤0.10 held-out
  FR on pooled and on each of the NOVOWEL-only / HALFVOWEL-only genuine sets (Wilson upper ≤0.10).
- **Q2.** Measured: Round 34 I3 (four nodes, L=400 marginal, HALFVOWEL margin 0).
- **Q5.** Any L or class failing → SEAL_PASS stays false with the per-L ceiling; the rule is not adopted.
- **Deliverable.** `round35/I3-d5c-prereg/` — `PREREG.md`, `calibrate.py`, `results.json`, `RESULTS.md`, `ledger.json`.

---

### B2 — The unmeasured payload legs  _(closeout)_

- **Q1.** Find how `T2.bin`, `folly.bin`, `2.jpg` were produced (R30-B1/B2 PREREG/RESULTS, `round29/L2-blob-cross`);
  if they derive from committed code + vendored images, regenerate and hash them; run the R30-B1 canon-as-key and
  XOR legs and the R30-B2 folly / 2.jpg legs with the promoted `canon_256.bin`, each with its original control.
- **Q5.** Inputs not regenerable → file the precise `not_covered` on R30-B1 / R30-B2 and stop.
- **Deliverable.** `round35/B2-payload-legs/` — regenerated inputs' hashes, per-leg outputs, `RESULTS.md`,
  `ledger_patches.json`.

---

### X1 — Red-team  _(last)_

Targets: (1) Round 34 B1 as written up by the coordinator (control-by-construction; reach arithmetic; the 38,223 s
sleep gap); (2) I1's natural-rate plant harness (is it really natural-rate?); (3) P1's hash chain end to end; (4)
S1's self-test and window arithmetic, and that the live S2 state is left resumable; (5) I3's pre-registration
(PREREG mtime before any output — the last two rounds' addenda broke this twice); (6) apply audited ledger patches,
run the gate, Round 36 critic list.

## 4. Verification and hit protocol
As Rounds 32–34. Any crosser from B1 or S1 is flagged-for-oracle (SEAL_PASS=false), re-screened at L=240 under v3,
and sent to ≥3 refute-by-default verifiers. No "exhausted / closed / solved".

## 5. Owner-only items (recorded, not blocking)
- S1 touches the **live** S2 state. The lane is scoped to a capped window and must leave the state resumable; if the
  owner would rather S2 stay parked, skip S1 — P1 still has value on its own.
- Sandbox snapshot cleanup; stale PRs #7–#10.

## 6. Orchestration
- **Wave A (parallel, ~4 agents):** I1, P1, I3, B2.
- **Wave B (after I1 / P1):** B1 (laptop, one process); S1 (sandbox) if P1 matched.
- **Wave C:** X1; coordinator closeout (SYNTHESIS, ledger, nav docs, gate, commit to master, push).
Discipline unchanged: Sonnet; no `git` in lanes; own `round35/<lane>/` dir; nproc=1; stream to disk; no `find /`;
PREREG dated before first output (addenda go in a separate dated file, not by rewriting PREREG).

## 7. Guardrails — do NOT re-run
Everything in Rounds 32–34 §6/§7; the PHP tiers as swept (R34-B1: prior-dense full, uniform 0.061 %); the Round 34
I1 null cells; Round 34 P1's readers.

## 8. Definition of a good Round 35
The head screen tolerates skips and the bash orbit's reach moves from ≈0.65–0.70 toward the beam's 0.98; the Round 19
panel is restored byte-exact or the repo knows exactly which corpus mirror drifted; S2 either advances with a verified
engine or stays parked for a stated reason; D5c is tested against a rule frozen in advance; the last unmeasured payload
legs are measured or precisely excluded. A survivor would be extraordinary; the round succeeds without one.
