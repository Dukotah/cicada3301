# Iteration 7 — GAME-THEORIST: Constant + Seed Provenance Audit

Goal: enumerate exactly which published constants/sequences the SOLVED-page
keystreams draw from, list every seed value the solved/clear pages EXPOSE to an
intended solver, and argue from Cicada's recruiter payoff structure where the
0-54 pad most likely lives. Output = a PRIORITY seed list for the
doubling-ratio-restoration oracle.

This is a RECON / provenance document. It does not run English-scored additive
lanes (those are sealed). It feeds the plaintext-blind oracle.

---

## PART 1 — Exact generator each SOLVED page uses

Read from `src/lp/ciphers.py`, `src/lp/gematria.py`, `tests/validate.py`,
`data/keys/solved_plaintext.txt`. The rig only ever needs FOUR generator
families to reproduce EVERY documented solve:

| Solved page(s)                         | Cipher family        | Generator / key source                                             | Constant class |
|----------------------------------------|----------------------|--------------------------------------------------------------------|----------------|
| Runes-01, 05, 06 ("simple" pages)      | Atbash + Caesar shift| `atbash_indices` then `(c + sign*k) mod 29`, k a small fixed shift  | trivial (no seed) |
| 03 (WELCOME/PILGRIM)                    | Vigenère             | keyword `DIVINITY` → GP indices, cycled (`repeat_key`)             | themed English word |
| 14 (A KOAN)                            | Vigenère             | keyword `FIRFUMFERENFE` (=CIRCUMFERENCE, runic C/F ambiguity)       | themed English word |
| "A KOAN"/0x totient page (lore-solved) | Running keystream    | `prime_totient_stream` = `(prime_i − 1) mod 29`, i.e. totient of primes | prime/totient sequence |
| AN-END page (the phi/totient page)     | Running keystream    | totient-indexed keystream `(totient(p_i) − 1)`; a per-prime shift  | prime/totient sequence |

Only TWO deterministic-sequence generators are ever the actual pad on a solved
page (the rest are keyword-Vigenère or trivial shifts):

  1. `prime_stream(L)`        = consecutive primes mod 29             — "THE PRIMES ARE SACRED"
  2. `prime_totient_stream(L)`= (prime_i − 1) mod 29 = totient(prime) — "THE TOTIENT FUNCTION IS SACRED"

`totient_stream(L, start=2)` = totient of consecutive INTEGERS mod 29 is exposed
in code as a "flavour" but is NOT the documented solve of any page; it is a
near-miss variant the gate can pick. Keep it in the seed list as a distinct
generator.

KEY GAME-THEORY OBSERVATION (confirmed here, not assumed):
Every solved key is either (a) a themed English word the page's own plaintext
names, or (b) the prime/totient sequence the pages EXPLICITLY sanctify
("the primes are sacred", "the totient function is sacred"). NONE is an external
file. This closes the preimage/rot-prone-file lane (already independently
proven) and strongly implies 0-54's pad is generator (b) or a keyword (a),
seeded by a value the artifact already teaches — NOT a true OTP.

---

## PART 2 — Every seed value the solved/clear pages EXPOSE

An "intended solver" who has read the solved pages holds exactly these numbers.
These are the candidate SEEDS / start-offsets / keyword sources for a
deterministic pad. Grouped by provenance and confidence.

### 2a. Sacred numeric constants (highest confidence — the pages sanctify them)
- `3301`  — the signature; prime (verified: 3301 is prime); appears on every PGP page.
- `totient(3301) = 3300` — the totient the pages sanctify, applied to the signature.
- The 29 Gematria-Primus primes `2,3,5,…,109`; their SUM = **1480**.
- `109` — 29th prime, largest GP value; natural stream `start`/offset.
- `29`  — the modulus / alphabet size; natural period.
- Magic-constant `3301` again: the KNOW-THIS 5×5 square rows/cols each sum to 3301
  (verified). Center cell = **809**. Border/first-row cells 434,1311,312,278,966.

### 2b. Structural counts the artifact exposes (medium-high confidence)
- `12956` — unsolved-rune count (pages 0-54), the count the MDL/doubling oracle uses.
- `13136` — total runes across all 57 `%`-segments in the transcription file.
- Per-page rune counts (0-54), which an interrupter/skip generator could key on:
  `[262,266,201,217,261,263,196,208,255,268,263,273,261,272,137,159,267,273,260,271,269,273,131,213,270,273,265,234,269,277,263,269,121,214,261,271,238,228,228,240,231,273,272,274,273,270,270,274,271,66,92,263,179,232,76,85,95]`
- `56` / `57` — page count (56 `%` separators → 57 segments); the LP is often cited as 58 pages.

### 2c. Themed keyword seeds (medium confidence — same class that solved 03 & 14)
Words the SOLVED plaintext literally emits, in GP-index form, as Vigenère-key
candidates for 0-54 (Cicada re-uses its own vocabulary as keys):
`DIVINITY`, `CIRCUMFERENCE`, `INSTAR`, `PARABLE`, `WISDOM`, `TOTIENT`, `PRIMES`,
`SACRED`, `PILGRIM`, `MASTER`, `TRUTH`, `WITHIN`, `EMERGE`, `KOAN`, `WELCOME`,
`THEEND` / `AN END` / `AN INSTAR`. (These parse cleanly via `keyword_to_indices`.)

### 2d. Published-lore constants (lower confidence — external but "well-known")
- `1595277641` (Cicada's early published prime product) — external, deprioritise
  per the closed-preimage finding, but a solver technically holds it.
- Golden ratio / Fibonacci: NOT sanctified anywhere in the solved text. The
  memory's "phi-indexed keystream" phrasing actually refers to Euler's totient
  φ(n), NOT the golden ratio. **Do not spend the oracle on golden-ratio pads.**

---

## PART 3 — Recruiter payoff argument: where does the 0-54 key live?

Cicada is a RECRUITER. Its payoff is maximised when EXACTLY the intended solver
passes and no one else. That constrains the key design:

1. **Self-contained & derivable.** Every solved key is derivable from the
   artifact + sanctified constants. A recruiter will NOT gate its funnel on an
   external, rot-prone, link-dies-in-a-year file. → The 0-54 pad is a
   DETERMINISTIC generator seeded by a taught value, not a random OTP and not an
   external key. (Consistent with the iter-6 finding: the stream is exactly
   incompressible yet retains English doubling-suppression → an English
   plaintext under a deterministic pad, not a machine pad.)

2. **Escalating difficulty, not impossibility.** The solved pages teach the
   EXACT tools (Atbash, Vigenère-with-themed-word, prime stream, totient stream,
   interrupter nulls). A recruiter's final on-book stage uses those SAME tools
   with a HARDER seed/composition, not a brand-new primitive. → 0-54 most likely
   = totient/prime stream and/or themed-keyword Vigenère, but with (i) a
   non-zero START offset, (ii) an interrupter rule, or (iii) a two-layer
   composition (keyword ⊕ prime-stream). The novelty is COMPOSITION/OFFSET, not
   a new generator.

3. **Was 0-54 even meant to be solved standalone?** Real risk: the 2014 LP is
   widely believed to be INCOMPLETE — Cicada went dark before releasing the
   step that hands over the 0-54 seed (the pattern elsewhere is "solve stage N to
   earn the key material for stage N+1"). If the 0-54 seed was to be delivered by
   a never-published later step, then 0-54 is a locked stage with an
   archival-loss key — matching the closed-preimage/hash finding. In that world
   the ORACLE's job is not to break it but to CONFIRM the pad family (does a
   totient/prime/keyword generator move the doubling ratio toward English even
   without the exact offset?). A partial signal from a family = evidence 0-54 is
   that family, guiding whatever future seed is recovered.

CONCLUSION: The pad most likely lives in the **prime/totient sequence family**
(the only sanctified deterministic generators) OR a **themed-keyword Vigenère**,
composed with a START OFFSET drawn from the sacred/structural constants above,
possibly under the interrupter (ᚠ-null) rule the solved pages already use. A pure
external OTP is ruled out by payoff structure + the incompressibility+doubling
evidence.

---

## PART 4 — PRIORITY SEED LIST for the doubling-ratio-restoration oracle

Feed these to the plaintext-BLIND oracle (measure doubled-rune suppression ratio
of ciphertext-minus-generated-stream; target the ~0.147 English band; null pad
≈1.0). Rank order = descending prior from Parts 1-3. Keep it BOUNDED.

GENERATOR FAMILIES (from ciphers.py, the only ones the rig ever needs):
  G1 = prime_stream(L, start)                 # consecutive primes mod 29
  G2 = prime_totient_stream(L, start)         # (prime_i − 1) mod 29  [SANCTIFIED]
  G3 = totient_stream(L, start)               # totient(consecutive ints) mod 29
  G4 = repeat_key(keyword→GP idx)             # themed-word Vigenère
  G5 = G4 ⊕ G2  (composition: keyword then totient stream, both signs)

START-OFFSET / SEED sweep (apply to G1/G2/G3 `start`, and as Vigenère phase):
  s ∈ { 0, 1, 2, 3, 29, 109, 3301, 3300, 1480, 809, 12956,
        <per-page rune count for that page> }

KEYWORD seeds for G4/G5 (parse via keyword_to_indices):
  DIVINITY, CIRCUMFERENCE, INSTAR, PARABLE, TOTIENT, PRIMES, SACRED, WISDOM,
  PILGRIM, TRUTH, WITHIN, EMERGE, KOAN, THEEND, ANINSTAR

CIPHER-DIRECTION / RULE knobs (small, must all be swept — the gate already
proves direction is empirical, not lore):
  sign ∈ {−1, +1};  atbash ∈ {False, True};  interrupter(ᚠ-null) ∈ {False, True}

EXPLICITLY DEPRIORITISED (do not spend oracle budget here):
  - Golden-ratio / Fibonacci pads (never sanctified; "phi" = totient, not ϕ_golden).
  - External file / OTP / preimage-of-hash pads (closed by prior iterations).
  - English-SCORED additive keytext lanes (sealed; use the BLIND doubling oracle).

VALIDATION REQUIREMENT (unchanged, non-negotiable): before trusting any oracle
hit, confirm the oracle recovers the KNOWN AN-END doubling ratio from
known-ciphertext-minus-known-keystream. Only a family that beats the 40-control
null band AND moves the residual doubling ratio diagnostically toward the
readable-English band (~0.147) counts as a restoration signal. Never fabricate.

---

## Provenance of every number in this doc (so it is auditable)
- Generators + keyword solves: `src/lp/ciphers.py`, `tests/validate.py` (SOLVED table).
- Gematria primes / modulus 29 / 109: `src/lp/gematria.py`.
- 3301 prime, totient(3301)=3300, GP-prime-sum=1480, magic-sum=3301, center=809:
  computed this iteration (see AUDIT run log).
- 12956 unsolved-rune count: `analysis/recon/i6_mdl/mdl_result.json`.
- Per-page counts, 13136 total, 57 segments: computed from
  `data/krisyotam_runes.txt` this iteration.
- Themed keywords: `data/keys/solved_plaintext.txt` (WELCOME/KOAN/PARABLE/INSTAR text).
