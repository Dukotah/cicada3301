# PREREG — Lane B4, Round 10B: PROSECUTE THE OTP VERDICT

Pre-registered **before** any code in this lane was run. Written 2026-08-12.

## 0. What this lane is and is not

This lane does **not** attempt a decode. It audits the repo's central conclusion:

> "LP2 0–54 is OTP-class — a full-length keystream against an external pad with soft
> anti-repeat filtering — therefore information-theoretically unsolvable without the pad,
> therefore unsolvable BY DESIGN."
> (`liber-primus/FINAL-SYNTHESIS.md` l.14/41/90, `ELIMINATION-LEDGER.md` l.18–24,
> `PICKUP-HERE.md` l.15–20, `research/DEAD_ENDS.md` l.198–199)

The object under test is an **inference chain**, not a cipher.

**Coordination (no duplication).** Round 10B lane **B2** forward-simulates short-key
Vigenère + phase drift; lane **B6** hunts non-English plaintext; Round 10 lanes run the
re-transcription, seed sweep and community SOTA. B4 runs *neither* a key search *nor* a
plaintext search. B4 runs **identifiability measurements**: given the repo's own published
statistic battery, which generative models are separated by it and which are not.

## 1. Hypotheses

- **H0 (the repo's position, to be prosecuted):** the measured battery {IoC·N = 1.0000,
  doublet 0.66% vs 3.45%, flat nonzero difference diagonals, entropy 4.8565} *forces*
  "full-length keystream against an external pad".
- **H1 (identifiability):** there exist generative models that are **not** an external pad
  and that reproduce the entire published battery inside sampling noise. If H1 holds, the
  battery is *consistent with* H0, not *evidence for* H0 over its rivals.
- **H2 (the IoC keystone):** the claim "perfectly flat IoC is only reachable by a
  full-length keystream" is false; flat IoC bounds key **period from below** at some finite
  p\*, and p\* is far smaller than 12,956.
- **H3 (the doublet bound):** for any additive cipher `c = p + k (mod 29)` in which the key
  stream `k` is **statistically independent of the plaintext** — this class contains every
  external pad, every PRNG, every raw keytext AND every *transformed* keytext and every
  *derived* long key — the ciphertext doublet rate obeys
  `P(c_i = c_{i-1}) = Σ_d P_Δp(d)·P_Δk(−d) ≥ min_d P_Δp(d)`.
  If `min_d P_Δp(d)` for English-in-futhorc exceeds 0.664%, then the observed rate refutes
  the *entire* plaintext-independent-key class **including the unfiltered external pad**,
  and the load-bearing object is the **filter**, not the pad.
- **H4 (the decisive question):** is there any ciphertext-only measurement that separates
  "external random pad" from "long key derived deterministically from a short seed"?

## 2. Pre-registered numeric thresholds — fixed before running

| Gate | Rule | Reads on |
|---|---|---|
| **G1 reproduce** | my independent recomputation of N, IoC·N, doublet%, entropy must match the published 12,956 / 1.000 / 0.664% / 4.8565 to ±0.001 (IoC), ±0.005 pp (doublet). Failure ⇒ report a transcription/instrument discrepancy and stop. | load-bearing evidence |
| **G2 IoC keystone (H2)** | define p\* = smallest key period whose ciphertext IoC·N is ≥ 2 sd above the flat-null mean in ≥95% of 200 trials at N = 12,956. **If p\* < 1,000, H2 is CONFIRMED** and the "only a full-length keystream" phrasing is an overreach. If p\* > 5,000, H2 is refuted and the repo's phrasing stands. | keystone |
| **G3 doublet bound (H3)** | measure `m = min_d P_Δp(d)` over ≥5 independent English-in-futhorc encodings of ≥100k runes each, using the repo's own greedy multigraph encoder. **H3 CONFIRMED if m > 0.664% in all 5 corpora**, i.e. the observed rate lies strictly below the theoretical floor of the whole independent-key class. Also verify the bound is *tight* by constructing the adversarial key that attains it. | keystone |
| **G4 identifiability (H1)** | a rival model **passes** if all six battery statistics (IoC·N, doublet%, entropy, χ²-uniform, difference-diagonal cv, off-diagonal bigram χ²) fall inside the 95% band of 200 realisations of the repo's own pinned model (OTP + soft filter). **H1 CONFIRMED if ≥2 structurally distinct rivals pass.** | forcing vs consistent |
| **G5 discriminator (H4)** | build a concrete derived-key model (SHA-256 counter-mode keystream from a short seed) + the same soft filter, and run the *entire* battery. If no statistic separates it from the external-pad model at p < 0.01 after Bonferroni over the battery, then H4 is answered **NO** and the OTP claim is declared **not falsifiable from the ciphertext**. | the decisive question |

## 3. Controls (mandatory)

- **Null control:** the real LP2 stream shuffled (seeded, 200 shuffles) — must land at
  IoC·N ≈ 1.000, doublet ≈ 3.45%. Any instrument that reports the shuffle as "special" is
  broken and its result is void.
- **Positive control (instrument sensitivity):** plant a *known* periodic key over English at
  periods 1, 5, 20, 40, 100, 400, 1000 and confirm the IoC instrument recovers the planted
  period for small p and demonstrably loses it at large p. An instrument that cannot see a
  planted period-5 key proves nothing about the absence of a period-500 one.
- **Positive control (doublet bound):** plant (a) English + true random pad → expect
  3.45 ± 0.16%; (b) English + the adversarial bound-attaining key → expect exactly
  `m`. Both must hit their predicted values or the bound derivation is wrong.

## 4. Deliberate re-dig statement

I re-derive the four headline statistics and the autokey difference-diagonal test even
though they exist in the repo (`analysis/run_stats.py`, `analysis/CAMPAIGN-X-FINDINGS.md`,
`analysis/campaign11_pin_the_filter.py`, `recon/i9_*`). Reason: **a prosecution may not
take the prosecuted party's own arithmetic on trust**, and the audit turns on whether each
number is a theorem or a simulation-backed inference — which cannot be graded without
re-running it. Total cost ≈ 2 minutes of compute. Everything else in the lane is new.

## 5. What would make me report "the verdict holds"

If G2 fails (p\* > 5,000), G3 fails (m < 0.664%), and G4 finds no passing rival, then the
battery really does force the OTP reading and I will say so in those words. A
prosecuted-and-surviving verdict is stronger than an unexamined one and I will report it
as such.
