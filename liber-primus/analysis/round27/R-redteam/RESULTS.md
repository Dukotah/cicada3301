# Round 27 / Lane R — red-team audit of the GO gate (C-engine 2^32 sweep)

**Date:** 2026-09-07. **Posture:** refute by default. **Trust anchor:** `tests/validate.py`
re-run first → `ALL VALIDATIONS PASSED` (5/5).

**VERDICT: NO-ERROR-FOUND** — the GO gate's evidence reproduces from raw artifacts, and
every adversarial fresh-material test (new seeds, novel plant seed, production-path
interrupt/resume) passed bit-exactly. Five NOTE-severity findings below; none invalidates
GO or any number in the gate report.

Audit scripts (committed, reproducible): `audit1.py` (artifact recompute, no binary),
`audit2.py` (fresh parity vs the real binary), `miniplan.json` + `testrun/` (production
`run_lane` liveness + resume test).

---

## 1. Gate evidence recomputed from raw artifacts — all reproduce

| gate claim | recomputed here | match |
|---|---|---|
| claim bar = 7.383520294328688 | mu + β·(ln 1e6 − ln(−ln .99)) from `vectors.json` Gumbel cell = 7.383520294328688 | ✔ exact |
| false-reject sample = frozen RNG 27002 | regenerated 100k seeds from `random.Random(27002)` == `py_scores.jsonl` seed set | ✔ |
| py max 5.538506 @ 342028379; 0 ≥ hard gate 5.8835; 6 ≥ cand bar 5.0 | 5.538506 @ 342028379; 0; 6 (seeds 342028379, 1767045001, 2992200523, 3507020799, 3602920670, 3627553781) | ✔ |
| all 6 C-flagged, false-reject 0/6 | re-scored all 6 with the real binary: every one ≥ 5.0, **&#124;d&#124; = 0** vs Python | ✔ |
| engine.dat == vectors.json | MU/SD vectors, C_SCREEN 120, PLANT_CIPHER 120, CAND_BAR 5.0, both claim bars — all byte-equal to `vectors.json` constants | ✔ |
| vectors.json honest (not a pyref closed loop) | `make_vectors.py` imports the R25 pipeline **verbatim** (`round25/compute-tail/runner.py` + module graph, reimplements nothing); I re-ran 4 fixed vectors direct through that pipeline → identical to frozen reprs incl. `pmax` at full precision | ✔ |
| R25 repro 2149309687 → 6.825835461843649 | reproduced in Python-direct AND in the production sweep candidate output, &#124;d&#124;=0 | ✔ |
| STATUS coverage arithmetic | bands contiguous [0,2^32) exactly (w2 end = 3×715827882 = w3 start; w5 absorbs the +4 remainder); coverage_fraction = Σ(cursor−band_start)/2^32 recomputed equal to 9 d.p. | ✔ |
| candidate rate K2 | live 7776/85.78M = 9.07e−5/seed = **1.30×** Gumbel 6.95e−5 → inside K2 [0.2×, 5×] | ✔ |
| candidates.jsonl integrity | 0 rows below bar, 0 duplicate seeds, max 7.035050 @ 2873275872 == STATUS best; histogram bins ≥ 5.00 == n_candidates (snapshot-consistent); 0 bins ≥ claim bar == n_claim_bar_hits 0 | ✔ |
| ETA math | 2^32/128,529 = 33,417 s = 9.28 h ✔; live sustained ~100–106k/s ⇒ ~11.3–11.9 h/lane, matching the gate's disclosed throttled case; both lanes well under the 48 h ceiling | ✔ |

## 2. Broken-magnet hazard — attacked three ways, held

**(a) Candidate emission cannot drop near-bar seeds.** `grind27.c` run_lane: the ONLY
filter is `pmax >= ln->cand_bar` (5.0); the claim-bar comparison (lines 983–989) purely
ADDS `HIT-CANDIDATE.json` and keeps sweeping — verified in source; it cannot suppress a
candidate. Margin geometry: cand bar 5.0 sits **0.88 below** the hard gate (claim−1.5 =
5.8835) and *below the empirical null maximum itself* (5.539 in 100k; 7.035 in 85.8M) —
the screen flags into the null bulk, i.e. errs on the over-flag side.

**(b) Fresh adversarial parity (not the frozen artifacts).** 24 new random seeds from my
own RNG (987654321) + the 6 near-bar seeds + a **novel plant at seed 271828182** (a seed
no P0/P2 artifact ever used, same skip_by_two recipe) + 4 non-true seeds under the plant
cipher: Python-direct vs C = **worst &#124;pmax diff&#124; = 0** across all 35; novel plant scores
17.931158509762 (margin 12.9 over bar), screen recovery vs truth = **1.000**, and the
neighbouring wrong seeds score 0.33–1.99 (the magnet attracts only the true seed).

**(c) The REAL production path, including resume.** The gate's drill Part B ran through
`--mode sweep` (`mode_sweep`), which shares the `screen_one` kernel + emission predicate
but is *not* `run_lane` (no checkpoint/resume/banding-state code) — see N1. So I ran the
actual production entry (`--plan`, `run_lane`) over a 100k-seed mini-plan containing the
R25 best word, **interrupted it mid-band at ~11% (`--seconds 0.35`), then resumed**:
final coverage exactly 100,000/100,000, lane marked complete, seed 2149309687 flagged at
pmax exactly 6.825835461843649, and the mini-run's 6 candidates are **identical (seed set
and bit-exact pmax) to the live production run's flags over the same band**. Resume
re-scans ≤255 seeds/worker (cursor is persisted *before* the seed it points at is
processed — lag is conservative; a skip is structurally impossible in this design).

## 3. PREREG compliance — honest

- **Five Aiming-Test answers present** (Q1–Q5), with the Q1 positive control planted in
  the actual shape *before* the C code existed (full-gate plant HIT=True at recovery
  1.000 + screen plant margin 12.9), Q2 citing `round18/L1-toolchain/RESULTS.md` §6 by
  path with an honest low-absolute-prior caveat, Q3 ENUMERABLE 2^32/cell, Q4 naming the
  **three conditionals** (key space / decoder transition model / adjudicator register —
  restated again in the gate report), Q5 kill conditions K1–K4 with numbers.
- **No silent re-run mislabeled as new:** the re-cover of R25's 0.5015% is disclosed and
  justified (cursor policy §S1); the S2 "correction to the tasking note" (pair ≡ R25
  config, so S2 = keyskip1 'exact') is disclosed rather than double-counting a re-run as
  a new cell; S3 deferred explicitly as unvalidated completeness rituals.
- **S2 gating stands:** `sweep_plan.json` S2 `_note` and MONITORING.md both state its
  null does not count until an `encipher_keyskip` planted control + V1-style vectors
  pass. Mechanical sweeping before that is fine (adjudication, not enumeration, is gated).
- Doctrine order respected: positive control → parity gates → nulls; value = coverage ×
  power reported (coverage 1.0/cell by construction; power = plant margins, register
  class named); survivors FLAGGED-FOR-ORACLE only (R21-L1) — wired into the C hits file
  text itself.

## 4. Findings (all NOTE severity — no defects)

- **N1 (wording, mitigated here):** the gate's "drill passes through the REAL sweep
  path" overstates slightly — `mode_sweep` ≠ `run_lane` (shared kernel, different loop/
  state code). My §2(c) test now covers `run_lane` + resume directly; nothing found.
  Suggest future drills use `--plan` + a temp run-dir.
- **N2 (cosmetic):** STATUS.json `aggregate.seeds_done` can lag Σ(workers.seeds_done) by
  a few (racy volatile reads at flush time) and `cursor` lags `seeds_done` by ≤255/worker.
  Reporting-only; coverage uses cursor arithmetic, which is exact and conservative.
- **N3 (documented quirk):** `--vectors`/`--lm` CLI flags are accepted but ignored — the
  engine loads `engine.dat` (exported from vectors.json). Audited byte-equal (§1) and the
  LM sha256 is independently pinned to `panel.npz`; the harness comparisons are all
  against `vectors.json` in Python, so no closed loop. Fine, but keep `check_vectors` in
  every future gate.
- **N4 (operational):** no Python stage_b consumer is running; candidates are
  accumulating (~8.8k at audit time, ~3.7e5 expected/lane). SPEC allows batch-at-lane-end,
  but K4 (C-vs-Python disagreement kill) only has teeth while stage_b runs — recommend
  starting the concurrent tail re-scorer soon.
- **N5 (scope, disclosed):** both plants (777 / 3141592653 / my 271828182) use the same
  English plaintext (`self_reliance[5000:5240]`); measured screen power covers exactly
  the skip_by_two + 9-register class PREREG Q4 names. This is the standing L7-A caveat,
  correctly carried — the eventual null must keep saying so.

## 5. The three conditionals this lane's negative will carry (restated per doctrine Q4)

1. **Key space:** Py2.7/mt19937ar `init_by_array([w])`, w ∈ [0, 2^32), reducer random29,
   offset 0.
2. **Decoder transition model:** driftbeam keyskip2 'pair' (S1) / keyskip1 'exact' (S2,
   control-gated), rejection-loop constructions only.
3. **Adjudicator register:** I2 9-register panel-max + English quadgrams at L120
   (stage-A screen), hitfn20 3-clause as claim gate.

**VERDICT: NO-ERROR-FOUND**
