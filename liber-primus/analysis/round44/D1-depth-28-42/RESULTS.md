# RESULTS — Round 44 lane D1: pages 28 and 42 are not two English texts in depth

_Run 2026-11-12, after `PREREG.md` (same day, written first). Reproduce: `python3 run_d1.py` (about
ten minutes; writes `results.json`). Nothing in the pre-registration was changed after the run._

## Verdict

**NEGATIVE in all three cells, with the control passed in each.** The joint two-plaintext decoder
reads planted English depth pairs at 70-94 % of runes and scores them far above every null. The real
pair scores like a null.

| cell | plants: recovery min / median / max | plants at >= 0.70 | S plants (min) | S nulls (mean +- sd, max of 40) | S real | verdict |
|---|---|---|---|---|---|---|
| G-LW letter-wise, Gematria order | 0.770 / 0.829 / 0.922 | 12/12 | -3.974 | -5.276 +- 0.072, -5.127 | **-5.267** (z = +0.12) | NEGATIVE |
| G-MG multigraph, Gematria order | 0.704 / 0.786 / 0.914 | 12/12 | -4.103 | -5.162 +- 0.070, -4.993 | **-5.159** (z = +0.04) | NEGATIVE |
| A-LW letter-wise, alphabet order | 0.768 / 0.844 / 0.942 | 12/12 | -4.014 | -5.251 +- 0.069, -5.030 | **-5.138** (z = +1.65) | NEGATIVE |

`S` is the joint log-probability of the best path in nats per aligned position. The gap between the
worst plant and the best null is 16 to 18 null standard deviations in every cell, so a true depth pair
in any of the three encodings would not have been missed. The decoded "texts" for the real pair are
word salad (`results.json`, fields `textA` / `textB`).

## What this does and does not settle

The anomaly that motivated the lane is real as a measurement and stays unexplained:
`D_i = (p28_i - p42_i) mod 29` has chi2 = 74.1 on 28 df, 65.2 of it in the symmetric half, at exact
alignment only (`../A0-fresh-eyes-audit/depth_pairs.py`). What is now excluded, at high power, is the
natural reading of it.

Three conditionals, as pre-registered:

1. **Key space:** none. The test is key-free. It assumes the same key values at the same page offsets
   on both pages, with no key-consuming desync on either.
2. **Transition model:** additive combination; plants carried 5 % overwritten positions.
3. **Register:** English only, in three encodings. A different numbering of the plaintext symbols, a
   non-English text, or a relation that is not depth at all is **not** covered.

Reopens if: a numbering other than the three is proposed (the difference stream's own spectrum is
the constraint: strong real components at frequencies 1, 5, 10, 11, 12 of 29, see
`depth_pairs.json`); or the same statistic is found on a second page pair; or the page images show
that pages 28 and 42 share something the transcription does not carry.

Family-wise, the motivating statistic is about 0.006 over the 1,326 aligned pairs of pages with at
least 100 runes, on the statistic fixed before looking at the split. It may be chance. It is filed so
that the next reader does not have to rediscover it, and so that nobody anchors a lane on it without
knowing the plain depth reading is already dead.
