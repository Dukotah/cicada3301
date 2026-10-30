# Round 38 / C1 — The semantic road — PREREG (dated 2026-10-30, written BEFORE any download or decode)

Clause under test (signed, verbatim, round36/O4-clue-coverage/clues.json): "their meaning is the road".
Doctrine R4: a public dictionary is a *definition*, not a lore prior. Everything below is frozen before any decode.
Nothing here asserts the clause means this; it is the literal-semantic reading made computable.

## (a) Resource A — WordNet
- Primary: Princeton WordNet 3.1 `wn3.1.dict.tar.gz` (https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz), files `dict/index.noun`, `index.verb`, `index.adj`.
- Fallback (only if primary is unobtainable): NLTK data `wordnet.zip` (WordNet 3.0) from
  https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip, same three index files. The version actually used is named in `lexicon_manifest.json` with sha256 of archive and of each index file.
- Mapping A: word = LP1 codebook word (the 726 tokens of E.W, lower-cased, apostrophes already removed).
  Candidate lemmas in order: raw; then, by the first matching suffix among ING, ES, ED, S: the stripped form; and for ING/ED also stripped+"e".
  For each candidate in order, for POS in (noun, verb, adj) in that order: if the lemma is in that POS's index file, value A = the FIRST synset offset listed on that index line (integer of the 8-digit offset). Stop at the first hit. No hit → 0. Coverage (count/726 with 0) is reported.
## (b) Resource B — frequency rank
- Norvig `count_1w.txt` (Google Web Trillion Word Corpus counts), https://norvig.com/ngrams/count_1w.txt, first N=50000 lines (file order = descending count). Fallback: https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english.txt (N=10000). File + sha recorded.
- Mapping B: value B = 1-based line rank of the lower-cased LP1 word (raw form only, no lemmatising); absent → N+1.
## (c) Reduction to a direction d (per LP1 word)
R29 = value mod 29; R28 = value mod 28; D29 = (decimal digit sum of value) mod 29. Six value variants: A-R29, A-R28, A-D29, B-R29, B-R28, B-D29.
## (d) Application (C1-R37 U3 machinery, enciphers_u2_u3.py: u3_d / enc_u3 / key_u3a3 / u3_direct), rho=1 only (the d for cipher word k is the value of codebook word (s+k) mod 726; the word boundaries are the cleartext cipher-word boundaries of the page). Sign sigma = ±1.
- A1 per-word additive shift; A2 cumulative shift: start s = 0..28 (shift modes), pages 0,1,2, sigma ±1, beam-free direct decode, judged vs keyskip1 bar.
- A3 key-pointer advance in K0 (LP1 rune stream, as in R37): start s = 0..725 step 1, pages 0,1,2, sigma ±1 (decoder sign = sigma), relation keyskip1 only, beam_v3 panel_max, panel-R36.
- Budget rule (frozen): measure the per-decode time t of A3 on the CONTROL runs; if 6 variants × 726 × 2 × 3 decodes would exceed 55 min, the A3 start step becomes ceil(full_time / 55 min), starts 0, step, 2·step … (same for every variant). The step is recorded; the untested fraction is reported as not covered.
## (e) Planted control per variant (cell = variant × mode)
Encipher a held-out 240-rune EN_MODERN window (testhalves-r36) with the variant, random s and sigma, page-0 word lengths, (A3: keyskip1, random seed) using the independent encipher code; the matching decoder (separate code path, from the ciphertext) must reach recovery ≥ 0.90 AND pmax120 ≥ bar_v3(1e6,120), pmax240 ≥ bar_v3(1e6,240). ALL controls run before the search.
## (f) Bars
Per cell: bar_v3 (round34/I1-v3-null/bars_v3.py) and bar12 (round36/B1-orbit-12reg/null12.json) at the actual N (per subfamily) and N=1e6; L=120 screen, L=240 gate (L=min(240, page length)). Crossing the actual-N L=120 bar → L=240 gate; gate pass → FLAGGED_FOR_ORACLE bundle. Near-miss = ≥ actual-N bar but < N=1e6 bar. Rows: 12-wide SWEEPROW, stock validate_store.
## (g) Kill
A cell whose control fails is INVALID (unmeasured), not negative; it is dropped from the search and listed. No "solved/closed/exhausted" language.
## Conditionals the RESULTS must state
(1) If any flag: verify by oracle bundle only. (2) A negative says only: this frozen WordNet/frequency definition, these three modes, rho=1, pages 0–2 heads, are not the key. (3) What is literal (the clause, "meaning" as dictionary sense) vs convenient (first-synset, offset-mod, R37 modes, rho=1, K0 codebook) is itemised.
