# PREREG ADDENDUM E — null-control correction + one added reading

Written after the first full pass and **before** re-running M2/M4 or running M9.
No threshold anywhere is changed; the first-pass numbers stay in the record.

## E1 — NULL-A is degenerate for length-derived readings (correction)

NULL-A shuffles rune **content** while holding word-boundary positions fixed. Any
reading that depends only on word **lengths** — M2's `len mod 26/29` family, M4's
`len` pointer family — is therefore **invariant** under NULL-A, which produced
`sd = 0` and a meaningless `z = 0.00` in the first pass.

Correction: add **NULL-B = permutation of the word order** (lengths preserved,
sequence destroyed) and pool it with NULL-A, 8 draws each. This is the correct null
for an "order carries the message" claim. Thresholds unchanged
(rune ≥ −13.5 & z ≥ +5; letters ≥ −6.0 & z ≥ +5; M4 ≥ −5.5 & z ≥ +5).

M4 is additionally reported **per pointer family**, with the count of distinct
pointers, because the `len` family can only ever address 14 of the 752 book words
and its high raw `score_norm` is an artifact of repeating a handful of real English
words, not a signal.

## E2 — M9, added reading: word numbers as direct ADDRESSES

"Its words are the map" also supports **direct addressing** rather than stepping:
each word's number names a location in the book, and the located symbols are the
message. Round 9 DIRECTION covered sequential walks (families A/B/C) and predicate
sieves (family D); direct word-number → absolute-position addressing is in neither,
and is at word granularity besides.

Ten families: `S_prime`, `S_idx`, their cumulative sums, `S + word-start-offset`,
`len × word-index`, addressing either the 12,956-rune stream or the 2,928
word-initial stream; × 29 shifts.
- **Threshold: identical to M1/M5 — rune-4-gram ≥ −13.5 AND z ≥ +5** vs NULL-A ∪ NULL-B.
  No new threshold is invented for it.
