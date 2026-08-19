# Gate status for the B-04 run of 2026-08-19 — read before interpreting `results_summary.json`

**Both pre-registered gates PASS. The run's own `results_summary.json` will say
`INCONCLUSIVE`, and that label is wrong** — it is an artifact of a bug in the driver, fixed
after the process had already started. This note records the correction; do not let the stale
label propagate.

## What happened

`sweep.py`'s `gate_g1()` reads D3's published control numbers back out of
`analysis/round12/D3/results.json` and checks them against PREREG §4. The key aliases it
searched for (`beam_correct`, `rigid_correct`) did not match the field names D3 actually
writes (`beam_correct_seed`, `rigid_correct_seed`), so both came back `None` and the gate
logic recorded FAIL for want of a number — not because any control failed.

Because the sweep was already running when this was spotted, the fix could not take effect in
that process: it had imported the module and will emit the stale banner
*"A GATE FAILED — every stage below is INCONCLUSIVE"* and a final `"verdict": "INCONCLUSIVE"`.

## The corrected gate results

**G1 — replicate `round12/D3/pc_derivedkey.py` verbatim.** Re-run standalone with the fixed
aliases (`results_G1_rerun.json`):

| quantity | value | PREREG §4 requirement | |
|---|---|---|---|
| beam, correct seed | **−4.170** | ≥ −5.5 | ✅ |
| char-recovery | **0.989** | ≥ 0.90 | ✅ |
| beam(correct) − beam(wrong) | **3.179** (−4.170 vs −7.349) | > 1.0 | ✅ |
| rigid, correct seed | **−6.835** | < −6.0 | ✅ |

→ **PASS.** D3's own `results.json` independently records `"control_passed": true`.

**G2 — plant-and-recover through this harness at real Stage-A settings.** Ran inside the live
process and logged to `sweep.log`:

- Plant: seed `THE PRIMES ARE SACRED` (family `slogan`, genuinely resident in the 2,165-entry
  dictionary), `sha256_ctr` / `mod29`, enciphered under the pinned soft key-skip filter
  (`sign=-1, supp=0.83, seed=3301`), 120 runes, resulting ciphertext doublet rate **0.0**
  — reproducing LP2's suppressed-doublet anomaly.
- Result: the planted `(seed, generator, reduction, sign, atbash, direction)` config ranks
  **#1 at −4.186**, recovering `THEPRIMESARESACREDANDTHETOTIENTFUNCTIONI…` in clear. Runner-up
  is noise at **−6.621**.

→ **PASS** — `G2 planted config ranked #1 = True; clears bar = True`.

## Consequence

The pre-registered condition for reporting a NEGATIVE is met: both gates pass, so a null over
the tabulated region is sound and should be reported as **NEGATIVE**, not INCONCLUSIVE.

Two independent artifacts on disk support this, both post-dating the buggy banner:
`results_G1_rerun.json` and the `G2 … -> PASS` lines in `sweep.log`.

Re-running `sweep.py` from scratch would emit the correct label, but re-running ~6.2M decodes
to fix a string is not a good use of compute. Anyone regenerating this campaign from the
committed code will get the correct label directly, since the alias fix is committed.

_Recorded 2026-08-19._
