# R45-W1 — What are the printed spaces? RESULTS

_2026-11-23. Pre-registration: `PREREG.md` (plus Addenda 1 and 2). Machine record: `results.json` (it merges
`q1_results.json`, `q2_results.json`, `q2b_posthoc.json`, `q3q4_results.json` and `calib.json`). Pure stdlib.
Reproduce from this folder: `python calib.py && python q1_scope.py 10000 150 3 && python q2_multiset.py 10000 1000 &&
python q2b_posthoc.py && python q3q4_leak_order.py 10000 300 && python assemble.py`. Q1 uses 8 processes, about 7 min._

## 0. Inputs and calibration

- The LP2 parse (`data/krisyotam_runes.txt`, rune-identical to the canonical dataset) gives 2,896 words, 55 pages,
  8 `$`-sections, 17 paragraphs, 173 sentences and 592 lines. Rules: `- . & $ §` and numerals break words; line
  breaks and page breaks (`/`, `%`) do not.
- **Solved reference = 739 printed words**: 694 LP1 words (from `data/sources/rtkd_master.txt`) plus 45 words from
  AN END and PARABLE. Fable52's 875-word reference came from the reference *text*, which includes editorial
  insertions. The printed lengths are the correct object.
- GP transliteration rule R-A (greedy ING/TH/EO/NG/OE/AE/IA/IO/EA) matches **739/739** printed solved lengths.
  R-B matches 95.4% and R-C 76.6%. English corpora use R-A.

## Q1 — Is there any scale at which LP2's lengths look ordered? **No. But which scope was shuffled can't be determined.**

Per-test α = 4.0e-4 (25 tests, family 0.01). Real nulls have 10,000 draws. Plants are 21 English windows of 2,896
words per type (7 corpora × 3, taken from corpus halves the LLR model never trained on), each with a 150-draw null.

| test family | LP2 result | power on intact English | can it tell scopes apart? |
|---|---|---|---|
| A_U order inside scope U (LLR + MI; U = global, sentence, line, paragraph, page, section) | all 12 null. z from −1.8 to +0.24, every p ≥ 0.38 | **1.00 for all 12** | size 0.00 on globally shuffled plants |
| B_U composition at U (G, SS) | all 10 null (p ≥ 0.12) | — | **uninformative.** Power on its own within-U plant is ≤ 0.52 (best is B_sect_G at 0.43 on section-shuffled plants) |
| C local ordered patch scan (max over windows of 25–400 words) | null, z_max = 3.03 vs empirical bar 4.56, p = 0.30 | 0.91 on a whole intact stream | patch power: w ≤ 100 → 0.00, w = 200 → 0.15, w = 400 → 0.23 |
| D per-unit max z | page: null, **uninformative** (single-page plant power 0.00). Section: null, p = 0.29 (single-section plant power 0.65) | — | — |

- **Solved Cicada reference** (739 printed words): A_global_LLR z = +3.79 (bar 3.35), MI z = +2.78. At the same
  per-word effect, 2,896 words would give z ≈ +7.5 (√n scaling). LP2 gives **z = −1.18**. The A statistic sees the
  author's own register. That makes A_global informative and the LP2 null a real one.
- **What A excludes:** plaintext-ordered lengths at any scope down to the line (about 5 words). Within-scope tests
  (null = shuffle inside each sentence, line, page or section) find no order *inside* those units either.
- **What nothing here can exclude:** English lengths shuffled within sentences, paragraphs, pages or sections all
  look exactly like a global shuffle. Every statistic has power ≤ 0.05 against them, except a line-scope shuffle,
  which A_global_LLR catches 0.48 of the time and which LP2 does not show. Composition heterogeneity in English is
  too weak to locate the scope (the Fable52 T8 failure, now measured rather than assumed). **The scope of the
  scrambling cannot be identified from word lengths alone.** The statement this work supports is "no order at any
  tested scale". It does not support "globally shuffled".
- Ordered patches shorter than about 400 words would not have been seen (power ≤ 0.23). Neither would a single
  ordered page (power 0.00).

## Q2 — Multiset

| test | result | control / power | verdict |
|---|---|---|---|
| M1 LP2 vs solved Cicada (permutation G) | G = 40.9, p ≤ 1e-4 | **size control failed:** 0.43 of same-corpus English pairs rejected | **uninformative** |
| M2 LP2 vs English (min G over 8 corpora, leave-own-corpus-out window null) | min G = 122 (nearest: *Pride*). English windows: median 57, q99 187, max 246. **p = 0.060** | merges of 5% and 10% undetectable (0.00); 20% merges 0.68 | null: inside the English spread |
| M3 geometric (random independent space insertion) | G = 1,502, p ≤ 5e-4 (bootstrap floor) | power vs English windows 1.00 | **rejected** |
| M4 fixed-period / keyed length generator, P = 2..300 | max z = 2.76 at P = 187, p = 0.67 | power ≥ 0.8 at keyed fraction f ≥ 0.2 (P = 13, 29, 97); f = 0.1 gives 0.40 / 0.05 / 0.00 | null |

- Log-likelihood of the LP2 lengths: solved-Cicada distribution −6,237 (0 parameters), pooled English −6,246
  (0 parameters), shifted Poisson −6,374, geometric −6,884, uniform −7,643. **The lengths are English-shaped, not
  random spacing.** The parameter-free solved-Cicada shape fits best of all.
- Means: LP2 4.47, solved 4.03, English corpora 3.66 to 4.15. LP2 sits at the top of the English range.
- **POST-HOC (Addendum 2, descriptive, no verdict):** 2-rune words are **15.5%** of LP2. That is below all 480
  English windows (minimum 19.7%) and below the solved pages (24.1%), about 250 words short. Every other length
  class falls inside the English window range, though 7 and 8 runes are near the top (1–2% of windows as extreme).
  Against the solved-Cicada distribution, LP2's G (193) exceeds 87% of English windows; it is not an outlier
  overall. In GP, "THE" is 2 runes (TH·E), so a shortfall in 2-rune words fits a plaintext with fewer articles or
  short function words — or lengths taken from somewhere other than the plaintext. This is **one post-hoc cell
  among 9**. Treat it as a lead for a pre-registered test, not as a finding.

## Q3 — Leakage

Per-test α = 5e-3. Null = circular shift of the whole boundary pattern against the rune stream (10,000 draws).

- **L1, rune distribution by word position (start / interior / end / single):** G = 79.3 vs null 87.1 ± 13.4,
  z = −0.58, p = 0.71. **Null.** Plants:
  - Content-keyed boundary rewiring (boundaries pulled onto runes from a keyed 4-set): q = 0.05 → 0.03,
    **q = 0.10 → 0.93**, q ≥ 0.20 → 1.00.
  - English with true spaces under an 8-letter Vigenère key → 1.00 (median z 86). Under an English running key → 1.00.
  - **English with true spaces under a uniform OTP plus the doublet filter → 0.00.** This test cannot see true
    spacing under an OTP-class key, by construction.
  - The solved LP1 ciphertext itself: z = +29.4.
- **L2, doublets across printed word boundaries vs within words:** 23/2,895 (0.79%) vs 63/10,060 (0.63%),
  two-sided p = 0.36. **Null.** Plant power: q = 0.10 → 0.55, **q = 0.20 → 0.93**, q = 0.30 → 0.98.
- Reading: the spacing is **not** keyed on the cipher runes at a rate of 10% of boundaries or more. Whether it is
  the true spacing cannot be tested this way if the key is OTP-class. If the key were Vigenère-like or an English
  running key, true spacing would have leaked overwhelmingly (z ≈ 20–86). LP2 shows nothing, which fits the
  OTP-class key the ledger already holds.

## Q4 — Rune order

- **R1:** printed lag-1 equalities number 86 against 447 expected. Lags 2–10 are all normal (438–479). The doublet
  filter therefore ran on the runes **in printed order, at lag 1**.
- At printed word boundaries, the estimated fraction of adjacencies that were **not** adjacent when the filter ran
  is **q̂ = 0.06, with a 95% upper bound of 0.20**. Line breaks: q̂ = 0.02, upper bound 0.39. Page breaks: 0/54
  doublets, no power (upper bound 1.0).
- So at least ~80% of printed word boundaries sit inside a run of runes the filter saw contiguously. The spaces did
  not cut the cipher stream into reorderable pieces. Word-level transposition of cipher words, words reversed in
  place, and reading-order tricks at word boundaries are excluded down to about q = 0.2.
- **R2 (honest):** with a uniform key and the rejection filter, the ciphertext's distribution does not depend on
  plaintext order. The numeric demo confirms it: ordered and word-shuffled English give identical cipher lag
  statistics (IoC·29 1.0001 vs 1.0006; lag-1 0 vs 0; lags 2–5 within noise). **No key-independent rune-level test
  of plaintext order exists on the ciphertext alone.** The only order R1 establishes is the order of the cipher and
  filter stream, and that order is intact.

## Implications for attack strategy (plain)

1. **Drop word-boundary and word-length-sequence cribs.** That covers C-01 SKELETON, word-sum keys, quote-span
   cribs keyed to printed word positions, and the HUMAN-ORACLE rule of reading by printed words, as evidence about
   plaintext *order*. Two caveats limit this:
   - A within-sentence (or page, or section) shuffle is **not excluded**, so a crib of the form "this sentence's
     words have this length *multiset*" stays possible.
   - Under the OTP-class key, nothing here tells us whether the lengths belong to the plaintext at all.
2. **The lengths are not random spacing** (geometric rejected outright). They are not a periodic or keyed length
   generator (no period up to 300 at keyed fraction ≥ 0.2). They are not keyed on the cipher runes (≥ 10% rewiring
   would show). The multiset is English-shaped; the 2-rune deficit is post-hoc. The best-supported description:
   **an English-like length multiset laid over an unbroken cipher stream, with its order destroyed**. One example is
   the true plaintext lengths permuted at some unknown scope. Another is lengths borrowed from a different text.
3. **As a message, the spaces show no structure these tools can find:** no order, no period, no rune dependence.
   Reading the length stream as numbers or symbols was **not** tested. It is a finite 2,896-symbol object, so it is
   cheap to hand to the standing panel if anyone wants to.
4. **Rune order at lag 1 is the generation order**, continuous across word and line breaks. Decoders should treat
   the rune stream as contiguous and ignore printed spaces. Any instrument whose plants keep real word boundaries
   should be re-planted without them (that is lane I1's job).
5. **Possible follow-up to pre-register:** the 2-rune-word deficit (a THE-frequency / function-word test), and a
   line-scope shuffle test with higher power.

## Conditionals (doctrine Q4)

1. **Space covered:** the registered battery only — 25 + 4 + 2 tests plus the R1 estimates. There was no key sweep.
2. **Spacing models represented:**
   - within-scope permutation (scopes: sentence, line, paragraph, page, section, global)
   - i.i.d. length generators (English multiset, geometric, Poisson, uniform)
   - a fixed-period keyed generator (P ≤ 300)
   - content-keyed boundary rewiring (keyed 4-set, ±3 runes)
   - filter-adjacency breaks at boundaries

   Not represented: keyed permutations with no composition signature, generators driven by the plaintext but not
   by the cipher, length-as-number channels.
3. **Register:** English GP over 8 corpora plus the solved Cicada printed lengths. MI is model-free; the LLR is
   trained on English. Under an OTP-class key, Q3/L1 has zero power against true spacing, whatever the register.

## Closing stamp
R45-W1 closed 2026-11-23. All registered tests run with full nulls. Verdicts:
- **Q1:** no order at any scale (power 1.00); scope uninformative.
- **Q2:** geometric rejected; English-consistent (p = 0.06); M1 uninformative; no period.
- **Q3:** no leakage (power 0.93 at 10% keyed rewiring; blind under OTP).
- **Q4:** filter order intact across word breaks (q ≤ 0.20).

Rows: `ledger_rows.json` (R45-W1-*). No files outside `analysis/round45/W1-spaces/` were written. Nothing committed.
