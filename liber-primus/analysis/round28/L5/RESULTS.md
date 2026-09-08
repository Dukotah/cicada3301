# Round 28 / L5 — payload-micro (E-01w / E-02v / H-03r) · RESULTS

_Executed 2026-09-08, nice -15 single-threaded, stdlib only. Trust anchor
`python3 tests/validate.py` = ALL VALIDATIONS PASSED (5/5) before the run.
Runner: `l5_payload_micro.py` + `h03r_indented.py`; raw output: `results.json`._

## Verdict: NEGATIVE — all three never-run remainders are now measured nulls. One community claim resolved as a layout artifact.

## 0. What this lane actually was (anti-repeat correction)

The planner's charter said E-01/E-02/H-03 "have no ledger row". That premise was stale:
all three ids carry NEGATIVE rows (E-01 → round 19/C1 with 738 tuples and a passed
strict-tier control; E-02/H-03 → round 16/zeroFP). Per doctrine R7 the lane was
re-scoped (PREREG Amendment 1, written before any compute) to the **genuine never-run
remainders** named inside those rows:

| front | consumed remainder | source of the gap |
|---|---|---|
| E-01w | 432-bit 2013 modulus over 54-byte **windows** of the payload | ledger E-01 `not_covered` (b), verbatim |
| E-02v | **varint** reads vs the doublet-gap sequence | round 16 ran uint8/u16LE/u16BE only |
| H-03r | 2012 P.S. digit-string **rotate-90/matrix** reading | round 16 ran only the cookie-XOR half |

Nothing already measured was re-run. `handoff/PARKED.md`'s bottom-table lines for
E-01/E-02/H-03 are now fully consumed.

## 1. Controls (all ran FIRST; one caught a bad bar)

| control | recovery | negative FP | gate |
|---|---|---|---|
| E-01w PKCS#1 v1.5-SHA1 plants (10, fresh 432-bit key, random offsets) | **1.00**, exact offset, no spurious | 0 strict / 200 random buffers (~487k matcher reads) | pass |
| E-01w PSS-SHA1 plants (5) | **1.00** | (same negative run) | pass |
| E-02v real-gaps re-encoded as varint (10, both flavours) | **1.00** (ρ=1, p<1e-4) | 0 / 50 random payloads | pass |
| H-03r printable-pair planted blocks (10) | **1.00** | first run **FAILED 37/200**, recalibrated, then **0/200** | pass after Amendment 2 |

**The H-03r negative-control failure is a finding about the instrument**: the 80 %
printable bar inherited from round 16's H-03 was calibrated for random *bytes*
(P≈0.44); digit *pairs* 00–99 land in ASCII 32–99, P(printable)=0.68, so 80 % sits
~2 σ off noise and fired 37 times on 200 random blocks. Bar recalibrated to ≥0.95
(analytic FP ≈1.6e-5/block) in a dated PREREG amendment **before any real reading was
examined**; plants still recover at 1.00. Round 16's own H-03 verdict is unaffected
(its 80 % bar gated bytes, where it is ~5 σ).

## 2. Results

### E-01w — windowed 2013-modulus RSA check: NULL
203 windows × 3 payload variants (canon / decpref / `payload_resolved`) × 2 byte
orders; per variant 831 pow-tuples evaluated (e ∈ {65537, 3, 17}), 387 excluded by
s ≥ n (recorded, not silently dropped), plus 1,218 direct-EM reads of the raw windows.
**Zero strict-tier matches anywhere.** One loose-tier row per variant — the identical
window at offset 62 (it avoids all 9 contested cells, so it is byte-identical across
variants) shows a pslen=0 PSS-SHA-256 frame under e=17: this is the ~1e-4 noise tier
round 19/C1 measured and excluded from the hit definition for exactly this reason.
Ledger E-01 `not_covered` (b) is hereby closed.

### E-02v — varint gap reads: NULL
12 decoded sequences (LEB128 + MSB-first base-128, forward/reversed, 3 variants), all
127 values (≥20 required) × 2 targets (85 inter-doublet gaps; 86-value with leading
first-doublet position 122, both re-derived from `seed_sweep/ct.bin`: 12,956 runes, 86
doublets). Max |Spearman ρ| = 0.119 (bar 0.5 + perm-p<1e-4). 24/24 null. The varint
word in E-02's hypothesis is no longer unexecuted.

### H-03r — 2012 P.S. rotate-90: NULL, and the community claim is RESOLVED
Source pinned to the primary artifact (`corpus/A-primary-artifacts/cijhho123/2012/…/
final message for 2012.txt`, 3 lines, 40+45+46=131 digits; 131 is prime so the 3-line
layout is the only rectangular matrix). 6 readings of the bare block + 4 of the
visually indented block (line 1 shifted 5 columns by the "P.S. " prefix — Amendment 3):

- **Bare block: "3301"/"1033" appear ZERO times in all 6 readings.** The community
  note in `armada_osint/artifacts/raw/2012.md` does not reproduce on the digits alone.
- **Indented block: "3301" appears once reading columns L→R bottom-up, "1033" once in
  the mirrored direction — the same digit run reversed.** This is precisely the
  claim's "3301 (or 1033 depending on rotate direction)". So the claim is real but is
  a **layout artifact of the 5-character "P.S. " indent**, and it is statistically
  unremarkable: expected motif count ≈0.013/reading, so one occurrence across 4
  readings has p ≈ 5 % — and the surrounding pair-ASCII is noise (≤0.785 printable vs
  the 0.95 bar), no ≥8-digit constant match, no derived string prime. It leads
  nowhere further; recorded as a resolved observation, not a channel.

## 3. Coverage × power

- **Coverage**: 100 % of the amended enumerable grid (2,493 pow-tuples + 3,654
  direct-EM reads + 24 correlation cells + 10 block readings), zero sampling.
- **Power**: measured 1.00 on all three fronts via 25 plants through the real code
  path; negative FP measured at 0 across 200+50+200 noise inputs at the final bars.
  Recognizer FP rates are analytic where possible (strict PKCS#1 ≲2⁻⁸⁰ frame,
  loose tier ~1e-4 and excluded from hits; R2 ≈1.6e-5/block).

## 4. The three conditionals of this negative

1. **Object space**: the 432-bit 2013 modulus only (the sole published modulus with an
   open windowed cell), contiguous 54-byte windows, e ∈ {65537, 3, 17}, 2 byte orders,
   3 payload variants; varint = LEB128/MSB-128 over forward/reversed bytes; H-03 = the
   10 enumerated column/concat readings of the 3-line artifact block ± the 5-col indent.
2. **Transition model**: none (no decoder) — purely structural recognizers: PKCS#1
   v1.5 type-1 strict (DigestInfo) / type-2, EMSA-PSS at standard salt lengths,
   Spearman rank vs the doublet-gap sequence, digit-pair ASCII, pinned constants.
3. **Register**: a payload meaningful in a shape *outside* these recognizers —
   non-PKCS signature formats, non-monotone gap transforms, non-ASCII digit semantics
   — is not covered by this null.

## 5. Not covered / reopens if

- Non-contiguous or bit-shifted windows; window sizes ≠ 54 under the 2013 modulus;
  e outside {65537, 3, 17}; unpublished moduli (untouchable — no artifact).
- Varint flavours beyond the 4 enumerated (e.g. zig-zag signed, base-64 chunked);
  gap definitions other than whole-book inter-doublet gaps.
- Matrix readings of the P.S. digits outside the artifact's own layout (arbitrary
  widths have no artifact warrant; 131 prime bars rectangles).
- **Reopens if**: a future blind read flips any payload byte (L2's round-28 verdict
  KEEPS canon, so the rider did not trigger; a re-run is seconds via this runner); a
  new published 3301 modulus surfaces; or a measured fact motivates a different gap
  sequence.

## 6. Artifacts

`PREREG.md` (+3 dated amendments), `l5_payload_micro.py`, `h03r_indented.py`,
`results.json`, `ledger_rows_proposed.json` (coordinator merges into `LEDGER.json`),
this file. No FLAGGED-FOR-ORACLE candidates were produced (0 hits), so no ORACLE-*.md
exists and `oracle_crosser.py`/`hitfn20` were not invoked — the gate was armed
(any hit exits FLAGGED-FOR-ORACLE, never auto-certified) but nothing reached it.
