# R47-X1 — Red-team audit of Round 47 (T2, L2, H1)

_2026-11-24. Doctrine R6: verdicts are FOUND-ERROR / NO-ERROR-FOUND, never "confirmed". Rulings per lane:
UPHELD / UPHELD-WITH-CORRECTIONS / REJECTED. All three lanes were audited after their closing stamps._

**Process note.** X1 wrote no PREREG. Two of its new measurements use a threshold fixed in advance by someone else:
the C10 checker's own finish line (§3.3) and a factual check (§1.3). The others are descriptive, and their ledger rows
say `threshold_fixed_in_advance: false`. The C9 extended beam's penalties were tuned on 8–12 plants at seed 4701 before
the 40-plant run at the **same** seed. It is a dev-seed result, not a sealed one. Every other number below is a
recomputation of a lane's own claim. X1 wrote only in this folder. The probe manifest for the C7 cheat was built in the
session scratchpad; a copy is kept here.

| lane | ruling | headline issue | severity |
|---|---|---|---|
| T2-transcription-closeout | **UPHELD-WITH-CORRECTIONS** | Stamps, freeze, gates and bounds all recompute. One factual error: reading M at 9877 **would** create a doublet (9876 is M). That adds a reader-independent 5.3 : 1 prior for canon D | low (verdict unchanged) |
| L2-g3-lexicon | **UPHELD-WITH-CORRECTIONS** | C0 faithfulness, CS/CE unit starts, real bests and all 8 bars recompute exactly. The (b′) "0.00" wording needs a decoder qualifier. "That is challenge C10" is a misattribution | low |
| H1-heavy-lifts | **UPHELD-WITH-CORRECTIONS** | V-BACK is a real representational gap (not a bug), but a 20-line relation closes it (32/40). **C10 is crossed** by a 58-line beam (0.962 / 0.976), so it is not a heavy lift. All four checkers can be passed by a cheat. V-NULL's crossing would not change L7-B | **high** (C10, gameability), medium (C9 framing) |

---

## 1. T2 — transcription close-out

### 1.1 Pre-registration and blinding: clean
- **Base stamp verified.** sha256 of the PREREG prefix before `## Addendum T2-A`, with the trailing `---` and
  whitespace stripped and one `\n` added, is `d9c40eb4…`. That equals `build_log.txt` line 1, stamped at 22:02:17.
  The full-file stamp `e4b2e86f…` equals the current file.
- **Timeline.** `build.py` mtime is 22:02:15 and it logged the PREREG at 22:02:17. The ten batches are 22:03–22:08,
  `unseal.py` is 22:09:57, and `results.json` is 22:10:16. `probe.py` (21:59) predates the PREREG; this is disclosed.
- **Freeze verified.** sha256 of all ten `reads_batchNN.json` equals `reads_frozen.sha256`.
- **Addendum T2-A is disclosure only.** It covers a line-count typo (16 → 15), a stacked reference image, and the
  post-hoc template run. It changes no threshold and no verdict.

### 1.2 Bounds: recomputed, correct
- Recomputed from CP95 (two-sided) / (1 − 0.2646 × 0.1765):
  - O/A/AE 4.6 %
  - M/D 19.9 % (13.4 % if 9877 is upheld)
  - TH/W/R 8.1 %
  - N/I 14.95 % (printed as 15.0)
  - B/E 14.95 %
  - all five 2.8 % (1.9 % if 9877 is upheld)
  - census of 206 (second reader only) 3.2 %
- n per family (S2 + T2: 72+10, 24+3, 42+4, 22+2, 19+5) matches the targets table. 1590, 1591 and 1593 correctly
  drop out of the S1-blind population.
- m_T2 = CP95(0/19) = 0.1765. That figure rests on only 1 D-shown swap. RESULTS says so ("controls under-sample
  it"), which is adequate.

### 1.3 Ask 4: 9877 M vs D. "Shared reader bias" is supported, and more strongly than T2 says (FOUND-ERROR in one sentence)
- **The 280 evidence is real but indirect.** At gpos 280 T2 reads M, while canon is D and the template is D
  (0.949 / 0.674). That shows T2 makes D→M errors on these renders. It does not show that S1 shares the bias. The
  S1 side rests on S1's published aggregate (D→M ×2).
- **What T2 missed:** in the LP2 stream, gpos 9874–9879 = **S Y M D Y S**, and T2's own row gives 9876 = M (T2, S1 and
  template all agree). So:
  - **A reading of M at 9877 would create an MM doublet.** LP2 has 86 doublets in 12,955 adjacent pairs.
  - Under LP2's doublet suppression, P(next = previous) is 0.664 %, while P(next = any one other rune) is 3.55 %.
    That is a **5.3 : 1 prior for canon D**, independent of every reader and of the template.
  - Both blind M reads sit immediately after a true M, which also fits a perseveration error. (280 follows S, so
    that one is not perseveration.)
- **Verdict on the ask.** The "leans toward reader error" reading is supported: template D at 0.969, the doublet
  prior, plausible perseveration, and a demonstrated T2 D→M miss. The pre-registered verdict still stands as
  `canon-error-candidate → oracle`, as it should.
- **Row:** `R47-X1-T2-9877-DOUBLET-PRIOR`.

### 1.4 Required corrections (`T2-transcription-closeout/RESULTS.md`; coordinator applies)
1. Replace `  - If M: canon has a family error at 9877 (line 455), which touches no doublet site.` with
   `  - If M: canon has a family error at 9877 (line 455), and the stream gains an MM doublet at 9876–9877 (9876 is M).
   LP2's doublet suppression alone makes that 5.3 : 1 less likely than D (R47-X1).`
2. After `So both "M" reads look
  like the same reader bias on this glyph shape.`, insert ` Independently of any reader, M at 9877 would follow the M at
  9876 and create a ciphertext doublet, which LP2's doublet rate (0.66 % vs 3.55 % for any given other rune) disfavours
  5.3 : 1; both blind M reads directly follow a true M (R47-X1).`
3. In `ledger_rows.json` `reopens_if`, replace `M -> one canon family error on line 455, no doublet site touched` with
   `M -> one canon family error on line 455 that also creates an MM doublet at 9876-9877 (5.3:1 prior against, R47-X1)`.

---

## 2. L2 — R38-C2-G3 re-run and lexicon plants

### 2.1 Pre-registration: clean
- PREREG sha256 `a232cbdf…` matches the current file. It is stamped in `run.log` at 22:02:07. The PREREG mtime is
  22:02:05, and `l2lib.py` (22:02:35) and the arms (22:03, 22:04) come after it. There are no addenda.

### 2.2 Ask 5: C0 faithfulness: **NO-ERROR-FOUND**
- The `RECORDED` constants in `arm_g3.py` and `arm_lex.py` trace to the original results:
  - `round38/C2-never-cells/RESULTS.md:13`: ks1 4.911 / ks2 4.700 / direct 4.038
  - `round38/C1-semantic-road/RESULTS.md:16–17`: 4.62 / 5.296
  - `round39/C1-sense-similarity/RESULTS.md:14–15`: 4.004 / 5.351
- The `*_faith.json` files reproduce each to the stated tolerance (< 0.0015), with C0 lengths equal to the rows'
  LENS / LENSP on every page.
- The decode counts match the originals: 576, 28,224 and 14,112.

### 2.3 Ask 5: CS/CE conventions implemented as stated: **NO-ERROR-FOUND**
- I recomputed from `l2lib.unit()` on `words.py` real words.
- The wrapped words are (261, 6), (525, 5), (943, 5) and (1206, 3), against page starts 262, 528, 946 and 1207.
  That gives on-page fragments of 5/6, 2/5, 2/5 and 2/3, as stated.
- Unit starts are C0 / CS / CE = 262/267/261, 528/530/525, 946/948/943 and 1207/1209/1206. These equal the RESULTS
  §1 table.
- CS takes the first word that starts on the page. CE takes the first word that ends after the page start (the
  wrapped word). Unit ends follow the stated rule.
- Pages 0 and 3 have no wrapped word.

### 2.4 Real re-runs and bars: **NO-ERROR-FOUND**
- **Bests.** My grouping of `g3/r38/r39_sweep_rows.jsonl` gives:
  - G3: ks1 CS 4.761 / CE 5.440; ks2 4.737 / 4.157; direct 4.111 / 3.560
  - R38: shift 4.112 / 4.075; A3 5.247 / 5.896
  - R39: shift 4.161 / 4.124; A3 5.007 / 5.171

  Row counts are 768, 37,632 and 18,816. These match RESULTS §3. The R38 per-row split agrees with the pooled
  maxima.
- **Bars.** `bars_v3.bar_v3(N, 120, rel)` recomputed: 224 ks1 6.048, 224 ks2 5.967, 896 ks1 6.574, 96 ks1 5.727,
  4,872 → 7.216, 60,984 → 8.174, 2,436 → 6.953 and 30,492 → 7.912. All eight are exact.
- **Pseudo-replication** is disclosed (streams per cell), and the Wilson bounds are labelled optimistic.

### 2.5 (b′) wording, after ask 2
- L2's 0/80, 0/320 and 0/36 under (b′) are correct **for each row's own decoder fed the printed lengths**, judged by
  `judge()` (recovery ≥ 0.90 plus sweep-scale bars).
- §3.3 shows that for the U2b word-jump class this is a decoder property. A segmentation beam recovers 0.96 at known
  key.
- Whether the same is true for G3 lagged pointers or the lexicon rows is **unmeasured**. Their constructions differ:
  the key depends on the previous word's value or identity, which a segmentation beam might also resolve.
- So "conditional (b′)" should be read as "not re-run with a b′-robust decoder", not as "blind".

### 2.6 Required corrections (`L2-g3-lexicon/RESULTS.md`)
1. In §0, replace `  - Under (b′) power is **0.00**.` with `  - Under (b′) power is **0.00** for the row's own decoder fed the
   printed lengths. No segmentation search was run, and for the U2b class one recovers 0.96 (R47-X1), so this is a decoder
   conditional, not a blindness bound.`
2. In §5, replace `This lane does not settle it. That is challenge C10 (H1).` with `This lane does not settle it. C10 (H1)
   does not settle it either: C10 asks for a decoder that works under (b′), and R47-X1 showed one for the U2b class. A
   b′-robust re-run of these four rows is unmeasured.`
3. Apply the same qualifier ("own printed-length decoder; segmentation search not run") to the (b′) cells of the four
   `ledger_rows.json` rows.

---

## 3. H1 — heavy-lift challenges C7–C10

### 3.1 Pre-registration and the two addenda
- **Stamps verified.** The base `7d769769…` is the prefix before `## Addendum 1` (rstrip + `\n`). Addendum 1
  `2489c7b4…` is the prefix before `## Addendum 2`. Addendum 2 `21a32c12…` is the full file. The `run.log` stamps
  are 22:08:28, 22:14:04 and 22:15:10, and baselines start at 22:19:18.
- `c7_corpus_forge.py` (22:11), `c9_*` (22:14:12) and `c10_*` (22:15:45) were all written after the base stamp.
- **Addendum 1 (V-NULL redefined): a legitimate correction.**
  - The trigger is the variant's own consistency check, not a beam result. I reproduce it independently: the
    registered null-then-re-emit form gives lag-2 5.66–6.61 % over 5 replicates, against LP2's 3.40 %.
  - It is stamped before any C8 or C10 number, and the superseded 0/12 row is disclosed.
  - **But the redefinition changed V-NULL's kind.** The null consumes no key, but the rejected key symbol is
    discarded. So the decoder sees a monotone, one-key-per-cipher-rune stream with junk runes inserted. That is
    why both beams score it as English (−4.54).
  - So the new V-NULL is not a transition-model gap for any score-based negative. Every beam negative **does**
    cover it at the detection level.
  - CHALLENGES.md's C9 text contradicts that twice: crossing V-NULL "changes L7-B-BEAM-ENVELOPE", and "no beam
    negative covers these two loops". Corrections 3.6 #4–5.
- **Addendum 2 (C10 finish line): a disclosed correction, not a self-serving goalpost move, but mis-sized.**
  - The registered line (≥ max(0.80, baseline + 0.30)) became 1.13, which no attack can reach. §3 of the PREREG
    only covered the case "baseline already crosses". The lane kept the registered number as measured (I reproduce
    0.830 at seed 4702 exactly), retired the metric rather than editing it, and stamped the change before the
    reported runs.
  - The new metric (recovery ≥ 0.90) is the one L1's `judge()` actually used, so the re-aim is substantively right.
  - What went wrong is the **size**. The new bar was set after seeing the printed-start rule fail (0/500), and was
    then assumed hard ("weeks", 2–10 M tokens). It is not (§3.3).
  - The goalpost moved in the direction that made the challenge **easier to meet**, not harder. The real error is
    that nobody tried the obvious decoder first.

### 3.2 Ask 1: C9 V-BACK (the most consequential claim)
- **Not a feed bug.** The plants are built in `make_plants` with a 6L key at offset 0 and sign −1, and the keyskip
  control through the identical path is 40/40 for both beams.
  - V-BACK leaves the ciphertext length equal to L, so there is no misalignment from length.
  - The failure has the predicted signature. A backstep shifts the key alignment by −1 for the rest of the window,
    and no forward-only relation (ks1, ks2, free ≤ 40) can follow it.
  - The expected first backstep comes after ~29/supp ≈ 36 runes, so recovery should be ≈ 0.15 + 0.85/29 ≈ 0.18.
    Observed: 0.188 / 0.194.
- **Representational, and closable.** `x1_c9_ext_decoder.py` is skipdecode's beam plus one BACK transition
  (p = c − K[j−1], allowed iff p + K[j] = c_prev, pointer stays) and one NULL transition. Through the unchanged C9
  checker (seed 4701, 40 plants, C3 7/7) it scores:
  - V-BACK **32/40 PASS** (0.80, Wilson 0.65–0.90), mean recovery 0.909, median correct-key score −4.296;
  - V-NULL 8/40 fail;
  - keyskip 36/40 (my arbitration between the two beams costs 4).

  So the correct key is visible to a beam that has the relation. The 0/40 is the L7-B envelope, exactly as H1 says.
- **Plausibility against LP2 statistics.** `x1_surface_stats.py` (20 replicate 12,956-rune English plants per
  variant) gives z of LP2 against V-BACK of −0.38 (lag-1), −0.59 (lag-2) and −0.27 (IoC·N). Keyskip gives −0.51,
  −0.72 and −0.18.
  - V-BACK is **not** excluded the way the old V-NULL was.
  - Its only trace, key reuse (c_t − c_{t−1} = p_t − p_{t−1} at a backstep), needs the key.
  - Nothing measured raises its prior either (doctrine Q2). It is one of an unbounded family of non-monotone loops,
    chosen for being a one-character edit.
- **Ruling.** "No beam-based ledger negative covers V-BACK" is **correct**. The weight H1 gives it needs two
  qualifiers: it is a representational gap that a ~20-line relation closes, and it carries no evidence that LP2
  uses V-BACK. The right follow-up is an in-house beam_v3 relation plus a re-run of beam-based negatives under it,
  not an outside heavy lift.

### 3.3 Ask 2: C10 and the R46-L1 qualification
- **Detection claim: verified.** At seed 4702 the baseline detection is 0.830 (my run, identical). On held-out
  *Dracula* at seed 4704 it is 0.918. "b′ ≤ 0.033 means can't recover, not can't see (at FPR 0.01, key in hand)" is
  correct as stated.
- **New and stronger result: FOUND-ERROR (C10 is not a heavy lift).**
  - `x1_c10_beam_attack.py` (58 lines) is a beam bucketed by rune position. It branches over the distinct remaining
    lengths of the current sentence's printed multiset, decodes word k at J_k (which depends only on k), and scores
    with lp.score quadgrams at beam width 16.
  - It **crosses the finish line through the unchanged checker**:
    - seed 4702 on dev texts: **481/500 (0.962)**, mean recovery 0.957, null FP 0.000, 73 s;
    - seed 4704 on held-out *Dracula*: **488/500 (0.976)**, null FP 0.000, 51 s.
  - It uses only (C, K, printed).
  - A first version that let different-length prefixes compete in one beam got 0/30. Shorter prefixes win on total
    log-probability; bucketing by position is the whole fix.
- **What this means for R46-L1's (b′) statements.** For the U2b word-jump class at known key, the (b′) loss belongs
  to the printed-start decoder, not to the information in the print.
  - "Conditional under (b′)" for R37-U2b now means "not re-run with a segmentation search". That re-run would cost
    roughly 0.1 s per unit-key instead of microseconds.
  - It does not mean "blind".
  - Rewording is needed. See 3.6 #7 for H1. The R46-L1 sentence is in §5 below for the coordinator.
- Not covered: an unknown key at sweep-scale bars, the doublet filter, and the other word-indexed constructions.

### 3.4 Ask 3: Gameability. FOUND-ERROR for all four checkers
| checker | cheat (file) | result |
|---|---|---|
| C7 | Dracula (English) labelled `language: non`, `register: Old Norse saga prose` (`x1_cheat_c7_manifest.json`) | validates; prints **"NEW REGISTER: this crosses the C7 finish line. Submit it"** (`out_x1_cheat_c7.txt`) |
| C8 | `score()` walks to `evaluate()` and returns 1.0 while `sp` is unbound (positives), 0.0 after (nulls) (`x1_cheat_c8.py`) | power **1.000** at L=236 against all four nulls (`--direct`; the trick does not depend on the protocol) |
| C9 | `decode()` reads `evaluate()`'s local `P` and `K`; returns P for the plant key, zeros otherwise; reference beam for C3 (`x1_cheat_c9.py`) | C3 7/7, V-BACK 40/40, V-NULL 40/40, wrong FP 0.00, **"FINISH LINE MET"** (seed 99) |
| C10 | `attack()` reads `evaluate()`'s loop tuple `c` (`c[3]` = plaintext) (`x1_cheat_c10.py`) | 500/500, null FP 0.000, **"FINISH LINE MET"** (seed 99) |

- The seal (hidden seed, held-out text) does not help against frame reading. The cheat reads the live plaintext.
- The plants themselves cannot be read in advance: seeds come from `os.urandom`, and the variant code is public by
  design, as H1 notes.
- Every cheat is obvious on code review. So the practical fix is to:
  - run submissions in a subprocess that receives only (C, K[, printed]) or idx and returns only `plain_idx` or a
    float;
  - change "FINISH LINE MET" to "finish line met, pending code and source review";
  - for C7, add a language-ID screen (for example, the English quadgram score of the folded source) before printing
    a crossing.
- H1 §4 anticipated the C7 and C8 labels. It did not anticipate the in-process frame access.

### 3.5 Other checks
- **C8 framing.** "At FPR 0.01 the register gap is narrower than L7-A suggests" compares a learned FPR-0.01
  threshold with L7-A's fixed −5.5 median rule at L = 120. Both are true. But sweep-scale bars, which is where
  L7-A's consequence lives, are not measured, and the ledger row's `not_covered` says so. The headline should carry
  the same qualifier (3.6 #2).
- **The numbers recompute.** These match `baseline_extra.json` and the `out_*` files: C9's table, C10 0/500 and
  0.331 / 0.319, C8 vowel-dropped English 0.00 / 0.325 at L = 236, and the C7 Latin 8.36 %.
- **Plants run through the lanes' own glue.** C9 and C10 recompute the English score from the returned `plain_idx`.
  C10's ceiling decodes 500/500 exactly.

### 3.6 Required corrections (H1 `RESULTS.md`, `ledger_rows.json`, `CHALLENGES.md`; coordinator applies)
1. **RESULTS §0, C9 bullet:** after `No beam-based negative in the ledger covers V-BACK.` insert ` It is a representational
   gap, not a hard one: a beam with one added backstep relation recovers 32/40 V-BACK plants through this checker
   (R47-X1, dev seed). V-BACK is consistent with LP2's surface statistics, but no measured fact raises its prior.`
2. **RESULTS §0, C8 bullet:** replace `**C8: at FPR 0.01 the register gap is narrower than L7-A suggests.**` with `**C8: at
   FPR 0.01 (not at sweep-scale bars, which were not measured) the register gap is narrower than L7-A's −5.5 rule
   suggests.**`
3. **RESULTS §0, C10 bullet:** append ` R47-X1 then crossed the re-aimed C10 finish line with a 58-line within-sentence
   segmentation beam (481/500 and 488/500, null FP 0), so for the U2b class at known key the (b′) recovery loss belongs to
   the printed-start rule, not to the information in the print.`
4. **CHALLENGES.md C9:** replace the text from `, because the transition-model` up to `covers these two loops.`
   (the end of the C9 finish-line paragraph) with:

   ```text
   . V-BACK is the transition-model gap: no beam negative covers it, though a backstep relation closes it
   (R47-X1, 32/40). V-NULL is a recovery gap only: beam negatives already score its correct key as English (−4.54).
   ```
5. **CHALLENGES.md C9, V-NULL bullet:** replace `This is the solved pages' interrupter, triggered by the doublet rule.` with
   `Because the rejected key symbol is discarded, the key still advances once per cipher rune, so beams stay in sync; unlike
   the solved pages' interrupters it does not shift the key.`
6. **CHALLENGES.md C10, and the summary and cost tables:** mark C10 **crossed in-house (R47-X1)**. Replace the C10 row
   `| weeks |` / `baseline **0/500**` with `crossed by R47-X1 (0.962 / 0.976)`, and remove C10 from the heavy-lift cost
   table, or re-scope it (unknown key at sweep-scale bars, the doublet filter, other word-indexed constructions).
   Replace `The attack that would still work has to search
  arrangements of each sentence's word lengths. That is a combinatorial search, which is where big agent
  loops and big CPU budgets help.` with `A position-synchronous beam over each sentence's length multiset recovers
  U2b plants at known key (R47-X1); what remains open is the unknown-key sweep and the other constructions.`
7. **H1 ledger row R47-H1-C10-SHUFFLED-LENGTHS-BASELINE:** append to `result`: ` A within-sentence segmentation beam
   recovers 0.962 / 0.976 (R47-X1-C10-SEGMENTATION-BEAM-CROSSING).`
8. **All four checkers:** the "FINISH LINE MET" / "NEW REGISTER … Submit it" messages should read `… pending code and
   source review (in-process submissions can read checker state; R47-X1)`. Add a line to the "How sealing works"
   paragraph of CHALLENGES.md: `Submissions run in the checker's process; credit also requires code review.`
9. **H1 ledger row C9:** append to `result`: ` V-BACK gap is representational (R47-X1-C9-VBACK-BACKSTEP-RELATION).`

---

## 4. Reproduce (from repo root, `PYTHONUTF8=1`)

```bash
X1_BEAM=16 python challenges/c10_shuffled_lengths.py liber-primus/analysis/round47/X1-redteam/x1_c10_beam_attack.py --n 500 --seed 4702
X1_PEN=3 X1_NC=7 python challenges/c9_rejection_loops.py liber-primus/analysis/round47/X1-redteam/x1_c9_ext_decoder.py --plants 40 --seed 4701
python liber-primus/analysis/round47/X1-redteam/x1_surface_stats.py
python challenges/c10_shuffled_lengths.py liber-primus/analysis/round47/X1-redteam/x1_cheat_c10.py --n 500 --seed 99
python challenges/c9_rejection_loops.py liber-primus/analysis/round47/X1-redteam/x1_cheat_c9.py --plants 40 --seed 99
python challenges/c8_register_scorer.py liber-primus/analysis/round47/X1-redteam/x1_cheat_c8.py --heldout liber-primus/data/keys/armada19/stoker_dracula.txt --direct --pos 50 --null 200 --beam-null 20 --seed 99
python challenges/c7_corpus_forge.py <dir with x1_cheat_c7_manifest.json as manifest.json> --build --seed 1
```

## 5. For the coordinator (outside X1's scope)
- **R46-L1 RESULTS line 29–30.** After `every word-indexed row
  falls to ≤ 0.033 (7-gram shape 0.033; all others 0).` add ` That is each row's own decoder fed the printed lengths. For
  the U2b class at known key, the printed-start rule still detects at 0.83 (FPR 0.01, R47-H1), and a segmentation beam
  recovers 0.96 (R47-X1). So (b′) is a decoder conditional, not a blindness bound.` Apply the same qualifier to
  R46-L1-REOPEN-VERDICTS / R46-L1-R37-U2B-U3-RECHECK.
- **Follow-up lane (Round 48 candidate).** Add a BACK relation to beam_v3 and re-run the R37-U2b real job under the
  segmentation beam. Both are cheap and in-house, and both close named conditionals.

---
CLOSED 2026-11-24 R47-X1 red-team | T2 UPHELD-WITH-CORRECTIONS (9877 "no doublet site" wrong: M would make an MM doublet, 5.3:1 prior for D) | L2 UPHELD-WITH-CORRECTIONS (faithfulness, conventions, bests, 8 bars exact; b′ wording) | H1 UPHELD-WITH-CORRECTIONS (V-BACK gap real + closable 32/40; C10 CROSSED by X1 beam 0.962/0.976; all 4 checkers cheatable in-process/by label; V-NULL is not an L7-B gap) | 5 ledger rows R47-X1-… | no LEDGER.json edit, no commit
