# Round 33 / B3 -- re-adjudicate the Round 32 B1/B2 survivor rows through beam_decode_v3: PREREG

_Written 2026-10-29 13:26 PT, before readjud.py or any output file existed (lane dir empty). Changes = dated addenda only._

## Instrument
`beam_v3.beam_decode_v3` design `panel_max`, tau=0 (hard max), lam_u=4, beam_w=400, sign -1, o=0. keyskip1 = advance 1, keyskip2 = advance 2.
`free` NOT run (3.7 decodes/s at L=120: ~1.1e5 s for the store); filed not_covered. Adjudicator = round32/I2 nine-register panel.
Ciphertext = unsolved LP2 runes [:120] (same C_SCREEN as Round 32). Keystream regenerated from the stored kid (seed, variant/cell) with the
Round 32 `ks()`; only STORED SURVIVOR ROWS are decoded, never the orbits.

## Row subset and fraction (fixed now)
Universe = every non-header row of `round32/B1-bash-random/sweep_rows.jsonl` (192,066) and `round32/B2-php-mtrand/sweep_rows.jsonl` (212,218)
= 404,284 (seed, variant|cell, relation) decodes; kid is `bash:<variant>:<seed>:<rel>` / `php:<cell>:<seed>:<rel>`. The universe is permuted
with `random.Random(3301).shuffle` and re-decoded in that order until a hard 1500 s wall budget for this stage; the processed prefix is a
uniform random sample. Realised fraction per store x relation is reported (no cherry-picking, no reordering, no resume-skipping).
The Round 32 I2 survivor lists (B-04 225, R16-KDF 48, R16-PRNG 20, R17 5,730) are stored as DECODED TEXTS (translit), with no ciphertext/key pair, so a
v3 re-decode is impossible: filed not re-decodable (their panel adjudication already stands in R32 I2). Their ledger rows get a not_covered note only.

## Control (before any null counts)
Cells: B1 {bash4.2, bash4.2_i32} x {keyskip1, keyskip2}, B2 {mt_scale, mt_mod, php_scale, php_mod} x {keyskip1, keyskip2} = 12 cells.
Per cell: 5 EN_MODERN + 5 EN_NOVOWEL plants (I2 testhalves, L=120, key = a real stored-survivor seed of that cell, enciphered with the Round 32
encipher: enc_exact for keyskip1, enc_pair supp 0.83 for keyskip2), pushed through the B3 stage-2 path (v3 decode + panel adjudication).
PASS = recovery >= 0.90 in >= 3 plants per cell and >= 3 EN_NOVOWEL recoveries per cell at the N=5 plants stated. Deviation (declared): the
Round 32 prefilter is not part of B3's path (survivors are already past it), so the control exercises the stage-2 path, not the 2^16-seed chunk.

## v3 null and bar
Real LP2 stream, `random.Random(3301+k).shuffle` of the full unsolved stream, first 120 runes, k=0..11999; each draw is paired with a
keystream from a round-robin of the 6 key families (2 bash variants + 4 php cells) using a seed drawn from the stored rows; decoded under
keyskip1 and keyskip2 by v3 and panel-adjudicated. Bar (per relation) = max of (a) peaks-over-threshold exponential tail fit (threshold =
90th percentile, mean excess -> beta) extrapolated to family-wise alpha=0.01 at N = rows actually re-adjudicated for that relation, and
(b) the empirical null max at N_null=12000. Also reported: 99th percentile. Whichever is larger binds. Extrapolation beyond N_null is declared.
The hitfn20 bars are not used (I1 s3).

## Flags
pmax >= binding bar for that relation -> "flagged-for-oracle", never certified; re-screened at L=240 (C[:240], same K, v3) and both reported.
Flag requires nothing else; no claim of a key. Wall cap 45 min total, one process, nproc=1, no git, no solved/closed/exhausted language.

## Addendum 13:37 PT (before the run): smoke timing showed wrong-key decodes cost ~2-10 ms, far below I1's planted-key speed, so the null is enlarged to N_null=12000 draws (k=0..11999) and the run budget is 1380 s. Nothing else changed.
