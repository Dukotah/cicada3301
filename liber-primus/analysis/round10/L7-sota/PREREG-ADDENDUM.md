# L7-sota — PRE-REGISTRATION ADDENDUM (isomorph statistic)

Written **after** the survey identified a capability gap, and **before** the test below was run.
Marked as an addendum, not back-dated into PREREG.md.

## Why

The survey's H1d test found that `micheloosterhof/aldegonde` — forked into the `cicada-solvers`
org on **2026-08-10**, the freshest external artifact in the whole sweep — ships
`stats/isomorphs.py`, and a repo-wide grep for `isomorph` in this repository returns
**zero hits across all .py and .md files**. So the community holds a statistic this repo has
never computed. A capability gap only matters if exercising it produces something, so I exercise
it here rather than merely reporting the gap.

## Hypothesis

H3: LP2 (unsolved pages 0–54, 12,956 runes) contains an excess of **isomorphs** — pairs of
equal-length windows with an identical internal repeat-pattern but different symbols — relative
to a symbol-shuffled null.

Rationale for why this is not already covered: the repo's corpus-wide coincidence scan (Campaign
XIV P1) tests for *identical* substrings at a lag; isomorphs are invariant under an arbitrary
per-window relabelling, so they survive a keystream that is *constant-within-window but different
between windows*. Under a true OTP the isomorph count must sit at the random null.

Note the anti-repeat filter is a confound in the *opposite* direction: LP2 suppresses adjacent
equal runes, which removes patterns containing adjacent repeats and so **depresses** the
isomorph count. Therefore the null control is run two ways (see below) so a deficit cannot be
mistaken for a signal and an excess cannot be explained away.

## Exact test

For window length L in {6, 8, 10, 12}: slide over the corpus; normalise each window to its
first-occurrence pattern (e.g. `XYXZZ` form); discard windows whose pattern is all-distinct
(trivial, carries no information); count the number of **isomorph pairs** = sum over patterns of
C(count, 2). Report the total and the longest non-trivial pattern shared by ≥2 windows.

## Null controls

- **NC-A (plain shuffle):** 200 uniform random permutations of the corpus symbols.
- **NC-B (anti-repeat-matched shuffle):** 200 permutations rejection-sampled/repaired to the
  measured adjacent-equal rate of 0.66%, so the null carries the same doublet deficit the real
  text does. This is the control that makes a deficit interpretable.

## Pass / fail threshold (fixed before running)

- **HIT** = isomorph-pair count z ≥ +4.0 against **NC-B** at any L, **or** a non-trivial shared
  pattern of length ≥ 14 present in LP2 and absent from all 200 NC-B nulls.
- **NULL** = |z| < 4.0 at every L against NC-B (a negative z against NC-A alone is expected and
  is not a finding — it is the known anti-repeat filter).
- Anything in 4.0 > |z| ≥ 3.0 is reported as **inconclusive-but-logged**, not as a finding.
