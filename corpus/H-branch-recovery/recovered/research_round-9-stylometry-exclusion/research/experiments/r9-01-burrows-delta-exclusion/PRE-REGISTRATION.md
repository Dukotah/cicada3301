# PRE-REGISTRATION — R9: Burrows' Delta stylometric EXCLUSION of LP solved prose

**Round 9. Status: EXPLORATORY / NON-DECISION-GRADE by construction.** At ~359 words no stylometric
method can support *positive* attribution (false-attribution >60% below ~3k words; Eder 2015, Koppel 2009).
This round attempts only **exclusion** ("LP prose does NOT cluster with candidate X"), and even that is
gated behind a discrimination-power control. **No positive authorship claim may be emitted regardless of
result.** The most likely and most valuable outcome is a *measured* confirmation that the corpus is too
small — converting the cited small-N barrier into one demonstrated on these specific candidates.

## Query corpus (LP)
The solved LP **authentic connected English prose**, PROPERLY WORD-SEGMENTED and DE-CONTAMINATED:
- Pages: A WARNING, WELCOME/pilgrim, SOME WISDOM, the two KOANs (incl. circumference), AN INSTRUCTION,
  AN END, PARABLE, LOSS OF DIVINITY.
- Source of word boundaries: a clean spaced community transcription (scream314 `liber_primus.md` and/or
  `SOLVED-PAGES-AND-INTERRUPTERS.md`). The repo's `analysis/armada20/key_solved_english.txt` is
  boundary-stripped and contaminated — DO NOT use it as the token source.
- **MUST strip** solver-annotation contamination: any occurrence of "outguessing the image yields …",
  "garbage output", "jpg", "none", "composite", "kB", "good luck" (the Instar-Emergence filler string),
  and the base-60/table gibberish. Report the final cleaned token list and its exact word count N_q.

## Candidate reference corpora (public domain; fetch at run time, save locally, gitignore raw texts)
- **Timothy C. May — *Cyphernomicon*** (cypherpunk register — the closest ideological neighbour).
- **Aleister Crowley** — public-domain works (*The Book of the Law*, *The Book of Lies*, *Liber* texts).
- **Zen koan translations** — public-domain only (e.g. the 1934 *Gateless Gate* / Mumonkan PD translation;
  NOT Reps "Zen Flesh Zen Bones", not PD).
- **Register controls (≥2 clearly-distinct authors):** e.g. a King-James / apophatic-mystic text and a
  neutral Gutenberg essay author — so the power control has ≥4–5 distinct author classes.

## Statistic
- **Burrows' Delta** (Manhattan distance over z-scored relative frequencies of the top-K MFW), K fixed at
  the number of words present in ALL corpora, capped at 150; **Cosine Delta** as a robustness cross-check.
- MFW list derived from the pooled reference corpora (NOT from the LP query, to avoid query leakage).
  Fixed before distances are computed.

## Prior work / delta (Gate #1 revision #3 — discharge redundancy)
A stylometry campaign already exists at `liber-primus/analysis/stylometry/` (2026-07-13): it ran Burrows'
Delta on the ~359-word **PGP-message** corpus with a closed-set power control
(`calibration_power.py`: **76% LOO accuracy, 9 authors, chance 11% at 359w** → the power gate PASSES at this
length) AND an open-set rejection control (`calibration_reject.py`: **62% impostor acceptance at 80% recall**
→ the exclusion boundary is UNRELIABLE at 359w), producing a "lead-shaped, do-not-name" result (top match
inside a ~6.6 noise band) and measuring LP prose function-word density at ~36% (vs ~54% in messages). The
Archivist missed this subtree; it is now reconciled. **R9 is non-redundant ONLY by:** (a) query = solved LP
**prose** (koan/aphorism/warning), NOT the PGP messages; (b) adding the formal **false-exclusion-rate (FER)**
control below — the operative gate the sibling campaign proved is binding; (c) Wilson-CI'd reporting.

## GATE (two controls; FER is decisive; fixed before any LP comparison)
**Control A — closed-set attribution power (necessary, expected to PASS).** Split each reference author into
non-overlapping N_q-word chunks (seed 3301; ≥3 chunks/author, else drop author). Leave-one-out
nearest-neighbour attribution among reference chunks ONLY. Report accuracy A + Wilson 95% CI vs chance
(1/n_authors). Passing this is NECESSARY BUT NOT SUFFICIENT (the sibling showed closed-set power does not
transfer to open-set exclusion).
**Control B — false-exclusion-rate calibration (OPERATIVE gate; Gate #1 revision #1).** For each held-out
GENUINE chunk of author X (register-varied where possible), apply the exact exclusion rule below against X's
own centroid (built from X's other chunks) and measure the **false-exclusion rate FER** (fraction of true
same-author chunks the rule wrongly excludes) + Wilson 95% upper bound.
**DECISION RULE (fixed):**
- If **FER Wilson-upper-bound > 10%** → the exclusion rule is uncalibrated at N_q → any LP exclusion is
  UNINTERPRETABLE → **round verdict NEGATIVE** (measured closure: "at LP's corpus size the exclusion rule
  false-excludes genuine same-author text, so no LP exclusion is trustworthy"). *Given the sibling's 62%
  impostor overlap and LP prose's ~36% function-word density, this is the predicted outcome.*
- If FER upper-bound ≤ 10% AND Control A lower-bound > chance → proceed to the LP exclusion step, EXPLORATORY.

## LP exclusion step (ONLY if BOTH controls pass)
- Compute LP query's Delta to each candidate centroid + nearest-neighbour author (descriptive only).
- **Exclusion criterion (fixed, Gate #1 revisions #5/#7):** LP is "excluded from author X" iff LP's Delta to
  X exceeds the **(1 − 0.05/m) percentile** of X's within-author chunk-to-centroid Delta distribution
  (Holm–Bonferroni over m candidates) **AND both Burrows Delta and Cosine Delta agree** (concordance). NO
  positive attribution from a low Delta — nearest neighbour is descriptive only, explicitly NOT attribution.

## Query register handling (Gate #1 revision #4 — do NOT silently pool)
The koan/circumference pages are voiced dialogue / likely-quoted mystic material (~36% function-word density,
near-zero Delta signal). Run TWO pre-registered arms: **(arm 1) connected-authorial-prose only** (exclude the
two koans + pure-aphorism pages) and **(arm 2) all solved prose**. Report N_q for each. If the connected-prose
N_q is too small for Control B to pass, THAT is the NEGATIVE result — do not pad with signal-free koan tokens.

## MFW / K derivation (Gate #1 revision #5 — no query leak)
MFW list and K are derived from the **reference corpora intersection ONLY (LP excluded)**, capped at 150;
LP-absent MFW get frequency 0 for the LP vector. Pre-registered sensitivity sweep K ∈ {50, 100, 150}.

## Candidate corpora — licensing fix (Gate #1 revision #6)
Use CONFIRMED-public-domain / already-in-repo corpora only: **Timothy May *Cyphernomicon*** (cypherpunk
register); in-repo vetted esoteric corpora under `data/keys/armada18/` and `armada19/` (e.g. Blavatsky, Levi,
Manly Hall) as PD substitutes for Crowley; a confirmed-PD **Mumonkan/Gateless Gate** edition (name translator
+ pub date, else substitute an in-repo PD mystic text); + ≥2 neutral PD register controls (e.g. a KJV/apophatic
text and a Gutenberg essayist). **Drop Crowley and any koan translation whose PD status cannot be confirmed.**

## Predictions
- **Primary (likely):** Control B (FER) FAILS → NEGATIVE. Value: the small-N exclusion floor measured on LP
  prose specifically, not merely cited — extending the sibling campaign's message-corpus result to LP prose.
- **Secondary (if both controls pass):** a set of concordant, family-corrected EXPLORATORY exclusions; still
  non-decision-grade, still no positive attribution.

## Determinism & outputs
Fixed MFW derivation; seed 3301 for chunking. Save `results.json` (N_q, cleaned LP tokens count, MFW list,
power-control accuracy + CI + chance, and — only if reached — LP Delta distances + exclusion table).
Raw fetched corpora saved under `corpus/` and **gitignored** (keep only derived frequency tables + results).
