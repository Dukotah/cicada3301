# Round 45 / I1 — Decoy-space instrument audit: PRE-REGISTRATION

_Written 2026-11-23, before any output file in this directory existed. Doctrine: `ARMADA-DOCTRINE.md` (R1 instrument
audit). Plan of record: `analysis/round45/CAMPAIGN-PLAN.md` lane I1. Writes only inside this directory; no commit; no
edit to `LEDGER.json` or any existing file._

## 0. Premise and question

Fable52 (`analysis/fable52/OUTPUTS.txt`, t4/t4b) and FlareZ123 measured that LP2's printed word-length sequence has
shuffle-level adjacent-length MI (z = +0.5; solved LP z = +7.4). So the printed spaces may not be the plaintext's words
in order. Two distinct alternatives are measured, because they hit different instruments:

* **H-decoy** — the rune stream is the in-order plaintext's encipherment, but the printed separators are not its word
  boundaries (permuted lengths, a decoy length sequence, or no information at all).
* **H-shuffle** — the separators ARE word boundaries, but the plaintext words were reordered before encipherment, so the
  *rune stream itself* is word-permuted prose.

Question: which standing instruments and closed ledger rows silently assume "printed spaces = plaintext word
boundaries, in order", and how much detection power do they lose when that is false?

## 1. Conditions (frozen)

For a plant built from held-out English prose with true word boundaries (`data/pride.txt`, `data/moby.txt`; neither
is a panel-R36 training corpus — EN_MODERN trains on self_reliance+mabinogion, EN_KJV on kjv), the "printed spaces"
handed to the instrument are:

| cond | printed spaces given to the instrument | rune stream |
|---|---|---|
| a | the plaintext's true word lengths (baseline) | in-order plaintext |
| b | the true word lengths permuted within the page | in-order plaintext |
| c | LP2's actual printed length sequence (decoy), from the canon page | in-order plaintext |
| d | no spaces (page = one word / no length sequence) | in-order plaintext |
| e (H-shuffle) | true boundaries of the reordered words | words permuted within page, then enciphered |

A "page" is the plant window (L = 120 or 240 runes; LP2 mean page = 235.6 runes, ~53 words).

## 2. Instruments and arms

1. **Inventory** (`inventory.py`): grep the standing instruments (beam_v3, pf_v4/pf_v4_12, panel-R36 adjudicate,
   bars_v3, verify_solution.py, HUMAN-ORACLE.md, tests/validate.py) and every `LEDGER.json` row (io.open utf-8) for
   consumption of word boundaries / lengths / initials / word sums / word-positioned cribs / plants that keep spaces.
   Each hit is hand-classified: **A** = negative conditional on spaces = plaintext words in order; **B** = reads the
   printed structure itself as the channel (not conditional; becomes *more* relevant under H-decoy); **C** = uses true
   spaces of SOLVED pages only (not conditional); **D** = space-blind but plants are in-order prose (H-shuffle only).
2. **arm_beam.py** — beam_v3 panel_max + panel-R36 adjudicate + bars_v3 (= the oracle pipeline) and pf_v4_12 head
   screen. Correct key handed over (SHA-256-CTR), enciphers keyskip1 (advance 1) and skip_by_two (advance 2), supp 0.83;
   registers EN (pride) and EN_NOVOWEL (pride, vowels dropped — the L7-A hard case); L = 120 and 240; N = 20 plants per
   cell. Conditions a–d run through the full pipeline literally; e is the word-shuffled stream.
3. **arm_wordsched.py** — word-boundary key schedules through their lanes' own encipherers/decoders:
   R37-C1 U2b and U3 (A1/A2/A3) via `round37/C1-composed-clue-readings` (enciphers_u2_u3.py + sweep.py decoders,
   `judge()` rule), and R41-C1 R14 wordsum_selfkey W1–W5 via `round41/C1-r14-r15/camp7.py` + `run_c1.enc_words`.
   Encipher with the TRUE segmentation; decode with the condition's segmentation.
4. **arm_skeleton.py** — Round 8 SKELETON `analysis/skeleton/wordlen_search.py::scan` (C-01): plant = a pride
   passage of W words (W = 120, 400); corpus = pride + moby; conditions a/b/c (d has no pattern: power 0 by definition).
5. **arm_7gram.py** — R44-W2A2-7GRAM-DIFFPLAIN assumes the 7-gram's plaintext shape is (3-rune word, 3-rune word,
   word head) from the printed gaps. Under H-decoy the shape is random: measure P(shape = 3|3|head) for a random
   7-rune window of held-out English (pride runes).

## 3. Metrics and frozen thresholds

* Beam/panel power (per cell): fraction of plants with rune recovery ≥ 0.90 AND panel pmax ≥ `bar_v3(N, L, rel,
  family="lp2")`, at **N = 1e6** (sweep scale) and **N = 1** (oracle single-key scale). Oracle PASS = both pages of a
  plant pair clear the N = 1 bar under the same relation (verify_solution `decide`, MIN_PAGES 2).
* Space-invariance claim: an instrument is declared **space-blind** iff conditions a–d give bit-identical decodes
  (sha256 of plain_idx) and identical pmax for 100 % of plants. Anything less is reported as space-dependent.
* pf_v4_12 power: fraction of correct-key plant heads (m = 24) with lse > frozen thr (frozen_op12.json) for the
  plant's relation.
* Word-schedule lanes: R37 rule `judge()` (pmax120 ≥ bar_v3(1e6,120) AND pmax240 ≥ bar_v3(1e6,240) AND recovery ≥
  0.90); R41 rule: rune recovery = 1.0 (exact) and, separately, pmax > the lane's own P-level null max 5.50
  (`round41/C1-r14-r15/RESULTS.md`).
* SKELETON detection: argmax over all corpus offsets is the planted offset AND its match count exceeds the max over 5
  shuffled-pattern scans of the same corpus.
* **Material loss / reopen rule (frozen):** a ledger row goes on the reopen list if its instrument's measured power
  under condition b or c (H-decoy) or e (H-shuffle, for class-D rows) is < 0.80 absolute, or < 0.5 × its power under a.
* Baseline gate (Q5 kill): condition (a) must reproduce documented power — beam EN keyskip1 L=120 power@1e6 ≥ 0.90
  (R33-I1: 20/20 over null); R37 U3/U2b ≥ 80 % recover; R41 W1–W4 exact recovery 100 %; SKELETON (a) detection ≥ 0.90
  at W = 400. A failed baseline marks that arm UNINFORMATIVE, not negative.

## 4. Aiming Test

**Q1 — What would a hit look like, and would this instrument recognise it?** A "hit" here is a measured power delta:
the same correct-key plant recognised under (a) and missed under (b/c/d/e). Recognition is through each lane's own glue
(own encipherer, decoder, bar and rule), with condition (a) reproducing the documented control first.

**Q2 — What measured fact raises the prior?** `analysis/fable52/OUTPUTS.txt` t4/t4b: adjacent word-length MI on the
2,896 printed LP2 words z = +0.51 (shuffle level) vs solved LP z = +7.43 on 875 words; nine 875-word LP2 windows span
−1.5…+2.3 while English 875-word windows have medians +2.8…+7.8. Independently found by FlareZ123.

**Q3 — Is the space bounded?** Yes, enumerable and small: 7 standing instruments + 351 ledger rows grepped; 5 conditions;
the measurement grid is fixed in §2 (≈ 2,000 decodes total). No key space is swept.

**Q4 — Three conditionals.** Key space: correct key handed over (power test, no sweep). Transition model: keyskip1 and
skip_by_two (beam), the lanes' own schedules (U2b/U3/W1–W5). Register: panel-R36 12 registers; plants EN and
EN_NOVOWEL (English prose from pride/moby) only — H-shuffle results for other registers are not measured.

**Q5 — Kill condition at 10 %.** If condition (a) fails the baseline gate in §3 for the beam arm (the first arm run),
stop the arm and report the rig unhealthy. If a–d are not bit-identical for the beam on the first 10 plants, stop and
investigate a hidden space dependency before continuing.

## 5. Deliverables

PREREG.md (this), scripts, `results.json`, `RESULTS.md`, `ledger_rows.json` (LEDGER.json entry schema, ids
`R45-I1-…`), closing stamp line at the end of RESULTS.md. Runs are single-process, each < 10 min; any longer arm writes
`heartbeat.txt` every few minutes.
