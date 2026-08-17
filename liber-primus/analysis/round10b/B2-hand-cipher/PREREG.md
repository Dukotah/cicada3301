# PREREG — Lane B2, Round 10B: THE HAND-CIPHER HYPOTHESIS

Pre-registered **before** any code was run. Written 2026-08-12.

## 0. How this differs from prior art (stated before running)

| Prior result | Its search space | Why it does not cover B2 |
|---|---|---|
| iter-11 `recon/i11_smirnov/` — "deterministic Smirnov/Carlitz rewrite over a linear ordering" RETIRED (LEDGER l.604) | A *deterministic un-bump map* applied to an otherwise **random/OTP pad**. 116 candidate orderings. | It tests the *rewrite function*, holding the base as a pad. B2 holds the *rewrite* loose (6 rules) and replaces the base with a **short-key Vigenere**, keyspace 29^k (k=4..12), i.e. ~10^6..10^17 — a different object entirely. |
| Round 5 #4 HALFTIDE — lag-k spectrum, suppression purely at lag 1, lags 2–6 at chance | Lags **2..6 only**, framed as an interleave test. | Does not reach k=7..12, and was never interpreted as a key-length detector under phase drift. B2 needs lags 1..400. |
| Round 5 #2 TIDELINE — inter-doublet gaps geometric (KS p=0.69) | Placement of the *residual* doublets. | Consistent with B2: under B2 the residuals are the p_keep≈0.18 survivors, also geometric. Does **not** discriminate. |
| Campaign XIV P1–P2 full-lag self-coincidence (per PA-2 census: 0 peaks >5σ, column IoC max 1.087) | The exact statistic B2 needs. | Prior *measurement* of the real stream exists — but **no forward simulation** establishes what a drifting short-key Vigenere would put there. Without that, "flat" does not license "not a short key". Supplying the forward model is the point of this lane. |
| Ledger A: "all periodic keys 1–40 (both directions + Atbash)" | **Rigid** periodic-key decode. | A rigid decoder is exactly what phase drift defeats. That is the lane's whole premise. |
| Round 6 TRANSITION-STRUCTURE — no 2nd-order structure beyond lag-1 identity | Transition lattice of the ciphertext. | Orthogonal: B2 predicts structure in *coincidence at lag k*, not in the 1-step transition tensor. |

**Deliberate re-dig statement:** I re-measure the full-lag coincidence spectrum of the real
stream even though Campaign XIV measured it, for one reason: I need it on the *same instrument*
and the *same 0–54 concatenation* as my forward simulation, so the comparison is apples-to-apples.
The re-measurement is ~1 second of compute. Everything else in the lane is new.

## 1. Hypothesis (H_B2)

LP2 pages 0–54 are a **short-key Vigenere** (key length k, 4 ≤ k ≤ 12, over the 29-rune
Gematria Primus) enciphered **by hand**, where the author applied a **local no-repeat correction**
whenever the next ciphertext rune would equal the previous one. The correction perturbs the
key/plaintext alignment, so the effective key phase is **piecewise constant with occasional
jumps** ("phase drift"). Under H_B2 the observed doublet rate (0.66%), the flat IoC (1.0000)
and the absence of a Kasiski period are all artefacts of the correction habit, not evidence of
a one-time pad.

Correction rules simulated (each also in a *soft* form fired with probability `p_fix`, so the
residual doublet rate can be tuned to the observed 0.66%):

- **R1 BUMP** — add +1 to the offending ciphertext rune. *(no phase drift)*
- **R2 KEYADV** — advance the key one extra step and re-encipher the same plaintext rune. *(drift +1)*
- **R3 KEYRESET** — reset key phase to 0 and re-encipher. *(phase reset)*
- **R4 PTSKIP** — drop the offending plaintext rune, take the next one. *(drift +1)*
- **R5 INTERRUPT** — emit an interrupter rune (ᚠ) instead, consuming neither key nor plaintext. *(drift +1)*
- **R6 REPICK** — re-pick a uniformly random rune ≠ previous. *(no phase drift)*

## 2. Instrument and the decisive statistic

κ(L) = P(c_i == c_{i+L}) over the concatenated unsolved stream (pages 0–54, n = 12,956).
Random expectation 1/29 = 0.034483; SD at this n ≈ 0.00160.

**Why κ(k) is the right discriminator, stated in advance:** κ(k) at the true key length is a
**local** statistic — it is elevated for every pair (i, i+k) that has *no drift event between
them*. Global phase drift, however large, cannot destroy it; only drift *within a k-window* can.
With drift rate ρ per position, the expected elevation is ≈ (1−ρ)^k · (IoC_plain − 1/29).
So H_B2 makes a hard, falsifiable prediction and cannot hide behind "the drift flattened it".

Secondary instruments: IoC·29 of the whole stream, IoC·29 of columns under every assumed
period 1..40 (the classic key-length detector), Kasiski trigram-spacing GCD histogram,
doublet rate, entropy.

## 3. Pre-registered pass/fail thresholds

**Stage 1 (forward simulation) — decides whether H_B2 survives at all.**

- **S1-PASS (H_B2 survives, go to Stage 2):** at least one (rule, k, p_fix) configuration
  simultaneously produces
  (a) doublet rate in [0.0050, 0.0085] (observed 0.0066),
  (b) IoC·29 of the full stream in [0.98, 1.03] (observed 1.0000),
  (c) **max κ(L) over L ∈ [2, 40] no more than +4σ above 1/29** (i.e. ≤ 0.0409), matching the
      real stream's own flatness, and
  (d) max column-IoC·29 over assumed periods 2..40 ≤ 1.10 (Campaign XIV's real-stream max 1.087).
- **S1-FAIL (H_B2 REFUTED):** every configuration that satisfies (a)+(b) violates (c) or (d) —
  i.e. any hand-correction scheme that reproduces the doublet deficit **necessarily leaves a
  key-length signature that the real ciphertext does not have.**
- I additionally pre-register reporting a **detection wall**: the largest key length k_max for
  which the simulated κ(k) still exceeds the real stream's observed max κ over L∈[2,400] by >5σ.
  Key lengths above k_max are *not* excluded by this test and must be handed to future work.

**Stage 2 (decoder), run only if S1-PASS.**
- **POSITIVE CONTROL (mandatory, gates everything):** plant known English enciphered with a
  random k=8 key under the surviving rule, at the surviving p_fix, over a 1,200-rune segment.
  The drift-tolerant decoder must recover ≥ 80% of plaintext runes exactly. If it cannot, I
  report the detection limit instead of a result and make no claim about the real ciphertext.
- **REAL-DATA CALL:** a break is claimed only if the decoded segment scores better than
  **−5.0 per character** on the repo's page-scale quadgram scale (English −4.2..−5.0,
  random −7.3) **and** the output is human-readable English **and** it reproduces under
  `liber-primus/tests/validate.py` conventions. Anything else is reported as negative.

## 4. Null controls (mandatory)

- **N1 shuffled-LP2**: random permutation of the real stream (destroys all order structure).
- **N2 memoryless + soft anti-repeat**: the repo's own established construction — i.i.d. uniform
  base with the p_keep≈0.18 anti-repeat filter, no key at all. This is the incumbent model;
  if the real stream's κ spectrum is indistinguishable from N2 and distinguishable from every
  B2 configuration, the incumbent wins.
- **N3 rigid short-key Vigenere, no correction** — sanity anchor: κ(k) must spike hugely here,
  proving the instrument can see a key length at all.

## 5. What would make me wrong

- A correction rule I did not think of that both suppresses doublets to 0.66% *and* erases κ(k)
  for k ≤ 12. (I mitigate by including a rule that resets phase and one that inserts symbols —
  the two most phase-destructive plausible habits — and by scanning p_fix.)
- A key length > k_max, which this test genuinely cannot see. Reported explicitly, not hidden.
