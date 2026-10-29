# Round 33 / B1 -- feed `payload_resolved.bin` to the four rows that never saw it -- PREREG

_Written 2026-10-29, before any script in this folder was run. Binding: `ARMADA-DOCTRINE.md`. Owner chose Option A (promote)._

## Inputs
* canon  = `analysis/pp49_51/canon_256.bin`; resolved = `analysis/round19/C1/payload_resolved.bin` (== round18/L5). Differ at idx 45 (81->107), 50 (21->47), 246 (224->198).
* `canon_256_decpref.bin` is a different object (a decimal-prefix variant; differs from canon at 6 other idx, and carries the same 3 uncorrected bytes). Corrected decpref := decpref with idx 45/50/246 patched to the resolved values (ASSUMPTION, stated; the 3-byte correction is applied, nothing else).

## Aiming test, per row
Q1 recognizer = the lane's own, unchanged. Q2 prior: three bytes, instrument-vouched; low probability of flipping anything. Q3 subset (enumerated, stated before running):
* **B-04**: payload-derived seeds in `round13/B04/seeds.py` s.7 = 7 (`canon256_raw, _rev, _head32, _tail32, _hex(lower), _hex(UPPER), _decpref`) of 2,165. head32 (idx 0..31) does not contain a corrected index so it is byte-identical; 6 of 7 change. Re-run stages A (offset 0, head L120), B (offsets x10, head L120), C (55 page heads, L100) for the 7 seeds with the original harness engine (`harness._init/_work` logic, `sk.beam_decode` beam 400, max_skip 3, 16 gens x 5 reds x sign x atbash x dir), in-process. Canon comparator re-run for the 6 changed seeds at stages A and B (stage C comparator = published `results_C.json`).
* **R17** (`round17/P3_tables`, pad `canon_256`): the one pad. Q5 check first: original dense-scan prefilter needs `trigram_idx.npy` built from `data/{kjv,moby,pride,war}.txt`; moby/pride/war are absent (gitignored) => original harness NOT re-runnable. Per Q5 the row's `not_covered` is filed as "corrected payload: harness not re-runnable". A SUPPLEMENTARY exhaustive-offset beam over the corrected pad (every valid offset, no prefilter; a superset of the prefilter's survivors) is reported as informational only, not as the original harness.
* **E-01 / E-02**: the tests themselves (`zerofp_tests.e01_rsa_pkcs1`, `e02_meta_parameters`, unmodified code, input file substituted via `load_bytes`). E-02A is single-byte sensitive (permutation window).

## Controls (run FIRST, per row)
* B-04: plant (a) `THE PRIMES ARE SACRED` sha256_ctr/mod29 (the lane's G2 plant) and (b) a payload-derived seed (resolved tail32, sha256_ctr/mod29) at L120 under keyskip supp 0.83; run the same engine over the 7 payload seeds + the planted seed; planted config must rank #1 and clear -5.5. If it fails, the row is INCONCLUSIVE.
* E-01/E-02: `tests/validate.py` and a synthesised positive for each recogniser (E-01: PKCS#1 v1.5 type-1 blocks accepted by `pkcs1_v15_check`; E-02A: a planted 56-permutation window must be found).
* Original-input reproduction: canon runs must reproduce the published lane outputs (E-01 NULL/8 pow checks; E-02 NULL, 201 windows; B-04 A/B/C best from `results_*.json`).

## Bars (stated before the run)
* B-04 legacy recognizer: `score_norm >= -5.5` (lane PREREG s5); L-aware `benchmark/null.threshold_for(N_stage, segment_len=L)`. Adjudicator: every decode is also scored by the round32 I2 nine-register panel (`pmax`) and persisted as a SWEEPROW; hitfn20 panelmax bar 7.3835 (pair) / 7.6342 (exact) [N=1e6 declared, from round32/B1]. A decode is **flagged-for-oracle** if score >= the L-aware bar OR pmax >= the hitfn20 bar. Flagged is never "certified".
* Keyskip relations: the original engine is keyskip1 (`sk.beam_decode`). For the resolved seeds at stage A, driftbeam `pair` (keyskip2, beam 64) is added; `exact` (keyskip1) is the original engine's relation.
* E-01 HIT = PKCS#1 type-1 padding + DigestInfo; E-02A HIT = a 56 (or 57) byte permutation window; E-02B bar |r|>0.5 and p<1e-6.
* changed-vs-canon = any difference in best score/pmax, the set of flagged configs, or test verdict.

## Compute
One Python process, nproc=1, ~20 min cap, rows streamed. No git, no writes outside this directory. No "solved/closed/exhausted".
