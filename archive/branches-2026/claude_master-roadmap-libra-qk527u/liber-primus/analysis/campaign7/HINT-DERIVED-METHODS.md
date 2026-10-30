# Hint-Derived Methods — did Cicada tell us the approach?

_2026-07-10. Premise (owner's): Cicada's puzzles were self-teaching — every solved
stage taught the technique needed later. So enumerate every **verified** hint, derive
its operational method classes, and audit each against our eliminated list. Anything
not already covered gets run._

## 1. The verified hint corpus (primary sources only)

| # | Hint | Source | Verified |
|---|------|--------|----------|
| H1 | "DO NOT EDIT OR CHANGE THIS BOOK… **EITHER THE WORDS OR THEIR NUMBERS**, FOR ALL IS SACRED" | A WARNING (solved LP page) | ✔ decrypts from canon |
| H2 | "THE **PRIMES** ARE SACRED. THE **TOTIENT FUNCTION** IS SACRED. ALL THINGS SHOULD BE ENCRYPTED" | SOME WISDOM (solved) | ✔ |
| H3 | The SOME WISDOM **magic square mixes numbers and words** — the words' gematria sums complete the square (SHADOWS=341, AETHEREAL=366, …; rows sum 1033) | solved page | ✔ |
| H4 | Every solved page's method was **taught by adjacent content**: koan → shift-3 ("circumference"), WELCOME → Vigenère key DIVINITY + interrupters, AN END → φ(prime)−1 stream | solve history | ✔ |
| H5 | "Liber Primus is the way. Its words are the map, their meaning is the road, and **their numbers are the direction**." | 2016 message, GPG-verified 7A35090F (see KEY-HINT-RESEARCH.md §5) | ✔ signature checked |
| H6 | The 2014 interactive phase demanded solvers "post the **three magic squares**" — matrices are first-class objects to Cicada; the book itself contains **three matrices** (5×5 trace-1033, 5×5 trace-3301, 4×4 trace-10673) | scream314 2014 catalog | ✔ |
| H7 | "Work alone." / "Command your own self" — self-reference motif | 2014 onion + solved pages | ✔ |

## 2. Hint → method class → coverage audit

| Method class the hint implies | Status in our record |
|---|---|
| **Thematic keyword Vigenère** (H4: "the hints name the key") | **Mechanically exhausted, keyword-independent:** per-page exhaustive L1–4 + interrupter beam and hill-climb L4–12 covered **every possible keyword** of those lengths — known or unknown. Even if a hint names the "right" word (INSTAR, SACRED, EMERGENCE…), it was already tried. This kills the entire "find the magic keyword" genre. |
| **Prime/totient/φ keystreams** (H2, H5) | Exhausted with offset search (Campaigns I–II); history-dependent prime variants (epoch-5 `seek_primes.py`) null. |
| **Self-referential running keys** (H7): solved text as key, page-on-page | Exhausted (Latin and rune space). |
| **Gematria word-sums as key material** (H1+H3+H5: words↔numbers interchangeable, "numbers are the direction") | **NOT previously tested** at word granularity → `wordsum_selfkey.py` (this doc, §3). |
| **The book's own matrices as Hill keys** (H3+H6) | Generic Hill 2×2 exhaustive + 3×3 sampled were null, but the **actual three book matrices (5×5, 5×5, 4×4) were never run in our rig with quadgram scoring**. r4nd0m ran them (segment-split, one direction, no automated scoring, no published result) → `hill5_magic.py` (§3). |
| **Gematria-sum book code** (numbers index into a text) | Ill-posed without the target text; the bounded variants (index into the rune corpus itself) were null (`token_as_index.py`). Open only in unbounded form. |

## 3. The two new hint-derived probes (this session)

1. **`hill5_magic.py`** — the three matrices Cicada printed in the book (+ r4nd0m's
   φ-substituted variants), applied as Hill ciphers mod 29: each matrix, its
   transpose, its inverse, and inverse-transpose, per page + whole book, with
   quadgram scoring. First rigorous, scored, recorded run of the book's own matrices.
2. **`wordsum_selfkey.py`** — "their numbers are the direction" operationalized:
   the gematria-prime-sum of each word drives the shift of the next
   (ciphertext-fed, plaintext-fed, cumulative, φ-of-sum, and per-rune prime autokey
   variants), ± sign, ± atbash, per page.

Results: see `*_results.json` + the table in `CAMPAIGN-VII-FINDINGS.md`.

## 4. The honest structural counter-argument

The doublet fingerprint constrains ALL of these: any **deterministic, position-local**
scheme derived from public material (matrices, word sums, primes) is a fixed keystream
— and the observed uniform *soft* doublet suppression (~20% residual) is the signature
of a **random filtered stream**, not a deterministic derived one (a deterministic rule
gives a *hard* pattern, not a soft stochastic one). So the hints, if they describe the
LP2 mechanism at all, most plausibly describe **how to use a key that was never
published** — which is consistent with every negative in this archive. We run the
hint-derived methods anyway, because "consistent with" is not "proven," and recording
the negative is the point.
