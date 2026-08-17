# PREREG — Lane L5-seed32 (Round 10)

Written BEFORE any run. Thresholds fixed here are the only ones that count.

## Context this lane inherits (not re-derived)

Round 8 track SEED swept 10 validated PRNG/reduction variants x 2 directions x every
unix-second seed 2011-01-01..2015-01-01 (126,230,400 seeds) = 2.52e9 decodes, 0 hits,
best -13.13; plus 15,408 lore/string/date seeds, 0 hits. The full 32-bit space was
started and never finished (`analysis/seed_sweep/results_full32.txt`, 2 lines, no DONE).

## Hypotheses and pre-registered decision lines

### H1 — SEED-COVERAGE. The pad is one of the 10 swept generators at some 32-bit seed
outside the 2011-2015 unix-second slice (a chosen constant, a PID, a hand-typed number).
- Test: `./sweep <g> 0 4294967296 48 -12.5` per generator, both directions, interrupter
  branching as built. Coverage measured in seeds actually swept, logged per chunk.
- PASS/HIT = any decode scores > -12.5 on the 48-rune window AND re-scores as English
  (<= -5.0 page-scale) over the full 12,956 runes AND reproduces under
  `liber-primus/tests/validate.py` conventions.
- NULL = every generator/chunk completed reports `hits>-12.5=0`, and coverage is recorded
  as an exact seed count. Partial coverage is reported as partial, never as "closed".

### H2 — THRESHOLD VALIDITY AT SCALE (the load-bearing test of this lane)
The -12.5 threshold was validated against the null max measured at N ~= 2.5e8 decodes per
generator (the time-seed slice). The full 32-bit space is 34x larger per generator, and
best-of-N under a null grows with log N. If the null max at full-32 N reaches -12.5, then
every `hits>-12.5=0` line in results_full32.txt is a statement about a threshold that no
longer separates signal from noise, and a "hit" would be uninterpretable.
- Test: run identical sweeps against SHUFFLED ciphertext (same 29-rune multiset, same
  length, F density preserved so interrupter branching is unchanged) at matched N, for the
  same generators. Fit best-of-N vs ln N. Extrapolate to N_total = 10 gens x 2^32 x 2 dirs
  = 8.59e10 decodes.
- PASS (threshold still safe) = extrapolated null max at N_total <= -12.60, i.e. >= 0.10
  score units of margin below -12.5.
- FAIL (threshold degraded) = extrapolated null max > -12.60. Consequence, fixed now: the
  full-32 sweep cannot be run at -12.5 as a decision rule; it must be re-run with a
  scale-corrected threshold, and any single decode crossing -12.5 must be treated as an
  expected null event, not a lead.

### H3 — DECISIVENESS. Does finishing the full 32-bit sweep add information?
- Measure: (a) planted-true score from `./sweep selftest` on this box (Round 8 reports
  true -11.24 vs wrong-seed -15.8..-16.9); (b) the null max-of-N curve from H2;
  (c) the resulting separation margin at N_total.
- Pre-registered reading: if (planted-true) - (null max at N_total) >= 1.0 score units,
  the sweep retains discriminating power and finishing it is informative. If the margin is
  < 0.5 units, finishing it is a completeness ritual and I will say so in those words.
- This is an argument, not a hit test; it is registered so the conclusion cannot be
  retro-fitted to whatever the numbers turn out to be.

### H4 — GENERATOR CENSUS. 10 generators is a choice, not a census.
- Deliverable: an explicit list of generator families a 2013-2014 author could plausibly
  have used that are NOT reachable from sweep.c, each marked covered / partly covered /
  uncovered against the ledger (BBS/LCG/MT were done in Campaign XIII / ARMADA-20).
- No pass/fail; this is inventory. Any generator I add must pass the same harness gate
  Round 8 used (exact reproduction against the reference implementation on >= 3 seeds x
  >= 500 draws) BEFORE it is swept. An unvalidated generator produces a meaningless null
  and will not be run.

## Null control (mandatory, applies to every run in this lane)
Every real-ciphertext sweep is paired with an identical sweep over a shuffled ciphertext
(seed-fixed permutation, recorded in the artifacts). A real-ct best score is only
interpretable against the shuffled-ct best score at the SAME N.

## Scale note
All scores in this lane are the sweep's stream-scale mean 4-gram log-prob over a 48-rune
window: random ~ -16, English ~ -11 to -12. This is NOT the page-scale scale (-4.2..-5.0
English, -7.3 random). No number here is comparable to a page-scale number.

## Budget and resumability
Single runs kept under ~20 minutes. Coverage is advanced in chunks with a checkpoint file
so the sweep is resumable by any later agent with one command. What is not finished is
reported as not finished, with the exact remaining seed count and a wall-clock estimate
measured on this box.
