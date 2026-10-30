# Round 37 / I2 - pf_v4 recalibrated on twelve registers; bash orbit re-screened: RESULTS
Pre-registered in `PREREG.md` (13:25, before any code ran). One Python process at a time; RAM waits honoured. The first sweep start was aborted at 56 chunks and restarted with a larger time cap (log kept as `sweep_aborted_first_start.log`; nothing from it is used). No git. Lane wall ~1 h 50 min.

## Verdict
**NEGATIVE (bounded, construction-conditional).** The twelve-register screen lifts HEBREW from 0.68 to 0.98, NORSE from 0.64 to 0.98 and GREEK from 0.91 to 0.985; every one of the 12 registers is >= 0.95 at the frozen point. Both ABIs were screened in FULL (296/296 chunks, 77,594,624 seeds each) and all 131,786 survivors were decoded under both relations: 0 rows clear the 12-register bar at actual N, 0 flagged-for-oracle, 0 near-miss. Best row anywhere is the recurring seed 1354603465 (LP64 keyskip2, 7.065, LP1_REAL), 0.96 below the actual-N bar. Nothing certified.

## 1. pf_v4_12 and the frozen point (`roc12.json`, `roc12_null.json`, `frozen_op12.json`)
`pf_v4_12.py` = pf_v4's Viterbi (m=24, k=2, pen 2 nats/skip, relations keyskip1 / keyskip2) with the final lse over the twelve panel-R36 LMs (sha a0682f0c...; asserted at import). Its per-column plant path `dp_cols` equals `dp_regs` exactly (max diff 0.0).
Calibration: 2^19 wrong-key heads per ABI (bash4.2 LP64, bash4.2_i32), keys random from the 74-prefix space, scored against the real LP2 head C[:24]; random 50/50 calibration / held-out split (seed 3701). Thresholds taken on the calibration half.
- **Frozen point: per-relation FPR 5e-4: thr keyskip1 = 7.4155, keyskip2 = 7.4412 (nats).** Total (OR) FPR: calibration 8.8e-4, **held-out 8.9e-4** (Wilson 95% 8.0e-4..1.0e-3); per ABI held-out 9.0e-4 (LP64) / 8.7e-4 (ILP32). Target 1e-3 total met. (R35's nine-register point: 7.099 / 7.176, held-out 8.4e-4.)
- ROC (per-relation FPR -> total held-out FPR -> min power over the 12 registers): 2.5e-4 -> 4.1e-4 -> 0.934; **5e-4 -> 8.9e-4 -> 0.952**; 1e-3 -> 1.7e-3 -> 0.963; 2e-3 -> 3.3e-3 -> 0.971; 5e-3 -> 8.2e-3 -> 0.977; 1e-2 -> 1.65e-2 -> 0.984. The minimum is EN_HALFVOWEL throughout.
- PHP cells: FPR NOT re-measured (not run). Only the two bash ABIs set the thresholds; PHP tiers keep their Round 34/36 statements.

## 2. Natural-rate power x12 at the frozen point (`power12_per_register.json`)
500 plants per register per relation (1000 per register, ABI alternating 250/250), text from held-out `testhalves-r36`, real `sk.encipher_keyskip` (keyskip1) / pair encipherer (keyskip2), supp 0.83, only filter = realised C[:40] doublet-free, NO skip-free selection. A plant passes if either relation's threshold is exceeded. "with-skip" = a skip altered any of the first 24 enciphered runes. Wilson 95% on the natural column.

| register | pf_v4_12 natural [Wilson] | skip-free (n) | with-skip (n) | ks1 / ks2 plants | R35 nine-reg (ks1/ks2) | R36 nine-reg measured |
|---|---|---|---|---|---|---|
| EN_MODERN | 0.985 [0.975, 0.991] | 1.000 (494) | 0.970 (506) | 0.978 / 0.992 | 0.984 / 0.981 | - |
| EN_KJV | 0.989 [0.980, 0.994] | 1.000 (515) | 0.977 (485) | 0.992 / 0.986 | 0.988 / 0.987 | - |
| LP1_REAL | 0.994 [0.987, 0.997] | 1.000 (503) | 0.988 (497) | 0.992 / 0.996 | 0.991 / 0.994 | - |
| LATIN | 0.967 [0.954, 0.976] | 0.983 (521) | 0.950 (479) | 0.966 / 0.968 | 0.972 / 0.975 | - |
| OE | 0.970 [0.958, 0.979] | 0.994 (527) | 0.943 (473) | 0.974 / 0.966 | 0.977 / 0.965 | - |
| DE | 0.984 [0.974, 0.990] | 0.998 (502) | 0.970 (498) | 0.982 / 0.986 | 0.985 / 0.987 | - |
| CY | 0.972 [0.960, 0.981] | 0.998 (527) | 0.943 (473) | 0.978 / 0.966 | 0.976 / 0.978 | - |
| EN_HALFVOWEL | 0.952 [0.937, 0.964] | 0.981 (485) | 0.924 (515) | 0.952 / 0.952 | 0.948 / 0.949 | - |
| **EN_NOVOWEL** | **0.985 [0.975, 0.991]** | 1.000 (513) | 0.969 (487) | 0.978 / 0.992 | 0.982 / 0.980 | - |
| GREEK | 0.985 [0.975, 0.991] | 1.000 (563) | 0.966 (437) | 0.992 / 0.978 | not measured | 0.91 (n=100) |
| **HEBREW** | **0.982 [0.972, 0.989]** | 1.000 (550) | 0.960 (450) | 0.988 / 0.976 | not measured | **0.68** (n=100) |
| **NORSE** | **0.981 [0.971, 0.988]** | 0.998 (523) | 0.962 (477) | 0.982 / 0.980 | not measured | **0.64** (n=100) |

**Requirement met: every register >= 0.85 (min 0.952, EN_HALFVOWEL).** The Q5 fallback (best curve / higher-FPR operating point) was therefore not needed; the ROC above is the curve. LP64 vs ILP32 plant power agrees within sampling (HEBREW 0.978 / 0.986; EN_HALFVOWEL 0.960 / 0.944; per-ABI numbers in `power12_per_register.json`). The gain on the new registers comes from the lse now containing a model of them; the nine-register screen was blind to them. No re-tuning on the orbit; pen=2, k=2, m=24 kept from R35.

## 3. Throughput (`throughput.json`)
2^18 bash4.2 seeds, both relations incl. keystream heads, two interleaved repeats each: pf_v4 (9 reg) 5.2 s (~50,000 seeds/s); pf_v4_12 6.2-7.3 s (~36,000-42,500 seeds/s). **pf_v4_12 costs 1.28x pf_v4.** Real sweep wall (incl. decodes, with other lanes contending): LP64 3,126 s, ILP32 2,194 s.

## 4. Natural-rate control through the real chunk path (`control.json`; gate run BEFORE the sweep)
pf_v4_12 frozen on a 2^16-seed chunk -> v3 L=120 (both relations, all survivors) under panel-R36 -> v3 L=240 -> adjudication. 10 plants each of EN_MODERN, EN_NOVOWEL, HEBREW, NORSE per ABI x relation = 160 plants; real encipherers; only filter C[:40] doublet-free; no skip-free selection. pass = prefilter AND pmax120 and pmax240 >= 12-register N=1e6 bars (9.102 / 8.999 at L=120; 8.978 / 9.282 at L=240); recover = pass AND L240 recovery >= 0.90. Pooled over 2 ABIs x 2 relations (n / prefilter / recover):

| register | skip-free | with-skip (head 24) |
|---|---|---|
| EN_MODERN | 17 / 17 / 17 | 23 / 22 / 22 |
| EN_NOVOWEL | 22 / 22 / 22 | 18 / 17 / 17 |
| HEBREW | 18 / 18 / 18 | 22 / 20 / 20 |
| NORSE | 21 / 21 / 21 | 19 / 18 / 18 |

Skip split: 82 of 160 plants (51%) have a skip in the head 24. Gate (>= 3 recoveries in every register x split, pooled): **PASSED** (minimum 17). Every plant that passed the prefilter passed both bars and recovered (155/155). The 5 misses are all prefilter misses on with-skip plants (EN_MODERN 1, NOVOWEL 1, HEBREW 2, NORSE 1), consistent with with-skip power 0.96-0.97. Per-ABI x relation x register x split counts are in `control.json` (`per_abi_rel`). The R35 coordinator question (a per-cell 100% with-skip NOVOWEL guarantee) is unchanged: 1 NOVOWEL with-skip screen miss in 18, not a harness defect.

## 5. Sweep (`sweep_rows.jsonl`, `sweep_summary.json`, `sweep_summary_final.json`)
| ABI | seeds screened | fraction of orbit | pf_v4_12 survivors | survivor rate | v3 L=120 decodes | rows |
|---|---:|---:|---:|---:|---:|---:|
| bash 4.2 LP64 | 77,594,624 | **1.000 (296/296)** | 65,815 | 8.48e-4 | 65,815 x 2 relations | 131,630 |
| bash 4.2 ILP32 | 77,594,624 | **1.000 (296/296)** | 65,971 | 8.50e-4 | 65,971 x 2 | 131,942 |
Survivor counts are 0.95x Round 35's (69,017 / 69,104), i.e. near R35's as expected from a screen frozen at about the same total FPR. The store holds 263,572 rows plus the header.

## 6. Best pmax vs bars (L=120; 12-register POT bars from `null12.json` mu/beta: bar = mu + beta ln(N / -ln 0.99))
| ABI | relation | N actual | best pmax (register, seed) | bar @ actual N | bar @ N=1e6 | clears |
|---|---|---:|---|---:|---:|---|
| LP64 | keyskip1 | 65,815 | 6.347 (LP1_REAL, 1368828634) | 8.113 | 9.102 | no |
| LP64 | keyskip2 | 65,815 | **7.065** (LP1_REAL, 1354603465) | 8.027 | 8.999 | no |
| ILP32 | keyskip1 | 65,971 | 6.506 (EN_KJV, 1338600942) | 8.114 | 9.102 | no |
| ILP32 | keyskip2 | 65,971 | 6.763 (LP1_REAL, 1354603465) | 8.028 | 8.999 | no |
These equal the R36 B1 12-register re-decode of the R35 survivors (6.347 / 7.065 / 6.506 / 6.763): the leading rows are shared, so the 12-register screen exposed no new top row. R36's null12 bars at its own N (69,017) were 8.130 / 8.044. Top-5 per cell are in `sweep_summary_final.json`.

## 7. Flagged / near-miss
Flagged-for-oracle: **none**. Near-miss (clears actual-N, not N=1e6): **none**. No L=240 screen was triggered (nothing at or above the actual-N bar), so no `HUMAN-ORACLE.md` bundle. Seed 1354603465 (keyskip2) is again the highest row (7.065 / 6.763), 0.96-1.27 below the bar.

## 8. Store
`sweep_rows.jsonl`: header names `panel_sha256` (a0682f0c...), `register_panel`, the 12 `registers`, and a `prefilter` block with the pf_v4_12 frozen point; rows are 12-wide. Stock `AD.validate_store` -> ok; stock `check_r3_store` -> `[]` (see `finalize.log`).

## 9. Per-register reach (orbit coverage x pf_v4_12 natural power x v3 recovery)
Coverage = 1.000 for both ABIs. v3 recovery on prefilter-passers: 155/155 in this lane's four-register control (EN_MODERN, EN_NOVOWEL, HEBREW, NORSE; Wilson lower ~0.98); GREEK 16/16 and HEBREW/NORSE 16/16 each in R36 stage 2; the other seven registers' recovery is assumed 1.00 from pooled controls, not measured here.
| register | power | v3 recovery | reach |
|---|---|---|---|
| EN_MODERN | 0.985 | 1.00 | 0.985 |
| EN_KJV | 0.989 | 1.00 (assumed) | 0.989 |
| LP1_REAL | 0.994 | 1.00 (assumed) | 0.994 |
| LATIN | 0.967 | 1.00 (assumed) | 0.967 |
| OE | 0.970 | 1.00 (assumed) | 0.970 |
| DE | 0.984 | 1.00 (assumed) | 0.984 |
| CY | 0.972 | 1.00 (assumed) | 0.972 |
| EN_HALFVOWEL | 0.952 | 1.00 (assumed) | 0.952 |
| EN_NOVOWEL | 0.985 | 1.00 | 0.985 |
| GREEK | 0.985 | 1.00 (R36 16/16) | 0.985 |
| HEBREW | 0.982 | 1.00 | 0.982 |
| NORSE | 0.981 | 1.00 | 0.981 |
Versus R36 B1: GREEK 0.91 -> 0.985, HEBREW 0.68 -> 0.98, NORSE 0.64 -> 0.98. These are reach for a key that lives in the orbit with <= 2 skips in the first 24 runes; they say nothing about whether the key is there.

## 10. Three conditionals
1. Key space: bash 4.2 auto-seed orbit (74 x 2^20 seeds, LP64 and ILP32, both complete), %29, offset 0, sign -1, C[0]-aligned.
2. Transition model: keyskip1 + keyskip2 under beam_v3 panel_max, L=120 screen; the screen is pf_v4_12 (heads with <= 2 skips in 24 runes). Not `free`, not L=31.
3. Register: panel-R36's twelve (GREEK/HEBREW/NORSE as romanised in R36 P1); reach per register as tabulated.

## not_covered
Heads with >= 3 skips in 24 runes; the `free` relation (its L-matched bar is I1's); L=31; offsets != 0; other reductions, bash versions, seedings; other PRNGs and the PHP tiers (PHP FPR under the 12-register point NOT measured); registers outside the twelve and unpointed Hebrew / other orthographies; thresholds are calibrated to the real C[:24] head; power plants use `testhalves-r36` text and the repo's encipherers (supp 0.83); v3 recovery for seven registers assumed; bars at actual N scale from R36's stored POT fit (L=240 from 4,000 draws, +-0.3), no new null drawn here; the control's with-skip label misses skips landing on an identical key rune (~1/29); control n=10 per cell.
Reopens if: the oracle clears a flagged row (none), a true-key head with > 2 skips in 24 runes is shown, or a register outside the twelve is added.
