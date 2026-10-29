# R32 / B2 PREREG - PHP `mt_rand` first-fire (canonical MT19937 + pre-7.1 broken twist)

_Written BEFORE the control or the sweep was run (only `php_mt.py` self-test and a throughput timing of the prefilter existed). Doctrine: `ARMADA-DOCTRINE.md`. No git was run. `LEDGER.json` untouched._

## Construction assumed (stated)

- **Version:** PHP 5.x (<= 7.0) engine. Its default behaviour equals PHP >= 7.1 `MT_RAND_PHP`; canonical equals `MT_RAND_MT19937` (PHP >= 7.1 default). Both are swept.
- **Seeding:** `mt_srand(seed)`: `php_mt_initialize` (`s[0]=seed; s[i]=1812433253*(s[i-1]^(s[i-1]>>30))+i`), then `php_mt_reload`; `mt_rand()` = tempered u32 `>> 1` (31 bit). `seed` is a uint32.
- **Twists:** `m ^ (mixBits(u,v)>>1) ^ (-(loBit(X)) & 0x9908b0df)`, canonical `X = v = s[i+1]`; legacy PHP `X = u = s[i]` (the bug: wrong operand). In-place reload, `N=624, M=397`.
- **Reductions:** (1) `scale29` = PHP 5 `mt_rand(0,28)` via `RAND_RANGE`: `floor(29 * n / 2^31)` (computed exactly as `(n*29)>>31`); (2) `mod29` = `mt_rand() % 29`. Both swept. Sign -1 (`p = c - k`), key offset 0. 4 key cells: {mt, php} x {scale29, mod29}.
- **Relations:** keyskip2 (`pair`) and keyskip1 (`exact`) of `round19/I1/driftbeam.py`, beam_w 64, L=120 screen, L=240 gate.
- **Not swept:** PHP `rand()` / `srand()`, `random_int`, `mt_rand()` with other ranges (e.g. `mt_rand(1,29)`, `mt_rand(0,29)%29`), offset != 0, sign +1, reversed/atbash, `uniqid`/`microtime` (non-integer) seeding, seeds > 2^32 (PHP truncates to 32 bits anyway), free-drift.

## Reference checks (php_mt.py selftest, reported not assumed)
Canonical seed 1 first u32 == 1791095845 (MT19937 reference); canonical stream == numpy `MT19937` bit-generator raw output (legacy seeding) over 700 draws; both twists x both reductions equal `analysis/round28/L4/gen28.py` (which R28-L4 gated `|delta|=0` against a real `/usr/bin/php` 8.5.4 in both engine modes) over 1100 draws x 5 seeds; vectorised head == scalar generator. The legacy first output for `mt_srand(1)` is 1244335972, which matches what I remember as the PHP 5 value (memory only; the binding reference is the R28-L4 php-binary gate).

## Aiming Test (five answers)

**Q1 - What named, bounded hypothesis?** The Liber Primus pad is `mt_rand()` (PHP, 2012-14 era) reduced to 0..28, seeded by an integer `mt_srand(seed)`, in one of the four cells above, with a skip-tolerant transition (keyskip1/2). This is the ledger's "highest-prior open generator" (CENSUS section C).

**Q2 - Measured fact above a flat prior?** Only the census ranking and that 2012-14 PHP is period-appropriate; there is no measured fact that LP2's key is PHP-derived. Tier (a) concentrates on seeds with prior mass (3301 lore, B04 numeric/primes, seedprior20 PGP seconds, dates 2011-2015 as unix-midnight and YYYYMMDD, hour-aligned unix times, ints < 2048). Tier (b) is flat prior, stated as such.

**Q3 - Power of the instrument?** Relation-agnostic nine-register trigram prefilter (B1's, first 16 decoded runes, FPR target 6e-4 per cell, calibrated per cell on 2^19 uniform seeds with np `default_rng(3301)`), then driftbeam + the I2 nine-register panel. Power is measured per twist x reduction x relation in `control.json` (prefilter power per register on 250 plants each; end-to-end plants, 8 per cell, >= 3 recovered required) BEFORE any null count. B1 measured prefilter power 0.47-0.74 (25-55 % of planted keys are lost before decode); expect the same here and it is a stated limit.

**Q4 - Coverage committed?** Tier (a): all ~487 core seeds decoded UNFILTERED in all 4 cells x 2 relations (= 3,896 decodes); ~47.5k dense seeds (dates/hours/small ints) prefiltered and ALL survivors decoded. Tier (b): uniform random sample (seed 3301) of the 2^32 space, same 4 cells prefiltered together (shared MT head), all survivors decoded, hard wall cap 2400 s for the whole sweep (tier a first). Measured throughput ~14k seeds/s (prefilter ~73k seeds/s, decodes dominate), so the expected coverage is ~2.5e7 seeds, **~0.5-0.7 % of 2^32; floor commitment 2^24 (0.39 %)**. The full 2^32 x 4 cells is ~3.3 days at this rate (~1.6e5 core-s of prefilter+decode); the remainder is explicitly deferred to bigger hardware (the R28-L4 grind queue) and is NOT claimed. Coverage is reported as fraction of 2^32 per tier and per twist (the same random seeds feed every cell, so per-twist fraction is identical).

**Q5 - Kill rule / what counts as a hit?** If any planted cell fails the control (< 3 end-to-end recoveries, or a recovered-count deficit greater than 1 vs. prefilter passers, or a selftest mismatch) the harness is fixed and the control re-run; the sweep refuses to start on a failed control. A hit needs hitfn20's 3 clauses (pmax >= `panelmax_bar` at N=1e6 declared: pair 7.3835 / exact 7.6342; recovery >= 0.90; held-out >= 0.90) at L=240; any survivor is "flagged-for-oracle", never certified. Near-misses (screen pmax >= bar at the ACTUAL N but < the declared-N bar) are recorded as B1 did. Claim bar is hitfn20 `panelmax_bar`, not the -5.5 floor (B1 finding). Nothing here is worded solved/closed/exhausted.

## Panel
`round32/I2-multiregister-readjudication/models/panel.npz` via I2 `adjudicate.py`; corpora hashes land in the SWEEPROW header (`AD.header`). SWEEPROW rows persisted for every decode.
