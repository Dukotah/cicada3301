# S1 build box - PREREG (written 2026-10-29, before any sandbox call)

Lane S1, Round 34. Compute only in a Linux sandbox; local files only here. No git, no resume of the real S2.

## Item 1 - C engine (grind27.c / grind28.c)
- Recognizer: `gcc -O2 -Wall -Wextra` builds both with exit 0; resume tests on COPIES of the parked S2 state:
  (a) seed 35563892 present once after resume (HIT-CANDIDATE restored, not duplicated);
  (b) a planted synthetic hit survives resume and appears in top-level `flagged_survivors`;
  (c) a bounded `--seconds` window advances cursors.
- Kill: compile error -> report verbatim, stop item 1.
- KNOWN RISK recorded in advance: `engine.dat`/`panel_lm.f32` are gitignored and regenerate from
  `round19/I2/models/panel.npz` (sha256 recorded in engine.dat: 14a23d3619fa02df...), which is NOT on disk;
  only round32 panels (different sha) exist. If the launch self-test (V1/V2) fails on a substitute panel, tests
  needing a running sweep are reported as BLOCKED-ON-INPUT, not as pass/fail of the resume code.
## Item 2 - PHP 5 reference
- Recognizer: PHP <=7.0 `mt_srand(1); mt_rand()` equals php_mt.py legacy ("php" twist) first draw; expected 1244335972
  (unverified). 20 draws + `mt_rand(0,28)` 20 draws compared. FOUND-ERROR / NO-ERROR-FOUND.
- Fallback (weaker, labelled): PHP >=7.1 with `MT_RAND_PHP`.
## Item 3 - O1 kill test
- Page 0 source is not in the repo (only synthetic controls: round29/L4-image-forensics/ctrl.ps, round18 chain_control.py).
  Item reduces to: render the repo's own test PS through gs 9.04 vs 9.14 at R18-L1 parameters
  (`-sDEVICE=jpeg -dJPEGQ=92 -r400`, then IM `-quality 92`) and byte-compare (and decoded planes).
- Identical -> O1 KILL "band not resolvable at render level" (for that input only; a synthetic PS is weaker than page 0).
  Different -> O1 live. Budget: stop at ~40 min of builds and record progress.

---
## ADDENDUM A (2026-10-29, written before the second sandbox pass; coordinator decision)
- Recognizer: for each gs release built from its ghostpdl tag (9.05, 9.06, 9.07, 9.09, 9.10, 9.12; 9.04 and 9.14 already measured:
  no ICC / ICC), render the font-free synthetic page (`nofont.ps`) with `-sDEVICE=jpeg -dJPEGQ=92 -r400` and record whether the JPEG
  carries an APP2 ICC_PROFILE of 2576 B with md5 e409cef13cd06f6b371f6cddc8e31fcf; also record file size and decoded-pixel md5.
- Kill: stop at ~25 min sandbox wall; a release that fails to build in a few minutes is skipped and reported.
- Reconcile first: re-read round18/L1-toolchain/RESULTS.md section 4 + icc_version_probe.sh to state what R18-L1 measured
  (profile FILE in source tree vs ICC actually embedded in a render).
