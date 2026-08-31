# H-3 (relaunch) progress — the HANDOFF capsule — COMPLETE 2026-08-19

Trust anchor: `python3 tests/validate.py` = ALL VALIDATIONS PASSED (run at start and at end).

## Delivered
- [x] `handoff/README.md` — index / entry point
- [x] `handoff/FOR-FUTURE-SOLVERS.md` — single entry doc (problem, corrected OTP-*class* verdict,
      proven vs unrefuted, method, what-not-to-do, what's open, 30-min quickstart, reopen triggers)
- [x] `handoff/PARKED.md` — P-1..P-11 + "not parked, merely unfinished" table.
      NOTE: another agent wrote its own PARKED.md over mine mid-run; I MERGED rather than reverted,
      keeping their unique content (R9 template-DP instrument, benchmark/null.py, B-05 avalanche
      control) and fixing two factual errors in it — see "Corrections made" below.
- [x] `handoff/capsule/MANIFEST.json` — 103 items, 103 hashed locally, 0 LOST
- [x] `handoff/capsule/build_manifest.py` — regenerates the manifest; hashes measured, not typed
- [x] `handoff/capsule/verify_capsule.py` — offline/--net/--net --fetch; DRIFT detection; tested
- [x] `handoff/capsule/iso_extract.py` — stdlib ISO9660 extractor (box had no 7z/bsdtar/pycdlib)
- [x] `handoff/capsule/RECOVERY-560.13.md` — recovery record + the _560.00 defect
- [x] `handoff/capsule/recovered/*.sha256` — committed hash receipts
- [x] `.gitignore` blocks for capsule fetches and the large recovered pads

## Headline results
- **DATA/560.13 RECOVERED** (was the one LOST item). sha256
  db79072ce580efa54acf5f31f3ef0eb00aef867871a051d04e27ee5e7fbc112f, 118,818,811 B — both matching
  the Git-LFS pointer in round12/A1/lfs_req.json. Route: archive.org item `3301.iso` is only
  136,398,848 B (not multi-GB as assumed) and archive.org serves per-member streaming +
  Range-resumable whole-ISO. The A1 RE-RUN WAS NOT PERFORMED (parked item P-3).
- **_560.00 IS TRUNCATED.** The copy Round 12 A1 swept is 2,412,544 B; the authoritative ISO copy
  is 3,992,970 B (~40% missing), different sha256. A1 used it for its positive control AND null
  ceiling, so that pad's negative covers only ~60% of the real blob. Authoritative copy placed
  alongside; truncated file deliberately left unmodified so A1 stays reproducible.
- **56/56 page-image SHA-1s re-verified** against the archived onion7 dump, extended to SHA-256.
- **nullcurve.py re-run**: E[null max] completed 10-gen sweep = -12.5707 -> old -12.5 bar FAILS.
  Corrected FWER thresholds 0.05/-12.2670, 0.01/-12.0602, 0.001/-11.7674; planted-true -11.2360.

## Corrections made to the other agent's PARKED.md while merging
1. P-6 (CT-log brute) said "non-viable on volume grounds ... unparks if bulk access gets cheap".
   That is wrong: CT logs hold CA-issued cert domains, not page contents or v2 onions, so there is
   no candidate to hash AT ANY SCALE. Rewrote as closed-by-construction, never unparkable.
2. P-2 procedure pointed at `analysis/seed_sweep/run_full32.sh`. L5-seed32/RESUME.md explicitly
   says DO NOT use it (logs one line per generator; a mid-generator kill loses hours, which is how
   gen=0 went missing). Repointed to L5-seed32/run32.sh, which checkpoints per chunk.

## Not done (out of scope / deliberately)
- Did not re-run round12/A1 (heavy compute; two sweeps were already running; it is P-3's job).
- Did not touch round13/**, round14/**, benchmark/**, or the nav docs.

---

## Handoff-doc refresh — 2026-08-31 (Rounds 20→25 folded in)

The three handoff docs were stale (dated Aug 19; stopped ~Round 19). Brought current through
Round 25 without deleting the older reasoning — superseded passages are marked in place with the
round that closed them, per repo doctrine. Trust anchor re-run: `python3 tests/validate.py` →
**ALL VALIDATIONS PASSED (5/5)** before and after. LEDGER.json `entries` now **142**.
No git commit (WSL no creds; owner pushes from Windows).

**What the six new rounds established (all confirming, none reopening the standing verdict):**
- **R20** (build the sieve): sieve **INFEASIBLE** — cannot reach ≥0.90 survival/register at ≥100×
  reduction (best 0.667); the Phase-S PRNG sweep never released on the sieve. Panel-max claim bar
  calibrated. Red-team flagged a latent **sieve × panel-max FP-inflation hazard** (~2.5×10⁶): do
  not re-enable the sieve without re-fitting the null on screened keys. Sweep-follow-up ran S-G3
  (0.057% of the Py2.7 space) + S-RESCOPE through a shipped recovery-gated hit function → 0 hits.
- **R21** (seal the gate): **L1 = KILL** — the no-oracle disjoint-fold seal is provably leaky
  (~0.82 catch, below the 0.90 bar) → survivors are now **FLAGGED-FOR-ORACLE, never auto-certified**.
  L2 measured the `n_skips` crossover at **L\*=6000**. L3 swept 3 more Py2.7 reducers + amd64 map
  (884k words, controls 4/4) = clean null. L5 red-team confirmed L1-KILL, 3× NO-ERROR-FOUND.
- **R22** (read the hinted channels): for the FIRST time every signed-hint channel was read —
  self-embedded acrostic (A), turtle/spatial render (B), literal imperatives (C), drop-cap (D) —
  **all clean, control-validated NEGATIVE; red-team NO-ERROR-FOUND**. Largely closes the standing
  "we never looked at the hinted channels" objection.
- **R23** (this session): **A2** = printed-line-geometry acrostic (the sharpest R22 reopener, using
  the TRUE page-image line breaks R22-A lacked) = clean NULL, Phase-0 recovery 1.000.
- **R24** (this session), all clean: **C1** matched-runic re-adjudication of the B-04 slice (20,480
  decodes) = null; **C2** DISCHARGED L7-B via the `skip_by_two` (`pair`/keyskip2) decoder (pair 100%
  vs beam 25.8% recovery), 245,975 keys → 0 hits; **C1-ext** language-aware Latin/Greek/OE/Enochian
  = null (Old Norse + romanized Hebrew marked UNAVAILABLE, not faked); **C2-ext** skip_by_two across
  bash/perl/tex/sha256_ctr + offsets + free_drift (113,432 keys, 8/8 controls) = null (PARTIAL
  coverage, flagged); **C8** date-indexed public pad = UNAVAILABLE BY PREMISE (unsolved pages 0–54
  carry no PGP signature to join a dated pad by), steelman probe null.
- **R25** (this session, PARKED live): compute-tail brute force of the Py2.7-MT 2³² seed space.
  6-core `analysis/round25/compute-tail/parallel_grind.py`, per-worker checkpoints
  `progress_w{0..5}.json`. PARKED mid-grind at **~0.49% coverage (~20.9M of 4.29B seeds incl.
  baseline), 0 hits, best pmax 6.826 vs pair bar 7.384.** Fully resumable; the in-band planted-seed
  control passes so the null is a true negative. See PARKED.md (new P-12).

**Note for the next agent:** the *navigation* docs (`README.md`, `PICKUP-HERE.md`,
`ELIMINATION-LEDGER.md`, `analysis/README.md`) are **also stale** past ~R19 and were intentionally
NOT touched here — they are a separate task. Everything this session is UNCOMMITTED on disk
(`?? analysis/round23,24,25`, edited `handoff/*`).
