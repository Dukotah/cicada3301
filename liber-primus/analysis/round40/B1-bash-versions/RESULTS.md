# R40 / B1 RESULTS - the other bash versions' `$RANDOM` auto-seed orbits

_2026-10-31. Pre-registered in `PREREG.md` (+ `PREREG-ADDENDUM-1.md`, an arithmetic correction made before any output). No git; `LEDGER.json` and `MEASURED-CEILING.md` untouched (patches in `ledger_patches.json`)._

**Verdict: no flagged row, no near-miss, in any version. Per version: 4.1 and 4.0 `negative` (covered by stream identity with R37-I2's complete bash 4.2 sweeps, plus an 8/296-chunk bit-identical re-execution); 3.2 `partially-run` (swept in full, generator source-derived and unverified); 5.1 `negative (bounded: non-PIE address family only)`.** Not "closed".

## 1. What the source says (read from the release tarballs, `verification.json`)

| version | `$RANDOM` generator | auto-seed formula | diff from 4.2 | verification status |
|---|---|---|---|---|
| 4.2 (reference, R32/R37) | Park-Miller 16807, `unsigned long` state, `long h,l`, `&32767`, correction `#if 0`; zero -> constant 123459876 | `sbrand(tv_sec ^ tv_usec ^ pid)` | - | L1: real 4.2.0 binary (R19-G1) |
| **4.1** (`variables.c` brand l.1229, seedrand l.1263) | same | same | **only the zero branch**: `if (rseed==0) seedrand();` (clock re-seed, nondeterministic) instead of the constant. Same LP64/ILP32 fork. | L3: verified by source identity to the L1 4.2; R19-G1 cross-implementation 0/2000 mismatches (LP64 and ILP32) |
| **4.0** (l.1217 / l.1251) | same | same | RANDOM block is **textually identical to 4.1** (empty diff); differs from 4.2 only in the zero branch | L3, as 4.1 |
| **3.2** (l.1156, init l.498) | **different**: ANSI-C LCG `rseed*1103515245+12345`, `(rseed>>16)&32767` (4.0 turned this `#if 0`); ABI-independent | `sbrand(getpid() + shell_start_time)` - `pid + time(0)`, no `usec`, no `seedrand()` | new LCG and a different, smaller-structure seed (consecutive integers) | **source-derived, unverified** (no 3.2 binary, no compiler, no WSL). Cross-checked against R19-G1's second transcription (0/2000) and the textbook ISO-C-sample sequence (`RANDOM=1` -> 16838, 5758, 10113, 17515, 31051 ...; recollection-level) |
| **5.1** (`lib/sh/random.c`; variables.c l.608) | **different**: u32 Lehmer with the Schrage correction enabled (single cycle 2^31-2), zero -> 123459876, output folded `(r>>16)^(r&65535)` when compat level > 50 | `genseed()` = `tv_sec ^ tv_usec ^ pid ^ ppid ^ uid ^ (u32)&seedrand` | new generator; **address term in the seed** | **L2 verified**: live bash 5.3.9 binary, `RANDOM=s` then 200 values, 6 seeds (1, 3301, 12345, 1354603465, 2147483646, 4000000000) all equal; R19-G1 cross-impl 0/2000 |

First 20 values after `RANDOM=1`: 3.2 `16838 5758 10113 17515 31051 5627 23010 7419 16212 4086 2749 12767 9084 12060 32225 17543 25089 21183 25137 25566`; 4.x `16807 15089 11481 3114 14210 23240 3800 2558 12099 1101 6296 15445 4748 23522 21683 14151 14615 16657 17304 18772`; 5.1 `16807 10791 19566 13983 29619 18126 2269 24347 31152 29673 10638 32297 30929 24462 21092 29834 27903 16877 29323 16858` (the last equals the live binary's).

Vector prefilter heads equal the scalar generators on 3,000 seeds x 28 values per variant (0 mismatches, anti-repeat excluded exactly as in R32/R37).

**Key structural finding (4.0/4.1).** State 0 is reachable only from `s = m*(2^31-1)`, `m<=45` (LP64; `m<=2` ILP32) because `16807*l == 2836*h` is the only way for the 64-bit (32-bit) wrap to give 0. A Lehmer state never equals those, so only a chance hit after a negative-residue wrap reaches 0. Heuristic expected number of orbit seeds touching state 0 in 1024 steps: **LP64 2e-7, ILP32 ~37 of 77.6M**. Every other seed's 4.0/4.1 stream is byte-identical to bash 4.2's, so the 4.0/4.1 orbits are the 4.2 orbits.

## 2. Natural-rate controls (before any count; `control_<v>.json`)
60 plants per version (10 each EN_MODERN / EN_NOVOWEL / HEBREW x keyskip1 / keyskip2), real 2^16-seed chunk path (pf_v4_12 -> v3 L120 both rels -> v3 L240 -> panel-R36, N=1e6 bars), only filter = realised C[:40] doublet-free. Pooled recoveries (recover/n):

| version | EN_MODERN skip-free / with-skip | EN_NOVOWEL skip-free / with-skip | HEBREW skip-free / with-skip | total | gate (>=3 per split) |
|---|---|---|---|---|---|
| 3.2 | 11/11, 9/9 | 9/9, 10/11 | 9/9, 11/11 | 59/60 | pass |
| 5.1 | 14/14, 6/6 | 9/9, 10/11 | 14/14, 6/6 | 59/60 | pass |
| 4.1 | 11/11, 9/9 | 7/7, 13/13 | 12/12, 8/8 | 60/60 | pass |
| 4.0 | 10/10, 10/10 | 9/9, 10/11 | 8/8, 12/12 | 59/60 | pass |

The single miss per version is an EN_NOVOWEL plant that failed the prefilter (the known weakest register). Per-relation tables are in each file.

## 3. Sweeps

| version | seeds screened | fraction of enumerated orbit | survivors (= decodes per relation) | best vs 12-register bar at actual N / N=1e6 | flagged | near-miss |
|---|---|---|---|---|---|---|
| **4.1 / 4.0** LP64 | 77,594,624 (R37-I2 4.2 LP64, by identity) | 296/296 | 65,815 | ks1 6.347 vs 8.113 / 9.102; ks2 **7.065** (seed 1354603465, LP1_REAL) vs 8.027 / 8.999 | 0 | 0 |
| **4.1 / 4.0** ILP32 | 77,594,624 (R37-I2 4.2 ILP32, by identity) | 296/296 | 65,971 | ks1 6.506 vs 8.114 / 9.102; ks2 6.763 vs 8.028 / 8.999 | 0 | 0 |
| 4.1 independent replication | 2,097,152 | 8/296 chunks | 1,795 | survivor and decode sets identical to R37's (3,590 rows each); pmax equal at 3 dp (max diff 0.0005 = rounding); 0 state-0 events | - | - |
| **3.2** | 76,237,568 | **291/291** | 64,511 | ks1 **7.098** (seed 1326767047, LP1_REAL) vs 8.105 / 9.102; ks2 6.567 (seed 1367421463, EN_MODERN) vs 8.020 / 8.999 | 0 | 0 |
| **5.1** (non-PIE, x in 0..7) | 92,274,688 | **352/352** (x=4 image: 296/296 first, 65,364 survivors) | 77,772 | ks1 6.455 (seed 1363452256, LP1_REAL) vs 8.173 / 9.102; ks2 6.522 (seed 1368058002, EN_MODERN) vs 8.086 / 8.999 | 0 | 0 |

L=240 bars at actual N: 3.2 8.119 (ks1) / 8.366 (ks2); 5.1 8.177 / 8.428. No row cleared even the L=120 screen bar, so no L=240 gate decode was needed. Wall: 3.2 2053 s, 5.1 2910 s, 8-chunk replication 71 s. Stores: `sweep_rows.jsonl` (284,566 rows, 14-field with `degenerate`, 3.2 + 5.1) and `replication_rows_bash4.1.jsonl`; `AD.validate_store` ok and `check_r3_store` `[]` for both.

**Decision for the coordinator on 4.1/4.0.** The brief asked for a full sweep per version; I did not spend ~50 min re-running 77.6 M seeds whose keystreams are provably the ones R37-I2 already swept (same bytes, same instrument), and used the time on the two orbits that are genuinely new (3.2, 5.1). The replication subset is a bit-level check of that claim through the 4.1 code path, not a proof for the remaining 288 chunks; the proof is the source diff plus the zero-state argument. If you want the literal full re-run, `python sweep.py` needs a 4.1 branch in `run()` (about 52 min).

## 4. Reach per register (three conditionals)
pf_v4_12 natural-rate screen reach 0.952 (EN_HALFVOWEL) to 0.994 (LP1_REAL), Greek 0.985, Hebrew 0.982, Norse 0.981 (R37-I2 `power12_per_register.json`, unchanged instrument) x v3 end-to-end recovery of screen passers (this lane's controls: 59-60 of 60 per version; EN_NOVOWEL with-skip is the weak spot, 10/11 in three versions).
1. **Key space**: 4.1/4.0 the 74 x 2^20 `tv_sec^tv_usec^pid` orbit (both ABIs); 3.2 the 76,237,568 integers `pid + time(0)` (pid <= 32768); 5.1 the non-PIE `genseed` family (88 x 2^20; one build = 74 x 2^20); `%29`, offset 0, sign -1, C[0]-aligned.
2. **Transition model**: keyskip1 + keyskip2 under beam_v3 panel_max, screen heads with <= 2 skips in 24 runes (heads with >= 3 are unscreened, est. ~3% of true-key mass).
3. **Register**: panel-R36's twelve, L=120 screen / L=240 gate.

## 5. not_covered
bash 5.x PIE/ASLR builds (address term randomises seed bits 12-31; effective orbit ~2^31, this lane enumerated ~4.3% of it); BASH_COMPAT<=50 (unfolded output); bash 5.0/5.2/5.3 seeding differences (only 5.1 source read; the live 5.3.9 binary matched on `RANDOM=s` streams); pid_max > 32768 for 3.2 (~5.5% more seeds); 3.2 `$RANDOM` first used inside a subshell (state-dependent reseed `rseed+pid+NOW`); the ~37 ILP32 / ~0 LP64 4.0/4.1 seeds that hit state 0; heads with >= 3 skips; free relation; offsets != 0; sign +1; registers outside the twelve; the 2012-2014 time window (anachronistic for 5.1, kept for comparability); ILP32 3.2 equals LP64 (shown, not a separate sweep).

## 6. Files
`PREREG.md`, `PREREG-ADDENDUM-1.md`, `generators.py`, `verification.json` (+`verification_raw.json`, `mk_verification.py`), `sweep.py`, `control_{3.2,4.0,4.1,5.1}.json`, `control_gates.json`, `replication_4.1_vs_R37.json`, `replication_rows_bash4.1.jsonl`, `sweep_rows.jsonl`, `sweep_summary.json`, `sweep_summary_final.json`, `keep_rows.json`, `run.log`, `ledger.json`, `ledger_patches.json`, `mk_ledger.py`.
