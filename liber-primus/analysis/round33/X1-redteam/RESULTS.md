# Round 33 / X1 -- red-team (R6) -- RESULTS

_2026-10-29. Refute-by-default. Each target is FOUND-ERROR or NO-ERROR-FOUND with citations; a NO-ERROR-FOUND states what was checked. No git run. Paths relative to `liber-primus/`. Compiler check: `gcc`, `cl` both absent on this machine (so the C patch stays unbuilt)._

## 0. FOUND-ERROR summary

| # | Target | Sub-verdict | One line |
|---|---|---|---|
| 1 | R32 B2 PHP mt_rand | NO-ERROR-FOUND on numerics; FOUND-ERROR (minor) on row/wording | counts, 48/48 and 0.970 % arithmetic reproduce; control is conditional on prefilter (48/64 = 0.75 end-to-end); seeds drawn with replacement (unique 0.9658 %); ledger `source_register` said round32/B1; PHP-5 reference unverifiable here |
| 2 | I4 D5c replication | replicates at L=240, FAILS at L=120 | third key `CICADA-X1R33`: catch 237/244 = 0.971, pooled FR 0/64; L=120: NOVOWEL FR 53/53. SEAL_PASS stays false |
| 3 | Uncompiled C patch | **FOUND-ERROR (real)** | `grind27.c:824-825` and `grind28.c:1114-1115` had a raw newline inside a string literal (compile error). Fixed in both. Still unbuilt |
| 4 | `not_covered` hygiene | FOUND-ERROR (hygiene) fixed | 9 drafts confirmed (F-01, H-03, E-02 reworded), 5 R30 rows filled, validator warning added |
| 5a | I1 | NO-ERROR-FOUND on numerics; FOUND-ERROR (minor) on provenance/null | table matches JSON (54/54, 0 mismatches), re-runs bit-identical; PREREG pre-run text unverifiable; null not register-matched |
| 5b | I2 | **FOUND-ERROR** vs R18-L7 | 0.84 % doublet figure does not replicate (0.595 % full length); table NO-ERROR-FOUND |
| 5c | B1 | FOUND-ERROR (minor) | E-01 "nearly vacuous" absent from patch; four-row list missed readers (R16-KDF, R30-B1/B2, capsule MANIFEST, ...) |
| 5d | B2 | NO-ERROR-FOUND (2 minor) | 2-char diff verified by manifest hash; p27:93 and LP1 diagnosis reproduce; data edit predates PREREG |
| 5e | O1 | NO-ERROR-FOUND (minor) | PREREG-only; "9 measured" miscount |
| 5f | B3 | not yet available at audit time | `B3-v3-readjudication/` has PREREG, control, null, partial rows but no `RESULTS.md`; coordinator to check |
| 6 | Ledger patches | applied | LEDGER.json 181 -> 187 entries, validator 0 errors |

## 1. Round 32 B2 (PHP mt_rand)

* `control.json`: 8 plants x 8 cells = 64 e2e plants; **48 pass the prefilter, 48 of 48 recover** (per-cell 4/4, 8/8, 6/6, 4/4, 7/7, 6/6, 6/6, 7/7 match RESULTS s2 `RESULTS.md:12-24`). 16/64 plants were dropped by the prefilter, so end-to-end recall is 0.75; "48/48" is true but conditional (prefilter power 0.436-0.756 over 32 cells, `control.json`). `all_pass: true` only means conditional recovery.
* `sweep_summary.json`: `tier_a_core 487`, `tier_a_dense 47549`, `decodes 212218`, `stage_b 529`, `flagged []`, `gate3_crossers []`, `coverage_fraction_of_2p32_tier_b 0.00970458984375` = 41,680,896 / 2^32. Reproduced. Seeds are drawn **with replacement** (`RESULTS.md:33`), so expected unique coverage is 1-(1-2^-32)^41,680,896 = **0.9658 %** (0.970 % is draws). Immaterial but the row now says so.
* Legacy twist: `php_mt.py` selftest passes, including `legacy_seed1_first = 1244335972`, but that "remembered" constant (`php_mt.py` selftest key name) is not independent of the author. X1 wrote `php5_independent.py` from the PHP 5 source structure (pointer-form `php_mt_reload`, `twist(m,u,v) = m ^ (mixBits(u,v)>>1) ^ (-(loBit(u)) & 0x9908b0df)`, tempering, `>>1`): seed-1 first draw **1244335972**, identical to `php_mt.stream31` for seeds {1, 777, 3301, 1325734783, 4294967295, 0} x 1500 draws. That value equals the widely published PHP 5.x `mt_srand(1); mt_rand()` output, but that equality rests on recalled documentation: **no PHP binary here (`which php` empty) and no fetch performed -> the PHP-5 reference value is recorded as unverifiable on this machine.** (PHP >= 7.1 canonical value is 895547922 = 1791095845 >> 1, matched by the selftest.)
* Ledger row `R32-B2-PHP-MT-RAND` (already filed by the R32 coordinator): `source_register` said `round32/B1` (fixed), `control_detail` and `coverage` annotated, `not_covered` last item updated.

## 2. D5c replication (`d5c_replicate.py`, `d5c_analyze.py`, `d5c_replication.json`, `feat_x1_*_{240,120}.json`)

I4's own `extract.py` recipe (POPS patched; outputs only here), key `CICADA-X1R33` (third clean key, new seeds), frozen `m_NV = 14.0128`, bar 7.6342. (`catch_surface_d5c.json` is not on disk in the I4 dir; the constant is taken from RESULTS.)

| L | draws NV/EN/spread | halluc caught | catch (Wilson) | FR EN_MODERN | FR NOVOWEL genuine | FR spread | FR pooled register-spread |
|---|---|---|---|---|---|---|---|
| 240 | 300/30/48 | 237/244 | **0.971** (0.942-0.986) | 0/30 | 0/16 (upper 0.194) | 0/48 | 0/64 (upper 0.057) |
| 120 | 300/30/48 | 162/163 | 0.994 (0.966-0.999) | 0/30 | **53/53** | 0/47 | 53/100 (0.433-0.625) |

L=240 replicates I4's virgin-2 (0.964, 0/113-ish); 7 hallucinations reach margin up to 15.72 > 14.01 (the margin overlap I4 reported). L=120 confirms the stated length-conditioning: every correct-key NOVOWEL decode (margins 6.8-10.7) is rejected by the L=240 constant. SEAL_PASS remains false; D5c is a conditional candidate at L=240 only.

## 3. The C patch (`round27/P1-engine/grind27.c`, `round28/L4/grind28.c`)

* **FOUND-ERROR (real):** `grind27.c:824-825` / `grind28.c:1114-1115` read `fprintf(f, "],` newline `");` -- a newline inside a string literal is a C compile error. The R32 X1 patch could never have built. Fixed in both files to `fprintf(f, "],\n");`. A quote/brace/paren scan after the fix: 0 raw-newline strings; braces 200/200 (grind27), 249/249 (grind28); parens balanced.
* Logic read: `load_lane_state` (grind27.c:891-905) re-reads `HIT-CANDIDATE.json`, matching `"lane"`, and restores `G_HITS`; `run_lane` zeroes `G_NHITS` (944) before the load; hit insertion dedupes by seed (1009-1011); `write_status` emits a top-level `flagged_survivors` from `G_HITS` (819-825). `jkey/jstr/jnext_obj` (grind27.c:652-700) handle the file shape written by `write_hits_file`. Known residual (R32 item d): a lane switch rewrites the single hit file and drops the prior lane's hits. Not a parse problem.
* Verdict stays "unbuilt/untested" (no compiler). Nav docs: `PICKUP-HERE.md` now carries an explicit **S2 do-not-resume until compiled** line; the R32 banner already said build before resume.

## 4. `not_covered` hygiene

* The 9 `[X1/R32 draft text]` items (B-05, B-16, R12-C1, R12-D2, A-03, E-02, F-01, H-03, R29-L1-ONION-STEGO) checked against each row's hypothesis/coverage/result and evidence: B-05, B-16, R12-C1, R12-D2, A-03 and R29-L1 (`sweep_log.tsv` is 1 line) **confirmed, tag dropped**. **F-01** reworded: its sweep is a skip-aware beam (`round16/F-01/sweep.py` imports `sk.beam_decode`, max_skip 3), so "keyskip1-class" is right but it is not "direct". **H-03** reworded: `round16/zeroFP/RESULTS.md` has no matrix/rotate section. **E-02** rewritten by the B1 patch (corrected payload now re-run).
* R30-A1/A2/B1/B2/C1 `not_covered` filled from their rows; B1/B2 mention the corrected-payload dependency.
* `analysis/handoff/validate_ledger.py`: new advisory warning `NULL-NOT-COVERED` for `negative`/`eliminated` rows with round >= 19 and empty `not_covered` (parses the leading integer of `round`). Before the fill it fired on R30-A1/A2/B1 (B2 and C1 were already counted among the five null rows); after the fill it fires on none (0 hits).

## 5. This round's lanes

**I1.** (a) Timing: `PREREG.md` mtime 13:23:59 post-dates `beam_v3.py` (12:58:29) and every output (12:59-13:22); it claims "Written 2026-10-29 12:57 PT, BEFORE ... any output file existed" and carries a declared Addendum "after outputs". The pre-run text cannot be verified from disk -> **FOUND-ERROR (minor), same shape as R32 I1**. (b) Numerics: `audit_i1.py` recomputes every cell median from `out_grid_base/panel_max.json` and fraction-over-null from `out_null_*`, compares to `power_envelope.json` and R32 I1's published medians: **0 mismatches, v3 54/54 RECOVERED, driftbeam 48/54, V2 violations 0** (`i1_envelope_audit.json`); nulls/bars in RESULTS s3 equal `power_envelope.json`. (c) Binding comparison: driftbeam on the same I2-halves plants is the right binding baseline (the plant-text deviation moves R32-published numbers, e.g. NOVOWEL keyskip1 0.946 vs 0.783 same-plant), so the envelope is **not cell-for-cell comparable to R32 I1 for NOVOWEL/lite-half registers**; the RESULTS says so, and the skip_by_two 0.721 agreement is coincidence. (d) Weakness: the RECOVERED rule's null clause uses a shuffled EN_MODERN null (`run_envelope.py` run_null) for every register; I4 shows NOVOWEL wrong-key overfits reach pmax > 7.6 routinely, so `frac_over_null` for NOVOWEL cells is lenient (recovery, the truth-based clause, is unaffected). (e) **Re-runs** (`rerun_i1.py`, `rerun_i1_cells.json`), EN_NOVOWEL skip_by_two L=120, 5 plants:

| design | seeds 0-4 recoveries | median | stored same seeds | fresh seeds 40-44 median |
|---|---|---|---|---|
| driftbeam (base) | .725 .083 .65 1.0 .9 | 0.725 | identical (row-for-row) | 0.283 (.167 .825 .283 .617 .192) |
| v3 panel_max | 1.0 x5 | 1.000 | identical | 1.000 |

Also EN_NOVOWEL free_q05 L=120: driftbeam 0.267 (fresh 0.525) vs v3 0.975 (fresh 0.992); EN_MODERN skip_by_two: both 1.000. All stored-seed re-runs bit-identical. Note the driftbeam 5-plant spread (0.08-1.0) is wide: the 20-plant median 0.721 is itself seed-sensitive.

**I2.** `rerun_i2_doublet.py` / `rerun_i2_doublet.json`: skip_by_two ciphertext doublet rate, three plaintext/encipher variants.

| variant | L | reps | mean % | median % | mean doublets |
|---|---|---|---|---|---|
| I2 (testhalves_lite, beam_v2 enc) | 240 | 300 | 0.572 | 0.418 | 1.37 |
| I2 | 12,956 | 30 | 0.593 | 0.587 | 76.8 |
| L7 encipher, I2 text | 240 / 12,956 | 300 / 30 | 0.587 / 0.596 | 0.418 / 0.602 | 1.40 / 77.2 |
| L7 encipher + self_reliance text (L7's own recipe) | 240 / 12,956 | 300 / 30 | 0.610 / 0.596 | 0.418 / 0.606 | 1.46 / 77.2 |

`0.84 % = 2/239`: a median-of-7 of integer counts at L=240 (median of 1 or 2 doublets). **FOUND-ERROR** against `round18/L7-redteam/ledger.json:119`/`RESULTS.md:260` and the R32 plan Q2 prior (`round32/CAMPAIGN-PLAN.md:86`): the figure does not replicate; skip_by_two's true rate ~0.59-0.60 % (analytic 0.6035 %), equal to keyskip1. LP2's 0.664 % is ~1.2 sd above. L7's *exclusion* of key-side/plain-side filters (3.77/3.80 %) is unaffected. Corrections: `../PICKUP-HERE.md:31`, `LEDGER.json` `L7-B-BEAM-ENVELOPE.r33_x1_supersession`, `ELIMINATION-LEDGER.md` block (original text kept). I2's RESULTS table matches `representability*.json` (14 rows regenerated, 0 mismatches). Internal tension (minor): s1 says the prior cannot discriminate, s3 then "earns" relations on it (R4).

**B1.** Facts reproduce: 3 bytes (idx 45/50/246: 81->107, 21->47, 224->198) differ between `pp49_51/canon_256.bin` and `round19/C1/payload_resolved.bin` (== `round18/L5-payload/payload_resolved.bin`); head32 identical, six other B-04 payload seeds change; 4480+4480+17920+49280 = 76,160; R17 inputs `data/{moby,pride,war}.txt` absent (only `kjv.txt` present), no `trigram_idx.npy`, so Q5 holds. Findings: (i) the ledger patch lacks "E-01 nearly vacuous" (only in RESULTS s Notes) -- added to the E-01 coverage; (ii) **readers missed by the four rows**: R16-KDF (`round15/KDF/sweep.py:72-73` uses `B04_SEEDS.core()`, whose prefix list includes `canon256_`, `round13/B04/seeds.py:289-294` -> 7 of 504 core secrets, 6 change; `C-CANON` named it but could not show the read), `round30/B1-blob-crypto/battery.py:33`, `round30/B2-rsa-gpg/b2_rsa_gpg.py:33` (canon_256.bin direct; both rows had `not_covered: null`), `round29/L2-blob-cross/attack.py:22,113`, `recon/lp2h_index/h1_index.py:51`, `campaign18_skip/{payload_skip,armada/payload_ciphertext,armada2/numeric2_skip}.py`, `campaign11/12/14` forensics, `round28/L2/{reader,keysweep}.py` (comparator), and `handoff/capsule/MANIFEST.json:1575-1587` (payload.canon_256 sha256 `4c8dc855...`) plus `round17/P3_tables/pads_manifest.json`. Already covering the corrected bytes: R19-C1, R28-L5 (`l5_payload_micro.py:555`), R20-SRESCOPE (`rescope20.py:41,325`). **Promotion is not safe to do as a bare file move**: it breaks the capsule hashes (`verify_capsule.py`) and leaves R16-KDF/R30-B1/B2 unfed. Also R30-E1 says decpref is refuted, so B1's patched-decpref seed is moot. R17 `not_covered` wording ("corrected payload: harness not re-runnable") is accurate. Applied with the owner's Option A (2026-10-29) cited on `C-CANON-PAYLOAD-3BYTES`; no data file moved.

**B2.** (a) Two-character diff: reverting exactly those two `-` characters (seg 8 gap 12 = U+16D2|U+16E1; seg 40 gap 8 = U+16BB|U+16AA) in the LF-normalised file reproduces `MANIFEST.json` sha256 `5e0003aa7f7dde3b238d17c5f964790dbf6bf9db5edacc4a5ec0bad81c6f4bce` -- **exactly two characters, exactly as the issue states**; `.` 183 -> 181 and `-` 2764 -> 2766 consistent (current counts 181 / 2766). Note the working-tree file is CRLF (44,428 B vs 43,739 B LF) so `verify_capsule` reports `runes.canonical` INTACT-FAIL, as it does for 12 other items (CRLF checkout); the manifest sha is now stale for this file regardless. (b) Ordering (minor): data file mtime 12:56:15 precedes `PREREG.md` 12:58:02 though Part A is written as a prescription ("Apply exactly two edits"); `_val_before/_after` at 12:55-12:56. (c) p27:93 = U: `p27_93.md` (6 px to singleton bitmap 421, itself a p13 U glyph; 11 px to 57x U; ~2,900 px to real Bs) is internally consistent; I did not re-derive the bitmaps. (d) LP1: `lp1_misses.json` reproduces: 1,699/1,796 = 94.599 %, 97 misses (89 missing / 1 wrong / 7 replace), **75 in SOME WISDOM canon 659-735, 22 isolated**, top-20 all U / 53 px / 11 with margin 5; without the block 1,698/1,720 = 98.72 %. The "coverage gap" reading is supported by the alone-alignment (44/76 scattered, longest run 4) but cannot be distinguished here from alignment drift on a page the vendored set only half covers (05.jpg 83 glyphs for 157 runes). `status` normalised data-correction -> audit.

**O1.** PREREG only (mtime 12:55:41, sole file, no outputs). Minor: Q3 says "9 measured gs releases" but lists 8 measured + 9.03 unmeasured. Filed `never-run` (queued).

**B3.** Not yet available at audit time (`B3-v3-readjudication/` holds PREREG.md, control.json, null_v3.json, readjud.py, readjud_rows.jsonl, run.out; no RESULTS.md, no ledger.json). Coordinator to check. Observation only: I1 itself says the hitfn20 bars are not valid for v3; B3 must use `null_v3.json`.

**Vocabulary.** `I1/ledger.json` status `positive` -> `measured`; `I2/ledger.json` (flat object, `instrument-result`, round string) -> `measured` entry; `B2` `data-correction` -> `audit`; B1 patches carry no status (patch-only). No "closed/exhausted" in any lane file (matches only prohibitions in B1/B3 PREREG and "solved pages" in B2).

## 6. Files edited (one-line diffs)

| File | Change |
|---|---|
| `LEDGER.json` | +6 rows (R33-I1, R33-I2, R33-B2 x2, R33-O1, R33-X1); B1 patches on B-04/R17/E-01/E-02/C-CANON (+ owner Option A, reader audit); 9 draft tags dropped (F-01/H-03 reworded); R30-A1/A2/B1/B2/C1 `not_covered`; R32-B2 row fixes; L7-B `r33_x1_supersession`; counts 181 -> 187 |
| `analysis/handoff/validate_ledger.py` | advisory `NULL-NOT-COVERED` warning |
| `analysis/round27/P1-engine/grind27.c`, `analysis/round28/L4/grind28.c` | fix raw-newline string literal in `write_status` (UNBUILT) |
| `ELIMINATION-LEDGER.md` | appended "Round 33 X1 corrections" block |
| `PICKUP-HERE.md` (liber-primus) | R33 banner: S2 do-not-resume, owner Option A, p27:93, 0.84 % superseded |
| `../PICKUP-HERE.md` | skip_by_two 0.84 % marked superseded; p27:93 status |
| `README.md` (liber-primus), `../README.md` | C-CANON owner decision; p27:93 machine-resolved |
| `analysis/README.md` | new round33/X1 row |
| `analysis/round33/X1-redteam/` | new: RESULTS.md, ledger.json, php5_independent.py, d5c_replicate.py, d5c_analyze.py, d5c_replication.json, feat_x1_*.json, rerun_i1.py, rerun_i1_cells.json, audit_i1.py, i1_envelope_audit.json, rerun_i2_doublet.py, rerun_i2_doublet.json, ext*.log |

## 7. Validators and tests (after all edits)

* `python analysis/handoff/validate_ledger.py` -> 187 entries, **ERRORS: 0**, WARNINGS: 23 (advisory; the 3 new `NULL-NOT-COVERED` hits seen before filling are gone), Unsound negatives: 0.
* `python tests/validate.py` -> ALL VALIDATIONS PASSED.
* `python -m pytest tests/ benchmark/ -q` -> 24 passed.
* `build_index.py`, `build_problem.py`, `build_knowledge.py`, `build_solved_pages.py` ran clean; `check_consistency.py` -> "No document drift detected." (The regenerated JSON files were rewritten in place; `git diff` not run.)
* `verify_capsule.py` (offline): 13 INTACT-FAIL (incl. `runes.canonical`, most CRLF-checkout noise), pre-existing class; the canon_256 entry would fail after promotion.

## 8. Round-34 candidates (ranked)

1. **Re-feed the corrected payload to the unfed readers and regenerate capsule hashes** (R16-KDF 7 secrets, R30-B1 blob battery, R30-B2 RSA/GPG, `h1_index`), then do the coordinator's promotion. Prior: low flip probability, near-zero cost, removes the last "unvalidated input" caveat (`round13/B04/seeds.py:289`, `round30/*`, `MANIFEST.json:1575`).
2. **v3-specific null refit (Gumbel) and register-matched nulls**, then B3-style re-adjudication at sweep scale. Prior: measured gap -- v3 free/L=400 null max 13.03 at N=100 (`I1 RESULTS s3`), NOVOWEL null not register-matched, I4 shows NOVOWEL wrong-key overfits are the dominant false-positive class.
3. **D5c length calibration `m_NV(L)` on >= 4 lengths** (and a second recipe). Prior: replication shows L=240 holds, L=120 fails 53/53 (`d5c_replication.json`); needed before any seal is usable on real page lengths.
4. **Build and test the patched C engine on a box with a compiler**, then resume S2 (44.14 %) and the R28-L4 queue. Prior: a real syntax bug was just found; the PHP full-2^32 tail (R32-B2 0.97 %) and S2 remain the largest finite uncovered spaces.
5. **O1 Ghostscript render compare** and a **PHP 5 binary cross-check** of the legacy twist (both need an off-box/Linux build). Prior: small for the key, but each is a falsifiable new observable (`O1 PREREG`; `R32-B2` not_covered).
(Dropped as a candidate: building relations for I2's skip_by_4/5/resets -- the doublet prior is non-discriminating (R4), now shown to be so for skip_by_two as well.)

## 9. Coordinator decisions

1. Perform the `payload_resolved.bin` promotion **together with** regenerating `handoff/capsule/MANIFEST.json` hashes and re-feeding R16-KDF/R30-B1/B2 (or accept stating them in `not_covered`, already done).
2. Commit the issue-12 data edit and close #12; regenerate the capsule sha for `data/krisyotam_runes.txt`.
3. Build the fixed `grind27.c`/`grind28.c` before any S2 resume.
4. Check B3 `RESULTS.md` when it lands (not audited here).
5. Whether I2's "earned" relations (s3) should be struck given its own s1.
