# PREREG - R37 C2-U4 prime line sums as a language-free recognizer

Dated 2026-10-30. Written BEFORE any statistic was computed on the solved pages.

## Statistic
For a page, take its physical lines = the rune-bearing lines of the page block in
`data/scream314_lp.md` as parsed by `src/lp/corpus.py` (non-rune hex-only lines on 73.jpg dropped;
numerals and tabs on 05.jpg ignored, only runes counted). Line sum = sum over the runes of the line of
the Gematria Primus prime value (`src/lp/gematria.py`, F=2 ... EA=109). A line PASSES if its sum is prime.
Page statistic f = passing lines / lines. Secondary: all-lines-prime indicator A.
Six pages: 01 A WARNING, 05 SOME WISDOM, 06 KOAN master/student, 03 WELCOME, 14 KOAN circumference, 73 AN-END.
Plaintext side: the decoded runes (documented method; interrupters get no plaintext rune, contribute 0).
Ciphertext side: the undecoded runes in the same lines. Decodes are verified against SOLVED-PAGES.json /
validate.py expected words before use.

## Nulls (10,000 each, seed fixed)
(a) shuffle null: permute the page's runes (of the side being measured) across the page keeping line lengths.
(b) random null: i.i.d. uniform random rune strings (29 runes) with the same line lengths.
Pooled: sum of passing lines over six pages / total lines, nulls summed with the same draw index.

## Test
One-sided p = (1 + #{null f >= observed f}) / (1 + 10000), per page and pooled, for each null.

## Decision rule
SEPARATION (language-free recognizer candidate) iff pooled p(shuffle) < 0.01 AND >= 4 of 6 pages with
individual p(shuffle) < 0.05, on the PLAINTEXT side. Otherwise NO-SEPARATION and the top-row (SWEEPROW
`plinefrac`) scoring is NOT run. Ciphertext-side result is reported only to distinguish "plaintext has
prime sums" from "ciphertext does"; it does not change the verdict.

## Positive control (run first)
Construct for each page lines of the page's lengths whose sums are prime by construction (random runes,
last rune(s) resampled until prime). Must score f=1.0 and pooled p < 1e-4; A WARNING-length and the
pooled set p < 1e-4 required; small pages (5 lines) may be limited by the 1/10001 floor and chance.

## Confounds reported
Line-length distribution, mean line sum, empirical null pass rate vs 1/ln(S) and the parity-corrected
2/ln(S) (all rune primes except F are odd, so sum parity is set by line length), and an English-text
control: pass rate of random English KJV windows of the same rune lengths mapped to GP.

## Stats of record
Existing claim (scream314_lp.md:122-136): A WARNING 9/9 lines prime (as listed 9 text lines, title excluded),
SOME WISDOM 4/5, WELCOME 3/5 - this is a post-hoc observation, so the prior is NOT evidence; the preregistered
all-six-pages test above is the measurement. Title lines are included in the primary statistic (all
physical rune lines); the author's title-excluded variants are reported as secondary only.
