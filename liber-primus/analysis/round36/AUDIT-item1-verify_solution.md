# AUDIT item 1 (HIGH) + item 13: `verify_solution.py` made register-aware

Date 2026-10-30. Addresses `AUDIT-inhibitors.md` item 1 (the L7-A defect in the front-door oracle) and the deferred item 13.
CLI is unchanged (`--selftest`, `--keystream`, `--key-module`, `--plaintext`, `--pages`, `--json`, `--skip-anchor`; PASS / FAIL / NOT-ADJUDICABLE words kept).

## New decision logic
1. Each page (first <= 240 runes) is decoded with `beam_v3.panel_max` under `keyskip1`, `keyskip2` and `free` (sign -1, key offset 0 per page, beam_w 400); `free` is decoded on the first 120 runes only (its observed null exists at L=120 only) and is skipped for pages shorter than 120.
2. Each decode is adjudicated directly with `adjudicate.adjudicate` against panel-R36 (12 registers, sha `a0682f0c...`; printed warning and fall back to the Round 32 nine-register panel if absent; exit 3 "unavailable" if no panel at all). Score = panel `pmax`, argmax register named.
3. Bar = `bars_v3.bar_v3(N=1, L, relation, alpha=0.01, family="lp2")`: a single submitted key. The output states N=1, the 3-relation family-wise alpha (~0.03) and that `free` has no observed bar above L=120.
4. PASS iff, under one relation, >= 2 distinct pages clear that relation's bar. PASS prints "flagged-for-oracle: a human must read two independent pages before the ledger moves" and the HUMAN-ORACLE bundle skeleton (key sha, relation, offset, sign, panel sha, bar, full decoded rune ids + text and per-register z trace for each clearing page).
5. FAIL prints the three conditionals tested (relations / panel registers / key-as-given o=0 sign -1 N=1) and "NEGATIVE UNDER THESE REGISTERS/RELATIONS ONLY"; the old English -5.5 rigid/beam score is one extra line labelled LEGACY and is not in the verdict.

## Self-test (L=120, 2 pages per register, keyskip1 plant, held-out text from `testhalves12.npz`)
New oracle: EN_MODERN 17.9/20.6, LATIN 18.2/17.7, EN_NOVOWEL 15.9/16.8, GREEK 19.6/19.8 (pmax per page; bar 4.0) all PASS with the correct key; wrong keys score 0.1-2.1 and FAIL in all four. SELF-TEST PASS.

Old oracle logic (legacy decoders + -5.5 band, same plants, null n=20):

| register | legacy page scores | old verdict on the CORRECT key | new verdict |
|---|---|---|---|
| EN_MODERN | -4.47, -4.23 | PASS | PASS |
| LATIN | -5.13, -5.57 | **FAIL** (1 page) | PASS |
| EN_NOVOWEL | -7.00, -7.34 | **FAIL** | PASS |
| GREEK | -5.36, -5.46 | PASS (marginal, 0.04 above bar; the English quadgram happened to tolerate the transliteration) | PASS |

## Other changes
`tests/test_verify_solution.py` (selftest on four registers; random key -> FAIL with the conditionals and L7 text; ~3 s, skipped if panel-R36 artefacts are absent). `analysis/handoff/build_problem.py` acceptance criteria rewritten and `PROBLEM.json` regenerated (English band moved under `legacy_informational`); `check_consistency.py` reads it from there; `README.md` and `AGENTS.md` descriptions updated (`PICKUP-HERE.md` does not describe the oracle); CI selftest step tolerates exit 3.

## Limits (honest)
* Only keyskip1 plants are recovery-gated in the self-test; keyskip2/free decode but have no planted gate.
* A random key (seed 5, 6 pages) cleared one page under keyskip1 and one under keyskip2 (never 2 under one relation): per-page false-clear is non-negligible with 3 relations x many pages, which is why PASS needs 2 pages under one relation; use `--pages 55` for any real PASS.
* N=1 is only right for one key fixed in advance. Panel .npz files are gitignored, so a fresh CI clone gets "UNAVAILABLE" (exit 3), not a pass.
* Pages restart the key at offset 0 (as the old oracle did); a key that continues across pages must be submitted as a per-page-aligned stream.
