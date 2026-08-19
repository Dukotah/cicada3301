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
