# Round 11 — the NUMBER CHANNEL armada (pre-registration)

_Registered 2026-08-17, before running the lenses. Follows
`analysis/NEXT-ARMADA-ROADMAP.md`. Phase 0 instrument = `lib_numchannel.py`, gated by
`PHASE0-GATE.py` (**PASS** 2026-08-17: reproduces the 12,956-rune stream, decrypts AN END,
English −4.42 vs noise −7.50 sep 3.08, N1 plant-recover clean)._

## Thesis

Every exclusion proof in this repo (flat IoC, doublet deficit, autokey refutation, entropy)
lives on the mod-29 **letter** stream. The signed hints point at the **numbers** ("the primes
are sacred", "either the words or their numbers", "their numbers are the direction"). Arithmetic
on the raw prime **magnitudes** (sums, gaps, digits, base conversions) lives in ℤ, outside the
group where we proved everything. This round attacks that space + the physical channels never
transcribed. Strong prior is still NULL (the letter-stream proofs are real); the value is that
these transforms and channels are genuinely untried, and follow the hints literally.

## Shared decision rule (every lens)

- **Scale:** English (runeglish) ≈ −4.0/−4.4; noise floor ≈ −7.5 (from Phase 0).
- **Positive control FIRST:** each lens must recover a *planted* signal under its own machinery,
  else it reports INCONCLUSIVE, not NEGATIVE.
- **Null:** the size-matched, histogram-preserving shuffle (`nc.shuffled`, seed 3301), ≥200 draws.
- **HIT bar:** score_norm ≥ −5.5 **AND** ≥ (null_max + 0.5) **AND** survives ≥3 refute-by-default
  verifiers, each of which **recomputes its false-positive ceiling at its own N** (the PA-2
  discipline). Anything else = NEGATIVE (in-band) or INCONCLUSIVE (control failed).
- No re-runs of any ELIMINATION-LEDGER lane.

## Lenses

**Phase 1 — number channel**
- **N1** cumulative-gematria feedback autokey: key[i]=f(Σ gematria[0..i−1]) for f∈{mod29, φ,
  digit-sum}; sign ±, forward/reverse, per-segment-reset vs continuous. (Feedback class the
  verdict left OPEN.)
- **N2** prime-gap and prime-index streams read as data: base-29/base-60/ASCII/coordinates.
- **N3** whole book as one integer: primality/factor structure of segments and the full number.
- **N4** digit-plane separation: primes in base {3,5,7,10}, each plane as a mod-N keystream and
  as text.
- **N5** totient-ladder escalation: φ(φ(p)), Carmichael λ(p), totient-of-running-sum as
  keystreams (decrypt + score). Positive control = reproduce AN END with φ(prime).

**Phase 2 — un-transcribed channels**
- **S1** interrupter-position channel: gaps between ᚠ (index-0) occurrences as an integer stream
  → decode base-29/ASCII/coordinates; also test gaps as "direction" numbers.
- **S2** separator/ornament channel: the −, /, ., % separators in `data/krisyotam_runes.txt` as a
  binary/ternary channel (RECON-A flagged "19 separator disagreements, ornaments never read").

**Phase 3 — verify + synthesis:** adversarial refutation of any hit; completeness critic; write
`SYNTHESIS.md` and fold verdicts into the nav docs + ELIMINATION-LEDGER.
