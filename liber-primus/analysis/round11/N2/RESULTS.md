# LENS N2 — prime-gap / prime-index streams read as DATA

**Verdict: NEGATIVE.** Positive controls PASS; no interpretation of any prime-derived
integer stream from the unsolved LP2 stream beats its size-matched null, and none clears
the HIT floor (−5.5).

## What was tested
Streams built on the 12,956-rune unsolved stream via the Phase-0 instrument:
`nc.v_prime_gap`, `nc.v_prime_index`, and their cumulative sums. Each read four literal ways:
- (a) base-29 digits regrouped (2- and 3-digit) → runes → translit → English score
- (b) values mod 29 as direct plaintext → English score
- (c) ASCII/byte values → printable ratio
- (d) coordinate pairs → top-pair concentration (structure proxy)

Null: `nc.null_band` = 200 `nc.shuffled` draws (seed 3301) per English-scoring route.
HIT bar: score ≥ −5.5 AND ≥ null_max + 0.5.

## Positive controls (machinery works)
- **C1 — PARABLE prime-index, mod-29 route:** prime_index = i+1, so mod 29 → i+1; undoing
  the +1 shift reconstructs PARABLE **exactly** (exact_match = 1.00, score **−4.42** =
  English, matching plaintext −4.42). Recovered head `PARABLELICETHEINSTARTUNNELNG...`.
- **C2 — planted-gap recovery:** a genuine runeglish message carried as `idx + 29k + 100`
  (large "gap-like" magnitude) is recovered exactly through the mod-29 route
  (exact_match = 1.00, score **−4.42**). The value-channel decode machinery recovers a
  planted signal cleanly.

`control_passed = True`.

## Unsolved-stream result (best English score per stream vs its null max)
| stream | distinct | best score | null max | null+0.5 | HIT |
|---|---|---|---|---|---|
| prime_gap | 5 | **−6.951** | −6.901 | −6.401 | no |
| prime_index | 29 | −7.482 | −7.432 | −6.932 | no |
| prime_gap_cumsum | 12956 | −7.523 | −7.447 | −6.947 | no |
| prime_index_cumsum | 12956 | −7.534 | −7.439 | −6.939 | no |

- Best overall: `prime_gap` = **−6.951**, its null max = **−6.901** → the stream scores
  *below* its own shuffle mean and is **in-band** (separation −0.05, far short of +0.5).
- ASCII route: printable ratio 1.000 for all (an artifact of the `%95+32` map — carries no
  signal). Coordinate route: top-pair concentration ≤ 0.123, no clustering above chance.
- prime_gap has only 5 distinct values (gaps ∈ {1,2,4,6,8}); its whole band is elevated and
  flat because a low-entropy residue sequence scores slightly above the fully random floor —
  this is a null-band property, not signal (the stream is *inside* that band).

## Conclusion
Reading the prime-gap and prime-index magnitudes as literal data (base-29, mod-29 plaintext,
ASCII, coordinates) yields nothing above the histogram-preserving null. The controls prove the
decode + scorer recover real structure when it exists, so this is a true NEGATIVE, not an
instrument failure. Consistent with the round's strong NULL prior: the signal, if any, is not
in these prime-derived integer streams read as data.
