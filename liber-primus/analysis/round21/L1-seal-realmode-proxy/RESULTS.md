# L1 RESULTS — Seal the real-mode held-out proxy (disjoint k-folds)

_Run 2026-08-29, AFTER the PREREG was frozen 2026-08-28. Binding: `ARMADA-DOCTRINE.md`.
Trust anchor `python3 tests/validate.py` → `ALL VALIDATIONS PASSED` (5/5) both before and after
this lane. No SWEEPROW/3 field order was touched (P-d holds — the lane ships a drop-in real-mode
proxy behind `recovery_source`, it does not re-order any store)._

## Verdict: KILL — the no-oracle gate is provably leaky. Report as a MEASURED BOUND.

The strengthened disjoint-fold proxy **improves** the no-oracle catch enormously over the single
cut (0.33 → 0.80 at the best genuine-safe cell) but **does not reach the pre-registered 0.90
catch** on the planted-45, and its best genuine-safe cell **fails to generalise** the false-reject
cap on the held-out surrogate. Per PREREG Q5 KILL clause: **Round 21's bar-clearing survivors are
reported as flagged-for-oracle, never auto-certified.** High-prior lanes still run (coverage × power
bounds are unaffected); only auto-HIT-calling is withheld until an oracle-free gate ≥0.90 exists.

`SEAL_PASS = false` (`tuning_pass=false`, `heldout_surrogate_pass=false`).

## Positive controls fired FIRST and PASSED (gate satisfied)

A null from this instrument is trustworthy only after both controls pass (doctrine mechanic 2).
Both did, so the negative result below is a real measured bound, not an artefact of a dead instrument.

| control | expected | measured | status |
|---|---|---|---|
| **Hallucination population** reproduces S-RESCOPE bit-identically | 45 cases | **45** | PASS |
| **Single-cut baseline** (the leak being fixed) | 15/45 (33 %) caught | **15/45 = 0.333** | PASS — reproduces the FOUND-ERROR exactly |
| **Genuine-decode panel** (correct key, EN_MODERN) | ≥10, all true-recovery ≥0.95 | **20/20**, min true-recovery 0.971 | PASS |
| `panelmax_bar` exact/1e6 | 7.634 (R19/R20 value) | **7.6341931878728095** | PASS — same bar |

Because the single-cut baseline reproduces the exact 15/45 the PREREG set out to fix, the leak this
lane targets is confirmed present before the fix is measured.

## Catch × false-reject SURFACE (the three conditionals, reported together — Q4)

Conditionals held fixed for every cell: **key space = correct key** (the hardest case — the
hallucinations are correct-key vowel-dropped-English overfits); **decoder relation = `exact`
preset**; **adjudicator register = EN_NOVOWEL argmax**. Varied: fold count `k ∈ {2,3,4,5,6}` ×
agreement rule `∈ {min, mean, frac_pass}`.

| k | rule | catch (of 45) | catch rate | genuine false-reject (of 20) | FR rate | ≥0.90 catch? | FR ≤0.10? |
|---|---|---|---|---|---|---|---|
| 2 | min/mean/frac | 19 | 0.422 | 1 | 0.05 | no | yes |
| 3 | min | 30 | 0.667 | 5 | 0.25 | no | **no** |
| 3 | mean | 26 | 0.578 | 3 | 0.15 | no | **no** |
| 3 | frac_pass | 30 | 0.667 | 5 | 0.25 | no | **no** |
| 4 | min | 34 | 0.756 | 3 | 0.15 | no | **no** |
| 4 | mean | 28 | 0.622 | 3 | 0.15 | no | **no** |
| 4 | frac_pass | 34 | 0.756 | 3 | 0.15 | no | **no** |
| **5** | **min** | **36** | **0.800** | **0** | **0.00** | no | **yes ← winner** |
| 5 | mean | 34 | 0.756 | 0 | 0.00 | no | yes |
| 5 | frac_pass | 36 | 0.800 | 0 | 0.00 | no | yes |
| 6 | min | 39 | 0.867 | 7 | 0.35 | no | **no** |
| 6 | mean | 32 | 0.711 | 4 | 0.20 | no | **no** |
| 6 | frac_pass | 39 | 0.867 | 7 | 0.35 | no | **no** |

**The tension is structural, not a tuning miss.** Higher `k` catches more hallucinations
(k=6/min → 39/45 = 0.867, the ceiling observed) but its finer folds shred genuine decodes too
(FR 0.35). The winning cell by the pre-registered rule (max catch subject to FR ≤ 0.10, tie-break
smaller k) is **k=5 / min** at **0.800 catch, 0.000 false-reject** — genuine-safe but 0.80 < 0.90.
No cell is both ≥0.90 catch AND ≤0.10 false-reject on the planted-45.

## Held-out surrogate audit (frozen cell k=5/min; fresh key seed `CICADA3301`, disjoint offsets)

The winning cell was FROZEN before the surrogate was scored (no re-tuning after seeing it — PREREG).

| measure | value | bar | verdict |
|---|---|---|---|
| surrogate hallucination n | 66 | ≥20 | ok |
| single-cut catch on surrogate | 0.318 | (contrast) | still leaky as expected |
| **k-fold catch on surrogate** | 54/66 = **0.818** | ≥0.90 | **FAIL** |
| surrogate genuine n | 24 | ≥10 | ok |
| **surrogate genuine false-reject** | 4/24 = **0.167** | ≤0.10 | **FAIL** |

The frozen cell **generalises its catch level** (0.800 → 0.818, so it is not overfit to the 45) but
**does not clear 0.90**, and the false-reject that read 0.00 on the tuning panel drifts to **0.167**
on fresh genuine decodes — over the cap. Both surrogate gates fail. This is the generalisation
failure P-b/P-c were written to detect.

## Value = coverage × power (doctrine R2 — reported together)

- **Coverage:** the full proxy-parameter space named in Q3 — `k ∈ {2,3,4,5,6} × rule ∈ {min, mean,
  frac_pass}` = 15/15 cells scored, on the frozen planted-45 tuning population AND a disjoint
  66-case + 24-genuine held-out surrogate under a fresh key. This is the complete pre-registered
  cell grid; nothing in Q3 is left unscored.
- **Power (the catch instrument's own measured power):** proven by the single-cut baseline
  reproducing 15/45 and the genuine panel recovering 20/20 at ≥0.97 — the harness demonstrably
  separates hallucinations from genuine decodes when a proxy can. The strengthened proxy's power to
  catch a correct-key EN_NOVOWEL overfit **without an oracle** peaks at **0.867 (k=6/min, genuine-unsafe)**
  and at **0.818 (k=5/min, genuine-safe, on held-out data)** — both **below** the 0.90 required to seal
  the gate. That is the number this lane exists to publish.

**Bound stated as a conditional (doctrine R7):** on the class `(relation=exact, register=EN_NOVOWEL,
correct key)`, no disjoint-fold cell in the swept grid seals the no-oracle gate to ≥0.90 catch while
holding genuine false-reject ≤0.10 on held-out data. NOT covered: other relations (keyskip1 was
named in Q4 but the planted 45 are `exact`-preset overfits, so keyskip1 catch is unmeasured here);
other registers; non-fold proxy families (a learned self-consistency score, a longer decrypt head,
a per-register fold bar). Any of those reopens the seal.

## Language-agnostic statistics persisted (doctrine R3)

`catch_surface.json` persists, at run time and per cell, the **held-out recovery values** (rune-index
self-consistency, language-agnostic by construction — the fold proxy uses NO plaintext oracle and
NO English LM; it compares re-decoded rune indices against the full-page decode's rune indices),
the **genuine true-recovery vector** (rune-index recovery, agnostic), the **panelmax bar** (7.634),
and per-cell catch / false-reject counts. The catch statistic is itself the language-agnostic
self-consistency measure the doctrine asks sweeps to store; it is not an English score.

## What remains OPEN

1. **The no-oracle seal is not achieved.** Round 21 sweeps must carry survivors as
   *flagged-for-oracle*. This is the operative consequence.
2. **keyskip1-relation catch is unmeasured** — the planted 45 are `exact`-preset overfits. A
   keyskip1 hallucination population would extend the surface along the relation axis (Q4 named it;
   this lane did not populate it).
3. **Non-fold proxy families are untouched** — a longer decrypt head (the 24–32-rune head capped
   the hard registers in R20 P1), a per-register fold bar, or a learned self-consistency gate could
   still reach 0.90. The fold family alone is bounded here at ~0.82–0.87, not the whole design space.

## Reproduce

```bash
cd /mnt/c/Users/dukot/projects/cicada3301/liber-primus
python3 tests/validate.py                                            # 5/5 trust anchor
python3 analysis/round21/L1-seal-realmode-proxy/audit_catch.py       # writes catch_surface.json
```
