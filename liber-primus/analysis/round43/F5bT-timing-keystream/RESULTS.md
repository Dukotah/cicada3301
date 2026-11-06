# Round 43 / F5b-T — onion-2 timing channel as LP2 keystream: RESULTS

2026-11-03. `PREREG.md` first (thresholds and matrix fixed before the merge and before any decode).
Standing instrument throughout: panel-R36 (12 registers) via `round19/I2/adjudicate.py`, free-null bar
of record `round34/I1-v3-null/bars_v3.py` — the same glue as R42 C1.

## Verdict: NEGATIVE (measured, panel-R36; plant gate passed 3/3) — and the witnesses are CONSISTENT

## 1. Witness merge (`merge_witnesses.py` -> `merged_intervals.json`, `key_streams.json`)

Four sources merged, byte positions fixed by unique byte-run match in the final 256-byte string,
BotSottile's absolute GMT+1 timestamps as anchor (restart dumps and off-grid stamps treated as upper
bounds only, per PREREG):

- **112 of 255 inter-byte intervals attested exactly** (bytes 143–256, minus the bounded pair 190–191).
  31 cells multi-witness, 81 single-witness, of which 9 (bytes 143–151) carry the wiki witness's own
  "cannot confirm" flag.
- **Alignment:** Cripion101 block 1 = bytes 152–173, block 2 = bytes 174–182 (contiguous with block 1);
  the two wiki tables = bytes 152–171; the wiki-00140 25-sample = bytes 143–167. BotSottile's log
  yields exact arrivals for 169–189 and 192–256.
- **Independent-witness agreement is exact everywhere they overlap.** All 14 cells where BotSottile's
  absolute timestamps and Cripion101's elapsed column both speak (bytes 169–173, 174–182) agree to the
  minute. Cripion vs wiki-00120 vs wiki-00140: all 19 shared interval values identical. The wiki-00140
  25-sample tail reproduces the other tables exactly, and its "unconfirmed" head independently matches
  Cripion's elapsed value at byte 152 (05).
- **Every inconsistency found (3 findings, one root cause):** Cripion's clock-minute for byte 168 (`fc`)
  reads 25 where wiki-00120 reads 15; Cripion's own elapsed column (05) contradicts his own minute and
  matches wiki-00120's clock and BOTH tables' interval value. Classified per PREREG as a single
  transcription slip in one digit of one clock cell; the interval VALUE (05) is never in dispute
  (no `value_disagreements` in the merge output). No timezone issue (minutes are tz-invariant; the
  04:10-GMT = 05:10-GMT+1 final-byte cross-check and the len-250/03:25-GMT cross-check both concur).
- **Bytes 190–191:** BotSottile offline (restart dump 18:56); sum of the two intervals = 30 min
  (18:30 -> 19:00), each >= 5 -> 5 bounded variants, swept as `S_AB(v)`.
- All 112 intervals are multiples of 5 and >= 5 ("multiples of five" confirmed at cell level).

**Consistency verdict: the independent witnesses agree where they overlap; nothing contradicts beyond
one single-digit transcription slip. The lane proceeds.**

Key streams derived (interval/5): `S_A` bytes 143–189 (47 values: 2 6 2 3 1 1 2 3 1 1 4 1 2 3 3 2 1 5
3 3 1 4 1 4 1 1 3 2 7 2 1 2 3 1 1 3 5 3 3 2 3 2 2 2 1 1 2), `S_B` bytes 192–256 (65 values), and the
five 114-value bridge variants `S_AB(1,5)…(5,1)`.

## 2. Positive controls (plant gate) — PASSED 3/3

Three known English-register plaintexts encrypted with interval-derived keys exactly as pre-registered
and pushed through the identical sweep (the sweep code does not distinguish them):

| plant | planted cell | grid-best pmax | bar | found planted cell | plaintext recovered |
|---|---|---|---|---|---|
| P1 | S_AB(3,3) fwd m1 vig- R rot17 L240 | **38.32** | 18.10 | yes | yes (byte-exact) |
| P2 | S_B rev m3 beaufort R rot5 L200 | **33.40** | 13.51 | yes | yes (byte-exact) |
| P3 | S_A fwd m2 vig+/atbash R rot0 L240 | **32.32** | 18.10 | yes | yes (byte-exact) |

All three grid-bests are non-degenerate, land in exactly the planted (stream, direction, mapping,
config, mode, rotation) cell, clear the bar by 14–25 z, and reproduce the plaintext byte-exactly.
The pipeline sees what it is supposed to see.

## 3. Keystream test (`run_f5bt.py` -> `f5bt_results.json`)

- **Matrix:** 7 streams x 2 directions x 3 mappings (k mod 29; 5k mod 29; Gematria-Primus prime mod 29)
  x 6 configs (vig-, vig+, Beaufort; each plain and atbash-composed) x {repeating: every rotation;
  one-shot page-start aligned: every suffix >= 60} = **34,668 decodes per page** (asserted at runtime),
  over all **55 unsolved pages** = **1,906,740 scored decodes** (+ 104,004 control decodes). 19.7 s.
- **Bars (fixed in PREREG before the run):** `bars_v3(34668, L_cap, "free")` = **13.513** (L_cap 120)
  / **18.103** (L_cap 240).
- **Result: 0 crossers.** Observed global best pmax **5.364** (page 30, S_B fwd, m2, beaufort+atbash,
  repeating rot 36, L=263) vs bar **18.103** — 12.7 z below the bar, deep in the wrong-key null.
  No near-miss anywhere in the grid (plants cleared the same bars by 14+ z in the same run).

## 4. Coverage x power

- **Covered:** interval cells bytes 143–256 (112 exact + 2 bounded of 255 = ~44% of the channel), as
  interval/5 under the full pre-registered matrix above, panel-R36 power (12 registers), free bar of
  record, both the single-witness "cannot confirm" head of S_A and the 5 bridge variants included.
- **NOT covered:** the intervals of bytes 2–142 (never witnessed in any held source — if the true key
  needs that span at a fixed absolute alignment, this lane cannot see it); the byte VALUES as key
  (separate, already-held object); intervals as transposition/permutation/skip/page-selection material;
  arithmetic beyond the three pre-registered mappings; interleavings of intervals with byte values;
  sub-runs shorter than the attested runs; sub-60-rune one-shot alignments; a fresh per-shuffle null
  (the standing bar is the null of record).

## 5. Files

`PREREG.md`, `merge_witnesses.py`, `merged_intervals.json`, `key_streams.json`, `run_f5bt.py`,
`f5bt_results.json`, `RESULTS.md`, `ledger_rows.json` (draft rows for the parent to apply —
`LEDGER.json` itself untouched by this lane).
