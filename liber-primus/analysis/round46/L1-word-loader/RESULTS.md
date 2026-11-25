# Round 46 / L1 — one correct printed-word loader, and the ten word-indexed rows re-measured: RESULTS

_2026-11-24. Pre-registered in `PREREG.md`. Its sha256 (`8cf2c0ca…`) was stamped in `run.log` before the first script ran.
No addenda. `tests/validate.py` passed at lane start. Merged numbers are in `results.json`, ledger rows in
`ledger_rows.json` (5 rows, `R46-L1-…`). No decode sweep was run. Nothing crossed a bar, so nothing is flagged for the
oracle._

## 0. Headline

- **The loader is right.** `words.py` gives **2,896 LP2 words**, exactly the target. The stream sha256 matches
  PROBLEM.json, and the page lengths match the dataset. The loader joins **420 wrapping words** (388 across a line,
  32 across a page). The tests pass 10/10: the stream hash, the word count, and *A WARNING* (atbash) and *PARABLE*
  decoded word by word against the reference.
- **Reconciliation is exact.** No legacy loader misses a single `words.py` boundary.
  - R41's `camp7` = 3,316 = 2,896 + 420 extra cuts (388 at `/`, 32 at `/%`).
  - R37/R38/R39's `mapcommon` and SKELETON's `lp2_words` = 2,928 = 2,896 + 32 extra cuts at `/%`.
- **R41-R14 was weakened before (page-level power ≈ 0.64 by its own score rule; ≈ 0 for W2/W3). It is now a
   full-power negative.**
  - Plants on LP2's real layout through camp7 recognise **2 / 1,760** pages (mean page recovery 0.48).
  - Through `words.py` they recognise **1,760 / 1,760** under (a) and **1,760 / 1,760** under (b).
  - Real re-run: W p(Z)/p(raw) = 0.249/0.262; P = 0.858/0.781. No crossing.
- **SKELETON (C-01) lost half or more of its power to the 32 page-wrap splits, even with true spaces.**
  - Legacy power is 10/20 at W120 and 5/20 at W400. `words.py` gets 20/20 at both.
  - The real re-run over 53 texts / 8.21 M words is at chance: best 20.2 % exact match, against ~100 % for a true hit.
- **R37/R38/R39 were barely affected.** Decoded-head boundaries are identical. Only U3 rho3 on pages 1–2 changes
  (those pages open mid-word). Those 928 decodes were re-run; the best is 4.35, below every bar.
- **Under (b), plaintext words shuffled within sentence,** every key-schedule row keeps full power. The rows that
  model word *order* — SKELETON — fall to 0.
- **Under (b′), printed lengths permuted within sentence** (the plan's "spaces shuffled"), every word-indexed row
  falls to ≤ 0.033 (7-gram shape 0.033; all others 0).

## 1. The loader (`words.py`, `test_words.py`, `reconcile.py` → `reconcile.json`)

**Rule.** Words break at `- . & $ §` and at digits. They do not break at `/`, `%`, or whitespace. A word records its
page, line, sentence, paragraph and section, plus `wraps_line` and `wraps_page`. The page and line where a word ends
come from its last rune; that fixed a first-draft count of 452/34 that counted a line opening with `-` as a wrap.

**Pins.** `dataset/liber_primus.json` pages 0–54 = krisyotam's first 12,956 runes; sha256 `023312066d…`
= PROBLEM.json. No word straddles rune 12,956. LP1 has 694 words and the solved tail has 45, both reproducing
R45-W1's calibration.

| loader | LP2 words | extra cuts vs words.py | where | missing |
|---|---:|---:|---|---:|
| **words.py** | **2,896** | — | — | — |
| R41 `camp7.word_pages` | 3,316 | 420 | 388 `/⏎`, 32 `/⏎%⏎` | 0 |
| R10/R37–R39 `mapcommon.parse` | 2,928 | 32 | `/⏎%⏎` | 0 |
| SKELETON `lp2_words` | 2,928 | 32 | `/⏎%⏎` | 0 |

`mapcommon` ignores `&` and `$` (X1 noted this). On the real text that has **no effect**: every `&` and `$` sits next to
a `-` or `.`.

**Solved-page tests.**
- *A WARNING*: the first 45 LP1 printed words, atbash-decoded, equal the reference words rune-for-rune. The page
  contains line-wrapped words.
- *PARABLE*: the last 20 solved-tail words equal the reference rune-for-rune.
- All 739 solved printed lengths align with the reference.

## 2. Plant protocol on LP2's real layout

Sentences from `data/pride.txt` (EN mapping of B6 `text_to_runes`) are laid over the 12,956 rune slots. The rendering
puts `-` between words, `.` at sentence ends, `/⏎` at every LP2 line-break position and `/⏎%⏎` at every page-break
position. Words therefore wrap lines and pages wherever LP2's geometry forces them to.

| regime | what it plants |
|---|---|
| **(a)** | words in order |
| **(b)** | words shuffled within each sentence before encipherment; the print shows the encipherer's words |
| **(b′)** | words in order, but the printed length list is a within-sentence permutation |

Each lane's own encipherer runs on the true word sequence. Decoders get words parsed from the rendered text, by
`words.py` (**L**) and by the lane's legacy rule (**O**).

## 3. Measured power (L = words.py, O = legacy loader)

| instrument | recognition rule | a / L | a / O | b / L | b / O | b′ / L |
|---|---|---|---|---|---|---|
| R41 R14 W1–W4 (pages) | exact page AND pmax > P null max 5.591 | **1760/1760** (32/32 streams, Wilson ≥ 0.89) | 2/1760 exact∧score; 1129/1760 score-only (R46-X1) | **1760/1760** | 1/1760 | 0/1760 |
| R41 R14 W1–W4 (whole stream) | exact AND pmax > W null max 1.416 | 32/32 | 0/32 | 32/32 | 0/32 | 0/32 |
| R41 W5 (space-blind control) | same, pages | 440/440 | 111/440 ¹ | 440/440 | 111/440 | 95/440 ¹ |
| R37 U2b (page-0 + page-1 heads) | `sweep.judge()` | 64/64 | 64/64 | 64/64 | 64/64 | 0/64 |
| R37 U3 (all rho) | `sweep.judge()` | 48/48 | 45/48 | 48/48 | 45/48 | 0/48 |
| R37 U3 rho3, page-1 head (opens mid-word) | `sweep.judge()` | 8/8 | 5/8 | 8/8 | 5/8 | 0/8 |
| SKELETON W120 | argmax at offset AND > 5 shuffled | 20/20 | 10/20 | 0/20 | 0/20 | 0/20 |
| SKELETON W400 | same | 20/20 | 5/20 | 0/20 | 0/20 | 0/20 |
| R44 7-gram shape | P(true 3\|3\|head \| printed 3\|3\|head) | 1.000 | 0.978 | 1.000 | 0.977 | 0.033 |

¹ W5 resets per page (`prev = 0`). Whenever the page grouping differs from the encipherer's, a page's first runes go
wrong (recovery 0.993, not exact). Here, the encipherer grouped words by the page each word *starts* on.

Median page pmax for R41 exact pages: 26.5 under (a) and 25.7 under (b). Shuffling words costs the panel almost
nothing (as in I1). For R37 the median pmax240 is 25.9 under (a) and 27.2 under (b).

## 4. Real-data re-runs

**R41 R14** (`r41_judge.json`).
- Setup: 20 variants × 55 pages + 20 whole-stream units on the 2,896-word segmentation. Each word belongs to the page
  it starts on. The blockperm null used D = 400 per block. The 20-draw probe projected 43 min per block at D = 1000, so
  the PREREG rule chose D = 400.
- Level W: best 0.843; p(Z) by block 0.234 / 0.249 / 0.020; p(raw) 0.165 / 0.187 / 0.262. Decision 0.249 / 0.262.
- Level P: best 3.752 (W1 s−1 atb p39); decision p(Z) 0.858, p(raw) 0.781.
- α = 0.0025, so nothing crosses.
- Top-5 page units: ioc·N 0.98–1.08, min-distinct₃₂ 14–17. Not degenerate.
- Faithfulness check: the same scorer on R41's own split segmentation reproduces R41's recorded best page, **3.642**.

**R37 U2b/U3 and the rho1 rows** (`r37_results.json`).
- Inside the decoded heads of pages 0–2 (240, 240 and 201 runes), word boundaries are identical under both loaders.
- Pages 1 and 2 open mid-word. The fragments are 5 of 6 runes and 2 of 5 runes.
- Under R37's "key restarts per page" convention, the fragment is word 0 of the page in both loaders. Only the rho3
  length value d₀ changes (fragment length vs full printed length).
- Re-decoded: all 928 U3 rho3 jobs on pages 1–2.

| relation | best re-decode | bar at actual N |
|---|---:|---:|
| ks1 | 4.352 | 6.632 |
| ks2 | 3.843 | 6.529 |
| direct | 3.697 | 6.895 |

  No gate run was needed.
- U2b, U3 rho1/rho2, and R38-WORDNET/FREQRANK and R39-SENSE (rho1, word index only) give real decodes identical by
  construction.

**SKELETON** (`skeleton_real.json`; `wordlen_search` glob; 53 texts, 8,206,267 words).

| window | words.py best | words.py z | legacy best (reproduces the record) |
|---|---|---:|---|
| full | 584 / 2,896 (20.2 %, mabinogion) | 1.54 | 581 / 1,441 (KJV) |
| 400 | 25.0 % | 1.41 | — |
| 120 | 34.2 % | 1.40 | — |

The "beats all shuffled" flag flips between loaders and slacks. It is a single-shuffle-per-text comparison, so that
is noise. A true plaintext would sit near 100 %. The shuffled null is weak
(one shuffle per text; the full-window real best 584 exceeds all 53 shuffled maxima, z 1.54); the negative
rests on the distance from the planted-hit level (20/20 at ~100 %), not on the null.

**R44 7-gram sites** (`sevengram.json`). Both sites read `001001` and start a word under both loaders. Site B's
page break at offset 6 carries a printed separator, so the shape is unchanged.

## 5. Corrected verdicts for the ten I1-reopened rows

| row | real-data under the new loader | power (a) | power (b) | power (b′) | verdict |
|---|---|---|---|---|---|
| **C-01** SKELETON | re-run, chance (20.2 %) | 1.00 (legacy 0.25–0.50) | **0.00** | 0.00 | negative holds under (a) for the resident corpus. The old negative was **weakened** even under true spaces. **CONDITIONAL** under (b) and (b′) |
| **R37-C1-U2** (U2b half) | identical decodes | 1.00 (64/64) | 1.00 | 0.00 | **holds** under (a) and (b); conditional under (b′) |
| **R37-C1-U3** | 928 rho3 re-decoded, best 4.35 < bars | 1.00 (48/48; legacy 0.94) | 1.00 | 0.00 | **holds** under (a) and (b); conditional under (b′) |
| **R38-C1-SEMANTIC-WORDNET** | identical decodes (rho1) | not measured (shares decoder/judge with U3 rho1, 16/16; lexicon glue not planted) | not measured | 0.00 | holds under (a) and (b) **by inheritance** (not separately planted); conditional under (b′) |
| **R38-C1-SEMANTIC-FREQRANK** | identical decodes (rho1) | not measured | not measured | 0.00 | same as WORDNET |
| **R39-C1-SENSE-SIMILARITY** | identical decodes (rho1) | not measured | not measured | 0.00 | same as WORDNET |
| **R38-C2-G3-LAGGED-POINTERS** | pages 0 and 3 unchanged; pages 1, 2, 4, 5 open mid-word, so word 1's cw/dw pointer depends on the fragment convention. **Not re-run** | U3-form plants 1.00 (page 0); pages opening mid-word unmeasured | as (a) | 0.00 | **CONDITIONAL** (fragment convention, plus b′) |
| **R41-C1-R14-WORDSUM-SELFKEY** | **re-run, negative** (p 0.25 / 0.86) | **1.00** (legacy 0.001 under exact∧score; 0.64 under R41's score-only criterion: the R41 negative was weakened, not uninformative) | 1.00 | 0.00 | now a negative that holds under (a) and (b); conditional under (b′) |
| **R44-W2A2-7GRAM-DIFFPLAIN** | site shapes unchanged | shape precision 1.000 | 1.000 | 0.033 | **holds** under (a) and (b); under (b′), coverage ≈ 3 % per site (I1: 1.2 % for page-scope permutation) |
| **R40-C1-INCONCLUSIVE-R31** | not word-indexed: `round10b/B3 t1_titlecrib.crib_positions` cribs at page starts and after `.` `&` `$`, and consumes no word segmentation | n/a | n/a | n/a | **unchanged INCONCLUSIVE** (32-rune floor). The word-space conditional does not apply; it carries a sentence-mark conditional instead. X1's doubt about I1 including it is **upheld** |

What decides between (b) and (b′) is R45-W1's open question: are the spaces the plaintext's words reordered, or
lengths from somewhere else? This lane does not settle it.

## 6. Three conditionals

1. **Key space.** No sweep. Real re-runs used each row's frozen space: R41's 20 variants; 928 R37 U3 rho3 jobs; the
   resident SKELETON corpus.
2. **Transition model.** R41: exact inverses, per-page reset, word on the page it starts on. R37: beam_v3
   keyskip1/keyskip2 and direct A1/A2, key restarting per page, an opening fragment as word 0 with its full printed
   length as the rho3 value (convention C1). SKELETON: exact length match.
3. **Register.** Panel-R36, 12 registers. Plants are English only, so power under shuffled words is unmeasured for
   Latin, OE, DE, CY, GREEK, HEBREW and NORSE.

## 7. Not covered

- The R41 W-level and P-level scorer is panel-R36 `AD.adjudicate` with its own null. It is not R41's round40
  `lib`/`panel12` build, which is gitignored; the faithfulness check above ties the two together.
- These were not re-run:
  - R38-C2-G3 on pages opening mid-word.
  - Book-scope shuffles.
  - Whole-stream key schedules (no per-page reset).
  - Assigning a page-wrap word to the page it *ends* on.
  - SKELETON beyond the resident corpus.
- Of the 55 LP2 pages, **32 open mid-word** (1, 2, 4–7, 9, 10, 17, 19, 20, 22, 24–26, 28, 30, 32, 34, 36, 41–49, 51,
  52, 54). Any future per-page word schedule must state its fragment convention.

## 8. Deviations and process notes

- **Plant truncation bug.** The first R41 plant run hit an assertion: `l1lib.make_plant` overran 12,956 runes by a few
  runes. It was fixed before any R41 plant number was produced. R37 heads and 7-gram windows lie inside the stream, so
  they were unaffected.
- **Killed SKELETON launch.** The first SKELETON plant launch was killed by a 590 s shell timeout before it produced
  any output, and was relaunched unchanged.
- **One test-file fix.** One expectation in `test_parse_rules_small` was miscounted (7 words, not 8) and was corrected.
  No threshold was edited.
- **Wall-clock gap.** The machine was apparently suspended for about 4.5 h (16:20 → 20:50). Elapsed-time fields that
  span that gap (null block 100 at 18,133 s; SKELETON plants) are wall time, not compute.
- **Uncommitted binaries.** The `r41_null_b*.npz` arrays (gitignore-able; `arm_r41.py null` regenerates them) and the
  `heartbeat_*.txt` files are left in the folder. The coordinator should add a `.gitignore` block. Nothing outside
  this folder was written.

---
CLOSED 2026-11-24T21:25 R46-L1 word-loader | words.py 2,896 LP2 words (sha = PROBLEM.json), 10/10 tests | R41-R14 re-run negative, power a/b 1.00 (legacy 0.001 exact∧score; 0.64 score-only) | R37 U2b/U3 hold (928 rho3 re-decodes < bars) | SKELETON re-run chance, legacy power 0.25-0.50 -> 1.00, b = 0 | 5 ledger rows | no crosser, no flag, no LEDGER.json edit, no commit

## X1 corrections applied

_Applied by the Round 46 coordinator from `../X1-redteam/AUDIT.md` (2026-11-24); PREREG untouched._ §5.8 items 1–7: R41 legacy power restated as ≈ 0.64 by R41's own score-only rule (0.001 only under exact∧score), so the old R41 negative was weakened, not blind; pages are pseudo-replicates (32/32 streams, Wilson ≥ 0.89); R38-WORDNET/FREQRANK and R39-SENSE power is "not measured" (was "1.00 inherited"); under (b′) word-indexed rows fall to ≤ 0.033 (7-gram 0.033); SKELETON negative rests on distance from the planted-hit level, not on the weak shuffled null. Same edits in `ledger_rows.json`. Item 8 (.gitignore for `r41_null_b*.npz`) done in the root `.gitignore`. New row R46-X1-R41-LEGACY-SCORE-POWER.
