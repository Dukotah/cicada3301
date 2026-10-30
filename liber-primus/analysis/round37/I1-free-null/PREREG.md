# Round 37 / I1 -- L-matched `free` null + `free` planted control: PREREG
Dated 2026-10-30, written BEFORE any decode of this lane (no output exists yet).

Instrument: `beam_v3.beam_decode_v3(C, K, "free", "panel_max", sign=-1, o=0, beam_w=400, tau=0, lam_u=4)`, imported as it stands at my start
(Lane T1 edits it concurrently; I do not edit it). Panel: **panel-R36** (`data/panels/panel-r36.npz`, 12 registers, EN_MODERN EN_KJV LP1_REAL
LATIN OE DE CY EN_HALFVOWEL EN_NOVOWEL GREEK HEBREW NORSE) used for BOTH the beam objective (`V.PANEL_PATH` set before first `V.panel()`; `register`-cluster
list is not used by panel_max) and the scoring statistic pmax = max-register z (`adjudicate_batch(..., pan=panel-R36)`). All numbers are therefore
12-register numbers; the O3 "15.15 / 14.33" were 9-register pmax9 and are NOT directly comparable (the O3 cell is re-decoded and re-scored here).
Key room: free consumes up to ~41 key symbols per rune (max_skip 40, max_free 2), so keys are 41*L+64 long (as O3), not R34's 6L+64.

## Null (Q2/Q3)
Shuffled-LP2 wrong-key draws (draw k: `random.Random(3301+k)` shuffles the LP2 rune stream U, take first L; keys round-robin over the six R34 families
B1 bash4.2 / bash4.2_i32, B2 mt_scale/mt_mod/php_scale/php_mod from keyskip1-survivor seeds, `rng=Random(3301+7L)`), identical machinery to R34 `run_null.py`.
L in {240, 400, 729} target >= 2,000 draws each, plus L=120 (1,000 draws) to compare with R34's `free` L=120 fit under the new panel.
Order/allocation (rule fixed now): 50-draw timing per L (these are draws 0..49 of the null, kept); then control L=240 (first, it decides usability);
then nulls in the order 120, 240, 400, 729 with wall allotments set from the measured cost so that null+control <= 90 min HARD. If L=729 gets < 2,000 draws
its fit is made from what ran AND reported as fitted from fewer draws / trend; I will not pad. Nothing is dropped after seeing a result.
Fit: R34 `fit.py` machinery -- exponential POT above the empirical 90th percentile u; beta = mean excess; mu = u + beta ln p_u;
bar(N) = mu + beta ln(N / -ln(0.99)) (alpha=0.01). Report mu, beta, per-L, empirical p99/max, xi_GPD, and the beta(L) power-law exponent.
Bars at N = 1e3, 1e5, 1e6. mu(L) interpolated in ln L between nodes in bars_v3 (flat outside 120..729; free at L<120 or >729 stays an error).

## Control (Q1)
Plant: held-out register text window (`testhalves-r36.npz`, window start `Random(9000+s).randrange`), enciphered with R32 `free_q05` (keyskip1 plus an
unrelated advance w.p. 0.05, supp 0.83, seed 3301+s) under K = SHA-CTR key (41L+64), decoded with the same free beam, scored pmax12.
Pass rule: plant pmax >= bar(N=1e6, L, free) in >= 19/20 seeds, per register. 12 registers x 20 seeds at L=240 (all). At L=400 and L=729 as many
seeds per register as the cap allows (>=5 at 400 / >=3 at 729 planned; the achieved number is reported and a per-register "pass" claim needs 19/20, so with fewer
plants a register is marked "n<20: indicative only", not passed). Optional L=120 12x20 repeat for comparability with R34 (only if time remains).
Verdict wording: "free carries claims at L=... for registers ..." lists only (L, register) pairs with >= 19/20 at N=1e6 AND a null with a fitted bar. No claim at a failing (L, register).

## O3 re-judgement (Q2)
Re-decode O3's cell (bash 4.2 ILP32 seed 1354603465, free, sign -1, L=729, o=0, c0=0, C=LP2[0:729], key length 41L+64 as in O3) under panel-R36; report its pmax12
(and the stored O3 pmax9/pmax12 from `cells.json`), the empirical quantile against my L=729 null, the Gumbel p (single-draw and family-wise for the O3 grid of ~460
free cells), and a verdict. The cell was the max of a selected grid (seed chosen as sweep max; ~460 free cells), so the family-wise reading is the one that counts.
Kill/noise rule: observed < N=1e6 bar (or family-wise p >= 0.01) -> NOISE/not a signal; no "solved".

## Authorised edit
`round34/I1-v3-null/bars_v3.py`: `relation="free"` returns the fitted bars for L in {240,400,729} (and 120 stays R34's original 9-register node unless explicit),
existing doctests unchanged, one doctest added; dated addendum appended to that RESULTS.md. NOTE the R34 `free` nodes are 9-register; mine are 12-register
(panel-R36). I will expose the new family as `bar_v3(..., relation="free", panel="r36")` and leave the default call unchanged.

## Addendum (2026-10-30, after the 50-draw timing, before the main run)
Measured free cost under panel-R36 (41L+64 keys): 0.62 s/draw (L=240), 1.31 (L=400), 2.16 (L=729). 2,000 draws at every L would need ~136 min > the 90 min cap.
Allocation fixed by the rule above, before any null or control result: control L=240 12x20; control L=400 12x5; control L=729 12x3; null L=120 1000 draws (<=250 s);
null L=240 up to 2000 draws (allot 1250 s); null L=400 allot 1350 s (~1000 draws); null L=729 allot 2400 s (~1100 draws). So **L=400 and L=729 will NOT reach 2,000 draws**; the
Gumbel POT fit uses the draws that ran (the tail k = 10% of n is ~100 exceedances), bars are stated with their SE, and this is a stated shortfall, not a hidden one.
The draws 0..49 of the timing run are kept as the first 50 draws of each null.

## Addendum 2 (2026-10-30, mid-run)
Operational: a path bug (R34 `common34.HERE` shadowed my lane dir) wrote the first stream files into round34/I1-v3-null/ (new files only, nothing overwritten); I moved them
into this lane dir and fixed the path. The chain was restarted at the L=240 null (control runs L=240/400/729 and null L=120 (701 draws; its 250 s allotment bound, cost 2.7 draws/s)
had completed). The L=729 allotment is cut from 2400 to 2000 s to keep the hard 90-min total.
