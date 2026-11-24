# R45-W1 — What are the printed spaces? (pre-registration)

_Dated 2026-11-23, written before any W1 output file. Lane W1 of Round 45 (`../CAMPAIGN-PLAN.md`).
Binding: `ARMADA-DOCTRINE.md`. Thresholds below are frozen; any change goes in a dated addendum
at the bottom with its reason. Lane writes only inside `analysis/round45/W1-spaces/`, does not commit._

## 0. Premise and prior inputs (already seen before this PREREG)

- Fable52 T4/T4b (`analysis/fable52/OUTPUTS.txt`): adjacent word-length MI on the 2,896 printed LP2 words is
  shuffle-level (z = +0.51); the solved-LP reference scores z = +7.43 on ~875 words. Fable52 T8 (between-unit
  ANOVA of length) **failed its English control** — it is uninformative and is not reused as a verdict.
- No W1 statistic has been computed on LP2 before this file. Parser sanity checks only (rune identity of
  `data/krisyotam_runes.txt` vs `dataset/liber_primus.json`: identical over 13,136 runes; rtkd LP2 part identical).

## 1. Inputs (pinned)

- **LP2 unsolved**: `data/krisyotam_runes.txt` (in-repo, rune-identical to the canonical dataset), first 12,956 runes.
  **AN END + PARABLE** (last 180 runes) are *solved* and go to the solved reference.
- **LP1 (solved)**: `data/sources/rtkd_master.txt`, the 2,797 runes before the LP2 start (located by rune match).
- **Parsing rule (same for LP1 and LP2, frozen)**: word break = any of `- . & $ §` or a numeric token; `/`, newline
  and `%` (line/page) do **not** break a word (words wrap across lines and pages; verified on LP1 e.g. ᚹᛏᚣᛈ/%ᚻ = one
  word). Numeric tokens are breaks but not words. A word is assigned to the line/page/paragraph/section where it
  **starts**. Units: sentence = `.`-delimited (also closed by `&`,`$`,`§`); paragraph = `&`; section ("chapter") = `$`;
  page = `%`; line = `/`.
- **LP1 plaintext reference** for transliteration calibration: `lp1-plaintext-reference.txt` (FlareZ123 resources,
  derived from krisyotam decoded pages) copied to `inputs/` with sha256 recorded in `calib.json`.
- **English corpora** (GP-transliterated): `data/{kjv,moby,pride,war}.txt`, `data/keys/{king_in_yellow,mabinogion,
  self_reliance,book_of_the_law}.txt` (Gutenberg headers stripped; wiki/HTML markup stripped).
- **GP transliteration** — calibration step (not a test): three frozen candidate rules, chosen by exact
  word-length agreement with the printed LP1 lengths over aligned LP1 words:
  R-A greedy {ING, TH, EO, NG, OE, AE, IA, IO, EA} one rune each, K/Q→C, V→U, Z→S (Fable52 `gp.py`);
  R-B only {ING, NG, TH} digraphs; R-C one letter = one rune. Highest agreement wins; ties → R-A.

## 2. Statistics, nulls, plants (per question)

Length classes: 1..7 and 8+ (8 classes) unless stated.

### Q1 — order and scope
- **A_U (order inside scope U)**: (i) LLR = Σ over adjacent pairs of log P_E(b|a)/P_E(b), with P_E an English
  length-transition model (add-one) trained on the **first half** of each English corpus (plants drawn from second
  halves); (ii) MI of adjacent length classes (model-free). Null = shuffle of lengths **within each U-unit**,
  U ∈ {global, sentence, line, paragraph, page, section}. One-sided (upper).
- **B_U (composition at scope U)**: (i) G-statistic of unit × length-class table; (ii) between-unit SS of mean
  length. Null = global shuffle. U ∈ {sentence, line, paragraph, page, section}. One-sided.
- **C (local ordered patch scan)**: per-pair LLR scores, windows w ∈ {25,50,100,200,400} words, step w/2,
  z_w = (S_w − mμ)/(σ√m) with μ,σ from the stream's own random pairing; statistic = max z over all windows and
  scales; null = same max on global shuffles (look-elsewhere built in).
- **D (per-unit max)**: per-page and per-section LLR z (each unit's z standardised by within-unit shuffle draws);
  statistic = max over units; null = same max over the within-unit shuffle draws.
- **Plants (positive controls), 2,896-word English windows from corpus second halves**: P0 intact; P_U = lengths
  shuffled within U for U ∈ {sentence (the English text's own sentences), line, paragraph, page, section (LP2's
  units mapped by word index)}; P_glob = global shuffle. Also the **solved Cicada reference** (LP1 + AN END +
  PARABLE printed lengths) run through A_global. For C: an intact English patch of w words inserted into a
  globally shuffled LP2-like background.
- **Pass/"informative" criteria (frozen)**: A_U is informative if power ≥ 0.8 on P0 at its per-test α.
  B_U is informative *for scope discrimination at U* if power ≥ 0.5 on P_U and its size on P_glob ≤ 2α.
  C reports power per w; D reports power for a single intact English unit planted into shuffled background.
  A test failing its criterion is reported **uninformative**, never negative.

### Q2 — multiset
- **M1** LP2 vs solved-Cicada multiset: two-sample G (classes 1..9+), permutation null.
- **M2** LP2 vs English: distance = G of LP2 counts against corpus Y's smoothed distribution, min over Y.
  Reference null = same min-distance for 2,896-word windows of corpus X against Y ≠ X (leave-own-corpus-out).
  p = fraction of English windows at least as far. Direction reported (mean, P(1), P(2), P(≥8)).
- **M3** geometric (random independent space insertion, P(L=k)=p(1−p)^{k−1}, MLE p): parametric-bootstrap G GOF.
  Descriptive AIC comparison vs shifted Poisson, uniform-on-support, English-best.
- **M4** fixed-period / keyed generator: for P = 2..300, between-phase SS of lengths by i mod P, standardised
  per P on shuffles; statistic = max over P; null = global shuffle. Plant: lengths = K[i mod P] (K drawn from the
  LP2 multiset) with probability f, else random from multiset; P ∈ {13, 29, 97}, f ∈ {0.1, 0.2, 0.3}.
- Controls: M1/M2 size and power via English-vs-English and English-vs-other-corpus samples at LP2/Cicada sizes;
  M3 power is trivially checked by planting geometric lengths and English lengths.

### Q3 — leakage
- **L1** G of position-class {start, interior, end, single} × rune value (29). Null = circular shift of the whole
  boundary pattern relative to the rune stream (offset uniform in [50, N−50]).
  Plants: (a) LP2 runes with a fraction q of boundaries moved to the nearest rune in a random 4-set S (±3 runes):
  content-keyed spacing; (b) English with true spaces enciphered by a short repeating Vigenère key (LP1-like);
  (c) English with true spaces under a uniform random key + doublet-rejection (OTP-class) — expected blind;
  (d) LP1 ciphertext (solved, real) reported as reference.
- **L2** doublet rate across printed boundaries minus within words; same circular-shift null. Plant: a fraction q of
  cross-boundary adjacencies replaced by non-filter-adjacent pairs (rate 1/29). Estimate of q with 95% CI.

### Q4 — rune order
- **R1** lag-1 vs lag-2..10 equality rates in printed order; upper 95% bound on the fraction of printed adjacencies
  (overall / at word breaks / at line breaks / at page breaks) that were **not** adjacent when the doublet filter ran.
- **R2** analytic statement + tiny numeric check: under a uniform key (with rejection filter) the ciphertext
  distribution is independent of plaintext order, so no key-independent plaintext-order statistic exists. Reported
  honestly, not as a test.

## 3. Multiple comparisons (frozen)

Family-wise α = 0.01 per question family, Bonferroni within family:
- Q1: 12 A + 10 B + 1 C + 2 D = **25 tests → per-test α = 4.0e-4**. Real-data nulls ≥ 10,000 draws.
- Q2: M1, M2, M3, M4 = **4 tests → 2.5e-3** (M4 null 1,000 draws → min p 1e-3; if p hits the floor, extend).
- Q3: L1, L2 = **2 tests → 5e-3**, 10,000 draws.
- Q4: estimates only (no test).
Plant power is measured with ≥ 150-draw nulls and a normal approximation to the per-test α (stated as such);
real-data verdicts use empirical add-one p.
Per-page / per-section individual z are descriptive; only D's max-statistic is a test.

## 4. Aiming Test

**Q1 — hit and recognizer.** A hit is any of: (a) order or composition in LP2's length stream at some scope, by
a statistic whose English plant at that scope fires; (b) an LP2 length multiset that is (or is not) English-shaped
beyond the English-vs-English spread; (c) runes or doublets that depend on printed boundary position beyond the
circular-shift null, at a q the plant shows detectable. Every recognizer is planted in the shape hunted (§2).

**Q2 — prior-raising fact.** Fable52 T4/T4b (`analysis/fable52/OUTPUTS.txt`): LP2 MI z = +0.51 vs solved-LP
+7.43 (scaled ≈ +22.8 at 2,896 words), replicated from FlareZ123 `im-results/lp2-original-wordlength-grammar-mi.md`.
The spaces are measured not to be plaintext-ordered words; characterising them is a bounded follow-up.

**Q3 — bounded?** Yes, finite: 2,896 lengths, 12,956 runes, ~25+4+2 registered statistics. Enumerable.

**Q4 — three conditionals.** (1) "Space" = the registered statistic battery and scopes (no key sweep);
(2) transition/spacing models represented: within-scope permutation, i.i.d. generators (English multiset, geometric,
Poisson, uniform), fixed-period keyed generator, content-keyed boundary rewiring, filter-adjacency break;
(3) register: English GP over 8 corpora + the solved Cicada printed lengths; MI is model-free, LLR is English-trained.

**Q5 — kill at 10%.** If the parser does not reproduce ~2,896 LP2 words or LP1 words fail to align with the
plaintext reference (< 90% length agreement under the best rule), stop and fix the input before any test. If A_global
fails on the solved Cicada reference, the order arm is declared uninformative and the lane continues with Q2–Q4 only.

## Addenda
(none yet)

### Addendum 1 — 2026-11-23 (before the full Q1 run; thresholds unchanged)
- Calibration (`calib.py` → `calib.json`): LP2 parses to 2,896 words / 55 pages / 8 sections / 17 paragraphs /
  173 sentences / 592 lines; solved reference = 694 LP1 + 45 AN END/PARABLE = **739 printed words** (Fable52 used
  875 words that included editorial insertions from the reference text — the printed count is used here).
  Rule R-A matches 739/739 printed LP1 lengths (R-B 95.4%, R-C 76.6%) → **R-A chosen**. Kill check PASS.
- `book_of_the_law` second half (2,893 words) is shorter than a 2,896-word window: it stays in the LLR training set
  but supplies no Q1 plants (7 corpora × 3 windows = 21 plants per type).
- A pipeline smoke run (80 real draws, 20-draw plant nulls) was executed to debug the code and its output was seen.
  No threshold, statistic or scope was changed after it; the full run below is the run of record.

### Addendum 2 — 2026-11-23 (after q1/q2 results were seen; no registered threshold changed)
- **M1's size control failed**: the word-exchangeable permutation null rejects 13/30 (0.43) same-corpus English
  pairs at α = 2.5e-3 (English word lengths are not exchangeable across windows of one text). M1 is therefore
  reported **uninformative** per §2, whatever its p.
- `q2b_posthoc.py` was written **after** seeing q2_results.json. It is descriptive only and carries no verdict:
  per-class shares of LP2 vs 480 English windows, and an English-window comparator for LP2-vs-solved (the role
  M1 could not fill). Any cell-level finding from it is a candidate for a future pre-registered test, not a result.
