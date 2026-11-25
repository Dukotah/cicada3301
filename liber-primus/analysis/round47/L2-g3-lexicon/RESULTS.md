# Round 47 / L2 — R38-C2-G3 re-run through words.py, and measured power for the three lexicon rows: RESULTS

_2026-11-24. Pre-registered in `PREREG.md` (sha256 `a232cbdf…5b65`, stamped in `run.log` at 22:02:07 before the first
script ran). No addenda; no threshold edited. Merged numbers: `results.json`. Ledger rows: `ledger_rows.json`
(4 rows, `R47-L2-…`). No decode sweep beyond the rows' own frozen spaces. Nothing crossed a bar, so nothing is flagged
for the oracle._

## 0. Headline

- **R38-C2-G3: the R46 CONDITIONAL on the fragment convention is closed.**
  - The real re-run covers pages 1, 2, 4 and 5 under CS and CE (768 decodes).
  - Best scores against the bars at the combined family N:
    - ks1 5.440 vs 6.048
    - ks2 4.737 vs 5.967
    - direct 4.111 vs 6.574
  - All three also sit below the original-N bars (5.727 / 5.658 / 6.252).
  - 0 gate runs.
  - Power on LP2's real layout is **1.00** under (a) and (b) for every convention: 80/80 on page 0, and 320/320 per
    convention on the mid-word pages.
  - Under (b′) power is **0.00** for the row's own decoder fed the
   printed lengths. No segmentation search was run, and for the U2b class one recovers 0.96 (R47-X1), so this is a decoder
   conditional, not a blindness bound.
- **The three lexicon rows now have measured power, not inherited power.** The rows are R38-WORDNET, R38-FREQRANK and
  R39-SENSE.
  - Each was planted through its own `enciphers.enc` → `sweep.dec_shift` / `dec_a3` → `judge()` path.
  - Under (a) and (b), power is **1.00** on page 0 (18/18 per row) and on pages 1–2 under C0, CS and CE (36/36 each).
  - Under (b′), power is **0.00** for every row and every convention (own printed-length decoder; segmentation search not run).
- **Real decodes under CS/CE on pages 1–2 stay below the bars.** Bests against the combined-N bars:

  | row | shift best | A3 best | bars (shift / A3) |
  |---|---:|---:|---|
  | R38-WORDNET | 4.112 | 5.102 | 7.216 / 8.174 |
  | R38-FREQRANK | 3.324 | 5.896 | 7.216 / 8.174 |
  | R39-SENSE | 4.161 | 5.171 | 6.953 / 7.912 |

- **The faithfulness checks were exact.** A C0 re-run of every original job reproduces each recorded family best to 3
  decimals:
  - G3: 4.911 / 4.700 / 4.038 (576 decodes)
  - R38: 4.62 / 5.296 (28,224 decodes)
  - R39: 4.004 / 5.351 (14,112 decodes)

  In every case the C0 word lengths equal the lane's own `LENS` / `LENSP`.
- **The convention matters.** Plants enciphered under one convention and decoded under another are recognised only
  0.00–0.68 of the time (mismatch arm, §4). So a negative is a statement per convention, and this lane now covers all
  three.

## 1. Fragment convention (PREREG §1)

Pages 1, 2, 4 and 5 open mid-word, with fragments of 5/6, 2/5, 2/5 and 2/3 runes. Pages 0 and 3 open on a word
boundary. Every row restarts its key per page, so the decode depends on which word counts as word 0.

| id | page p's unit starts at | word 0 | real-data status |
|---|---|---|---|
| **C0** split (legacy mapcommon) | page start | the on-page fragment | identical to the recorded R38/R39 decodes (faithfulness re-run) |
| **CS** belongs to the page it starts on (L1/R41 carry-over) | first word starting on page p | that word | re-run here |
| **CE** belongs to the page it ends on | the wrapped word's first rune (on p−1) | the whole wrapped word | re-run here |

Unit starts on real data:

| page | C0 | CS | CE |
|---:|---:|---:|---:|
| 1 | 262 | 267 | 261 |
| 2 | 528 | 530 | 525 |
| 4 | 946 | 948 | 943 |
| 5 | 1207 | 1209 | 1206 |

R46's convention "C1" adds a rho3 length value. None of these four rows uses length values, so here C1 ≡ C0. Nothing
on the held artifact picks one convention over another, so all three stand.

## 2. Measured power (lane's own `judge()`: pmax120 ≥ bar_v3(1e6,120) ∧ pmax240 ≥ bar_v3(1e6,240) ∧ rec240 ≥ 0.90)

The plants are English (`l1lib.make_plant`) laid over LP2's real 12,956-rune layout and rendered in krisyotam format.
The decoder gets word lengths parsed back by `words.py`. The encipherer works on the TRUE words of the regime. Each
(regime × page × convention × rep) is a fresh plant stream, and each cell is planted once per stream.

**R38-C2-G3** (40 cells, k/n):

| regime | page 0 | mid-word, C0 | CS | CE | verdict |
|---|---|---|---|---|---|
| a | 80/80 | 320/320 | 320/320 | 320/320 | **holds** (Wilson ≥ 0.988 mid-word) |
| b | 80/80 | 320/320 | 320/320 | 320/320 | **holds** |
| b′ | 0/80 | 0/320 | 0/320 | 0/320 | **conditional** |

**Lexicon rows** (9 cells each, k/n):

| row | regime | page 0 | pp 1–2 C0 | CS | CE | verdict |
|---|---|---|---|---|---|---|
| R38-C1-SEMANTIC-WORDNET | a / b | 18/18 / 18/18 | 36/36 / 36/36 | 36/36 / 36/36 | 36/36 / 36/36 | **holds** (Wilson ≥ 0.904) |
| | b′ | 0/18 | 0/36 | 0/36 | 0/36 | **conditional** |
| R38-C1-SEMANTIC-FREQRANK | a / b | 18/18 / 18/18 | 36/36 / 36/36 | 36/36 / 36/36 | 36/36 / 36/36 | **holds** |
| | b′ | 0/18 | 0/36 | 0/36 | 0/36 | **conditional** |
| R39-C1-SENSE-SIMILARITY | a / b | 18/18 / 18/18 | 36/36 / 36/36 | 36/36 / 36/36 | 36/36 / 36/36 | **holds** |
| | b′ | 0/18 | 0/36 | 0/36 | 0/36 | **conditional** |

**Pseudo-replication.** In each regime, the cells of a row share the plant streams:
- G3: 18 streams per regime (page 0 × 2, plus 4 mid-word pages × 3 conventions × 2).
- Lexicon: 14 streams per regime.

Per-convention cells rest on 8 streams (G3) or 4 streams (lexicon). Read the Wilson bounds as optimistic. At the stream
level, every stream under (a) and (b) had every cell recognised, and no stream under (b′) had any cell recognised.

## 3. Real re-runs (`*_real.json`; SWEEPROW stores validated: `validate_store` ok, `check_r3_store` [])

| row | decodes (CS+CE) | best CS | best CE | bar_v3 combined N (orig N) | gate runs | flagged |
|---|---:|---|---|---|---:|---:|
| G3 ks1 | 256 | 4.761 | 5.440 (cw index M29 self A3, p4, GREEK) | 6.048 (5.727) | 0 | 0 |
| G3 ks2 | 256 | 4.737 | 4.157 | 5.967 (5.658) | 0 | 0 |
| G3 direct | 256 | 4.111 | 3.560 | 6.574 (6.252) | 0 | 0 |
| R38-WORDNET shift / A3 | 18,816 (A + B) per conv | 4.112 / 5.010 | 4.075 / 5.102 | 7.216 / 8.174 (6.895 / 7.853) | 0 | 0 |
| R38-FREQRANK shift / A3 | (same family) | 3.247 / 5.247 | 3.324 / 5.896 | same | 0 | 0 |
| R39-SENSE shift / A3 | 9,408 per conv | 4.161 / 5.007 | 4.124 / 5.171 | 6.953 / 7.912 (6.632 / 7.590) | 0 | 0 |

The combined N counts the original family plus this lane's new decodes, per relation or group, as PREREG §4 sets out:
- G3: 224 / 224 / 896.
- R38: 4,872 / 60,984.
- R39: 2,436 / 30,492.

All bests are below even the more lenient original-N bars. The smallest margin is G3 ks1 CE: 5.440 vs 5.727 (0.29),
and vs 6.048 at the combined N (0.61). Pages 0 and 3 were not re-run, because their L=120
screen windows are identical under all three conventions. They differ only past the page end, in the L=240 gate span on
page 3, which never fired.

## 4. Mismatch arm (regime a, encipher under X, decode under Y ≠ X; reported only)

| row | power range over the 6 (X, Y) pairs |
|---|---|
| G3 | 0.43–0.68 (cw/A1-type cells self-synchronise after one word) |
| R38-WORDNET | 0.00–0.56 |
| R38-FREQRANK | 0.00–0.50 |
| R39-SENSE | 0.00–0.50 |

**Approximation.** When the decoder's unit starts before the encipherer's, the leading runes (which belong to page p−1's
schedule) are filled in as plaintext. The arm shows only that the convention is load-bearing. It is not a power figure
for any row.

## 5. Corrected verdicts

| row | (a) | (b) | (b′) | change from R46 |
|---|---|---|---|---|
| **R38-C2-G3-LAGGED-POINTERS** | holds, C0/CS/CE (power 1.00; real CS/CE re-run below bars) | holds | conditional (0.00) | R46 "CONDITIONAL (fragment convention, not re-run)" → negative holds under (a)/(b) for all three conventions |
| **R38-C1-SEMANTIC-WORDNET** | holds (measured 1.00, C0/CS/CE) | holds | conditional (0.00) | "not measured / by inheritance" → measured. Real result now covers CS/CE on pages 1–2 too |
| **R38-C1-SEMANTIC-FREQRANK** | holds | holds | conditional | same |
| **R39-C1-SENSE-SIMILARITY** | holds | holds | conditional | same |

What decides between (b) and (b′) is still R45-W1's open question: are the printed spaces the plaintext's words reordered,
or lengths from somewhere else? This lane does not settle it. C10 (H1)
does not settle it either: C10 asks for a decoder that works under (b′), and R47-X1 showed one for the U2b class. A
b′-robust re-run of these four rows is unmeasured.

## 6. Three conditionals

1. **Key space.** Each row's frozen space, unextended:
   - G3: 40 cells, pages 0–5, σ ±, ks1/ks2 for A3, s = 0, lag 1.
   - Lexicon rows: their variants × A1/A2 (s 0..28) and A3 (s 0..725 step 1), σ ±, pages 0–2, rho 1.

   Each space is covered under C0 (recorded), CS and CE.
2. **Transition model.** A1/A2 are beam-free direct decodes, judged against the keyskip1 bar.
   - G3 A3 uses beam_v3 ks1/ks2, with the lane's **skip-free** A3/cw planted encipherer. The cw pointer is circular under
     skips; this is R38-X1's conditional, carried forward.
   - Lexicon A3 uses beam_v3 ks1 only.
   - All rows restart the key per page.
3. **Register.** Panel-R36, 12 registers (sha a0682f0c…). Plants are English only. Non-English power on the real
   layout is not measured here; R40-I1 replanted the page-0 controls in LATIN/GREEK/EN_NOVOWEL/HEBREW.

## 7. Not covered

- Lag > 1.
- dw inside the beam.
- A skip-circular A3/cw plant.
- A "carry" variant, where page p's first lag-1 pointer is the wrapped word's value.
- Lexicon rows on pages > 2.
- rho 2/3.
- keyskip2/free for the lexicon rows.
- Non-English plants on the real layout.
- (b′) alternatives other than a within-sentence permutation (book-scope, borrowed lengths).

The rows' own `not_covered` lists still apply.

## 8. Process notes and files

- **No deviations.** No threshold was edited. The kill checks of Q5 both passed: exact faithfulness, and page-0 (a)
  power of 1.00 for every row.
- **Run time.** The whole lane took about 10 minutes, so heartbeat files were written but none was needed.
- **Background exit code.** The background wrapper of the lexicon arms exited 1 only because of a trailing multi-file
  `tail` in the shell command. Every arm wrote its outputs and logs completely.
- **Large gitignore-type outputs** (regenerated by `arm_g3.py real`, `arm_lex.py r38|r39 real`):
  - `r38_sweep_rows.jsonl` (6.7 MB)
  - `r39_sweep_rows.jsonl` (3.4 MB)
  - `g3_sweep_rows.jsonl` (0.15 MB)

  `g3_plants.json` (1.6 MB) is also large. The coordinator should add a `.gitignore` block for `round47/L2-g3-lexicon/*_sweep_rows.jsonl`.
- **Files.**
  - Pre-registration and log: `PREREG.md`, `run.log`.
  - Code: `l2lib.py`, `arm_g3.py`, `arm_lex.py`, `finalize.py`.
  - Arm outputs: `g3_{faith,real,plants}.json`, `r38_{faith,real,plants}.json`, `r39_{faith,real,plants}.json`.
  - Logs: `*_real.log`, `*_plants.log`.
  - Heartbeats: `heartbeat_*.txt`.
  - Merged outputs: `results.json`, `ledger_rows.json`.
- **Writes and commits.** Nothing was written outside this folder. LEDGER.json was not edited. Nothing was committed.

---
CLOSED 2026-11-24T22:20 R47-L2 g3-lexicon | fragment conventions C0/CS/CE stated + all run | G3 re-run 768 decodes, best 5.440 < 6.048 (ks1), power a/b 1.00 all conventions, b' 0.00 | WORDNET/FREQRANK/SENSE power measured: a/b 1.00 (C0/CS/CE), b' 0.00; real CS/CE re-runs 56,448 decodes all below bars | faithfulness exact (G3, R38, R39) | 4 ledger rows | no crosser, no flag, no LEDGER.json edit, no commit

## X1 corrections applied

_Applied by the Round 47 coordinator from `../X1-redteam/AUDIT.md` §2.6 (2026-11-25); PREREG untouched._ Items 1–3: every (b′) 0.00 is now qualified as "own printed-length decoder; segmentation search not run" (§0 and the four `ledger_rows.json` rows); the C10 misattribution in §5 is replaced. With the key in hand the (b′) loss is the decoder's, not the information's (R47-X1: a segmentation beam recovers 0.962 / 0.976 of U2b plants); with an unknown key from a 65,536-key family, printed-start ranking plus that arrangement beam recovers 78–88/100 (R47-H2). Whether the same holds for G3 lagged pointers and the lexicon rows (key depends on the previous word's value or identity) is unmeasured; it is a Round 48 item (arrangement-aware decoder for word-indexed rows where the key family is bounded).
