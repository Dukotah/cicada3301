# Round 16 — the derived-keystream armada (fresh, 2026-08-23)

_Drafted 2026-08-23. Executes the unrun body of `round15/CAMPAIGN-PLAN.md` plus its
follow-ons, all inside the **one hypothesis class the ciphertext cannot rule out**: a
short-seed **derived** keystream (finite keyspace, brute-forceable), the branch D3 exposed
(`round12/D3/RESULTS.md`) and the only compute that can possibly succeed._

## Why this is the fresh run, not a repeat

Everything eliminated in this repo lives on the mod-29 **letter** stream, or in the
**external-pad** branch (information-theoretically closed) — or was a bare, single-application
derived key (B-04, NEGATIVE). What has **never been run at scale**:

1. **Key-stretching KDFs** — `PBKDF2 / scrypt / EVP_BytesToKey / iterated-hash`. A
   cryptographically literate 2013–14 author deriving a reproducible pad from a memorable
   secret would reach for a KDF-with-iteration-count, not a bare hash. Gate K2 already
   **passes** (planted `PBKDF2-SHA256` seed ranks #1, reads `THEPRIMESARESACRED…`). Only a
   10-item smoke test has run.
2. **The uncovered PRNG generators** — PHP `mt_rand` (period-correct for Cicada's PHP stack),
   .NET `System.Random`, ISAAC, BBS, LFSR/Geffe/Gollmann. "Seeded PRNGs, do not re-run" was a
   ~3%-of-keyspace coverage bound wearing a closed label.
3. **A-03 haplography count-audit** — the cheap falsifier: the whole OTP-class verdict rests on
   the 0.664% doublet *deficit*; no audit ever checked rune **count** (only identity). If ~20
   of the 86 doublet sites are transcription **merges**, autokey returns to the table.
4. **The zero-false-positive batch** — E-01 RSA/PKCS#1, E-02 meta-parameters, H-03 micro-crosses,
   H-01 onion HTTP. Analytic FP probabilities → decision-grade, minutes of compute apiece.
5. **F-01 LP2-as-pad inversion** — the unsolved pages as key material against every other
   machine-readable Cicada object. Finite, never run.
6. **The matched runic scorer** — +18% separation (34.4σ→40.5σ), productionized so every lane
   above is harder to fool.

## Discipline (from `PICKUP-HERE.md` §"how to start a fresh armada without repeating one")

- **Trust coverage bounds, distrust terminal verdicts** — including our own.
- Every lane is pre-registered: hypothesis + pass/fail threshold + positive control + size-matched
  null, written before the run. A null with a **failed** positive control is not evidence.
- Heavy sweeps (KDF, PRNG) are **bounded to a stated coverage bound**, not run to exhaustion —
  the machine is RAM-constrained. "Swept X, best score Y vs bar Z, control passed" is the
  deliverable, not "exhausted."
- No branches. Results land on `master`; the four navigation docs + `LEDGER.json` are updated
  when the round finishes (`CLAUDE.md`).

## Execution waves (RAM-aware: heavy lanes staggered, not concurrent)

- **Wave 1 (light, parallel):** matched scorer · A-03 haplography bound · zeroFP batch · F-01.
- **Wave 2 (heavy, sequential):** KDF full Stage-A sweep → PRNG family (validate each generator
  against a reference implementation first, then beam-sweep a period-appropriate seed range).
- **Wave 3:** adversarial verify (refute-by-default) any hit at its own N; synthesis +
  coverage bounds; nav-doc + `LEDGER.json` update. A genuine solve becomes the CicadaSolvers
  writeup; a null becomes a tightened bound.

## Honest expectation

Most or all of this returns negative. It is worth running because the derived branch is **cheap
to eliminate and impossible to eliminate by argument**, its controls pass (so a real hit would
be caught), and every lane leaves a coverage bound that makes the next attempt cheaper.
</content>
</invoke>
