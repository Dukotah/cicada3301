# ORACLE-PENDING — lane S1, the 19 weak flags

_Written 2026-11-12 by the lane coordinator per `HUMAN-ORACLE.md` section 2 (a coordinator who cannot open an issue leaves the
bundle in place). Adjudicator: the repo owner. **Recommended adjudication: NOISE-CROSSER, 19 of 19.**_

## What crossed

The sweep of all 2^32 Perl `rand` seeds (four modes each, 1.72e10 seed-mode pairs) left 19 pairs with a full-page index of
coincidence (x 29) between 1.402 and 1.433 on page 0. The registered threshold is 1.40; the weakest of 432 calibration plants
scored 1.614; no pair reached 1.50. The PREREG addendum, written before any output was read, predicted a few such values from
wrong keys alone and called them weak flags. Its crude decay rule marks 5 of the 19 as null-consistent; the other 14 are owed
this note.

## Why they are noise (all three checks were chosen after the flags were seen, each has a control)

1. **The held-out page.** The sweep selected on page 0 only. Decoding page 1 from the key position where page 0 ended:
   two-page plants score 1.797 or more on page 1; **every flag scores between 1.068 and 1.175** (mean 1.128), which is what a random key gives. `heldout_page1.py`.
2. **The back half of page 0** (runes 120-261 alone): plants 1.686 or more; flags at most 1.425. `adjudicate_flags.py`.
3. **Reading.** Each decode solved as a simple substitution of English (the adjudicator is blind to how the plaintext is labelled, so this is what reading a flag means): relabelled English plants come back as readable English and score -5.41 or better; wrong keys score -7.08 or worse; the flags score -6.48 or worse.
4. **Tail shape.** Pairs at or above each level of the full-page statistic: 1.30: 5,647, 1.32: 1,813, 1.34: 605, 1.36: 182, 1.38: 49, 1.40: 19, 1.42: 4, 1.44: 0. A smooth geometric decay with no isolated point; lane S2 shows the same curve at 1/24 the height.

## The rows

| seed | mode | IoC x 29, L=120 | IoC x 29, page 0 | page 1 (held out) | back half | reading score |
|---|---|---|---|---|---|---|
| 2206085107 | s=-1 q=2 | 1.527 | 1.433 | 1.140 | 1.286 | -6.85 |
| 2298247635 | s=-1 q=1 | 1.491 | 1.427 | 1.089 | 1.425 | -6.81 |
| 2264892615 | s=-1 q=2 | 1.629 | 1.427 | 1.125 | 1.243 | -6.87 |
| 2669644562 | s=-1 q=2 | 1.637 | 1.426 | 1.083 | 1.272 | -6.86 |
| 2254161132 | s=-1 q=2 | 1.511 | 1.419 | 1.119 | 1.330 | -7.02 |
| 3260260163 | s=+1 q=2 | 1.511 | 1.415 | 1.144 | 1.306 | -6.87 |
| 4262316153 | s=-1 q=2 | 1.511 | 1.415 | 1.144 | 1.306 | -6.91 |
| 2007729473 | s=+1 q=2 | 1.519 | 1.413 | 1.103 | 1.347 | -7.00 |
| 1198237473 | s=+1 q=2 | 1.511 | 1.410 | 1.140 | 1.243 | -6.77 |
| 1344471619 | s=+1 q=2 | 1.738 | 1.409 | 1.108 | 1.275 | -7.06 |
| 142997270 | s=+1 q=2 | 1.515 | 1.407 | 1.157 | 1.388 | -6.89 |
| 4193912973 | s=+1 q=1 | 1.515 | 1.406 | 1.151 | 1.333 | -6.95 |
| 2205610001 | s=+1 q=2 | 1.442 | 1.405 | 1.141 | 1.370 | -6.67 |
| 517150155 | s=-1 q=1 | 1.690 | 1.405 | 1.068 | 1.298 | -6.94 |
| 2948922096 | s=+1 q=2 | 1.458 | 1.404 | 1.143 | 1.289 | -7.07 |
| 3767868758 | s=+1 q=2 | 1.454 | 1.404 | 1.125 | 1.318 | -6.48 |
| 3037903454 | s=-1 q=2 | 1.572 | 1.403 | 1.175 | 1.292 | -6.80 |
| 3217961791 | s=+1 q=2 | 1.446 | 1.403 | 1.144 | 1.295 | -7.08 |
| 794670246 | s=-1 q=2 | 1.543 | 1.402 | 1.128 | 1.243 | -7.04 |

Reproduce any row: `perl -e 'srand(SEED); print join(" ", map { int(rand(29)) } 1..700)'` gives the keystream; `s=+1` means
`decode = C - K`, `s=-1` means `C + K`; `q` is the number of draws a rejection consumes. Page-0 decodes in Gematria order are in
`results.json` (`flagged[].decode_gematria_order`), the substitution readings in `flags_adjudication.json`.

## What the owner is asked to do

Glance at the readings in `flags_adjudication.json` and record `NOISE-CROSSER` (or not) here. Nothing downstream waits on it:
no ledger row moves to positive on these rows under any outcome of the checks above.
