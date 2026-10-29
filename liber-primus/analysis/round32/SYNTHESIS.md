# Round 32 — SYNTHESIS (INSTRUMENT & RED-TEAM armada)

_Run 2026-10-28 on the owner's laptop (~7 GB RAM, < 1 GB free, no C toolchain). Plan of record:
[`CAMPAIGN-PLAN.md`](CAMPAIGN-PLAN.md). Doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md).
Eight lanes, nine agents (Sonnet), ~4.5 h wall. Every lane ran a positive control before its null counted.
`LEDGER.json`: 181 rows, 0 errors, 0 unsound negatives; `tests/validate.py` passes; `pytest tests/ benchmark/`: 24 passed._

## 1. Verdict in one paragraph

No survivor, no crosser, no flagged-for-oracle candidate. That is the expected outcome of an instrument round and
it is not the result. The result is that four load-bearing defects named in the plan are now measured or fixed:
the beam's `skip_by_two` blind spot has a power envelope (I1), the English-only conditional on the historical
negatives has been re-scored where it could be and restated where it could not (I2), R3 is machine-enforced and
the null is segment-length-aware (I3), and the auto-certification seal's ceiling is re-measured and still below the
bar (I4). Two enumerable/stated-fraction generator lanes (B1, B2) fired through the repaired instrument and
returned bounded negatives with honest coverage. The red-team lane found errors in all seven standing claims it was
pointed at and corrected the navigation docs and ledger (X1).

## 2. Lane scoreboard

| lane | verdict | control | coverage × power | headline |
|---|---|---|---|---|
| I1 | VALID (kill rule did not fire) | planted skip_by_two recovered 1.00 @ L=120/400 | instrument only | decoder pre-existed in `round19/I1/driftbeam.py`; the lane is the measurement. Legacy relation 0.30 → `advance=2` 1.00; `free` covers all three at L≤400. **EN_NOVOWEL unrecovered (0.72)**. Bounded B-04 SHA256-CTR re-adjudication under advance=2: 0 flagged (6,604 decodes, <1 % of B-04). |
| I2 | gate PASS; negatives restated | 9/9 registers ≥0.917 @ L=120, 1.00 @ L=240 | survivor-level only | corpora restored (CY = modern Welsh prose substitute). B-04 / R16-KDF / R16-PRNG / R17-PUBLIC-PAD: best pmax_ne 5.36 / 3.97 / 2.61 / 7.55 vs escalate bars 6.37 / 6.05 / 6.25 / 8.08. Sweeps themselves still English-only (only English-ranked heads stored). |
| I3 | SHIPPED | failing-then-passing tests (4) | n/a | `validate_ledger.py` check 7 hard-fails non-R3 stores (round ≥19); `threshold_for(..., segment_len)` implemented; null exponent −0.546 ± 0.041 (6 cells incl. L=320; pooled with R19: −0.559 ± 0.028; R19 alone: −0.583). L=240/400 not measured here. |
| I4 | SEAL_PASS=false (unchanged) | L1 leak reproduced | ceiling 0.623 catch at both FR limits (pre-registered designs) | D3a/D3b learned gates = register detectors (reject 13/13 correct-key EN_NOVOWEL). Post-hoc D5c: 0.964 catch / 0.009 FR on one L=240 split — unreplicated, length-conditioned, NOT adopted. |
| B1 | NEGATIVE, bounded, prefilter-lossy | 25/26 end-to-end plants | 77.6M seeds × 2 ABIs screened (1.00); prefilter power 0.47–0.74; 192,066 decodes | bash 4.2 auto-seed, `%29`, keyskip1+2, I2 panel. Best 7.068 vs declared bar 7.38; near-miss seed 1354603465 fails the L=240 gate (re-screened by X1). "~28 min" in the plan was a 16-core estimate with a sieve that never existed. |
| B2 | NEGATIVE, bounded, 0.97 % tier-b | 48/48 prefilter-passing plants recovered, 8 cells | tier (a) 48,036 prior-dense seeds fully decoded; tier (b) 41.7M = 0.970 % of 2³² per twist; 212,218 decodes | PHP ≤7.0 `mt_rand`, canonical + legacy twist, scale29 + mod29, keyskip1+2. Best 6.856 vs bar 7.63. Legacy twist checked vs php 8.5.4 `MT_RAND_PHP`, not a PHP 5 binary. Remainder → `R28-L4` queue. |
| B3 | R28-L3 `inconclusive`; glibc gen=0 NEGATIVE, prior-dense | 6/6 | 48,036 seeds × 2 relations (1.1e-5 of 2³²) | L3's bulk store never reached this machine; controls/progress on disk are consistent (0 flagged, 2,500,207 decodes). |
| X1 | FOUND-ERROR ×7 | two re-screens | n/a | see §4. |

## 3. What the instrument now says that it did not say yesterday

1. **"Would the true key have survived our sweeps?"** — under `skip_by_two`, every pre-R19 sweep: no (legacy
   relation recovers 0.30). Under the round19 `driftbeam` relations: yes for EN/LA/OE/DE (0.93–1.00), **no for
   vowel-dropped English** (0.72 best; the beam still searches with the English quadgram). That is the single
   largest remaining instrument gap and it is construction × register, not key space.
2. **Every "NEGATIVE" before R19 now carries a written register conditional** ("English-ranked survivors;
   non-English re-scored at survivor level only"). The discarded decodes cannot be re-scored; the conditional is
   permanent for those rows.
3. **Future negatives mean what they say or CI fails.** A sweep-declaring row from R19 on must point at a store
   that passes `validate_store` with `ioc`/`mds`/`pmax_ne`/`zl` in its header.
4. **The −5.5 bar at L=31 was far too loose** (L-aware bar −4.08 at N=1e6); at L≥240 the floor binds to ~1e13
   trials. Round 18 L6 scripts already pass `segment_len`; their stored outputs predate the fix.
5. **Auto-certification is still not possible.** Every survivor stays flagged-for-oracle. The one promising rule
   (D5c) needs a third clean key and a threshold-vs-length curve over ≥4 lengths before it can be trusted.

## 4. Red-team findings (X1) — all FOUND-ERROR

| # | claim | correction |
|---|---|---|
| 1 | GS 9.01–9.15 | 9.04–9.14 (`icc_versions_early.json`: 9.00–9.02 non-matching, 9.03 unmeasured) |
| 2 | Py2.7-MT "coverage 1.00" | `pair`-only; `exact` (S2) at 44.14 %, R28-L4 zero. "exhausted" removed. |
| 3 | canon vs payload_resolved (idx 45/50/246) | both options written; **owner decision** |
| 4 | "transcription closed three ways" | LP2-typeface-only (T1 LP1 gate failed 95.09 %); p27:93 unresolved |
| 5 | `not_covered: null` ×9 | R12-A1 already filled; 8 drafted texts applied, tagged for confirmation |
| 6 | `STATUS.json` vs `HIT-CANDIDATE.json` | resume bug in `grind27.c`/`grind28.c` (hits reset, never restored); patched, **uncompiled**. Seed 35563892 = NOISE (stage-b 4.96/5.78 vs 7.38/7.63). |
| 7 | B-10 ↔ R29-L1 | B-10 named OutGuess 0.2, R29-L1 ran 0.4; R29-L1 `not_covered` was null |

Lane audit: minor errors only (I1 PREREG post-dates outputs; I2 0.917 rounded to 0.92; I3 test path; I4 Wilson
upper on the NOVOWEL class). B1 numerics reproduce. B2 was filed by the coordinator after X1 closed; its
`ledger_patches.json` needed the same status/positive_control normalisation as B1/B3 and has not had an
independent audit — Round 33's X-lane should start there.

## 5. Open for the owner

1. `C-CANON-PAYLOAD-3BYTES` — Option A (promote `payload_resolved.bin`, re-check B-04/R17/E-01/E-02) or B (restate
   `not_covered`). X1 leans A. Nothing in Round 32 depends on it.
2. Build and test the patched C engines before resuming S2.
3. Confirm the 8 drafted `not_covered` texts; fill R30-A1/A2/B1/B2/C1 (still null, validator does not flag it).
4. Whether to re-price the R28-L4 PHP cells at the measured ~71 h / 2³² laptop rate.

## 6. Round 33 — the completeness critic's ranked seed list

1. **A register-aware beam.** The panel sees EN_NOVOWEL/LA/OE/DE; the search does not (I1: 0.72). This is the
   instrument gap with the largest measured mass and it is bounded (one decoder, planted-control gated).
2. **Feed `payload_resolved.bin` to B-04, R17, E-01, E-02** — cheap, closes a standing caveat (needs #1 above decided).
3. **Human read of p27:93 + an LP1 transcription audit** — LP1_REAL anchors every panel.
4. **Skip models beyond {1, 2, free}** — per-page / per-line key resets, advances ≥3.
5. **The off-repo rendering channel** — build GS 9.04–9.14, byte-compare renders against the 58 LP2 JPEGs.

Not opened this round, by design: any new unbounded key space. Nothing in §6 is one either.
