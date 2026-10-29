# R32 / I3 PREREG -- R3 enforcement + length-aware null

Honesty note: the validator design (Q1-Q5 below) was fixed before the validator edit, but this file was
written to disk after the first calibration smoke runs (L=120, M=1024 and 200k). The null-curve acceptance
criteria below were stated before the fit was computed.

- **Q1 recognizer.** `validate_ledger.py` must reject a SWEEPROW store lacking any of ioc, mds, pmax_ne, zl
  (or the 9-vector z), and accept a compliant one. Proven by `analysis/handoff/test_validate_ledger_r3.py`
  (each field dropped in turn must fail; compliant must pass). For the curve: the fitted exponent must be
  within 2 SE of round19's -0.583, or the discrepancy is reported.
- **Q2 prior.** R3 had 0/15 compliance in R10b; round19/I2/SWEEPROW.md s7 recorded wiring as never done.
  Curve: round19/I3 measured beta ~ L^-0.583 from two points (zero DOF).
- **Q3 bounded.** Yes: one scan of the 172-row ledger and 5-8 null cells of 2e5 decodes.
- **Q4 conditionals.** Key space: n/a (instrument). Transition model: keyskip1, beam_w 400, max_skip 3.
  Register: legacy EN quadgram score_norm only (the bar `null.py` publishes); other registers untouched.
- **Q5 kill/scoping.** If any historical row newly ERRORs, report it and do not loosen: scope to round >= 19
  rows that declare a sweep; implicit (evidence-jsonl) detection is WARN-only. If the new fit exponent
  disagrees with -0.583 by > 2 SE, report it and do not silently adopt either.
