# R40-B3 PREREG ADDENDUM 1 (2026-10-31, written after the B04 control and before any grid sweep row)

Implementation decisions that fix open parameters of `PREREG.md` section 2 (G3/G4) and section 5; no threshold or bar is changed.

1. **Counts confirmed before any sweep** (`counts.json`): B-04 seeds regenerated 2,165 / core 504 (original 2,165 / 504); planned head-variants A 1,385,600, B 2,064,384, C 3,548,160 (total 6,998,144).
   KDF secrets regenerated 534 (original 534), planned 692,064 (original 692,064).
2. **Pad grids (G3, G4) are bounded stated-fraction lanes.** Per (pad, builder, direction) cell the offset set is: all offsets if the cell has <= cap offsets, else offsets 0..7 + the A1
   ladder {1e3, 5e3, 2e4, 1e5, 1e6, 1e7, 5e7} + the R28-L1 stride grids (560.00 auth: multiples of 16,384; 560.13: multiples of 331,777) + an evenly strided sample of `cap` offsets.
   Caps: G3 (R17-P3 28 pads) cap = 40,000 per cell; G4 (CicadaOS) cap = 250,000 per cell. Sign is screened both ways; atbash is NOT applied for pad grids (neither R17 nor R12/R28 swept atbash).
   A sweep decode requires >= 200 key symbols after the offset (offsets closer to the end of a pad are not decoded; pads with < 200 symbols for a builder are skipped).
3. **Builders.** G4: the five R28-L1 reductions. G3: the six `lib_padsweep.BUILDERS` + `nibbles` (the R17 P0/P3 addendum builder); `hexchars` only for pads <= 2 MB (its python `eng_to_idx` cost is prohibitive above that); the
   large-pad hexchars cells are declared uncovered. Controls plant only in cells with >= 2,000 symbols.
4. **Pad inventory.** G4 = ISO members `DATA/_560.00` (the "authoritative" 3,992,970 B), `DATA/560.13`, `DATA/560.17`, `AUDIO/761.MP3`, extracted with `handoff/capsule/iso_extract.py` from the archive.org `3301.iso`
   (sha1 df433cba... as in `RECOVERY-560.13.md`); sha256 of 560.00 auth and 560.13 compared to the committed receipts. NOT regenerable here: R12-A1's truncated 2,412,544 B `_560.00`, `folly`/`wisdom`, `prime_echo`
   (sources were the cicada-solvers mirror / local artifacts no longer on disk); R17-P1 (Bitcoin) and R17-P2 (beacon + random.org) (multi-GB fetches).
5. **KDF gate.** fwd KDF survivors are gated at L=240 by re-expanding the same block to 1,024 symbols (prefix-identical to the 184-symbol buffer); rev survivors cannot be extended (their screen buffer is the reversal of the 184-symbol buffer) and any rev
   survivor clearing the L=120 actual-N bar is flagged directly. KDF rev plants are therefore L=120 plants (pass = pmax120 >= bar, recovery >= 0.90 over the 120 runes).
6. **Decoy columns in the control** are 512 random columns per plant for B-04, 128 for KDF (derivation cost), 256 for pads; the decoy survivor rate is reported as an extra screen-FPR measurement.
