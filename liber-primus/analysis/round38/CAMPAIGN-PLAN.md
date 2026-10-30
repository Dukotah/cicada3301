# Round 38 — THE REMAINING MASS (pre-registration / plan of record)

_Drafted 2026-10-30 as Round 37 closed. Binding doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Seeded
by Round 37 X1's critic list, the Round 36 O4 matrix recount after Round 37, and the standing hardware-bound queues.
Each lane's `PREREG.md` is authoritative once written and is dated before its first output; addenda go in a separate
dated file._

## 0. Thesis — the instrument is at its measured ceiling; what is left is mass, not method

Six rounds of instrument repair end with a decoder that searches twelve registers, a head screen with ≥0.95 power in
every one of them, an observed null for every relation at every length that matters, a reproducible panel as the
engine gate, and a front-door oracle that would recognise a non-English solve. The clue readings the owner suspected
were never tried are now tried: the composed map → road → direction rule, the first part's numbers as a schedule, the
2016 clauses as seeds, the book-code indices, and every English-only clue reading, all negative under that instrument
with planted controls. The recurring near-miss is noise on three verifiers plus a length-matched `free` null.

What remains is of three kinds, and the round is sized to each honestly:

1. **Mass the instrument can now reach but has not been pointed at.** The Py2.7-MT S2 sweep (54.6 % of 2³² still
   unswept, verified engine, reproducible gate) and the PHP `mt_rand` 2³² tails (99.4 % per cell). These are enumerable
   and the sandbox is a second machine; the honest unit of work is a *window* with a stated fraction, never "finish".
2. **Readings the matrix still marks NEVER after Round 37** (recount in `round37/X1-redteam/RESULTS.md`) that have a
   literal clue basis and a bounded encoding — chiefly the *semantic* reading of "their meaning is the road", which C1
   left untested because no lore-free definition of "meaning" was in hand. One can be defined without lore: a fixed,
   public, versioned lexical resource (WordNet synset offsets; or a frequency-rank table) applied deterministically,
   with the definition frozen in PREREG and a planted control. That is a reading, not a prior; it runs at C1's cost.
3. **Instruments that failed their own control and are therefore unmeasured, not negative**: the per-page geometry
   reading (U8: no glyph recognizer with power), and the X4 derived-key family (C3: bars transferred from random-key
   nulls, no bespoke null). Each gets one bounded attempt to build the recognizer; failure again is a recorded ceiling.

**Not a target:** new generator families; seal (D5c) work, paused since Round 36; O1 (no page-0 source).

## 1. Doctrine budget allocation

| share | goes to | lanes |
|---|---|---|
| **≈40%** | enumerable mass, windowed, on the sandbox — S2 and PHP | S1, S2 |
| **≈30%** | the semantic reading + the remaining NEVER cells | C1, C2 |
| **≈15%** | the two unmeasured instruments | I1, I2 |
| **≈15%** | red-team + closeout | X1 |

## 2. Lane roster

| ID | Type | Title | Compute | Gates on |
|---|---|---|---|---|
| **S1** | sandbox sweep | S2 (Py2.7-MT `exact`): validate the planted exact-relation control independently FIRST (Round 36 S1's open item), re-score `top_S2.json` under panel-R36, export the Round 36 snapshot lists, then ≥2 windows of ≤45 min each; coverage stated per window | sandbox | — |
| **S2** | sandbox sweep | PHP `mt_rand` tier (b) continued on the sandbox under pf_v4_12 + beam_v3 + panel-R36: blocks 200–318 of the R32 stream first (so the seed set grows), then a fresh `default_rng(3302)` stream; windows of ≤45 min; rows persisted and downloaded | sandbox | — |
| **C1** | bounded (flagship) | The semantic "road": "meaning" defined by a frozen public lexical index (WordNet 3.1 synset offset; and, as the alternative, a COCA/BNC-style frequency rank — both versioned, hashed, no lore), composed with C1-R37's map/direction machinery; planted control; ≈5–10k decodes | ~1 h laptop | — |
| **C2** | bounded | The remaining O4 NEVER cells with a literal basis (from the X1-R37 recount): each gets a one-paragraph PREREG, a planted control, and ≤1k decodes; cells without a literal basis are recorded as "no operation stated" and closed as such | ~1 h laptop | — |
| **I1** | instrument | A glyph recognizer with measured power for per-page geometry: stroke-aware, rotation-invariant (Hu moments / closure / stroke count) tested on planted glyphs in LP2 page noise; required ≥0.9 detection at FPR ≤0.05 on 200 shuffles; then re-score U8-R37's 232 renders | light | — |
| **I2** | instrument | X4 bespoke null: re-derive the key from each shuffled stream (not a random key) for the Round 22-C X4 family; re-judge the X4 rows; add a planted X4 control | light | — |
| **X1** | red-team | this round; the S1 control validation; the C1 "meaning" definition (is it lore-free and frozen?); Round 39 critic | light | last |

## 3. Lanes in detail

All decode lanes: `beam_v3` (panel_max, `set_panel("data/panels/panel-r36.npz")`), keyskip1 + keyskip2 (+ `free`
where I1-R37 licensed it: L=240 for 10 registers, L=400/729 for all 12), bars from `round34/I1-v3-null/bars_v3.py`
(keyskip) and its `free` extension, or `round36/B1-orbit-12reg/null12.json` (12-register keyskip at L=120), 12-wide
SWEEPROW rows (stock validation since T1-R37), PREREG before the first output, planted control before the null, no
`git`, RESULTS.md + ledger.json written before the lane replies.

---

### S1 — S2 windows, done properly  _(sandbox)_

- **Q1.** (a) The planted exact-relation control: generate a Py2.7-MT keystream for a known seed under `exact`, encipher
  a known plaintext, run the engine's own stage path on it, and show the engine recovers it and scores it above the
  claim bar — done INDEPENDENTLY of the engine's `GRIND27_S2_CONTROL_OK` flag (Round 36 S1 listed this as the one
  unvalidated piece). (b) Re-score `top_S2.json` (Round 19-scored) under panel-R36 so the top list is one instrument.
  (c) Export the Round 36 snapshot's `top_S2.json`, `hist_S2.u64`, `candidates.jsonl` to the lane dir (the snapshot
  expires ~2026-11-06). (d) Windows: resume from `state_after/` cursors, ≤45 min each (the session cap), ≥2 windows,
  snapshot state before/after each, report seeds advanced and fraction per window, crossers ≥7.6342 → local v3
  L=240 re-screen under panel-R36 → flagged-for-oracle; near-misses ≥7.5342 listed.
- **Q2.** Highest-prior parked enumerable sweep in the repo; engine verified (R34 S1), gate reproducible (R36 P1),
  one window already run clean (R36 S1).
- **Q3.** Enumerable; this lane covers ≈2.5 pp per 2-vCPU window-pair; the remainder stays parked with its fraction.
- **Q5.** Control (a) fails → stop; S2 stays parked; record exactly what failed.
- **Deliverable.** `round38/S1-s2-windows/` — `control_exact.json`, `top_rescored.json`, `exported/`, per-window
  `state_before_k/`, `state_after_k/`, `RESULTS.md`, `ledger_patches.json` (R27-CPORT-MT32-FULLSWEEP coverage per
  instrument).

---

### S2 — PHP tier on the sandbox  _(sandbox)_

- **Q1.** Natural-rate control through the real chunk path on the sandbox (≥10 EN_MODERN + ≥10 EN_NOVOWEL + ≥10
  HEBREW per cell × relation) with pf_v4_12 → beam_v3 → panel-R36; PHP-cell FPR under the 12-register thresholds
  measured on 2^17 wrong-key heads per cell (I2-R37 left it not_covered).
- **Q2.** `ELIMINATION-LEDGER.md` names PHP `mt_rand` the highest-prior open generator; three laptop attempts reached
  ≤1 % of 2³² per cell; the sandbox is a second CPU.
- **Q3.** Windows: blocks 200–318 of the R32 `default_rng(3301)` stream (new seeds), then a fresh `default_rng(3302)`
  stream; ≤45 min per window, ≥2 windows; rows persisted (append mode) and downloaded; fraction stated per cell.
- **Q5.** Control fails → fix the harness, no coverage claim.
- **Deliverable.** `round38/S2-php-sandbox/` — `control.json`, `fpr12_php.json`, `sweep_rows.jsonl` (downloaded),
  `RESULTS.md`, `ledger_patches.json` (R32-B2 / R36-B2 extension with the honest "seeds added" count).

---

### C1 — The semantic road  _(flagship bounded lane)_

- **Q1.** Freeze in PREREG: the lexical resource (WordNet 3.1, the exact file + sha; frequency table, exact file + sha),
  the mapping "LP1 word → sense index" (first synset offset of the lemma; or frequency rank), the reduction to a
  direction (offset mod 29 / mod 28; rank mod 29), the application (per-word additive shift / cumulative / key-pointer
  advance at cleartext word boundaries — reuse `round37/C1-composed-clue-readings/enciphers_u2_u3.py`), the start
  index range, and the planted control (encipher a known plaintext under each variant; the matching decoder recovers
  ≥0.90). Then search pages 0–2 at L=120 under panel-R36; any clearer → L=240 → oracle bundle.
- **Q2.** The clause "their meaning is the road" is signed and verbatim (`round36/O4-clue-coverage/clues.json`); C1-R37
  tested only positional and length stand-ins for "meaning" and said so; this is the literal reading, defined without
  lore (a public dictionary is not a Cicada prior).
- **Q3.** Bounded: ≤10 variants × ≤3 pages × ≤500 start indices ≈ 5–10k decodes.
- **Q5.** Planted control not recovered → that variant is INVALID, not negative.
- **Deliverable.** `round38/C1-semantic-road/` — `PREREG.md`, `lexicon_manifest.json` (files + hashes), `enciphers.py`,
  `sweep.py`, `control.json`, `sweep_rows.jsonl`, `RESULTS.md`, `ledger.json`, `ledger_patches.json` (O4 matrix cell
  reclassified).

---

### C2 — The remaining NEVER cells  _(bounded closure)_

- **Q1–Q5.** From the X1-R37 recount: for each NEVER cell with a stated operation, a one-paragraph PREREG (recognizer,
  prior = the clue text, bound, kill), a planted control, ≤1k decodes, 12-wide rows; for each NEVER cell with no
  stated operation (O4 counted 38 such in Round 36), record "no operation stated — not a lane" so the matrix stops
  carrying them as open. Deliverable: `round38/C2-never-cells/` with one subdir per cell run, a `closed_no_operation.md`
  list, `RESULTS.md`, `ledger.json`, `ledger_patches.json` (O4 reclassifications).

---

### I1 — A glyph recognizer with power  _(instrument)_

- **Q1.** Five planted glyphs (U8-R37's) in LP2 page-0 noise must be detected ≥0.9 at FPR ≤0.05 against 200 shuffles by
  a stroke-aware, rotation-invariant recognizer (segment the polyline into strokes; closure; stroke count; Hu moments of
  the rasterised path; template distance on the normalised stroke sequence). If it passes, re-score U8-R37's 232
  renders (`round37/C2-recognizer-index-readings/U8-geometry/`) and report. Q5: fails → record the measured ceiling;
  U8 stays inconclusive and is retired from the queue.
- **Deliverable.** `round38/I1-glyph-recognizer/` — `recognizer.py`, `power.json`, `rescore_u8.json`, `RESULTS.md`,
  `ledger.json`.

---

### I2 — X4 bespoke null  _(instrument)_

- **Q1.** For the Round 22-C X4 family (`prime_index/atbash_pre/...`), build the null by re-deriving the key from each
  shuffled stream exactly as the family derives it from the real stream (≥2,000 draws), plant an X4 control, re-judge
  the X4 rows from C3-R37 against that null; also re-check the degenerate-decode filter (does any real row it removed
  clear the bespoke bar?). Q5: none — this is a measurement.
- **Deliverable.** `round38/I2-x4-null/` — `null_x4.json`, `control.json`, `rejudged.json`, `RESULTS.md`, `ledger.json`.

---

### X1 — Red-team  _(last)_

Targets: S1's exact-relation control (independent of the engine flag? planted correctly?); C1's lexicon definition
(frozen before any decode? lore-free? the mapping deterministic?); C2's "no operation stated" closures (any with a
literal operation missed?); I1/I2 controls; the ledger patches; the O4 matrix final recount; the gate; Round 39 critic
list.

## 4. Verification and hit protocol
As Rounds 32–37 with `HUMAN-ORACLE.md`: any crosser produces the bundle and waits for the owner to read two
independent pages as language before any status moves.

## 5. Recorded, not blocking
- Sandbox snapshots: Round 34's (~2026-11-05) and Round 36's (~2026-11-06, holds the only copy of the panel-R36 S2
  histogram/top list until S1 exports them).
- The `round29/L4-image-forensics/fingerprints.json` stray file.

## 6. Orchestration
- **Wave A (parallel):** S1 and S2 (sandbox, independent sessions if the tool allows; else sequential), C1, I1, I2
  (laptop: at most two heavy processes; C1 is the heavy one).
- **Wave B:** C2 (after X1-R37's recount is read; laptop).
- **Wave C:** X1; coordinator closeout (SYNTHESIS, ledger, nav docs, gate, commit to master, push).
Discipline unchanged: Sonnet; no `git` in lanes; own `round38/<lane>/` dir; nproc=1; stream to disk in append mode;
no `find /`; PREREG dated before first output; RAM check before heavy runs; stores gitignored.

## 7. Guardrails — do NOT re-run
Everything in Rounds 32–37 §6/§7; the bash orbit (R35-B1, R36-B1, R37-I2 — three negatives, the last at reach ≥0.95
in all twelve registers); the composed-rule variants C1-R37 ran; the Round 10/11/22-C re-scores (C3-R37).

## 8. Definition of a good Round 38
S2 and the PHP tier advance by stated fractions under one instrument on a second machine, with a validated control;
the literal semantic reading of "meaning" is run under a frozen, lore-free definition; the matrix's NEVER column is
either run or closed as "no operation stated"; the two unmeasured instruments either gain power or record their ceiling.
A survivor would be extraordinary; the round succeeds without one.
