# Round 41 / X1 (part A) -- PREREG (red-team of I1 and B2)

_Dated 2026-10-31, written BEFORE any re-run output of this lane. Refute-by-default. No `git`. nproc=1, one Python process at a time, free RAM checked before each (wait if < 0.4 GB; psutil absent, so `Win32_OperatingSystem.FreePhysicalMemory`). Writes only inside `round41/X1-redteam/`. `LEDGER.json`, `MEASURED-CEILING.md`, I1 and B2 files are not edited._

## Targets and the test for each
**I1**
- (a) Population: is the null conditioned on the real ciphertext's survivors (circular), or only on the real LP2 head via the same screen the sweeps use? Test: read `i1lib.py`/`run_null.py` for any use of real-sweep rows in the draw; KS the null survivors against the real R37-I2 survivors at L=120; judge whether screening on the real head is the right population (it is iff the sweep's own non-key rows are drawn from it) or a leak.
- (b) Fit vs data: independent POT refit from `null_stream.jsonl`; independent exceedance counts of the 307,377 real rows against the fit at thresholds 5.0-7.0 (extends I1's Q5 counts, which used the null stream only); GPD-vs-exponential bracket; honest band for N=1e6 (statistical SE vs model band). Check the "max(refit, pooled real POT)" rule and the Q5 kill logic for internal consistency.
- (c) Five re-judged rows: recompute bar at actual N from `fit.json` cell parameters (mu, beta) and the pooled real parameters; compare with `rejudged_rounds36_40.json`.
- (d) The two 18/20 cells: from `control_raw.jsonl` confirm every loss is a `prefilter_pass: false`; check whether the page already states the screen's per-register power.
- (e) Run `bars_v3.py` doctests, `benchmark/bars_matched.py` doctests/tests, reproduce the R13 fixture p-values (500 draws).
- (f) Read MEASURED-CEILING.md section 1 null row and the 12 pins against the ledger row; run `round39/P1-measured-ceiling/check_ceiling.py`.

**B2**
- (a) Re-plant (offset 2, sign -1) and (offset 0, sign +1), 5 plants each, with my own code path: enciphered from the true `K_raw[k:]` with the true sign, screen fed the advanced/negated keystream, then v3 decode; criterion: recovers (>= 0.90) and clears the bar of record.
- (b) Recompute a handful of `wrapcheck.json` entries independently (own generator implementation of bash 4.2 `$RANDOM`).
- (c) Re-judge B2 best rows at actual N against `bars_v3(family="survivor12")`; write `ledger_b2_corrected.json` (row + patches), not editing B2's files.
- (d) Misaligned control (offset-1 plants at offset-0 alignment, 6/20): scope of the statement; whether it changes any stored orbit row's `not_covered`; propose exact text.

## Verdict vocabulary
FOUND-ERROR (with size and whether any stored verdict flips) / NO-ERROR-FOUND (with what was checked). A claim that cannot be re-run in < 20 min is marked NOT-RERUN, not NO-ERROR.
