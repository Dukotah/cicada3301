# Round 16 / KDF — PRE-REGISTRATION (full Stage-A)

_Written before the run. Pre-registered 2026-08-23._
_Trust anchor: `python tests/validate.py` from liber-primus/ = ALL VALIDATIONS PASSED._

## Inherited from Round 15 / KDF

This lane is the FULL Stage-A execution of the harness pre-registered in
`analysis/round15/KDF/PREREG.md`. Everything in that pre-registration holds without
change — hypothesis, decision threshold (BAR = −5.5), escalation protocol, what-is-not-covered.
Only the smoke-run limit is lifted.

## What changed

Round 15 ran ONLY a 10-item SMOKE (secret list capped to 10 + plant).  
Round 16 / KDF runs the **full** Stage-A cross product:
- 534 unique secrets (504 core + 30 passphrases × 4 forms, deduplicated)
- 27 KDF configs (PREREG §4.2)
- 3 Stage-A salts: `empty`, `3301`, `self` (PREREG §4.5)
- 2 reductions × 2 signs × 2 atbash × 2 directions = 16 decode variants per (secret, kdf, salt)
- Offset 0 only (Stage A)
- 120-rune head (Stage A)

Estimated decode count: ~692k. Estimated wall time with 11 parallel processes: ~2–3 min.

## Gates (from PREREG §5)

**K1** — D3 expander control. Required: beam(correct) ≥ −5.5, char-recovery ≥ 0.90,
rigid(correct) < −6.0. The smoke run did not run K1; this run will.

**K2** — plant-and-recover. Already PASSED in the smoke run (score −4.186, rank #1,
reads THEPRIMESARESACRED…). Will be re-confirmed or trusted from smoke run.

Both must pass before any null is trusted as NEGATIVE.

## Decision threshold (PREREG §6)

HIT iff `score_norm ≥ max(−5.5, null_max + 0.5)`.  
The null band is recomputed fresh against the 120-rune head in this run.

## RAM/time constraint

Full sweep fits in ~8 min on 11 CPUs. If PBKDF2-100000 and scrypt time exceeds budget,
subsample those families at N=100 secrets each and report the exact bound.

## Coverage bound declared in advance

If sweep completes: 27 KDF configs × 534 secrets × 3 salts × 16 decode variants = 692k decodes.
If expensive KDFs subsampled: reported in RESULTS.md as an explicit gap.
