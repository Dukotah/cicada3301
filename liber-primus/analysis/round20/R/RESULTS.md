# R — RED-TEAM Round 20's OWN reasoning — RESULTS

_Round 20, Phase R (doctrine R6). Target: THIS ROUND'S reasoning (P1/P2/P3), not the cipher.
Verdicts are FOUND-ERROR / NO-ERROR-FOUND, never "confirmed". Pre-registered in
[`PREREG.md`](PREREG.md) BEFORE any re-measurement. Trust anchor `tests/validate.py` → ALL
VALIDATIONS PASSED (before + after; I ran no destructive change)._

## Verdict table

| sub-attack | verdict | the number that decided it |
|---|---|---|
| **(a)** structured wrong-key null leaks P1 power? | **NO-ERROR-FOUND** | structured wrong-key survival **0.000** (= RAND floor) on all 5 registers; true-key survival transfers (0.67–0.92). Bar was >0.20. |
| **(b)** sieve × panel-max-null destructive interaction (B-iv replay)? | **FOUND-ERROR (latent)** | screened-survivor panel-max FP **0.025/decode** vs the bar's nominal **1.0e-8/decode** → **2.5×10⁶ inflation**. Unscreened wrong-key FP **0.000/200**. |
| **(c)** is "not-a-re-run" true for each S-family? | **NO-ERROR-FOUND** | LEDGER coverage: R19-G1/G2/G3, G4-TEX, R16-PRNG all **ZERO key-space decodes scored**; the one prior full-2³² sweep (seed_sweep/results_full32.txt, gens 1–9) is **rigid + English 4-gram + fixed −12.5 bar = zero power** per R19-G3-CORRECTION's own words. |
| **(d)** does every hit path gate on RECOVERY, not score? | **FOUND-ERROR** | `panelmax20.py` returns a **score bar only**, no recovery field; `SWEEPROW/1,2` persists **no recovery field**; **no hit-decision function exists in round20**; EN_NOVOWEL clears the bar at **0.26 recovery (drift) / 0.84 (exact)**. The win-condition's recovery≥0.90 exists only in prose. |

**halt_sweep = TRUE.** Not because of the cipher, but because as the round currently stands the
Phase-S hit path can certify a hallucinating decode (sub-attack d), and the one interaction that
would flood it with false positives if the sieve were ever re-enabled is real and measured
(sub-attack b). Concrete reopen/clear conditions below. **(a) and (c) are clean NO-ERROR-FOUND.**

---

## (a) — structured wrong-key null: NO-ERROR-FOUND

**The attack.** P1 validated its sieve only against a **uniform-random-plaintext** (RAND) control,
which survives 0.000. Doctrine's A-i reopener asks whether a *structured* wrong-key population
(real language, wrong key) leaks through where uniform noise did not. If it did, P1's per-register
survival surface would be measuring against the wrong null and the reduction claim would understate
the true survivor count.

**What I measured** ([`structured_null.json`](structured_null.json), reusing P1's own seed-3301
harness, real hash-verified Marsaglia bytes, n=12/register). I enciphered a **real EN_MODERN
plaintext** (structured, not uniform) at a *wrong* offset `o_dec` in the same pad, then asked
whether that structured wrong offset survives the Stage-A screen **run on the true cipher**:

| register | true-key survival (B) | **structured wrong-key survival** |
|---|---:|---:|
| LP1_REAL | 0.833 | **0.000** |
| EN_MODERN | 0.667 | **0.000** |
| LATIN | 0.833 | **0.000** |
| CY | 0.917 | **0.000** |
| EN_HALFVOWEL | 0.667 | **0.000** |

**Why no leak.** A structured plaintext only decodes to language under *its own* key; enciphered at
`o_dec` it is noise under the *true* cipher's screen, so it lands in the bulk, not the top-fA. The
screen discriminates the (cipher, key) *pairing*, not "is there language somewhere in the pad." The
true-key survival reproduces P1's published surface (0.67–0.92), so the surface is measured against
a valid null. **P1's sieve does not leak power on a structured wrong-key null.** NO-ERROR-FOUND.

## (b) — sieve × panel-max-null destructive interaction: FOUND-ERROR (latent)

**The attack.** Round 19's R1 B-iv found free-drift × panel interact destructively. Stage-A's
screen statistic (`zmax` — per-register z, then **max over 9 registers**) and P3a's adjudication
statistic (`pmax` — per-register z, then **max over 9 registers**) are the **same max-over-9
family**. The screen therefore pre-selects for panel-max outliers; but P3a's bar is fitted on
**fresh, unscreened** wrong-key decodes (`I19:vecbeam.keyskip1+I2|pmax|L120`, M=10⁶). So the bar's
null is not conditioned on the selection the screen imposes on the population it will adjudicate.

**What I measured** ([`interaction_b.json`](interaction_b.json), 8 plant-populations, 200 screened
+ 200 unscreened wrong-key decodes, exact preset, bar @N=10⁶ = 7.634):

| population adjudicated | clears the 7.634 bar | per-decode FP |
|---|---:|---:|
| **screened** wrong survivors (top-fA=1e-3 by zmax) | 5 / 200 | **0.025** |
| unscreened wrong offsets (matched) | 0 / 200 | 0.000 |
| the bar's *nominal* per-decode FP (Gumbel μ=2.358 β=0.287) | — | **1.0×10⁻⁸** |

The screen inflates the adjudicated population's per-decode FP by **~2.5×10⁶** over what the bar
assumes. This is the B-iv mechanism replayed at the sieve→adjudicator boundary: the double max
compounds multiplicity, and the panel-max bar — calibrated on the wrong (unscreened) population —
**does not control its FP rate on the survivors an S-lane would actually feed it.**

**Why "latent".** P1 fired its INFEASIBLE kill, so per the frozen PREREG **Phase S runs G3 only,
un-sieved** — the double-max does not fire in *this* round. But the CAMPAIGN-PLAN §S text
(lines 208, 226–233) still specs S-PERL and S-TEX as "sieve-gated / requires P1," a spec now
un-runnable-as-written (its gating sieve is INFEASIBLE) and NOT reconciled in §5/§7. If any future
round relaxes the survival bar to make the sieve deployable, this FP inflation fires unless the
panel-max null is re-fit on **screened** wrong keys. FOUND-ERROR, carried as a reopen condition.

## (c) — "not-a-re-run" for each S-family: NO-ERROR-FOUND

Queried `LEDGER.json` `coverage`/`not_covered` (not `status`), per doctrine mechanic 6:

| S-family | ledger entry | key-space coverage | at power? |
|---|---|---|---|
| S-G3 (Py2.7) | R19-G3 | "**0 decodes of key space cleared**" — Phase-1 lane holding at scoring boundary | n/a (unmeasured) |
| — prior full-2³² | R19-G3-CORRECTION | 9 gens over 0..2³² **DID run**, but via `sweep.c decode_score()` = **RIGID** (interrupter-null only, no key-skip), **mean English 4-grams vs fixed −12.5 bar** | **ZERO power** (rigid+English+fixed-bar) |
| S-BASH | R19-G1 | "**NO KEYSTREAM WAS SCORED AGAINST LP2. Phase 0 hold, by design.**" | n/a |
| S-PERL | R19-G2 | "**ZERO key-space coverage. This lane swept no seeds and excludes nothing.**" | n/a |
| S-TEX | G4-TEX-RNG | "**ZERO decodes of coverage.** … HOLDS at the scoring boundary" | n/a |
| S-MARS | B-13-MARSAGLIA | 1.54×10⁹ offsets scanned but `threshold_for=−5.38`, English-only rigid; C2 re-scoped it as a staged hold | zero power for the register axis |

R19-G3-CORRECTION's own `reopens_if` states the nine full-32 negatives reopen when "re-adjudicated
through round19/I1+I2 — **which is exactly S2's job**." So S-G3 re-adjudicating that seed space at
power is the ledger's own **pre-registered reopener**, not a re-run of measured ground. Every
S-family is genuinely unmeasured on the register×decoder axes the repaired instrument covers.
**NO-ERROR-FOUND** — the not-a-re-run justification holds, with the receipts above.

## (d) — recovery-gating (the A-iv decoupling hazard): FOUND-ERROR

**The win-condition** (CAMPAIGN-PLAN §2): a HIT = clears the panel-max null **AND** rune-index
recovery **≥0.90** **AND** reproduces on the held-out ¾. R1's A-iv named the hazard: score alone
certifies a hallucinating decoder (a decode can score above the bar at low recovery).

**What I found in the actual code:**
1. `panelmax20.py` — the ONE bar every S-lane calls — returns **a score bar only**
   (`panelmax_bar`/`panelmax_contract`). `grep recovery` → **NONE**. It cannot enforce recovery.
2. `SWEEPROW/1` (fields 0–12) and `SWEEPROW/2` (13,14 = n_skips, n_unexplained) persist **no
   recovery field**. A downstream re-adjudication (e.g. S-RESCOPE re-reading survivor rows)
   literally cannot threshold on recovery — the field is not stored.
3. **No hit-decision function exists anywhere in `analysis/round20/`** (`grep def.*hit|decide|
   certif` → none). The recovery≥0.90 gate lives only in prose.
4. Recovery is computed by `driftbeam.recovery(plain_idx, truth_idx)` — it **requires
   ground-truth plaintext**. On a real unknown LP2 pad there is **no `truth_idx`**, so recovery is
   *uncomputable directly on a real candidate*; the round must infer it from the score/recovery
   coupling its controls measured — a coupling the shared instrument does not encode.
5. The measured decoupling is real ([`out_plant_recovery.json`], P3): **EN_NOVOWEL clears the
   panel-max bar at recovery 0.84 (exact, power 0.70) and 0.26 (drift, power 0.10)** — below the
   0.90 win-condition. The "EN_NOVOWEL = detection-only" caveat is a **string in the contract
   dict**, not an enforced `preg`-exclusion gate.

So as the round stands, an S-lane that calls `panelmax_bar` and certifies a bar-clearing decode as
a hit is certifying on score alone, with **no runnable recovery gate**, and a drift decode whose
argmax register is EN_NOVOWEL can clear the bar at ~26% recovery — a hallucinating decode by the
round's own definition. **FOUND-ERROR.**

**Mitigating fact (why fixable, not fatal):** no S-lane is built yet (no `analysis/round20/S*`
dirs), so the gate CAN be added before Phase S scores anything — which is exactly what halt_sweep
enforces.

---

## halt_sweep = TRUE — and the concrete conditions that clear it

Phase S (G3-only, un-sieved) must **not score a single LP2 decode** until the hit path gates on
recovery, not score. Clear conditions:

1. **(d) — implement the recovery gate in runnable code before S scores.** A hit-decision function
   that requires, jointly: (i) `pmax ≥ panelmax_bar(preset,N_adj)`; (ii) rune-index recovery ≥0.90
   — for a real candidate, via the score/recovery coupling P3 measured (or by excluding
   `preg == EN_NOVOWEL` outright, since it is the only register that clears the bar below 0.90
   recovery under both presets); (iii) reproduction on the held-out ¾ of the page under the same
   key. Persist a recovery proxy as a `SWEEPROW/3` field so re-adjudication can gate on it too.
2. **(b) — do NOT re-enable the sieve without re-fitting the panel-max null on SCREENED wrong
   keys.** The current bar under-states screened-survivor FP by ~2.5×10⁶. If a future round relaxes
   P1's survival bar to deploy the sieve for S-PERL/S-TEX, calibrate a fresh panel-max null on the
   screen's *output* population, or the round will certify ~2.5% of screened noise as bar-clearing.
3. **Spec hygiene (carry, not halt):** CAMPAIGN-PLAN §S lines 208/226–233 still call S-PERL/S-TEX
   "sieve-gated / requires P1"; with P1 INFEASIBLE those lanes are un-runnable as written. §5/§7
   should be reconciled to state they are deferred (no affordable sieve), not merely queued last.

Once (1) is in place, halt clears for S-G3 (the only lane the frozen P1 kill actually releases);
(2) is a standing condition on any sieve revival; (3) is a doc correction.

## Coverage × power of THIS red-team (doctrine R2)

- **Coverage.** (a) 60 structured-null decodes across 5 registers; (b) 400 wrong-key beam decodes
  (200 screened / 200 unscreened) across 8 plant-populations; (c) full read of 6 ledger families'
  coverage/not_covered; (d) full code/schema audit of panelmax20/sweeprow2/adjudicate + the P3
  plant-recovery table. Time-box: ≤15 min wall, respected.
- **Power.** (a)/(b) instruments are validated by internal controls: (a)'s true-key arm reproduces
  P1's surface (recognizer works); (b)'s unscreened arm reproduces the bar's ~0 nominal FP
  (baseline works), so the screened-arm inflation is a real contrast, not instrument noise. (b)'s
  n is small (5/200) but the effect size (2.5×10⁶) is not marginal to n. (d) is a code fact, power
  n/a. The three conditionals of each verdict: key space (Marsaglia offsets / ledger entries /
  code), decoder relation (keyskip1 `exact` + `drift`, as P1/P3 measured), adjudicator register
  (the 9-register panel; EN_NOVOWEL is the decoupled one).

## Files

- [`PREREG.md`](PREREG.md) — the 5 Aiming-Test answers, controls, frozen thresholds, kill/halt authority.
- [`structured_null.json`](structured_null.json) — sub-attack (a): structured wrong-key survival = 0.000.
- [`interaction_b.json`](interaction_b.json) — sub-attack (b): screened FP 0.025 vs bar nominal 1e-8.
