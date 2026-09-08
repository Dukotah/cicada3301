# R28-L1 RESULTS — cicadaos-pads: dense-offset + pair-relation sweep of the authoritative author pads

_Round 28, lane L1, 2026-09-08. Mode run-now-light: one core, `nice -n 15`, single-threaded,
S2 (round27 grind27, PID 494140) untouched throughout (pcpu 580 start → 572 end, a 1.4% drift, inside the 10% guard).
PREREG: `PREREG.md` (with the pre-run dated addendum). Trust anchor `tests/validate.py`
= ALL VALIDATIONS PASSED (5/5) before and after the lane._

## Verdict: **NEGATIVE** (zero claim-bar crossers, zero FLAGGED-FOR-ORACLE)

## 1. What was swept (coverage)

Two sha256-receipted author pads from the held CicadaOS ISO, as LITERAL byte→symbol
keystreams over the LP2 unsolved head (400 runes), dense offset grids:

| pad | bytes | stride | offsets | prior R12-A1 offsets | density gain |
|---|---|---|---|---|---|
| `_560.00.iso-authoritative` (`a24051a8…`) | 3,992,970 | 16,384 | 244 | 11 | ×22 |
| `DATA_560.13` (`db79072c…`) | 118,818,811 | 331,777 | 359 | 8 | ×45 |

Per offset: 5 reductions {mod29, prime_to_idx, hi_nibble, lo_nibble, byte_scaled} ×
{fwd, rev} × sign {−1, +1} × relation {**exact** = keyskip1 beam (A1's published decoder,
beam_w 120, max_skip 3), **pair** = keyskip2 (`skip_by_two`-exact, the relation R18-L7-B
proved the beam CANNOT represent)}. Anti-repeat: the 40 keyskip1 cells at offset 0 were
skipped (R12-A1's own artifacts cover them exactly); pair at o=0 ran (new axis).

**Rows persisted: 24,080 of 24,080 planned (100%)** (`sweep_rows.jsonl`, SWEEPROW/1 per doctrine R3:
en, pmax, preg, pmax_ne, pcon, ioc·N, min-distinct-32, H2, zlib, 9-register z — every decode
re-interpretable later). Elapsed 35.9 min at 0.089 s/decode (plan budgeted 0.5-0.7 s).

## 2. Instrument power (planted controls, run BEFORE any null decode)

`control.py` → `control.json`. Both plants use the REAL authoritative `_560.00` bytes
(mod29) at non-zero on-grid offset 49,152, supp 0.83, PARABLE-register English, L=240,
through the lane's ACTUAL screen path and the ACTUAL hitfn20 3-clause gate:

| plant | decoder | screen pmax (bar 5.0) | recovery | held-out | HIT |
|---|---|---|---|---|---|
| one-draw keyskip | exact/keyskip1 | 32.286 | **1.000** | 1.000 | **True** (bar 7.634) |
| skip_by_two | pair/keyskip2 | 32.538 | **0.996** | 0.994 | **True** (bar 7.384) |

Cross-check: the keyskip1 beam handed the skip_by_two plant recovers **0.071** and fails
clause 1 — i.e. the pair axis of this lane is real power the prior A1 sweeps did not have,
not a re-labelling. A1's historic control (−4.211/100% at offset 5000) is thereby
re-confirmed in stronger form (deeper offset, authoritative bytes, 3-clause gate).
Both plants clear ≥0.90 with margin ≫ the bar → **measured power ≈ 1.0 for this lane's
construction × register class** (conditionals in §5).

## 3. Bars and null

- Candidate/promotion bar 5.0 (pre-registered; = round27 cand_bar). Nothing above it was
  dropped: every crosser auto-escalated to stage B (hitfn20 + full-stream re-decode).
- Claim bars, conservative N=1e6 constants: pair 7.3835 / exact 7.6342. At the lane's true
  N (24,080 adjudicated decodes) the bars are pair 6.379 / exact 6.567 — survivors were
  checked against BOTH; the fixed −5.5 bar was never used (doctrine mechanic 4).
- Lane-local shuffled-ciphertext null (n=200/relation, seed 3301, real mod29 keystream):
  exact mean 2.414 / max 4.193; pair mean 2.307 / max 5.290.

## 4. What came back

- Best screen pmax over the whole grid: **5.606** (`560.00auth:mod29:s+1:o3850240:pair`, firing register LP1_REAL) — below even the true-N pair bar 6.379, and 1.78 below the pre-registered claim bar 7.384.
- Screen candidates ≥ 5.0: **23** (15 exact, 8 pair; range 5.00–5.61), all null-level
  (expected Gumbel tail at N≈2.4e4 given the pair null max itself is 5.29). Every one was
  stage-B adjudicated: **0 of 23 cleared any claim bar (1e6 or true-N: L=240 pmax range
  1.61–4.95, full-stream pmax ≤ 3.32 — every candidate COLLAPSES as the window grows, the
  canonical noise signature); 0 passed the 3-clause gate.** Zero FLAGGED-FOR-ORACLE.
- Stage-B details for each candidate are in `results.json["candidates"]` (pmax at L=240,
  recovery, held-out, full-stream score/pmax).

## 5. The three conditionals of this negative (doctrine Q4)

1. **Key space:** these 2 pads × 5 per-byte reductions × {fwd, rev} × 2 signs × the stated
   strides (16,384 / 331,777) at the stated offsets only — a 6.1e-5 / 3.0e-6 fraction of
   single-byte offset resolution per pad.
2. **Transition model:** keyskip1 beam (max_skip 3) and keyskip2 `pair` (max_skip 8) only.
   Other rejection-loop constructions (e.g. skip-by-k>2, PRF-driven skips, per-page
   restarts beyond A1's originals) are NOT represented.
3. **Register:** the I2 9-register panel (EN modern/KJV, LP1_REAL, Latin, OE, DE, CY,
   half-vowel, no-vowel English) + legacy quadgram — the L7-A conditional stands for any
   register outside the panel.

## 6. Not covered (honest remainder — what reopens this)

- Offsets off-grid: >99.99% of byte positions at single-byte resolution (a hit at offset
  o is detectable from nearby grid points ONLY if the construction re-synchronises, which
  literal pads do not — so this null says nothing about off-grid offsets).
- Reductions outside the 5 per-byte maps (bit-level packings, multi-byte words, XOR-fold).
- PRF/seed/salt uses of the pads (B-05's axis, not this lane's).
- Per-page keystream restarts beyond A1's originals; other relations; other registers.
- The 4 smaller author pads at dense offsets (their R12-A1 grids were offset-sampled too,
  but they are ≤12 KB–2.4 MB; `560.17`/`tmp_*`/`prime_echo` dense grids remain unswept
  under `pair`).

## 7. Records

- `PREREG.md` (+ dated addendum), `control.py`/`control.json`, `sweep.py`,
  `sweep_rows.jsonl` (24,080 rows, SWEEPROW/1), `results.json`, `sweep.log`.
- Correction of record absorbed into `handoff/PARKED.md` P-3 (the "A1 re-run was NOT
  performed" line was stale; the 2026-08-19 runs + this lane are now cited).

## 8. Ledger row (ready to absorb)

id `R28-L1-CICADAOS-PADS-DENSE-PAIR`; status negative; coverage = §1 grid at power ≈1.0
(§2, conditionals §5); not_covered = §6 verbatim.
