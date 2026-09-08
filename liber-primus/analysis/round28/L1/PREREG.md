# L1 — cicadaos-pads: dense-offset + pair-relation sweep of the authoritative author pads

_Round 28, pre-registered 2026-09-08, before any decode. Mode: run-now-light (one core,
`nice -n 15`, single-threaded)._

## Hypothesis

The LP2 0–54 keystream is a literal byte→symbol reduction of one of Cicada's own authored
CicadaOS binaries — specifically `DATA/560.13` (118,818,811 B, sha256 `db79072c…`, receipt
`handoff/capsule/recovered/DATA_560.13.sha256`) or the authoritative `_560.00`
(3,992,970 B, sha256 `a24051a8…`) — at a byte offset the prior sweeps never sampled, and/or
readable only under the `skip_by_two`/keyskip2 relation the prior sweeps could not represent.

## Anti-repeat (ledger ids extended, with the staleness correction)

- **`R12-A1`** (status negative, `not_covered: null`): covers all 6 author pads ×
  {mod29, prime_to_idx, hi_nibble, lo_nibble, byte_scaled} × fwd/rev × both signs ×
  **sampled offsets only** — and, via the 2026-08-19 addendum runs
  (`../../round12/A1/results_560_13.json`: offsets {0,1e3,5e3,2e4,1e5,1e6,1e7,5e7}, 160
  configs; `results_560_00_full.json`: 11 offsets to 3.5e6, 220 configs), the authoritative
  pads too. **Correction of record:** `handoff/PARKED.md` P-3's line "The A1 re-run was NOT
  performed" is stale — it was performed the same day the pads were recovered. What R12-A1
  demonstrably does NOT cover (from its own artifacts): (a) offsets other than the 8–11
  sampled positions — 8 positions on a 118.8 MB pad is a 6.7e-8 offset fraction; (b) the
  keyskip2/`pair` relation — all prior decodes used the keyskip1-class beam
  (`sk.beam_decode`, max_skip=3), which R18-L7-B measured at 25.8% recovery on `skip_by_two`;
  (c) the hitfn20 3-clause gate + N-scaled bar — prior runs used the fixed −5.5 bar
  (doctrine mechanic 4 declares fixed bars invalid at changed N).
- **`R17-PUBLIC-PAD`** family: establishes the public/author-pad branch is real and
  worth finite closure. Not a sweep of these bytes.
- L1 does **not** re-run any (pad, variant, sign, dir, offset, relation) tuple already in
  `results_560_13.json` / `results_560_00_full.json` / `sweep_results.json`; the offset grid
  below excludes those exact positions for the beam relation (they ARE re-run under `pair`,
  which is a new axis, not a repeat).

## Aiming Test

**Q1 — What would a hit look like, and would this instrument recognise it?**
A keystream slice `reduce(pad[o:])` that decodes the 12,956-rune unsolved stream (screened on
the first 400 runes) into panel-recognisable plaintext. Recognizer written before the search:
per-relation screen score with a pre-registered bar, then the hitfn20 3-clause gate
(pmax ≥ bar, recovery ≥ 0.90, held-out ¾ ≥ 0.90). **Planted control (before any null
counts):** encipher a PARABLE-register plaintext with the real authoritative `_560.00` bytes
under (i) the one-draw key-skip filter and (ii) the `skip_by_two` filter, at a non-zero
offset; the pipeline must recover ≥0.90 with HIT=True under keyskip1-beam for (i) and under
the R24-C2 `pair` decoder for (ii). A1's historic control (−4.211 / 100% at offset 5000)
is re-confirmed, not assumed.

**Q2 — Measured fact raising the prior above flat?**
The pads are the author's own binaries from the held CicadaOS ISO, sha-receipted
(`handoff/capsule/RECOVERY-560.13.md`); R12-A1's own RESULTS.md called 560.13 "the one
remaining A1 lever"; and R17 measured the public-pad branch as real. This is a finite
human-made artifact of the target, doctrine R5 class 1–2, not lore.

**Q3 — Is the space bounded, and by what?**
Enumerable and explicitly sized to one throttled core (~6–10 h at the measured ~0.36 s/decode
un-niced, budgeted 0.5–0.7 s/decode niced ⇒ ~45–55k decodes):
- `_560.00.iso-authoritative` (3,992,970 B): offset stride **16,384** → 244 offsets.
- `DATA_560.13` (118,818,811 B): offset stride **331,777** → 359 offsets.
- Per offset: 2 pads' variants × 5 reductions × {fwd, rev} × {sign −1, +1} ×
  {keyskip1-beam, keyskip2-pair} = 40 decodes/offset/relation.
- Total ≈ (244+359) × 80 ≈ **48,240 decodes** on the 400-rune head.
Everything finer goes to `not_covered` with the stride stated. If throughput undershoots,
the grid is coarsened by a factor of 2 and the coverage statement restated — never silently.

**Q4 — The three conditionals of the negative** (named again in RESULTS):
1. key space: these 2 pads × 5 reductions × 2 dirs × 2 signs × the stated offset strides;
2. transition model: keyskip1 beam (max_skip 3) + keyskip2 `pair` only — no other
   rejection-loop constructions;
3. register: the I2 9-register panel / English-quadgram adjudication (L7-A conditional).

**Q5 — Kill condition at 10% of budget?**
(a) Either planted control fails (<0.90 recovery or HIT=False) → lane halts, instrument bug
filed, no null published. (b) At the 10% checkpoint (~4,800 decodes), if throughput is <50%
of plan, coarsen per Q3; if S2's process is observed degraded by this lane (its
`--status` throughput drop >10%), pause immediately.

## Bars and null

- Fixed −5.5 is NOT used. Per relation, family-wise bar from the existing calibrated
  machinery: `pair` claim bar 7.3835 and `exact`-class 7.6342 at the N=1e6 ceiling
  (conservative for N≈4.8e4; `../../round27/PREREG.md` constants), plus a lane-local
  shuffled-ciphertext null (n=200, seed 3301) whose max is reported alongside.
- Doctrine R3: every screened row persists decrypt IoC·N, min distinct symbols/32-window,
  best non-English LM score, compressibility (SWEEPROW/3 shape).
- Any bar-crosser: full-stream re-decode, hitfn20, then **FLAGGED-FOR-ORACLE**
  (oracle_crosser pattern) — never auto-certified.

## Addendum 2026-09-08 (before any sweep decode; after timing probe only)

1. **Arithmetic correction to Q3's total.** Q3's "≈48,240 = (244+359)×80" double-counts the
   relation factor already inside its own per-offset enumeration. The enumerated grid is
   5 reductions × {fwd,rev} × 2 signs × 2 relations = **40 decodes/offset**, so
   (244+359)×40 = **24,120**; minus the 40 keyskip1 cells at offset 0 (both pads) excluded
   by this PREREG's own anti-repeat clause → **24,080 sweep decodes**. Strides, axes and
   coverage statement are unchanged; this is fewer decodes than budgeted, not more ground.
2. **Decoder settings frozen** (unstated above): `exact` relation = driftbeam
   `PRESETS["exact"]` (keyskip1, max_skip 3) at beam_w 120 = A1's published settings
   (G-EQ-gated equal to `sk.beam_decode`); `pair` relation = `PRESETS["pair"]` (keyskip2,
   max_skip 8) at beam_w 120. Screen head L=400 as stated; screen statistic = I2
   `adjudicate` pmax; candidate/promotion bar 5.0 (round27 `sweep_plan.json` cand_bar),
   claim bars as in "Bars and null".
3. **Timing probe** (nice 15, 1 thread, S2 running): 0.475 s/decode exact, 0.115 s/decode
   pair, adjudication included → projected ~2.0 h total. No coarsening invoked.

## Coverage promise (honest)

Delivered: the stride grid above at measured power (control margins reported), both
relations. Not covered and stated so: offsets off-grid (>99.99% of byte positions at
single-byte resolution), reductions outside the 5, PRF/seed/salt uses of the pads (that is
B-05's axis), per-page restarts beyond A1's originals, other relations/registers.
