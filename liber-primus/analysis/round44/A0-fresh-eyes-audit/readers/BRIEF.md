# Fresh-eyes audit brief (shared by every reader fork) — 2026-11-12

Owner's ask: "a full sweep of all 43 rounds and the repo as a whole; see if anything was left over; fresh eyes to move the ball."
You are ONE reader in a partitioned sweep. Your partition is in your prompt. Read-only on the repo: do NOT edit, create, or
commit anything under the repo root. Write ONLY inside the scratchpad `audit/` directory. Do not spawn agents.
No compute heavier than ~3 minutes total; small verification snippets (python3/jq/grep) are encouraged.
An independent loader for the canonical 12,956-rune stream is at scratchpad `lpdata.py` (hash-verified) if you need the data.

## What already is known (do not re-report)
- Current state: Round 43 closed; Round 44 plan = physical-page channels (P1 red ink, P2 p15 grid, P3 punctuation/quote spans,
  P4 onion blobs as pads, P5 tail, R1 per-page/line key resets + p27/p54 7-gram). Deferred: I1(b) widened k<=3-4 screen,
  S2 PHP retry, 10-keytext refetch, B2 offset remainder. Owner decisions pending: WATCH band, R13 DIRECTION, KDF noise-crosser
  sign-off, with_degenerate default, N5/N4 bundle read.
- Everything in `liber-primus/PICKUP-HERE.md`, `liber-primus/MEASURED-CEILING.md` section 3, `liber-primus/handoff/PARKED.md`,
  `analysis/round36/O4-clue-coverage/untried.md` and LEDGER.json rows with status never-run/open/partially-run is ALREADY TRACKED.
  An item that is already tracked there is NOT a finding — unless the tracking is wrong, stale, or contradicted.

## What counts as a finding (classify each)
1. DROPPED-LEAD — an anomaly, near-miss, crosser, odd statistic, "worth following up", or a recommendation that appears in a
   results/synthesis doc but has NO later resolution and NO tracking row. Show how you checked (grep terms over later rounds,
   LEDGER.json, PICKUP-HERE).
2. UNDISCHARGED — a "deferred / not run / blocked / pending / TODO / reopens_if" whose condition later became satisfiable or
   satisfied, but nothing re-ran; or that silently vanished from the tracking docs.
3. LOGIC-GAP — a conclusion wider than its measurement: a closure "by mechanism" resting on a narrower model; a control that
   planted something easier than the hypothesis; a null not matched to the tested population; a statistic on the wrong
   population; multiple-comparison errors in either direction; a "negative" whose decoder could not represent the hypothesis.
4. INSTRUMENT-DEFECT — an actual bug or silent modelling assumption in a load-bearing script (READ THE CODE of the plant
   functions, decoders, scorers, loaders for the most consequential lanes in your partition; do not trust the prose).
5. UNEXAMINED-INPUT — an artifact/channel/file referenced, fetched, or held that no lane analysed, or analysed only through
   a lossy loader.
6. SHARED-PREMISE — an assumption every lane in your partition shares and none tested (examples of the kind: sign, offset 0,
   mod 29, page order 0-54, reading order, F as the only interrupter, key consumed one-per-rune, plaintext is running prose,
   Gematria index order, one cipher for all 55 pages, the doublet deficit being a *filter* rather than intrinsic to a cipher).
7. CONTRADICTION — two repo documents (or a doc and a result JSON) that disagree on a number or a status.

## Standard of evidence
- Every item: file path + line number(s) (or JSON key), a one-sentence statement, why it matters for *solving* (not for tidiness),
  what you checked to make sure it is not already resolved/tracked, and a cost estimate to discharge (minutes/hours/days; finite?).
- Rank by (chance it changes what the project believes) x (cheapness). Tidiness-only items go in a short tail list.
- An honest "NO-ERROR-FOUND; here is what I checked" for a sub-area is a valid and useful return. Do not manufacture findings.
- Be adversarial toward the repo's own claims AND toward your own candidate findings (try to kill each before you report it).

## Output
A. Write the full notes to scratchpad `audit/<YOUR-ID>.md` (as long as needed; cited).
B. Your final message (returned to the coordinator) must be <= 900 words: the ranked top findings (max 12) in the format
   `[CLASS] one-line claim — path:line — why it matters — cost`, then "checked & clean" (one line per sub-area), then
   "premises this era never tested" (max 5 bullets). No preamble.
