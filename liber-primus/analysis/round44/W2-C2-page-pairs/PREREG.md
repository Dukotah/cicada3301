# Round 44 / WAVE-2 CELL C2 — ALL-PAIRS PAGE XOR / PAGE-AS-KEY-FOR-PAGE — PREREG

_Dated 2026-11-09, written BEFORE any execution of this cell (no plant, no decode, no sweep).
The only numbers computed in advance are (a) the bars_v3 thresholds from the committed fit
(`analysis/round34/I1-v3-null/bars_v3.py`), (b) read-only premise facts from canon (page count,
lengths, line-start counts), and (c) a throughput benchmark of `adjudicate_batch` on RANDOM
synthetic data (feasibility only, no canon decode). Doctrine binds (ARMADA-DOCTRINE.md). This
file is hash-stamped into `run.log` before the first run (R44 X1 hygiene fix). No `git commit`
from this cell._

## 0. What this cell is

The never-run "all-pairs page XOR and canon-as-key" parts of the Round 16 F-01 reading:
every unsolved page used as a mod-29 running key over every other unsolved page (page-as-pad),
and the full canon stream used as a running key over every unsolved page, at line-start and
offset-swept alignments, adjudicated under the standing panel-R36 + bars_v3 instrument.
"XOR" in rune space = the mod-29 additive group: the family of decodes
`p[m] = eps_j*C_j[t+m] + eps_i*K_i[o+m] + s (mod 29)`.

## 1. Cited ledger rows (LEDGER.json queried 2026-11-09 before writing; 322 entries)

- **R40-C1-R47-F01-LP2-AS-PAD** (negative) — `not_covered` verbatim: "T4 AN-END hash (63
  values < L=120) and T5 payload (absent); **all-pairs page XOR and canon-as-key parts of the
  reading**; other target objects; windows beyond 500 runes". This cell is exactly the bolded
  clause. The covered part (LP2 fwd/rev/atbash/neg as pad over T1/T2/T3/T6 at windows
  0/120/240/360) is NOT re-run: none of my cells key a page with the LP2 head over 2012-13
  texts / solved LP1 / PGP bodies; my keys and ciphertexts are both unsolved-canon pages (or
  the canon stream over unsolved pages — the T6 overlap is only the degenerate self-key
  diagonal, which F-01 already measured as degenerate and which I EXCLUDE: i == j cells are
  skipped, and canon-as-key cells where the key window overlaps the target page are computed
  but reported separately as `self_overlap` and excluded from the verdict family, matching
  F-01's handling).
- Wave-1 context: `round44/CAMPAIGN-PLAN.md` (P-lanes are presentation channels; this cell is
  the deferred cipher-space remainder named open by the W2 tasking). F3 (Round 16) measured
  cross-page kappa (coincidence) at offset 0 only — a statistic, not a decode; no decode rows
  exist for any page-pair key construction at any offset.
- **R44-R1-SEVENGRAM** (measured): the p27:28 / p54:70 repeated 7-gram is the only repeated
  7-gram in canon (expected 0.005). A page-as-pad relation between p27 and p54 is one
  construction that produces repeated ciphertext n-grams from repeated plaintext or repeated
  key material; the (27,54)/(54,27) pairs run FIRST and are reported individually.
- Non-overlap check: the bash-orbit / artifact-key rows (R32-B1, R34-B1, R37-I2, R40-B1/B2,
  R40-C1-R30-B1) sweep generator/artifact key STRINGS, not canon pages, under keyskip beam
  relations; R44-R1 swept 51 standing streams under reset phases — canon pages as keys are in
  none of them (R44-R1's key roster is generators + solved-page-derived streams, not raw
  unsolved pages).

## 2. The Aiming Test

**Q1 — What would a hit look like, and would THIS instrument recognise it?**
A hit = a (ct page, key page or canon offset, relation, direction, shift, offset) cell whose
decode is non-degenerate and crosses the fixed bars_v3 free bar under panel-R36
(`round19/I2/adjudicate.py` + `data/panels/panel-r36.npz`, 12 registers). Recognizer = exact
argmax + bar comparison over the sweep. Plants: THREE synthetic ciphertexts built by
enciphering real register text (EN_KJV, LATIN) with a REAL canon page (and, for the canon
lane, the real canon stream) under in-family cells — including a reversed-key, nonzero-shift,
line-start-offset cell — pushed through the IDENTICAL runner. Pass = each plant is recovered
at exactly its planted coordinates (argmax over that ct page's cells), crosses its bar, and is
non-degenerate. If any plant fails: INSTRUMENT-INCOMPLETE, no verdicts.

**Q2 — What measured fact raises the prior above flat?**
(a) The clause is a named `not_covered` remainder of a validated lane (R40-C1-R47-F01), i.e.
the open part of a reading the ledger says was never run — closure work, not a fresh flat
sweep. (b) R44-R1-SEVENGRAM: a <<1-in-200 repeated 7-gram joins p27 and p54; page-pair keying
is a construction class that can produce exactly that signature, and no row has ever decoded
a page under another page as key at ANY alignment (F3 measured only offset-0 coincidence).
(c) Honest label: beyond those two facts this is completeness work on a bounded enumerable
family; it is queued in wave 2 accordingly.

**Q3 — Is the space bounded, and by what?**
Enumerable and fully run. Pair lane: 55x54 = 2,970 directed pairs x key direction {fwd, rev}
x sign pattern {sub, add, negadd} x shift {0, +1, +28} x offsets ({0..29} UNION key-page line
starts > 29; measured mean 38.8/page) = 115,236 x 18 ~= 2.07M cells (cells with usable window
L < 60 skipped and counted). Order-swap closure: beau (p = K_i - C_j) = sub of the swapped
ordered pair; atbash-on-key = the opposite sign pattern plus shift +-1; neg-key sub = add —
so {fwd,rev} x {sub,add,negadd} x {0,+1,+28} over ORDERED pairs spans the full closure of
F-01's variant set {fwd, rev, atbash, neg} x {vigenere, beaufort, add}. Canon lane: key =
full 13,136-rune canon (fwd only), ct = each of the 55 pages, offsets 0..(13136 - len_j),
x {sub, add, negadd} x {0,+1,+28} ~= 6.4M cells. Total ~= 8.5M decodes; bars fixed at
N_bar = 16,000,000 >= any actual N. Measured throughput 178k panel rows/s: minutes.

**Q4 — The three conditionals** — see §6.

**Q5 — Kill condition at 10% of budget.**
(i) Any plant fails its pass criterion -> INSTRUMENT-INCOMPLETE, stop, no verdicts.
(ii) Premise re-verification fails (57 canon pages; unsolved lens min 66 / max 277 / sum
12,956; 7-gram at p27:28 and p54:70) -> UNAVAILABLE-BY-PREMISE, stop.
(iii) Sanity checkpoint after the (27,54)+(54,27) pairs + the first 5 key pages: if the
pmax distribution is pathological (constant, or median outside [-3, +6]), stop and debug the
instrument before continuing. Checkpoint order: plants -> premise -> p27/p54 pairs -> full run.

## 3. Fixed design

- **Masters**: canon = `data/krisyotam_runes.txt` via the R44-R1 validated parser
  (`analysis/round44/R1-key-resets/resets.py: parse_pages`, 57 pages). Unsolved = pages 0..54.
- **Decode family**: `p[m] = eps_j*C_j[t+m] + eps_i*K[o+m] + s (mod 29)` with
  sub = (+1,-1), add = (+1,+1), negadd = (-1,-1); s in {0, 1, 28}; t = 0 always (ct read from
  page start; ct-side line-start alignments are covered via the ordered swap, see Q3).
- **Pair lane**: K = page_i (i != j), direction fwd or rev (rev = reversed rune sequence of
  page_i, offsets indexed into the reversed stream). Offsets o in {0..29} UNION {line starts
  of page_i > 29}. Window L = min(len_j, len_i - o); skip if L < 60.
- **Canon lane**: K = all 57 pages concatenated (13,136 runes), fwd only, o in
  0..(13136 - len_j), L = len_j. Cells whose key window [o, o+len_j) overlaps the ct page's
  own canon interval are computed but tagged `self_overlap` and excluded from the verdict
  family (reported separately).
- **Adjudication**: `adjudicate_batch` (panel-R36, 12 registers) pmax for every cell; full
  `adjudicate` (14-field SWEEPROW stats incl. ioc/mds/h2/zl, degenerate flag) for the top 100
  rows per lane and every bar-crosser. Doctrine R3 stats are persisted for all full-adjudicated
  rows; per-cell pmax summaries (per family: count, max, argmax coordinates, quantiles) are
  persisted for the whole sweep.
- **Order**: plants, premise, pairs (27,54) and (54,27) first (reported individually), then
  all pairs, then canon lane.

## 4. Fixed thresholds (computed 2026-11-09 from the committed fit, before any run)

- Bar of record: `bar_v3(16_000_000, L_node, "free")` (free relation, panel-R36 12-register
  node; these are direct decodes, no beam, no skips — the same instrument choice as
  R44/W2-A2's crib sweep):
  - L_node = 120 (cells with L < 240): **16.7816**
  - L_node = 240 (cells with L >= 240): **22.6382**
- Cells with L in [60, 120) are compared against the 120 bar; the free fit has no node below
  120, so for these short cells the bar may be slightly lenient — acceptable because a crosser
  is only ever FLAGGED-FOR-ORACLE (HUMAN-ORACLE.md), never certified, and the flag triggers a
  full-adjudicate + manual inspection anyway.
- Degenerate guard: `adjudicate(...)["degenerate"]` (standing R38 I2 guard). Degenerate
  crossers are reported but do not flag.
- Verdict rule: NEGATIVE iff no non-degenerate cell reaches its bar; any non-degenerate
  bar-crosser -> FLAGGED-FOR-ORACLE, loudly, per HUMAN-ORACLE.md. No threshold edits after
  results; addenda only, dated.

## 5. Plants (through the cell's OWN runner, before any real target)

- **Plant A** (pair lane, fwd): EN_KJV plaintext (letters -> rune indices via
  `gp.keyword_to_indices`, from `data/kjv.txt`), length 200, enciphered so that sub with key
  page 13 fwd at a LINE-START offset > 29 of page 13, shift 0, recovers it. Injected as an
  extra ct page through the identical pair runner.
- **Plant B** (pair lane, rev + shift): LATIN plaintext (`analysis/latin/latin_28233.txt`),
  length 150, enciphered for add with key page 40 REVERSED at offset 17, shift 1.
- **Plant C** (canon lane): EN_KJV plaintext (a different passage), length 180, enciphered for
  sub with the canon stream at offset 7,001, shift 0, through the identical canon runner.
- Pass (all three required): recovered at EXACTLY the planted coordinates (argmax over the
  plant ct page's cells), pmax >= the fixed bar, non-degenerate; and for each plant the
  runner's second-best non-planted-coordinate cell on that ct page stays below the bar OR is a
  shift/offset neighbour of the plant (documented if so).

## 6. three_conditionals (what a negative here is conditional on)

1. **key_space**: unsolved canon pages 0..54 as running keys over each other (ordered pairs,
   fwd/rev, sub/add/negadd closure = F-01 variant closure, shifts {0,1,28}, offsets {0..29}
   UNION key line starts) + the fwd canon stream over each unsolved page at all offsets, same
   relations/shifts. NOT: reversed/atbash canon stream lane, shifts outside {0,1,28} (full
   Caesar layer), key-stream interrupter/skip models, ct windows other than page start
   (beyond what the order-swap closure covers), solved pages as keys, multi-page composite
   keys.
2. **transition_model**: exact position-wise group operation (no beam, no skips, no
   interrupters, no autokey). A construction with null-F interrupters or skip rejection is
   NOT represented.
3. **adjudicator_register**: panel-R36, 12 registers (EN_MODERN, EN_KJV, LP1_REAL, LATIN, OE,
   DE, CY, EN_HALFVOWEL, EN_NOVOWEL, + R36 additions), pmax vs bars_v3 free bars at
   N_bar = 16e6; languages/orthographies outside the panel are invisible.

## 7. Outputs

`pair_results.json`, `canon_results.json`, `plant_pair.json`, `plant_canon.json`,
`RESULTS.md`, `ledger_rows.json` (draft; schema per tasking: positive_control "passed" +
control_detail, threshold_fixed_in_advance true, status from the controlled vocabulary),
`run.log` (hash-stamped). Scripts: `c2lib.py`, `plant_run.py`, `run_pairs.py`, `run_canon.py`.
Pure python3 + numpy, no network.
