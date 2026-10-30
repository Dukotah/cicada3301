# PRE-REGISTRATION — R8-S1: ICC-profile interior parse (generation-tooling fingerprint)

**Registered:** Round 8, before any code was run against the ICC interior.
**Hypothesis (security-researcher lane):** The APP2/ICC blob embedded in every LP page JPEG carries
generation-tooling metadata (Ghostscript/Artifex build string and/or an ICC creation timestamp) that
prior work never structurally parsed (`stego_scan.py` only did `has_icc = "icc_profile" in im.info`).
Reading it could narrow/date the production window or the operator's toolchain.

## Prior state (novelty basis)
`analysis/stego/provenance.json` stores SHA1s only; `stego_scan.py` records `has_icc` (boolean) and an
empty `text_segments`. The "Artifex Software 2011" phrase in STEGO-VERDICT.md was NOT produced by a
structured tag parse. Confirmed by Critic Gate #1.

## Procedure (fixed)
1. Extract the raw ICC profile bytes from the APP2 `ICC_PROFILE` segment of `data/relikd/p0.jpg`
   (concatenating multi-chunk if present).
2. Verify the ICC blob is byte-identical across ALL 56 pages (SHA-256 of the extracted ICC per page).
   If identical, one parse characterizes the whole corpus.
3. Parse the 128-byte ICC header: profile size, CMM type, version, device class, colour space, PCS,
   **creation date/time** (offset 24, six uint16 BE), platform, profile creator, profile ID.
4. Parse the tag table (uint32 count at offset 128, then 12-byte entries) and dump every tag signature.
5. Extract the text of `desc`, `cprt`, and any `dmnd`/`dmdd`/`mluc` text tags.

## Falsifiable predictions & decision rule (fixed BEFORE parse)
- **POSITIVE-DATABLE:** the profile contains an explicit tooling **version** token (e.g. a Ghostscript
  release number) OR an ICC **creation timestamp** that is non-zero and specific — either of which
  constrains the production window beyond the already-known "≈2014 render". → report as a new datable
  fingerprint; cross-check consistency with the known onion7 publication (2014).
- **NULL:** the profile is generic IEC 61966-2.1 sRGB boilerplate whose only date is the static profile
  copyright year (2011, the sRGB-profile epoch, NOT a build date) and whose creation-date field is zero.
  → NEGATIVE: no new datable tooling fingerprint beyond what STEGO-VERDICT already asserted.
- **DECISION TOKEN:** a "datable narrowing" REQUIRES a version/date token beyond the static 2011 copyright.
  Anything else is NULL. (This token is fixed now; it does not move after seeing data.)

## Control / anchor
`gs` is not installed locally, so the positive control (parse a known-Ghostscript render and confirm the
parser reads its version string) cannot be run here — **stated as a limitation**. Substitute control:
validate the parser against the ICC spec (header magic `acsp` at offset 36 must be present; tag offsets
must be in-bounds) so a mis-parse is caught. A camera-JPEG negative control is run if any is available;
else the null interpretation is bounded by "we can read tags that exist; absence ⇒ none present".

## Determinism
Pure byte parsing; no RNG. Output → `results.json` in this dir.
