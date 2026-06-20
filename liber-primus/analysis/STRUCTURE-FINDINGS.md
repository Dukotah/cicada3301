# Structural probes — interrupter, boundaries, per-page (2026-06-20)

Three novel internal analyses on the 55 unsolved LP2 pages. Reproduce:
`python analysis/structure_analysis.py`. All negative for a crack, but each is a
genuine contribution (more ruled out + one real structural insight).

## 1. Interrupter (ᚠ) is not a hidden channel
- **F-count per page** (onion7 0–55, for OEIS/sequence-checking by others):
  `14,13,7,7,7,8,3,1,8,11,7,14,12,12,2,7,10,12,10,12,7,8,6,7,12,9,9,11,12,8,8,9,4,9,6,4,8,6,3,4,10,11,14,17,12,8,9,9,14,2,0,4,10,5,3,3`
  (total 458, mean 8.18, range 0–17). **Not** the primes, **not** Fibonacci.
- **Gaps between F runes**: no sharp peak (top lengths 3,2,6,7,4,5; mean 25.3).
- **F/not-F mask as a bitstream → ASCII**: 0/56 pages decode to mostly-printable
  text. The interrupter placement does not hide ASCII.
- Conclusion: the ᚠ interrupter behaves as a cipher null/skip, not a carrier of
  the key or method.

## 2. The keystream is CONTINUOUS across the whole book (no boundary reset)
Doublet rate (a proxy for "is the no-repeat rule active here") by what separates
each adjacent rune pair:

| separator | pairs | doublet rate |
|---|---|---|
| none (within word) | 9640 | 0.0062 |
| word `-` | 2589 | 0.0081 |
| clause `.` | 133 | 0.0075 |
| line `/` | 534 | 0.0075 |
| **page `%`** | 54 | **0.0000** |

Random would be ~0.0345. The no-repeat suppression holds across **every** boundary
type — including page joins (the last rune of a page is never equal to the first
rune of the next). So the keystream/no-repeat constraint is applied to the **entire
concatenated book as one continuous stream**, not reset per page/paragraph/line.
- Implication for solvers: there is **no boundary where the keystream restarts**,
  so the hoped-for "shorter effective key per page" / in-depth-at-boundaries attack
  does **not** apply. This tightens the one-time-pad-class characterization.

## 3. No outlier pages
IoC_norm across the 55 pages: mean 0.969, sd 0.136 (English-class ~1.70). The
highest is page 55 at 1.099 — but it is the shortest page (76 runes), i.e.
small-sample noise, not structure. **No page deviates from the flat OTP profile**,
so there is no "weak page" that is easier to attack than the rest.

## Net
The interrupter carries no recoverable side-channel; the keystream is one
continuous no-repeat stream over the whole book; and all pages are uniformly flat.
Consistent with — and strengthening — the one-time-pad-class verdict.
