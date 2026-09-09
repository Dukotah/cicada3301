# Round 28 · Lane R — red-team audit · RESULTS

_2026-09-08. PREREG: [`PREREG.md`](PREREG.md). Mode run-now-light, all compute
`nice -n 15` single-threaded; S2 never touched (read-only copies out of
`round27/P1-engine/run/`, never a write). Trust anchor `tests/validate.py` = ALL
VALIDATIONS PASSED (5/5) at lane start. Reports per doctrine R6: **FOUND-ERROR /
NO-ERROR-FOUND** only — never "confirmed"._

## Verdict summary

| target | verdict | one line |
|---|---|---|
| T1 ledger hygiene R12-A1 / PARKED P-3 | **FOUND-ERROR** (hygiene, not substance) | `not_covered: null` on R12-A1 despite real uncovered mass; P-3 staleness real but already corrected by L1, correction verified exact |
| T2 S1-CLOSEOUT recomputation | **NO-ERROR-FOUND** | every headline number recomputes exactly from artifacts (histogram sum, tails, blemish, 3 oracles bit-exact, 120-seed parity delta 0.0) |
| T3 L3 i386-subsumption claim | **NO-ERROR-FOUND** (one prose note) | claim verified empirically: 106/106 keystream identity incl. 55 negative-hash strings; 66/66 parity vs real CPython 2.7.18; abs()-hypothesis excluded 30/30 |
| T4 PREREG-vs-code drift L1–L5 | **NO-ERROR-FOUND** (two minor notes) | L1 grid/bars/ordering verified cell-exact; L2/L3/L4 consistent; L5 minor control-acceptance drift, moot |
| T5 S2 non-interference | **FOUND-ERROR** | S2 interval throughput dropped ~43% below its unloaded average during concurrent multi-lane execution — the round's >10% guard was breached (details, attribution and prescription in §T5) |

---

## T1 — R12-A1 ledger hygiene + PARKED P-3 staleness: FOUND-ERROR (doctrine R7)

**Recomputed from artifacts:** `round12/A1/results_560_13.json` = 160 configs, exactly
8 offsets {0,1e3,5e3,2e4,1e5,1e6,1e7,5e7} on the 118,818,811-byte pad (offset fraction
6.7e-8), keyskip1 beam only, fixed −5.5 bar, NEGATIVE, dated 2026-08-19;
`results_560_00_full.json` = 220 configs, 11 offsets to 3.5e6, NEGATIVE. Yet the ledger
row carries `"not_covered": null`. That is the R7 defect the planner suspected:
uncovered mass (offset density, the pair relation, the N-scaled gate) with no
`not_covered` statement. **Proposed replacement text: `T1-PATCH-PROPOSALS.md` §1**
(coordinator applies).

**P-3 staleness:** the "The A1 re-run was NOT performed" line was genuinely stale
(the runs exist on disk, dated 2026-08-19) — but R28-L1 had already applied a dated
CORRECTION OF RECORD before this lane ran. This lane verified every figure in the
applied correction against the artifacts: exact. Closed as OVERTAKEN-AND-VERIFIED
(`T1-PATCH-PROPOSALS.md` §2).

**Systemic note:** `B-05` also has `not_covered: null` with status negative — the
defect is a class, not a one-off (`T1-PATCH-PROPOSALS.md` §3; row census below in §T1-c).

**T1-c census:** 9 of 157 rows with status negative/eliminated carry an empty
`not_covered`: `B-05, B-16, R12-A1, R12-C1, R12-D2, A-03, E-02, F-01, H-03`.
Recommend a one-time hygiene pass (each fix is a paragraph, derivable from the
row's own coverage/notes text, as done for R12-A1 in `T1-PATCH-PROPOSALS.md`).

## T2 — S1-CLOSEOUT independent recomputation: NO-ERROR-FOUND

Positive control first (PREREG Q1): one histogram bin of a scratch COPY corrupted
(+7 in worker-2 bin 600) → checker FAILED it on 2 clauses (`t2_hist_check.py`,
control exit 1). Then, on the pristine copy:

1. **Histogram total** = 4,294,967,296 = 2³² exactly (6×2600 u64 bins) — PASS.
2. **Tail ≥ 5.00** = 392,131 — PASS; Gumbel ratio 392,131 / 298,500 = **1.3137×**,
   inside K2 [0.2×, 5×] and equal to the closeout's 1.31× — PASS.
3. **Tail ≥ 7.39** = 3, occupied bins exactly {7.42–7.43, 7.60–7.61, 7.67–7.68} =
   the three adjudicated crossers — PASS.
4. **The one-lost-flag blemish recomputes exactly:** `candidates.jsonl` holds 392,130
   unique S1 seeds; per-bin diff vs histogram = one single bin, [5.31, 5.32),
   4,570 vs 4,569 — precisely as recorded in S1-CLOSEOUT §4.
5. **All three ORACLE records re-run through the recorded driver**
   (`oracle_crosser.py`): stage-A pmax |Δ| = 0.0 vs both the C value and the record;
   stage-B L=240 clause-1 pmax |Δ| = 0.0 (4.963841996903331 / 4.533995152761554 /
   5.784086568753328); hit=False, verdict NOISE-CROSSER, bar 7.383520294328688 —
   all three match their `ORACLE-*.md` bit-for-bit (`work/oracle_recheck_*.json`).
6. **Independent K4 spot parity** (my own RNG seed 28, disjoint sampling design from
   the closeout's seed-27 batch): 120 seeds (60 from the hard-gate zone ≥5.8835,
   60 below) re-scored through `pyref runner.stage_a` — **max |C − Python| = 0.0**
   (`work/t2_spot_parity.json`).

## T3 — L3's i386-subsumption claim, tested empirically: NO-ERROR-FOUND

`t3_subsumption_test.py` → `work/t3_results.json`.

- **Control first:** comparator proven able to distinguish streams — the true word
  matches, a planted wrong word (w+1) does not.
- **Part A (the claim itself):** 106 strings (100 from L3's real `dictionary.jsonl`
  + forced negatives + edges "", "a", " ", "\x00"; **55 of them with negative 32-bit
  py2-hash**): for every one, `keystream(s, wordsize=32)` ≡ the integer-word
  keystream of w = hash32 & 0xFFFFFFFF over 2,000 draws, and every w ∈ [0, 2³²) —
  the space S1 swept to measured exhaustion. 0 failures.
- **Part B (ground truth, the real interpreter):** 66 strings (30 with negative
  64-bit hash) against the live amd64 CPython **2.7.18** binary
  (`/home/dukotah/py27/root2718/usr/bin/python2.7`): hash parity 66/66, 2,000-draw
  stream parity 66/66. **The abs()-hypothesis is empirically excluded:** for all
  30 negative-hash strings, seeding with `abs(hash)` yields a stream ≠ the real
  interpreter's — CPython 2.7 uses the **unsigned cast** `(unsigned long)hash`
  (and gen_py27 implements exactly that, incl. the −1→−2 hash edge).
- **Prose note (not an error in the claim):** L3's PREREG sentence "the (absolute
  value of the) hash is fed to init_by_array" mis-describes the string path — abs
  applies only to int/long seeds. The CODE (gen_py27 `h & mask`) is correct, so
  the sweep tests the right image; recommend the coordinator fix the sentence.
- **Conditional:** the real-binary cross-check is amd64-only (no i386 interpreter on
  the box); the i386 half rests on gen_py27's wordsize-32 parameterization of the
  same code path (validated against captured 2.7.3 vectors, `round19/G3/validation.json`).

## T4 — PREREG-vs-code drift, L1–L5: NO-ERROR-FOUND (two minor notes)

Positive control first: two rows planted in a COPY of L1's sweep rows (a duplicate
cell + an off-grid offset) → checker FAILED all four P2 clauses (`t4_l1_check.py
work/l1_rows_PLANTED.jsonl`). One clause of my own first checker draft was naive
(substring-matched hardcoded bars; L1 derives them) — the fix is recorded in the
checker; the defect was in MY audit tool, not L1.

- **L1 (complete):** planned grid reconstructed independently from the PREREG
  (244+359 offsets × 40 − 40 anti-repeat cells = 24,080): rows on disk = **exactly
  the planned set** (0 dup, 0 off-grid, 0 missing); candidates ≥5.0 = 23 with all 23
  stage-B adjudicated and none over even the true-N bar 6.379; best pmax 5.606
  matches RESULTS; control.json predates sweep rows; bars derived from
  `panelmax_bar` and verified equal to the frozen R27 constants
  (7.3835202943286884 / 7.6341931878728095); fixed −5.5 absent. **NO-ERROR-FOUND.**
- **L2 (read half complete, decode half in-flight):** Amendment 1's A-04/B-05 quotes
  verified against the actual LEDGER fields (they match, including `reopens_if`
  wording); artifact ordering PREREG 11:40 → reader gate 11:51 → plant control
  12:02 → null calibration 12:10 → sweep (running); family-wise Gumbel bar computed
  in code, historical −5.2 carried as report-only. Both in-lane control failures
  (78/100 gate bug, offset-42 plant) disclosed with cause. **NO-ERROR-FOUND** on
  everything auditable pre-completion.
- **L3 (mid-run):** controls.json (5/5 cell gates, 11:45) precedes first sweep row
  (11:47); grid/cell order matches PREREG A1; bars in code = frozen R27 constants;
  progress shows 31 seeds `skipped_excluded` in r29_pair_t0 = the R26-C exclusion
  A3 promised. Its A6 instrument finding (hitfn20 clause-3 false-negative channel
  ~0.1–0.2 on true keys in some cells) is acknowledged by this lane and is
  consistent with L4's independent ~1/8 measurement; both lanes adopted the correct
  mitigation (pmax-crossers FLAGGED-FOR-ORACLE regardless of clauses 2/3).
  Operational note: at audit time L3's runner process was not running while
  `progress28.json` said in-progress (grbrej_pair_t0 at 177 done) — coordinator
  should confirm it resumes/records rather than silently stalling. **NO-ERROR-FOUND.**
- **L4 (build+queue):** 25 queued cells, all lane names distinct, every per-cell
  gate file present, engine executable; schema = R27 `sweep_plan.json` superset
  (adds `engine`, `gate`); claim bars recomputed independently =
  `panelmax_bar(rel, 2³², 0.01)` exactly (9.638182362052774 / 10.031081507059358),
  i.e. per-cell N with the 25-cell family disclosed — the conservative direction
  (a lower bar surfaces MORE candidates to the oracle; a real key cannot be lost
  to it). Zero coverage claimed anywhere. **NO-ERROR-FOUND.**
- **L5 (run finished at audit time, RESULTS pending):** code bars match the amended
  PREREG exactly (R2 0.95 dual-alignment per Amendment 2, ρ>0.5 ∧ p<1e-4, seed
  3301, ≥8-digit R3 constants); the two control failures that forced Amendments
  2–3 were caught and re-registered BEFORE real-data reads — the control system
  working as designed. **Minor note:** code accepts the PSS plant control at 4/5
  (0.80) vs the doctrine-standard 0.90; moot because the measured result was 1.0,
  but the acceptance constant should read 0.90. **NO-ERROR-FOUND** (note stands).

## T5 — S2 non-interference: FOUND-ERROR (the round's own guard was breached)

Metric: interval Δseeds_done/Δt from S2's own `run/STATUS.json` (read-only), against
the unloaded lifetime average 125,159 seeds/s (S2 ran essentially alone 05:27–11:38).
Numbers in `work/t5_throughput.json`:

| window | seeds/s | drop vs unloaded |
|---|---|---|
| 12:18–12:32 (L2+L5+R-lane compute) | 70,316 | **43.8%** |
| 12:40–12:45 clean (R-lane idle, only L2 + host activity) | 65,335 | **47.8%** |

The round's guard is 10%. **Breached by >4×.** Three findings inside the finding:

1. **The guard metric the lanes used cannot see the breach.** L1 guarded with
   `ps` pcpu (580→572, "1.4%, inside guard") — pcpu is a CUMULATIVE average since
   process start and structurally dilutes any recent drop. Interval STATUS.json
   deltas must be the guard metric from now on.
2. **Attribution is mixed, and the biggest bite is not the niced lanes.** grind27
   runs at **nice 10**, round-28 lanes at nice 15 — CFS weight 110:36 per thread
   predicts only ~4% steal per lane thread, and the clean window (one L2 thread)
   still shows 47.8% down. Observed concurrently: UN-niced host dev activity
   (node/esbuild/claude sessions, weight 1024 vs grind's 110) bursting 45–90% CPU,
   load average 10.4–16.0 on 6 cores, grind27 instantaneous CPU as low as 92%.
   An un-niced process out-prioritizes the nice-10 sweep ~9:1.
3. **Material impact:** ~2.79e9 S2 seeds remained at last sample — ~6.2 h at the
   unloaded rate vs ~12 h at the observed rate.

**Prescription (per this lane's pre-registered consequence "lanes pause"):** no NEW
round-28 lane compute (including L3's remaining cells and L4's queue) starts until
S2 exits; L2's in-flight sweep should be allowed to finish (killing mid-run risks a
corrupt partial null) — coordinator decision. Owner-level: if S2 dominance is wanted
against host noise, `renice 0` (or lower) PID 494140, or quiesce the un-niced dev
sessions; the round cannot enforce that from inside.

## Three conditionals of every NO-ERROR-FOUND above (PREREG Q4)

1. Only the five named targets were audited — nothing else is endorsed.
2. Recomputation used the committed artifacts and drivers, not re-runs of the sweeps.
3. T2's parity is a 120-of-392,130 sample (+ the closeout's own 10,971); T3 is a
   106+66-string sample of an unbounded string space; T4 audited the artifacts that
   existed at audit time (L2 decode half, L3 remaining cells, L5 RESULTS post-date it).

## Coverage × power

Coverage: 5/5 pre-registered targets executed (T4 partially bounded by lanes still
in flight, stated above). Power: every checker was validated on a planted defect
before its clean pass (corrupt bin → caught; planted duplicate/off-grid rows →
caught; wrong-word keystream → caught); the T5 guard fired on a real breach, which
is itself the positive demonstration that the monitoring has power.

## Artifacts

`t2_hist_check.py`, `t3_subsumption_test.py`, `t4_l1_check.py`,
`T1-PATCH-PROPOSALS.md`, `work/` (histogram copies incl. the corrupt-control,
oracle re-run JSONs, `t2_spot_parity.json`, `t3_results.json`, planted-rows copy,
T5 samples).
