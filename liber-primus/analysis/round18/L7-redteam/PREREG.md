# L7 — INSTRUMENT RED-TEAM — pre-registration

_Written 2026-08-25, **before any measurement in this lane was run**. Thresholds below are
fixed and are not edited after seeing a result (Round 18 rule 1)._

## What was read before this document was written

`round18/CAMPAIGN-PLAN.md`; `AGENTS.md` §§1–8; `round12/D3/RESULTS.md`;
`round17/SYNTHESIS.md`; `benchmark/{null,gates,plant}.py`, `benchmark/README.md`;
`src/lp/{score,gematria}.py`; `analysis/campaign18_skip/skipdecode.py`;
`analysis/round11/lib_numchannel.py`; `analysis/round17/lib_padsweep.py`;
`analysis/round10b/B6-non-english-plaintext/RESULTS.md` (+ its `run_lang.py` corpus loader);
`analysis/round12/D2/g3_floor_probe.py`; `LEDGER.json` (all 62 entries, `coverage` /
`not_covered` fields); `campaign14/REDTEAM-PROPOSALS.md`; and the recorded result JSONs of
round13/B04, round16/{KDF,prng,F-01,scorer}, round17/{P0,P3}.

No decode, plant, null or sweep of this lane's own has been executed at the time of writing.

## Trust anchor (run before anything else, recorded in RESULTS.md)

- `python3 liber-primus/tests/validate.py` — must print ALL VALIDATIONS PASSED.
- `python3 liber-primus/benchmark/gates.py` — must print 7/7.

Both were run first and both passed (recorded in RESULTS.md §0). If either had failed this
lane would report INCONCLUSIVE and stop.

---

## Sub-attack A — THE ENGLISH-ONLY SCORER

**Hypothesis A.** Every adjudication in this repository — B-04's 6,224,300 decodes, R16-KDF's
692,064, R16-PRNG's 52,556, Round 8's 2.52 × 10⁹, Round 17's ≈14.5 × 10⁹ offsets — is decided by
`lp.score.Quadgram.score_norm`, a quadgram model trained on four modern-orthography English books
(KJV, Moby-Dick, Pride & Prejudice, War & Peace; see `data/BUILD-QUADGRAMS.md`), against a fixed
English band (≥ −5.5). If the LP2 plaintext is not in that register, the **correct key** scores
below the bar and every one of those negatives is conditional in a way no ledger entry states.

This is **not** the question Round 10b lane B6 answered. B6 asked *can a non-English payload be
detected from the ciphertext alone* (monoalphabetic-invariant detectors, plus LM windows over
decode families). A asks *does the instrument recover and pass the **correct key** when the
plaintext is not modern English*. B6's own §0 states the archive cannot answer that, because the
archive was filtered by the metric being bypassed.

### A-i instrument and controls

Instrument, unchanged from the repo: `benchmark/plant.plant(key=…, mechanism='skip',
supp=0.83)` → `skipdecode.beam_decode(C, K, sign=-1, o=0, beam_w=400, max_skip=3)` →
`Quadgram.score_norm`. Recovery measured on **rune indices** (AGENTS.md §4).

- **Positive control:** the `EN_MODERN` panel (held-out English prose, not in the quadgram
  training set) must recover at ≥ 0.95 rune-index recovery and score ≥ −5.2 at every segment
  length tested. If it does not, the panel machinery is broken and A reports INCONCLUSIVE.
- **Null panel:** uniform-random rune plaintext, correct key. Establishes the floor.
- **Wrong-key arm:** for every panel, the same ciphertext decoded under a wrong key, to confirm
  the measured drop is a property of the plaintext register and not of the plant.

### A-ii panels (registers), fixed now

`EN_MODERN` (held-out English), `EN_KJV` (in-training English, upper bound), `LP1_REAL` (the
five solved LP pages' actual plaintext transliterations from `SOLVED-PAGES.json`), `LATIN`
(Caesar + Principia), `OE` (Old-English Beowulf lines + the OE rune poem),
`DE`, `CY` (Welsh) as extra non-English references, `EN_NOVOWEL` (all of A E I O U Y dropped),
`EN_HALFVOWEL` (half the vowels dropped), `RAND` (uniform runes).
Segment lengths **L ∈ {31, 120, 240, 400}** — chosen because they are the lengths the repo's
own sweeps actually scored at (R17 short-pad heads 25–44; B-04's null calibration L=120;
gate length 240; R17/A1 escalation head 400). 12 independent replicates per (panel, L), each a
different text window and a different plant seed.

### A-iii pre-registered decision rules (fixed, not editable)

1. A panel is **INVISIBLE** to the repo's instrument at length L if its **median** correct-key
   beam `score_norm` is **< −5.5** (the repo-wide bar in `PROBLEM.json` and in every sweep's
   HIT rule). "Invisible" means: had that been the true plaintext register, the correct key
   would have been recorded as noise.
2. A panel is **DEGRADED** if its median correct-key score is ≥ −5.5 but its median rune-index
   recovery is < 0.85 (the `benchmark/gates.py` MIN_RECOVERY constant).
3. **Verdict FOUND-ERROR for A** iff at least one panel that is a *plausible* register for LP2
   — i.e. one of {LP1_REAL, LATIN, OE, EN_NOVOWEL, EN_HALFVOWEL} — is INVISIBLE at L = 120 or
   L = 400, **and** no ledger entry states the English-register conditionality. Otherwise
   NO-ERROR-FOUND for A.
4. **Re-scoring the archive** (the never-run `campaign14/REDTEAM-PROPOSALS.md` line ~155 item,
   restricted here to sweeps that post-date B6): mine every stored candidate decode
   (`top50` / `top20` `head` fields) from round13/B04, round16/KDF, round16/prng and round17
   P0–P3, and re-score under the B6 rune-space LMs (EN/LA/DE/CY/OE) and a decrypt-IoC·N gate.
   Flag = z ≥ 4.0 against a length-matched random-rune null **and** above that null's maximum
   (B6's rule, adopted verbatim so the two are comparable).
5. **Power of that re-scoring**, computed and reported whether or not it flags anything: using
   the measured panel distributions from A-ii and each sweep's own recorded score histogram,
   compute P(a correct non-English key would have entered the sweep's stored top-N). If that
   probability is < 0.05, the re-scoring in rule 4 is declared **UNDERPOWERED** and its null is
   reported as an unknown, not as a negative.

---

## Sub-attack B — BEAM POWER ENVELOPE

**Hypothesis B.** `skipdecode.beam_decode` admits a key skip only when *every* skipped key
position would have reproduced the previous cipher rune. That validity test is exact for the
pinned `encipher_keyskip` model and for nothing else. Constructions that desynchronise the key
for any other reason are therefore not merely harder for the beam — they are **excluded by its
transition rule**, and the correct key is unreachable at any beam width.

### B-i instrument and controls

Same instrument. Plaintext held fixed at `EN_MODERN`/`DEFAULT_PLAINTEXT` throughout so that the
scorer is at full power and any loss is attributable to the decoder. Every construction is run
with (a) the correct key and (b) a wrong key.

- **Positive control:** construction `skip @ supp=0.83, max_skip=3, beam_w=400` must reproduce
  the published gate: correct-key score ≥ −5.2 and recovery ≥ 0.95. Recorded.

### B-ii constructions, fixed now

1. `supp` ∈ {0.0, 0.2, 0.4, 0.6, 0.83, 0.95, 1.0} under key-skip.
2. Mechanism: `skip`, `rewrite`, plus two never-tested placements — **key-side** (the keystream
   itself is generated doublet-free, rigid encipherment) and **plaintext-side** (plaintext
   doublets removed before encipherment). For each, also report whether it reproduces LP2's
   0.664 % ciphertext doublet rate, i.e. whether it is even a candidate mechanism.
3. Position-varying suppression: `supp(i)` ramping 0 → 1 across the segment; alternating
   per-page blocks; and a single burst.
4. **Free key drift** — with probability q ∈ {0.002, 0.005, 0.01, 0.02, 0.05} the encipherer
   advances the key one extra symbol for a reason unrelated to the doublet rule (an
   interrupter, a line break, a discarded draw). This is the construction the beam's validity
   test cannot represent.
5. **Rejection-consumes-draws** drift: on rejection the key advances by 2 rather than 1; and a
   variant where the rejected draw is discarded and never re-tested.
6. Low-entropy pads: keystream with constant runs of length r ∈ {1, 2, 4, 8, 16}, at
   `max_skip` ∈ {3, 8}.
7. `max_skip` ∈ {1, 2, 3, 5, 8} and `beam_w` ∈ {50, 120, 400, 1000} at `supp = 1.0`.

### B-iii pre-registered decision rule

For each construction, the instrument **provably misses** it if the **correct key** scores
< −5.5 (median over ≥ 5 seeds at L = 240). The power curve is the boundary in each parameter.
**Verdict FOUND-ERROR for B** iff at least one construction that (a) reproduces LP2's observed
doublet rate to within ±0.3 pp and (b) is not already named in any ledger `not_covered` field,
is provably missed. Otherwise NO-ERROR-FOUND for B.

---

## Sub-attack C — THE BARS AND THE ARITHMETIC

Every number below is re-derived from raw data with independently written code; agreement with
the published value is the pass criterion, disagreement is the finding.

1. **Headline statistics** — n, doublet count and rate, IoC·N, entropy, lag-1 suppression
   (published 80.75 %). Recomputed from `PROBLEM.json`'s pinned runes.
2. **The G3 doublet-deficit floor** (published `min_d Pdp(d)` = 1.38–1.83 % over four English
   corpora, "no natural-language plaintext" reaches 0.664 %). Recomputed, and — the red-team
   extension — computed for **Latin, Old English, German, Welsh, the real solved-LP register,
   and vowel-dropped English**, none of which the published floor covers. Pre-registered
   trigger: if any of those registers has `min_d Pdp(d)` ≤ 0.80 % (the observed 0.664 % plus its
   ~2 SE sampling allowance at 86 doublets), the "the key must be output-aware" step is
   **English-conditional** and must be restated.
3. **`threshold_for()`** — verify that `DEFAULT_MU`/`DEFAULT_BETA` are an exact zero-degree-of-
   freedom two-point solve rather than a fit; quantify the sampling error of β when each anchor
   is a single observed maximum; test the model **out of sample against every recorded sweep
   maximum in the repo** (B-04 A/B/C/D, R16-KDF, R16-PRNG, F-01, R17 P0–P3). Pre-registered
   trigger: a residual larger than 3 Gumbel SD (3 × βπ/√6) at any lane means the constants do
   not transfer to that lane and any bar computed from them there is not calibrated.
4. **Segment-length transfer.** `null.py` documents its constants as "L~120 segments, skip-aware
   beam" at `beam_w=400`. Measure μ and β directly at (L, beam_w) ∈ {(31,120), (120,400),
   (400,120)} with n = 200 shuffle nulls each. Pre-registered trigger: if β at L = 400 differs
   from `DEFAULT_BETA` by more than a factor 1.5, then every `threshold_for()` value R17
   reported for its head-400 and head-25..44 lanes is mis-calibrated, and the direction of the
   error (too strict / too lax) is reported.
5. **Bar-at-own-N audit.** For each major sweep, compute `threshold_for(N)` at that sweep's own
   N and check what the sweep actually compared against. Report the N at which the −5.5 floor
   stops binding.
6. **Multiple-comparisons tally (B-17, "frozen at 5 across Rounds 8–9")** — recomputed honestly
   over every round to date, at three levels of granularity (pre-registered hypotheses,
   configurations, decodes), with the repo-wide family-wise bar each implies.

**Verdict FOUND-ERROR for C** iff any published load-bearing number fails to reproduce, or any
bar was computed with constants that item 3 or 4 shows do not transfer to the lane that used it.

---

## What this lane will NOT do

Re-run any sweep (rule 7). No new keyspace is searched. Nothing here can produce a solve; the
only outputs are power measurements, restated coverage bounds, and corrections.

## Files

`PREREG.md` (this), `a1_scorer_language.py`, `a2_rescore_archive.py`,
`b1_power_envelope.py`, `c1_bars.py`, `RESULTS.md`, `ledger.json`, plus the raw
`out_*.json` each script writes.
