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

---
## Section 4 addendum (2026-10-29): ICC embedding by release, and what R18-L1 actually measured

**Per-release table** (font-free page, `-sDEVICE=jpeg -dJPEGQ=92 -r400`; `gs_icc_by_release.json`). All six requested releases built.

| gs release | ICC embedded in the JPEG | ICC md5 | JPEG bytes |
|---|---|---|---|
| 9.04 | **no** (no APP2) | - | 332,761 |
| 9.05 | yes, 2576 B | e409cef13cd06f6b371f6cddc8e31fcf | 335,355 |
| 9.06 | yes | e409cef1... | 335,355 |
| 9.07 | yes | e409cef1... | 335,355 |
| 9.09 | yes | e409cef1... | 335,355 |
| 9.10 | yes | e409cef1... | 335,355 |
| 9.12 | yes | e409cef1... | 335,355 |
| 9.14 | yes | e409cef1... | 335,355 |

Decoded pixels are identical across all eight; 9.05-9.14 are byte-identical to each other on this page.

**Reconciliation with R18-L1 section 4.** R18-L1 measured *files in source trees*, not renders: `icc_version_probe.sh` fetches
`iccprofiles/srgb.icc` per ghostpdl tag from raw.githubusercontent.com and records length, md5 and the PCS-illuminant bytes
(`icc_versions.json`); the 9.00-9.17 tags returned "fetch failed" at that path, and `icc_oldpath_probe.sh` re-probed `gs/iccprofiles/srgb.icc`
(`icc_versions_early.json`: 9.00-9.02 = 3144 B, 9.04+ = 2576 B e409cef1). The sentence "Artifex introduced the 2576-byte profile at 9.04"
is therefore a statement about when the **file first ships in the tree**, and the "operative window 9.04-9.14" combines that with the
May-2014 date bound. R18-L1 never ran an old Ghostscript; its chain control used the modern system gs 10.06 and showed that the *render*
output carries an Artifex ICC. S1 now supplies the missing link: the 9.04 tree does ship the e409cef1 file (md5 re-verified here in
`gs/iccprofiles/`), yet the 9.04 `jpeg` device does **not** embed it; 9.05 is the first release that does. The two claims do not
conflict; they bound different things:
- file-in-tree window (R18-L1): 9.04 to 9.21, upper edge 9.14 by date;
- ICC-embedded-in-jpeg-device-output window (S1, this build recipe): 9.05 onward, so 9.05 to 9.14 under the same date bound.

Effect on O1: the render-level band for LP2's stage 1 narrows from 9.04-9.14 to 9.05-9.14 (still containing Ubuntu 12.04's 9.05).
It does **not** single out a release inside 9.05-9.14 (same bytes on this page). The 9.04 exclusion rests on one device, one parameter set,
a gcc-15 compatibility build, and an assumption that LP2's ICC came from gs rather than being added later by ImageMagick/another tool
(R18-L1's chain control showed IM only carries an existing ICC through). Per the doctrine: a measured constraint, not a pin and not a solve.

**Sandbox, second pass:** resumed the stopped sandbox from its snapshot; 1,274 s (21.2 min) wall, 2,225 s active CPU; stopped before the 25 min kill.
