# Round 39 / C1 — Sense-similarity "meaning" — PREREG (dated 2026-10-31, written BEFORE any index build or decode)

Clause (signed, verbatim, round36/O4-clue-coverage/clues.json): "their meaning is the road". R38/C1 read "meaning" as a lexical
*address* (synset offset) and was negative. This lane reads it as sense *position* in the lexical-semantic structure. Frozen now.

## Resource
Princeton WordNet 3.1, files already in `../../round38/C1-semantic-road/lex_download/dict/` (not re-downloaded); sha256 of
archive and index.noun/verb/adj verified against `../../round38/C1-semantic-road/lexicon_manifest.json`; sha256 of data.noun/verb/adj
recorded in this lane's manifest at build time.

## Per-word values (LP1 codebook = the 726 tokens of E.W, same lemma rule as R38: raw, else ING/ES/ED/S-stripped (+e for ING/ED); POS order noun, verb, adj; first synset = first offset on the index line)
- (a) DEPTH: hypernym depth of the first synset = number of steps to the root following the FIRST hypernym pointer ('@' or '@i', first listed) in that synset's data line, repeatedly, until none (cycle guard). Uncovered word -> 0.
- (b) LEX: lexicographer-file number (the 2-digit lex_filenum field of the data line, 0-44) of the first synset. Uncovered -> 0.
- (c) depth-of-lexname-category: NOT RUN (WordNet ships no hierarchy over lexnames; not cheap). Listed as not_covered.
- Reductions: mod 29, mod 28. Variants: D-R29, D-R28, L-R29, L-R28. If max depth < 28, D-R28 == D-R29 identically; the duplicate is merged (reported once as D, N not inflated).
## Application (R38 modes, rho=1, cipher word k uses codebook word (s+k) mod 726; boundaries = cleartext cipher-word boundaries)
A1 per-word additive shift; A2 cumulative shift (s=0..28); A3 key-pointer advance in K0 (s=0..725 step 1, subject to the R38 budget rule: if full time > 55 min, step = ceil(full/55min)). sigma = +-1; pages 0,1,2; keyskip1 only (keyskip2 for A3 only if A3 decode time leaves it under the cap — decided on control timing; otherwise listed not_covered).
Decoders reuse R38 enciphers.py/sweep.py (separate encipher code vs decode path), panel-R36, beam_v3 panel_max.
## Planted controls (ALL before any search)
Per variant x mode: 2 plants (sigma +-1, random s), held-out 240-rune EN_MODERN window enciphered by the independent encipher code with page-0 word lengths; matching decoder recovers >= 0.90 AND pmax120 >= bar_v3(1e6,120), pmax240 >= bar_v3(1e6,240). Failed cell = INVALID (unmeasured, not negative), dropped and listed.
## Bars
bar_v3 (round34/I1-v3-null/bars_v3.py) and bar12 (round36/B1-orbit-12reg/null12.json) at actual N (per subfamily: shift, A3) and N=1e6; L=120 screen, L=240 gate. Crossing actual-N L=120 bar -> L=240 gate -> FLAGGED_FOR_ORACLE bundle (HUMAN-ORACLE.md). Near-miss = >= actual-N bar, < 1e6 bar. Rows 12-wide SWEEPROW; stock validate_store.
## Conditionals for RESULTS
(1) Flags verified by oracle bundle only. (2) A negative says only: this frozen WordNet depth/lexname definition, these modes, rho=1, pages 0-2 heads, are not the key. (3) Literal vs convenient itemised. No "solved/closed/exhausted".
