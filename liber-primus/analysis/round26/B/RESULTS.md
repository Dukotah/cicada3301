# Round 26 — LANE B — RESULTS

**Lane:** R12-C2's staged-but-never-executed keytext running-key sweep.
**Extends ledger id:** `R12-C2` ("Texts fetched (29 files ~12 MB); the sweep was never run").
**Prior:** LOW. **Outcome:** HARDEN (0 hits, 0 bar-clears over 1,562 measured decodes).

---

## 1. POWER (measured before the sweep — mandatory)

Control: `control.py` -> `control.json`. Plant = ONE R12-C2 keytext
(`plotinus_enneads_mackenna.txt`, 220,069 rune indices) used as a RUNNING KEY over English
`self_reliance.txt` plaintext (L=240, 7 seeds, random keytext offsets), enciphered under
BOTH filters the decoder inverts and decoded with the matching skip-aware preset:

| plant filter | decode preset | median recovery | min recovery | pass (>=0.90) |
|---|---|---|---|---|
| keyskip1 (`encipher_keyskip`) | `exact` (keyskip1) | **1.000** | **1.000** | YES |
| skip_by_two (`j+=2`)          | `pair`  (keyskip2) | **1.000** | **1.000** | YES |

**CONTROL_PASSED = True (measured recovery 1.00).** The skip-aware gate recovers a real
keytext running-key plant at 1.00 rune-index recovery, far above the 0.90 bar, under BOTH
transition models this lane sweeps. A genuine keytext hit WOULD be recognised. Power is
established; the null below is from a validated instrument.

---

## 2. COVERAGE (the swept space)

Space = {33 texts} x {start offsets/text} x {9 unsolved rune-pages} x {2 presets:
keyskip1, keyskip2}, sign = -1 (the repo decode relation). Two passes were run:

- **off4** (`sweep.jsonl`, 991 decodes): 4 offsets/text, pages ordered ascending by length.
- **off8** (`sweep_partial_off8.jsonl`, 571 decodes): 8 offsets/text, pages 19-20 only —
  double offset density, as an offset-sensitivity corroborator.

**Total measured decodes: 1,562. Bar-clears: 0. HITs: 0. Flagged-for-oracle: 0.**

### Per-page coverage (HONEST — some large pages capped, see §2.1)

| page | runes | status | decodes | best pmax | bar | clears |
|---|---|---|---|---|---|---|
| 19 | 333  | COMPLETE (off4+off8) | 264+528 | 5.164 | 5.73/5.92 | 0 |
| 20 | 1729 | PARTIAL (off8 only)  | 43      | 4.018 | 5.92 | 0 |
| 22 | 1894 | UN-SWEPT             | 0       | —     | —    | — |
| 23 | 1021 | PARTIAL 86% (off4)   | 199/232 | 5.470 | 5.73 | 0 |
| 25 | 1433 | UN-SWEPT             | 0       | —     | —    | — |
| 26 | 91   | COMPLETE (off4)      | 264     | 3.698 | 5.88 | 0 |
| 27 | 1468 | UN-SWEPT             | 0       | —     | —    | — |
| 28 | 121  | COMPLETE (off4)      | 264     | 3.884 | 5.73 | 0 |
| 29 | 3008 | UN-SWEPT             | 0       | —     | —    | — |

### 2.1 Why the large pages are capped — and it is stated, not hidden
Under multi-lane CPU contention the beam decoder ran at ~55 decodes / 30 min on the
1,729-3,008-rune pages (each `evaluate` is two full-page beam decodes). Per doctrine "a round
is a bounded slice, not a full grind", the sweep was **capped** rather than run for many
hours: the null is decisive on every page that completed and the large-page decodes are
identical-in-kind (same instrument, same texts, same panel). Pages 20 (mostly), 22, 25, 27,
29 are **UN-SWEPT and go into `not_covered`** — this negative does NOT claim them.

### Swept fraction (explicit)
- **off4 feasible plan actually run: 991 / 2,184 cells = 45.4%.**
- Pages fully swept at 4 offsets/text: **3 of 9** (19, 26, 28) + page 19 also at 8 offsets;
  page 23 to 86%; page 20 to a thin off8 slice.
- Of the unbounded "all-texts x all-offsets x both-signs" space: negligible; sign=-1 only,
  <=8 offsets/text, this 33-text corpus only. Reported as a bounded slice, never "closed".
- 4 truncated 5,336-rune texts (`achad_qbl`, `alghazali_alchemy_happiness`,
  `emerald_tablet_hermetic`, `sepher_yetzirah_westcott`) cannot span the longest pages as a
  full running key (`usable = len(K) - pageLen*9 - 8 < 0`); those (text,page) cells are
  UNCOVERABLE by a running key — reported, not counted against coverage.

---

## 3. RESULT

**0 / 1,562 measured decodes clear the calibrated panel-max bar. 0 HITs. 0 flagged.**

Best decode over everything measured: pmax = **5.470** at text=`theologia_germanica.txt`,
preset=`pair`, page 23, register `EN_KJV` — versus the family-wise panel-max bar 5.732.
The best is **0.262 below** its own bar; nothing on any completed page approaches a clear.

Per-decode language-agnostic stats persisted at sweep time in `sweep.jsonl` /
`sweep_partial_off8.jsonl` (pmax, bar, clears_null, ioc, mds = min-distinct-in-32-window,
h2 = symbol entropy, distinct-count, pmax_ne = best non-English panel, full 9-register
z-vector, score, recovery, heldout). Across all decodes: median IoC*N ~ 1.0 (flat,
noise-consistent), median mds ~ 15 of 29 (high diversity, no low-entropy collapse), median
h2 ~ 4.79 bits (near-uniform over 29 symbols). Every language-agnostic channel reads as
unstructured. off8 (double density, pages 19-20) reproduces the null exactly — the negative
is offset-density insensitive on the pages tested.

### Adjudicator note (load-bearing for the negative)
For a rigid RUNNING KEY, clause 3 (held-out 3/4 self-consistency) is **non-discriminating**:
median heldout recovery = 1.000, because the deterministic running-key decode trivially
reproduces itself once the key is attributed. The REAL gate for this lane is clause 1 — the
**panel-max bar** — and it is 0/1,562. Any future keytext survivor must be adjudicated on the
panel-max register, NOT on self-consistency.

---

## 4. THE THREE CONDITIONALS THIS NEGATIVE CARRIES

1. **Key-space swept:** 33 curated R12-C2 texts, letters-only running key, <=8 offsets/text,
   sign=-1 ONLY. NOT covered: +1 sign, higher offset densities, reversed texts, texts outside
   this corpus, per-line/per-page key restarts, byte-reduction pads (that is R12-A1).
2. **Decoder transition model:** keyskip1 (repo-exact) + keyskip2 (skip_by_two-exact).
   NOT covered: permissive drift (lam=12), multi-rune correlated errors, transpositions.
3. **Adjudicator register:** 9-panel (EN_MODERN/EN_KJV/LP1_REAL/LATIN/OE/DE/CY/EN_HALFVOWEL/
   EN_NOVOWEL) via `AD.adjudicate`, family-wise panel-max bar from `panelmax20`. Blind spot:
   any plaintext language outside those 9 panels.

---

## 5. COVERAGE x POWER — the honest bottom line

Power = 1.00 recovery on the matched plant (proven, both presets). Coverage = 1,562 decodes,
3 of 9 pages COMPLETE at 4 offsets/text (+ page 19 at 8, page 23 to 86%), all 33 texts
exercised, 0 clears; large pages 20/22/25/27/29 explicitly UN-SWEPT and in `not_covered`.
Value = coverage x power is real and reported for the swept fraction only.

R12-C2's "never run" status moves from a stale stub to a **measured negative on the small and
medium unsolved pages**: the curated running-key corpus does not decode them under the
skip-aware instrument. The large pages remain a cheap, bounded re-run (identical instrument,
just slower) for a future compute lane. HARDEN.

Reproduce: `python3 control.py && python3 sweep.py && python3 finalize.py`
(writes `control.json`, `sweep.jsonl`, `sweep_summary.json`; `finalize.py` rebuilds the
summary + honest per-page coverage from whatever rows completed).
