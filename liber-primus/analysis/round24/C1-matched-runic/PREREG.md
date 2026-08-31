# Round 24 — Lane C1 — matched-runic + non-English re-adjudication — PREREG

_Frozen 2026-08-30, before any real scoring. Binding: `../../../ARMADA-DOCTRINE.md`,
`../PLAN.md` (C1 survivor sketch). No thresholds edited after a result is seen; only dated
addenda._

## What this lane is (and is not)

An **instrument / closure audit** (doctrine R1 + R6), NOT a new key-space sweep. It re-adjudicates
the strongest prior derived-key slice (B-04, ordered by the R20 seed prior) with the ONE adjudicator
axis the ledger states verbatim was never adopted by any lane: the `round16/scorer` **matched-runic
quadgram scorer** (`analysis/round16/scorer/scorer.py`), corrected for the 7 digraph rune expansions
and the lossy K/Q->C, V->U, Z->S folds. Ledger `L7-A-SCORER-ENGLISH-ONLY.not_covered[2]` and
`round19/I2.not_covered` both record it as unadopted. R3's four language-agnostic statistics
(decrypt IoC·N, min distinct symbols over a 32-rune window, best non-English rune-trigram LM,
compressibility) are persisted per row at sweep time (R3, non-negotiable).

It can only REOPEN old negatives, not manufacture a new hit — its realistic best case is a tightened
bound: "the English-only / orthography-mismatched sweeps were hiding a non-English survivor" OR "the
negatives hold under the corrected scorer." (PLAN.md honest note.)

## The Aiming Test (five answers, required before running)

**Q1 — What would a hit look like, would THIS instrument recognise it?**
A hit = a real B-04 seed whose decrypt, invisible to the English quadgram scorer, scores above the
seed-3301 order-matched null under the matched-runic scorer (or one of the persisted agnostic stats).
The positive control (§ Control) plants Latin AND Greek into the rune space, enciphers under a real
key + the pinned filter, decodes with the CORRECT key, and confirms the matched scorer recovers them
where the English scorer does not. If the control does not reproduce a matched > English power gap,
STOP — the instrument is not doing what the lane claims.

**Q2 — What measured fact raises this family's prior above flat?**
L7-A measured the English quadgram adjudicator at power 0.33 (Latin) / 0.00 (vowel-dropped English)
even though the beam recovers 100% of rune indices (`LEDGER.json` L7-A-SCORER-ENGLISH-ONLY.result).
The B-04 slice is ordered by the R20 seed prior (rank-1 = 1325734783, the 3301 key-creation second;
`round20/P3/seedprior20.json`), an evidence-derived ordering (R4), not a flat one.

**Q3 — Is the space bounded, and by what?**
Enumerable + bounded. Re-decode a fixed slice: the top-K R20-prior seeds × B-04's generator/reduction/
sign/atbash/offset cross-product, at a fixed segment length, all pure-Python in-session. Slice size is
reported as coverage. This is NOT the full 6.22M-decode B-04 sweep; it is a re-adjudication of a
bounded, prior-ordered subset (PLAN.md: "re-run a subset to persist the new register scores" — the
old rows are English-argmax only and un-reinterpretable, L7-A-HANDOFF-NONCOMPLIANCE 0/15).

**Q4 — The three conditionals the negative carries:**
1. **Key space:** top-K R20-prior seeds × B-04 generators (`round13/B04/ks.py`) × reductions × sign ×
   atbash × the offsets B-04 covered. Seeds outside the R20 prior / generators outside ks.py NOT covered.
2. **Decoder transition model:** `skipdecode.beam_decode(max_skip=3)` — the ONE key-skip rejection
   relation; INHERITS L7-B (skip_by_two, free drift unrepresentable). That is lane C2's scope.
3. **Adjudicator register:** the matched-runic quadgram scorer + the 4 R3 agnostic stats + a rune-space
   trigram panel (EN/LA/GR). This is the axis being repaired. The matched scorer is still an ENGLISH
   language model with corrected rune ORTHOGRAPHY — see the red-team note below on what it can and
   cannot see.

**Q5 — Kill condition at 10% of budget:**
If the positive control does NOT show the matched scorer recovering planted Latin/Greek above its
seed-3301 null where the English scorer fails (i.e. no measurable matched>English power gap), the
instrument claim is false for this construction — STOP and report control-failed, do NOT run the real
re-adjudication as if it meant something.

## The control (mandatory, before real scoring)

Plant Latin (`analysis/latin/*.txt`, fold LA) AND romanized Greek (extracted + scholarly-romanized
from the repo's Greek-bearing texts; see `greek_corpus.py`) into rune indices. For each register ×
length × replicate: encipher under `make_key("sha256_ctr", seed=CICADA3301)` + `encipher_keyskip(supp=0.83)`,
`beam_decode(beam_w=400, max_skip=3)` with the CORRECT key; adjudicate the recovered `plain_idx` under
BOTH the English quadgram scorer AND the matched-runic scorer, plus the truth-plaintext under both.
Also run EN_MODERN (upper bound), EN_NOVOWEL (L7-A's 0.00 case), and RAND (floor).

**Control pass:** matched-scorer power > English-scorer power on at least one non-English register at
L=120, reproducing L7-A's direction (English underpowered on Latin/Greek). Power = fraction of
replicates whose adjudicated score exceeds the register's OWN seed-3301 order-matched null bar.

## Null (per register, seed 3301, order-matched)

For each register × length, a seed-3301 order-matched null: N_null decodes of the register's own
enciphered ciphertext under UNIFORM-RANDOM wrong keys through the identical beam, adjudicated by the
same scorer. Order-matched = same L, same filter, same beam, same scorer; only the key is wrong.
The per-register bar = that null's maximum (family-wise over N_null), reported alongside `threshold_for(N_null)`.

## Family-wise bar (real slice)

Panel-max `threshold_for(N)` at the ACTUAL re-adjudicated N (`benchmark/null.py`), per register, NEVER
the habitual -5.5. The best score is compared to that bar and to the expected null max.

## Coverage × power (reported together, R2)

- Coverage = the exact re-adjudicated slice size (seeds × generators × reductions × axes × offsets).
- Power = measured per-register recovery of the CORRECT key under the matched scorer vs the English
  scorer (report the envelope: EN≈1.0, Latin, Greek, EN_NOVOWEL≈0 — not a single number).

## Red-team, pre-registered (R6)

1. **FP-inflation hazard (double-max):** the repo logged a sieve×panel-max FP-inflation hazard
   (R21-L5, B-04 GATE-NOTE). Do NOT compound a prefilter max with a panel max. The real slice uses
   ONE adjudication per decode per register; the bar is a single family-wise `threshold_for` per
   register at the true N. Recompute the FP ceiling under the matched scorer and confirm it is not
   inflated relative to the English scorer at matched N.
2. **What the matched scorer can and cannot see (decisive):** the round16 matched scorer is trained on
   ENGLISH quadgrams pushed through the rune round-trip; it corrects ORTHOGRAPHY (digraph expansion +
   lossy folds), not LANGUAGE. It is NOT a Latin or Greek language model. So its advantage over the raw
   English scorer, if any, is bounded by the orthography round-trip cost L7-A measured (delta -0.139).
   A true non-English survivor whose LANGUAGE the model cannot see is still invisible; the rune-space
   LA/GR trigram panel + the agnostic stats are the language-aware axis. Any survivor is refuted-by-
   default and, per R21-L1 SEAL, FLAGGED-FOR-ORACLE — never auto-certified.

## Pass / fail (frozen)

- Control PASS iff matched power > English power on >=1 non-English register at L=120.
- Real re-adjudication HIT-flagged iff any decode's matched-scorer score (or any per-register panel
  score) clears its own seed-3301 order-matched null max AND the family-wise `threshold_for(N)`.
- Otherwise NULL, reported with coverage × power and the three conditionals.
