# Round 28 — second red-team (refute-by-default) over L1/L2/L4/L5/R + chainer

_Audit run 2026-09-16T05:0x–05:1xZ (2026-09-15 ~22:0x local), read-only against S2's run
dir throughout. Trust anchor `tests/validate.py` re-run by this lane: **ALL VALIDATIONS
PASSED (5/5)**. S2 (grind27 PID 701083) alive and advancing the whole audit
(coverage 0.4189 → 0.4274, ~76k seeds/s under contention)._

## Verdict summary

Every lane headline **reproduces from raw artifacts**. Every planted control demonstrably
ran through the shared production code path. Anti-repeat citations spot-checked against
LEDGER.json are real, and L1's non-duplication claim was re-derived from R12-A1's own
result files. No candidate anywhere near a bar was dropped — including in the orphaned
premature grind28 partial run, which this audit checked explicitly. The 25 queued cells
all have vector+plant gates that the engine structurally re-validates with no override.
Defects found are process/records-class (D1–D6 below); none touches a scientific negative.

## Per-lane recomputation (item 1)

### L1 (R28-L1-CICADAOS-PADS-DENSE-PAIR) — CONFIRMED NEGATIVE
- `sweep_rows.jsonl`: 24,080 rows, 24,080 unique kids. Grid arithmetic exact:
  560.00auth pair 4,880 = 244 offsets x 5 red x 2 dir x 2 sign; exact 4,860 (o=0's 20
  cells excluded); 560.13 7,180/7,160 (359 offsets). The only o=0 rows are the 40 `pair`
  rows — exactly the pre-registered R12-A1 exclusion, no more, no less.
- Headline recomputed: max pmax 5.606 (`560.00auth:mod29:s+1:o3850240:pair`); rows with
  pmax >= 5.0 = **23**, and the 23 candidates in results.json are exactly that set (only
  3-decimal rounding differences). All 23 carry stage-B adjudication records with explicit
  FAIL reasons vs bars 7.634/7.384. 110 rows in [4.5, 5.0) sit below the pre-registered
  screen bar; nothing between screen and claim bar is missing.
- Control (control.json, mtime 11:38, BEFORE results.json 12:17): both plants built with
  the real authoritative pad at non-zero offset 49152 and pushed through the same
  `driftbeam`/`adjudicate`/`hitfn20` imports the sweep uses (verified in control.py and
  sweep.py source) — keyskip1 recovery 1.000 HIT=True, skip_by_two 0.9958 HIT=True, and
  the beam-on-pair cross-check fails at 0.071, proving the pair axis is separate power.
- Anti-repeat verified from raw R12-A1 artifacts: `results_560_00_full.json` offsets are
  {0,1e3,5e3,2e4,1e5,5e5,1e6,2e6,2412544,3e6,3.5e6} — **only o=0 is a multiple of
  16384**, so excluding only o=0 on the exact relation is exactly correct (same check
  passes for 560.13 stride 331,777).

### L2 — CONFIRMED NEGATIVE
- 7,168 rows = 128 variants x 56 targets, zero duplicate (variant,target) pairs — the
  resume ("kept_variants": 74) lost nothing.
- Recomputed: best score −6.3502 (b0m16/…/page54, beaufort off237, matching the reported
  top-20 exactly); 0 rows >= family bar −5.7923; 0 rows within 0.15 of it; per-row
  `above_family_bar`/`near_bar` flags all false and consistent.
- Plant control ran through the real battery (`plant_control()` calls the same enumeration
  and scoring, and hard-exits the sweep on failure): top-1 = planted b0m37 at the planted
  config, recovery 1.000, and a runner-up only 0.017 behind — a genuinely discriminating
  control, not a special-case branch.
- Reader half: blind gate 100/100, min correct margin 0.08334 (matches claim); conflict
  verdicts in reader_out.json are 3-pass unanimous with margins clearing the control
  minimum. PREREG Amendment 1 dated 2026-09-08 before the run.
- A-04 ledger citation real; its `reopens_if` text ("independent BLIND transcription…")
  is verbatim what L2's read-half answers.

### L4 (QUEUED) — CONFIRMED BUILD-VALID, item 2 satisfied
- `receipts/gates_receipts.json` recomputed for all **25/25** cells: plant_fullgate
  hit=True and recovery **1.0 on every cell**; min screen margin over the frozen N=2^32
  claim bars = 7.90; max false-reject pmax 4.054 vs min claim bar 9.638 (clean
  separation); **every gate .dat on disk matches its receipt SHA-256**; queued_cells.json
  lane/bar/reducer/relation/offset all cross-match the receipts, and all 25 gate files
  exist at the queued paths.
- grind28.c: gate is structurally REQUIRED for plan lanes ("A lane whose gate is missing
  or failing DOES NOT SWEEP — no env-var override exists"); source grep confirms no
  override hook. Separate binary; grind27 binary+source mtimes 2026-09-07 (untouched).
- genval.json: per-seed exact-match booleans vs on-box PHP 8.5.4 across all generator
  variants, seeds incl. 0/1/3301/2^31/2^32−1, 2000 draws.
- PREREG amendments section present and dated; QUEUE.md leads with the DO-NOT-FIRE hold.

### L5 — CONFIRMED NEGATIVE
- results.json internally consistent with every headline: E-01w = 831 pow-tuples + 387
  s>=n exclusions per variant, **0 strict hits**, the single known loose PSS row at
  offset 62 appearing identically in all 3 variants (the ~1e-4 noise tier, disclosed);
  E-02v = 24 rows all "null", max |rho| 0.1187 vs bar 0.5; controls all 1.0 with 0 FP.
- Amendments 1–3 dated 2026-09-08; Amendment 2 documents the H-03r negative-control
  failure and bar recalibration BEFORE real data — the control genuinely gated the run.
- E-01 anti-repeat citation verified verbatim in LEDGER.json (`not_covered` (b): the
  432-bit modulus over a 54-byte WINDOW — exactly what L5 then swept).

### R (first red-team) — CONFIRMED
- All six cited commits exist on master (584d0f0, d41f3e2, 3931c05, d66aab0, 35dc3dd,
  63af1bb). Oracle recheck receipts present and parity_ok=true, delta 0.0 on all three
  S1 crossers. t5_throughput.json substantiates the 125k-unloaded vs ~70k-loaded finding
  from STATUS.json deltas (the method this audit also used).

## Chainer + queue safety (item 2)

- Run-dir separation is real: queue launches with `--run-dir $R28/run` (does not exist
  yet, created at launch) — it can never touch `round27/P1-engine/run/`. Marker file is
  written FIRST; HIT-CANDIDATE handling is copy-and-flag, never certify; fallback plan
  (queued_cells.json) is the same 25 validated cells as the merged plan (set-verified).
- grind27 resume path has a `pgrep -x grind27` double-launch guard; the observed live
  resume (05:02:50–53Z) behaved exactly as coded: clean checkpoint continuity
  0.4171 → 0.4189, new PID 701083 written to sweep.pid, coverage rising since.
- `GRIND27_S2_CONTROL_OK=1` is grind27's own resume attestation for a lane whose planted
  control was already validated (commit 047feeb armed the S2 control) — legitimate use,
  not a control bypass.

## S2 disturbance (item 3)

S2 was never written to (its run dir holds only engine-authored files; grind27
binary/sources untouched since 09-07). Throughput: R-lane T5 already established the
44–48% interval drop during round-28 lane compute was dominated by **un-niced host dev
processes**, with niced lanes ~4%/thread; L1's own pcpu samples (580→572, 1.4%) agree.
Current post-resume rate ~76k seeds/s vs 125k unloaded — contention continues (see D3).
Crucially: **no S2 hit can have been lost** — the S2 lane already has its one claim-bar
crosser (seed 35563892, pmax 7.6707 >= 7.6342) duly recorded in
`P1-engine/run/HIT-CANDIDATE.json` as FLAGGED-FOR-ORACLE (see D6).

## Defects and open items

- **D1 (MEDIUM, process — REPORTED, not self-fixed): chainer has no singleton lock and
  `launch_queue` has no already-running guard.** `resume_s2` guards grind27 with pgrep,
  but nothing stops a second chainer instance (or a relaunch while a queue is live) from
  double-launching grind28 into the same `round28/run` dir. The rogue premature launch
  proves out-of-band launches happen on this host. Not self-fixed because editing
  `chain_after_s2.sh` while PID 701073 is executing it risks corrupting the running
  interpreter's read offset. Proposed patch (apply only after the current chainer exits,
  or to a copy + clean restart): at script top,
  `exec 9>"$R28/chainer.lock"; flock -n 9 || { echo "chainer already running"; exit 1; }`
  and in `launch_queue`:
  `pgrep -f 'grind28 --plan' >/dev/null && { log "REFUSED: grind28 already running"; return 1; }`.
- **D2 (LOW, records): the incident narrative is mis-dated.** The of-record story says a
  host reboot on **2026-09-11** killed grind27 494140, but chain.log shows PID 494140
  alive with S2 coverage advancing 0.4034 → 0.4171 until 2026-09-16T04:52:21Z; the actual
  outage window is 04:52–05:02Z on 2026-09-16 (21:52–22:02 local 09-15). Either the date
  is wrong or a second undocumented interruption occurred. No coverage was lost either
  way (checkpoint continuity verified). Also the note "checkpointed cleanly at
  ~250k/band" understates the rogue run's cursors (~4.5M seeds/band done) — immaterial,
  since that dir is orphaned and re-swept, but the incident record should be corrected.
- **D3 (LOW-MEDIUM, prescription conflict): R-T5's prescription "no new round-28 compute
  until S2 exits" is being violated by L3's sweep** (`sweep28.py` PID 689907, cwd
  round28/L3, running since 21:34 local). The chainer note calls it "unrelated and left
  running"; T5 named only L2-in-flight as exempt. Impact is small (niced single thread,
  ~4%/thread per T5's measurement), but the standing order and practice disagree —
  coordinator should either amend T5's prescription of record or stop/parking-lot L3
  until S2 exits.
- **D4 (MEDIUM, ledger hygiene): R-T1's corrected `not_covered` texts are still
  unapplied.** As of this audit LEDGER.json still shows `not_covered: null`/None on
  R12-A1, E-02, H-03 (spot-checked) — the 9-row defect T1 found stands uncorrected in
  the ledger of record; the patch texts sit in `R/T1-PATCH-PROPOSALS.md`. No science was
  harmed (L1/L5 re-derived true uncovered mass from raw artifacts), but future
  anti-repeat checks that trust these fields will be misled. Coordinator should apply
  and commit the T1 patches.
- **D5 (LOW — FIXED HERE): orphaned premature grind28 output could be mistaken for
  authoritative coverage.** `L4/run/` holds the SIGTERM'd rogue run's partial results and
  `L4/sweep28.pid` its two stale PIDs. This audit verified the orphan is clean — 2,508
  partial candidates, best pmax **6.765** vs claim bar **9.638**, nothing near a bar —
  and dropped `L4/run/ORPHANED-PREMATURE-RUN.txt` marking it non-authoritative (the
  sanctioned queue re-sweeps from seed 0 in `round28/run/`).
- **D6 (LOW, engine cosmetics + open adjudication): STATUS.json's `flagged_survivors` is
  hardcoded `[]`** in grind27.c (line 805) and inherited verbatim by grind28.c (line
  1095) — the field can never reflect real flags, and worker `best_pmax/best_word` carry
  across lanes, so S2's STATUS currently displays S1's crosser while looking like an
  unflagged S2 claim-bar crossing. The real record is `HIT-CANDIDATE.json`, which
  correctly lists seed 35563892 for lane S2 (pmax 7.6707 >= 7.6342). **Open item:** that
  S2 crosser still owes its stage-B/oracle adjudication at S2 closeout (its S1
  adjudication was NOISE-CROSSER with bit-exact parity, so the expectation is NOISE, but
  the S2-lane verdict must be recorded, not inherited). The chainer launches the grind28
  queue on S2 completion without waiting for that closeout — launch and adjudication are
  independent, so nothing is lost, but the coordinator's closeout checklist must include
  it.

## Three conditionals of this audit
1. Recomputation was from persisted artifacts (rows, receipts, logs, LEDGER, source) —
   not an independent re-execution of the sweeps themselves (except the trust anchor and
   the R12-A1 offset-grid derivation, which were re-run).
2. "Control through the real path" was verified by source inspection of shared imports
   and call graphs plus receipt values, not by instruction-level tracing.
3. S2 non-disturbance rests on STATUS/log deltas and file mtimes; sub-minute
   interference below those instruments' resolution is not excluded (R-T5's point).

**VERDICT: ERRORS-FOUND-NONE-SCIENTIFIC — 6 process/records defects (D1–D6), 1 fixed
in-audit (D5), 0 affecting any negative result, 0 dropped candidates, queue and chainer
safe to fire post-S2 once D1's lock is applied at the next chainer restart.**
