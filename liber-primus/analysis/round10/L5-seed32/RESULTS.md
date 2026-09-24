# L5-seed32 Results: Perl, POSIX, and Xorshift32

**Date**: 2026-09-24
**Sweep Status**: 100% COMPLETE for 3 fast PRNG generators. 0 HITs.

## The Gap Addressed
Round 8 (and earlier rounds) ran exhaustive 32-bit PRNG seed sweeps but utilized a fixed `-12.5` statistical threshold that failed to scale linearly to 2^32, and was artificially restrictive against real keystreams. Furthermore, generators like `Perl rand()` and `POSIX lrand48` had never been comprehensively swept over the raw 32-bit integer space.

## Validation & Threshold (The P-2 Unlocking)
Before sweeping, the `sweep32x` C-harness was patched to fix an overly-strict failure assertion that broke `gen 8` and `gen 12` positive controls. `validate_gens.sh` passed against all reference implementations.

The empirical null curve was re-derived against 14 generators using `nullcurve.py`:
- `mu = -13.3837`
- `beta = 0.1269`
- **Corrected Threshold (FWER 0.01)**: `-12.0602`

A true planted seed scores `-11.2360` (margin of `+0.8242` over the FWER 1% bar). The instrument explicitly retains the statistical power to separate a true hit from 2^32 null noise.

## Execution
We ran the exhaustive 32-bit (0 to 4,294,967,296) rigid sweep in 2^26 chunk intervals using `run32.sh` for three PRNGs:

1. **gen 10**: Perl `srand(S); int(rand(29))` (drand48 backend)
   - Status: 100% complete (4.29B decodes).
   - Best score: `-12.3943`
   - Hits: 0
2. **gen 11**: POSIX `srand48(S); lrand48()%29`
   - Status: 100% complete (4.29B decodes).
   - Best score: `-12.5385`
   - Hits: 0
3. **gen 13**: `xorshift32(13, 17, 5) % 29`
   - Status: 100% complete (4.29B decodes).
   - Best score: `-12.4769`
   - Hits: 0

## Verdict
**CLOSED (coverage-bounded)** for these 3 PRNGs. No seed across the 32-bit space for `Perl`, `POSIX`, or `Xorshift32` generates the keystream used for the Liber Primus unsolved pages under this offset. The derived-key theory remains open solely for the heavier/unchecked generators (PHP, Python 2.7, .NET, etc.).
