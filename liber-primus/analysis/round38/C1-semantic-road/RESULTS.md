# Round 38 / C1 — The semantic road — RESULTS (2026-10-30)

## Frozen definition (PREREG.md, written before download/decode; no fallbacks used)
- A = Princeton WordNet 3.1 (`wn3.1.dict.tar.gz`, sha256 3f7d8be8...c22a; index.noun 799fad7c..., index.verb e65b2d67..., index.adj 7d2b4d40...; full hashes in `lexicon_manifest.json`). Value = first synset offset on the lemma's index line (noun, then verb, then adj; lemma = raw, else ING/ES/ED/S-stripped (+e for ING/ED)). Coverage: 468/726 LP1 codebook tokens nonzero; 258 tokens (function words: from, this, what, you, to ...) have no synset -> 0. 259 distinct words.
- B = Norvig `count_1w.txt` top 50,000 (sha256 51df159f...e690); value = 1-based rank, unknown -> 50001. Coverage 715/726.
- Reductions: mod 29, mod 28, digit-sum mod 29 (6 value variants). Index: `lp1_meaning_index.json`.
- Application (R37 U3 machinery, rho=1): A1 per-word shift, A2 cumulative shift (s=0..28), A3 key-pointer advance in the LP1 rune stream (s=0..725, step 1); sigma +-1; pages 0-2 heads; keyskip1 only.

## Controls (run before the search; `control.json`)
18/18 cells (6 variants x A1/A2/A3), 36/36 plants (2 each, sigma +-1, random s): recovery 0.996-1.0 at L=240, pmax120 ~16-21 vs bar_v3(1e6,120)=9.235, pmax240 ~21-31 vs 9.514. No variant INVALID. (A3 decode ~0.03 s, so the budget rule gave step 1; nothing thinned.)

## Search
N = 28,224 decodes (shift 2,088 direct; A3 26,136 beam_v3 panel_max, 12 registers, panel-R36). 12-wide SWEEPROW rows, `AD.validate_store` ok.
| group | N | best pmax120 (cell) | bar_v3 actual N | bar_v3 N=1e6 | bar12 actual / 1e6 |
|---|---|---|---|---|---|
| shift A1/A2 | 2088 | 4.62 (A-R29 A1) | 6.895 | 9.235 | 6.858 / 9.102 |
| A3 | 26136 | 5.296 (B-R29 A3, page 1, s=477, sigma -1, register LP1_REAL) | 7.853 | 9.235 | 7.777 / 9.102 |
Per-cell bests (all 18): 3.0-5.3, listed in `sweep_summary.json`. Crossers of the actual-N bar: 0. Gate runs: 0. Flagged-for-oracle: none. Near-misses (>= actual-N bar, < 1e6 bar): none.

## Three conditionals
1. Coverage: only this frozen WordNet-3.1-first-synset and Norvig-rank definition, three reductions, rho=1, the three R37 modes, pages 0-2 L=120 heads, keyskip1, English plaintext (panel-R36) were read; N=28,224 (more than the lane's 5-10k estimate because A3 is cheap; the step rule would only have thinned it if it were slow).
2. Power: planted controls recovered in every cell with margin (pmax ~2x the bar), so the instrument could see these constructions had they been the key.
3. Result: nothing within reach of any bar; the best (5.30) is below the actual-N bar 7.85. Bounded negative, definition-conditional; not a statement about "meaning" in general.

## Literal vs convenient
- Literal: the clause "their meaning is the road" (signed, verbatim); "meaning" = a dictionary sense in a public versioned lexicon; "road" = the sequence of LP1 words traversed in order (R37's map) with the interrupters as boundaries.
- Convenient (analyst choices): first synset (WordNet's sense-frequency order) rather than all senses; offset (an arbitrary file address, not semantic content) mod 29/28; the lemmatiser; the 726-word LP1 list as codebook and its K0 rune stream as the key source; direction = value read as a shift/pointer jump; rho=1; Norvig web-corpus rank as the second "meaning" proxy. Offsets in particular are an identifier, so variant A tests "which sense file position", not sense similarity; a semantic-similarity or sense-graph reading is a different, untested construction.

## not_covered
Senses other than first; other lexicons/frequency lists; offsets of hypernyms or sense counts; rho=2/3; keyskip2/free; shift starts beyond 0..28; pages beyond 2 and heads beyond L=120/240; non-English plaintext; any non-frozen definition of "meaning".

Files: PREREG.md, lexicon_manifest.json, lp1_meaning_index.json, build_index.py, enciphers.py, sweep.py, control.json, sweep_rows.jsonl, sweep_summary(_final).json, gate_hits.jsonl (empty), ledger.json, ledger_patches.json, make_docs.py; raw downloads in lex_download/ (data only).
