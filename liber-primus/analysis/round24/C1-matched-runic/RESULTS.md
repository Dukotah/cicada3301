# Round 24 — Lane C1 — matched-runic + non-English re-adjudication — RESULTS

_Run 2026-08-30. PREREG frozen before scoring (`PREREG.md`). Binding doctrine:
`../../../ARMADA-DOCTRINE.md`. This is an instrument/closure audit (R1 + R6), not a key-space sweep._

## Verdict

**NULL — control-validated YES.** The matched-runic adjudicator does NOT change any historic
negative for the re-adjudicated slice: the strongest prior B-04 slice, re-scored under the
matched-runic scorer + a language-aware EN/LA/GR rune-trigram panel + the four R3 language-agnostic
statistics, produces **zero survivors** at 20,480 decodes. The English-only sweeps were **not** hiding
a non-English survivor in this slice; the negatives hold under the corrected scorer.

## Trust anchor

`python3 tests/validate.py` -> **5/5 PASS** (reproduces all known solved pages) before scoring.

## Positive control (mandatory) — PASS, with the L7-A gap reproduced

`control.py` plants Latin AND romanized Greek into the rune space, enciphers under
`sha256_ctr(CICADA3301)` + `encipher_keyskip(supp=0.83)`, decodes with the CORRECT key at
`beam_decode(400,3)`, and adjudicates the recovered plaintext under BOTH the English quadgram scorer
and the round16 matched-runic scorer. Rune-index recovery is 100% on every linguistic register (the
DECODER works; only the ADJUDICATOR was ever in question — exactly L7-A).

Power measured two ways at L=120 (fraction of correct-key decodes scoring above the bar):

| register | median corr EN | median corr MATCHED | power EN (fixed -5.5) | power MATCHED (fixed -5.5) |
|---|---:|---:|---:|---:|
| EN_MODERN | -4.173 | -4.027 | 1.00 | 1.00 |
| **LATIN** | -5.523 | **-5.241** | **0.50** | **0.79** |
| GREEK (romanized) | -5.226 | -5.149 | 1.00 | 1.00 |
| EN_NOVOWEL | -7.562 | -7.502 | **0.00** | **0.00** |
| RAND (floor) | -7.326 | -7.287 | 0.00 | 0.00 |

**The matched scorer's advantage is real and measured:** on Latin it rescues ~29 percentage points
of correct-key decodes the English scorer discards (0.50 -> 0.79), confirming the L7-A gap (English
Latin power 0.33-0.50) and the matched scorer's claimed edge. EN_NOVOWEL stays at 0.00 under BOTH
scorers — reproducing L7-A's 0.00 exactly.

**What the control also proves (the decisive red-team fact, pre-registered):** the matched scorer
corrects rune ORTHOGRAPHY (the 7 digraph expansions + lossy K/Q->C, V->U, Z->S folds), NOT LANGUAGE.
It rescues Latin (whose letters are English-quadgram-shaped once the orthography penalty is removed)
but CANNOT rescue vowel-dropped English (a language/phonotactic gap). So the matched scorer widens the
adjudicator only along the orthography axis, bounded by L7-A's -0.139 round-trip cost. The
language-aware axis is the EN/LA/GR rune-trigram panel, run alongside it.

## Re-adjudication (the real slice) — clean NULL

`readjudicate.py` re-decodes a bounded, R20-prior-ordered slice of the B-04 derived-key family and
adjudicates every decode under EN + matched + EN/LA/GR trigram panel, persisting the four R3 stats per
row (doctrine R3 — the axis L7-A-HANDOFF-NONCOMPLIANCE recorded as 0/15 for the original sweeps).

- **Slice (coverage):** top-40 R20-prior seeds (`round20/P3/seedprior20.json`, rank-1 = 1325734783,
  the 3301 key-creation second) x 16 B-04 generators (`round13/B04/ks.py`) x 4 reductions
  (mod29/rej29/hi_nib/bits5) x 2 signs x 2 atbash x 2 seed-byte-forms (ASCII-decimal + raw big-endian),
  offset 0, L=120, target = real unsolved LP2 head. **N = 20,480 decodes.**
- **Power (control-measured envelope):** EN ~1.0, Latin 0.50 (EN) / 0.79 (matched), Greek 1.0,
  EN_NOVOWEL 0.00 under both. So the slice is powered for EN/Latin/Greek and blind to vowel-dropped
  English (permanent; a language gap the matched scorer does not close — inherited from L7-A).
- **Null:** seed-3301 order-matched, 400 uniform-random wrong keys through the identical beam on the
  SAME real ciphertext. matched null: mean -7.278, sd 0.229, max -6.604.
- **Family-wise bars at true N (`benchmark/null.py::threshold_for`):** EN -4.775, MATCHED -4.685,
  panel -1.306.

| scorer | best score | its family-wise bar | margin | survivors |
|---|---:|---:|---:|---:|
| English | -6.374 | -4.775 | **-1.60** | 0 |
| matched-runic | -6.294 | -4.685 | **-1.61** | 0 |
| EN/LA/GR panel-max | -1.460 | -1.306 | **-0.15** | 0 |

Every best decode sits far below its bar. The best matched decode's R3 stats are textbook noise:
IoC·N 1.072 (flat), min-distinct-over-32 = 15 (high), compress 0.82 (incompressible), head
`EAEAMMXIATTHMPUTUNGERNGNGWOEONGCEORAETHOTHISLEAM`. The best panel-GR decode is likewise gibberish
(`NGDIUYEAXSNBJIAEAEAUCONUJFPGRIAPTYJOENGROOHANTHR`).

## Red-team (R6, mandatory) — NO-ERROR-FOUND; refute-by-default upheld

1. **FP-inflation / double-max hazard (R21-L5, B-04 GATE-NOTE):** recomputed the FP ceiling under the
   matched scorer at true N. Expected false-positives AT the bar = **0.0100 (matched) vs 0.0101
   (English)** — identical, exactly the alpha=0.01 family-wise design. The matched scorer does NOT
   inflate the FP rate. No sieve x panel-max compounding: ONE adjudication per decode per register, ONE
   family-wise `threshold_for` per register. The hazard was not reintroduced.
2. **Instrument scope (what the matched scorer can/cannot see):** established by the control —
   orthography-correcting, not a non-English language model. The negative therefore does NOT extend to
   a register whose LANGUAGE neither the matched scorer nor the LA/GR trigram panel models
   (vowel-dropped English, Welsh, Hebrew, Norse, Enochian, non-linguistic payloads — the last is B6-
   undetectable in principle). Those remain `not_covered`.
3. **Survivors:** none. R21-L1 SEAL would apply if any bar-clearer appeared (FLAGGED-FOR-ORACLE, never
   auto-certified); there is nothing to flag.

## The decision-relevant finding

**The matched-runic adjudicator does NOT overturn any historic negative on the re-adjudicated slice.**
The matched scorer is genuinely more powerful than the English scorer on Latin (0.50 -> 0.79 recovered)
and reproduces the exact L7-A power gap — so the instrument audit is real, not a formality — but when
that corrected instrument (plus a language-aware LA/GR trigram panel and the four R3 stats) is turned
on the strongest prior B-04 slice, every decode is deep noise: 1.6 score-units below the family-wise
bar, flat IoC, incompressible. The English-only B-04 negatives were **not** hiding a non-English
survivor in the R20-prior top-40 x B-04 cross-product.

## Three conditionals this negative carries (Q4)

1. **Key space:** top-40 R20-prior seeds x B-04 generators x {mod29,rej29,hi_nib,bits5} x sign x
   atbash x 2 seed-forms, offset 0. Seeds outside the R20 prior, generators outside ks.py, offsets
   != 0, and deeper R20-prior ranks are NOT covered (the slice is bounded, not the family).
2. **Decoder transition model:** `beam_decode(max_skip=3)` — the one key-skip relation; INHERITS
   L7-B (skip_by_two, free drift unrepresentable). That closure is lane C2.
3. **Adjudicator register:** English quadgram + round16 matched-runic (orthography-corrected English)
   + EN/LA/GR rune-trigram panel + 4 R3 agnostic stats. Registers whose LANGUAGE none of these models
   (vowel-dropped English, Welsh, Hebrew, Norse, constructed langs, non-linguistic payloads) are NOT
   covered.

## Reopens if

A wider R20-prior depth, a non-zero offset, a generator/reduction outside this slice, OR a genuinely
language-aware non-English adjudicator (Hebrew/Norse/Enochian LM, not just orthography-corrected
English) produces a decode whose score clears the seed-3301 order-matched null max AND the family-wise
`threshold_for(N)` bar. Any such survivor is FLAGGED-FOR-ORACLE (R21-L1), never auto-certified.

## Files

- `PREREG.md` — frozen pre-registration (five Aiming-Test answers, control, null, bars, red-team).
- `greek_corpus.py` — romanized-Greek corpus builder (15,150 letters from the repo's Greek fragments).
- `control.py` -> `out_control.json` — positive control (matched vs English power, L7-A gap reproduced).
- `readjudicate.py` -> `results.json` — the bounded B-04 re-adjudication (20,480 decodes, R3 stats persisted).
- `ledger.json` — this lane's ledger row.
