# PA-2 — PRE-REGISTRATION (Round 10B, internal prior-work census)

Written before reading past the four mandatory orientation docs. **This lane runs no
cryptanalytic attack.** It is a census of this repo's own prior mass-agent runs, so that
Round-10B lanes can cite instead of re-run, and so we know which past runs are trustworthy.

## Hypotheses

- **H1 (coverage):** the repo's navigation docs (`ELIMINATION-LEDGER.md`, `DEAD_ENDS.md`,
  `PICKUP-HERE.md`) accurately enumerate what was run. **Falsified** if any campaign/armada
  folder contains an executed run whose result is absent from all three, or if any doc cites a
  log/artifact that does not exist on disk.
- **H2 (instrument quality):** every promoted elimination rests on a run that (a) had a positive
  control and (b) had a null matched to the search size. **Falsified** by any elimination whose
  attack was never shown to recover a planted signal, or whose null was best-of-N against a search
  of best-of-M with M >> N.
- **H3 (scope creep):** no conclusion is stated more broadly downstream than at its source.
  **Falsified** by a downstream doc asserting a strictly stronger claim than the artifact supports.
- **H4 (queued-not-run):** every item a past armada queued was executed. **Falsified** by any
  RANK/track/proposal item with no corresponding log, output file, or findings entry.

## Numeric pass/fail thresholds (fixed in advance)

- **H1 falsified** if >= 1 cited artifact is missing from disk, or >= 1 executed run is
  undocumented in all of the three index docs.
- **H2 falsified** if >= 1 promoted elimination has null_N / search_N < 1e-3.
- **H3 falsified** if >= 1 pair of docs makes contradictory scope claims about the same run.
- **H4 falsified** if >= 1 queued item has zero on-disk evidence of execution.
- **Lane result is reported regardless of direction** — a clean "everything checks out" is a
  valid and useful outcome.

## Method

Read every campaign/armada/round doc and cross-check each cited artifact against the filesystem;
read the harness source for every promoted elimination to extract its control design (positive
control present/absent; null trial count) and compare against the sweep's actual search size.

## Controls

Not applicable (no decode is attempted). The census's own falsifier is the filesystem: every
claim below cites a path or a line, and is checkable by `ls`/`grep`.

## Scope limits stated in advance

Covers material committed to this repo only. Does not cover the public community record
(that is PA-1/RECON-C's lane). Does not re-execute any run; where a run's soundness is
questioned, the questioning is about the *instrument's design as written in its source*, not a
re-measurement.
