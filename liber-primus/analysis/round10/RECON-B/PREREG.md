# RECON-B — PREREG (register lane, no attacks run)

**Lane type.** Documentation audit. No cryptanalytic test is executed, so there is no
statistic, no null model and nothing to add to the multiple-comparisons tally in
`research/LEDGER.md`. This file records the scope and the acceptance rule *before* the
mining pass, so the register cannot be retrofitted to whatever turned up.

## Two questions, fixed in advance

1. **Enumerate** every lead that Rounds 1–9 (plus the 2026-07 campaign era feeding them)
   left in a non-closed state: open, partial, scope-limited, stated-but-uninterpreted.
   Each entry must carry a `file:line` where the repo itself says so.
2. **Audit the rounds against the navigation docs.** For each round, compare
   (a) the scope actually executed — window sizes, corpus sizes, parameter ranges, disclosed
   underpowered arms — against (b) the claim `README.md`, `PICKUP-HERE.md`,
   `liber-primus/ELIMINATION-LEDGER.md` and `liber-primus/analysis/README.md` now make from it.
   Flag every place where a narrow negative has been promoted into a broad closure.

## Acceptance rule (fixed before mining)

An entry enters the register only if **one** of these is demonstrable from the repo text or
from the artifacts on disk:

- **R1 — scope gap.** The round's own writeup states a coverage bound (corpus size, parameter
  range, window length, "for that corpus", "disclosed underpowered") and at least one
  navigation doc restates the result without that bound.
- **R2 — unfinished artifact.** A script, output file or half-finished stage exists on disk
  whose completing step was never run, or whose result was never written into any doc.
- **R3 — self-declared open.** The repo explicitly labels the item open / inventory /
  uninterpreted / left as a thread and no later doc closes it.
- **R4 — stale premise.** A kill or closure rests on a factual premise about the repo or the
  environment that is no longer true.

Entries failing all four are **not** registered, however interesting. In particular, an item
already killed with a recorded reason is *not* re-registered merely because a later doc words
it loosely — the wording problem is registered, the attack is not revived.

## Falsifiability standard for the register

Every entry must name a **falsifiable test** that would settle it, with a stated outcome that
would close it. "Look at it again" is not a test. Where the settling test is a documentation
fix rather than a measurement, that is stated explicitly so nobody counts it as a lead.

## Explicit non-goals

- No attack is proposed, revived or run. Where an audit finding touches a killed family, the
  finding is about the *argument*, not about reviving the family.
- No existing file is modified. Output is this folder only.
- Priority is expected-value of *resolving the ambiguity*, not P(solve).
