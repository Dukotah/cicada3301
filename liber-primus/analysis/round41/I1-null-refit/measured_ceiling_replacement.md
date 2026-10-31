# Replacement text for MEASURED-CEILING.md section 1 (NOT applied by the lane; coordinator applies, files the ledger row, then runs check_ceiling.py)

In the 'Observed wrong-key nulls' row of section 1, replace the Measured-limits cell's clause beginning `X1/Round 40: the stored survivors of the sweeps score higher ...` (through `... (mean 1.1, sd 0.5)`) with:

> X1/Round 40 found that the 'actual-N' bars quoted from this null were fitted on shuffled-LP2 wrong keys with no prefilter, a population less English-like than the survivors the sweeps decode (L=120 median 2.33 vs 2.80). Round 41 I1 refit the bar on the population it is applied to (wrong-key seeds from six generator families, real LP2 head, pf_v4_12 survivors, beam_v3 panel_max under panel-R36; 40,482 distinct survivors at L=120, 5,194 at L=240): the survivor median is 2.809 / 2.828 (keyskip1 / keyskip2) against the real sweeps' 2.80 / 2.82, and the L=120 bar of record is 9.6325 / 9.6549 at N=131,786 and 10.4645 / 10.4856 at N=1e6 (stored null12: 8.365 / 8.275 at N=131,786 and 9.102 / 8.999 at N=1e6); at L=240 the N=1e6 bar of record is 10.0529 / 10.3539. The Gumbel tail is conservative (the real sweeps' maxima lie 0.7-2.8 SE below it), the bar of record at L=120 is the higher of the refit and the pooled real-sweep survivor POT line, and the 1 % family-wise level at N~1.3e5 is not empirically measurable. The planted-key gate (480 plants, bar of record at N=1e6) fails in two register x relation cells (LATIN keyskip1, OE keyskip2, 18/20) through the pf_v4_12 screen, not the bar (470/470 screen-passers clear it). All 34 best rows of Rounds 36-40 stay below the bar of record at their actual N and at N=1e6 (smallest gap 0.9, the withdrawn KDF flag); no stored verdict moves. Direct (non-key) families need the page-/region-scale matched null (benchmark/bars_matched.py), not this bar; N=1e6 bars are tail extrapolations.

and add `[[R41-I1-NULL-REFIT-SURVIVOR12]]` to that row's Rows cell. Add these pins to the pin block at the bottom of the page (each is checked against the row JSON):

```
<!-- pin: R41-I1-NULL-REFIT-SURVIVOR12 | 9.6325 -->
<!-- pin: R41-I1-NULL-REFIT-SURVIVOR12 | 9.6549 -->
<!-- pin: R41-I1-NULL-REFIT-SURVIVOR12 | 10.4645 -->
<!-- pin: R41-I1-NULL-REFIT-SURVIVOR12 | 10.4856 -->
<!-- pin: R41-I1-NULL-REFIT-SURVIVOR12 | 10.0529 -->
<!-- pin: R41-I1-NULL-REFIT-SURVIVOR12 | 10.3539 -->
<!-- pin: R41-I1-NULL-REFIT-SURVIVOR12 | 40,482 -->
<!-- pin: R41-I1-NULL-REFIT-SURVIVOR12 | 5,194 -->
<!-- pin: R41-I1-NULL-REFIT-SURVIVOR12 | 2.809 -->
<!-- pin: R41-I1-NULL-REFIT-SURVIVOR12 | 480 plants -->
<!-- pin: R41-I1-NULL-REFIT-SURVIVOR12 | 470/480 -->
<!-- pin: R41-I1-NULL-REFIT-SURVIVOR12 | 7.435 -->
```

Row to file in LEDGER.json: `ledger.json` (id `R41-I1-NULL-REFIT-SURVIVOR12`). Notes to apply: `ledger_patches.json`. The 'N=1e6 bar is the effective one' sentence is withdrawn: the bar of record at the sweep's actual N is now calibrated, and the N=1e6 bar of record is 10.4645 / 10.4856.
