# S1 build box - RESULTS (Round 34, 2026-10-29)

Sandbox obtained: **yes** (Vercel Sandbox via MCP, 2 vCPU / 4 GB, Ubuntu 26.04, gcc 15.2). Wall 20.9 min, active CPU 15.9 min,
no cost figure exposed. Stopped; see `sandbox.log` for the leftover persistent snapshot.

## Item 1 - C engine: COMPILES CLEAN; RESUME-PATH FIX VERIFIED; REAL SELF-TEST BLOCKED ON A MISSING INPUT
- `gcc -O2 -Wall -Wextra`: grind27.c and grind28.c both rc=0, 0 errors, 2 warnings each (all `-Wformat-truncation` on the
  `hist_*.u64` / `top_*.json` snprintf into char[2048]; benign). Source hashes matched the working tree / GitHub master.
- **Blocker found (finding):** `engine.dat`/`panel_lm.f32` cannot be regenerated exactly. `export_data.py` needs
  `analysis/round19/I2/models/panel.npz` (engine.dat records panel sha `14a23d3619fa02df...`); it is not on disk and not on GitHub
  (gitignored, not re-derivable by a committed script as far as S1 could see). With the round32 panel (sha 36a01dcb...) as substitute,
  `--self-test` fails: V1 26/64 seeds exact (worst |dpmax| 1.165), V2 pmax 17.9333 vs 17.9312. Decoder fields (ptr/skips/nchars)
  matched on every V1 line, so only LM values differ. **The launch self-test (K3) therefore cannot pass on any fresh box, and
  no S2 resume is possible, until that panel is restored.** That is a Round 35 prerequisite, independent of the resume code.
- Resume tests, on COPIES of the parked S2 state, using a harness copy `grind27_nost.c` (the single `if (self_test(NULL))` abort
  neutralised) with `GRIND27_S2_CONTROL_OK=1`; the real run dir was never touched. pmax values come from the substitute panel.

| test | result |
|---|---|
| (a) resume from parked STATUS+HIT-CANDIDATE: seed 35563892 present once, restored | **PASS** (hit file `[35563892 @7.6707232992600876]`, `flagged_survivors=[35563892]`, n=1) |
| (a2) cursor rewound to 35563800 so 35563892 is re-scanned: not duplicated | **PASS** (hit file pmax planted 1.0 stays 1.0, n=1; with hit file deleted the seed IS re-found, n=1) |
| (b) synthetic hit 123456789 @7.7 planted: restored + in `flagged_survivors` | **PASS** (`[35563892, 123456789]`, n=2) |
| (c) 4-6 s bounded window | **PASS** (all six cursors advance ~16k seeds/worker; timebox exit "interrupted (checkpointed)") |

- Note: the parked `STATUS.json` has no top-level `flagged_survivors` (written by the pre-fix binary); the fixed binary writes it.
- grind28 was compiled only; its gate files (`make_gates.py`) need the same missing panel. Source shows the same fix (L1181, L1297).
- **Proposed one-line change for `PICKUP-HERE.md` (coordinator's call, NOT made here):**
  "grind27/28 resume path verified on a Linux box (R34-S1): restore-hits, dedupe and `flagged_survivors` PASS; S2 resume still gated on restoring `round19/I2/models/panel.npz` (sha 14a23d36...) so the K3 self-test passes."

## Item 2 - PHP 5 reference: **NO-ERROR-FOUND**
Built real PHP **5.6.40** from source (cli only; had to patch `php_config.h` for gcc-15 mis-detection of readdir_r/crypt).
`mt_srand(1); mt_rand()` = **1244335972** (matches the unverified expectation). The first 20 `mt_rand()` and the first 20
`mt_rand(0,28)` equal `php_mt.py` legacy twist ("php") and scale reduction `(n*29)>>31` exactly (20/20 and 20/20);
canonical-twist and `%29` do not match. Cross-check: PHP 8.5.4 `mt_srand(1, MT_RAND_PHP)` gives the same 40 numbers.
Seed 1 only; a wrap-around (>624 draws) and other seeds were not exercised (R32-B2 already ran 8-seed receipts against 8.5.4).
Values in `php5_reference.json`.

## Item 3 - O1 kill test: **O1 LIVE (not killed)**, with caveats
Built Ghostscript 9.04 and 9.14 from ghostpdl tags; PS/PDF page-0 source is not in the repo, so the repo's own `ctrl.ps`
(and a font-free `nofont.ps`) were rendered at `-sDEVICE=jpeg -dJPEGQ=92 -r400` + ImageMagick `-quality 92`.
- Not identical: ctrl.ps stage-1 JPEG md5 `00da2e15...` (9.04) vs `6429595f...` (9.14); stage-2 differ; decoded pixels differ (AE 3029
  JPEG, 87 in a lossless PNG: glyph rasterisation).
- Font-free page: decoded pixels **identical** (AE 0), but JPEG files differ by exactly one segment: **9.14 embeds the 2576-byte
  Artifex ICC profile (md5 `e409cef13cd06f6b371f6cddc8e31fcf`, the LP2 profile) in an APP2 marker; 9.04 embeds no ICC at all.** DQT, SOF, DHT
  and the entropy-coded scan are byte-identical.
- Controls: same-version rerun byte-identical; Q91 vs Q92 differ; the comparator separates 9.04 from 9.14.
- Reading (a measurement, not a solve): the LP2 files carry that ICC profile, so a bare 9.04 `jpeg` device (this build) could not have
  produced them; the embed starts somewhere in 9.05-9.14 (untested). That is a render-level discriminator inside R18-L1's 9.04-9.14 band.
- Caveats: synthetic page; gcc-15 builds not period toolchain; Helvetica source between the trees unchecked; only two versions built.
  Natural follow-up: build 9.05/9.06/9.07/9.09/9.10/9.12 (each ~2 min at -j2 once the recipe in BUILD.md is scripted) and find the embed boundary.

## Decisions for the coordinator
1. Find/regenerate `round19/I2/models/panel.npz` (sha for engine.dat: 14a23d36...) before any S2 resume is scheduled.
2. Whether to spend a second sandbox run on the 9.05-9.12 bisect (cheap) - O1 is live and this would narrow the pin.
3. Delete the leftover sandbox `moccasin-certain-whippet-5ZiipV` / snapshot `snap_84wyROyjgjBX7veiBuxb8bqgyJYU` if unwanted.
4. A temporary secret GitHub gist carried the 543 KB round32 panel to the sandbox; it was deleted (`gh gist list` shows none).
