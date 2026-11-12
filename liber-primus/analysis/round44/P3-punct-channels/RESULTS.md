# Round 44 / P3 — punctuation-identity + quote-span channels: RESULTS

_Run 2026-11-09 per `PREREG.md` (dated before any extraction output; Addendum 1 = the Plant-B2
length arithmetic, corrected before any plant or sweep ran). Instrument: panel-R36
(`analysis/round19/I2/adjudicate.py`), free bars of record (`round34/I1-v3-null/bars_v3.py`),
degenerate guard on. Everything below reproduces from `extract_channels.py` → `plants.py` →
`run_p3.py` in this folder._

## Verdict

**NEGATIVE on readings (a), (b), (c); (d) is a census (measured, no verdict claimed — as
preregistered). 0 bar-crossers anywhere. Nothing flagged for oracle.** All five positive
controls passed through the lane's own extraction+decode glue, and every one also **crossed its
bar** — including Plant-B at the real channel's own length (L=60), so the (b1) negative is a
true powered negative, not an underpowered one.

## Step 1 — witness cross-check (kill gate: PASSED)

- relikd 9-file rune stream = krisyotam canon prefix, **12,956/12,956 exact**.
- 7 quote spans extracted at **exactly the F2b offsets** ([1659,1677) [5459,5478) [9715,9727)
  [9811,9869) [10211,10279) [10279,10439) [12522,12592); 405 runes).
- **All 7 spans appear quoted verbatim in scream314_lp.md** (rune+quote skeleton match) — the
  two independent transcriptions agree on both the span contents and the quoting.
- Apostrophes re-derived at 1110, 5138, 8515, 10089 (= F2b). Separator counts 180 (⁘145 ⁚4 ⁜31)
  incl. the 4 p15 grid-row dots / 176 excl.; base-4 stream 2,911 — all as preregistered.

## Positive controls (plants_results.json — 5/5 PASSED, 5/5 crossed)

| plant | reading | shape | pmax | bar | recovered |
|---|---|---|---|---|---|
| A | (a) extraction + selection | quoted span L=160, Caesar+11 | 26.30 | 11.584 | exact, planted cell |
| B | (b1) | 180 sep identities = base-3 triples, L=60 | 17.45 | 11.943 | exact, planted cell, argmax |
| B2 | (b2) | 2,911 sep identities = 5-bit packing, L=1164 | 63.39 | 20.296 | exact, planted cell, argmax |
| C | (c) | crib in quoted span, period-7 page key | 31.28 | 17.913 | exact full page, screen fired p=7 |
| D | (b3) | sep-adjacent +v shifts, map (1,2,3) | 28.55 | 11.943 | 100%, planted config argmax |

## Test matrix and numbers vs bar (p3_results.json)

| reading | decodes | bar(s) | best non-degenerate pmax | crossers |
|---|---|---|---|---|
| (a) spans as selection: 8 streams × 116 dressings | **928** | 11.584 (L_cap 120) / 16.902 (concat, 400) | **7.259** (span3, L=12, rev+atbash+24) ; concat best 2.865 | **0** |
| (b1) base-3 identity stream: 6 perms × 2 dir × 2 packings × 2 variants | 48 | 11.943 | all 48 **degenerate** (see below) | **0** |
| (b2) base-4 incl. •: 2 assigns × 2 dir × 3 packings | 12 | 20.296 (L_cap 729) | all 12 **degenerate** | **0** |
| (b3) identity as sparse keystream over adjacent runes: 32 configs × 55 pages | 1,760 | 11.943 / 15.925 | **3.577** (b3-4rev, sign −, prev, page 35, L=271) | **0** |
| (c) crib-gated derived-key sweep | **26,784 derivations** | 13.376 / 17.913 | — (see below) | **0** |

- **(a)** The quote-span channel is not monoalphabetically-dressed plaintext in any of the 12
  registers: the 405-rune concatenation's best dressing scores 2.865 vs bar 16.902 (14z-scale
  below); every per-span best is ≤7.26 vs 11.584, and the short-span bests (L=12–19) are the
  expected small-N inflation, not near-misses.
- **(b1/b2)** Every one of the 60 real token-stream decodes trips the standing degenerate guard
  — and that is itself the measurement: the real identity stream is **145 ⁘ / 4 ⁚ / 31 ⁜**
  (0.81 bits/token; the base-4 stream with • is 0.385 bits/token), i.e. far too skewed to carry
  register text under ANY packing, while Plant-B proves a genuinely data-bearing stream of the
  identical shape and length decodes and crosses. The separator hierarchy reads as typography
  (punctuation frequencies), exactly as R11-S2 found for run-lengths — now established for
  identity/SHAPE too, closing B-12's named not_covered.
- **(b3)** No separator-adjacent correction scheme in the 32-config map family moves any page
  off noise: best 3.577 vs bar 15.925.
- **(c)** Of **26,784** crib placements × derivations (24 cribs ≥10 runes × 7 spans × all
  alignments × {additive, Beaufort} × {atbash off,on}), **zero** implied key fragments belong to
  the derived family at all — not one is exactly periodic (p ≤ 13, len ≥ 2p) or an exact AP
  mod 29 — so zero page extensions existed to adjudicate (adjudications = 0; the N=26,784 bar
  was never needed). Plant-C proves the screen+extension+adjudication path end-to-end. Under
  the VERDICT-OTP-CLASS cap this is the strongest statement this reading permits: no crib from
  the fixed list implies a periodic/AP key anywhere in any span.
- **(d) census (measured; no verdict):** apostrophes at canon 1110/5138/8515/10089 (mod 29:
  8,5,18,26); runes before→after: I→W, O→Y, E→T, J→C (correcting F2b §4's `'ᚳ` example glyph —
  it is the 4th instance only; positions all confirmed); gaps 4028/3377/1574 (mod 29: 26,13,8).
  Inline numerals: the `7` at canon offset 2566; list labels 1–5 at offsets 8805/8944/9035/
  9133/9229; the 16-number grid digits all at offset 3612 (lane P2's object, not re-run here);
  the base-60 table digits at offset 12114 (pp49–51 payload, covered by A-04/R28-L2, not
  re-run). All candidate streams are length ≤ 12 — below the L=120 bar node.

## Coverage × power

**Covered** (panel-R36, 12 registers, free bars of record, α=0.01 family-wise per reading, all
plants passed AND crossed): the 7 quote spans (405 runes, both witnesses agreeing) as a
selection channel under 2 dir × 2 atbash × 29 shifts, per-span and concatenated; the separator
IDENTITY stream (shape) as base-3 (6 assignments × 2 dir × triples/pairs × grid-incl/excl) and
base-4 (2 assignments × 2 dir × pair16/5-bit/tri64) data, and as a sparse mod-29 keystream over
separator-adjacent runes (32 maps × 55 pages); crib-implied additive/Beaufort key fragments
from 24 fixed cribs at every in-span alignment, screened for exact period ≤13 / exact AP and
(had any survived) extended page-wide.

**NOT covered:** quote spans as keys/selectors over OTHER pages; polyalphabetic dressing
within spans; separator packings/assignments beyond those fixed; crib texts beyond the 24;
derived families beyond exact-period/AP (keytext running keys are R26-B/R42-C1's ground;
per-line resets are lane R1's); sub-120-rune bar nodes (bars floored at 120 — though plants at
L=60 and L=12-grade streams were never claimed); registers outside the 12-register panel;
the p15 grid numbers (lane P2) and base-60 tables (A-04/R28-L2) seen in the numeral census.

**Reopens if:** a new witness changes any span boundary or separator identity; a preregistered
reading pairs the spans with a key family outside exact-period/AP; the panel gains a register;
an oracle-side reason emerges to read the 0.81-bit/token identity stream as a sub-register
channel (e.g. a binary/Baconian payload shorter than 60 symbols with an external key).

## Files

`PREREG.md` (+ Addendum 1), `extract_channels.py`, `channels.json`, `cribs.py`, `plants.py`,
`plant_[a,b,b2,c,d].txt`, `plants_results.json`, `run_p3.py`, `p3_results.json`,
`ledger_rows.json` (drafts — LEDGER.json untouched by this lane).
