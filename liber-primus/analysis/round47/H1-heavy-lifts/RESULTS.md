# Round 47 / H1 — heavy-lift challenges C7–C10: RESULTS

_2026-11-24. PREREG: `PREREG.md` (sha256 `7d769769…` stamped in `run.log` before the first checker number; Addendum 1
`2489c7b4…`, Addendum 2 `21a32c12…`, each stamped before the numbers they govern). Ledger rows: `ledger_rows.json`
(4 rows, `R47-H1-…`). Every number below is reproduced by `run_baselines.sh` (~8 min). The `out_*.txt` files are the
checkers' own output. No key space was swept, and nothing is claimed about LP2's plaintext. No crosser, no flag._

## 0. Headline

- **Four checkers shipped** under `challenges/`: `c7_corpus_forge.py`, `c8_register_scorer.py`, `c9_rejection_loops.py`,
  `c10_shuffled_lengths.py`, plus `_heavy.py` (shared), three example submissions, the C7 worked example, and
  `test_heavy_checkers.py` (5/5 pass). `CHALLENGES.md` has a new "Heavy lifts" section, table rows C7–C10, and
  copy-paste agent prompts.
- **C9 found a new beam blind spot.** Under **V-BACK** (on a rejected doublet the key pointer steps *back* one
  place, a one-character change from keyskip), both the C3 reference beam and beam_v3 (all three relations) score the
  **correct key as noise**: 0/40 recovered, median −7.01 / −6.79. No beam-based negative in the ledger covers V-BACK. It is a representational gap, not a hard one: a beam with one added backstep relation recovers 32/40 V-BACK plants through this checker (R47-X1, dev seed). V-BACK is consistent with LP2's surface statistics, but no measured fact raises its prior.
  **V-NULL** (doublet-triggered null + discard) is only a *recovery* gap: the beams stay in sync and score English
  (−4.54), but every null leaves a junk rune, so positional recovery is 0.17.
- **C10 qualifies R46-L1.** Under b′ the L1 battery's U2b rule recovers **0/500** plants (mean rune recovery 0.33).
  But with the key in hand it still **detects** at FPR 0.01 with power **0.83 / 0.81** (two seeds). "b′ power ≤ 0.033"
  is a statement about recovery at sweep-scale bars, not about blindness. The registered detection finish line was
  unreachable because of this, so C10 was re-aimed to recovery (Addendum 2). R47-X1 then crossed the re-aimed C10 finish line with a 58-line within-sentence segmentation beam (481/500 and 488/500, null FP 0), so for the U2b class at known key the (b′) recovery loss belongs to the printed-start rule, not to the information in the print.
- **C8: at FPR 0.01 (not at sweep-scale bars, which were not measured) the register gap is narrower than L7-A's −5.5 rule suggests.** The English scorer detects Latin and German
  page-size windows at power 1.00 against all four nulls. The gap is in **sequence-unlike** registers, where the
  shuffled-text null defeats both instruments: vowel-dropped English (English 0.00, panel 0.33) and reversed English
  (English 0.87, panel 0.62).

## 1. Checker self-tests (controls)

| checker | control | result |
|---|---|---|
| C7 | Aeneid example validates, 500/500 re-derived; a copy with every 7th sentence altered FAILS | PASS (82/500 mismatches caught) |
| C8 | English scorer on English held-out ≥ 0.80 at L = 236 | PASS (1.000) |
| C9 | keyskip control recovered by both beams; C3 gates 7/7 on the example decoder | PASS (40/40, 40/40; 7/7) |
| C10 | true-start decode reproduces plaintext exactly; ceiling ≥ 0.95 | PASS (500/500; 1.000) at both seeds |

## 2. Baselines

### C7 (seed 4700): `out_c7_selftest.txt`
Latin (*Aeneid*, R-A table): 63,788 words, 3,279 sentences, 0 % unmapped. 2-rune share **8.36 %** (window p01–p99
6.87–9.70 %). LP2's 15.47 % is above all 1,000 windows. T3 G = 1,348 vs within-text bar 25.2, so **rejected**,
consistent with R46-P1. This is a covered register, so it is not a crossing. Caveat: the checker's bar is within-text,
which makes a single-corpus rejection weak (R46-P1 X1).

### C8 (seed 4703 self-test; seed 4705 extra): `out_c8_selftest.txt`, `out_c8_extra.txt`, `baseline_extra.json`
Power at FPR 0.01 against every one of uniform / real-LP2 / shuffled-positive / beam-wrong-key nulls. Positives are
planted via keyskip and decoded by the reference beam with the correct key. 200 positives per length.

| held-out | L | English reference | panel-R36 pmax |
|---|---|---|---|
| English (*Dracula*) | 236 / 120 / 60 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 |
| Latin (latin_218) | 236 / 120 / 60 | 1.00 / 0.995 / 0.955 | 1.00 / 1.00 / 1.00 |
| German (de_2) | 236 / 120 / 60 | 1.00 / 1.00 / 0.98 | 1.00 / 1.00 / 1.00 |
| vowel-dropped English | 236 / 120 / 60 | **0.00** / 0.005 / 0.00 | **0.33** / 0.32 / 0.37 |
| reversed English (off-panel) | 236 / 120 / 60 | 0.87 / 0.46 / 0.24 | **0.62** / 0.32 / 0.15 |

For vowel-dropped English the panel is ≥ 0.90 against the three wrong-key nulls. The shuffled null is the one that
binds, and it is stricter than the R36 gate, which used wrong-key nulls only. A quick `--direct` probe (no plant/beam)
had given the panel 1.00 on vowel-dropped English. The full protocol gives 0.33, so plant+beam and the shuffled class
matter and `--direct` is rightly labelled "not a claim".

### C9 (seed 4701, 40 plants per variant, L = 240): `out_c9_selftest_40.txt`

| variant | reference beam: ok · mean rec · median score | beam_v3 best of 1/2/free |
|---|---|---|
| keyskip (control) | 40/40 · 0.998 · −4.29 | 40/40 · 0.997 · −4.29 |
| **V-BACK** | **0/40 · 0.188 · −7.01** | **0/40 · 0.194 · −6.79** |
| **V-NULL** | **0/40** · 0.171 · −4.54 | **0/40** · 0.171 · −4.54 |
| V-DEFER (diagnostic) | 39/40 · 0.941 · −4.60 | 39/40 · 0.950 · −4.59 |

Wrong-key false positives are 0.00 in every cell. Surface check at supp = EXACT_SUPP on English plants (lag-1 / lag-2
repeat rate; LP2 0.66 % / 3.40 %): V-BACK 0.69 / 3.60, V-NULL 0.67 / 3.51, V-DEFER 0.70 / 3.56. The registered V-NULL
(null, then re-emit the rejected value) gives 0.66 / **6.03**, so LP2 excludes it (Addendum 1). Example decoder at seed
4706 (`out_c9_example.txt`): C3 7/7, V-BACK 0/12, V-NULL 0/12, which is not a crossing.

### C10 (500 plants + 500 nulls): `out_c10_selftest_4702.txt`, `out_c10_selftest_4704.txt`

| seed | baseline plants recovered | mean recovery | baseline detection @1 % FPR | ceiling |
|---|---|---|---|---|
| 4702 | 0/500 (Wilson ≤ 0.008) | 0.331 | 0.830 (0.795–0.860) | 500/500 |
| 4704 | 0/500 | 0.319 | 0.812 | 500/500 |

Why recovery is about 1/3: J_k depends only on the word index k, so a rune decodes correctly exactly where the printed
word index equals the true one. The within-sentence shuffle preserves that at about a third of positions, which is
enough English to clear a wrong-key floor and far too little to read.

## 3. Deviations (all pre-registered as addenda)

1. **Addendum 1:** V-NULL redefined, because the registered form is excluded by LP2's lag-2 rate. The superseded
   12-plant V-NULL row is not reported.
2. **Addendum 2:** C10's registered detection finish line was unreachable (baseline 0.83 ⇒ need 1.13). That result
   is kept as measured above, and the challenge was re-aimed to recovery (the quantity L1's own rules used).
3. The C8 example first carried a non-panel label and printed "FINISH LINE MET" on English text. It now uses
   `REGISTER = "EN_MODERN"`, and the checker's crossing message says the register is a label pending human check.
   This changes no threshold.
4. The first beam_v3 timing probe hung for about 15 min with no output and was killed. Re-run probes took 0.02–0.4 s
   per decode. The cause was not diagnosed, and it had no effect on any number.

## 4. Gameability notes (for X1)

- **C7:** the register is judged by humans. The ISO code in the manifest drives the "covered" flag, so it can lie.
  The sampled re-derivation only proves the corpus follows the table. It doesn't prove the table is faithful.
- **C8:** `REGISTER` is a label. A submitter could submit English under a new name. The checker flags panel names
  only, and the maintainers' held-out re-run is the real guard. The shuffled-positive null blocks unigram scorers.
- **C9/C10:** the checker recomputes scores from `plain_idx`, so a returned score can't be faked. Wrong-key and
  null arms block "always English" outputs. A decoder could special-case the variant enciphers (they are public).
  That is allowed by design, because modelling the loop *is* the task. What has to be checked is that it still
  passes C3.

## 5. Conditionals (doctrine Q4)

1. **Key space:** none swept. Every power is at the correct key against fresh wrong-key nulls.
2. **Transition model:** C8 is keyskip1. C9 is V-BACK / V-NULL / V-DEFER plus the keyskip control. C10 is the U2b word
   jump without a doublet filter.
3. **Register:** C9 and C10 are English plaintext with English adjudication, so they are English-only negatives
   (L7-A). C8 is per held-out text, as tabled.

## 6. For the coordinator (outside this lane's write scope)

`AGENTS.md` §2 and `.github/ISSUE_TEMPLATE/challenge.yml` still say "C0-C6". The nav docs (`README.md`,
`ELIMINATION-LEDGER.md`, `analysis/README.md`, `PICKUP-HERE.md`) need the V-BACK finding and the R46-L1 qualification.
`challenges/examples/c7_latin_aeneid/.gitignore` ignores the built `corpus.txt`. `python -m pytest -q -m "not network"`
from `liber-primus/`: **120 passed, 5 skipped, 3 deselected** (`out_pytest.txt`).

---
CLOSED 2026-11-24T22:40 R47-H1 heavy-lifts | C7–C10 checkers + CHALLENGES.md section, self-tests 4/4 PASS, tests 5/5 | C7 Latin example rejected (covered) | C8 English 1.00 on LA/DE, vowel-dropped 0.00/panel 0.33, reversed 0.87/0.62 | C9 V-BACK 0/40 both beams (correct key = noise), V-NULL 0/40 recovery-only gap | C10 b′ baseline 0/500 recovered, detection 0.83 | 2 addenda, no threshold edited | 4 ledger rows | no crosser, no LEDGER.json edit, no commit

X1 corrections applied (R47-H2, 2026-11-24): AUDIT.md §3.6 #1, #2 and #3 inserted verbatim in §0 above; #7 and #9 in
`ledger_rows.json`. C9 and C10 were then re-scoped / redesigned by R47-H2 (PREREG Addendum 3,
`../H2-harden/RESULTS.md`): the C10 described in this file is retired (preserved as `../H2-harden/c10_v1_keyed.py`),
and C9 scores V-NULL only.
