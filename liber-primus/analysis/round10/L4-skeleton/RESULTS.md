# RESULTS — Round 10, Lane L4 (SKELETON EXTENSION), Test T1

Author: L4 armada agent (resumed run). Date: 2026-08-17.
Folder: `liber-primus/analysis/round10/L4-skeleton/` (write-only scope).

This document records **T1 — THE SCAN** (PREREG.md §2). T0 (positive control) and
T0b (detection floor) had already passed/completed before the interruption; T1 was
never run when the window crashed. This resumes and completes it exactly as
pre-registered.

---

## 1. What T1 tested

**H1**: LP2's unsolved plaintext (pages 0–54: 2,928 words / 12,956 runes / 458 ᚠ
interrupters, per-word ᚠ-histogram `[2506, 387, 34, 1]`) is a **contiguous passage**
of some text in the extended corpus, matched at the word-length-sequence level.

- **Corpus**: 224 unique texts, **22,643,594 words** (Round-8's 51 texts + the ~206
  recursively-globbed `data/keys/**` keytexts Round 8 never reached + fetched
  esoteric/hermetic/scripture sources; 20 duplicate files dropped by content-hash).
  Identical corpus to the validated T0 run (`positive_control_T0.json`).
- **Real pattern**: the true LP2 word-length sequence (loaded by `skel.lp2_words()`;
  verified this run: 2,928 words, 12,956 runes, 458 ᚠ, fc-hist `[2506, 387, 34, 1]`
  — matches PREREG exactly).
- **Matchers**: `exact` (slack 0), `slack1` (Round-8 symmetric ±1, for continuity),
  and the **directional interval** matcher (corpus length `v` matches word `i` iff
  `v ∈ [obs_i − fc_i, obs_i]`).
- **Null control**: the real sequence **shuffled** — a permutation preserves the exact
  length histogram and interrupter count, destroying only order (the sharpest possible
  null for this statistic). **4 independent shuffles** per matcher, scanned identically.
- Also windows **400** and **120** (interval matcher) on the first-W words for a
  partial-match probe, each with its own window-shuffled null.

## 2. Command run

```
cd analysis/round10/L4-skeleton/
python3 run_scan.py        # → scan_results.json, t1_scan.log
```

No methodology was rewritten; `run_scan.py` is the committed T1 runner and reuses the
same `skel` + `scanner` machinery the positive control (T0) validated. Scan wall time:
**4.7 min**. Fully completed — no bounding/capping was needed.

## 3. Pre-registered thresholds (PREREG.md §3)

| | PASS | FAIL |
|---|---|---|
| **T1** | Real best ≥ **60%** at W=2928 **AND** z ≥ **10** vs shuffled null **AND** a single coherent offset in one text | Real best inside the null band (z < 3), or above null but below the T0b detection floor → **NEGATIVE** |

A "suggestive" band `3 ≤ z < 10` was pre-declared **not a finding**.

## 4. Results — full window (2,928 words)

| matcher | real best | % | text @ offset | null max | null mean | **z vs null** |
|---|---|---|---|---|---|---|
| `exact` | 595 | 20.3% | keys/kg_bahir.txt @76253 | 606 | 598.3 | **−0.71** |
| `slack1` | 1482 | 50.6% | keys/kg_bahir.txt @76104 | 1486 | 1477.5 | **+0.70** |
| `interval` | 664 | 22.7% | keys/tyndale_new_testament.txt @145429 | 682 | 670.7 | **−1.03** |

Null = 4 shuffles of the real sequence. Every real best sits **inside its own shuffled
null band** — two of three matchers score *below* the null mean (negative z).

Partial-match windows (interval matcher):

| window | real best | % | text @ offset | null max | null mean | z |
|---|---|---|---|---|---|---|
| W=400 | 112 | 28.0% | data/war.txt @471572 | 111 | 110.0 | +2.00 |
| W=120 | 47 | 39.2% | keys/homer_iliad.txt @26860 | 50 | 49.0 | −2.00 |

Both partial windows are also inside the null band (|z| ≤ 2, below the 3 threshold).

### Length-ordering artifact confirmed (the PREREG §3 caution)
The real:interval per-text leaderboard is ordered by text length, exactly as PREREG
warned (Round 8's z=2.07 was this same effect). Top texts:

```
664.0 (22.7%)  keys/tyndale_new_testament.txt   (largest scripture)
662.0 (22.6%)  keys/kg_bahir.txt                (the NULL's own favorite text)
655.0 (22.4%)  keys/norse_njalsaga_dasent.txt
651.0 (22.2%)  keys/scripture_book_of_mormon.txt
651.0 (22.2%)  keys/scripture_quran_rodwell.txt
648.0 (22.1%)  keys/bible_douay_rheims.txt
647.0 (22.0%)  data/kjv.txt
```

These are simply the biggest texts (most offsets = highest max-of-many). `kg_bahir` is
the single text that also topped **both null matchers** in T0 and the real:exact scan
here — i.e. the leaderboard reflects corpus geometry, not a plaintext.

## 5. Instrument was NOT blind (T0, already on file)

For contrast, the same scan on a **planted** known passage (`positive_control_T0.json`):

| | planted best | % | null max |
|---|---|---|---|
| interval | 2928/2928 | **100.0%** | 825 (28.2%) |
| exact | 2506/2928 | **85.6%** | 725 (24.8%) |

Planted texts ranked **#1** at 100% (interval) with z ≫ 10. The instrument detects a
plaintext it is known to contain. The T1 real signal (22.7%, below null mean) is nowhere
near this floor — it is null-indistinguishable.

## 6. VERDICT — **NEGATIVE**

The real LP2 word-length sequence produces **no match above the shuffled-null band** in
any matcher at any window:

- Best real interval-match **22.7%** vs pre-registered PASS bar **≥60%** — fails by ~37 pts.
- Best real z = **+0.70** (slack1); the interval and exact matchers are **negative**
  (z = −1.03, −0.71). All |z| < 3, inside the pre-declared "not a finding" band.
- The top hits are the length-ordering artifact, not a single coherent offset.
- The planted positive control on the identical corpus lands at 100% / z ≫ 10, so this is
  a true negative, not a blind instrument.

**LP2's unsolved plaintext is NOT a contiguous, verbatim-ish, English-transliterated-to-
futhorc passage of any text in this 224-text / 22.6M-word extended corpus, at the
word-length-sequence level, under directional interrupter tolerance.**

### Scope of the negative (PREREG §4)
Covers: contiguous, verbatim-ish, English→futhorc plaintext from the enumerated corpus,
word-length level, directional interrupter tolerance. Does **not** cover: original Cicada
prose never published; a translation/recension not in the corpus; non-contiguous /
reordered plaintext; a language with a different transliteration convention; or a
word-boundary convention other than split-on-`-`-and-`.`. The T0b detection-floor number
`p*` (in `positive_control.json`) is what quantifies "verbatim-ish".

## 7. Coverage / what was and was NOT run

- **RAN & fully completed**: T1 as pre-registered — full 224-text corpus, all three
  matchers at W=2928, 4 shuffled nulls each, plus W=400 and W=120 partial probes with
  window-matched nulls. No capping. Output: `scan_results.json`, log `t1_scan.log`.
- **NOT run here (optional follow-on, T1b)**: `run_windows.py` — a sub-window sweep of
  **every** non-overlapping W=120 and W=400 slice of LP2 across the whole corpus (this
  T1 only probed the *first* 400/120 words). It closes the "a passage somewhere else
  inside LP2" hole. Given the full-length and first-window results are both flatly
  null, this is not expected to change the verdict, but to complete the lane exhaustively:

  ```
  cd analysis/round10/L4-skeleton/
  python3 run_windows.py     # → window_results.json  (~5 min, same machinery)
  ```
