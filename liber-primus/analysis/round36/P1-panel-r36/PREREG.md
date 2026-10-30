# Round 36 / P1 - PREREG (panel-R36: the recorded gate)
Dated 2026-10-30, written BEFORE any build, hash inventory or gate run in this lane.

## What is being decided
Panel-R36 = 12 registers (EN_MODERN, EN_KJV, LP1_REAL, LATIN, OE, DE, CY, EN_HALFVOWEL, EN_NOVOWEL, GREEK, HEBREW, NORSE)
built FROM DISK by I1's `build_models_r36.py --nine=rebuild` (not the Round 32 arrays carried verbatim in I1's panel12.npz),
with every input's path, sha256, bytes and acquisition route recorded in `inputs_r36.json`. Coordinator decision (given).

## Fixed parameters (no tuning in this lane)
* Builder: I1's `build_models_r36.py` unchanged, called through `build_r36.py` with `--nine=rebuild`, mapping variants GREEK/HEBREW/NORSE = 1,
  lambdas (0.70,0.20,0.09,0.01), LP1 mix 0.5, null 20000 draws x 14 lengths, seed 3301. Full null (not --quick).
* Build twice into `build1/`, `build2/` (same parameters, fresh process each); sha256 of every output file compared.
  Pass = byte-identical `panel12.npz` and `testhalves12.npz` (and identical out_build JSON after dropping the wall-clock fields `built`, `elapsed_s`).
  If not identical: diagnose and fix determinism in the wrapper/builder invocation; do not wave it through.
* Power gate: Round 32 `power.py` protocol via I1's `run_gate.py` pattern (plant_trial verbatim, 24 reps, L in {120,240}, beam (400,3), nproc=1),
  reduced pre-registered null (wrong-key real-LP2: 4000 at L=120, 2000 at L=240; shuffled-LP2 2000), bar = max(empirical, GPD) 1-1e-3 quantile of
  the 12-panel pmax. Required: pmax power >= 0.90 for EACH of the 12 registers at BOTH lengths.
* Disclosure (stated in advance): the rebuilt nine differ from Round 32 (KJV/Mabinogion on disk are now the Round 19 originals, not the Round 32
  substitutes), and EN_NOVOWEL sat at 0.917 (22/24) in Round 32, so it has no spare margin; a from-disk EN_NOVOWEL below 0.90 is a possible honest outcome.

## Outcomes and what each means
* All 12 >= 0.90 and build-twice identical -> panel-R36 is a valid recorded gate; engine copy re-pointed.
* Any register < 0.90 (L=120 or 240) -> recorded at its measured power; panel-R36 is recorded as FAILING the gate; the engine copy is still
  produced but marked NOT-FOR-USE and the coordinator decides (I will not drop the register or alter the gate to rescue it).
* Build not byte-identical after diagnosis -> no gate claim; S1 must not proceed.

## Engine re-point (in a COPY only)
Live Round 27 files are not touched. The copy contains: `grind27.c` with NREG 9 -> 12, `export_data_r36.py`, regenerated `engine.dat` and
`panel_lm.f32` (12 x 24389 float32). V1 reference pmax values and the V2 planted pmax are RE-SCORED under panel-R36 with the C engine's own formula from
the stored plain_idx (the beam is quadgram-only, panel-independent), mu/sd at n=120 taken from panel-R36's calibration. Panel sha and V1/V2 reference
changes are recorded in `engine_config_diff.txt`. Claim bars are NOT silently recalculated: flagged to the coordinator.

## Not claimed
No decode, no key-space result. This is an instrument/governance lane (status: measured). S2 rows after the re-gate are a new measurement, not a
continuation of Round 19-gated rows. The `--self-test` itself is not run here (needs the S1 sandbox); I record a Python replica of its V1/V2 arithmetic only.
