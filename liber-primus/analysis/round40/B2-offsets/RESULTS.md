# R40 / B2 RESULTS - key offsets and sign +1 on the bash 4.2 LP64 auto-seed orbit

_2026-10-31. Pre-registered in `PREREG.md` (dated before any output). No git; `LEDGER.json` and `MEASURED-CEILING.md` untouched (patches in `ledger_patches.json`)._

**Verdict: no flagged row, no near-miss in any cell run. Status `partially-run`:** cells (0,+1), (1,-1), (2,-1) swept in full (296/296 chunks), (3,-1) at 143/296 chunks (48.3 %), (28,-1) not run (the ~2.5 h cap bound). Not "closed".

## 1. Alignment statement (how the offset and sign enter)
Let K_raw[i] = `$RANDOM`_i % 29 for the exact stream after `RANDOM=seed` (anti-repeat loop from the seed, last=0). Cell (k, s): ciphertext C[0] is paired with K_raw[k]; decode p = c - K_raw[k+j] (s = -1, repo convention) or p = c + K_raw[k+j] (s = +1). Implemented as an effective keystream K' = K_raw[k:] (s=-1) or (29 - K_raw[k:]) % 29 (s=+1), fed unchanged to the pf_v4_12 head Viterbi and to beam_v3 (sign -1, key-skip advance 1/2 moving the index forward from there). In the vectorised screen the heads are generated over m+k steps (anti-repeat not applied, as in R32/R37), the first k rows are dropped and, for s=+1, negated mod 29 BEFORE the Viterbi. Verified (`wrapcheck.json`): wrapper at (0,-1) equals R37's heads exactly; for every cell the screen heads equal the exact stream (300 seeds x 28 values, 0 mismatches). Plants are enciphered from the TRUE K_raw[k:] with the TRUE sign (`encipher_keyskip(sign=s)` / `enc_pair_s`), independently of the negation shortcut.

## 2. Controls (before any orbit; `control_<cell>.json`, `control_gates.json`)
40 natural-rate plants per cell (10 EN_MODERN + 10 EN_NOVOWEL per relation), real 2^16-seed chunk path, N=1e6 bars at L120 and L240, recovery >= 0.90. Gate = >= 3 recoveries in every register x skip split (pooled over relations): **passed in all five cells**.

| cell | recovered / plants | prefilter pass | smallest split n (recovered) |
|---|---|---|---|
| (0,+1) | 39/40 | 39 | EN_NOVOWEL skip-free 7 (7) |
| (1,-1) | 40/40 | 40 | EN_MODERN with-skip 7 (7) |
| (2,-1) | 39/40 | 39 | EN_NOVOWEL with-skip 8 (8) |
| (3,-1) | 40/40 | 40 | EN_MODERN skip-free 7 (7) |
| (28,-1) | 40/40 | 40 | EN_MODERN with-skip 8 (8) |

(The one miss in (0,+1) and (2,-1) each is a plant that failed the prefilter/gate: EN_NOVOWEL with-skip and EN_MODERN skip-free respectively.) Controls cover EN_MODERN and EN_NOVOWEL only; other registers are the instrument's measured reach (0.952-0.994, R37-I2) and were not re-planted.

**Misaligned negative control** (`control_misaligned_o1_sm.json`, 20 offset-1 plants screened at offset 0, i.e. the instrument every earlier orbit sweep used): 16/20 pass pf_v4_12, **6/20 recover end to end** (skip-free 6/13, with-skip heads 0/7). So offset 1 was not completely invisible to the earlier offset-0 sweeps (the skip tolerance absorbs a one-step shift in part), but reach at offset 1 was roughly 0.3, not 0.95-0.99. n is small. Offset 2/3/28 were not measured this way.

## 3. Sweeps (`sweep_rows.jsonl`, 455,264 14-field rows + header; `sweep_summary.json`; `sweep_progress.json`)
Bars: `null12.json` POT at actual N and N=1e6. Survivor-rate checkpoint after 30 chunks within [0.5x, 2x] of R37's 222/chunk: passed in every cell (216-225/chunk).

| cell | chunks | seeds | survivors | keyskip1 best vs bar (actual N / 1e6) | keyskip2 best vs bar (actual N / 1e6) | flagged | near-miss |
|---|---|---|---|---|---|---|---|
| (0,+1) | 296/296 | 77,594,624 | 65,314 | 6.557 (s1351506977, LP1_REAL) vs 8.110 / 9.102 | 6.588 (s1360905550, EN_KJV) vs 8.024 / 8.999 | 0 | 0 |
| (1,-1) | 296/296 | 77,594,624 | 65,229 | 6.831 (s1329866581, LP1_REAL) vs 8.109 / 9.102 | 6.713 (s1364795802, LP1_REAL) vs 8.024 / 8.999 | 0 | 0 |
| (2,-1) | 296/296 | 77,594,624 | 65,358 | 6.794 (s1399396022, LP1_REAL) vs 8.110 / 9.102 | 6.696 (s1393579878, EN_HALFVOWEL) vs 8.024 / 8.999 | 0 | 0 |
| (3,-1) | **143/296** (48.3 %) | 37,486,592 | 31,731 | 6.348 (s1360556499, CY) vs 7.847 / 9.102 | 6.332 (s1370298412, EN_HALFVOWEL) vs 7.766 / 8.999 | 0 | 0 |
| (28,-1) | 0/296 (control only) | - | - | not run | not run | - | - |

No survivor reached the L=120 screen bar at actual N, so no L=240 gate decode was needed. Seeds 1354603465 (the known near-miss at offset 0, sign -1) is not a feature of these cells. Wall per full cell 2,150-2,720 s (shared machine). `AD.validate_store` ok; `check_r3_store` `[]`.

## 4. Deferred remainder (stated fraction)
Offset x sign axis = 29 offsets (0-28) x 2 signs = 58 cells. Done before: 1 ((0,-1), R37-I2). Here: 3 full + 0.48 of a cell = 3.48 cells (6.0 % of the axis; 7.7 % with R37-I2). **Untouched: 53 cells (91.4 %)**: offset 28 and offsets 4-27 at sign -1 (25 cells), offsets 1-28 at sign +1 (28 cells), plus the second half of (3,-1). The brief's "5 of 58" was the plan; actual completion is 3.48 of 5. ILP32 was not run at any offset (the plan's orbit is LP64).

## 5. Three conditionals
1. **Key space**: bash 4.2 LP64 auto-seed orbit (74 x 2^20 seeds), `%29`, at the listed (offset, sign) cells only.
2. **Transition model**: keyskip1 + keyskip2 under beam_v3 panel_max; heads with <= 2 skips in 24 runes screened (>= 3 unscreened, est. ~3 % of true-key mass); not `free`; not L=31.
3. **Register**: panel-R36's twelve; reach 0.952-0.994 (R37-I2 instrument) x v3 recovery (this lane: 198/200 plants, EN_MODERN and EN_NOVOWEL only).

## 6. not_covered
Offset 28 (sign -1; control passed 40/40, no sweep); the other half of offset 3; offsets 4-27 at sign -1; every offset 1-28 at sign +1; ILP32 at any offset; offsets > 28; an offset that is nondeterministic (depends on shell activity before the first `$RANDOM` read); heads with >= 3 skips; the free relation; registers outside the twelve; plants cover two registers only.

## 7. Notes for the coordinator
- The misaligned control (section 2) is a new measured fact for `MEASURED-CEILING`: earlier offset-0 orbit negatives had partial (~0.3) reach at offset 1; this should temper any statement that offset 1 was "never seen".
- Decide whether to run (28,-1) and the remaining cells (~36 min each on this machine when B3 is not competing), or ILP32 at the same cells.

## 8. Files
`PREREG.md`, `sweep.py`, `mk_ledger.py`, `wrapcheck.json`, `control_{o0_sp,o1_sm,o2_sm,o3_sm,o28_sm}.json`, `control_misaligned_o1_sm.json`, `control_gates.json`, `control.log`, `run.log`, `sweep_rows.jsonl`, `sweep_progress.json`, `sweep_summary.json`, `keep_rows.json`, `ledger.json`, `ledger_patches.json`.
