# LENS N5 — Totient-ladder escalation — RESULTS

**Verdict: NEGATIVE**  (control PASSED; no ladder generator escapes the null band)

## Thesis
The solved LP pages (e.g. AN END) escalate to a `phi(prime)` keystream, applied
**positionally** — `key[i] = (p_{i+1} - 1) mod 29` over consecutive primes, independent of
the rune values. N5 tests the NEXT rung of totient-family generators as decrypt keystreams
over the 12,956-rune unsolved stream:

- `phi_phi_prime`   — iterated totient `phi(phi(p_i))` (positional) — the primary next rung
- `lambda_prime`    — Carmichael `lambda(p_i)` (positional; == p-1, control cousin)
- `phi_runsum`      — `phi(` running sum of consecutive primes `)`
- `phiphi_runsum`   — `phi(phi(` running sum `))`
- `lambda_runsum`   — `lambda(` running sum `)`
- `phi_primeindex`  — `phi(i)` totient of position index
- `phi_phi_prime_RI`— rune-INDEXED iterated totient (uses the runes' own prime values)
- `phi_runsum_RI`   — `phi(` running sum of the runes' OWN prime magnitudes `)`

Each swept over sign +/-, full additive offset 0..28, continuous whole-stream AND
per-segment-reset (best offset per page).

## Positive control — PASSED
- AN END via `ciphers.prime_totient_stream` (library path): head =
  `ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHA`, decrypt score **-5.282** vs raw **-7.738**.
- My own positional `lambda(prime)` generator reproduces the SAME head — my ladder machinery
  is on the correct positional keystream, not a rune-indexed mistranslation.
- Ladder-machinery plant: encrypt real English with `phi_phi_prime`, decrypt with the same
  generator → recovered EXACTLY. plain **-4.437** → ct **-7.502** → rec **-4.437**.
  The instrument recovers a planted signal cleanly (noise ~-7.5 → English ~-4.4).

## Result on the unsolved stream
| generator | continuous best | per-segment best |
|---|---|---|
| phi_phi_prime | -7.456 | -7.136 |
| lambda_prime | -7.474 | -7.126 |
| phi_runsum | -7.460 | -7.127 |
| phiphi_runsum | -7.455 | -7.134 |
| lambda_runsum | -7.451 | -7.135 |
| phi_primeindex | -7.455 | -7.124 |
| phi_phi_prime_RI | -6.748 | **-6.667** |
| phi_runsum_RI | -7.456 | -7.134 |

- **Best real score across all N5 runs: -6.667** (rune-indexed phi_phi, per-segment)
- **Null** (200 shuffles, seed 3301, matched pipeline = winning generator + full offset sweep):
  mean **-6.760**, **max -6.722**
- HIT bar = max(-5.5, null_max + 0.5) = max(-5.5, -6.222) = **-5.5**

## Decision
Real best -6.667 is **below -5.5** and only **+0.055 above null_max** (needs +0.5).
Every generator sits inside its own shuffled-null band. The per-segment lift of the
rune-indexed variants is a free-parameter artifact (best-of-57 offsets per page) — the null,
which gets the same sweep, absorbs it. **NEGATIVE.**

## Interpretation
The next rungs of the totient ladder (iterated totient, Carmichael lambda, totient-of-
running-sum, prime-index totient) do NOT key the unsolved stream. The solved-page escalation
does not continue with these generators. Consistent with the round's strong NULL prior; the
value here is that these specific totient generators are now explicitly eliminated.
