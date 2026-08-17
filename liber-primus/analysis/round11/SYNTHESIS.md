# Round 11 — the NUMBER CHANNEL armada: synthesis

_Run + synthesized 2026-08-17. Pre-registration: `PREREG.md`. Instrument: `lib_numchannel.py`,
gated by `PHASE0-GATE.py` (PASS). 7 lenses, each with a validated positive control and the
seed-3301 histogram-preserving null._

## Bottom line

**The number channel is empty. All 7 lenses NEGATIVE, all 7 positive controls PASSED, 0 hits.**

This is the round the hints demanded and nobody in ten years had systematically run. Every
prior exclusion proof lived on the mod-29 *letter* stream; the signed hints ("the primes are
sacred", "either the words or their numbers", "their numbers are the direction") point at the
*value* channel, and arithmetic on the raw prime magnitudes lives in ℤ, outside the group where
those proofs hold. We built a validated instrument for that space and attacked it. It carries no
recoverable message under any transform we tried. The verdict is **tightened, not overturned**:
the hints' literal target is now a measured negative, not an unexamined loophole.

Crucially, every negative is *interpretable* because every lens first recovered a planted signal
through its own machinery — these are true negatives, not blind scans (the PA-2 failure mode).

## Verdict table (English scale: ~−4.4 English, ~−7.5 noise; HIT bar −5.5 AND null_max+0.5)

| Lens | Hypothesis | Best real | Null max | Control | Verdict |
|---|---|---|---|---|---|
| **N1** | cumulative-gematria feedback autokey (open "feedback" class) | −7.438 | −7.446 | ✓ recovered PT- & CT-feedback plants exactly | **NEGATIVE** (48 configs, all in −7.44…−7.48) |
| **N2** | prime-gap / prime-index streams read as data | −6.951 | −6.901 | ✓ PARABLE index route + planted msg recovered | **NEGATIVE** (in-band; prime_gap has only 5 distinct values) |
| **N3** | whole book / segments as number-theoretic objects | −7.440 | −7.466 | ✓ 11/11 (Mersenne, RSA-semiprime, perfect power) | **NEGATIVE** (0 primes/powers/notable in 55 segs; structure *below* null) |
| **N4** | digit-plane separation (bases 3/5/7/10) | −5.728 | −5.722 | ✓ planted-plane recovered | **NEGATIVE** (42 trials, in-band) |
| **N5** | totient-ladder escalation φ(φ(p)), λ(p), Σ-totient | −6.667 | −6.722 | ✓ reproduced AN END via φ(prime); φφ plant recovered | **NEGATIVE** (+0.055 over null, needs +0.5) |
| **S1** | interrupter-position channel (458 F-runes, 457 gaps) | −5.994 | −5.997 | ✓ planted gap-message recovered (sep 2.26) | **NEGATIVE** (12 routes in-band) |
| **S2** | separator / ornament channel | −5.357 | −3.810 | ✓ ternary + binary plants recovered exactly | **NEGATIVE** (real < null; see finding below) |

## Genuine sub-findings worth keeping (beyond "null")

1. **N3 — the ciphertext is anti-special, not special.** Across the 55 unsolved segments there
   are **0** primes, 0 perfect powers, 0 Mersenne-ish, 0 near-hash/RSA bit-lengths, 0
   RSA-shape semiprimes. Real "notable structure" total = **0 vs a null mean of 0.125** — the
   real number stream has *less* number-theoretic coincidence than random. The "sacred 2048-bit
   prime" intuition, already dead at pp49-51 scale, is dead at book scale too, and then some.
2. **S2 — the separators are typography, not a channel (resolves a RECON-A open flag).**
   RECON-A had flagged "19 separator disagreements / ornaments never read." Read now: mean run
   length before `/` = 2.39, before `.` = 4.13, before `-` = 3.96 → `/` marks line-wrap, `.`
   marks sentence, `-` marks word. Run-length variance ratio 0.307 (more regular than random).
   They track linguistic structure; they do not carry a hidden payload. The flag is closed.
3. **N2 — the gap channel is low-entropy.** prime_gap over the 29 gematria primes takes only 5
   distinct values, so "gaps as direction/data" is information-poor by construction; the
   printable-ratio 1.000 that looked promising is a mapping artifact (every byte forced in range).

## What this does and does not change

- **Does NOT reopen anything.** No hit, nothing verified. OTP-class / unsolvable-by-design holds.
- **Tightens the boundary:** the hint-literal number channel — the single most-cited "surely
  they meant the primes" intuition in the whole mystery — is now a measured, control-validated
  negative across feedback keystreams, number-theoretic structure, digit planes, the totient
  ladder, and the two physical channels (interrupters, separators) nobody had transcribed.
- **Publishable-honest:** the novel contributions are the value-channel instrument + the
  "anti-special" number-theoretic result (N3) + the separator-is-typography resolution (S2) +
  the first control-validated null on the feedback-autokey class (N1) at the exact place the
  verdict said was "open but unbounded."

## Do NOT re-run

All 7 lenses are recorded with controls + nulls. The number channel is closed the same way the
letter channel is. The only residue from the roadmap not yet run is external/low-prior (PA-3
binary pads under the skip-aware decoder; the dense-OTP re-segmentation) — those are inputs and
imaging, not more transforms of the stream we already have.
