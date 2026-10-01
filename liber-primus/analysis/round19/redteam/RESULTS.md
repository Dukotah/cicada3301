# Round 19 — LANE 3 (RED-TEAM on this repo's own claims) — RESULTS

**Verdict: NO-ERROR-FOUND** on the targeted construction-class / coverage closure, with **one
actionable finding** (a trust-anchor spec gap, sub-audit a) and the **AN-END holdout RECOVERED
blind**. Written under ARMADA-DOCTRINE R6/R7 — report FOUND-ERROR or NO-ERROR-FOUND, never
"confirmed"; state what was NOT covered and what reopens the lane.

Artifacts: `run_redteam.py`, `results.json` (this folder). Reused instrument:
`../instrument/power_envelope.py` (validated 9-register panel + R3 helpers). `tests/validate.py`
re-run green this phase; `analysis/handoff/validate_ledger.py` reports 0 unsound negatives.

> **Honesty note (R6 in action).** A first pass of this lane logged a FOUND-ERROR — "AN-END's
> positional φ(prime) keystream is absent from every swept catalog" — after auditing only
> `campaign18/armada/numeric_skip.py` and `round11/lib_numchannel.py`. That was **wrong**, and
> continued auditing refuted it: `campaign18/armada/rosetta_keys.key_phi_prime` is byte-identical
> to AN-END's keystream and WAS swept skip-aware over all 55 pages. The retraction is itself the
> result — the doctrine's "read coverage, don't re-run measured ground" discipline worked.

---

## The AN-END HOLDOUT — RECOVERED (blind)

Mandatory doctrine gate. Given only the ciphertext (`data/sources/relikd_p56_an_end.txt`,
85 runes) and AN-END's **stated external input** — the prime sequence (page 05: "the primes are
sacred ... the totient function is sacred") — and **not** handed the key, the keystream
`k_i = (p_i − 1) mod 29` (positional running totient of the i-th prime, shift-DOWN) was derived
and decoded:

> **AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO IT IS THE DUTY OF EUERY
> PILGRIM TO SEEC OUT THIS PAGE** (OF=OE, SEEC=SEEK, lossy transliteration)

7/7 target phrases recovered; one F-interrupter at CT position 56; beam/decode score −5.282
(clears the −5.5 confirm floor). Holdout = **RECOVERED**.

---

## NO-ERROR-FOUND — the coverage closure holds (PREREG sub-audit b + target claim)

The load-bearing inference red-teamed was *"the number-theoretic / totient keystream family is
covered as NULL for LP2 0–54."* AN-END is the one page with a known generative keystream, used as
the probe. Measured result: **the exact AN-END construction is covered.**

**1. Crib-drag (b).** Crib-dragging AN-END's known plaintext back through the keystream recovers
a stream **exactly equal to φ(prime)** (`recovered_equals_phi_prime = true`). Of the enumerable
generator family tested (8 base generators × {value, diff, sum} × sign × atbash = 96 streams),
the only family that fits is `phi_prime` itself (the second apparent hit is the trivial atbash/
sign mirror `(N−(−k))≡k` of the same stream). **No second, index-extensible generative family
fits.** Q5 kill condition met: only φ fits → no generative-family leak.

**2. Catalog audit.** Running candidate keystreams through the live LP2 beam on the real AN-END
ciphertext (AN-END used as a positive control *for the generator catalog*):

| keystream | construction | beam EN-quadgram | clears −5.5? |
|---|---|---|---|
| **φ(prime) POSITIONAL (AN-END TRUE)**, sign −1 | positional, consecutive primes, −1 | **−5.282** | **YES** |
| `ks_totient_n` (campaign18 numeric) | φ(n) of consecutive INTEGERS | −7.302 | no |
| `primes` (campaign18 numeric) | consecutive primes | −7.770 | no |
| `v_totient` (R11/R22/R24) | ciphertext-SELF-keyed p(ct)−1 | −7.0…−7.6 | no |

The campaign18 `numeric_skip` catalog and the R11/R22 `v_totient` (despite its `# phi(prime)=p-1`
comment) are **different constructions** from AN-END's and score as noise on it. **But** —

**3. The exact construction IS swept.** `campaign18/armada/rosetta_keys.key_phi_prime` =
`(prime_i − 1) mod 29` is **byte-identical** to the AN-END keystream
(`anend_true_IS_in_rosetta_key_phi_prime = true`), and `rosetta_sweep.py` ran it **skip-aware
over all 55 unsolved pages, both signs, both atbash** → **NULL** (`RUN-rosetta.log`, global best
−6.334; on page 30 `phi_prime` itself was that page's best at −6.90, still noise). Independently,
`round11/N5/RESULTS.md` uses positional φ(prime) as its **validated positive control** (−5.282,
matching this lane exactly) and sweeps the totient *ladder* (φ(φ(p)), λ(p), running-sum variants,
positional and rune-indexed) over the full unsolved stream → **NEGATIVE** (all −7.1…−7.5).

So the totient family — including AN-END's exact member — is genuinely covered by a sound,
skip-aware, control-validated sweep. **NO-ERROR-FOUND.**

**What this NEGATIVE does NOT exclude (R7).** (i) The crib uniqueness in (1) is for AN-END's own
combiner (plain shift-DOWN + F-interrupter skips), not the pinned soft-anti-repeat REWRITE
combiner. (ii) `rosetta_sweep` scored on the English quadgram only; per L7-A the totient-family
null is an English-register null (N5 likewise) — a non-English plaintext under φ(prime) is not
excluded by these runs. (iii) The ladder in N5 is finite; a totient-derived generator outside
{value, φ∘φ, λ, running-sum, ±sign, additive-offset, positional/rune-indexed} is not excluded.

---

## Actionable finding — trust-anchor spec gap (PREREG sub-audit a)

AN-END's φ(prime) solve is documented in prose (`docs/SOLVED-PAGES-AND-INTERRUPTERS.md`, page
73 / LP2 p56) and the keystream is correctly implemented in `rosetta_keys.key_phi_prime` and used
as a control in N5 — but it is **absent from the machine trust anchor**: `SOLVED-PAGES.json` /
`tests/validate.py` validate only pages 01/03/05/06/14. The trust instrument the whole repo's
negatives rest on has **never reproduced** the φ(prime) keystream as a *validated solve*. This
lane reproduces it blind and clean.

**Recommendation:** add page 73 (AN-END) to `SOLVED-PAGES.json` with method
`phi_prime (positional totient of primes, shift-down) + 1 F-interrupter at CT pos 56`. It is the
project's only solved generative-keystream page; promoting it to the trust anchor would make the
positional-prime-totient + F-interrupter construction a permanent CI-guarded positive control.
(Severity: low — it is a spec/CI-coverage gap, not a decode error; the keystream and its null are
both already correct in the research code.)

---

## R3 columns

All 12 `coverage_gap_rows` in `results.json` persist IoC·N, min-distinct-32, best non-English LM
over the EN/LA/OE/DE/CY/EN_NOVOWEL panel (+ register), and gzip compressibility, computed on the
correct-key decode. The crib-recovery and generator-family legs are deterministic equality checks
(power 1.0 by construction), not scored sweeps.

---

## Reopens (R7)

- The totient coverage reopens as a **register** question, not a construction question: re-run
  `rosetta_sweep`/N5's φ(prime) ladder under the L7-A non-English panel (English-only nulls are
  near-meaningless per R18 L7-A). This is the single cheapest reopener and the one this lane's
  measured power most directly licenses.
- Minor doc hygiene: `lib_numchannel.py:47`'s `# phi(prime)=p-1` comment is misleading
  (`v_totient` is ciphertext-self-keyed, not positional); and `COVERAGE-MATRIX.md §A` / the
  R22-C/R24 ledger lines should name *which* totient constructions were swept (positional
  φ(prime) via rosetta = covered; φ(n)-of-integers + self-keyed = also covered but distinct),
  so a future reader does not re-derive the false gap this lane initially logged.
