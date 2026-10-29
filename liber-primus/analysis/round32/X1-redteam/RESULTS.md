# Round 32 / X1 -- red-team of the repository's own claims (R6 standing lane) -- RESULTS

_2026-10-28. Stance: refute-by-default. Every item is FOUND-ERROR or NO-ERROR-FOUND with a citation; a
NO-ERROR-FOUND states what was checked, not that the claim is true. Nothing here says solved / closed /
exhausted. No git was run. Paths are relative to `liber-primus/`._

## 0. FOUND-ERROR summary table

| # | Target | Sub-verdict | One line |
|---|---|---|---|
| 1 | Ghostscript lower bound | **FOUND-ERROR** | "GS 9.01-9.15" is contradicted by `round18/L1-toolchain/icc_versions_early.json` (9.00/9.01/9.02 `matches_LP2:false`); supported window is 9.04-9.14 (9.03 unmeasured) |
| 2 | R27 "coverage 1.00" | **FOUND-ERROR** | per-relation figure (`pair`) read as closure of the Py2.7-MT space; S2 `exact` 44.14 %, R28-L4 zero |
| 3 | C-CANON-PAYLOAD-3BYTES | **FOUND-ERROR (documented, undecided)** | coverage stated on `canon_256.bin`; 3 bytes differ in `payload_resolved.bin`; README said "canon_256 stands" while R28-L2 vouches for the corrected bytes |
| 4 | Transcription scope | **FOUND-ERROR** | pooled T1 gate FAILED 95.09 % (bar 99 %); claim never said LP2-typeface-only; p27:93 unresolved |
| 5 | `not_covered: null` hygiene | **FOUND-ERROR** | 8 rows applied; R12-A1 had already been filled in R28; the plan's "texts in T1-PATCH-PROPOSALS.md" exist for R12-A1 only, the other 8 were drafted here |
| 6 | Seal reporting bug + parked crosser | **FOUND-ERROR** (real engine bug, different from the one reported) + crosser re-screen: NOISE | see section 6 |
| 7 | R30 D1 bookkeeping | **FOUND-ERROR (minor)** | links exist both ways; but B-10 named OutGuess 0.2, R29-L1 ran 0.4; R29-L1 `not_covered` was null; `sweep_log.tsv` header-only |
| A-I1 | I1 skip-by-two decoder | **FOUND-ERROR (minor)** | PREREG mtime post-dates the envelope; otherwise NO-ERROR-FOUND on numerics |
| A-I2 | I2 re-adjudication | **FOUND-ERROR (minor)** | EN_NOVOWEL L=120 power 22/24 = 0.917 reported as 0.92 and "meets_target_0.92: true"; patch would have clobbered `restated_from` |
| A-I3 | I3 R3 enforcement | **FOUND-ERROR (minor)** | test file cited at wrong path; numerics NO-ERROR-FOUND |
| A-I4 | I4 non-fold seal | **FOUND-ERROR (minor)** | `PASS_point_and_wilson_upper_le_0.10: true` omits the NOVOWEL class (upper 0.153); D5c NOT adopted in SEAL_PASS (checked) |
| A-B3 | B3 close-out | **NO-ERROR-FOUND** on label; **FOUND-ERROR (minor)** wording at `round28/L3/RESULTS.md:92`; patch `positive_control` text strings fail the validator |
| A-B1 | B1 bash `$RANDOM` | **NO-ERROR-FOUND** on numerics; near-miss re-screen reproduces; patch status `negative-bounded` outside vocabulary |

## 1. Ghostscript lower bound -- FOUND-ERROR

Evidence: `analysis/round18/L1-toolchain/RESULTS.md:200-212` (table: 9.00/9.01/9.02 -> 3,144 B profile, illuminant
`0000f6d6...0000d32d`, **no**; 9.04..9.21 -> 2,576 B, byte-identical, **YES**) and
`icc_versions_early.json` (9.00, 9.01, 9.02: `"matches_LP2": false`; 9.04: `true`). Release 9.03 has no row in either JSON, so the
honest lower bound is "9.04 is the first release measured to match; 9.03 unmeasured" (L1 RESULTS.md:207 states "Ghostscript >= 9.04", which
is slightly tighter than its own table). The upper bound is 9.14 by publication date (L1 RESULTS.md:211) and 9.21 by profile alone.
`round30/SYNTHESIS.md:19,30` and `LEDGER.json R30-A3-PDF-FORENSICS` asserted "9.01-9.15" and said only 9.06 was byte-confirmed
("9.05/9.07/9.10/9.14 tags 404'd") -- R18-L1 had already byte-matched 9.04, 9.05, 9.06, 9.07, 9.09, 9.10, 9.12, 9.14, so A3 re-derived a weaker bound and did not inherit L1's.
**Corrected to "GS 9.04-9.14 [9.00-9.02 measured non-matching, 9.03 unmeasured]"** in every file that carried it (list in section 9).

## 2. R27 "coverage 1.00" -- FOUND-ERROR

`ELIMINATION-LEDGER.md` lines 24-25 (pre-edit): "R20/21/25/27 Py2.7-MT pair-decoder over [0,2^32) at coverage 1.00 / power 1.00" and root
`README.md:323` / `liber-primus/README.md:62-64` "that branch is **exhausted**". Facts on disk: `analysis/round27/P1-engine/run/STATUS.json`
`lane_coverage_fraction: 0.441383776`, `current_lane: S2`, `relation: exact`, `lanes_completed: ["S1"]`; R28-L4 `LEDGER.json` status `never-run`. Restated in the
ledger, both READMEs and PICKUP-HERE: coverage 1.00 is **per-relation (`pair`, S1)**; the `exact` relation is 44.14 % and L4 is zero. "Exhausted" removed from the README.

## 3. C-CANON-PAYLOAD-3BYTES -- FOUND-ERROR, decision left to the coordinator

Facts: `analysis/pp49_51/canon_256.bin` and `analysis/round19/C1/payload_resolved.bin` (== `round18/L5-payload/payload_resolved.bin`) differ at exactly
3 positions: idx 45 (81 -> 107), 50 (21 -> 47), 246 (224 -> 198) (checked byte-by-byte). Who reads which:
- B-04: `round13/B04/seeds.py:251-262` reads `canon_256.bin` (+ `canon_256_decpref.bin`) as ONE of the seed sources among 2,165.
- R17: `round17/P3_tables/build_pads.py:213-216` reads `canon_256.bin` as ONE of many pads.
- R16 zeroFP E-01/E-02: `round16/zeroFP/zerofp_tests.py:85,247` read `canon_256.bin` directly (E-02's permutation test is single-byte sensitive).
- R16-KDF: not shown to read the payload; whether its 534-item secret list contains payload-derived items was NOT checked here.
- B-05 was re-run on the corrected bytes in R19 (counts note).
- **Inconsistency found:** root-`liber-primus/README.md` said R28 "agrees with the canon 100 %, all three byte flips included, so `canon_256` stands"; but the flips are *away from* `canon_256.bin`, and R28-L2 itself (`round28/L2/RESULTS.md:95-98`) says "the correct payload remains `payload_resolved.bin`". Corrected in the README.

**Option A -- promote `payload_resolved.bin` + flag for re-check.** Cost: small (a handful of B-04 payload-derived seeds, R17's one pad, E-01, E-02 re-fed the
corrected file; not re-sweeps); benefit: the transcription evidence (R19-C1 A-04, R28-L2 blind instrument) already favours the corrected bytes.
**Option B -- keep `canon_256.bin`, restate `not_covered`.** Proposed text (also stored as `x1_r32_options` on the ledger row, status still `open`):
> "Coverage is stated against canon_256.bin. The 3 bytes corrected by R19-C1 (idx 45/50/246, payload_resolved.bin) were not re-fed to B-04's payload-derived seeds, R16-KDF payload-derived secrets, R17's canon_256 pad or E-01/E-02; results could differ at those 3 bytes. Not covered: the corrected payload as input."
X1 did not choose. Evidence tilts to A (cheap, and the current state is "unvalidated input" for four rows).

## 4. Transcription-closed scope -- FOUND-ERROR

`round19/T1/RESULTS.md:10-13`: G-READ-LP2 180/180 PASS; **G-READ-ALL 1,879/1,976 = 95.09 % FAIL (bar 99 %)**; LP1 recall 94.60 %, 75 of 89 misses in one section, "NOT licensed: any claim about LP1" (line ~250). p27:93 U->B margin 5 is "nominated, not resolved. A human should look at that one glyph" (T1 RESULTS.md:414-416, 488); `PICKUP-HERE.md` (liber-primus) C-eyeball section carried it without a status. Edited: `ELIMINATION-LEDGER.md` (line 33 area), `../README.md` and `../PICKUP-HERE.md` ("verified three/four independent ways" now says LP2-typeface-only and surfaces p27:93), `liber-primus/PICKUP-HERE.md` (scope note at the C-eyeball block).
NB: the 450/450 agree-with-canon result is on the O/A/AE disagreement set and is consistent with the LP2-only pass; it does not contradict p27:93, which lies outside that set (T1 RESULTS.md:430).

## 5. `not_covered: null` hygiene -- FOUND-ERROR (partly applied before this lane)

Recount of `LEDGER.json` rows with null/empty `not_covered`: before X1 there were 8 of the 9 named plus many `open/never-run/audit` rows (those are not negatives;
`audit` rows have no coverage claim). **R12-A1 was already filled** (R28 merge note: "R12-A1 not_covered filled per R28-R T1 patch"; text matches `analysis/round28/R/T1-PATCH-PROPOSALS.md` section 1) --
the plan's premise was stale for that row. `T1-PATCH-PROPOSALS.md` supplies text **only** for R12-A1 (section 3 just lists the other rows, `R/RESULTS.md:42`). X1 therefore **drafted** texts for
B-05, B-16, R12-C1, R12-D2, A-03, E-02, F-01, H-03 from each row's own hypothesis/coverage/result/reopens_if (tagged "[X1/R32 draft text]" so a human can overrule). Applied to `LEDGER.json`; `validate_ledger.py`: 0 errors.
**Remaining null-`not_covered` negatives found (not applied, listed for the coordinator):** `R30-A1-FONT`, `R30-A2-SUBPIXEL`, `R30-B1-BLOB-CRYPTO`, `R30-B2-RSA-GPG`, `R30-C1-ART-ATTRIBUTION` (R29-L1 was filled under target 7).
The validator does not flag a negative with null `not_covered`; a one-line check would.

## 6. Seal reporting bug + parked crosser -- FOUND-ERROR (engine) / NOISE (seed)

**Engine.** `analysis/round27/P1-engine/grind27.c` (and `round28/L4/grind28.c`, inherited):
(a) per-worker `"flagged_survivors": []` is a literal (grind27.c:805; confirmed, R28-R D6); (b) **new finding:** `G_NHITS` is reset to 0 at every `run_lane` start (grind27.c:919) and
`load_lane_state` (grind27.c:~857-895) restores cursors/hist/top but **not** hits, so after a resume `n_claim_bar_hits` reads 0 and `write_hits_file` (grind27.c:755) would **overwrite**
`HIT-CANDIDATE.json` with only post-resume hits, dropping 35563892. That is exactly the observed STATUS (`n_claim_bar_hits: 0`) vs HIT-CANDIDATE (1 hit) disagreement.
(c) **Refuted:** R28-R D6's other claim -- that worker `best_pmax` "carries across lanes", so S2's STATUS merely displays S1's crosser. `run_lane` resets `best_pmax=-1e30` (grind27.c:916) and only restores it if `STATUS.current_lane` equals the lane; my re-screen below shows the S2 `exact` screen score for this seed is genuinely 7.6706-7.6707.
(d) HIT-CANDIDATE.json is a single file rewritten per lane: S1's three crossers' record lives only in `round27/ORACLE-*.md`, not in that file.
**Patch (minimal, unbuilt, no compiler here):** in both `.c` files -- `load_lane_state` now re-reads `HIT-CANDIDATE.json` and restores this lane's hits; hit insertion skips a seed already in `G_HITS` (resume re-scans after the last checkpoint);
`write_status` emits a top-level `"flagged_survivors": [seeds]` from `G_HITS` (the per-worker literal is left as is). **Must be compiled and tested against the parked S2 state before use.**

**Crosser re-screen (`rescreen_35563892.json`, `rescreen.py`).** Py2.7 `init_by_array([35563892])`, `random29`, offset 0, sign -1, beam_w 64, L120 screen, round32/I2 panel, `round19/I1/driftbeam.py`, hitfn20 gate at L240, N=1e6.

| relation | screen pmax | register | n_skips | L240 gate | verdict |
|---|---|---|---|---|---|
| `pair` (keyskip2) | 7.6706 (C engine 7.6707) | LP1_REAL | 0 | stage-b pmax 4.962 < bar 7.3835 -> FAIL clause 1 | noise crosser |
| `exact` (keyskip1) | 7.6706 | LP1_REAL | 0 | stage-b pmax **5.778 < bar 7.6342** -> FAIL clause 1 (recovery 1.0 / held-out 1.0 are self-consistency, no language evidence) | **noise crosser under S2's own relation** |

The decode has **zero key skips**, which is why `pair` and `exact` give a bit-identical screen score (the relation is moot for this seed). The 0.0001 difference from the C value is the rebuilt panel (round19/I2 `models/` is not on disk).
Reconciliation: HIT-CANDIDATE.json (1 S2 hit, seed 35563892 @ 7.6707 >= 7.6342) is the correct record; STATUS `n_claim_bar_hits: 0` is the resume bug. The S2-lane adjudication owed by R28-R D6 is now recorded: NOISE at L=240. This discharges one seed, not S2 (44.14 % swept).

## 7. Round 30 D1 bookkeeping -- FOUND-ERROR (minor)

Linked: `R29-L1-ONION-STEGO` `supersedes:["B-10"]`; `B-10` `status: superseded`, `superseded_by:["R29-L1-ONION-STEGO"]`; ELIMINATION-LEDGER.md:1041-1044 cites it. 24,078 = 4,013 x 3 x 2 checks out; control passed (keyless baseline).
Belief-vs-evidence mismatches: (i) B-10 was "OutGuess **0.2** Linux control"; `round29/L1-onion3-crack/FINDINGS.md:66,145` ran **OutGuess 0.4** + steghide -- the discharge is tool-mismatched; (ii) `sweep_log.tsv` is header-only (1 line), so the 24,078 figure rests on FINDINGS.md + re-runnable `sweep_fast.py`; (iii) `R29-L1` had `not_covered: null` on a negative. Fixed (iii) and noted (i)/(ii) on the rows.

## 8. Audit of this round's lanes (refute-by-default)

**I1 (`I1-skipbytwo-decoder`) -- FOUND-ERROR (minor).** Recomputed: RESULTS table matches `power_envelope.json`/`ledger.json` values (adv1 on skip_by_two 0.300/0.168, adv2 1.000, NOVOWEL 0.721/0.705; re-adjudication 0 flagged, best 4.54). Timing: PREREG.md mtime 16:32:32 is *after* the envelope outputs (16:17-16:31) and `readjud.py`; it states "Written BEFORE any envelope cell was run" with an in-place Addendum A -- the original pre-run text cannot be verified from disk (no copy), so the pre-registration claim is unverifiable, not disproved. Doctrine: lane honestly reports a failed control (EN_NOVOWEL), "decoder pre-exists in R19/I1", coverage <1 % of B-04; no "closed/exhausted". Lite 7-register panel (no EN_KJV/CY) means the bars are empirical shuffle-null maxima (n=100, alpha~1/n) -- thin at L=6000 (n=4, 3 plants). Row filed as `measured`.

**I2 (`I2-multiregister-readjudication`) -- FOUND-ERROR (minor).** PREREG (16:15) precedes outputs; corpus substitutions disclosed in RESULTS section 1. (a) `out_power.json`/`gate_proof.json`: EN_NOVOWEL L=120 `pow_pmax 0.92` is 22/24 = 0.9167, rounded; `meets_target_0.92: true` and "target met exactly" are false at full precision (gate >= 0.90 is met). (b) EN_NOVOWEL recovery is only 80 %; (c) L=240 null reduced 5x, L=400 not run (disclosed). (d) The proposed `ledger_patches.json` writes a new text into `restated_from`, which in this ledger holds the **original** coverage text (counts note: "Original coverage text is preserved in each entry's restated_from") -- applying literally would destroy it; X1 stored the text in `r32_i2_restatement`, appended it to `coverage`, replaced only the "non-English plaintext registers" `not_covered` item and appended evidence. (e) Its own caveat is right: survivor-level only; short heads; bars extrapolated 1/sqrt(L). Panel CY is **modern Welsh prose**, not Middle Welsh.
**Welsh fetcher:** `data/fetch_sources.py` never fetched the corpus. Added `ensure_welsh_substitute()` / `python data/fetch_sources.py --welsh` building `data/keys/welsh/welsh_mabinogion.txt` from Project Gutenberg #3680, #57981, #56275, #67424 (boilerplate stripped). Test: rebuilt = 716,406 chars vs the file I2 used = 716,409 (3-char difference, not byte-identical; not diagnosed), so a fresh-clone panel is a sibling of I2's, as I2 already says. The English `mabinogion.txt`/`kjv.txt` substitutes were copied from `analysis/bookcipher/books/`; not added to the fetcher (local copy, noted here).

**I3 (`I3-r3-enforcement`) -- FOUND-ERROR (minor).** Recomputed from `null_curve32.json`: exponent -0.5675, SE 0.0623 (5 pts, 3 DOF), pooled -0.5791 SE 0.0318, two-point -0.5815, beta(120)=0.07095 -- all match RESULTS section 5. Ledger validator before/after (0 errors; 18->22 warnings) consistent with my run (24 warnings after the new rows). Error: RESULTS/PREREG/ledger cite `analysis/handoff/test_validate_ledger_r3.py`; the file is `tests/test_validate_ledger_r3.py` (corrected in the three lane files and the row). PREREG was written after the null curve was computed (file mtime 17:07:55 vs `null_curve32.json` 17:06:07) -- disclosed in the PREREG's own honesty note. Scope caveat worth stating: with the -5.5 floor binding at L>=120, N<=1e6 the "L-aware" bar equals the legacy bar for every historical sweep at L>=120; the change only bites at short L. `ARMADA-DOCTRINE.md` R3 "CI-enforced" is now true for new `sweep_store` rows only; the pytest file is in `tests/`, which CI collects only if configured -- not verified.

**I4 (`I4-nonfold-seal`) -- FOUND-ERROR (minor).** D5c rule: Addendum A written after the seen-data run, Addendum B after virgin-1 and before virgin-2 (PREREG lines 78, 103; RESULTS says "derived post hoc"). `catch_surface.json`: `SEAL_PASS: false`, `SEAL_PASS_L1_COMPARABLE: true`, `ledger_SEAL_PASS: False`, `SEAL_CANDIDATE` D5c -- so D5c is **not** adopted in SEAL_PASS. Numerics 378/392=0.964, FR 0/40, pooled 1/113 match the JSON. Error: the key `PASS_point_and_wilson_upper_le_0.10: true` omits the NOVOWEL class, whose own Wilson upper bound is 0.153 > 0.10; PREREG Addendum B's rule ("point estimate meets, bound does not") would label that cell "point only". Also: virgin-2 asked for 500 NOVOWEL reps and scored 392 hallucination + 33 genuine + 39 gray (disclosed); L=120 probe shows `m_NV` is length-dependent (FR 92/92). Row filed as `audit`, SEAL_PASS unchanged.

**B3 (`B3-closeout`) -- NO-ERROR-FOUND on the R28-L3 label; minor wording error; patch normalised.** Checked on disk: `round28/L3/` has `progress28.json`, `controls.json`, `control_e2e.json`, `hash_gate.json`, `subsumption.json`, `dict_meta.json`; `candidates28.jsonl` and `dictionary.jsonl` absent (gitignored `.gitignore:374-376`). `sweep28.py:271-277` appends to `flagged_survivors` on `v.hit` and stops, so the empty list in `progress28.json` is a real record, not the grind27 hardcoded `[]`. `inconclusive` is a valid status and follows B3's own pre-registered kill rule, so it is the conservative-correct label; it understates what is on disk (stage-A + gate record of 0 flagged), which the row note now says. Error: `round28/L3/RESULTS.md:92` "every one had pmax < a claim bar per best_pmax" infers stage-B (L=240) pmax from stage-A (L=120) `best_pmax`. glibc first-fire: `sweep_summary.json` 96,072 decodes, 11 stage-B, 0 flagged, `complete:true` match RESULTS; panel is a lane-local rebuild (disclosed). Patch problems: `positive_control` was a long text string (validator demands exactly `passed` on negatives) -> moved to `control_detail`; `round` was a string; R19-G3-CORRECTION pointer applied.

**B1 (`B1-bash-random`) -- NO-ERROR-FOUND on numerics; near-miss re-screened.** `sweep_summary.json`: 74/74 prefixes, 192,066 decodes, 47,449+48,584 survivors, 490 stage-B, `flagged: []`, `gate3_crossers: []` -- matches RESULTS; control 25/26 and head mismatch 0/4000 verified in `control.json`. PREREG finalised during the sweep, disclosed in its header (mtime 17:24 after control 17:22, before sweep end 17:56); no decision changed after seeing scores is asserted, not verifiable. Power is the binding term (prefilter 0.43-0.76; planted keys with early skips dropped), so "coverage 1.00 of seeds" must not be read as closure -- RESULTS section 6 says so. Patch status `negative-bounded` is not in the vocabulary -> `negative`; `positive_control` string -> `passed`.
**Near-miss seed 1354603465 (`rescreen_1354603465.json`):**

| ABI | relation | screen pmax (reproduced) | n_skips | L240 gate |
|---|---|---|---|---|
| bash4.2 LP64 | keyskip2/`pair` | **7.0680** (B1: 7.068) | 8 | stage-b 4.662 < 7.3835, recovery 0.61 -> FAIL clause 1 |
| bash4.2 LP64 | keyskip1/`exact` | 2.800 | 8 | 3.620 < 7.6342 -> FAIL |
| bash4.2_i32 | keyskip2/`pair` | **6.7624** (B1: 6.762) | 6 | 6.086 < 7.3835, recovery 0.87 -> FAIL |
| bash4.2_i32 | keyskip1/`exact` | 2.863 | 3 | 1.827 < 7.6342 -> FAIL |

Reproduced exactly. At the actual-N bar (6.939 per B1) the L240 stage-b scores (4.66, 6.09) are still below the bar; I did not re-run the gate at that N. B1's decision not to flag it follows its declared-N, hitfn20-gated rule; the 7.068 > 6.939 clearance is disclosed. Treated as a single-draw extreme of the null (consistent), not a hit.

## 9. Files edited by X1 (one-line diffs)

| File | Change |
|---|---|
| `ELIMINATION-LEDGER.md` | GS 9.01-9.15 -> 9.04-9.14; Py2.7-MT "coverage 1.00" scoped to `pair`; transcription scope note; "Round 32 X1 corrections" block appended |
| `README.md` (liber-primus) | GS bound; "exhausted" -> pair-only complete null; R28 "canon_256 stands" replaced; "closed" -> "re-read" |
| `../README.md` | GS bound; "exhausted" scoped; transcription LP2-typeface-only; contested-bytes sentence + C-CANON pointer |
| `PICKUP-HERE.md` (liber-primus) | GS bound; scope note on p27:93 / LP2-only; X1 banner (S2 crosser, build-before-resume warning) |
| `../PICKUP-HERE.md` | transcription claim scoped (2 places) |
| `analysis/README.md` | GS bound in round30 row; new round32/X1 row |
| `../AGENTS.md`, `../PAPER.md`, `analysis/round30/SYNTHESIS.md` | GS 9.01-9.15 -> 9.04-9.14 |
| `LEDGER.json` | +8 `not_covered` (B-05,B-16,R12-C1,R12-D2,A-03,E-02,F-01,H-03); R30-A3/G-01/counts note GS bound; `x1_r32_options` on C-CANON (status still open); R29-L1 `not_covered`; B-10 note; I2 restatements on B-04/R16-KDF/R16-PRNG/R17-PUBLIC-PAD (`r32_i2_restatement`, `coverage`, `not_covered`, `evidence`); 8 new rows (I1, I2 audit, I3, I4 audit, R28-L3 inconclusive, R32-B3, R32-B1, R32-X1); R19-G3-CORRECTION note; counts 172 -> 180 |
| `analysis/round27/P1-engine/grind27.c`, `analysis/round28/L4/grind28.c` | restore hits on resume; dedupe re-found hit; top-level `flagged_survivors` from `G_HITS` (UNBUILT) |
| `data/fetch_sources.py` | `ensure_welsh_substitute()` + `--welsh` flag (Gutenberg 3680/57981/56275/67424) |
| `analysis/round32/I3-r3-enforcement/{RESULTS.md,PREREG.md,ledger.json}` | test-file path corrected to `tests/test_validate_ledger_r3.py` |
| `analysis/round32/X1-redteam/` | new: RESULTS.md, ledger.json, rescreen.py, rescreen_35563892.json, rescreen_1354603465.json |

## 10. Validators and tests (after all edits)

- `python analysis/handoff/validate_ledger.py` -> **180 entries, ERRORS: 0, WARNINGS: 22 (all advisory, none from the new rows), Unsound negatives: 0.** B1's and B3's `sweep_store` (192,066 / 96,072 rows) pass the new R3 check.
- `python tests/validate.py` -> **ALL VALIDATIONS PASSED -- rig reproduces known solves.**
- `python -m pytest tests/ benchmark/ -q` -> **24 passed in 16.03s.**
- grind27.c / grind28.c: **not compiled** (no gcc/cc on PATH).

## 11. Completeness critic -- which channel / instrument axis did Round 32 still not read? (seeds Round 33)

1. **Register-aware beam scoring (decoder side).** I1 measured EN_NOVOWEL under skip_by_two at 0.72/0.71 recovery and 0.31 for `free` (`I1 RESULTS.md` s3, s4): the adjudicator sees vowel-dropped text, the *search* does not. Every Round-32 sweep decodes with an English-guided beam. Prior: measured, not speculative; cheap (one decoder change + the existing gates). Also unread: Greek/Hebrew/Norse registers (I2 not_covered).
2. **Corrected-payload input axis (C-CANON).** Four rows (B-04 payload seeds, R17 canon pad, E-01, E-02) were never fed `payload_resolved.bin`; 3 bytes differ and the independent instrument vouches for the corrected ones. Prior: low probability of flipping anything, near-zero cost, and it removes a standing "unvalidated input" caveat.
3. **LP1-typeface transcription + p27:93.** T1's LP1 read gate failed (94.60 %, undiagnosed, 75/89 misses in one section); LP1-derived solved text underlies the LP1_REAL register used in every panel. One human glyph check settles p27:93. Prior: moderate-low for the cipher, high for instrument hygiene (the panel's anchor register is partly un-audited).
4. **Skip-model grid beyond {1,2,free}: key resets at line/page boundaries and advances of 3+.** I1 not_covered ("resets, rewrite/keyside/plainside, advances other than 1,2"); L7-B showed the beam is relation-bound, and `free_q05` at L=6000 already exceeds budget (0.611). The 83 % suppression is the one hard number the filter is pinned by; page-restart keys are the era-natural implementation of a per-page loop. Prior: moderate (explicitly unrepresented, plausible implementation), compute light.
5. **Off-repo artifact channel: source PDF/PS + differential GS 9.04-9.14 render.** The one new fact of R29-R30 is toolchain provenance; R30 SYNTHESIS item 2 (build GS 9.05/9.07/9.10/9.14, render through the jpeg device, compare byte-for-byte with the 58 LP2 JPEGs) was never run, and with the bound now 9.04-9.14 it is a finite 11-release check that could pin the exact version/dpi/ImageMagick flags. Prior: small for the key, but it is the only lane with a falsifiable *new* observable (match/no-match), and it constrains which RNG/OS box to model.
(Also still open and compute-bound, not an unread channel: S2 at 44.14 %, R28-L4 25-cell queue, B2's php mt_rand.)

## 12. Decisions for the coordinator

1. C-CANON-PAYLOAD-3BYTES: Option A (promote + re-check four rows) or Option B (restate, text above). X1 recommends A but did not decide.
2. Build and test the patched `grind27.c`/`grind28.c` before resuming S2 (no compiler here).
3. Whether to fill `not_covered` for R30-A1/A2/B1/B2/C1 (listed in section 5) and add a validator warning for null-`not_covered` negatives.
4. Confirm the drafted `not_covered` texts for B-05, B-16, R12-C1, R12-D2, A-03, E-02, F-01, H-03 (tagged "[X1/R32 draft text]").
5. I1: credit as replication + extension (its own recommendation) and rewrite CAMPAIGN-PLAN s3 I1 accordingly.
6. B2 (php mt_rand) is not filed or audited; its row and patches should pass the same vocabulary / `positive_control == "passed"` checks that B1/B3's patches initially failed.
