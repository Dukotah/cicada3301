# LENS S2 — separator / ornament channel

**Verdict: NEGATIVE** (control passed, no channel clears the bar)

## What was parsed
Raw file `data/krisyotam_runes.txt` read directly (not `load_pages`, which strips separators).
- 13,136 runes, 3,551 inline separators.
- Separator histogram: `-` 2764, `/` 604, `.` 183.
- Page/section metadata (`%` 56, `&` 18, `$` 9, `§` 1, digits 1–7) treated as non-content and skipped.
- Run-length stream (runes between separators): len 3552, min 0, max 14, mean 3.70.

## Positive control (PASSED)
Planted "THE PRIMES ARE SACRED":
- Ternary encode (byte -> 5 base-3 digits -> `-/.`) then decode -> recovered **exactly**, score **-4.180**.
- Binary encode (dash/slash bits) -> recovered **exactly**.
Machinery demonstrably recovers a planted separator-type signal.

## Channels tested vs null (shuffle sep types, seed 3301, 200 draws)

| Channel | best score | null_max | clears bar? |
|---|---|---|---|
| (a) sep-type -> bits -> bytes (binary; 3 groupings × MSB/LSB × 8 offsets) | **-5.357** | -3.810 | NO (below null_max+0.5) |
| (a) sep-type -> base-3 -> bytes (ternary) | -8.770 | -8.543 | NO (in-band) |
| (b) run-lengths as ints (mod29 / ASCII) | -6.692 | -6.621 | NO (in-band) |

The single sub‑(-5.5) absolute score, a_binary/dot_vs_rest, is an artifact of a sparse
(9% printable, mostly-zero) bitstream; its shuffle null routinely scores **higher** (max -3.81),
so it is nowhere near the null_max+0.5 requirement. HIT bar = score ≥ -5.5 AND ≥ null_max+0.5;
nothing satisfies the second clause.

## Channel (c) placement vs structure
- Run-length variance ratio vs same-mean geometric (random placement) = **0.307** — separators
  are placed *more regularly* than random, i.e. they track word/segment structure.
- Mean run before `/` = 2.39 (short, line-wrap), before `.` = 4.13, before `-` = 3.96.
  `/` and `.` sit at different structural boundaries than `-`.
- Interpretation: separators are ordinary orthography (word `-`, line `/`, sentence `.`),
  correlated with segment structure — not a hidden number/ornament payload.

## Bottom line
best_score = -5.357, null_max = -3.810. Control recovered a planted signal cleanly, so the
NEGATIVE is trustworthy. The separator/ornament channel carries no readable message under
binary, ternary, or run-length decoding. Placement is structural, not stego.
