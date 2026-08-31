# Round 24 — Lane C1-EXT — genuinely LANGUAGE-AWARE non-English adjudication — RESULTS

_Run 2026-08-30. PREREG frozen before scoring (`PREREG.md`). Binding doctrine:
`../../../ARMADA-DOCTRINE.md`. Instrument/closure audit (R1 + R6). Follow-up to lane C1, closing
the axis C1 explicitly left `not_covered`: genuinely language-aware non-English models, not merely
orthography-corrected English._

## Verdict

**NULL — control-validated YES.** A genuinely language-aware panel spanning **Latin, Greek, Old
English poetic, and Enochian** — each control-validated to recover its OWN planted language 2-5x
better than the English quadgram scorer — produces **zero survivors** on the strongest prior B-04
slice (20,480 decodes, identical to C1). **The English-only adjudicator was NOT structurally
hiding a non-English plaintext in this slice; the negatives hold across every non-English language
that could be honestly modelled from in-repo corpora.**

## Trust anchor

`python3 tests/validate.py` -> **5/5 PASS** (reproduces all known solved pages) before scoring.

## Honest register availability (the decisive honesty call)

The rune folder is Latin-alphabet based, so a language-aware model in the rune space needs a
connected corpus of that language in LATIN letters. Measured from the repo, no external downloads:

| register | source | clean Latin-script mass | verdict |
|---|---|---:|---|
| Latin (calibration) | `analysis/latin/latin_28233.txt` | >200k | AVAILABLE |
| Greek (calibration) | romanized (`../C1-matched-runic/greek_corpus.py`) | ~15k | AVAILABLE |
| **Old English poetic** | genuine þðæ lines in bilingual `round10b/.../oe_beowulf.txt` | ~121k | **AVAILABLE** |
| **Enochian (phonetic)** | Angelic Keys in `analysis/foundation/enoch_text.txt` | ~11k | **AVAILABLE (control-validated)** |
| Old Norse (native) | all repo Norse = ENGLISH TRANSLATIONS; native þð mass <25 chars | ~0 | **UNAVAILABLE** |
| Hebrew (romanized) | 18.7k NATIVE-script (unmappable) + only isolated romanized proper nouns | ~0 connected | **UNAVAILABLE** |

**Old Norse and romanized Hebrew were refused, not faked.** An English translation of the Edda is
an English LM, not a Norse LM (PREREG red-team #1). Inventing a romanization corpus or downloading
text is forbidden. A plausible-but-wrong hit is worse than a clean null. Old English poetic is the
honest, in-repo stand-in for the "Old Norse / Old English poetic" register the task names — the
same alliterative Germanic register the Anglo-Saxon futhorc actually served.

## Positive control (mandatory) — PASS on all four non-English registers

`control.py` plants each register into the rune space, enciphers under
`sha256_ctr(CICADA3301)` + `encipher_keyskip(0.83)`, decodes with the CORRECT key at
`beam_decode(400,3)`, and adjudicates the recovered plaintext under BOTH the English quadgram
scorer AND that register's OWN language-aware rune-trigram LM. Rune-index recovery is **100%** on
every linguistic register — the DECODER works; only the ADJUDICATOR was ever in question.

Power measured as **d-prime** (median correct-key score minus null mean, over null SD — a
scale-free comparison across the two scorers' different score ranges) at L=120:

| register | median corr EN | median corr LM | **d' English** | **d' language-LM** | LM wins? |
|---|---:|---:|---:|---:|:--:|
| EN_MODERN | -4.173 | -0.907 | 11.13 | 20.24 | yes |
| **LATIN** | **-5.523** | -0.928 | 10.11 | **19.89** | **yes** |
| GREEK | -5.226 | -0.931 | 10.68 | **32.87** | **yes** |
| **OLD_ENGLISH** | **-5.383** | -1.000 | 7.84 | **17.94** | **yes** |
| **ENOCHIAN** | **-5.827** | -0.884 | 7.10 | **34.37** | **yes** |
| EN_NOVOWEL | -7.562 | -1.147 | -1.01 | 17.79 | yes |
| RAND (floor) | -7.326 | -1.877 | 0.03 | -0.47 | no |

**The decisive L7-A fact reproduced and extended:** the English scorer places genuine **Latin
(-5.52), Old English (-5.38) and Enochian (-5.83) AT or BELOW the -5.5 publication bar** — it would
REJECT them as noise — while each language LM places them **18-34 SD above its own noise floor**.
This is exactly the English-only blindness the campaign was worried about, and unlike C1's
orthography-corrected matched scorer (which scored 0.00 on vowel-dropped English), a genuinely
language-aware LM recovers the language, including the two registers C1 could not model. The RAND
floor is non-discriminating for the LM (d' -0.47) — the LM does not reward arbitrary decodes.

All four non-English registers **VALIDATED** and eligible for the real panel.

## Re-adjudication (the real slice) — clean NULL

`readjudicate.py` re-decodes the IDENTICAL C1 slice and adjudicates every decode under the English
scorer + the control-validated 5-language trigram panel {EN, LA, GR, OE, Enochian}, persisting the
four R3 statistics per row.

- **Slice (coverage):** top-40 R20-prior seeds (rank-1 = 1325734783) x 16 B-04 generators x 4
  reductions x 2 signs x 2 atbash x 2 seed-forms, offset 0, L=120, target = real unsolved LP2 head.
  **N = 20,480 decodes** (identical to C1).
- **Power (control-measured):** all four non-English registers validated (language-LM d' strictly
  above English d' on their own planted text). Coverage x power reported together (R2).
- **Null:** seed-3301 order-matched, 400 uniform-random wrong keys through the identical beam on the
  SAME real ciphertext, adjudicated by the SAME widened panel. panel-max null: mean -1.539, sd
  0.017, **max -1.4875**.
- **Family-wise bars at true N (`benchmark/null.py::threshold_for`):** EN -4.775, panel-max **-1.347**.

| scorer | best score | its family-wise bar | margin | survivors |
|---|---:|---:|---:|---:|
| English | -6.374 | -4.775 | **-1.60** | 0 |
| language-aware panel-max | -1.460 | -1.347 | **-0.11** | 0 |

The best panel decode (register GR) sits above the null max but **below** the family-wise bar, so
it does not clear both gates. Its R3 stats are textbook noise: IoC·N 1.03 (flat), min-distinct-32 =
16 (high/unrestricted), compress 0.84 (incompressible), head
`NGDIUYEAXSNBJIAEAEAUCONUJFPGRIAPTYJOENGROOHANTHR`. **No language leads meaningfully** — per-register
best: EN -1.50, LA -1.70, GR -1.46, OE -1.59, Enochian -1.46; Old English and Latin never even beat
the panel noise floor (-1.4875). The two languages this lane added over C1 (OE, Enochian) surfaced
nothing the 3-language C1 panel missed.

## Red-team (R6, mandatory) — NO-ERROR-FOUND

1. **English-translation trap (decisive honesty):** avoided by construction. Old English modelled
   ONLY from genuine þ/ð/æ-bearing poem lines; Enochian ONLY from phonetic Angelic text; Old Norse
   and Hebrew (translation-only / native-script-only) refused rather than faked.
2. **Unvalidated-dimension inflation:** a register failing its control is dropped before the
   panel-max. All four non-English registers validated here, so none added a noisy max term.
3. **Double-max / multiple-comparisons FP inflation (R21-L5, B-04 GATE-NOTE):** widening the panel
   from 3 languages (EN/LA/GR, C1) to 5 (+OE +Enochian) did **NOT** inflate the FP rate. Expected
   false-positives AT the bar = **0.0101 (widened panel) vs 0.0101 (English)** — identical, exactly
   the alpha=0.01 family-wise design, and identical to C1's 3-language panel. This holds because the
   panel-max statistic is computed the same way for the observed decodes AND the seed-3301 null, so
   the null already carries the max-over-registers and `threshold_for(N)` is the correctly inflated
   family-wise bar. No prefilter-max compounded with panel-max. The hazard was not reintroduced.
4. **Survivors:** none. R21-L1 SEAL would flag any bar-clearer FOR-ORACLE (never auto-certified);
   nothing to flag.

## The decision-relevant finding

**The English-only adjudicator was NOT structurally hiding a non-English plaintext in the strongest
prior B-04 slice.** A genuinely language-aware panel — Latin, Greek, Old English poetic, Enochian,
each control-validated to recover its own language 2-5x better than the English scorer, including
the registers C1's orthography-only scorer could not model — yields zero survivors, 0.11 (panel) /
1.60 (English) score-units below the family-wise bar, on decodes with flat IoC, high min-distinct,
and incompressible payloads. The negatives hold across every non-English language that could be
**honestly** tested from in-repo corpora. The two registers named in the task that had NO honest
in-repo corpus — **native Old Norse (translation-only)** and **romanized Hebrew (no connected
corpus)** — could not be tested and remain `not_covered`; they were refused rather than faked.

## Languages honestly tested vs not

- **Tested (control-validated, NULL):** Latin, Greek, Old English poetic, Enochian.
- **UNAVAILABLE (not_covered, refused not faked):** native Old Norse, romanized Hebrew.

## Files

- `PREREG.md` — frozen pre-registration (register availability audit, Aiming Test, control, null,
  widened-panel double-max mitigation, pass/fail).
- `nonenglish_corpus.py` — honest Old English + Enochian corpus builders (genuine text only).
- `control.py` -> `out_control.json` — positive control (d-prime per register, L7-A gap reproduced,
  validation gate).
- `readjudicate.py` -> `results.json` — the widened-panel re-adjudication (20,480 decodes, R3 stats).
- `ledger.json` — this lane's ledger row.
