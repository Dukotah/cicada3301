# Round 42 / X1 — red-team: RESULTS

_2026-11-02 (script written at the end of the lane runs); executed and filed 2026-11-03 at the
closeout. Refute-by-default. `x1_verify.py` re-derives, re-hashes and recounts from the artefacts —
it does NOT trust the lane RESULTS files. Raw output: `x1_output.txt`._

## Verdict: 23/23 independent checks PASS, 0 fails. One process deviation recorded (bounded, no verdict flip).

### What was re-checked (all PASS)

- **S1 counting is from downloaded state only.** The local `state_recovered/STATUS.json` re-hashes
  to the recorded sha256 `1aa52944…`; the window-2 cursor sum (2,235,695,586) strictly exceeds the
  window-1 sum (2,059,308,008); `n_claim_bar_hits == 0`; `best_pmax` 7.3071 < the 7.5342 near-miss
  bar. Nothing was counted that is not on this laptop.
- **S3 binary fidelity.** The built bash 3.2.0 `RANDOM=1` first-20 matches
  `round40/B1-bash-versions/verification.json` 20/20.
- **C3 provenance + re-derivation.** The 43 auto keys recount to exactly 43 from the present raw;
  MIDISCV and WORKING both re-derive (the X1-B/R41 claim's success test); verdict NEGATIVE with 0
  crossers; global best 5.496 sits far below every per-page bar.
- **C1 data-integrity finding reproduces.** Independently re-classifying `round12/C2/texts/`
  reproduces exactly 10 corrupt (globalgrey 404 HTML) and 23 real texts; verdict NEGATIVE.
- **C2 verdict NEGATIVE**, best 5.003 far below bar.
- **Free bars sane.** `bars_v3` free bars increase with N (16.941 → 17.422 for C2 → C1 grid sizes)
  and sit in the 8..20 range — the thresholds the C lanes quoted are real outputs of the null of
  record, not transcription.
- **Ledger patches landed.** All five R42 rows present (`R42-S1-S2-WINDOW2-RECOVERED`,
  `R42-S3-BASH32-BINARY-L1`, `R42-C1-R35-KEYTEXTS-RUN`, `R42-C2-R36-DATED-PADS-RUN`,
  `R42-C3-B1-43-AUTO-KEYS-RUN`); `counts.total == len(entries)` (304 == 304).

### Gate and checkers (run at closeout, 2026-11-03)

- `tests/validate.py` → ALL VALIDATIONS PASSED (trust anchor).
- `analysis/handoff/validate_ledger.py` → **Unsound negatives: 0** (304 rows).
- `analysis/round39/P1-measured-ceiling/check_ceiling.py` → **PASS** (125 rows cited, 110 pins).
- The FULL documented gate `pytest -q -m "not network"` → see `SYNTHESIS.md` header for the count
  (run before the closeout commit per X1-B/R41 B-9; CI runs only a subset).

## FOUND-DEVIATION (process, bounded): the C lanes planted no fresh positive controls

The campaign plan §3 (C1/C2/C3 Q3) required "positive controls through the real decode path
(natural-rate, ≥ 3 registers)". The three PREREGs as written substituted the **standing
instrument**: panel-R36 + `bars_v3` free bars, whose power was measured in Rounds 36/41, plus (C3
only) the MIDISCV/WORKING re-derivation as the lane's named success test. No fresh plants were
decoded through `run_c1/c2/c3.py`.

Why it is bounded: the decode path the C lanes used is the same panel-R36 adjudication whose
recovery was control-measured in R36-I1/R41-I1 (not a new instrument), the PREREGs declared the
substitution *before* output (no post-hoc weakening), and the negatives sit 11–12 pmax units below
their bars — far outside the region where marginal screen power decides anything. Why it still
matters: an end-to-end plant through each lane's own windowing/transliteration glue would have
caught a glue bug (wrong page indexing, dead transliteration) that the standing bars cannot see.
**Disposition:** verdicts stand; the three rows' negatives carry the standing conditionals; any
future re-run or extension of these cells (the 10 refetched keytexts, deeper pad offsets) MUST
plant through the lane glue per the plan text. Recorded here so the Round 43 critic inherits it.

## Not audited (never ran — carried to Round 43)

- **S2 (PHP tier retry)** and **I1** (WATCH-band wiring — still gated on the owner's yes — and the
  widened k≤3–4 head screen) never ran in Round 42. I1(b) remains the gate for the whole B2
  offset remainder (110.5 of 116 cells).
- The 10 corrupt R35 keytexts (globalgrey 404 captures) need a fresh hash-pinned re-download
  before their cells can be called covered.

## Round 43 critic (what this round would hide from its successor)

1. The S1 negative is **mixed-instrument coverage** (44.1 pp Round-19-gated + 7.9 pp panel-R36 of
   2³²); quoting "52.05 % done" without the split overstates the panel-R36-judged fraction.
2. The fresh snapshot `snap_Rw1QyGFA39to1dV9rR8qA8WJEgm6` expires **~2026-11-09** — the full
   candidate lists exist only in sandbox-side storage (snapshot + persistent sandbox); only
   summaries are on the laptop. If the lists matter, export them before the date; if they do not,
   say so in a row note and let them lapse deliberately.
3. The C-lane deviation above: future artefact-cell lanes must plant through their own glue.
4. The free bars used as thresholds are standing nulls, not fresh per-shuffle nulls — stated in
   every RESULTS; fine at these margins, not fine if a future cell lands within ~2 of its bar.
