# EXECUTION NOTE — R8-S1 (integrity flag on the auto-VERDICT field)

The raw measurement in `results.json` is correct and complete. However, the script's derived
`VERDICT` field reads `POSITIVE-DATABLE`, which **contradicts the pre-registered decision token** and
must be overridden to **NULL** by that rule. Recorded here transparently rather than by editing the
raw output (no goalpost move).

**Pre-registered decision token (verbatim):** "a 'datable narrowing' REQUIRES a version/date token
**beyond the static 2011 copyright**. Anything else is NULL."

**What the raw data actually shows:**
- ICC profile is byte-identical across all 56 pages (1 unique SHA-256), len 2576, valid (`acsp` magic OK).
- `creation_datetime` = all zero (no timestamp).
- No `manufacturer`, `model`, `creator`, or profile-ID; no Ghostscript build-version tag.
- Only text tags: `desc` = "Artifex Software sRGB ICC Profile"; `cprt` = "Copyright Artifex Software 2011".
- Tag set = the standard 10-tag minimal sRGB profile.

The only "version-like" string the script flagged is the **static 2011 sRGB-profile copyright** — exactly
the token the pre-registration excludes. The script's `has_tooling_version_token` regex failed to apply
that exclusion (implementation defect in the summary label only; the raw fields are correct).

**Correct verdict under the pre-registered rule: NULL / NEGATIVE for new datable info.**

**What S1 legitimately establishes (secondary, still useful):** the embedded profile is the *stock
Artifex sRGB ICC profile* that Ghostscript ships by default. This **structurally confirms** the renderer
as Ghostscript/Artifex (previously asserted via a printable-strings scan, per STEGO-VERDICT.md) — it
UPGRADES that provenance claim from strings-based to structured-parse-based, but adds **no new dating,
no build version, no operator fingerprint**. `platform = APPL` is hardcoded in this stock profile and is
NOT evidence of a Mac operator. Gate #2 to adjudicate NEGATIVE vs INCONCLUSIVE.
