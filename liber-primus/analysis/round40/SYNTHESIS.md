# Round 40 — SYNTHESIS (THE MASS THE CEILING PAGE NAMES)

_Run 2026-10-31 on the owner's laptop (sandbox quota locked until 2026-11-01 00:00 UTC). Plan of record:
[`CAMPAIGN-PLAN.md`](CAMPAIGN-PLAN.md). Doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Five lanes
closed (B1, C1, I1, B3, X1); B2 (key offsets) still sweeping and S1/S2 (sandbox) not yet run — all three file into
Round 41 when they land. `LEDGER.json` 290 rows, 0 errors, 0 unsound negatives; `tests/validate.py` passes; `pytest`
41 passed; capsule PASS; `check_ceiling.py` PASS; no document drift._

## 1. Verdict in one paragraph

No survivor. Two of the three "not excluded" lines the position page named as enumerable are now measured rows: the
other bash versions (3.2 and 5.1 swept in full with their own generators; 4.0/4.1 shown to emit the 4.2 stream on
every reachable seed) and the English-era SHA/KDF/public-pad/CicadaOS grids re-decoded under the skip-aware,
register-aware instrument (B1, B3). The matrix's English-only and legacy-beam cells are re-scored under twelve
registers (C1), and the exclusion lines that rested on English-only plants now carry four more registers at measured
power (I1). One KDF row was flagged by its own pre-registered rule, read by the coordinator and independently by X1,
and is a noise-crosser; one direct read (R13) was a near-miss under the lane's null and dies under a
structure-matched one. The round's instrument finding is X1's: the twelve-register null (`null12`) was fitted on a
survivor population less English-like than the sweeps actually produce, so its actual-N bars are lenient — the
N=1e6 bar is the only flag gate until it is refit on the sweep population (Round 41 I1).

## 2. Lane scoreboard

| lane | verdict | control | coverage × power | headline |
|---|---|---|---|---|
| B1 | 3.2 partially-run (generator source-derived), 5.1 NEGATIVE (non-PIE), 4.0/4.1 NEGATIVE by identity | 59–60/60 per version | 3.2: 76.2 M (1.000); 5.1: 92.3 M non-PIE (≈4.3 % of the PIE orbit); 4.x: 4.2's 296/296 by identity (8 chunks replicated byte-for-byte) | best 7.098 (3.2) / 6.522 (5.1) vs ≈8.1 actual-N; 0 flagged. |
| C1 | 35 cells → TRIED, 4 → PARTIAL, 7 blocked | 6/6 per family | 28,236 rows | 0 flagged; R13 DIRECTION near-miss (p≈0.005 under the lane null) → NEGATIVE under page/region-matched nulls (X1); R14/R15 code found in the branch archive → re-score in Round 41. |
| I1 | 16/18 rows recover 1.00 ×4 registers | 2,050 plants | — | five ceiling lines widened; L2-MAP weaker than its one-plant control (EN 8/10, NOVOWEL 1–2/10) → its own partial line. |
| B3 | NEGATIVE ×4 grids | 80/80, 78/80, 78/80 | B-04 2,165 seeds; R16-KDF 534; R17 28 P3 pads (P1/P2 not regenerable); CicadaOS 4 ISO pads; pad offsets sampled 0.48–0.78 % | KDF rev row flagged by rule (6.528 vs 6.342 actual-N; 8.868 screened; decays to 5.531 at L=174; no words) → NOISE-CROSSER. |
| B2 | in flight | — | — | files into Round 41. |
| S1/S2 | not run (quota) | — | — | Round 41 first wave. |
| X1 | FOUND-ERROR ×12 (one instrument-level) | re-runs | — | §4. |

## 3. What the instrument now says that it did not say yesterday

1. **The bash family is measured to its edges.** 3.2, 4.0, 4.1, 4.2, 5.1 (non-PIE) — all negative or identity-covered
   at reach ≥0.95 in twelve registers; what remains is the 5.1 PIE orbit (~2³¹), 3.2 beyond pid 32768, and a real
   3.2 binary to retire "source-derived".
2. **The English-era grids no longer carry a keyskip1-only, English-only conditional.** They are negative under
   keyskip1+2 with ≤2 head skips, twelve registers, plants in three.
3. **`null12` is lenient at scale.** Its survivor population (median 2.33) is less English-like than real sweep
   survivors (median ≈2.8); the empirical 99 % bar at N≈130k is ≈9.6 against 8.3 stored. No stored verdict flips
   (every best row is ≥1 below even the lenient bar), but the bar of record must be refit on the sweep population
   before any actual-N claim is made again.
4. **A structure-matched null kills the last near-miss.** R13's backward self-indexing walk is the top of 923
   collapsed trajectories, ≈3 sd, the expected maximum.

## 4. Red-team findings (X1)

Instrument: `null12` population mismatch (above). B1: ceiling patch under-stated 3.2's caveats (fixed); replication
chunks were the first 8 of the shuffled order, not random (wording). B3: "screened-N primary" unsupported (withdrawn);
PREREG/RESULTS dense-space figure mismatch; patch strings matched no row. C1: R14/R15 code exists in
`archive/branches-2026/`; four patch ids nonexistent; H4xF6 → PARTIAL; N convention differs from B1/B3. I1: "power
1.00" is a point estimate; cite form; `positive_control` prose. NO-ERROR with re-runs: all generators (`RANDOM=1` ×20
per version), 2 replication chunks, 24 KDF bars, the KDF cell re-decoded (NOISE concurring), 2 C1 cells, 15 I1 plants,
L2-MAP's weakness. Coordinator adopted: R13 → negative; N=1e6 bar the only flag gate pending the refit.

## 5. Recorded, not blocking

- **Deadline:** S2 window 2 snapshot `snap_ff0SWU76EW32OqbWJvp00fnORypR` (~2026-11-07); quota resets 2026-11-01 00:00 UTC.
- B2 merges only after an audit of its offset alignment (Round 41 X1).
- The KDF bundle (`B3-english-era-grids/ORACLE-KDF-iter_md5_1000-rev/`) stays for the owner to overrule.

## 6. Round 41 — THE BAR OF RECORD (plan: [`../round41/CAMPAIGN-PLAN.md`](../round41/CAMPAIGN-PLAN.md))

I1 refit `null12` on the sweep survivor population (and page/region-scale matched nulls for direct families); S1 S2
window-2 recovery + persistent windows; S2 PHP retry; S3 a real bash 3.2 binary on the sandbox to verify the only
source-derived generator; C1 R14/R15 from the archived code + the blocked cells; B2 (offsets) filed and audited; X1.
No new key space. A survivor would be extraordinary; the round succeeds without one.
