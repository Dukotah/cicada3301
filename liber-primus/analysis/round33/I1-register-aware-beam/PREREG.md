# Round 33 / I1 -- register-aware beam (`beam_decode_v3`): PREREG

_Written 2026-10-29 12:57 PT, BEFORE `beam_v3.py` was written or any output file existed (the lane directory
was empty, `ls -A | wc -l` = 0, when this file was created). Thresholds below are fixed. Changes = dated
addenda at the bottom, never edits._

## 0. Hypothesis
Round 32 I1 measured that the repaired transition relations (driftbeam keyskip1 / keyskip2 / permissive)
recover planted EN_NOVOWEL only at 0.72 (L=120) / 0.71 (L=400) under `skip_by_two`/advance 2 and 0.31 / 0.13
under `free`, because the *search* ranks partial decodes with the English quadgram (`driftbeam.py` L41).
H1: replacing the search score with a register-aware one lifts EN_NOVOWEL recovery to >= 0.90 at L=120
without costing any other register > 0.05. A negative on this is a result (Q5).

## 1. Instrument
`beam_v3.py`: the driftbeam transition relation re-implemented unchanged (same enumeration, same `ADVANCE`
presets: keyskip1 / keyskip2 / permissive with max_skip 8/8/40, max_free 0/0/2, start_slack 0/0/2, beam_w 400),
with the hypothesis score replaced. Score is computed in RUNE space from the Round 32 I2 nine-register trigram
panel (`round32/I2-multiregister-readjudication/models/panel.npz`, read-only):

    U_r = sum over trigrams of (LM_r[t] - mu_r(L)) / (sd_r(L) * sqrt(L))     (mu, sd from Panel.cal(L), L = len(C))

so a register's U_r is its running z*sqrt(m). A penalty `lam_u * n_unexplained` is subtracted (free relation
only; lam_u in U units; driftbeam's lam=12 is in quadgram-log10 units and is NOT carried over).
Designs, in this order, each tried only if the earlier one did not pass its gate:
 1. **panel-max**: search score = max_r U_r  (variant: softmax tau*log sum exp(U_r/tau)).
 2. **register-conditioned**: 7 parallel beams, one per cluster {EN_MODERN,EN_KJV,LP1_REAL}(max within) / LATIN / OE /
    DE / CY / EN_HALFVOWEL / EN_NOVOWEL; the 7 final decodes are merged by the panel (highest `pmax`).
 3. **language-agnostic**: search score = negative adaptive code length (order-0 + order-1 mixture, PPM-style
    escape=2). Stated deviation: min-distinct-over-32-window is not tracked incrementally in the search (it needs a
    32-rune window per hypothesis); IoC is subsumed by the order-0 adaptive term. Panel only at the end.
Final adjudication for every design: `round32/I2/adjudicate.adjudicate` (nine-register panel), unchanged.

## 2. Positive control / grid (cell-for-cell with Round 32 I1)
Key = `beam_v2.sha_ctr_key(L*12+2048)`; enciphers `keyskip1`, `skip_by_two`, `free_q05` (supp 0.83, seed 3301+s);
plant window start `random.Random(9000+s).randrange(0,len-L-1)`; s = 0..19 (20 plants per cell); L = 120, 400;
correct key and offset 0 handed to the decoder; sign -1. Matched pairs: (keyskip1, advance 1),
(skip_by_two, advance 2), (free_q05, advance free) -- 9 registers x 3 relations x 2 L x 20 = 1080 decodes per decoder.
Registers: the 9 of the I2 panel. **Plant texts = the I2 `testhalves.npz` held-out halves** (the halves the panel
LMs were NOT trained on). STATED DEVIATION: Round 32 I1 used its 7-register lite test halves; for LATIN, OE, DE,
LP1_REAL the arrays are identical (same shapes), but EN_MODERN, EN_HALFVOWEL, EN_NOVOWEL differ (lite =
self_reliance only; I2 = self_reliance+mabinogion split-half) and EN_KJV, CY have no Round 32 I1 baseline. To keep
every comparison same-plant, **driftbeam (`beam_v2`) is re-run on exactly these plants** as the binding baseline;
Round 32 I1's published numbers are shown beside it where they exist. Tuning seeds (below) are disjoint from 0..19.
Recovery = rune-index recovery vs the plant. Summary stat = median over 20 (as Round 32 I1), with mean and
fraction >= 0.85 also stored.

## 3. Null
Per (relation, L in 120/400), 100 decodes of the Round 32 I1 null ciphertexts (planted skip_by_two on lite
EN_MODERN window s, seed 3301+s, then `random.Random(3301+s).shuffle`) -- identical ciphertexts to
`round32/I1/out_null.json`, decoded by v3 and adjudicated with the panel. Bars reported, and which binds stated:
 (a) `benchmark/null.py threshold_for(N, segment_len=L)` on the legacy `en` score, N = 100 (own null size) and
     N = 1e6 (sweep scale);
 (b) hitfn20 panel-max bar `round20/P3/panelmax20.panelmax_bar(preset, N)` (preset exact/pair/drift for advance
     1/2/free; the calibrated cell exists at L=120 only -- at L=400 the L=120 cell is applied and flagged). It was
     calibrated on driftbeam wrong-key decodes, so v3's own null max is the binding check of record;
 (c) v3's own shuffle-null max `pmax` (R32 I1 convention) -- RECOVERED = median recovery >= 0.85 AND >= 80% of
     seeds with pmax above this.
Not done in this lane: a null on the real shuffled LP2 stream (R32 I1's planted-shuffle null is used for
cell-for-cell comparability).

## 4. Gates
**VALID (all required):**
 V1. EN_NOVOWEL median recovery >= 0.90 at L=120 under `skip_by_two`/advance 2 (the Round 32 headline cell). The
     other two relations are also reported; a pass on only one relation is stated as such.
 V2. For every register x matched relation x L in {120,400}: v3 median recovery >= (same-plant driftbeam median) - 0.05;
     also reported against Round 32 I1 published medians where they exist.
 V3. Null: reported; v3's null max `en` vs the L-aware `threshold_for(100, L)` floor (-5.5) and null max `pmax` vs
     plant medians, stated either way.
**Q5 kill checkpoint (10% of budget):** after design 1 at L=120 on EN_MODERN + EN_NOVOWEL only,
2 registers x 20 plants x 2 relations (keyskip1/1, skip_by_two/2) = 80 decodes: if NOVOWEL (skip_by_two/2) median
recovery < 0.80 AND design-1 wall time per decode > 3x driftbeam's (same cells, same machine), drop design 1 and
move to design 2. If all three designs fail NOVOWEL >= 0.90 at L=120, STOP and record "EN_NOVOWEL is not
beam-searchable with n-gram register LMs" -- a result, filed as a permanent not_covered.
Design 1 reaching >= 0.80 at the checkpoint proceeds regardless of cost (cost is reported).

## 5. Tuning (the only free parameters; tuned on tuning seeds only)
Tuning plants: s = 500..509, registers EN_NOVOWEL + EN_MODERN, L=120. Grid: tau in {hard max, 5.0} on
skip_by_two/2; lam_u in {2, 4, 8} on free_q05/free (NOVOWEL). Choose the setting maximizing NOVOWEL mean recovery
with EN_MODERN not worse than hard-max by > 0.02; ties -> hard max / smaller lam_u. No tuning on s = 0..19.
beam_w = 400 for all designs (D3 may be reduced for the free relation if time forces it -- stated if so).

## 6. Aiming-test answers
**Q1.** Recognizer = planted correct key over each register's held-out text, rune-index recovery, adjudicated by the
panel; control = driftbeam on identical plants (should reproduce Round 32 I1's NOVOWEL failure; if it does not,
that is stated).
**Q2.** `round32/I1-skipbytwo-decoder/RESULTS.md` s3 (NOVOWEL 0.72/0.71/0.31/0.13); `round18/L7-redteam/RESULTS.md` A;
the adjudicator already sees NOVOWEL (pmax still above null for NOVOWEL under advance 2, R32 I1 s3).
**Q3.** Bounded: <= 1080 plants x (baseline + up to 3 designs) + 600 null decodes per design; no key space opened.
**Q4.** Conditionals: key space = none (instrument; correct key handed over); transition model = keyskip1 /
keyskip2 / permissive-with-2-free-advances (unchanged, so resets, advance >= 3, interrupters remain uncovered);
adjudicator register = nine-register trigram panel. The search LMs are the SAME LMs the adjudicator uses, so
planted-vs-panel agreement is partly circular (stated).
**Q5.** As in s4.

## 7. Hard limits
One Python process; no `git`; writes only under this directory; beam_w <= 400; no filesystem-wide find.

## Addenda
(none yet)

### Addendum 2026-10-29 (after outputs; no threshold changed)
- Order actually run: Q5 checkpoint (80 decodes x design 1 + same-cell driftbeam) -> tuning (seeds 500-509) -> nulls -> full matched
  grid for driftbeam and design 1 -> speed for all three designs -> supplementary L=120 runs of designs 2 and 3 (not required once
  design 1 passed the checkpoint and gates; added for the speed/coverage record).
- Checkpoint passed on recovery, so the kill rule's cost clause was moot. Tuning chose tau = hard max (tie) and lam_u = 4.
- Everything else as pre-registered; the I2-testhalves plant deviation was declared in s2 before running.
