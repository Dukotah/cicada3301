# R — RED-TEAM Round 20's OWN reasoning — PRE-REGISTRATION

_Round 20, Phase R (doctrine R6). Target is THIS ROUND'S reasoning (P1 sieve, P2 n_skips null,
P3 panel-max null + seed prior + drift re-baseline), NOT the cipher. Verdicts are
FOUND-ERROR / NO-ERROR-FOUND, never "confirmed". Frozen BEFORE any re-measurement is run._

## What is being attacked

The four mandatory sub-attacks named in the lane brief and CAMPAIGN-PLAN §R1:

- **(a)** Does P1's sieve leak power on a STRUCTURED wrong-key null (not the uniform/RAND
  control it used) — the reopener R1 attached to A-i? A sieve validated only against uniform
  RAND plaintext can pass RAND at 0.000 yet still admit a large fraction of a *structured*
  wrong-key population (real Marsaglia offsets that happen to trigram-score high in some
  register), inflating the survivor set and destroying the reduction claim.
- **(b)** Does sieve × panel-max-null interact destructively the way free-drift × panel did in
  Round 19 (B-iv)? Specifically: the multi-register z-max screen (Stage A) and the panel-max
  bar (P3a) both take a MAX over 9 registers. Taking a max-over-registers TWICE (once to screen,
  once to adjudicate) can compound the multiplicity: a wrong offset that survives the screen
  BECAUSE it scored high in register r is then adjudicated by a bar whose null was NOT
  conditioned on "already screened by max-over-register." The screen pre-selects for panel-max
  outliers, so the adjudicator's FP rate on survivors is HIGHER than on a fresh wrong-key draw.
- **(c)** Is the "not-a-re-run" justification for each Phase-S generator family actually true?
  Read LEDGER.json coverage/not_covered for R19-G1/G2/G3, R16-PRNG, G4-TEX-RNG and confirm the
  prior sweep genuinely left this space UNMEASURED AT POWER (rigid / English-only / flat = zero
  power), rather than re-running measured ground. Special scrutiny: R19-G3-CORRECTION reveals a
  prior full-2^32 sweep (seed_sweep/results_full32.txt) with a RIGID decoder — is S-G3
  re-running it, or is that prior sweep genuinely zero-power?
- **(d)** The A-iv decoupling hazard: verify P1 and every planned S-lane gate on RECOVERY
  (≥0.90), not score alone. A decode can score above the panel-max bar at 6% recovery = a
  hallucinating decoder. Does the shared instrument (panelmax20.py) ENFORCE the recovery gate,
  or is it left as an unenforced obligation on each S-lane's own code?

## The 5 Aiming-Test answers

**Q1 — recogniser (what would a found-error look like, would this instrument see it?).**
For each sub-attack the "hit" (FOUND-ERROR) is a concrete, reproducible defect:
- (a) FOUND-ERROR iff a structured wrong-key population survives the FROZEN P1 sieve at a rate
  materially above the RAND floor (>0.20, the same void threshold P1 set for RAND) — i.e. the
  reduction claim (fA·fB) understates true survivor count on structured pads.
- (b) FOUND-ERROR iff the double-max compounds FP: measured survivor-conditioned panel-max FP
  rate exceeds the bar's nominal alpha by >2× at the gating block (the same failure mode as
  R19 B-iv, which I will quantify by running screened wrong-keys through panelmax_bar).
- (c) FOUND-ERROR iff any S-lane's space is ALREADY measured at power ≥0.9 in the ledger
  (making it a re-run), OR NO-ERROR-FOUND iff coverage/not_covered confirm zero power.
- (d) FOUND-ERROR iff panelmax20.py (the shared bar) returns a pass on score alone with no
  recovery field, AND no S-lane / P-lane code path enforces recovery≥0.90 before certifying a
  hit — i.e. the win-condition's recovery gate exists only in prose (CAMPAIGN-PLAN §2), not in
  runnable gating code.

**Q2 — prior (measured fact raising this above flat).** The reopeners are named in the lane
brief itself (R1 attached A-i structured-null and B-iv destructive-interaction reopeners; A-iv
decoupling hazard). Round 19's R1 already MEASURED that free-drift×panel interacts destructively
(B-iv), so (b) has a measured precedent, not a fishing expedition. P1's own RESULTS §2 states
"drift slightly HURTS non-English registers … the R1 §A.6/B-iv mechanism replayed at screen
scale" — the round admits the mechanism is live; (b) tests whether it also poisons the
adjudicator, not just the screen.

**Q3 — bounded.** Each sub-attack is a bounded check: (a) one structured-null survival run
reusing P1's own measure harness with wrong (non-true) offsets as the structured population
(≤5 min); (b) a panelmax FP measurement on screen-conditioned wrong keys (reuse P3's fitted
cell, ≤3 min); (c) a pure LEDGER.json read (no compute); (d) a code/prose audit + a grep for
any recovery≥0.90 gate in the P/S code paths (no compute). Total ≤15 min wall.

**Q4 — three conditionals of my own verdicts.** Each verdict names: the key space it inspected
(P1's Marsaglia offset population / the ledger entries / the code), the decoder relation it
covers (keyskip1 + drift, as P1/P3 measured), and the register register the defect lives in
(P1's per-register surface / the panel-max register set). A NO-ERROR-FOUND is conditional and
does not certify absence beyond what I measured.

**Q5 — kill / halt authority.** Per the brief: set halt_sweep=true ONLY if a defect would make
Phase S waste compute or certify hallucinations (e.g. the sieve/adjudicator passes hallucinating
decodes). Kill at ≤10% budget: if sub-attack (a) shows the structured null survives at ≤ the
RAND floor + noise (≤0.20) in the pilot, I do NOT escalate (a) to a full sweep — it is
NO-ERROR-FOUND and I move on. If (d)'s code audit shows the recovery gate IS enforced in code,
(d) is NO-ERROR-FOUND immediately with no further measurement.

## Positive control (my instrument must recognise a planted defect)

For (b), the positive control is INTERNAL to the round: R19-B-iv already established that a
max-over-register adjudicator over-counts when fed a max-over-register-screened population; if
my FP measurement on screened wrong keys does NOT exceed the FP on unscreened wrong keys, my
measurement instrument is not sensitive and I say so. For (d), the positive control is: does
panelmax_contract() return ANY recovery field? (It must not, by inspection — that IS the finding
if no other code supplies it.)

## Seed-3301 order-preserving surrogate null

All re-measurements reuse the round's own seed-3301 rooted harnesses (P1 measure_survival SEED0,
P3 nrep draws at base 3301). No process-salted hash(). Re-running reproduces the identical draws.

## Pass/fail threshold (SET NOW, NEVER EDITED)

- (a): FOUND-ERROR if structured-null survival > 0.20 at the frozen P1 operating point;
  else NO-ERROR-FOUND.
- (b): FOUND-ERROR if screened-wrong-key panel-max FP > 2× nominal alpha at the gating block;
  else NO-ERROR-FOUND.
- (c): FOUND-ERROR if any S-family shows coverage at power≥0.9 in the ledger; else
  NO-ERROR-FOUND (with the not_covered receipts quoted).
- (d): FOUND-ERROR if no runnable recovery≥0.90 gate exists on the hit path; else
  NO-ERROR-FOUND.

halt_sweep = true iff (d) is FOUND-ERROR at the "certifies hallucinations" severity OR (b) is
FOUND-ERROR at a magnitude that inverts an S-lane verdict. (a) and (c) FOUND-ERRORs are carried
as conditionals, not halts (they reshape coverage claims, they do not certify hallucinations).

## Trust anchor

`tests/validate.py` must PASS (I run no destructive change). I WRITE FILES ONLY; the coordinator
commits. Time-box ≤15 min wall.
