# Round 42 / C2 — R36 dated pads (H7xF9) under panel-R36: RESULTS

2026-11-02. `PREREG.md` first. panel-R36, standing free-null bar of record.

## Result: NEGATIVE (measured, 12 registers)

X1-B/R41 (B-2) showed the R17 pad data (523 MB) is present (round41-C1's "absent" was
clone-scoped). Re-ran the dated-pad cell under the current instrument:

- **12 pad byte streams** applied as additive mod-29 pads: P1 (Bitcoin `hash_display/internal`,
  `merkle_display/internal`, `nonce_le`, `time_le`, + 2013 variants) and P2 (NIST beacon
  `outputValue` / `seedValue`, random.org aggregate pads). Each read to a 4 MB prefix, windowed
  from ~150 stride-sampled offsets, both signs (c+pad, c-pad), both atbash, every decode
  adjudicated under panel-R36. Grid 7,200.
- **Verdict.** Global best **pmax 5.003** (`hash_internal_2013.bin`, page 46, L=270, start
  1,664,190, sign-1 atb0, register LP1_REAL) vs free bar of record **16.94**. **0 crossers**, no
  near-miss. The dated public pads are a measured negative under 12 registers — consistent with
  the doublet exclusion of additive full-entropy keystreams.

## Scope / not covered
Each pad read to a 4 MB prefix (the random.org aggregates are larger; offsets beyond the prefix
not swept); ~150 stride-sampled offsets per pad; additive `c +/- pad` + atbash only (no
date→offset anchoring beyond the offset sweep); `byte % 29` carries a mild bias (256 = 8·29+24,
values 0–23 slightly favoured) — immaterial to a null this far from the bar but noted; the free
bar is the standing null, not a fresh per-shuffle null.

## Ledger
Adds `R42-C2-R36-DATED-PADS-RUN` (negative); patches `R41-C1-R36-DATED-PADS-VERIFIED`.

## Files
`PREREG.md`, `RESULTS.md`, `run_c2.py`, `c2_results.json`, `ledger_patches.json`, `apply_ledger.py`.
