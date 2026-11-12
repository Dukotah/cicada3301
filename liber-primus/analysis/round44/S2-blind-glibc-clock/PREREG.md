# PREREG — Round 44 lane S2: glibc `rand()` seeded by the clock, through the blind adjudicator

_Written 2026-11-12, while lane S1 (`../S1-blind-perl/`) was running and before any glibc seed was
evaluated against the real ciphertext. What had been run: the generator check against the system libc
on six seeds (both reductions match, including the two server timestamps and seeds above 2^31).
Same instrument, same thresholds and same page-0 head as S1; read `../S1-blind-perl/PREREG.md` first._

## 1. Hypothesis

The LP2 keystream is glibc `rand()` (identically `random()`) after `srand(t)`, where `t` is the unix
time at which the enciphering program ran, or a small integer typed by hand; one draw per rune from
rune 0 of page 0; reduced to 0..28 either as `rand() % 29` or as `floor(29 * rand() / 2^31)` (the
scaling PHP 5's `rand(0, 28)` and much C code use).

Seeds enumerated, for each of the two reductions:

- every integer in `[0, 2^24)`;
- every second in `[1322697600, 1396483200)`: 2011-12-01 00:00:00 UTC to 2014-04-03 00:00:00 UTC.
  The window contains both server timestamps Round 43 F5b recorded and no lane had used: 1389478032
  (Sat 11 Jan 2014 22:07:12 GMT) and 1396427599 (Wed 02 Apr 2014 08:33:19 GMT, the Last-Modified of
  the page that served Liber Primus).

That is 90,562,816 seeds per reduction, 181,125,632 keystreams, four modes each.

## 2. Instrument and thresholds

Exactly lane S1's: `../S1-blind-perl/blind.c`, stages L = 64 / 120 / 262 with sums of squares
>= 247 / 828 / 3564 (IoC x 29 >= 1.316 / 1.436 / 1.40). A pair clearing all three is
FLAGGED-FOR-ORACLE, never a solve.

## 3. Positive control, through the sweep's own glue

16 secret seeds inside the swept ranges (fixed RNG), eight per reduction. The keystream comes from
**the system C library itself** (a ten-line C program calling `srand` and `rand`, compiled at run
time), not from this lane's generator code. Plants rotate the same texts, variants, filter
constructions and key signs as S1's control. The sweep binary is run over a window of 2^18 seeds
containing each planted seed with the planted ciphertext in place of the real one. The control passes
if at least 15 of 16 planted seeds are flagged and no other seed in any window is.

## 4. Verdict rule

FLAGGED if any pair clears stage 3 (and no more than 20 do); NEGATIVE if none does and the control
passed; INCONCLUSIVE otherwise (control failed, or the ranges were not completed: the covered
fraction is then reported and nothing more is claimed).

## 5. What is persisted (doctrine R3)

The complete stage-1 histogram per reduction and mode; every pair that reaches stage 3; a SWEEPROW/1
store of the 1,000 best rows adjudicated by panel-R36.

## 6. The Aiming Test

- **Q1:** section 3; plants are the hypothesised object, keystream from libc itself.
- **Q2:** Round 18 L1 ranks glibc first on the toolchain evidence, and `srand(time(NULL))` is the
  commonest seeding idiom there is. Under the repaired instrument only midnights and top-of-hour
  seconds had been tried for glibc (ledger `R32-B3-GLIBC-GEN0-PRIORDENSE`); Round 8's per-second sweep
  used a rigid 48-rune English kernel (`../A0-fresh-eyes-audit/AUDIT.md` section 2).
- **Q3:** enumerable; 1.8e8 keystreams.
- **Q4 (three conditionals):** (1) *key space:* the two seed ranges above, two reductions, no draws
  before the first rune, stream starts at rune 0 of page 0; seeds outside the ranges (for example
  `time ^ pid`) are not covered. (2) *transition model:* as S1: one or two draws per rejection, in-stream
  coin, both key signs, any combiner constant, Atbash and Beaufort covered; a stalled key pointer,
  deletion or rewrite without a draw, and separators that consume draws are not. (3) *register:* none
  needed (any plaintext with IoC x 29 of about 1.4 or more over the page).
- **Q5 (kill):** stop before the sweep if the control flags fewer than 15 of 16.
