# Round 36 / B1 - the Round 35 bash orbit re-adjudicated under 12 registers: RESULTS
Pre-registered in `PREREG.md` (dated 11:56, before any code ran). One Python process at a time, nproc=1, streamed append-mode; stages `null` (26 min, incl. RAM waits) -> `control` -> `pfpower` -> `run` (31 min) -> `final`. No git. Panel-R36 = `round36/P1-panel-r36/build1/panel12.npz` (sha256 `a0682f0c...bbe6c`, asserted at load), held-out text `testhalves12.npz`.

## Verdict
**NEGATIVE (bounded, construction-conditional).** All 276,242 persisted rows were re-decoded (fraction 1.000) and read by 12 registers: 0 rows clear the 12-register bar at actual N, 0 flagged-for-oracle, 0 near-miss. Best row anywhere is the recurring LP64 keyskip2 seed 1354603465 (pmax 7.065, LP1_REAL) against a bar of 8.044. The three new registers add nothing: their best z over the whole orbit is 6.14 (HEBREW), 6.08 (NORSE), 5.88 (GREEK). Nothing certified. The main new finding is about the instrument, not the key: **pf_v4's measured natural power on HEBREW (~0.68) and NORSE (~0.64) is far below its 0.95-0.99 on the nine original registers**, so the orbit's coverage for those two registers is limited by the screen, not by the decoder or the panel.

## 1. Did the rows hold text? No - re-decoded in full
SWEEPROW rows store statistics only (`kid`, n, en, pmax, ... 9-wide z), not the decode. So the survivor seeds were re-decoded: unit = (ABI, seed), both relations, `beam_decode_v3` panel_max (lam_u=4, beam_w=400) with `PANEL_PATH`/`_PAN`/`AD._PANEL` repointed to panel-R36 in-process, L=120 on LP2[:120]. Universe 138,121 units (69,017 LP64 + 69,104 ILP32; both relation sets cover the same seeds) = 276,242 rows. Order `Random(3301)` shuffle; **completed 138,121/138,121 units in 1,875 s (73.7 units/s), fraction = 1.000**, so no sampling. Same universe as the 276,242 R35 rows (matches the 276,243 lines less the header).

## 2. Controls (`control.json`)
**Stage-2 planted keys, new registers** (v3 with the true key handed over, real `enc_exact`/`enc_pair`, keys = R35 survivor seeds alternating ABI, held-out text from `testhalves12`, 8 per relation per register; pass = pmax120 >= 12-register declared-N (1e6) bar AND pmax240 >= its L=240 bar AND recovery240 >= 0.90):

| register | keyskip1 | keyskip2 | pooled recover | own-register argmax | min pmax120 (bar 9.10 / 9.00) |
|---|---|---|---|---|---|
| GREEK | 8/8 | 8/8 | **16/16** | 16/16 | 17.93 |
| HEBREW | 8/8 | 8/8 | **16/16** | 16/16 | 16.64 |
| NORSE | 8/8 | 8/8 | **16/16** | 16/16 | 16.43 |

(20 of the 48 plants have a skip in the head 24 runes.) Gate (>=5 each) passed. Caveat: `recovery120` in `control.json` is a diagnostic bug of mine (a 120-rune decode scored against the 240-rune plaintext, so it reads 0); it is not used in any pass/recover decision, which use the L=240 recovery. Stage 2 is the key-handed path; it measures what the decoder + panel can do once a seed survives the screen, not screen power.

**Round 35 B1 natural-rate control re-scored under panel-R36** (same RNG and plant rule, 96 natural-rate EN_MODERN/EN_NOVOWEL plants; pf_v4 on its frozen 9-register LMT; v3 + bars under panel-R36, bars = 12-register N=1e6): pooled recover EN_MODERN skip-free 23/23, with-skip 24/25 (24/24 of prefilter passers); EN_NOVOWEL skip-free 28/28, with-skip 18/20 (18/18 of passers). Identical counts to Round 35 (same 3 prefilter misses); v3 recovery on prefilter-passers 93/93. **Gate PASSED, still passes under 12 registers.** (Plants regenerate from `testhalves12`, not R32 `testhalves`; counts coincide.) The R35 coordinator decision point about 2/20 NOVOWEL with-skip screen misses is unchanged.

## 3. 12-register null and bars (`null12.json`, `null12_stream.jsonl`)
Shuffled real LP2, wrong key (R35 survivor seeds, ABI alternating), both relations per draw, panel-R36 pmax. L=120: **25,000 draws** (>=20,000 required); L=240: 4,000 draws (needed for the L=240 gate bar). POT exponential tail above the empirical 90th percentile (round34 `fit.tailfit`), `bar = mu + beta ln(N/-ln 0.99)`, beta from the node at its own L (no power-law-in-L interpolation: only L=120 and 240 were drawn).

| L / relation | null mean | emp max | 12-reg bar N=69,017 | 12-reg bar N=1e6 | 9-reg bar_v3 same N | 9-reg bar_v3 N=1e6 |
|---|---|---|---|---|---|---|
| 120 keyskip1 | 2.332 | 5.586 | 8.130 | **9.102** | 8.221 | 9.235 |
| 120 keyskip2 | 2.341 | 5.624 | 8.044 | **8.999** | 8.058 | 9.034 |
| 240 keyskip1 | 3.056 | 5.578 | 8.140 | 8.978 | 8.572 | 9.514 |
| 240 keyskip2 | 3.072 | 5.415 | 8.389 | 9.282 | 8.262 | 9.150 |

Each new register wins the null argmax 8-10% of the time (~uniform over 12). **The 12-register bars do not rise relative to the 9-register `bar_v3` bars; at L=120 they are 0.01-0.13 lower.** This is a fit/sample difference (different draws, direct-node beta vs R34's power law, 25k vs 40k draws), not evidence that adding registers lowers the family-wise bar; I1's gate-beam null moved the bar up by 0.02-0.07. The verdict does not depend on it (best 7.065 vs 8.04-8.13). L=240 bars (n=4,000) are noisier (k=400 tail points): treat +-0.3. Declared-N=1e6 is the near-miss reference as in R35.

## 4. Per ABI x relation: best vs bars (12-register, L=120, rows re-decoded)
| ABI | relation | N | best pmax (register, seed) | bar12 actual N | bar12 N=1e6 | bar9 actual N / 1e6 | clears |
|---|---|---:|---|---:|---:|---|---|
| LP64 | keyskip1 | 69,017 | 6.347 (LP1_REAL, 1368828634) | 8.130 | 9.102 | 8.221 / 9.235 | no |
| LP64 | keyskip2 | 69,017 | **7.065** (LP1_REAL, 1354603465) | 8.044 | 8.999 | 8.058 / 9.034 | no |
| ILP32 | keyskip1 | 69,104 | 6.506 (EN_KJV, 1338600942) | 8.130 | 9.102 | 8.222 / 9.235 | no |
| ILP32 | keyskip2 | 69,104 | 6.763 (LP1_REAL, 1354603465) | 8.044 | 8.999 | 8.059 / 9.034 | no |

R35 nine-register bests were 6.349 / 7.068 / 6.679 / 6.762; the re-decode under panel-R36 reproduces them to within 0.003 for three cells (the ILP32 keyskip1 best moved from 6.679 EN_HALFVOWEL to 6.506, because the decoded text depends on the panel through the beam's `panel_max` hooks and is not identical to R35's). Best z per register over the orbit (max over all 276k rows; full per-cell table in `readjud_summary.json`): GREEK 5.88, HEBREW 6.14, NORSE 6.08 (max over cells) against LP1_REAL 7.07 and EN_HALFVOWEL 6.50. Argmax shares per cell are ~uniform (GREEK 7.3%, HEBREW 6.7%, NORSE 7.6%). Top-8 per cell in the summary.

## 5. Flagged / near-miss
**Flagged-for-oracle: none. Near-miss (clears actual-N but not declared-N): none. No L=240 re-screen was triggered** (nothing at or above the actual-N bar). The seed 1354603465 near-miss from R32/R33/R34/R35 reappears at 7.065 / 6.763, 1.0-1.3 below the bar again; under the 12 registers its argmax is still LP1_REAL. Oracle / verifier steps are the coordinator's.

## 6. Per-register reach (coverage x pf_v4 natural power x v3 recovery)
Coverage = 1.000 (full re-decode of every pf_v4 survivor; and the orbit itself was swept in full in R35). v3 recovery on prefilter-passers: 93/93 in the natural-rate control for EN_MODERN/EN_NOVOWEL; 16/16 per new register in stage 2 (lower bounds only, Wilson 0.81 at n=16). pf_v4 power: nine registers from `round35/I1-skip-tolerant-screen/power_per_register.json` (2000 plants, frozen point); **three new registers MEASURED HERE** (`pfpower_new.json`, 100 natural-rate plants each, 50 per relation, ABI mixed; calibration EN_MODERN 100/100 vs recorded 0.98; binomial s.e. about 0.05 on the new values; screen applied to the single plant seed with the absolute frozen thresholds, equivalent to the chunk path).

| register | pf_v4 power ks1 / ks2 | v3 recovery | reach (orbit, a key that lives in it) |
|---|---|---|---|
| EN_MODERN | 0.984 / 0.981 | 1.00 | 0.98 |
| EN_KJV | 0.988 / 0.987 | 1.00 (assumed from pooled) | 0.99 |
| LP1_REAL | 0.991 / 0.994 | 1.00 (assumed) | 0.99 |
| LATIN | 0.972 / 0.975 | 1.00 (assumed) | 0.97 |
| OE | 0.977 / 0.965 | 1.00 (assumed) | 0.97 |
| DE | 0.985 / 0.987 | 1.00 (assumed) | 0.99 |
| CY | 0.976 / 0.978 | 1.00 (assumed) | 0.98 |
| EN_HALFVOWEL | 0.948 / 0.949 | 1.00 (assumed) | 0.95 |
| EN_NOVOWEL | 0.982 / 0.980 | 1.00 | 0.98 |
| **GREEK** | 0.88 / 0.94 (measured, n=50 each) | 1.00 (16/16) | **0.91** |
| **HEBREW** | 0.66 / 0.70 (measured) | 1.00 (16/16) | **0.68** |
| **NORSE** | 0.66 / 0.62 (measured) | 1.00 (16/16) | **0.64** |

The seven EN-family/Latin/OE/DE/CY "assumed" recoveries carry over from R35's pooled control (only EN_MODERN and EN_NOVOWEL were planted in the chunk path there; the 12-panel re-score changes none of its numbers). Hebrew and Norse reach is ~0.65-0.70: roughly a third of keys that decode to those registers would have been discarded by the frozen 9-register-calibrated prefilter before ever reaching the 12-register panel. The panel and decoder are not the bottleneck for them (stage 2: 16/16 with pmax 16-19 vs bars ~9). Re-calibrating pf_v4's thresholds with the three registers in its log-sum-exp (not done: it would change the frozen FPR and the orbit survivor set) is the lever; that is a coordinator decision.

## 7. Store validation (`readjud_rows.jsonl`)
276,242 rows + header; header `registers` = the 12 names, `panel_sha256` = panel-R36, `n_registers`=12, `panel_build` names the P1 build. `AD.header` was called with `pan=PAN` and the extra fields overridden (its `out_build.json` and `corpora_sha256` read the stale R32 nine-register build, so `corpora_sha256` is a pointer to `P1/inputs_r36.json`). Row z is 12-wide (`AD.to_row` takes `len(res["z"])`). **Validation:** `AD.validate_row(row, hdr, n_registers=12)` over all 276,242 rows: pass (local `validate12`). The stock `AD.validate_store(path)` and therefore `handoff/validate_ledger.check_r3_store` FAIL on this store (they default `n_registers=9` and reject the 12-vector - this is the "z must be a 9-vector" error, and is a validator limitation, not a data defect). `check_r3_store_local12` (the same header/R3-column test without the 9-wide validator) -> `[]`. **CI impact for the coordinator:** a ledger entry pointing `sweep_store` at this file will trip the R3 check in `validate_ledger.py` until `validate_store` reads the register count from the header (a one-line change in `round19/I2/adjudicate.py` / `round32/I2`; not made here since I write only under my lane). The ledger row below therefore names the store in `evidence`/`sweep_store_note` and flags this.

## 8. Three conditionals (Doctrine Q4)
1. **Key space:** the 138,121 pf_v4 survivor seeds of the bash 4.2 LP64 + ILP32 auto-seed orbit (R35 B1: 74 x 2^20 seeds each, full), %29, offset 0, sign -1, C[0]-aligned. The prefilter is the frozen nine-register pf_v4 (not re-run); orbit coverage for GREEK/HEBREW/NORSE is capped by pf_v4 power 0.91/0.68/0.64.
2. **Transition model:** keyskip1 + keyskip2 under beam_v3 panel_max, L=120 screen / L=240 gate, heads with <= 2 skips in 24 runes (pf_v4); not `free`, not L=31.
3. **Adjudicator register:** panel-R36, 12 registers (new three only as written by I1's romanisations: pointed-Hebrew with vowels from niqqud, Nestle 1904 Greek, normalised Old Norse; CY is a modern-Welsh substitute). 12-register bars from a 25,000-draw L=120 null (4,000 at L=240).

## not_covered
PHP tiers (not re-run; Round 34 stands); heads with >= 3 skips in 24 runes; `free` relation; L=31; offsets != 0; other reductions; other bash versions/seedings; pf_v4 power for the three new registers measured at n=50 per relation on LP64+ILP32-mixed natural plants (not the 2000-plant R35 protocol); pf_v4 thresholds not recalibrated for 12 registers; v3 recovery of the seven non-planted existing registers assumed from the pooled control; L=240 bars from only 4,000 null draws; L=400 not run; unpointed Hebrew, other Greek/Norse orthographies, other scripts; `recovery120` diagnostic field in control.json is invalid. Reopens if: the oracle clears a flagged row (none), a true-key head with > 2 skips in 24 runes is shown, or pf_v4 is recalibrated for the 12-register panel and the orbit re-screened for HEBREW/NORSE.

## Files
`PREREG.md`, `readjud.py`, `driver.sh`, `control.json`, `null12.json`, `null12_stream.jsonl`, `pfpower_new.json`, `readjud_rows.jsonl` (276,242 rows + header), `run_state.json`, `readjud_summary.json`, `readjud.log` (+ `*.out`), `ledger.json`, `ledger_patches.json`, `RESULTS.md`.
