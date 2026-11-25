# Round 47 / H1 — heavy-lift public challenges C7–C10: PREREG

_Pre-registered 2026-11-24, before any checker in this lane produced a number. Lane spec:
`analysis/round47/CAMPAIGN-PLAN.md` §1 row H1 and §2. Inputs read before writing (code and docs only):
`CHALLENGES.md`, `challenges/{_common.py, c2_short_recognizer.py, c3_decoder_gates.py, c5_t7_mechanism.py,
examples/rigid_decoder.py}`, `AGENTS.md`, `ARMADA-DOCTRINE.md`, `benchmark/{gates.py, plant.py}`,
`campaign18_skip/skipdecode.py`, `round33/I1-register-aware-beam/beam_v3.py`, `round32/I1-skipbytwo-decoder/beam_v2.py`,
`round32/I2-multiregister-readjudication/adjudicate.py` (Panel API), `round36/P1-panel-r36/RESULTS.md`,
`round37/C1-composed-clue-readings/{c1lib.py, enciphers_u2_u3.py}`, `round45/W1-spaces/w1lib.py`,
`round46/P1-leads/{p1lib.py, RESULTS.md}`, `round46/L1-word-loader/{words.py, l1lib.py, arm_r41.py, arm_r37.py,
arm_7gram.py, RESULTS.md, ledger_rows.json}`, and the LEDGER rows L7-A-SCORER-ENGLISH-ONLY, L7-B-BEAM-ENVELOPE,
R36-P1-PANEL-R36-GATE, R46-L1-R41-R14-RERUN, R46-L1-REOPEN-VERDICTS, R46-P1-TWO-RUNE-EXPLANATIONS.
One timing probe (reference beam and beam_v3 on one 240-rune plant) was started before this file was finished; it
produces no challenge number and no threshold below depends on it beyond the default sample sizes._

## 0. What this lane is

An **instrument / community** lane (doctrine R1, R5 rank 3). No key space is swept and nothing about LP2's
plaintext is claimed. The deliverable is four checkers under `challenges/`, each with a finish line fixed here, a
baseline measured by this lane, and the ledger row a crossing would change. Every number this lane reports is a
**baseline power of the repo's current instrument** on a plant class the checker defines.

## 1. The four challenges (design frozen here)

### C7 — Reference-corpus forge (`challenges/c7_corpus_forge.py`)

*Question:* R46-P1 placed LP2's 2-rune-word share (15.47 %) and 9-class length profile against English, Latin,
German, Welsh, Old English and the solved pages only. Greek, Hebrew, Norse and every other language are
`not_covered` in R46-P1-TWO-RUNE-EXPLANATIONS because no Gematria-Primus-transliterated corpus exists for them.

*Submission:* a directory with `manifest.json` (register, language, provenance: title, author, edition, URL,
licence = public domain, source sha256; a transliteration **table** grapheme → GP token list; separators and
sentence marks), `source.txt` (the public-domain text) and `corpus.txt` (one sentence per line, words joined by `-`,
written in runes). The checker can build `corpus.txt` from the table (`--build`) so nobody needs a private
transliterator; the value is in the table and the source.

*Checks:* manifest schema; source sha256; every table value is a sequence of the 29 canonical GP tokens; unmapped
characters ≤ 0.1 % of letters; `corpus.txt` line count = derived sentence count and a seeded sample of 500 sentences
re-derived from the table equals the corpus byte for byte; ≥ 20,000 words and ≥ 1,000 sentences.

*Measurement (printed as a ready-to-add row):* 2-rune share, 9-class profile (classes 1..8, 9+), 1,000 contiguous
windows of 2,896 words (LP2's word count, `round46/L1-word-loader/words.py`), LP2's percentile among them, and the
R46-P1 T3 statistic: G of LP2's profile against the corpus profile vs the 99th percentile of the corpus's own
window G (admitted / rejected).

*Covered registers (a submission in one of these validates but is not a crossing):* modern/archaic/translated/verse
English (R45-W1 + R46-P1 T1, 30 + 8 corpora), Latin (Aeneid, latin_218), German (Faust, de_2), Welsh (Mabinogion),
Old English (Beowulf), solved Cicada pages.

*Finish line:* checker PASS on a corpus in a register **not** in that list (e.g. Koine Greek, Biblical Hebrew,
Old Norse, Middle English, Vulgate Latin, Old Irish, Gothic, Old Icelandic). *Changes:* adds a reference to
R46-P1-TWO-RUNE-EXPLANATIONS / -DEFICIT-REPLICATION (`not_covered` "Greek, Hebrew, Norse … and other languages").

*Seed example:* Latin, *Aeneid* (`data/keys/armada19/virgil_aeneid_latin.txt`, committed), R-A GP table, built in
memory by `--self-test` (covered register; demonstrates the format, not a crossing).

### C8 — Non-English adjudicator (`challenges/c8_register_scorer.py`)

*Question:* L7-A: every negative is an English-register negative unless re-adjudicated. Panel-R36 covers 12
registers (EN_MODERN, EN_KJV, LP1_REAL, LATIN, OE, DE, CY, EN_HALFVOWEL, EN_NOVOWEL, GREEK, HEBREW, NORSE).

*Submission:* a module with `REGISTER = "<name>"` and `score(idx: list[int]) -> float`, plus a held-out text in
that register (a rune file, or a C7 manifest the checker transliterates).

*Protocol:* windows of L = 236 runes (LP2 mean page = 12,956 / 55 = 235.6), also L = 120 and 60 reported.
**Positives** = held-out windows planted with the repo's standard plant: keyskip encipher
(`skipdecode.encipher_keyskip`, supp = `plant.EXACT_SUPP`) under a fresh SHA-256-counter key, then decoded with the
correct key by the C3 reference beam (`skipdecode.beam_decode`, w = 400, max_skip 3); the decode is what is scored.
`--direct` skips encipher/decode for fast iteration (not valid for a claim). **Null classes:** (u) uniform random
runes, (r) real LP2 windows from the 12,956-rune unsolved stream, (s) the positive windows shuffled, (w) beam
decodes of real LP2 windows under a wrong SHA-256 key. Threshold per class at its (1 − FPR) quantile; the
reported threshold is the **maximum** over classes, so FPR ≤ 0.01 against every class.

*Baselines (this lane):* the English reference (`lp.score` quadgram `score_norm`) and the incumbent panel-R36
pmax (`data/panels/panel-r36.npz`), on in-repo held-out texts.

*Finish line:* power ≥ **0.80** at FPR **0.01** at **L = 236**, against every null class, for a register not among
the 12 panel registers, re-confirmed by the maintainers on their own held-out text of that register at a seed
chosen at review. *Changes:* L7-A-SCORER-ENGLISH-ONLY `not_covered` ("languages not modelled") and the panel's
register list. If the incumbent panel-R36 pmax already reaches 0.80 on the same windows, the result is filed as
"register already seen by panel-R36" (a coverage measurement), not as an extension.

### C9 — Second rejection-loop decoder (`challenges/c9_rejection_loops.py`)

*Question:* L7-B: every beam negative covers the transition relations the beam represents. beam_v3 represents
keyskip1, keyskip2 and a `free` relation (any **forward** key advance ≤ 40, ≤ 2 unexplained, penalty). Every
relation is monotone in the key pointer and maps every ciphertext rune to exactly one plaintext rune.

*Sealed variants (outside every beam_v3 relation by construction):*
- **V-BACK (backstep):** on a would-be doublet, with probability supp the encipherer steps the key pointer
  **back** one place (`j -= 1`, the one-character sibling of keyskip's `j += 1`) and retries; it then continues
  from the new pointer. Key symbols are reused; the pointer is non-monotone.
- **V-NULL (null insertion):** on a would-be doublet, with probability supp the encipherer emits a null rune
  (uniform, ≠ previous and ≠ the rejected value) that consumes **no key**, then emits the rejected value. Ciphertext
  is longer than plaintext; the interrupter mechanism of the solved pages, triggered by the doublet rule.
- **V-DEFER (diagnostic, not required):** the rejected key symbol is held back and used for the **next**
  plaintext rune (local key swap). Reported only.

*Protocol:* English plaintext windows of 240 runes from the dev texts (held-out text at review), fresh SHA-256-counter
key per plant, supp = EXACT_SUPP, sign −1, key offset 0 (the C3 setting). The checker **recomputes** the English
score of the returned `plain_idx` itself. Plant passes iff positional rune recovery ≥ 0.85 and recomputed score
≥ −5.2; the same ciphertext under an independent wrong key must score ≤ −6.0. Variant passes iff ≥ 80 % of its
plants pass and wrong-key false positives ≤ 5 %.

*Baselines (this lane):* C3 reference beam (`skipdecode.beam_decode`) and beam_v3 panel_max under advance 1, 2 and
`free` (best recovery of the three, panel-R36).

*Finish line:* C3 7/7 **and** V-BACK and V-NULL both pass on 40 sealed plants each, at a maintainer seed and on
held-out plaintext. *Changes:* L7-B-BEAM-ENVELOPE (the transition-model conditional of every beam-based negative)
gains a second qualified decoder; this lane's baseline row records how the current beams fare on the two variants.

### C10 — Attack under shuffled word lengths (`challenges/c10_shuffled_lengths.py`)

*Question:* R46-L1 (b′): with printed lengths permuted within sentence, every word-indexed row of the battery fell to
≤ 0.033 power. Is any attack able to recover power when only the per-sentence length **multiset** and the sentence
boundaries are trustworthy?

*Plant (the R37-U2b word-jump construction on the benchmark's derived-key family):* a unit = consecutive whole
English sentences totalling 236–472 runes (re-drawn if longer). Base key K = SHA-256-counter keystream from a fresh
seed. Rune i of **true** word k is enciphered with K[i + J_k], J_k = Σ_{j ≤ k} S[j], S[j] = PRIMES[j mod 29] (the GP
prime values), c = (p + K[·]) mod 29 (decode p = c − k). The print shows the true sentence boundaries and the true
word lengths **permuted within each sentence** (regime b′). **Null** = the same unit, the same print, enciphered
under an independent key K′; the attack is still handed K. The attack gets `(C, K, printed)` and returns a float.

*Baseline (this lane):* the L1-battery rule for U2b applied to the printed lengths — jumps at the printed word
starts, decode, English `score_norm`. Positive control: the same decoder with the **true** lengths must reproduce the
plaintext exactly on every plant (asserted in `--self-test`).

*Finish line:* power ≥ **0.80** at FPR **0.01** and at least **0.30** above the baseline measured in the same run, on
500 plants + 500 nulls at a maintainer seed and held-out text. *Changes:* R46-L1-REOPEN-VERDICTS and
R46-L1-R37-U2B-U3-RECHECK (b′ power ≤ 0.033 / 0/64) for the word-jump class.

*Why not the R41 W1–W4 class:* its key is constant within a word, so the ciphertext's within-word differences are
plaintext differences and a print-free difference statistic would see it regardless of b′ (not measured here). That
is not a b′ question, so it is not the plant.

### Sealing (all four)

Every checker draws fresh plants from `--seed` (default: 64 random bits from `os.urandom`, printed so a run can be
reproduced). Credit is decided at review: the maintainers post sha256(seed) in the submission issue, run the checker
at that seed (C8/C9/C10 also on held-out text they choose then), and reveal the seed with the verdict. Fixed dev
inputs are public and can be overfit; the sealed run cannot.

## 2. Aiming Test

**Q1 — What would a hit look like, and would this instrument recognise it?** A hit is a submission the checker
passes. Each checker carries its own positive control in `--self-test`: C7 rebuilds the Aeneid example and must
re-derive it exactly, and must FAIL a deliberately corrupted copy; C8 must give the English scorer power ≥ 0.8 on
English held-out text (else the null/plant path is broken); C9 must pass the reference beam on keyskip plants
(the variant it represents) and run C3; C10 must decode every plant exactly with the true lengths and keep the true-
length decoder at power ≥ 0.95. A self-test whose control fails exits non-zero.

**Q2 — What measured fact raises the prior?** L7-A (`round18/L7`, LEDGER L7-A-SCORER-ENGLISH-ONLY), L7-B
(L7-B-BEAM-ENVELOPE: the beam's relation is exact for one construction), R46-L1 (b′ power ≤ 0.033 for every
word-indexed row, `round46/L1-word-loader/RESULTS.md` §3) and R46-P1 (`not_covered` Greek/Hebrew/Norse). These are
instrument gaps, measured, not lore. The challenges aim outside compute at exactly those gaps (doctrine R1).

**Q3 — Is the space bounded?** No key space. Each checker's plant space is samplable and stated: C8 windows of a
held-out text; C9 two (+1) constructions × L = 240 × fresh keys; C10 sentence units × fresh keys; C7 a finite text.

**Q4 — Three conditionals.** Every baseline row states: (1) key space: none swept, correct key known (C8–C10 power
is measured at the correct key, wrong-key nulls); (2) transition model: C8 keyskip1 beam; C9 the three named
variants; C10 the U2b word-jump construction without the anti-repeat filter; (3) register: C8 the held-out register;
C9 and C10 English plaintext, English adjudication (an English-only negative, L7-A).

**Q5 — Kill condition at 10 % of budget.** (i) If the plant path cannot reproduce the C3 gates (reference 7/7)
from `challenges/`, stop and report. (ii) If C10's true-length decode does not reproduce the plaintext exactly, the
plant is wrong; stop C10. (iii) If a full baseline run of any checker exceeds 30 min on this machine at default
sizes, reduce the default sample size (stating it) rather than ship a checker nobody can iterate with.

## 3. What this lane will not do

No sweep, no claim about LP2's plaintext, no LEDGER.json edit, no commit, no network. Baseline numbers are reported
as power of the current instruments on the checker's plant class and carry the conditionals above. If the baseline
already crosses a finish line (the current instrument already sees the class), that is reported as the result and
the challenge text says so; the threshold is not moved.

## Addendum 1 (2026-11-24, after the first C9 self-test, before any C8/C10 number)

**V-NULL redefined.** As registered, V-NULL emits a null and then the *rejected* value, so every null sits between
two equal runes. A surface check run while building the checker (`c9_rejection_loops.py` variants on 13,000-rune
English plants vs the real stream) shows that leaves a lag-2 repeat rate of **6.0 %** against LP2's **3.40 %**, i.e.
the registered V-NULL is already excluded for LP2 by a one-line statistic and would make a pointless sealed
variant. V-NULL is therefore: *on a would-be doublet, with probability supp, emit a null (uniform, ≠ previous rune)
that consumes no key, discard the rejected key symbol, and retry with the next key symbol.* Measured at supp =
EXACT_SUPP on English plants: lag-1 0.67 %, lag-2 3.51 % (LP2 0.66 % / 3.40 %). V-BACK (0.69 % / 3.60 %) and V-DEFER
(0.70 % / 3.56 %) were checked the same way and are unchanged. Thresholds are unchanged. The first self-test's
V-NULL row (old definition: reference beam 0/12, beam_v3 0/12) is superseded and not reported as a baseline.

## Addendum 2 (2026-11-24, after the first C10 self-test at the registered metric)

**Registered C10 result, kept as measured:** seed 4702, 500 plants + 500 nulls, the printed-start decoder (L1 rule)
has power **0.830** (Wilson 0.795–0.860) at FPR 0.01 against the matched wrong-key null; the true-start ceiling is
1.000 and 500/500 plants decode exactly at the true starts. The registered finish line (≥ max(0.80, baseline + 0.30)
= 1.13) is therefore **unreachable**, which §3 says is reported as the result, not hidden by moving the threshold.

**Why, and what it means.** A known-key detection test at FPR 0.01 is far easier than what R46-L1 measured: L1's
rules required exact (R41) or ≥ 0.90 (R37 `judge()`) recovery plus sweep-scale bars (N = 10⁶). The words that keep
their place (sentence-initial words whose printed length happens to match, and every word after a coincidental
re-alignment) decode correctly and lift the English score above the wrong-key floor. So "b′ power ≤ 0.033" is a
statement about **recovery at sweep-scale bars**, not about total blindness; at FPR 0.01 with the key in hand the
printed-start rule still detects. This goes into RESULTS and the ledger row as a qualification of R46-L1.

**C10 re-aimed (new metric; the registered one is retired, not edited).** The challenge becomes *recovery*, the
quantity L1's rules measured: `attack(C, K, printed) -> plain_idx`. A plant passes iff rune recovery ≥ **0.90**
(R37 `judge()`'s recovery bar) and the checker-recomputed English score ≥ −5.2; the attack run on each null must
keep the recomputed score ≤ −5.2 on ≥ 95 % of nulls. **Finish line:** ≥ **0.80** of 500 plants pass (and the null
condition holds) at a maintainer seed and held-out text. Baseline and ceiling are the same two decoders as before.
Plant, null, sealing and sizes are unchanged.

## Addendum 3 (2026-11-24, R47-H2, written after R47-X1's audit and before any number of the redesigned C10)

_Appended by lane R47-H2 (`analysis/round47/H2-harden/`). The text above this heading is unchanged; its stamps
(`7d769769…`, `2489c7b4…`, `21a32c12…`) still verify on the prefix before `## Addendum 3`. This addendum is stamped
in `H2-harden/run.log` before the first C10 baseline below is run. Disclosed probes before the stamp: a numpy-vs-
Python equality check of the key family and one timing of the exhaustive ranker (2.5 s per unit); neither
produced a recovery number._

**Why.** R47-X1 crossed the re-aimed C10 (Addendum 2) with a 58-line within-sentence segmentation beam (0.962 /
0.976, null FP 0) because the attack was handed the key. That crossing stays recorded as a result: with the key in
hand, the (b′) loss for the U2b class is the printed-start decoder's, not the information's
(R47-X1-C10-SEGMENTATION-BEAM-CROSSING). The registered and the re-aimed C10 are both retired, not edited; the old
checker is preserved at `H2-harden/c10_v1_keyed.py`.

**C10, redesigned.** Plant and print as before (R37-U2b word jump, whole English sentences, 236–472 runes, lengths
shuffled within sentence, sentence boundaries true), except the key is **unknown**: per unit, s is drawn
uniformly from a stated bounded family of F = 2¹⁶ keys, K_s[t] = splitmix64(SALT + s·2³² + t) mod 29
(`c10_shuffled_lengths.key_stream`). Null = the same construction under a key from outside the family
(s ≥ 2²⁰). Submission: `attack(C, printed) -> plain_idx`, run in an isolated child process, 60 s wall-clock per
unit. Plant passes iff recovery ≥ 0.90 and recomputed English score ≥ −5.2; null condition: output score ≤ −5.2
on ≥ 95 % of nulls. Scored size n = 100 plants + 100 nulls.

**Baselines (all at dev seed 4710, n = 100 + 100 unless stated):**
- (i) the repo's decoder exhaustive over all F keys with the TRUE lengths (rank by rune-bigram, re-score the top 64
  by quadgram). Control: must pass ≥ 0.95 with null FP ≤ 0.05, else the family is not "solvable when spaces are
  true" and C10 is stopped.
- (ii) the same with jumps at the PRINTED starts (L1 rule).
- (iii) R47-X1's arrangement beam (width 16) given no key, i.e. per key. Full enumeration is F × t_key per unit,
  so it is measured on 16 plant units (correct key + 1,024 sampled wrong keys: does the correct key out-score all
  sampled?) and 16 null units (max over 1,024 keys); cost extrapolated to F. Reported, not used in the rule
  below (it does not fit the 60 s budget by construction if t_key × F > 60 s).
- (iv) two-stage, the obvious composition of (ii) and (iii): rank all F keys by the printed-start decode, run X1's
  beam on the top m, return the best; m = 64 and m = 512 (n = 100 + 100 each).

**Finish-line rule (fixed here).** B = the highest plant pass rate among (ii), (iv m=64), (iv m=512), counted
whatever their null FP. FINISH = max(0.80, B + 0.20), rounded up to a multiple of 0.05. If FINISH > 0.95, C10 is
**not** published as a heavy lift: CHALLENGES.md says the redesigned C10 is crossed or nearly crossed in-house at
this family size, and a re-scope (larger F, or the doublet filter) goes to Round 48. The threshold is not moved
after the numbers. If (i) fails its control, C10 is retired pending R48.

**C9 (re-scoped per R47-X1 §3.2).** V-BACK is no longer scored: one backstep relation recovers 32/40 (R47-X1, dev
seed), so it is a representational gap closable in-house, scheduled for Round 48 (re-adjudicate beam negatives with
a backstep-aware beam). C9 keeps V-NULL only (a recovery gap no backstep relation represents). Thresholds for V-NULL
are unchanged. Crossing V-NULL changes no beam negative's detection claim (the beams already score its correct key
as English, −4.54); it changes the recovery qualifier only.

**C7 label gate (calibrated, not pre-registered).** A corpus whose GP bigram profile is within JSD 0.06 of the
English reference or of a covered language other than its claimed one is rejected. τ was set from in-repo texts
(H2 RESULTS §2) so that the Latin worked example passes and R47-X1's English-labelled-as-Old-Norse corpus fails.

**Isolation (C8, C9, C10).** Submissions run in a `python -I` child that receives only the inputs the challenge
grants, in a random order from os.urandom. R47-X1's four cheats are re-run as regression tests and must fail.
