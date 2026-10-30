# R36 / O3 PREREG - near-miss autopsy of bash 4.2 seed 1354603465 (written 2026-10-30, BEFORE any grid / verifier / null was run)

Timing disclosure: before this file existed I ran ONE 4-decode timing probe (L=120 keyskip2/keyskip1/free, L=240 keyskip2, LP64, o=0)
to check feasibility; it reproduced pmax 7.068 (keyskip2 L=120) and nothing else was looked at. Everything below is fixed now.

Note on paths: the Round 33 re-screen lives at `analysis/round32/X1-redteam/rescreen_1354603465.json` (not round33).

## Hypothesis under test
H1: seed 1354603465 under bash 4.2 `RANDOM=seed; $RANDOM%29` (sign -1, key offset 0, C[0]-aligned), keyskip2, is the true LP2 keystream
generator (the only recurring near-miss: R32 B1 / R33 X1 re-screen / R35 B1 pmax 7.068, argmax LP1_REAL).
H0: it is the maximum of ~7e4 (actual-N) wrong-key decodes in a pf_v4-filtered orbit and nothing more.

## Instrument
beam_v3 `panel_max` (tau 0, lam_u 4, beam_w 400) driven exactly as R35 B1 (`decode_seed`); adjudication by the R32 9-register panel
(`panel.npz`) AND the R36 12-register panel (`panel12.npz`, same decode re-scored; the beam search itself uses the 9-panel as in the sweep).
Bars: `bars_v3.bar_v3(N, L, rel, family="lp2")`, N_actual=69,017 (R35 B1 LP64 survivors) and N_declared=1e6; L=262/729 are outside/between fit nodes
(nodes 31,120,240,400; flat clamp beyond 400) - flagged as extrapolated, so the size-matched null (verifier A) is the bar of record at those L.

## Reproduction (step 2) - pass criterion
LP64 keyskip2 L=120 pmax == 7.068 +/- 0.001, argmax LP1_REAL; ILP32 keyskip2 L=120 == 6.762 +/- 0.01 (beam_w 400; R33 used beam_w 64, so tiny drift allowed).
If not reproduced, report that and stop.

## Grid (step 3) - cells.json
ABI {bash4.2 LP64, bash4.2_i32} x relation {keyskip1, keyskip2, free} x sign {-1,+1} x L {120, 240, 400, 262 (= whole page 0), 729 (= pages 0-2 concatenated;
page lengths 262+266+201)} x offset axes, ONE AXIS AT A TIME (not a product):
  - key offset o in 0..28 (beam `o`, ciphertext U[0:L]); this contains the key-phase offsets 0..7
  - cipher-start offset c0 in 1..28 (ciphertext U[c0:c0+L], o=0)
`free` at L=400/729 only at o=0,c0=0 (cost). Compute is capped; if the cap hits, the uncovered cells are listed in RESULTS (coverage stated, not hidden).
Every cell records pmax and argmax register under the 9-panel AND the 12-panel. "Best cell" = max pmax9 BUT ranked per (rel, L) against that cell family's bar,
and the best cell over the whole grid is compared against a grid-matched null (below), because the grid itself is a selection.

## pmax-vs-L (step 3)
For the best (ABI, rel, sign) at o=0,c0=0 report pmax at L=120,240,262,400,729. Positive-control growth: a PLANT (below) decoded at the same L.
Rule: TRUE-KEY-LIKE = pmax(729) >= 1.5*pmax(120) AND monotone non-decreasing over the L series AND pmax(729) clears the verifier-A 99.9% quantile at L=729.
PLATEAU/FALL = pmax(729) <= pmax(120) (noise-like: a wrong key's pmax is L-independent by construction since z is standardised).

## Verifier A - size-matched null  (kill: if the observed value is below the stated quantile ceiling -> consistent with noise)
2000 random in-orbit bash 4.2 seeds (same draw as R35: top bits from the 74 prefixes of 2^20 span 2012-01-01..2014-05-31, low 20 bits uniform), identical cell
(LP64, keyskip2, sign -1, o=0, c0=0, beam_w 400) at L=120 and L=262 (2000 each), L=729 (400 draws, cost), ILP32 L=120 (2000).
Report empirical quantile / exceedance count of 7.068 and of the best full-page score; then the family-wise ceiling P(max over N_actual >= obs)
via an exponential POT tail fit above the null's 90th percentile (Gumbel, as bars_v3 does) - the ceiling is "how often the BEST of 69,017 wrong seeds looks this good".
Grid-matched null: 40 random seeds x the L=120 keyskip2/keyskip1/free o-axis + both signs (sign x o: 2 x 29 x 3 = 174 decodes per seed) -> distribution of best-over-grid; compare with the seed's own best-over-the-same-slice.
KILL (NOISE) if observed 7.068 is below the 99.9% empirical quantile x family-wise bar (i.e. the actual-N family-wise p >= 0.01) AND no L-growth.
ESCALATE only if ALL of: (i) pmax(729) clears verifier-A's 99.9% (or max) quantile at L=729, (ii) growth per rule above, (iii) verifier B stable, (iv) verifier C text is language-like.

## Verifier B - register consistency
(1) One long decode (pages 0-2, L=729, best rel); cut into non-overlapping 120-rune segments; per-segment 9- and 12-panel pmax and argmax register.
(2) Independent decodes of consecutive 120-windows (U[120k:120k+120], o=0) - for a true key with fixed o the keystream alignment is unknown after skips, so (1) is the primary
test; (2) is reported as a weaker check using o = ptr_end of window k-1.
Baseline: the argmax-register distribution of the 2000-seed null (how often LP1_REAL wins by chance; LP1_REAL is the panel's modal winner for English-ish junk).
KILL: argmax wanders (LP1_REAL in <= 50% of segments, or segment pmax not above the L=120 null median+1) -> noise. A true English-like key should hold one register in >=75% of segments with each segment z > ~3.

## Verifier C - the decoded text
Best decodes for L=120/240/262/729 as letters (R32 transliteration) with per-register z, IoC*N, mds, h2, zlib vs the null medians; plus a calibration PLANT in `decode_text.md`:
the same bash seed as key, enc_pair (supp 0.83) over held-out EN_MODERN text (corpora from common.corpora()) AND over held-out LP1 page text from testhalves12, decoded with the identical pipeline.
Positive control PASS = plant decode recovered >=0.85 and its pmax clears the 99.9% null quantile at each L and grows with L. The plant's decode must read as English; the candidate's must not read as any language to be escalated.
KILL: candidate decode has no word-level structure (no recurring multi-rune words, IoC/mds within the null's central 95%).

## Verdict rule
NOISE if A+B+C all kill. INCONCLUSIVE if the control fails. ESCALATE -> flagged-for-oracle only if all four escalate conditions above hold; never "solved/confirmed".

## Aiming test (short)
Q1 recognizer = the plant. Q2 prior = recurring near-miss across R32/R33/R35 (a selection effect, not evidence). Q3 space = single seed, bounded. Q4 conditionals: key space = this seed under bash 4.2 `%29` only;
decoder = keyskip1/2/free beam_v3 panel_max; adjudicator = 9/12 register trigram panel. Q5 abandon at: reproduction fails, or verifier A shows 7.068 below its own 99% null quantile at L=120 for >=1% of random seeds AND L-curve flat.
