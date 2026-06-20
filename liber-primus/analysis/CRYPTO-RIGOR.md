# Final crypto-rigor probes (2026-06-20) — closing the last untried doors

Three structural attacks that earlier rounds only argued "by logic" or never ran.
Reproduce: `python analysis/crypto_rigor.py` (55 unsolved LP2 pages, 12956 runes).

## A. F-rune run-length histogram — block/permutation decode UNSUPPORTED
If the cipher encoded fixed-length blocks or permutations delimited by the ᚠ
interrupter (the "Lehmer/factoradic/no-repeat-block" family), the gaps between F
runes would peak sharply at one length. They do not: 403 gaps, mean 25.3, median
19, spread 2–140, **modal-gap share only 0.055** (no peak). The combinatorial
block-decode family is not supported by the data. (This is the cheap gate the
novel-attack recon flagged; it kills "Idea 3".)

## B. Transposition-validity — the delta=0 hole is STRUCTURAL, not a reading artifact
The completeness-critic's key doubt: maybe the "no equal neighbours" fingerprint
(doublet 0.66%, delta=0 hole) only exists because we read runes in file order; a
transposition-first cipher would make our adjacency fake. Test: de-transpose at
every columnar width 2–40 and re-measure the doublet rate.

- Native (file order) doublet rate = **0.0067** (suppressed).
- Every transposition width **restores** doublets toward random (~0.0345); the
  lowest any width reaches is 0.0294 (w=11).
- File order is the **unique global minimum.** The suppression is specific to
  file-order adjacency ⇒ **reading order is native and the no-repeat rule is a
  real generative constraint**, not an artifact. The fingerprint is trustworthy.

## C. No-repeat / collision inversion decodes — no language
Parameter-free decodes that exploit c[i]≠c[i-1], scored by normalized IoC
(flat = 1.00; English-class ≈ 1.70):

| decode | IoC_norm |
|---|---|
| rank-of-c[i] in the 28 allowed symbols | 1.037 |
| first-difference (control) | 1.024 |
| cumulative-sum / integral (control) | 1.000 |
| collision-unbump (+1) | 1.000 |
| raw ciphertext (reference) | 1.000 |

Nothing rises toward language. The delta≠0 family yields no plaintext.

## Net
The last untried structural families are now run and closed, and the no-repeat
fingerprint is confirmed structural. Combined with the prior exhaustive key/keystream
search and the perfect-IoC-flatness argument, the unsolved LP2 pages are
**one-time-pad-class**: a full-length keystream with a deliberate no-repeat rule,
information-theoretically unsolvable from ciphertext alone without the key.
