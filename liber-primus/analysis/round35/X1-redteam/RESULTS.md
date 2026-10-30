# Round 35 / X1 -- red-team (R6) -- RESULTS

_2026-10-30. Refute-by-default. Each target is FOUND-ERROR or NO-ERROR-FOUND with citations; a NO-ERROR-FOUND states what was checked. No git run. Paths relative to `liber-primus/`. One Python process at a time, nproc=1; no filesystem-wide search. Re-runs: `rerun_i1.py/.json` (I1), `rerun_b1_r34.py/.json` (R34 B1 re-derivation). `B1-bash-orbit-pfv4` and `I3-d5c-prereg` were still running; neither had a `RESULTS.md` at audit time (section 7)._

## 0. FOUND-ERROR summary

| # | Target | Sub-verdict | One line |
|---|---|---|---|
| 1a | R34 B1: PHP prior-dense "no prefilter / reach ~1.00" | **FOUND-ERROR** | only the 487 core seeds are unfiltered; 47,549 dense seeds go through `chunk_php` (pf_v3) -- `sweep.py:51-56, 200-212`, `sweep_summary.json` phase.php `tier_a_core` 487 / `tier_a_dense` 47,549. Reach there is ~0.65-0.71 |
| 1b | R34 B1: 38,223 s gap reading | **FOUND-ERROR** | `sweep_php.log`: 1,966,080 seeds at t=110 s, **2,621,440 at t=38,223 s** (RESULTS says 2,621,440 at t=110). The sleep consumed the 2,100 s cap; the cap alone (~17.9 k seeds/s) would have reached ~1.07 % of 2^32, so 0.061 % is a sleep artefact |
| 1c | R34 B1: store `sweep_rows.jsonl` | **FOUND-ERROR** | 26,050 rows, **all PHP** (mt_scale 6,380 / mt_mod 6,594 / php_scale 6,586 / php_mod 6,490); the resumed invocation reopened the file with mode "w" (`sweep.py:161`; `resume` skips the bash loop at :186) -> 324,798 bash decodes not persisted; RESULTS/ledger describe the store as complete. First invocation also crashed (`sweep.log` traceback at `php_tier_a`) -- unmentioned |
| 1d | R34 B1: store header | **FOUND-ERROR (minor)** | header `prefilter.power_EN_NOVOWEL: 0.998` is the superseded pre-X1 number (RESULTS says "not I2's headline 0.998" in prose but never flags the header field); header `key_space` says "ILP32 stated fraction" though ILP32 ran 296/296 |
| 1e | R34 B1: "bash phases took 911 s each" | **FOUND-ERROR (trivial)** | LP64 933.7 s, ILP32 911.1 s (`sweep_summary.json`) |
| 1f | R34 B1: per-cell table, fraction 1.000, reach arithmetic | NO-ERROR-FOUND | see section 1 |
| 2 | R35 I1 (pf_v4) | **NO-ERROR-FOUND** (numerics + harness) | natural-rate plants confirmed; two cells re-run within 2 SE; k=0 == pf_v3 exactly; fresh-seed FPR under 1e-3; (24,1) alternative matches `roc_both.json` |
| 3a | R35 P1: verdict and hashes | NO-ERROR-FOUND | recomputed sha256 of `data/kjv.txt` / `data/keys/mabinogion.txt` against `round19/I2/out_build.json`; 10/11 corpora equal; CY unrecoverable and recorded as such |
| 3b | R35 P1: "nothing written outside the lane dir; substitutes untouched" | **FOUND-ERROR** | `data/kjv.txt`, `data/keys/mabinogion.txt`, `data/fetch_sources.py`, `handoff/capsule/MANIFEST.json` were changed at 09:31 (RESULTS 09:30:29); R32 substitutes now live only in `P1-restore-r19-panel/backup/`. Addendum appended to RESULTS |
| 3c | R35 P1 -> `data/fetch_sources.py` "now yields those bytes" | **FOUND-ERROR (substantive)** | the script had **no** KJV/Mabinogion fetch at all; the only P1 edit changed the Welsh SUBSTITUTE URL form (cache/epub -> /files/N/N-0.txt), which changes the substitute's bytes (781,166 B vs 761,024 B; recorded 761,030 / 624ffc97). **Fixed** (section 3) |
| 4 | R35 B2 | **NO-ERROR-FOUND** (minor wording) | identity caveat present on the ledger rows; two comparator numbers reproduce stored R30 values exactly |
| 5 | PREREG mtimes, RESULTS vs JSON, vocabulary | NO-ERROR-FOUND | I1, P1, B2, I3 (and B1 observed) all have PREREG before first output; section 5 |
| 6 | Ledger / gate | applied | LEDGER.json 195 -> 200 entries; section 6 |
| 7 | B1 (R35), I3 | not yet available at audit time | coordinator audits |
| 8 | Round-36 critic | 5 candidates | section 8 |

## 1. Target 1 -- Round 34 B1 as written up by the coordinator

Re-derived by `rerun_b1_r34.py` from `round34/B1-orbits-v3/{sweep_summary_final.json, sweep_summary.json, keep_rows.json, sweep.log, sweep_php.log, sweep_rows.jsonl}`; output `rerun_b1_r34.json`.

**Per-cell table.** All 12 rows of the RESULTS table (N actual, best pmax, register, seed, bar at actual N, bar at 1e6, clears) equal `sweep_summary_final.json` cell by cell (e.g. bash4.2|keyskip2: 81,414 / 7.068 / LP1_REAL / 1354603465 / 8.118 / 9.034 / False). No cell clears; `flagged` and `near_miss` are empty. NO-ERROR-FOUND.

**"Fraction 1.000 both ABIs".** `sweep.log` has 74 progress lines per ABI (printed every 4th chunk), the last being `chunk 296/296` (LP64 t=934 s, ILP32 t=911 s); `sweep_summary.json` phase: `chunks_done` 296 / `chunks_total` 296, `fraction_of_orbit` 1.0, `complete` true for both. 296 x 2^18 = 77,594,624 = 74 x 2^20 (`rerun_b1_r34.json` `chunk_arith`). `seeds_screened` 77,594,624 for both. NO-ERROR-FOUND. (Caveat: `sweep.log` is from the first invocation; the log contains a traceback at `php_tier_a` right after the ILP32 phase, a resumed invocation produced `sweep_php.log`. RESULTS does not mention the crash.)

**Survivor counts / N.** survivors 81,414 (LP64) / 80,985 (ILP32); PHP cells 3,190 / 3,297 / 3,293 / 3,245 = `N_actual`. `seeds_screened` per PHP cell = 2,669,476 = 487 + 47,549 + 2,621,440. 0.00061 = 2,621,440 / 2^32 (0.00061035). NO-ERROR-FOUND.

**Reach arithmetic.** pf_v3 operative power 0.66 (NOVOWEL) / 0.71 (MODERN) x v3 recovery 0.98-1.00 x fraction 1.0 = 0.647-0.66 / 0.696-0.71: RESULTS' "~0.65 / ~0.70" is correct. For the PHP tier (b): x 0.00061 = 0.0004: correct. **But** the PHP prior-dense line "reach = v3 recovery ~0.98-1.00 (no prefilter)" is wrong for 47,549 of 48,036 seeds (1a).

**1a.** `sweep.py:200-212`: `core` seeds go to `decode_seed` directly; `dense` seeds go through `chunk_php` (pf_v3 screen then decode). The RESULTS table says "decoded with no prefilter" for the whole 48,036; the ledger coverage says "(no prefilter)". The `tier_a_seeds` docstring (`sweep.py:~100`) says it: "core = ... decoded unfiltered; dense = ... prefiltered".

**1b. The 38,223 s gap.** `sweep_php.log` verbatim: `php b seeds=1966080 t=110s` then `php b seeds=2621440 t=38223s`. The 4th report is the first one after the sleep; the final block completed at t=38,223 s, then `time.time()-tp < 2100` failed and the loop ended. RESULTS: "shows 2,621,440 seeds at t=110 s and then a 38,223 s gap ... the sweep resumed and closed out cleanly, but tier (b) did not advance past the cap window". The sleep did not "resume"; the wall-clock cap was consumed. Pre-sleep rate 1,966,080 / (110-21) s ~ 22 k seeds/s (17.9 k with the 21 s tier-a offset) -> the cap alone would have given roughly 1 % of 2^32. The claim "0.061 % honest" is honest about what ran, not about what the budget implied; a Round-36 re-run is cheap (~35 min awake).

**1c. The missing bash rows.** Checked directly: `sweep_rows.jsonl` 26,050 data rows, all `kid` prefixed `php:`; none `bash`. Expected unstored bash decodes: 2 x (81,414 + 80,985) = 324,798 (`rerun_b1_r34.json`). R3 (ARMADA-DOCTRINE R3: persist language-agnostic statistics) holds for PHP only. `validate_ledger.py` still passes because the store header is a valid SWEEPROW header and the store is internally valid -- it cannot detect a store that omits half of its declared coverage.

**1d. Header fields.** `rerun_b1_r34.json` `store_header_flags`: `key_space_says_ILP32_stated_fraction` true, `power_EN_NOVOWEL` 0.998. The RESULTS "Coverage x power" text does supersede 0.998 in prose; the field in the store header itself (which downstream readers of the store will see) is not flagged anywhere. Flagged now in the addendum to `round34/B1-orbits-v3/RESULTS.md` and the ledger row.

**Control caveat.** `sweep.py:70-71` (`if any(naive[i] == naive[i+1] ...): continue`) selects doublet-free naive cipher windows; RESULTS discloses it. NO-ERROR-FOUND.

## 2. Target 2 -- I1 (pf_v4)

**Is the plant harness natural-rate?** `I1-skip-tolerant-screen/run.py`: plants are drawn in the loop at lines ~46-60: random testhalves window `st = rng.randrange(0, len(txt)-40)`, enciphered with the real encipherer (`enc1` = `sk.encipher_keyskip`, `enc2` = j+=2 variant with the same 0.83 suppression), then `Cs.append(Cc[:24])` unconditionally. `f` (first skip position) and `dbl` (first doublet) are recorded as covariates and used only to **split** the reported power (`evaluate`: natural / skip_free / with_skip / natural_no_cipher_doublet); nothing is filtered. Calibration vs held-out is by plant index (`i < NPL//2`). NO-ERROR-FOUND: natural-rate. (49-50 % of m=24 heads contain a skip, consistent with R34 X1's 37-51 % at m=18-24.)

**Re-run (`rerun_i1.py`, own seed 777, own plants, frozen thresholds 7.0994 / 7.1761, pen 2, m=24, k=2, OR of both relations):**

| cell (keyskip2 plants, 300, bash LP64) | lane (1000 held-out) | X1 re-run | pf_v3 (m=20, thr 3.9054) on the same plants |
|---|---|---|---|
| EN_NOVOWEL natural | 0.980 | **0.973** (diff 0.7 pt) | 0.730 |
| EN_NOVOWEL with-skip (146 plants) | 0.959 | 0.945 | 0.445 |
| EN_NOVOWEL skip-free | 0.998-1.000 | 1.000 | -- |
| EN_HALFVOWEL natural | 0.949 | **0.970** (+1.7 SE) | 0.643 |
| EN_HALFVOWEL with-skip (163 plants) | 0.920 | 0.957 | 0.356 |

Both cells reproduce within sampling error (lane se ~0.007-0.008, re-run se ~0.01); the screen's gain over pf_v3 (0.73 -> 0.97) is reproduced. NO-ERROR-FOUND.

**k=0 == pf_v3 on 1,000 heads:** `max_abs_diff` 0.0 (`rerun_i1.json` `k0_vs_pfv3_1000`).

**Held-out FPR on fresh seeds (2^16 each, my own seed stream):** bash LP64 57/65,536 = **8.70e-4**; bash ILP32 51/65,536 = **7.78e-4** (lane: 7.8e-4 / 9.2e-4; pooled 8.4e-4). Under 1e-3. NO-ERROR-FOUND.

**(24,1) alternative.** `roc_both.json` `k1|m24|0.001`: NOVOWEL 0.907, min other 0.889 (EN_HALFVOWEL), bar not met, FPR 8.3e-4; `k1|m24|0.003`: 0.922 / 0.902, bar met, FPR 2.6e-3; `k2|m20|0.001`: min other 0.886; frozen `k2|m24|0.001`: 0.98 / 0.948. All equal the numbers in RESULTS "Q5 / cost tradeoff". Throughput ratios (3.5x, 5.8x, 9.1x, 10.9x) equal `throughput.json`. 77.6 M / 56.6 k per s = 22.8 min per ABI. NO-ERROR-FOUND.

**Residual caveats (not errors; stated in lane):** plants use LP64 keystream only; thresholds calibrated on the real C[:24]; one hygiene event (common.py rebinding `HERE` wrote three json into `round32/B1-bash-random`) is described by the lane and confirmed cleaned (no I1 files remain there). X1's own `rerun_i1.py` hit the same trap (wrote into `round32/B1-bash-random/` once; moved back, script fixed).

## 3. Target 3 -- P1 hash chain

- `sha256(data/kjv.txt)` = `0f1a83cbcdc1d3fae6bcc3daaa496d4fa723fcce9526e84e20df12ae33fda986`, 4,436,268 B; `sha256(data/keys/mabinogion.txt)` = `80dc6f0d8efc8398a2d1cc8cdf17237020c881cf4fbd2412dfa37ec8be19a5ed`, 617,362 B -- both equal `round19/I2/out_build.json` (`corpora.EN_KJV`, `corpora.EN_MODERN[1]`). Checked all 11 recorded corpus paths: 10 equal sha and size; `data/keys/welsh/welsh_mabinogion.txt` is 761,030 B sha 624ffc97 (recorded 524,561 B 4b3fd926). NO-ERROR-FOUND on the chain.
- `P1/fetch_log.json`: both `files/10/10-0.txt` and `files/5160/5160-0.txt` fetched `raw` match; I re-fetched both into a temp dir through the new `ensure_r19_corpora()` and got the recorded shas (live Gutenberg still serves them).
- **Welsh recorded as unrecoverable, not "not tried":** `P1/ledger.json` "UNRECOVERED ... six archive.org OCR candidates tried, none match"; RESULTS "NOT FOUND"; ledger row `R35-P1-R19-PANEL-RESTORE` verdict "UNRECOVERABLE (tried, not found)". No document claims the R19 panel was rebuilt (`panel_sha.json`: `rebuilt: null`, `NOT_BUILT`). `._round31_stale_backup` (named in P1's RESULTS as a place to look) holds no panel, welsh or mabinogion file (targeted `find`, that directory only).
- **FOUND-ERROR 3b.** See table row 3b. mtimes: P1 RESULTS 09:30:29; `data/kjv.txt`, `data/keys/mabinogion.txt`, `data/fetch_sources.py` 09:31:13; `handoff/capsule/MANIFEST.json` 09:31:13. Consequence: Round 32's recorded corpus hashes for EN_KJV (0204adae) and EN_MODERN (b2f3dbd3 + e177d7c2, in the R34 B1 store header and `round32/I2` build record) no longer match `data/`; the Round 32 panel itself is unaffected (a pre-built `.npz`), but a rebuild from `data/` would not reproduce it. Substitutes kept in `P1-restore-r19-panel/backup/` (sha verified 0204adae / e177d7c2 / 624ffc97).
- **FOUND-ERROR 3c.** `data/fetch_sources.py` before X1 had `ensure_sources()` (RTKD/relikd transcriptions) and `ensure_welsh_substitute()` only. P1's comment claims the `/files/N/N-0.txt` form is the byte-exact source for KJV/Mabinogion, but the code it was attached to fetches the four Welsh Gutenberg ids. Measured today: for ids 3680/57981/56275/67424 `cache/epub` concatenation (strip as in script) = 761,024 B (sha da02fef6...) vs `/files/N/N-0.txt` = 781,166 B (sha 709d01f1...); recorded substitute 761,030 B / 624ffc97 (6 B off the cache form -- Gutenberg re-issue drift). So P1's edit moved the recipe 20 KB further from the substitute. **Fix applied** to `data/fetch_sources.py`: Welsh URL form restored to cache/epub (comment explains), plus `ensure_r19_corpora()` / `--r19` that fetches the two Round 19 corpora raw and refuses on sha/size mismatch (tested: idempotent on current files; fresh fetch into a temp dir reproduces both shas).
- **Capsule verifier:** `python handoff/capsule/verify_capsule.py` -> `ABSENT 14 / OK 89 / SKIP 1`, final line `PASS`. The manifest's `corpus.kjv` note ("original download restored byte-exact from the /files/N/N-0.txt Gutenberg URL; the Round 32 substitute is no longer on disk") is consistent with the on-disk state once the backup location is added (done via this RESULTS; the manifest note is left as the coordinator wrote it).

## 4. Target 4 -- B2

- Caveat on rows: `B2/ledger.json` `not_covered[2]` "Identity of T2.bin and 2.jpg to the original files is statistical/structural: no full hash was ever recorded", plus the R30-B1 and R30-B2 patch texts ("T2.bin identity rests on size + entropy + chi2 + byte0 and reproduction of the stored XOR rows"; "2.jpg identity rests on the JPEG structural fingerprint and size"). All three are in the applied `LEDGER.json` rows. NO-ERROR-FOUND.
- Staged hashes recomputed: `inputs/T2/T2.bin` 35d31e61...f6db, `inputs/folly/folly.bin` 7e5ec097...c385a, `inputs/jpg/2.jpg` 74e955eb...e34 -- equal `inputs.json`/RESULTS.
- Comparator reproduces stored R30 (from `B2/R30-B1/compare.json` against `round30/B1-blob-crypto/results.json`): **T2^canon fwd entropy 7.1666** (stored 7.1666, results.json:90/138) and **canon^folly rev 7.138** (stored 7.138, :162); also folly^canon rev 7.2487 and folly^canon fwd 7.2106 appear in the stored file. NO-ERROR-FOUND.
- Minor wording: RESULTS says "the 8 canon rows moved by <= 0.015 bits"; `compare.json` has folly^canon:rev bit-identical at 4 d.p. (7.2487 vs 7.2487) while `xor_rows_changed_count` is 8 (rows compared on more than the 4-d.p. entropy). Max move is 0.0141 (canon^folly:rev 7.138 -> 7.1521). Also `comparator_vs_stored.gpg_raw` is `false` in `R30-B2/compare.json` (declared as first-run keybox stderr + random message salt). The control gate printed False in the first promoted R30-B1 run (1/500 false fire, unseeded urandom); disclosed in RESULTS; rerun 0/500.

## 5. Target 5 -- discipline

| lane | PREREG mtime | first non-PREREG artifact | verdict |
|---|---|---|---|
| I1 | 09:29:26.4 | `pf_v4.py` 09:29:48.8; outputs >= 09:33 | OK |
| P1 | 09:28:46.7 | `backup/` 09:28:46.8 (a copy of the substitutes, pre-fetch), `dl_*` >= 09:28:47.3 | OK (0.1 s margin) |
| B2 | 09:29:38.4 | `fetch_try/` 09:30:37.7 | OK |
| I3 | 09:30:07.3 | `feat/*` first 09:30:17.7; **but** `gen.py` 09:29:01.2 (code) and a disclosed 60-draw `THROWAWAY-PILOT` run precede PREREG; PREREG states the pilot, the key is not an R35 key | OK; disclosed |
| B1 (R35, in flight) | 09:38:46.7 | `sweep.py` 09:40:02.4, `control.json` 09:43:45.9, `sweep_rows.jsonl` 09:48:21 | OK (observed; RESULTS absent) |

RESULTS vs JSON: I1 (`roc*.json`, `frozen_op.json`, `power_per_register.json`, `throughput.json`) and B2 (`compare.json`) agree with their RESULTS (sections 2, 4). P1's RESULTS agrees with `fetch_log.json` / `panel_sha.json` except for the stale "untouched" sentence (3b). Vocabulary: lane ledgers use `measured`, `audit`, and P1's free-text `NO-MATCH (panel not rebuilt)` (normalised to `measured`); positive_control values `passed`. No "closed", "exhausted" or "solved" in the R35 lane RESULTS (grepped). I1's RESULTS opens "Status: MEASURED" (vocabulary-conformant). I3 PREREG clause 1 uses a **point estimate** for catch >= 0.90 where the campaign plan asked for Wilson on pooled/each class; the PREREG's own (looser) rule is what the lane will be judged on -- coordinator to hold I3 to the stricter plan reading when it reports.

## 6. Ledger patches applied and gate output

`apply_ledger.py` (idempotent) merged into `LEDGER.json` (195 -> 200 entries):
- new rows: `R35-I1-PFV4-SKIP-TOLERANT-SCREEN` (measured), `R35-P1-R19-PANEL-RESTORE` (measured; NO-MATCH, Welsh corpus recorded unrecoverable), `R35-S1-S2-WINDOW` (never-run, skipped with cause), `R35-B2-PAYLOAD-LEGS` (audit), `R35-X1-REDTEAM` (audit);
- B2 `ledger_patches.json` applied to `R30-B1-BLOB-CRYPTO` and `R30-B2-RSA-GPG` (coverage appended, `not_covered` residuals replaced; identity caveat kept);
- `R34-B1-ORBITS-V3-PFV3`: coverage/notes/not_covered corrected (originals in `coverage_original_r34`), `x1_r35` audit field;
- pointer fields: `R34-I2-NOVOWEL-PREFILTER.r35_i1`; `R27-CPORT-MT32-FULLSWEEP.r35_p1` and `R34-S1-BUILD-BOX.r35_p1` (S2 resume still blocked on the Welsh corpus / panel hash 14a23d36..., recorded sizes 4b3fd926... / 524,561 B; **S2 not resumed**); counts block + note extended.
- B1 (R35) and I3 rows **not** written (not available).

Gate output is in section 9 (filled after the run).

## 7. Not yet available at audit time

- **`round35/B1-bash-orbit-pfv4/`**: directory exists, `RESULTS.md` absent (sweep at `sweep_rows.jsonl` 09:48, `sweep.log` 09:47 when checked). Not audited. Two things for the coordinator to check when it lands, from this audit's findings on R34 B1: (i) that `sweep_rows.jsonl` contains **bash** rows (R34's resume path truncated them), (ii) that the PHP prior-dense tier is not described as unfiltered.
- **`round35/I3-d5c-prereg/`**: `feat/` generation finished for key I3b L=400; `calibrate.py` outputs and `RESULTS.md` absent. Not audited beyond PREREG ordering (section 5).

## 8. Completeness critic -- Round 36 (ranked)

1. **Add the missing registers (Greek, Hebrew, Norse/Old Norse) to the panel and measure power.** Evidence: the nine-register panel has been unchanged since Round 32 (`round32/I2-multiregister-readjudication`), and R6/R7 of the doctrine and R18-L7-A (`round18/L7-redteam/RESULTS.md`, measured power 0.00 for registers outside the scorer) say every uncovered register is a silent hole in **every** negative (including R34-B1 and, once filed, R35-B1). Cost: a corpus + `build_models` + a plant-recovery power row per register; light. Prior: no evidence for a specific language, but instrument-first is the doctrine's own ordering (R1) and it multiplies the value of all finished sweeps.
2. **A Welsh-free route for S2: re-gate the C engine on a NEW panel with a recorded build** (governance change, not a hack: record build inputs, per-model hashes and numpy version; re-derive the self-test vectors V1 64/64 and V2 on the new panel; keep the old gate's failure documented). Evidence: S2 is the highest-prior parked sweep (R27-S2, 44.14 %, `ELIMINATION-LEDGER.md` line ~26); the engine is verified (R34-S1 4/4 resume tests); the only blocker is a gate on a file whose input is unrecoverable (R35-P1). 55.86 % of 2^32 remains. Needs an owner decision (the old panel's hash cannot be reproduced) and a sandbox window.
3. **Close I1's own not_covered cheaply, then re-persist what B1/R34 lost:** (a) measure pf_v4 power on ILP32 and PHP plant keystreams (I1 plants are LP64-only), and heads with >= 3 skips (Poisson on the measured 49-50 % with-skip rate gives P(>=3 in 24) ~3 %; k>=3 is therefore a ~3 % mass, not a priority); (b) re-run the R34 PHP tier (b) awake (~35 min for ~1 % of 2^32, `rerun_b1_r34.json` rate) with pf_v4 and **persist the rows**. Evidence: this audit, sections 1b-1c. Prior: same low PHP prior as R34-B1.
4. **PHP 2^32 tails with pf_v4 on bigger hardware** (R28-L4 queue; 99.94 % of each of four cells). Evidence: `R34-B1` not_covered; rate ~18-22 k seeds/s on this laptop -> ~55-66 h per cell, so only worth it on a multi-core box. Prior: PHP <= 7.0 `mt_rand` has no measured evidence of use (R32-B2); completeness ritual -> queue last of the sweeps.
5. **D5c, conditional on I3's outcome.** If I3 passes every L with the frozen `m_NV = 0.055 L` (including EN_HALFVOWEL argmax), the next step is validation on *real* page-scale decodes (not plants) before any SEAL_PASS flip -- the rule is post-hoc-rounded from four R34 nodes; if I3 fails at any L, stop D5c and record the per-L ceiling. Evidence: `round35/I3-d5c-prereg/PREREG.md` (frozen rule, Wilson criteria), R34-I3 ledger row. Do not plan beyond I3's result.

Weighed and not ranked: the **O1 text-page bisect** (R33-O1, `partially-run`; the LP2 page-0 source is still not in the repo, so there is nothing to bisect; reopens only if a page-0 source surfaces); **heads past 24 runes** (cost is the Viterbi width at 10.9x already; the marginal reach gain is bounded by the 2 % pf_v4 misses, I1 RESULTS).

## 9. Files edited (one-line diff summary each) and gate output

| file | change |
|---|---|
| `LEDGER.json` | +5 rows (R35-I1/P1/S1/B2/X1), B2 patches on R30-B1/R30-B2, R34-B1 corrections, pointer fields on R34-I2 / R27-CPORT / R34-S1, counts block + note (via `analysis/round35/X1-redteam/apply_ledger.py`) |
| `ELIMINATION-LEDGER.md` | line 26 notes S2 resume still blocked; R35-X1 correction block after the R34 section; new "Round 35 (PARTIAL)" section |
| `analysis/README.md` | +1 row for `round35/` |
| `PICKUP-HERE.md` (liber-primus) | +Round 35 (PARTIAL) block above the Round 34 block |
| `../README.md` (repo root) | status line: Round 35 partially filed, panel not rebuilt, S2 parked |
| `data/fetch_sources.py` | Welsh substitute URL form reverted to cache/epub; `ensure_r19_corpora()` + `--r19` added (CRLF preserved) |
| `analysis/round34/B1-orbits-v3/RESULTS.md` | appended "Addendum (Round 35 X1)" with the five corrections |
| `analysis/round35/P1-restore-r19-panel/RESULTS.md` | appended addendum: data/ files were replaced after RESULTS; fetch_sources fix |
| new in `analysis/round35/X1-redteam/` | `RESULTS.md`, `rerun_i1.py/.json`, `rerun_b1_r34.py/.json`, `apply_ledger.py`, `ledger.json` |

**Gate output (run after all edits):**
- `analysis/handoff/validate_ledger.py`: `LEDGER.json 200 entries (recounted from the rows)`, **ERRORS: 0**, WARNINGS: 22 (pre-existing advisory R3/evidence notes; none on R35 or R34-B1 rows), **Unsound negatives: 0**, exit 0.
- `python tests/validate.py`: `ALL VALIDATIONS PASSED - rig reproduces known solves.`
- `python -m pytest tests/ benchmark/ -q`: `24 passed in 10.27s` (with `-m "not network"`: 21 passed, 3 deselected).
- `python handoff/capsule/verify_capsule.py`: ABSENT 14 / OK 89 / SKIP 1, `PASS - every checked item is intact / reachable.`
- CI drift regen (`build_index.py`, `build_problem.py`, `build_knowledge.py`, `build_solved_pages.py`): all wrote their artifacts, all paths resolve, PROBLEM.json n=12,956 doublets=86, SOLVED-PAGES 5 pages.
- `check_consistency.py`: all [ok], `All entry points agree. No document drift detected.`
