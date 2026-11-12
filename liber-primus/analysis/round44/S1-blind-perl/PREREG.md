# PREREG — Round 44 lane S1: every Perl `rand` seed, through the blind adjudicator

_Written 2026-11-12, before any Perl seed was evaluated against the real ciphertext. What had been
run when this was written: the generator check against the `perl` binary on two seeds, and the
calibration on random non-Perl keys and plants (`calibrate.py`, `calibration.json`). Doctrine:
`../../../ARMADA-DOCTRINE.md`. Parent audit: `../A0-fresh-eyes-audit/AUDIT.md` sections 1.7, 2, 5._

## 1. Hypothesis

The LP2 keystream is Perl's `int(rand(29))` after `srand(s)` (explicit or automatic), one draw per
rune from rune 0 of page 0, combined additively mod 29 with the plaintext, with the anti-repeat rule
consuming one or two draws per rejection. Perl's generator is `drand48` seeded with a 32-bit value,
so the family is **exactly 2^32 keystreams** and the sweep enumerates all of them.

## 2. Instrument (new; measured before use)

`blind.c`, the language-model-free adjudicator specified in the audit. For each seed and each of
four modes (sign s = +-1 of the key in the combiner; rejection step q = 1 or 2) it searches every
key-pointer path that jumps only at admissible sites (r rejected draws are equal; the accepted one
differs from them by `C[i] - C[i-1]`; for q = 2 a kept doublet may burn one more draw) and takes
the largest sum of squared symbol counts of the decode. The statistic is the index of coincidence,
so it does not depend on the plaintext's language, spelling or numbering, on a constant in the
combiner, or on Atbash / Beaufort reflection.

Three exhaustive stages on page 0: L1 = 64, L2 = 120, L3 = 262 (the whole page).

## 3. Thresholds, fixed here

Stated as IoC x 29 and as the integer sum of squares the kernel compares.

| stage | L | threshold | where it comes from |
|---|---|---|---|
| 1 | 64 | IoC x 29 >= 1.316 (sum of squares >= 247) | 6 % of 2,000,000 random keys pass per mode; 431 of 432 calibration plants pass |
| 2 | 120 | IoC x 29 >= 1.436 (sum of squares >= 828) | 1e-4 of random keys pass per mode; calibration plants: minimum 1.482 |
| 3 | 262 | IoC x 29 >= 1.40 (sum of squares >= 3564) | calibration plants: minimum 1.614; a random key's full-page value is about 1.1 |

A (seed, mode) pair that clears all three is **FLAGGED-FOR-ORACLE** (never a solve: its decode is
written out, adjudicated by panel-R36 in Gematria order, and read by a human per `HUMAN-ORACLE.md`).

## 4. Positive control, through the sweep's own glue

24 secret seeds drawn by a fixed RNG. For each: the keystream comes from the **`perl` binary itself**
(not from this lane's generator code), a 262-rune passage is enciphered with one of the repository's
own constructions (`campaign18_skip/skipdecode.encipher_keyskip`, `round19/I1/constructions`
`enc_skip_by_two`, `enc_coin_from_key`), in a rotation of English letter-wise / English multigraph /
Latin, as written / under a random relabelling of the plaintext / with a +7 constant / as Beaufort,
with sign +1 or -1. The sweep binary is then run over a window of 2^18 seeds containing the planted
seed, with the planted ciphertext in place of the real one. The control passes if **at least 23 of
24** planted seeds are flagged and no other seed in any window is.

## 5. Null and expected false flags

The sweep is its own null: all but at most one of the 2^32 seeds are wrong. From the calibration,
about 1e-4 of (seed, mode) pairs reach stage 3, and a wrong key's full-page IoC x 29 sits near 1.1
with a spread of a few hundredths, so the expected number of false flags at 1.40 is far below one.
If more than 20 pairs are flagged the threshold was mis-set and the lane is reported INCONCLUSIVE
with the flagged list, not as hits.

## 6. What is persisted (doctrine R3)

- the complete stage-1 histogram, per mode, over all 2^32 seeds (`hist.json`);
- every (seed, mode) pair that reaches stage 3 with its three statistics (`survivors.bin`,
  gitignored; rebuilt by `run_s1.py`);
- a SWEEPROW/1 store of the 2,000 best stage-3 rows, each decoded along its best path and
  adjudicated by panel-R36 (`sweep_rows_top.jsonl`), so the result can be re-read in any register.

## 7. Verdict rule

- **FLAGGED** if any pair clears stage 3 (and the count is <= 20): hand to the oracle.
- **NEGATIVE** if none does and the control passed.
- **INCONCLUSIVE** if the control failed, or the sweep did not cover all 2^32 seeds (then the covered
  fraction is reported and nothing more is claimed).

## 8. The Aiming Test

- **Q1 (recognizer):** section 4. Plants are the hypothesised object exactly: a Perl keystream from
  the real binary, the repo's own filter constructions, decoded by the sweep binary.
- **Q2 (prior):** Perl is the only generator with signed first-party evidence. Two signed messages
  (2012-01-15, 2014-01-06) carry `Crypt::RSA` armor and Perl `Data::Dumper` output
  (`../../round19/C3/RESULTS.md` section 2c'). About 25,000 Perl seeds had ever been decoded, and the
  one prior-dense run was aimed at a mid-book slice (`../A0-fresh-eyes-audit/AUDIT.md` 1.6).
- **Q3 (bounded):** enumerable and complete: 2^32 seeds.
- **Q4 (three conditionals):**
  1. *key space:* all 2^32 seeds of `srand`; the idiom `int(rand(29))`; no draws consumed before the
     first rune; the stream starts at rune 0 of page 0.
  2. *transition model:* one draw per rune; a rejection consumes one draw (q = 1) or two (q = 2, with
     or without the in-stream coin at kept doublets); at most 8 / 12 / 24 rejections in the first
     64 / 120 / 262 runes; both signs of the key; **any constant in the combiner, Atbash and Beaufort
     are covered**. Not covered: a key pointer that stalls (F left in clear), rejection by deletion
     or by rewriting the rune without a draw, separators that consume draws.
  3. *register:* none needed. Any plaintext whose symbol distribution has IoC x 29 of about 1.4 or
     more over 262 runes, in any language, spelling or numbering. A plaintext that is itself
     near-uniform over 29 symbols is not covered.
- **Q5 (kill):** if the control flags fewer than 23 of 24 plants, stop before the sweep. If the first
  2^26 seeds send more than 1e-3 of pairs to stage 3, stop: the calibration did not transfer.

---

## Addendum 2026-11-12, written while the sweep was at chunk 17 of 256 and before any of its output was read

Reason: lane S2 (`../S2-blind-glibc-clock/`, same instrument and thresholds) finished first, and it
shows that section 5 above mis-estimated the null at stage 3. A wrong key that reaches stage 3 is not
an unselected random key: it got there on a head with a fluke-high index of coincidence, and the
full-page search then has thousands of paths with which to keep agreeing with that head. Over S2's
7.2e8 seed-mode pairs the largest full-page IoC x 29 of a wrong key was **1.388**, not "about 1.1 with
a spread of a few hundredths". This lane evaluates 1.7e10 pairs, 24 times as many, so by ordinary
extreme-value scaling it should be expected to produce a few values between 1.40 and about 1.45 from
wrong keys alone. The weakest of the 432 calibration plants scored 1.614 on the full page.

The threshold in section 3 is not changed (it is the registered one, and every pair at or above 1.40
is reported and decoded). What is added, before looking:

- a pair with full-page IoC x 29 **>= 1.50** is a **strong flag** and goes to the human read;
- a pair in **[1.40, 1.50)** is a **weak flag**: reported, decoded and adjudicated by panel-R36 like the
  others, and classed *null-consistent* if its full-page value is lower than its own L = 120 value by
  more than 0.15 (a true key's statistic does not decay with length; a head fluke's does) and its
  decode shows no panel score above the bar. A weak flag that is not null-consistent by that rule is
  treated as a strong flag.

The verdict rule of section 7 is read accordingly: NEGATIVE requires no strong flag and every weak
flag null-consistent; the "more than 20 flagged" clause applies to the total.
