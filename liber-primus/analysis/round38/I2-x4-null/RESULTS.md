# Round 38 / I2 - X4 bespoke null and re-judgement: RESULTS
Dated 2026-10-31 (PREREG.md written first, 2026-10-30). Measurement lane. No discovery claim; nothing here is "solved/closed/exhausted". Conditional on: X4 key space as C3 regenerated (12 configs, offset 0, 6 page-start windows) x keyskip1/2 x panel-R36 (12 registers).

## Deviations (declared)
- **L=240 null has 121 draws, not 2,000.** A L=240 draw (about 120 beam decodes) costs ~8 s on this loaded laptop; 2,000 would take ~4.5 h, and the session stalled once overnight. The L=240 bar is therefore rough (empirical q99 of 121 maxima; Gumbel cross-check). **L=120 has the full 2,000 draws.**
- The two configs whose decode is a stream-independent constant (prime_index/none/sign-1, prime_index/atbash_pre/sign+1; plain = -1 identically, mds=1, IoC*N=29) were decoded for the first 20 draws (degenerate in all), then counted as degenerate without re-decoding (declared in PREREG). Null family N = 60 non-degenerate rows/rel/L, same as the real family (72 rows - 12 degenerate).
- Control construction: the family's key is a function of the ciphertext letter, so the plain is a fixed letter-map g(C); see below.

## Planted control (control.json, run FIRST) - PASS
Ciphertext chosen as C = g^-1(P) so the key derived from the planted ciphertext's own letters deciphers it exactly (asserted); family decoder (beam_v3 panel_max, keyskip1/2, family sign) on held-out EN_MODERN/LATIN/GREEK text, 2 plants x 3 registers x 2 relations x L in {120, 240}.
- Gate (the 2 bijective configs, prime_index/none/sign+1 and prime_index/atbash/sign-1): **24/24 recovered >= 0.90 at L=120 and 24/24 at L=240; min recovery 1.0.**
- Supplementary (8 image-limited configs, plaintext projected onto the 20-21-letter image alphabet): recovery >= 0.90 in 21-24 of 24 cells each. Not gating; documented distortion.
- Structural finding: prime-value and totient configs have |image| = 20-21 of 29, so they cannot carry an arbitrary plaintext (only plaintexts over the image alphabet); the other two prime_index configs are constant maps. Only 2 of 12 X4 configs are a general-purpose cipher.

## Null table (null_x4.json; doublet-matched shuffles, key re-derived from each shuffled stream)
Family max of pmax over 60 non-degenerate rows per relation.

| L | draws | rel | family-max mean (sd) | **bespoke bar q99** (Gumbel q99) | null max | transferred actual-N (C3 N=84) | transferred declared 1e6 |
|---|---|---|---|---|---|---|---|
| 120 | 2000 | keyskip1 | 5.395 (0.58) | **6.994** (7.212) | 7.803 | 5.690 | 9.102 |
| 120 | 2000 | keyskip2 | 5.406 (0.58) | **6.994** (7.233) | 7.803 | 5.645 | 8.999 |
| 240 | 121 (partial) | keyskip1 | 6.646 (0.59) | **7.919** (8.480) | 8.699 | 6.036 | 8.978 |
| 240 | 121 (partial) | keyskip2 | 6.663 (0.59) | **7.931** (8.507) | 8.699 | 6.145 | 9.282 |

**The transferred actual-N bars undercut the true X4 null by ~1.3 (L=120) and ~1.9 (L=240).** Data-dependent keys follow the stream, so X4 shuffles produce family maxima near 5.4 / 6.65 on average, around or above the transferred bar. The transferred bar was too LOW, so C3 could only over-call, never under-call; every C3 negative stands. The transferred declared-N (1e6) bars (~9) are above the bespoke bars (conservative).

## Re-judged real X4 rows (rejudged.json; 72 rows/rel/L)
| L | non-degenerate rows | best non-degenerate (cfg, window) | pmax | bespoke bar | family-wise p | clears |
|---|---|---|---|---|---|---|
| 120 | 120 (60/rel) | v_prime/none/sign+1, w7307 (ks1 and ks2) | **4.779** | 6.994 | 0.871 | none |
| 240 | 120 | v_prime/atbash_pre/sign-1, w12114 (ks1/ks2) | **5.455** | 7.919 / 7.931 | 0.984 | none |

Per-config best non-degenerate pmax, L=120 / L=240: prime/none/-1 3.40/3.98; prime/none/+1 4.78/5.19; prime/atbash/-1 4.77/5.46; prime/atbash/+1 3.53/4.23; pindex/none/+1 3.22/3.80; pindex/atbash/-1 2.98/4.06; totient/none/-1 3.56/4.84; totient/none/+1 3.02/3.89; totient/atbash/-1 3.18/3.73; totient/atbash/+1 3.58/4.44. **0 of 120 non-degenerate rows clear at either L. Negative, conditional as above.** The best real L=240 row sits at the 98th percentile of a null whose mean is 6.65, so the partial L=240 null is not what limits this verdict.

## Degenerate-filter audit (filter_audit.json; 48 real rows removed, 24 per L)
Filter (C3): mds <= 6 or IoC*N >= 4.24. Every removed row is from the two constant configs (all 6 windows x 2 relations); the decode is identical across windows.
| L | config | raw pmax | mds | IoC*N | argmax reg | vs bespoke bar |
|---|---|---|---|---|---|---|
| 120 | prime_index/none/sign-1 | 6.886 (6.890 one row) | 1 | 29.0 | GREEK | below q99 6.994 |
| 120 | prime_index/atbash_pre/sign+1 | 8.702 | 1 | 29.0 | OE | numerically above |
| 240 | prime_index/none/sign-1 | 9.749-9.886 | 1 | 28-29 | GREEK | numerically above 7.92 |
| 240 | prime_index/atbash_pre/sign+1 | 12.404 | 1 | 29.0 | OE | numerically above |

No non-degenerate row was removed. The removed rows are one repeated constant stream (plain = -1 for every symbol) that the panel LM scores high. Where it numerically exceeds the bespoke bar this is a **RECOGNIZER FAILURE, not a hit**: IoC*N = 29 (real language <= 3.24), 1 distinct symbol (real >= 7 per 32). Not sent to L=240/oracle. The filter should be standing.

## Verdict
Control passes; the bespoke X4 bar is higher than the transferred actual-N bar (6.99 vs 5.64-5.69 at L=120; 7.92-7.93 vs 6.04-6.15 at L=240); re-judged, 0 of 120 non-degenerate X4 rows clear at either L (best 4.78 and 5.455); the filter removes only a constant decode. R22-C X4 stays negative with the transferred-bar caveat resolved at L=120 and partially at L=240. Conditionals unchanged (offset 0; 6 windows; keyskip only).

## Coordinator decisions
1. Accept `ledger_patches.json` (resolves C3 coordinator decision 3).
2. Extend the L=240 null to 2,000 draws (~4.5 h laptop or a sandbox window)? Not needed for the verdict.
3. Make the degenerate guard (mds <= 6 or IoC*N >= 4.24) a standing flag in the adjudicator output: a constant stream beats every bar.

## Files
PREREG.md, common.py, control.py, null_x4.py, analyze.py, control.json, null_rows_L120.jsonl (2000 draws), null_rows_L240.jsonl (121), null_x4.json, rejudged.json, filter_audit.json, ledger.json, ledger_patches.json.
