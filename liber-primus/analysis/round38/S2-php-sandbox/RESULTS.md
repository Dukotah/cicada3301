# R38 S2 RESULTS - PHP mt_rand tier (b) on the sandbox: NOT RUN TO A RETAINED RESULT (data lost; sandbox quota then exhausted)

Status: **never-run as a coverage claim.** No sweep rows, no control.json, no fpr12_php.json were retained. Everything below the "observed in sandbox logs" heading was read from command logs during the session and is NOT backed by a persisted artifact, so it carries no coverage and no ledger weight. Pre-registration: [`PREREG.md`](PREREG.md) (written before the first sandbox existed).

## What happened (plain)
1. Harness `sweep_s2.py` (pf_v4_12 + beam_v3 panel-R36, 12 registers, four PHP cells, null12 bars, append-mode store, resumable state) was written and smoke-tested on the laptop, then run on two non-persistent 2-vCPU Vercel sandboxes (project skyfling, 45-min hard cap; `extend_session_timeout` is refused, so the cap is 45 min total per session, not per window).
2. Session 1 ran smoke, FPR, control, W1 and the start of W3. Session 2 ran smoke, FPR, control and the start of W2. I then issued a batch of sleeping `run_session_command` calls; one hung for 2573 s with no response, and both sessions hit their 45-min cap and stopped while I was blocked. Both were non-persistent and no snapshot exists. Session 1 had a checkpoint uploader (egress 15.1 MB shows an upload happened) but its returned URL was only written inside the sandbox, so it is unrecoverable. Session 2 had no uploader; egress 69 KB.
3. Re-creation then failed: `402 payment_required, Hobby plan usage limit exceeded, reset 2026-11-01T00:00:00Z` (tried twice, persistent and non-persistent). The temporary input gist was removed (two by me, the third by the coordinator).

## Observed in sandbox logs (not persisted; informational only)
* Environment: Python 3.14.4, numpy 2.5.4 (pip --user), Ubuntu, 2 vCPU, 4 GB. Smoke test passed on the sandbox AND on the laptop (12 registers, panel sha ok, planted keyskip1 mt_scale seed 647892279, with-skip head, pf_v4_12 pass, 60 chunk survivors, pmax240 27.872, recovery240 1.0; php_mt selftest all true including gen28 match).
* FPR under the frozen 12-register point (2^17 uniform wrong-key heads per cell, default_rng(3399), union of both relations): pooled 450 / 524,288 = **8.58e-4** (Wilson 95 % 7.83e-4 .. 9.41e-4); mt_scale 115 (8.77e-4), mt_mod 108 (8.24e-4), php_scale 126 (9.61e-4), php_mod 101 (7.71e-4). Consistent with the 8.89e-4 held-out FPR of frozen_op12.json. `fpr12_php.json` was written on the sandbox and lost; this is a rerunnable 3-second computation.
* Natural-rate control (240 plants = 4 cells x 2 rel x 3 registers x 10; real chunk path 2^16 seeds): gate PASSED. Pooled recoveries / n: EN_MODERN skip-free 46/46, with-skip 33/34 (1 prefilter miss); EN_NOVOWEL skip-free 47/47, with-skip 31/33 (2 prefilter misses); HEBREW skip-free 44/44, with-skip 34/36 (2 prefilter misses). Every plant that passed the screen was recovered. Per-cell detail lost.
* Throughput: ~5.2-5.6 s per 2^17-seed block (all four cells, 2 workers on 2 vCPU), i.e. 119 blocks = 650.6 s. This is ~2.5x faster than the loaded laptop in R36 (14-19 s/block); a 45-min session can hold ~450 blocks, and one session fits control + W1 (blocks 199-317) + a long W3 (blocks 318+).
* Progress when last seen: W1 (default_rng(3301) blocks 199-317, 119 blocks) completed in 650.6 s; W3 (3301 blocks 318+) had 40 blocks at 225 s; session 2 W2 (default_rng(3302)) had 12 blocks at 71 s. Survivor counts and best scores were not read after the early blocks (early snapshots showed best pmax in the 5.3-6.3 range, far below the ~8.1 L120 bars), so **no statement about crossers or near-misses can be made.**

## Coverage / seeds added
**Zero seeds added** to any ledger: no rows were persisted. (Even had W1 been kept: blocks 199-317 of the 3301 stream are not new seeds relative to Round 32 B2, which already covered blocks 0-317 with a weaker screen; only blocks >= 318 of 3301 and the 3302 stream add seeds. R36 X1 already recorded that R36's tier (b) was not new seed coverage.)

## What this lane did establish
* The harness and its three gates work on the sandbox (smoke, FPR, control as above, from logs).
* The sandbox is far faster than assumed (5.4 s/block vs 14-19 s), and the 45-min cap is per session, not extendable.
* Lessons for the next attempt: never leave more than one blocking sandbox call in flight; write checkpoint URLs somewhere I can read frequently; use `persistent:true` so a stop snapshots the disk; the Hobby quota resets 2026-11-01T00:00Z (it was consumed by this lane and S1's 4-vCPU persistent sandbox).

## not_covered
Everything: tier (b) beyond R36's 0.607 % per cell is unchanged; 12-register PHP FPR is only log-observed; per-cell control detail, W1/W2/W3 survivors, bars at actual N, crossers, near-misses all unmeasured.

## Reopens
Rerun `run_commands.sh` after 2026-11-01T00:00Z (one 45-min session covers control + W1 + W3; a second parallel session covers W2). Inputs must be moved with `write_session_files` (no gist).

## Files
PREREG.md, sweep_s2.py (harness), up.sh / drv_a.sh / drv_b.sh (drivers + checkpoint uploader), run_commands.sh, RESULTS.md, ledger.json, ledger_patches.json. No rows file exists.
