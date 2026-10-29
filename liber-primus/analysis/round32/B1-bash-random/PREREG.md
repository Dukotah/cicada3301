# R32 / B1 PREREG - bash 4.2 `$RANDOM` auto-seeded orbit

_Timing disclosure: the harness was built and the positive control (`control.json`, 4 cells x 10 plants) was run and passed
BEFORE the sweep was launched; this file was finalised while the sweep was running and before any sweep result was read
beyond the progress counter (no decision below was changed after seeing a sweep score). The prefilter threshold, M, FPR and
coverage commitment were fixed by the control step. Doctrine: ARMADA-DOCTRINE.md. No git was run._

## Construction assumed (stated, enumerated)

bash 4.2 `initialize_shell_variables()` calls `seedrand()` => `sbrand(tv_sec ^ tv_usec ^ getpid())`; `rseed` is the state itself
(`round19/G1/RESULTS.md` section 3.3). For a run 2012-01-01..2014-06-01, `tv_usec < 2^20` and `pid < 2^15` only rewrite the low 20 bits
of `tv_sec`, so the reachable seed set is `(prefix << 20) | v`, **74 prefixes x 2^20 = 77,594,624 seeds** (the figure PICKUP-HERE names).
Generator = `round19/G1/gen_bash.py` (`brand` verbatim from bash-4.2 `variables.c`, plus the `get_random_number` anti-repeat loop with
`last_random_value = 0`). The two cheap plausible 4.2 constructions are both swept:

1. `bash4.2` - LP64 (`unsigned long` 64-bit) - validated L1 against a real bash 4.2.0 binary.
2. `bash4.2_i32` - ILP32 - L4 only (re-typed transcription; no real 32-bit binary; G1 NC-1).

Reduction `$RANDOM % 29`, `sign -1` (`p = c - k`), key offset 0 (seed == offset for bash; G1 M1). NOT swept: bash 3.2 / 4.0 / 4.1 / 5.x maps,
other reductions (`rej29`, `scale29`, hi-nibble...), `RANDOM=<n>` explicit seeds outside the auto-seed set, subshell re-seeding, 3 of 4
possible tv_sec ranges outside 2012-01-01..2014-06-01, `sign +1`, reversed/atbash orientation.

## The 28-minute figure

It comes from `round20/CAMPAIGN-PLAN.md` S-BASH: "77.6M seeds, 28 min on **16 cores**" with the **P-gate sieve** assumed open (a prefilter
whose power/FPR the P-gate lane was to measure; P1 was INFEASIBLE, so it never was). At this laptop's measured ~64 (pair) / ~142 (exact)
beam decodes/s, 77.6M x 2 variants x 2 relations = 6.2e8 decodes = ~70 days. Not feasible unprefiltered.

## Prefilter (language-agnostic, relation-agnostic)

Before the first key skip both relations decode identically, so the first `M=16` decoded runes `p = (C - K) mod 29` are scored against all
nine registers of the **round32/I2 panel** (sum of trigram log10, z-normalised per register on a seeded-3301 null of 2^19 in-set seeds
against the real LP2 head); a seed survives if the **max over 9 registers** exceeds the null `1 - 6e-4` quantile (per variant). Survivors are
decoded exactly (exact generator, anti-repeat included) under BOTH keyskip1 (`exact`) and keyskip2 (`pair`), beam_w 64, L=120, adjudicated by
the I2 panel (SWEEPROW rows persisted for every decode). `pmax >= 5.0` goes to the hitfn20 3-clause gate at L=240 (`N = 1e6` reference, bars
pair 7.3835 / exact 7.6342, recovery >= 0.90, held-out). An IoC-only prefilter was measured first (its scratch output was not kept; numbers: power at null q0.999, m=24, EN 0.017 (keyskip2), LATIN 0.047, EN_NOVOWEL 0.14) and
rejected: power 2-23 % at FPR 1e-3. The head-only trigram prefilter was chosen from `prefilter_power2.json` (power ~0.7 at FPR 1e-3).
**It is lossy by design: ~0.45-0.76 power depending on register (EN_NOVOWEL lowest), so coverage x power is NOT 1.00.**

## Aiming Test

| Q | Answer |
|---|---|
| Q1 hit shape + recognizer | A seed whose bash-4.2 `$RANDOM%29` keystream decodes LP2 0-119 under keyskip1 or keyskip2 to panel `pmax >= 5.0` and then passes hitfn20 (pmax >= bar, recovery >= 0.90, held-out). Recognizer proven on planted EN_MODERN/LATIN keys through the real chunk path (prefilter -> screen -> gate), >= 3 end-to-end recoveries per (variant x relation) cell, recorded in `control.json` before the sweep file was opened. |
| Q2 prior | R18-L1 puts the author on Ubuntu 11.04-12.04 whose `/bin/bash` is 4.2 (G1 section 5, "bash4.2 is THE era-correct variant"); the auto-seed set is derived from the date window, not a guess. Flat prior within the 77.6M (NC-4: pid/usec joint not modelled). Prior is modest; stated as such. |
| Q3 bounded? | Yes: 77,594,624 seeds x 2 ABIs x 2 relations, enumerable. Coverage committed: **the whole orbit prefiltered (coverage 1.00 of seeds) with decode-stage coverage = prefilter pass rate (~0.45-0.76 by register)**, within a 2500 s hard cap, prefix order shuffled with `Random(3301)` so any truncation is an unbiased random sample, reported as fraction (never silent). |
| Q4 conditionals | key space = bash-4.2 auto-seed set above, 2 ABIs, mod29, sign -1, offset 0; transition = keyskip1 + keyskip2 (not `free`; `pair`+`exact` is cheaper than `drift` by 2x and each is exact for its planted relation); adjudicator = round32/I2 nine-register panel (EN_MODERN, EN_KJV, LP1_REAL, LATIN, OE, DE, CY, EN_HALFVOWEL, EN_NOVOWEL; NOVOWEL detection-only). |
| Q5 kill | Planted control fails => fix harness, claim no coverage (REFUSE guard in `sweep.py`). Prefilter power on the control < 0.3 => do not claim orbit coverage, run stated-fraction sample instead. Neither triggered. |

## Threshold / null

Claim bars = hitfn20 `panelmax_bar` at the declared N=1e6 (L=120 cell, conservative vs actual ~2e5 decodes). `benchmark/null.py threshold_for(n, segment_len=120)` (I3's L-aware function) is also evaluated at the actual adjudicated N and reported; it governs the legacy `en` statistic and returns its -5.5 floor at this N (stated in RESULTS). Seeded null: seed 3301. Corpora hashes: carried in the SWEEPROW header (`corpora_sha256`), from `round32/I2-multiregister-readjudication/out_build.json`.

Verdict language: `negative (bounded: prefilter-lossy, construction-conditional)` if control passes and nothing is flagged; never "closed/exhausted/solved".
