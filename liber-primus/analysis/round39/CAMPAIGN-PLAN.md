# Round 39 — THE MEASURED CEILING (pre-registration / plan of record)

_Drafted 2026-10-31 as Round 38 closed. Binding doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Seeded
by Round 38 X1's critic list and the state after seven armadas. Each lane's `PREREG.md` is authoritative once written
and is dated before its first output; addenda in a separate dated file._

## 0. Thesis — say what this instrument generation excludes, then spend only on what it cannot yet see

Rounds 32–38 built and measured an instrument — twelve-register search, skip-tolerant screen, observed nulls for
every relation and length, a reproducible gate, a register-aware oracle — and pointed it at every enumerable key
family the ledger names, every clue reading the matrix found untried, and every English-only reading the audit
reopened. All negative, with planted controls, at stated power. The repo has never written down what that *means* as
a position: which key families, constructions and registers are now excluded, at what power, and what single
observation would re-open each. Outside solvers arriving at this repo should read that in one page rather than in 250
ledger rows. That page is a closure audit — the activity the doctrine's own evidence table credits with every real
finding here — and it is this round's flagship (P1).

Alongside it, three things the instrument cannot yet see, each bounded:

1. **S2 window 2 and the remaining 52 % of the Py2.7-MT `exact` space.** The window ran; its end state is in a
   snapshot the quota lock prevents reading until 2026-11-01 00:00 UTC (17:00 PDT 2026-10-31); the snapshot expires
   ~2026-11-07. Recover it, then continue in persistent sessions (S1).
2. **The PHP `mt_rand` tier** has a working sandbox harness and zero persisted coverage beyond ~1 %. Retry with the
   fixed protocol: `write_session_files`, one blocking call, `persistent:true` (S2).
3. **Two instrument gaps with a known fix:** the V2 geometry render needs a page-matched null (I1-R38 showed clean
   V2 pages draw glyph-like loops no shuffle reproduces); ciphertext-derived keys (N4/N5/X4) need the key-matched
   null as the standing null, and the adjudicator needs the degenerate-decode guard as a standing flag (T1).

And one reading left on the semantic branch: C1-R38 defined "meaning" as a lexical *address* (synset offset,
frequency rank) and said so; a sense-*similarity* reading (hypernym depth, synonym class) is a different construction,
bounded, and the last F5 cell the matrix can name (C1).

**Not a target:** new generator families; the seal (paused); O1; the 34 "no operation stated" cells.

## 1. Doctrine budget allocation

| share | goes to | lanes |
|---|---|---|
| **≈30%** | the position statement (closure audit) + solver-facing docs | P1 |
| **≈35%** | enumerable mass on the sandbox, after the reset | S1, S2 |
| **≈20%** | the two instrument gaps + the last semantic reading | T1, I1, C1 |
| **≈15%** | red-team + closeout | X1 |

## 2. Lane roster

| ID | Type | Title | Compute | Gates on |
|---|---|---|---|---|
| **P1** | closure audit (flagship) | `MEASURED-CEILING.md`: for every key family / construction / register in the ledger, the measured exclusion power, the three conditionals, and the one observation that re-opens it; a solver-facing rewrite of `handoff/FOR-FUTURE-SOLVERS.md` §1–§3 and the root `README.md` headline | none (reads ledger + RESULTS) | — |
| **T1** | tooling | key-matched null as the standing null for ciphertext-derived key families (one function, used by N4/N5/X4 lanes); degenerate-decode guard (mds ≤ 6 or IoC·N ≥ 4.24) emitted as a SWEEPROW flag by `adjudicate.py`; `bar_v3(N,120,'free')` moved to the 12-register node; tests | light | — |
| **S1** | sandbox | after 2026-11-01 00:00 UTC: recover S2 window 2 from `snap_ff0SWU76EW32OqbWJvp00fnORypR` (STATUS, HIT-CANDIDATE, top list, histogram → downloaded in chunks); then ≥2 further windows in persistent sessions; coverage per instrument | sandbox | quota reset |
| **S2** | sandbox | PHP tier retry with `round38/S2-php-sandbox/run_commands.sh`: control + FPR persisted FIRST (downloaded before any window), then 3301 blocks 318+ and the 3302 stream in ≤40-min windows, rows downloaded after each | sandbox | quota reset; S1 scheduled first |
| **I1** | instrument | page-matched null for V2: for each page, shuffle *within line* and *within word* (keeping interrupters) so the loop-drawing structure survives; re-measure D2's FPR on V2; if ≤0.05, re-score U8's V2 renders | light | — |
| **C1** | bounded | sense-similarity "meaning": frozen WordNet hypernym depth and synonym-class index per LP1 word (manifest + hashes), composed exactly as C1-R38; planted controls; pages 0–2 | ~1 h laptop | — |
| **X1** | red-team | this round + the position statement (refute-by-default on every exclusion claim it makes: is each backed by a row with measured power?) + Round 40 critic | light | last |

## 3. Lanes in detail

---

### P1 — The position statement  _(flagship closure audit)_

- **Q1 (recognizer).** A claim in `MEASURED-CEILING.md` is admissible only if it cites a `LEDGER.json` row with
  `coverage` × measured power and all three conditionals; every claim is machine-checked by a script
  (`check_ceiling.py`) that resolves each cited row and fails on any claim without one. X1 runs it.
- **Q2 (prior).** ARMADA-DOCTRINE §0's evidence table; the Round 36 inhibitor audit (foreclosure labels were the
  repo's historical failure mode); no document currently states the instrument generation's exclusions as a whole.
- **Q3 (bounded).** Reads only; ≤250 rows.
- **Content.** (1) The instrument: decoder, screen, panel, nulls, oracle — each with its measured power and its
  measured limits (OE/EN_HALFVOWEL out of `free` at L=240; ≥3-skip heads; PHP-cell FPR under the 12-register
  screen; v3 recovery assumed for seven registers at the orbit level). (2) The exclusion table: bash `$RANDOM`
  auto-seed orbit (reach ≥0.95 ×12 registers); PHP `mt_rand` prior-dense (full) and uniform (≈1 %); Py2.7-MT `pair`
  (full, Round 19 panel) and `exact` (47.95 % + window 2 pending, panel-R36 from 44.14 % on); SHA-256-CTR / PBKDF2
  seed lists; keytexts; the clue readings (composed, schedule, seeds, indices, semantic address); the Round 10/11/22-C
  reopened families; the near-miss autopsy; geometry (unmeasured, with the reason). (3) For each: the one observation
  that re-opens it. (4) What is NOT excluded: unbounded pads; constructions outside {keyskip1, keyskip2, free ≤2
  skips}; registers outside the twelve; the 52 % of S2; 99 % of PHP; sense-similarity "meaning"; the 34 clue cells
  with no stated operation. (5) The human-oracle path, restated in two lines.
- **Deliverable.** `liber-primus/MEASURED-CEILING.md`, `analysis/round39/P1-measured-ceiling/check_ceiling.py` (+ CI
  hook), the `FOR-FUTURE-SOLVERS.md` §1–§3 rewrite, the root `README.md` headline paragraph, `ledger.json` (audit row).

---

### T1 — Standing nulls and flags  _(tooling)_

- `analysis/round19/I2/adjudicate.py` (both copies): emit `degenerate: bool` (mds ≤ 6 or IoC·N ≥ 4.24) per row and
  exclude degenerate rows from any `pmax` maximum the row writer reports; `benchmark/null.py` or a new
  `bars_keymatched.py`: `bar_keymatched(family_keyfn, L, N, draws)` that re-derives the key from each doublet-matched
  shuffle (the I2-R38 recipe), with the I2-R38 X4 null as its first fixture; `bars_v3`: `free` at L=120 → the
  12-register node (document the change in `round34/I1-v3-null/RESULTS.md` addendum). Failing-then-passing tests; CI.
- **Deliverable.** `round39/T1-standing-nulls/` — patches in place, `tests/test_standing_nulls.py`, `RESULTS.md`,
  `ledger.json`.

---

### S1 — S2 window 2 recovery and further windows  _(sandbox; after the reset)_

- **Q1.** Recovery recognizer: `run_r36/STATUS.json` from the snapshot shows cursors strictly beyond window 1's
  (2,059,308,008) and `HIT-CANDIDATE.json` is readable; report seeds advanced, candidates, crossers ≥7.6342 (→ local
  beam_v3 L=240 under panel-R36 → oracle bundle), near-misses. Then ≥2 windows in `persistent:true` sessions with ONE
  blocking call in flight and state downloaded after each (STATUS, HIT-CANDIDATE, top-1024 in ≤2 KB chunks).
- **Q5.** Snapshot unreadable → record it; continue from `state_after_1/` cursors (window 2 is then lost and said so).
- **Deliverable.** `round39/S1-s2-windows/` — `window2_recovered.json`, per-window state dirs, `RESULTS.md`,
  `ledger_patches.json` (R27-CPORT-MT32-FULLSWEEP coverage per instrument).

---

### S2 — PHP tier retry  _(sandbox; after S1's first session)_

- As Round 38 S2's `run_commands.sh`, with the protocol fixes: control + FPR written and DOWNLOADED before the first
  window; windows ≤40 min; rows appended and downloaded after each; nothing is counted that is not on the laptop.
- **Deliverable.** `round39/S2-php-sandbox/` — `fpr12_php.json`, `control.json`, `sweep_rows.jsonl`, `RESULTS.md`,
  `ledger_patches.json` (seeds ADDED per cell per stream).

---

### I1 — Page-matched null for V2  _(instrument)_

- **Q1.** On the five planted glyphs: D2 detection ≥0.9 at FPR ≤0.05 on V2 with a null built by shuffling runes
  within each line (and, as the second variant, within each word) of the SAME page so that the page's loop structure
  survives; 200 draws per page. If it passes, re-score U8's 58 V2 renders (above p95, above max; PNGs for anything
  above max). Q5: fails → V2 is recorded as unmeasurable by this recognizer family; the geometry reading closes as
  "V1/V3/V4 chance-level, V2 unmeasured".
- **Deliverable.** `round39/I1-v2-page-null/` — `power_v2.json`, `rescore_v2.json`, `RESULTS.md`, `ledger.json`.

---

### C1 — Sense-similarity "meaning"  _(bounded)_

- **Q1.** Frozen in PREREG before any decode: WordNet 3.1 (C1-R38's manifest) → per LP1 word the hypernym depth of the
  first synset (0 if none) and the index of its synonym class (lexname index 0–44); reductions mod 29 / mod 28;
  applications and start ranges exactly as C1-R38; planted controls per variant; pages 0–2; keyskip1 (+ keyskip2 if
  cheap). Q5 as C1-R38.
- **Deliverable.** `round39/C1-sense-similarity/` — `PREREG.md`, `lp1_sense_index.json`, `sweep.py`, `control.json`,
  `sweep_rows.jsonl`, `RESULTS.md`, `ledger.json`, `ledger_patches.json` (the last F5 cells).

---

### X1 — Red-team  _(last)_

Targets: every exclusion claim in `MEASURED-CEILING.md` (run `check_ceiling.py`; spot-check 10 claims against their
rows' measured power); T1's backward compatibility; S1's recovery arithmetic and that windows were counted only from
downloaded state; S2's "nothing counted that is not on the laptop"; I1's page-matched null (does it leak the glyph?);
C1's frozen index; ledger patches; gate; Round 40 critic.

## 4. Verification and hit protocol
As Rounds 32–38 with `HUMAN-ORACLE.md`.

## 5. Recorded, not blocking
- Snapshots `snap_fWma12lA…` (~11-06), `snap_3uGXrds5…`, `snap_ff0SWU76…` (~11-07): S1 reads what it needs, then the
  owner may delete the stopped sandboxes and old snapshots from the dashboard.
- The `round29/L4-image-forensics/fingerprints.json` stray file.

## 6. Orchestration
- **Wave A (now, laptop):** P1, T1, I1, C1 (≤2 heavy laptop processes: C1 and I1's power test).
- **Wave B (after 2026-11-01 00:00 UTC):** S1, then S2, in separate persistent sessions, one blocking call each.
- **Wave C:** X1; coordinator closeout (SYNTHESIS, ledger, nav docs, gate, commit to master, push).
Discipline unchanged: Sonnet; no `git` in lanes; own `round39/<lane>/` dir; nproc=1; stream in append mode; stores
gitignored; no `find /`; PREREG dated before first output; RAM check before heavy runs; agents must not block on
sleeping timers (poll with short bounded commands instead).

## 7. Guardrails — do NOT re-run
Everything in Rounds 32–38 §6/§7; the bash orbit (three negatives at ≥0.95 ×12); the composed/schedule/seed/index/
semantic-address clue readings; the Round 10/11/22-C re-scores; the X4 and N5/N4 re-judgements; the 34 no-operation
cells.

## 8. Definition of a good Round 39
A stranger can read in one page what this instrument generation excludes, at what power, and what would re-open each
item, and a script enforces that every such claim is backed by a measured row; S2 window 2 is recovered and S2 advances
under persistent sessions; the PHP tier finally has persisted rows; V2 geometry is measured or closed as unmeasurable;
the last semantic reading is run. A survivor would be extraordinary; the round succeeds without one.
