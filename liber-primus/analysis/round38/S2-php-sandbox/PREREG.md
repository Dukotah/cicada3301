# R38 / S2 PREREG - PHP mt_rand tier (b) on the Vercel sandbox under pf_v4_12 + beam_v3 + panel-R36
Written FIRST, 2026-10-30, before any sandbox was created or any output produced. No git. Writes only under this dir (local) / a mirrored dir (sandbox).

## Cells and relations
Four cells: mt_scale, mt_mod, php_scale, php_mod (PHP 5.x mt_rand, canonical or legacy<=7.0 twist x scale29|mod29), offset 0, sign -1, C[0]-aligned. Relations keyskip1 + keyskip2. Same four cells as R32-B2 / R36-B2; nothing re-tuned.

## Instrument (frozen)
Screen: round37/I2 pf_v4_12 (m=24,k=2,pen 2, rel=both, thr a1 7.4155 / a2 7.4412 from frozen_op12.json, lse over the 12 panel-R36 LMs). Decoder: round33/I1 beam_v3 panel_max tau=0 lam_u=4 beam_w=400, set_panel(panel-r36.npz), L=120 screen / L=240 gate. Bars: round36/B1 null12.json POT fit (the same bar_v3 form as round37/I2) at actual N per cell x rel and at N=1e6. Survivors of EITHER relation are decoded under BOTH.

## Steps and order
1. Smoke: beam_v3 + panel-R36 + pf_v4_12 import on the sandbox; plant one key, pf passes it, v3 decodes it (recovery>=0.90).
2. FPR12 (`fpr12_php.json`): 2^17 uniform wrong-key heads per cell (numpy default_rng(3399)), frozen thresholds, per relation and union, Wilson 95%. (The sweep's own survivor rate over millions of seeds is reported as a second, larger measurement.) Closes R37-I2 not_covered "PHP-cell FPR under the 12-register point".
3. Control (`control.json`): per cell x relation x register in {EN_MODERN, EN_NOVOWEL, HEBREW}: 10 natural-rate plants (=240) via real enc_exact/enc_pair, uniform 32-bit seed, held-out testhalves-r36 windows, only filter = realised C[:40] doublet-free, NO skip-free selection; real chunk path (2^16-seed chunk with the plant -> pf_v4_12 -> v3 L120 both rels on survivors -> L240). recover = pass declared-N=1e6 bars at L120 AND L240 AND recovery240>=0.90. Skip / skip-free split reported. Gate: >=3 recoveries in every pooled register x split; if it fails, no coverage claim and the lane stops at the harness fix.
4. Windows (each <=45 min compute cap, parallel 2 worker processes, blocks of 2^17 draws screened on all four cells at once):
   * W1: default_rng(3301) blocks 199..317 inclusive (119 blocks, 15.60 M seeds per cell). R36 covered blocks 0-198 (199 blocks = indices 0..198; index 199 was never screened, which is why this window starts at 199 rather than 200); R32 B2 covered blocks 0-317 of the same stream with a weaker screen (9-register, older pf). Therefore W1 gives the *new instrument* on these seeds (the 12-register screen + panel-R36), but ADDS ~0 genuinely unscreened seeds beyond block 317 relative to R32's weaker screen; it adds 119 blocks relative to R36. This is stated, not hidden. If W1 finishes under its cap, it continues into blocks 318.. (never screened by either) until the cap.
   * W2: fresh default_rng(3302), blocks 0.. until its 45-min cap (disjoint-by-construction random stream; overlap with 3301 expected ~ blocks*2^17/2^32 and is not removed).
   * W3 only if sandbox quota/time is comfortable: 3301 blocks past W1's end.
   Rows written in APPEND mode to one store (header once; the harness refuses "w" on a non-empty store); state after every block; rows downloaded to the lane dir (chunked if large).
5. Adjudication: pmax120 >= bar120 at actual N -> L240 re-decode with the cell key -> pmax240 >= bar240 -> FLAGGED_FOR_ORACLE bundle (SEAL_PASS=false). Clears actual-N but not declared-N 1e6 bar: near-miss list. Survivors scored for all 12 panel registers (preg reported). Stock validate_store + check_r3_store locally on the downloaded store.
6. Seeds-added honesty: per stream, the count of blocks not screened before by ANY prior lane vs by R36 (12-reg/9-reg-pf_v4 instrument) is tabulated separately; duplicates not removed.

## Kill / stop
Control gate fails -> harness fix, no claim. Any window cap fires -> report what ran, do not extend. Sandbox creation fails -> write script and stop. No "solved/closed/exhausted" wording; a negative result is "no crosser in the screened fraction f of cell X".
