# Round 43 / F5b-T — onion-2 timing channel as LP2 key material: PREREG

_Dated 2026-11-03, written BEFORE the witness merge and before any decode output. Follow-on named in
`round43/F5-stored/RESULTS-irc.md` §1a. panel-R36, bars_v3 free bar of record, no `git`._

## Aiming Test

- **Q1 (target).** The cu343l33nqaekrnw.onion (Jan 6-7 2014) growing-string INTER-ARRIVAL INTERVALS,
  divided by 5, as deliberate numeric key material for the 55 unsolved LP2 pages. Finite object
  (doctrine R5): at most 255 interval cells, of which the four stored witnesses attest ~112.
  Sources (all local, stored by F5b):
  - `round43/F5-stored/onion2-timing_BotSottile_qn8jmPJr.txt` — absolute per-byte IRC timestamps
    (GMT+1), string lengths 159→256.
  - `round43/F5-stored/onion2-timing_Cripion101_5bTLHqCN.txt` — 31 samples (22 + 9), clock-minute /
    elapsed / byte.
  - `corpus/C-community/wikis/uncovering-cicada/export_cur_00120.xml` — 20-column
    clock/interval/interval÷5/byte table.
  - `corpus/C-community/wikis/uncovering-cicada/export_cur_00140.xml` — same 20-column table in list
    form + a 25-sample delay sequence (first 10 flagged "cannot confirm" by the witness).
- **Q2 (prior).** Low-to-moderate for the class, flat within it: the intervals are Cicada-chosen
  structured numbers ("multiples of five", 23 hours of deliberate drip) that no prior lane ever held;
  but nothing ties them to LP2 specifically, and coverage is partial (bytes ~143-256 only), so even a
  true keystream could be missed if the usable alignment needs bytes 1-142. Value = first-ever test of
  a never-held Cicada-published numeric channel, closing F5b's named follow-on either way.
- **Q3 (instrument / power).** The STANDING instrument, same glue as R42 C1
  (`analysis/round19/I2/adjudicate.py` `adjudicate`/`adjudicate_batch`, panel
  `data/panels/panel-r36.npz`, 12 registers, panel-max pmax; pages via `analysis/run_stats.load_pages()[:-2]`
  = 55 unsolved pages, L 66-277). No hand-rolled scorer. Power is demonstrated in-lane by three planted
  positive controls pushed through the identical sweep (below); verdict is void unless all plants recover.
- **Q4 (three conditionals).** See `three_conditionals` below.
- **Q5 (kill / success).** A page crosses iff its non-degenerate grid-max pmax >= its free bar (below).
  0 crossers -> NEGATIVE (measured, panel-R36, coverage as stated). Any crosser -> FLAGGED-FOR-ORACLE
  per `HUMAN-ORACLE.md`, never auto-certified. If independent witnesses contradict beyond
  timezone/rounding/single-digit transcription slips, or if any planted control fails, the lane is
  KILLED (no keystream verdict is issued).

## Hypothesis

The onion-2 inter-arrival intervals ÷ 5 are a deliberate numeric keystream for the unsolved LP2 pages,
usable additively (mod 29), as Beaufort, atbash-composed, forward or reversed, repeating or one-shot,
raw or mapped through the Gematria Primus primes.

## Witness-merge protocol (step 1, before any decode)

Anchor = BotSottile absolute timestamps (GMT+1; minutes are timezone-invariant). Bot-restart full-string
dumps (12:39, 12:53, 18:56 — and any other non-5-minute-grid stamp) are upper bounds, not arrivals.
Byte positions are fixed by locating each witness's byte run in the final 256-byte string (held in both
wiki exports and the BotSottile log). Every overlapping cell is cross-checked; every mismatch is
reported. A single clock-minute digit that contradicts the SAME witness's own elapsed column while all
other witnesses agree is classified a transcription slip (reported, then resolved by majority);
anything else is a mutual inconsistency and kills the lane if it leaves the interval value undetermined.
Cells where the bot was offline and no other witness reports (expected: bytes 190-191, bounded to
interval_190 + interval_191 = 30 min, each >= 5) are carried as bounded-variant cells, not exact cells.
Output: `merged_intervals.json`, per-cell `{pos, interval_min, k (=interval/5), witnesses, confidence,
conflicts}`.

## Fixed key material (structure fixed now; values come from the merge)

- `S_A` = k-sequence for bytes 143-189 (expected 47 values; 143-151 are single-witness "cannot
  confirm" cells — included, and named in coverage).
- `S_B` = k-sequence for bytes 192-256 (expected 65 values).
- `S_AB(v)` = bytes 143-256 (114 values) with the bounded bridge (k_190, k_191) = v, for all v in
  {(1,5),(2,4),(3,3),(4,2),(5,1)} (sum 6, each >= 1).
  Seven streams total. If the merge changes these extents, the actual extents are recorded and used;
  the sweep structure does not change.

## Fixed sweep (the test matrix)

For each unsolved page c (55), each stream S (7), each direction d in {forward, reversed}, each mapping
m in {m1: k mod 29; m2: 5k mod 29 (the raw minutes); m3: PRIMES[k mod 29] mod 29 (Gematria Primus)},
each cipher config in {vig-: (c - K) mod 29; vig+: (c + K) mod 29; beaufort: (K - c) mod 29} x
atbash in {off, on: c -> 28 - c first} (6 configs):
- **Mode R (repeating):** rotations r = 0..Lk-1, decode the whole page with key index (r+i) mod Lk.
- **Mode O (one-shot, page-start aligned, attested-run alignment sweep):** key suffix S[r:] applied at
  page start, decode = page prefix of length min(Lk - r, L_page), for every r with Lk - r >= 60.
  (S_A, Lk=47, has no mode-O rows; noted in coverage.)

Grid size per page (fixed now): [47 + (65+6) + 5x(114+55)] x 2 x 3 x 6 = **N = 34,668**.

## Thresholds (fixed BEFORE running)

Bar = standing free-null bar of record, `bars_v3.bar_v3(34668, L_cap, "free")` with L_cap = the largest
of {120, 240, 400, 729} <= decode length, floored at 120 (the R42 C1 convention). Exact values at
N = 34,668, computed from the committed fit before any decode:

| L_cap | bar (pmax) |
|---|---|
| 120 | **13.513** |
| 240 | **18.103** |
| 400 | 19.374 (no unsolved page reaches L=400; listed for completeness) |
| 729 | 22.430 (idem) |

A page crosses iff a non-degenerate decode's panel-R36 pmax >= the bar at its decode's L_cap.
alpha = 0.01 family-wise within the per-page grid, per the bars_v3 model of record.

## three_conditionals

- **key_space:** the onion-2 interval/5 sequences from the merged witness table — 7 streams (S_A, S_B,
  5 bridge variants of S_AB) x 2 directions x 3 value mappings (raw mod 29, x5 mod 29, Gematria-Primus
  prime mod 29). Bytes 1-142's intervals are NOT in the key space (unattested).
- **transition_model:** position-independent additive/Beaufort substitution mod 29 (vig+, vig-,
  beaufort) x atbash pre-composition, key applied repeating (all rotations) or one-shot page-start
  aligned (suffix sweep, min decode 60).
- **adjudicator_register:** panel-R36 (12 registers), beam-free direct-decode panel-max pmax
  (`adjudicate`/`adjudicate_batch`), free-null bar of record `bars_v3 'free'` as tabled above.

## Positive controls (planted through the SAME glue, scored in the SAME sweep)

Three plants, built before the real sweep and appended as synthetic pages; the sweep code does not
distinguish them. Each encrypts a known English-register plaintext (>= 200 runes) with an
interval-derived key so that exactly one swept cell inverts it:
- **P1:** plaintext A, key S_AB(3,3), mapping m1, config vig- (encrypt: c = (p + K) mod 29), forward,
  repeating, rotation 17.
- **P2:** plaintext B, key S_B reversed, mapping m3, config beaufort (encrypt: c = (K - p) mod 29),
  rotation 5.
- **P3:** plaintext C, key S_A forward, mapping m2, config vig+ with atbash (encrypt:
  c = 28 - ((p - K) mod 29)), rotation 0.
Pass iff every plant's grid-best is non-degenerate, >= its bar, and sits in the planted
(stream, direction, mapping, config) cell. Any plant failing -> lane KILLED, no verdict.

## Coverage statement

Covered: interval cells for bytes 143-256 (~112 exact + 2 bounded of 255; ~44% of the channel), under
the 7x2x3x6 x {repeating all rotations, one-shot suffix >= 60} matrix above, over all 55 unsolved pages,
at panel-R36 power with the free bar of record.
NOT covered: intervals of bytes 2-142 (never witnessed in any held source); the byte VALUES as key
(already in the record; separate cell); intervals as transposition/permutation keys, page-selection
indices, rune-skip schedules, or lengths/counts; non-/5 arithmetic other than the three named mappings;
interleavings with the byte values; keys shorter than the attested runs (sub-runs); a fresh per-shuffle
null (the standing bar is the null of record); sub-60-rune one-shot alignments.

## Deliverables

`merge_witnesses.py`, `merged_intervals.json`, `run_f5bt.py`, `f5bt_results.json`, `RESULTS.md`,
`ledger_rows.json` (draft rows, id `R43-F5BT-TIMING-KEYSTREAM`; parent applies — `LEDGER.json` itself
is not modified by this lane).
