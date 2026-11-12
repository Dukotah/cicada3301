# Round 44 / P3 — punctuation-identity + quote-span channels: PREREG

_Dated 2026-11-09, written BEFORE any extraction output or decode. Plan of record:
`round44/CAMPAIGN-PLAN.md` lane P3 (X0 NEW #3, item 19, 4-touch blind convergence). Source map:
`round43/F2-inventory/token-channels.md` (F2b). Standing instrument: panel-R36
(`analysis/round19/I2/adjudicate.py`, `data/panels/panel-r36.npz`, 12 registers) + free bars of
record from `analysis/round34/I1-v3-null/bars_v3.py`. No git; the coordinator commits._

## Aiming Test

- **Q1 (what would a hit look like, and would this instrument recognise it?)** Four shapes:
  (a) the 7 quote-delimited spans (405 runes at F2b-mapped canon offsets), read as a selected
  stream, are plaintext in one of the 12 panel registers under at most a monoalphabetic dressing
  (Caesar/atbash/direction) — the panel sees that directly; (b) the ⁘/⁚/⁜ separator-identity
  sequence is a base-3/4 data stream that, packed to mod-29 symbols, is register plaintext;
  (c) a quote span is a CRIB: its known plaintext implies an additive/Beaufort key fragment that
  belongs to a *derived key family* (exact short period ≤13 or exact arithmetic progression
  mod 29) and, extended over the span's page, decodes the page; (d) apostrophe/numeral positions
  carry a positional channel (census; below adjudication floor, no verdict claimed).
  Recognition is proven in-lane by four plants pushed through MY OWN extraction+decode glue
  (R42 X1 rule — synthetic witness files in relikd format, parsed by the same extractor, swept by
  the same sweep code). No verdict is issued for a reading whose plant fails.
- **Q2 (measured fact raising the prior).** `round43/X0-firewall/ADJUDICATION.md` item 19:
  4 of 6 blind agents independently touched this channel; F2b measured that the loader deletes
  every one of these marks at load time (quote marks: 14→0; ⁚ and inline ⁜ identity erased;
  apostrophes deleted), i.e. **no decode in 309 ledger rows has ever been able to see them** —
  the same blind-spot class that hid the pp49–51 payload for six campaigns. B-12's own
  not_covered names "Inter-word separator SHAPE (only counts and gaps were measured)".
- **Q3 (bounded?).** Fully enumerable, fixed before running: reading (a) 928 decodes; reading
  (b) 1,820 decodes; reading (c) 26,784 derivations (crib list and placement arithmetic below),
  of which only screen-survivors are decoded; reading (d) is a census. Minutes of compute.
- **Q4** — see `three_conditionals` below.
- **Q5 (kill condition, checkpoint at ~10% of budget).** The witness cross-check (step 1) and
  the plants ARE the checkpoint. KILL the lane (no verdict on any reading) if: the relikd rune
  stream fails to match the krisyotam canon stream rune-for-rune over the shared 12,956 runes;
  or the 7 quote spans extracted from relikd disagree with the spans quoted in scream314 (rune
  sequence) beyond the already-documented witness differences; or Plant-A's extraction does not
  reproduce its ground-truth span offsets exactly. A reading whose plant decodes but does not
  cross its bar is reported with measured power capped (verdict `inconclusive` for that reading,
  never `negative`).

## Hypothesis

The non-rune marks the solver input erases — quote marks, the ⁘/⁚/⁜ separator hierarchy,
apostrophes, inline numerals — are a deliberate data channel: quote spans select or crib
plaintext, separator identity encodes a token stream, positions parameterize a key.

## Coverage of adjacent ledger rows (queried before running; LEDGER.json untouched)

- **R11-S2-NUMBER-CHANNEL** (measured): separator channel as RUN LENGTHS only ("separators read
  as typography"); not_covered "binary/ternary byte routes" — reading (b) is exactly that gap.
- **B-12** (measured): 11 geometric channels, 8 bit packings — counts and gaps; not_covered:
  "Inter-word separator SHAPE (only counts and gaps were measured)". Reading (b) is the SHAPE.
- **C-02** (negative): ciphertext-visible positional subsets = line/word/page/sentence
  initials+finals, 232 GP variants each. Quote-span membership is NOT one of its subsets.
- **VERDICT-OTP-CLASS** (open): caps crib adjudication — a crib fixes key values nothing can
  check unless the key is derived/running. Reading (c) therefore pairs every crib with a
  **derived key family** (exact period ≤13 / exact AP mod 29) and only a family member that
  *extends over the rest of the page* is adjudicated. Bare crib "fits" are not reportable.
- **R26-B-KEYTEXT-RUNNINGKEY-SKIPAWARE / R42-C1-R35-KEYTEXTS-RUN** (partially-run / negative):
  keytext running keys — adjacent to (c)'s key families but disjoint (mine are derived
  periodic/AP, not keytexts); not re-run.
- **R43-F6-PAGE56-HASH-AS-KEY, R28-L2**: harness precedent only; cells disjoint.
- Grep over all 309 rows: no row contains the quote spans, the ⁚/⁜ identity stream, or the
  apostrophe positions (X0 item 19 stamped NEW on exactly this basis).

## Source-of-truth / witness protocol (step 1, before any decode)

Positions: `data/relikd/p*.txt` (9 files, file order = page order), whose rune stream F2b
verified char-identical to `data/krisyotam_runes.txt` for all 12,956 shared runes — RE-VERIFIED
in-lane before use. Spans: a quote span = the runes strictly between an opening `"` and its
closing `"` (7 spans expected, 405 runes, offsets per the F2b table: [1659,1677) [5459,5478)
[9715,9727) [9811,9869) [10211,10279) [10279,10439) [12522,12592)). Cross-witness: each span's
rune sequence must also appear quoted in `data/scream314_lp.md`; any disagreement is reported,
and an undetermined span kills the lane (Q5). Separator stream: all ⁘/⁚/⁜ tokens in relikd file
order (expected 145+4+31=180), with a second variant excluding the 4 p15 number-grid row dots
(176, documented in F2b as grid-row terminators); counts cross-checked against krisyotam's
181 `.` under F2b's mapping rules. Apostrophes: expected canon rune indices 1110, 5138, 8515,
10089 (F2b §4), re-derived in-lane.

## Fixed test matrix

**(a) Quote spans as selection channel — N_a = 928.** Streams: S0 = 405-rune concatenation +
S1..S7 = the 7 spans (L = 18,19,12,58,68,160,70). Variants per stream: direction {fwd,rev} ×
atbash {off,on} × Caesar shift 0..28 = 116. 8 × 116 = 928 decodes, each adjudicated
(panel-R36 pmax, degenerate guard on).

**(b) Separator identity as token stream — N_b = 1,820.**
- b1 (base-3, the 180/176-token ⁘⁚⁜ stream): symbol assignment = all 6 permutations of {0,1,2}
  over (⁘,⁚,⁜) × direction {fwd,rev} × packing {triples big-endian → 0..26, pairs → 0..8} ×
  stream variant {incl-grid 180, excl-grid 176} = 48 decodes (L = 60/90 and 58/88; remainder
  tokens dropped, stated).
- b2 (base-4, all 2,911 separators incl. •): assignment {(•,⁘,⁚,⁜)→(0,1,2,3), reverse} ×
  direction {fwd,rev} × packing {pair→0..15; 2-bit→5-bit groups mod 29 (L=1164);
  triple→0..63 mod 29 (L=970)} = 12 decodes.
- b3 (separator identity as sparse mod-29 keystream over adjacent runes, whole canon pages
  0–54 then adjudicated per page): maps = 6 permutations of (1,2,3) over (⁘,⁚,⁜) × sign {+,−}
  × target {next rune, prev rune} = 24 configs, plus base-4 maps {(•,⁘,⁚,⁜)→(0,1,2,3),
  reverse} × sign × target = 8 configs; (24+8) × 55 pages = 1,760 decodes.
  N_b = 48 + 12 + 1,760 = 1,820.

**(c) Quote spans as cribs gating a derived-key-family sweep — N_c = 26,784 (upper bound on
adjudications; every derivation counted whether or not its screen survives).** Fixed crib list
(24 phrases, LP1-solved vocabulary + the 2014 signed messages, all ≥10 runes under
`keyword_to_indices`; the exact list is frozen in `cribs.py` written with this PREREG):
BELIEVE NOTHING FROM THIS BOOK; EXCEPT WHAT YOU KNOW TO BE TRUE; TEST THE KNOWLEDGE; FIND YOUR
TRUTH; EXPERIENCE YOUR DEATH; DO NOT EDIT OR CHANGE THIS BOOK; THE LOSS OF DIVINITY; WELCOME
PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS; SOME WISDOM; THE PRIMES ARE SACRED;
THE TOTIENT FUNCTION IS SACRED; ALL THINGS SHOULD BE ENCRYPTED; SHED YOUR CIRCUMFERENCES; SHED
OUR CIRCUMFERENCES; AN INSTRUCTION; COMMAND YOUR OWN SELF; THE CIRCUMFERENCE PRACTICES THREE
BEHAVIORS; EPIPHANY IS UPON YOU; YOUR PILGRIMAGE HAS BEGUN; ENLIGHTENMENT AWAITS; BEWARE FALSE
PATHS; ALWAYS VERIFY PGP SIGNATURE; THE INSTAR EMERGENCE; A WARNING BELIEVE NOTHING FROM THIS
BOOK. Placements: every alignment of each crib inside each span (Σ = 6,696) × derivations
{additive k=(c−p) mod 29; Beaufort k=(c+p) mod 29} × atbash-on-ciphertext {off,on} = 26,784.
Screen (deterministic, fixed): the implied fragment has an exact period p ∈ 1..13 with
fragment length ≥ 2p, OR is an exact arithmetic progression mod 29 (constant nonzero first
difference). Survivors only: extend the key over every canon page the span touches (period/AP
continued, anchored at the span's in-page offset), decode the full page under the derivation's
inverse, adjudicate. VERDICT-OTP-CLASS compliance: only extended-page crossers are reportable;
a crib fit alone is not a result.

**(d) Apostrophe + inline-numeral positional channel — census, no verdict.** The 4 apostrophe
canon indices and the inline numerals ('7' on solver p10; list labels 1–5 on pp36–38): report
positions, runes at/after positions, gaps mod 29, and the concatenated value stream. All
streams are length ≤ 12 — below any calibrated bar node (min L=120). Pre-declared outcome
class: `measured` census only; no negative is claimed for (d).

## Thresholds (FIXED before running; bars_v3 free bar of record, α=0.01, L_cap = largest of
{120,240,400,729} ≤ decode length, floored at 120 — the R42 C1 convention)

| reading | N | L_cap | bar (pmax) |
|---|---|---|---|
| (a) | 928 | 120 | **11.584** |
| (a) concat L=405 | 928 | 400 | **16.902** |
| (b) | 1,820 | 120 | **11.943** |
| (b) pages L≥240 | 1,820 | 240 | **15.925** |
| (b) b2 long streams | 1,820 | 729 | **20.296** |
| (c) extended pages | 26,784 | 120 | **13.376** |
| (c) extended pages L≥240 | 26,784 | 240 | **17.913** |

A cell crosses iff its decode is non-degenerate (standing R38 I2 guard) and pmax ≥ the bar at
its L_cap. 0 crossers → NEGATIVE for that reading (conditionals below). Any crosser →
**FLAGGED-FOR-ORACLE per `liber-primus/HUMAN-ORACLE.md`, never self-certified**. Thresholds are
not edited after results; any addendum is dated.

## Positive controls (planted through MY OWN extraction+decode glue; synthetic relikd-format
witness files parsed by the SAME extractor and swept by the SAME sweep code)

- **Plant-A (extraction + reading a):** synthetic witness with 2 quoted spans at known rune
  offsets; span 2 (L=160) = a known English plaintext encoded via Gematria and Caesar-shifted
  +11 (fwd, atbash off). Pass iff the extractor reproduces both ground-truth offsets exactly
  AND the reading-(a) sweep's best cell for that span is (fwd, atb off, decode shift 18) with
  exact plaintext recovery and pmax ≥ 11.584 (bar at N_a=928, L_cap 120).
- **Plant-B (reading b1):** synthetic witness whose 180 ⁘/⁚/⁜ identities encode a 60-rune
  English text in base-3 triples under permutation id, fwd. Pass iff the b1 sweep recovers the
  exact plaintext in the planted cell and that cell is the grid argmax; its pmax vs the 11.943
  bar is the MEASURED POWER of (b) at the channel's real length and is reported either way —
  if it does not cross, reading (b1)'s no-crosser outcome is capped to `inconclusive`.
- **Plant-B2 (reading b2):** synthetic witness with 2,911 separators whose base-4 identities,
  packed 5-bit, encode a 582-rune English text (values kept <29 so packing is exactly
  invertible). Pass criterion as Plant-B; decode L=582 → L_cap 400; bar
  bar_v3(1820,400,'free') = **17.362**, fixed here (value corrected from a mis-computed
  18.588 before any extraction or decode ran; dated 2026-11-09).
- **Plant-C (reading c):** synthetic 240-rune page = English plaintext containing the crib
  "THE PRIMES ARE SACRED" inside a quoted span (L=58), enciphered with a period-7 additive key.
  Pass iff the crib machinery finds the placement, derives the fragment, the screen fires
  (period 7), the extension decodes the full page with exact recovery and pmax ≥ 17.913.
- **Plant-D (reading b3):** synthetic page (real page-0 separator layout, English plaintext)
  with separator-adjacent runes shifted by map (⁘,⁚,⁜)→(1,2,3), sign +, target next. Pass iff
  the b3 sweep's planted config recovers the plaintext at 100% and is the per-page argmax.

No verdict for a reading unless its plant passes its pass criterion.

## three_conditionals

- **key_space:** (a) monoalphabetic dressings only (2 dir × 2 atbash × 29 shifts) over the
  quote-span selection; (b) separator-identity token stream under 6+2 symbol assignments,
  2 directions, 5 packings, and sparse adjacent-rune keystreams with value maps over
  permutations of (1,2,3)/(0..3); (c) derived key families = exact period 1..13 and exact
  AP mod 29, seeded by 24 fixed cribs at all in-span alignments, additive/Beaufort × atbash.
  NOT in the key space: keytext running keys, non-AP non-periodic derived keys, crib lists
  beyond the 24, spans as transposition/selection KEYS over other pages.
- **transition_model:** position-independent substitution mod 29 (Caesar/Vigenère-additive/
  Beaufort × atbash), rigid alignment, no skips/resets; (b3) sparse additive shifts at
  separator-adjacent positions only.
- **adjudicator_register:** panel-R36, 12 registers, direct-decode panel-max pmax
  (`adjudicate`), degenerate guard on; free-null bars of record as tabled. Registers outside
  the panel (and sub-120-rune power, per the plants) are the stated blind spots.

## Coverage statement (to be restated with numbers in RESULTS.md)

Covered: the quote-span selection channel under monoalphabetic dressings; separator SHAPE as
base-3/4 data under the fixed packings; crib-implied periodic/AP key fragments extended over
their pages; apostrophe/numeral census. NOT covered: quote spans as keys over OTHER pages;
richer span dressings (polyalphabetic within-span); separator stream under packings/assignments
beyond those fixed; crib texts beyond the 24; non-periodic/non-AP derived families (incl.
keytexts — R26-B/R42-C1's ground); per-line resets (lane R1's ground); sub-120-rune
adjudication power wherever the plants measure it short.

## Deliverables

`extract_channels.py` (witness parse + cross-check), `channels.json`, `plants.py` + plant
witness files + `plants_results.json`, `run_p3.py`, `p3_results.json`, `RESULTS.md`,
`ledger_rows.json` (drafts; LEDGER.json itself untouched).

## Addendum 1 (2026-11-09, before any plant or sweep ran; extraction/witness checks only run so far)

Plant-B2 arithmetic correction: 2,911 base-4 tokens carry 5,822 bits = 1,164 five-bit groups
(+2 remainder bits, dropped — same remainder convention as the real reading). The plant text is
therefore **1,164 runes**, not 582; its decode L = 1,164 → L_cap 729, pass bar
`bar_v3(1820, 729, 'free')` = **20.296** (already in the threshold table). The 17.362 value
stays in the table as the generic (b) L_cap-400 bar. No other change.
