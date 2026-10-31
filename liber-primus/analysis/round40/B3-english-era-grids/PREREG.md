# R40-B3 PRE-REGISTRATION: the English-era seed / key grids re-decoded with the skip-aware, register-aware instrument

_Written 2026-10-31 (Round 40, lane B3), BEFORE any control or grid output of this lane. Thresholds below are not edited after
results; later changes go in `PREREG-ADDENDUM-n.md`, dated, with the reason._

## 0. What is re-decoded, and why

The B-04 (SHA/HMAC/RC4/AES/ChaCha seed dictionary), R16-KDF (PBKDF2/scrypt/iterated/EVP), R17 public-pad and R12-A1/R28-L1 CicadaOS-pad
grids were decoded with the legacy one-rejection beam (`skipdecode.beam_decode`, English `score_norm`). Round 18 L7-A/L7-B and Round 39 X1
item 5 measured that instrument: English-register power 1.00; Latin 0.33-0.50; vowel-dropped English 0.00; it recovers 0.258 of a
`skip_by_two` plant (0.071 for the `exact` beam on the R28 pad plant). So these grids' negatives carry **three conditionals** (doctrine Q4):
key space, **keyskip1-only** transition model, **English-only** register. This lane re-DECODES the same regenerated key lists (not survivors)
under: beam_v3 `panel_max` on panel-R36 (12 registers), relations `keyskip1` + `keyskip2`, head screen pf_v4_12 (frozen point,
`round37/I2-pfv4-12reg/frozen_op12.json`, m=24, k=2, rel=both), bars from `round36/B1-orbit-12reg/null12.json` (POT fit) at the actual N and at
N=1e6, L=120 screen and L=240 gate. `free` (<=2 skips) is not run (R34-I1: unlicensed at L=120).

Instrument is imported UNCHANGED from `round37/I2-pfv4-12reg/sweep.py` (`v3dec`, `bar_v3`, `AD`, panel-R36, `to_row(..., with_degenerate=True)`,
14-field SWEEPROW rows; `AD.validate_store` and `validate_ledger.check_r3_store` at the end). Keystream heads are swapped per grid.

## 1. Aiming Test (Q1-Q5)

- **Q1 recognizer.** A hit = a regenerated key config whose head (L=120) panel `pmax` clears the null12 bar for its relation at the actual N AND whose L=240
  decode also clears the L=240 bar, then goes to the HUMAN-ORACLE bundle (never auto-certified). Planted controls through the real path first (section 5).
- **Q2 prior.** None above flat is claimed. B-04/KDF are the "short Cicada-flavoured seed through a standard hash/KDF" family named in
  MEASURED-CEILING section 2a; the CicadaOS pads have a measured provenance (held ISO, sha-receipted, `handoff/capsule/recovered/*.sha256`). This lane is a
  **re-run of measured ground under a repaired instrument** (the Round 40 item-4 list of `analysis/round39/X1-redteam/RESULTS.md`); labelled closeout, not discovery.
- **Q3 bounded.** All four are enumerable lists; sizes in section 2. The pad grids are NOT densely enumerable (R17 swept 1.45e10 offsets): only a stated
  fraction is re-decoded (section 2, G3/G4); everything else is declared uncovered.
- **Q4 conditionals the negatives will carry.** (1) key space = exactly the regenerated lists of section 2; (2) transition model = `keyskip1` + `keyskip2`
  with <=2 skips in the head (pf_v4_12 does not screen heads with >=3 skips, ~3% of true-key mass by the R37 Poisson estimate); `skip_by_4`, `skip_by_5`,
  reset-per-page/line, `free`, and combined axes unrepresented; (3) register = panel-R36's 12 registers, power per register = the plant counts reported.
  Keystream-model screen caveat: the pf_v4_12 threshold was calibrated on bash heads (uniform Z29); for `hi_nib`/`lo_nib` (Z16) and `bits5` reductions the
  wrong-key FPR may differ; the realised survivor rate per reduction is reported and the planted controls cover each reduction.
- **Q5 kill.** If any register's planted control (section 5) fails the pooled gate for a grid, that grid-register cell is reported INCONCLUSIVE and carries
  no coverage claim. If RAM free < 0.4 GB for >20 min the lane stops and reports the fraction done. Hard cap ~2 h wall.

## 2. Key lists regenerated from committed code (counts stated; mismatches recorded)

### G1  B-04 (`analysis/round13/B04/seeds.py`, `ks.py`, `harness.py`, `sweep.py`)
- Seeds: `seeds.build()` -> **2,165** (original 2,165; core subset **504**, original 504); needs gitignored `data/keys/armada18|19` which ARE present.
  16 generators (`ks.GEN_NAMES`), 5 reductions. Keystream = `ks.make_ks(g, red, seed, nsym, raw=make_bytes(g, seed, int(nsym*1.35)+256))` exactly as the
  original worker, reverse = full-buffer reversal with the stage's own `nsym` (A: 728, B: 4029, C: 628), so rev heads equal the original rev heads.
- Stage A: 2,165 seeds x 16 x 5 reds x {fwd,rev} x sign{-1,+1} x atbash{0,1}, offset 0, head = `nc.unsolved()[:120]` -> **1,385,600** configs.
- Stage B: 504 core x 16 x {mod29, rej29} x {fwd,rev} x 4 sign/atbash x offsets **{0..7} U {16,29,64,128,256,512,1024,3301}** (original ladder
  {1,4,16,29,64,...,3301} U 0..7 = 16 offsets) -> **2,064,384**.
- Stage C: 504 core x 16 x {mod29, rej29} x fwd x 4 x **55 page heads** (`nc.segments()[:-2]`, per-page restart at offset 0) -> **3,548,160**
  (page heads of length < 120 are decoded at their own length; the L=120 bar is then not calibrated for them and the cell is marked `short_page`).
- Total screened: **6,998,144** head-variants (original 6.22 M beam decodes; ours is larger because of the added offsets 0,2,3,5,6,7).
- Not regenerable / not covered: Stage D (escalation of survivors) is superseded by the L=240 gate. `rev` at the L=240 gate reuses the stage's own buffer.

### G2  R16-KDF (`analysis/round15/KDF/kdf.py`, `sweep.py`)
- Secrets: `build_secrets()` = 504 core + 30 PASSPHRASES x 4 forms, deduplicated -> expected **534** (original 534). 27 KDF configs (`kdf.KDFS`), salts
  {empty, 3301, self}, reductions {mod29, rej29}, dir {fwd,rev} x sign x atbash = 8 variants, offset 0, K = `expand(block, 120+64, red)` (rev = reversal of that
  184-symbol buffer, as original) -> **692,064** configs. For fwd survivors the L=240 gate re-expands to 304 symbols; a rev survivor that clears L=120 at
  actual N is flagged directly (its original 184-buffer reversal cannot be extended to L=240).

### G3  R17 public pads (`analysis/round17/`)
- P3 pad list (28 pads, `P3_tables/pads_manifest.json`; RAND digits fetched from rand.org with the pinned sha256; Cicada-published bytes from
  `corpus/A-primary-artifacts/pgp`, regenerated by `build_pads.py` logic into the scratchpad, sha256 compared to the manifest; mismatches are listed, not hidden).
  P1 (Bitcoin heights 0-303,726, 12 builder files) and P2 (NIST beacon v1 + random.org 153 files) require ~GB of network fetches and are **declared NOT
  regenerated in this lane** (stated uncovered).
- Builders: `lib_padsweep.BUILDERS` (mod29, hi_nibble, lo_nibble, byte_scaled, prime_to_idx, hexchars) x {fwd, rev} x sign{-1,+1}; keystream symbol-index space.
- Offsets: all pads **0..7 plus the A1 ladder {1e3,5e3,2e4,1e5,1e6,1e7,5e7 where in range}**, plus a deterministic stride sample sized to a per-grid head
  budget (G3: <= 20 M head-variants; G4: <= 8 M), uniform over (pad, builder, dir) cells. Offsets are in the builder's symbol-index space. The fraction of the
  R17 dense space re-decoded is reported (expected ~0.5% of 5.76e9 offsets for P3); this is **a stated sampled fraction, not a dense re-sweep**.
  The R33-B1 gitignored-corpus trigram prefilter is NOT used; the screen is pf_v4_12.

### G4  CicadaOS pads (`analysis/round12/A1/`, `round28/L1/`)
- Pads from the held ISO (archive.org `3301.iso`, member extraction with `handoff/capsule/iso_extract.py`), sha256 compared to
  `handoff/capsule/recovered/*.sha256` (`DATA__560.00.iso-authoritative` a24051a8..., 3,992,970 B; `DATA_560.13` db79072c..., 118,818,811 B).
  Other R12-A1 pads (`560.17`, `folly`, `prime_echo`, `761.mp3`) are added if their bytes can be regenerated (ISO member / local `puzzles/2013/artifacts`).
- Builders: the five R28-L1 reductions {mod29, prime_to_idx, hi_nibble, lo_nibble, byte_scaled} x {fwd,rev} x sign; offsets: 0..7, the R12-A1 ladders, and the R28-L1
  stride grids (16,384 on 560.00, 331,777 on 560.13) U a uniform stride sample within the G4 head budget.

## 3. Screen and decode

- Screen: pf_v4_12 `dp_regs`/`lse_from_regs` with the frozen thresholds (thr a1 7.415, a2 7.441), applied to (C-head variant, effective key head); effective key for
  sign +1 is (-K) mod 29, so decoding is always C' - K_eff; atbash = 28 - C. A config is a survivor if either relation's lse exceeds its threshold (rel=both).
- Survivors: beam_v3 `panel_max` (tau=0, lam_u=4, width 400) under BOTH relations at L=120 (or page length if shorter), written as 14-field rows
  (`to_row(a, kid, with_degenerate=True)`) to `rows_<grid>.jsonl` in APPEND mode. N for the bars = survivors decoded per relation.
- Bars: `bar_v3(N, L, rel)` from null12 at the actual N and at N=1e6; additionally reported at N = number of configs screened (conservative, since the
  screen is part of the instrument). Primary decision uses the actual-N bars (as R37-I2); the others are context.
- Gate and flags: a row with pmax120 >= bar120(actual N) is re-decoded at L=240 (first 240 runes of the same stream and head variant); pmax240 >= bar240(actual N)
  => **FLAGGED_FOR_ORACLE** (HUMAN-ORACLE bundle written, never certified). pmax120 >= bar120(actual N) but failing the gate, or clearing actual-N but not
  N=1e6, or pmax >= 6.0 with `degenerate=false`: listed as **near-miss** with seed/config/register. `degenerate=true` rows are listed separately.

## 4. Nulls

Wrong-key FPR of the screen is measured by the realised survivor rate over the full grid (all configs are overwhelmingly wrong keys) and reported per reduction.
The grid's own v3 score histogram (floor(pmax) bins) is persisted. No new null fit is made; `null12.json` bars are used as of Round 36.

## 5. Planted controls (before any grid output counts)

Per grid, through the real route: draw a random config of the grid (seed/secret x generator/KDF x reduction x direction x sign x atbash x offset incl. stage-B/C
offsets), regenerate its key with the grid's own key function, encipher a 240-rune plain window from the panel-R36 held-out test halves
(`data/panels/testhalves-r36.npz`) under the real anti-repeat filter at natural rate (`enc_exact` for keyskip1, `enc_pair` for keyskip2; C' then atbash if the config says so;
only filter: C[:40] doublet-free, as the real LP2 head), then run the **sweep's own screen function** on the planted head together with 512 random decoy configs of the
same grid, then v3 L=120 (both relations), L=240 gate, panel, recovery. **Registers: EN_MODERN, EN_NOVOWEL, LATIN; 10 plants per (register x relation) per grid
(60 per grid)**; skip split (skip in first 24 runes of the head or not) reported. Pass per plant = pmax120 >= bar120(N=1e6) and pmax240 >= bar240(N=1e6)
and recovery240 >= 0.90. **Grid gate:** each (register, with-skip/skip-free) pooled cell must show >= 3 recoveries (the R37-I2 gate) to license that register's
coverage; otherwise INCONCLUSIVE for that register.

## 6. Reporting

`RESULTS.md` per grid: keys regenerated / original count, control table, N per relation, best vs bars (actual N, N=1e6, N=screened), flagged / near-miss, the
conditionals carried (keyskip1+keyskip2; 12 registers; sampled fraction). `ledger.json` (one row per grid), `ledger_patches.json` (B-04, R16-KDF, R17-PUBLIC-PAD,
R12-A1 / R28-L1 coverage extended with the construction x register cell; MEASURED-CEILING lines to refresh with pins). No terminal vocabulary: bounds, not verdicts.
No `git` is run by this lane.

## 7. Resource discipline

ONE Python process (nproc=1); RAM free checked (`Win32_OperatingSystem.FreePhysicalMemory`) before each batch, wait if < 0.4 GB (max 20 min);
rows streamed in append mode; downloads (ISO, RAND zip) go to the session scratchpad, not the repo.
