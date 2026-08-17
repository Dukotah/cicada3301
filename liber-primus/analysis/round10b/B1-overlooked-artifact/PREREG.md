# Lane B1 — PRE-REGISTRATION (written before any sweep was run)

**Lane:** B1 — "The overlooked variable." Test the owner's thesis head-on:
*a key-shaped string released by Cicada 3301 between 2012 and 2016, which this repo has
never fed to an LP2 decode, is the key — under the author's own demonstrated
hand-scale cipher toolkit.*

**Instrument:** PA-3's artifact inventory (`../PA-3/ARTIFACT-INVENTORY.md`) §G gap list,
Tiers 2 and 3 (published prose / published number sequences never fed), plus every
key-shaped alphabetic string recoverable from the locally-held verbatim scream314 archive
`analysis/armada_osint/artifacts/raw/{2012..2017}.md`.

## H1 (primary)
There exists an artifact-derived string S (from the 2012–2016 released material, absent
from every previously-swept key corpus) such that at least one unsolved LP2 page 0–54
decrypts to readable English under one of the author's demonstrated operations:
Vigenère(S) with sign ±1, optional Atbash pre-stage, optional key-phase rotation, with and
without the ᚠ-interrupter beam.

## H2 (secondary)
The same for an artifact-derived **numeric** string used as a repeating mod-29 additive
keystream (poster access codes, Dataset/Offset triplets, GPS coordinate digits, SSSS share
hex, the 2012 book-code number list, the 2013 boot/tweet numbers).

## H3 (audit, no compute)
The repo's kill on "external cribs as additive key" (Round 4) and its kill on "any keytext"
(Round 7) are about **different objects**. Determine precisely which kill binds which, and
whether a class was declared dead by an argument that does not cover it.

## Pre-registered numeric thresholds — fixed before running

Scale in use: `attack.py` / `lp.score.Quadgram.score_norm`, **page-scale**.
Real English on this scale ≈ −4.0…−4.4 (measured on the 5 solved pages: −4.13…−4.98).
Gibberish ≈ −7.4. Repo confirm threshold = **−5.2**.

| Gate | Rule |
|---|---|
| **PASS / BREAK** | any (page, key, method) with `score_norm > −5.2` **and** the plaintext contains ≥3 English words ≥4 letters **and** it re-derives under `tests/validate.py` conventions |
| **SIGNAL, follow up** | `score_norm > −5.5` and strictly above the null-control max for the same sweep |
| **FAIL / NEGATIVE** | best real score ≤ null-control max, or ≤ −5.5 with no readable output |

Multiple-comparisons control: the **null control** (identical key set, identical method
grid, run against per-page rune-shuffled LP2) sets the empirical false-positive ceiling.
A real-sweep best that does not exceed the null max is a negative regardless of its
absolute value.

## Controls — both mandatory, run before any negative is trusted

**PC-A (rig-level, real Cicada ciphertext).** `python tests/validate.py` must reproduce all
five solved pages, including `03.jpg` = WELCOME via Vigenère **DIVINITY** + interrupters and
`14.jpg` via **FIRFUMFERENFE**. Recorded verbatim in RESULTS.md.

**PC-B (harness-level, real Cicada ciphertext).** DIVINITY and FIRFUMFERENFE are inserted
into the B1 key list and the *B1 sweep itself* is pointed at the solved pages 03.jpg and
14.jpg. The sweep must rank the true key first and clear −5.2. If it does not, every B1
negative is void.

**PC-C (planted signal, artifact key).** Take a held English plaintext, encipher it under an
artifact-derived keyword (`THEKEYISALLAROUNDYOU`, 2013 boot screen) exactly as the author
enciphered page 03 (Vigenère, sign −1, F-runes inserted as interrupters), splice it in as a
synthetic page, and confirm the B1 sweep recovers that keyword above −5.2.

**NULL.** Per-page Fisher–Yates shuffle of the real LP2 rune indices (preserves each page's
exact rune multiset and length, destroys order), same key set, same method grid.

## What would falsify the lane
Best real score ≤ null max across the full artifact key set under all four operation
families. That is a genuine negative on the owner's thesis *in its keyword/keystream form*
— it does not touch its "key is a binary pad file" form (PA-3 Tier 1), which is a
different lane.

## Scope declared up front
- Only the author's **demonstrated** toolkit: Vigenère (both signs), Atbash, Caesar/shift
  over all 29 offsets, totient/prime shift, ᚠ-interrupter handling. No new cipher classes.
- Rigid alignment for the main sweep (this is what actually solved pages 03/14), plus a
  key-phase rotation arm.
- Long-running-key arm included for the never-fed prose blocks, at all offsets, but it is
  reported as covered-by-mechanism, not as a new avenue.
