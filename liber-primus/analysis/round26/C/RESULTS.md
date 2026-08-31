# Round 26 — Lane C — SEMANTIC-SEED enumeration — RESULTS

Date 2026-08-31. Target: **LP2 0–54** (`lib_numchannel.unsolved()`, the OTP-class page set).
Composition: corpus-semantic value **AS SEED** × generator zoo (page-56 ladders + PRNG) ×
skip-aware decode (keyskip1 `exact` + keyskip2 `pair`) × `hitfn20` recovery-gated certifier.

## Control recovery (mandatory gate — passed BEFORE the sweep null counts)

`control.py` plants a `enc_skip_by_two` (j += 2 per rejection, supp=0.83) English payload,
keystream produced by feeding a SEMANTIC seed through EACH generator, and requires `hitfn20`
recovery ≥ 0.90 + HIT=True. Result (`control.json`):

| generator | seed | recovery | held-out | pmax / bar | HIT |
|---|---|---|---|---|---|
| py27_random29 | 3301 | 1.000 | 1.000 | 25.24 / 6.76 | True |
| py27_grb5_mod | 3301 | 1.000 | 1.000 | 25.24 / 6.76 | True |
| py27_grb5_rej | 3301 | 1.000 | 1.000 | 25.24 / 6.76 | True |
| perl_glibc_r29 | 3301 | 1.000 | 1.000 | 25.24 / 6.76 | True |
| ladder_prime | 3301 | 1.000 | 1.000 | 25.24 / 6.76 | True |
| ladder_totient | 3301 | 1.000 | 1.000 | 25.24 / 6.76 | True |
| ladder_prime_totient | 3301 | 1.000 | 1.000 | 25.24 / 6.76 | True |
| py27_random29 (STR seed "THE PRIMES ARE SACRED") | — | 0.992 | — | — | True |

**measured control min recovery = 0.9917 ≥ 0.90 → ALL PASS.** The instrument recognises a
semantic-seed hit produced by every generator in the zoo. The null below is therefore a genuine
negative, not the null of an unmeasured instrument. (The `pair` relation is required: the plain
beam gets ~0.26 on skip_by_two — L7-B.)

## Coverage × power

**Coverage.** Seed set = **323 deduplicated corpus-semantic values** (`seeds.json`:
292 int + 31 str) spanning primes(94), totient-of-prime(98), prime-index(49), totient(≤60),
notable Cicada ints(20: 3301, 509/503, 0x7A35090F fragments, 2012 P.S. digits, telnet/onion),
dates unix+cal(12), coords(2), canon256/alphabet(2), and gematria sums + string forms of 31
solved-plaintext/koan phrases(16 sums + 31 str). Generator zoo = **7 families** ×
**2 decoders** (`exact` keyskip1, `pair` keyskip2), int seeds on all 7, str seeds on the 3 py27
reducers → **4,274 (seed × generator × decoder) rows, 100% of the enumerated set swept**
(`rows.jsonl`, `summary.json`). Elapsed 166 s.

Swept fraction: **323/323 semantic seeds × 7/7 generators × 2/2 decoders = 100% of the stated
enumerated semantic-seed space** at offset 0. Fraction of the raw 2^32 key space ≈ 0 by
construction — this lane's claim is the ENUMERATED semantic set, NOT a slice of 2^32. Not "closed".

**Power.** Control min recovery 0.9917 (≥ 0.90) on every generator + decoder; the full three-clause
`hitfn20` gate fires HIT=True on each planted semantic-seed hit. The instrument would recognise a
semantic-seed solve if one existed in this set.

## Result — clean NULL, zero survivors, zero flags

- **best screen score across all 4,274 rows = −6.578** (escalation bar = 5.0; gap > 11.5). Not one
  decode came within an order of magnitude of the bar.
- **survivors escalated to full hitfn20 = 0. flagged_for_oracle = 0.** No STOP-AND-ALERT event.
- Language-agnostic distribution (per doctrine R3, persisted per row): **IoC×N** min 0.853 / median
  **0.999** / max 1.284 (0.999 = exactly flat-random for N=29); **entropy** median 4.679 of a
  4.858 max; **min-distinct-32** median 17; **screen score** median −7.35, max −6.58.
- The single best decode = seed=3 (trigram) through `ladder_prime_totient` (the page-56 ladder),
  preset `exact` — still IoC×N 1.08, entropy 4.65: pure noise. Even the corpus-endorsed generator
  that solved page 05 produces only noise on 0–54 for every semantic seed.

## The three conditionals this negative carries (Q4)

1. **key-space swept:** ONLY the 323-value enumerated corpus-semantic seed set, fed as SEEDS
   (hash/abs+chunk for MT; srand48 for glibc; start-offset for the ladders), offset 0. NOT raw
   2^32 words; NOT non-corpus seeds; NOT offsets ≠ 0.
2. **decoder transition model:** keyskip1 + keyskip2 only. Rejection loops burning > 2 draws /
   rejection and permissive drift are outside this lane's relation.
3. **adjudicator register:** `hitfn20` panel (EN/LA/OE/DE/CY/LP1) + panel-max null. A pre-language
   payload register (base32/gzip/IoC-only) is out of scope.

## Checkpoint outcome (Q5)

Kill-condition was: max recovery < 0.55 AND zero bar-clears at 10% budget. Observed at 100%: max
screen −6.58, zero bar-clears — the lane is DEAD across the full enumerated set, exactly as the
checkpoint predicted at the tail. No semantic seed approaches the recovery floor.

## Honest verdict

This HARDENS the OTP-class verdict along a genuinely un-run axis: the "puzzle-must-be-solvable"
reframe (semantic value AS SEED through the page-56 ladder + PRNG zoo under the repaired skip-aware
+ panel-max instrument) produces noise for 100% of the 323-value enumerated corpus-semantic seed
set. The instrument is proven powerful (control 0.99); the space is bounded and fully swept; the
result is flat-random (IoC×N median 0.999). It does NOT move the needle toward a solve, and it
removes the "maybe the derived key just needs a Cicada-flavoured seed through the right generator"
hope for this bounded, high-prior-per-item set. Swept fraction: **323/323 semantic seeds ×
7/7 generators × 2/2 decoders = 100% of the enumerated semantic-seed space at offset 0**;
≈0% of raw 2^32 (out of scope by design).
