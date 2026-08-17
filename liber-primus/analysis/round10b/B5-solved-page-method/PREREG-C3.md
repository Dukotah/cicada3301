# Round 10B / Lane B5 — PRE-REGISTRATION #2 (candidate C3)
## "the word is the map, its SACRED NUMBERS are the direction"

Written **before** the C3 sweep was run. `PREREG.md` (candidate C1 = composed
keyword×generator, and C2 = deep generator start-offset) is **not modified**; its
thresholds stand as written and its verdicts are recorded in `RESULTS.md`.

Trust anchor re-confirmed 2026-08-17: `python tests/validate.py` →
*ALL VALIDATIONS PASSED* (01.jpg −4.48, 05.jpg −4.98, 06.jpg −4.13,
03.jpg/DIVINITY −4.34, 14.jpg/FIRFUMFERENFE −4.24).

---

## 1. Why this candidate, from the continuity reconstruction

Two facts from the escalation table in `PREREG.md` §1:

1. **p14 proves the author transforms the SPELLING of a key by a book-internal
   rule** — the key is `FIRFUMFERENFE`, i.e. CIRCUMFERENCE respelled in the
   author's own C→F orthography. The solver's new work at that stage was not
   guessing a harder word; it was realising the word is *written in the book's
   own system* before it becomes numbers.
2. **p56 proves the author's terminal move is to run a SACRED NUMERIC MAP over a
   symbol sequence** — φ(pᵢ) = pᵢ − 1 mod 29 over the primes, licensed by p05's
   "the primes are sacred and the totient function is sacred".

Every keyword sweep ever run — here (`campaign18_skip/RUN-keywords-full.log`,
~620 words × sign × Atbash × offset, best −6.021) and publicly (relikd,
mortlach, LiberPrimusSolver) — turns a key word into numbers by exactly one map:
**the rune's INDEX 0–28**. But the Gematria Primus assigns each rune *two*
numbers, and the book sanctifies the other one. C3 asks the obvious continuity
question nobody has asked: **what if the key word's shifts are its PRIMES, or
φ of its primes, rather than its indices?**

This is also the most literal available reading of the signed 2016 clause
"their **numbers** are the direction": the word chooses the map, the *numeric
valuation* of that word chooses the shift.

Novelty argument (why this is not a re-dig): a valuation map π applied to the key
symbols is a **non-affine permutation** of the key alphabet (π(i) = pᵢ mod 29 is
not i+c or −i+c), so the resulting keystream is not reachable by the
sign/Atbash/offset knobs of any prior keyword sweep. It is equivalent to
index-keying with the word π(W), which is a rune string that is *not a word* and
therefore appears in no wordlist. Separately, `ELIMINATION-LEDGER.md` §iter-8
killed alphabet-RELABELING of the *ciphertext* (monoalphabetic hill-climb,
F = −6.026); it says nothing about the valuation of the *key*.

## 2. Hypothesis (H-C3)

```
K[j] = s · M( W[(j + phase) mod L] )   mod 29 ,     p[i] = ( c[i] + K[key_ptr(i)] ) mod 29
```

- `W` = a themed / LP-lexicon word (`data/keys/thematic.txt` + `words_expanded.txt`
  + `i7_constants/priority_seeds.json` → 600+ words);
- `M` ∈ {`index` (anchor, known null), `prime` = pᵢ mod 29,
  `phi_prime` = (pᵢ−1) mod 29 (**the p56 sacred map**),
  `atbash` = 28−i (affine anchor), `cumprime` = running Σp mod 29};
- `s` ∈ {+1, −1}; `phase` ∈ 0..min(L,12)−1;
- `key_ptr` advances under the **validated skip-tolerant beam**
  (`campaign18_skip`: rigid −7.24/8.5% vs beam −4.15/100%).

## 3. Controls (mandatory)

- **PC-A** — the `index` map must re-find **DIVINITY** on 03.jpg and
  **FIRFUMFERENFE** on 14.jpg as the top word of the full list at ≥ −5.0
  (inherited from `composed_key.pc_a`, re-run).
- **PC-B** — plant real English enciphered under `M = phi_prime` valuation of
  **CIRCUMFERENCE**, with the 0.83 doublet key-skip filter. Requirement: the
  sweep recovers word **and** map at ≥ −5.0, while the rigid decode with the
  correct key scores < −6.0. Failure ⇒ ABORT (instrument blind to its own signal).
- **Null** — identical sweep on length-matched shuffles of the same real pages.

## 4. Pre-registered decision rule (identical numbers to PREREG.md §4)

| verdict | condition |
|---|---|
| **BREAK** | real best ≥ **−5.2** and readable English and reproducible under `tests/validate.py` conventions |
| **POSITIVE (lead)** | real best ≥ **−5.5** and exceeds shuffled-null max by ≥ **0.5** |
| **NEGATIVE** | real best < −5.5, or real best ≤ null max + 0.3 |
| **ABORT** | either positive control fails |

## 5. Scope declared in advance

Pages 0, 1, 2, 5, 20, 54 + 6 length-matched shuffles, one run. A negative is a
negative for *sacred-valuation single-word keys on these pages*, not for all
valuations; `--pages` makes it resumable over the other 49.
