# Round 39 / C1 — Sense-similarity "meaning" — RESULTS (2026-10-31)

## Frozen definition (PREREG.md, dated before any index build/decode)
WordNet 3.1 (R38's files; archive + index hashes re-verified against the R38 manifest; data.* hashes in `lp1_sense_index.json`). Same lemma rule as R38. Per LP1 word (726 tokens, 259 distinct): D = hypernym depth of the first synset (steps along the first listed `@`/`@i` pointer to the root; 0 if uncovered; observed max 13); L = lexicographer-file number (0-44) of the first synset (34 distinct values used). Reductions mod 29 / mod 28. D-R28 is identically D-R29 (max depth 13 < 28) so it is merged: variants D, L-R29, L-R28. Modes A1 per-word shift, A2 cumulative, A3 key-pointer advance in K0 (rho=1); sigma +-1; pages 0-2; keyskip1. Third variant (lexname-category depth) not run: WordNet has no hierarchy over lexnames.
**LP1 coverage: 468/726 tokens have a synset (258 function-word tokens = 0), identical to R38.**

## Controls (before the search; `control.json`)
9/9 variant-mode cells valid, 18/18 plants recovered (recovery >= 0.90, pmax120 >= bar_v3(1e6,120)=9.235, pmax240 >= 9.514). No variant INVALID. A3 decode 0.051 s, so no thinning (step 1).

## Search
N = 14,112 decodes (shift 1,044 direct; A3 13,068 beam_v3 panel_max), 12-wide rows, `validate_store` ok.
| group | N | best pmax120 (cell) | bar_v3 actual N | bar_v3 N=1e6 | bar12 actual / 1e6 |
|---|---|---|---|---|---|
| shift A1/A2 | 1044 | 4.004 (L-R28 A2, p1, s=18, sigma -1, OE) | 6.632 | 9.235 | 6.606 / 9.102 |
| A3 | 13068 | 5.351 (D-R29 A3, p1, s=574, sigma +1, LATIN) | 7.590 | 9.235 | 7.525 / 9.102 |
Per-cell bests (all 9) in `sweep_summary_final.json`. Crossers of actual-N bar: 0. Gate runs: 0. **Flagged-for-oracle: none. Near-misses: none.**

## Conditionals
1. Coverage: only this frozen WordNet depth/lexname definition, these three modes, rho=1, pages 0-2 heads, keyskip1, English panel-R36.
2. Power: controls recovered with ~2x margin, so the instrument could see these constructions had they been the key.
3. Result: bounded, definition-conditional negative; the best (5.35) is far below the actual-N bar (7.59). Not a statement about "meaning" in general.

## Literal vs convenient
- Literal: clause "their meaning is the road"; meaning as position in a public, versioned lexical-semantic hierarchy (hypernym depth, semantic-class file); road = LP1 word sequence.
- Convenient: first synset only; first hypernym path; depth and lexname as the only two sense features (not a pairwise similarity metric); mod 29/28; R38 modes; rho=1; K0 codebook as key source; 258 uncovered tokens forced to 0.

## not_covered
Other senses/hypernym paths; lexname-category depth; pairwise similarity (path/Lin/embedding) readings; rho=2/3; keyskip2/free (A3 was cheap enough that keyskip2 is feasible but needs its own controls, not done); shift starts beyond 0..28; pages >2; non-English plaintext.

Files: PREREG.md, build_index.py, lp1_sense_index.json, enciphers.py, sweep.py, control.json/.log, sweep_rows.jsonl, sweep_summary(_final).json, gate_hits.jsonl (empty), keep_rows.json, ledger.json, ledger_patches.json, make_docs.py (all in analysis/round39/C1-sense-similarity/).
