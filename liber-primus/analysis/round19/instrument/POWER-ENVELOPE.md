# Round 19 — LANE 1 — INSTRUMENT POWER ENVELOPE — RESULTS

_Run 2026-10-01. Doctrine `liber-primus/ARMADA-DOCTRINE.md` (R1/R2). This is the ≈30 %
instrument share: it measures the decoder+adjudicator power for the derived-key hypothesis
class across **both** axes, so every other Round-19 lane's null means something._

Machine-readable, for Lane 2 to cite cell-by-cell:
- `power_table.json` — 1,386 rows, one per (register × construction × L × key_family × seed),
  every row carrying its R3 columns.
- `power_summary.json` — 198 per-cell medians + both-axis power numbers.
- `anend_row.json` — the AN-END-class ground-truth row (totient keystream + F-interrupters).

Reproduce: `PYTHONUTF8=1 python3 power_envelope.py` then `python3 anend_row.py`.

---

## 0. Headline (what this lane changes)

R18-L7 measured the two axes **separately and never crossed**, and it scored every
non-English register with the **English quadgram scorer only** — so its near-zero
non-English powers were confounded: they measured "English scorer on foreign text," not
"can a matched instrument see a foreign plaintext at all." This lane crosses the axes and
adds a **matched per-register rune-space LM** to the adjudicator. Three facts fall out:

1. **The foreign-register nulls were a scorer artifact, not a cipher fact.** Handed the
   correct key, the beam recovers **100 % of runes** for Latin, Old English, German and Welsh
   under the pinned keyskip construction. The English quadgram scorer then rates them
   INVISIBLE (power 0.00–0.71). A **matched rune-space trigram LM** rates every one of them
   at **power 1.00**, separating the correct key from a wrong key by a margin of **+0.58 to
   +0.83** log10/trigram. **Every prior non-English negative in this repo is therefore an
   instrument artifact and carries no information about the cipher.**

2. **The construction hole (R18-L7-B) is real, register-independent, and the dominant loss.**
   `skip_by_two` — the one-character variant that burns key at a different rate — collapses
   rune recovery to **10–41 %** across *every* register. This is a DECODER loss: it is present
   even in English where the scorer is at full power, and the matched LM cannot rescue what
   the decoder never recovered.

3. **The instrument cannot read a page the project has already solved.** On an AN-END-class
   construction (totient keystream `φ(prime)=p−1 mod 29`, shift-down, + F-interrupters), the
   live keyskip beam recovers **14.4 %** and scores it −7.04 (noise); the interrupter-aware
   oracle with the correct interrupter set recovers **100 %**. The beam's transition relation
   is keyskip, so it is blind to the interrupter construction. **This is a FOUND-ERROR (R6):
   any Round-19 lane whose key hypothesis implies an interrupter page MUST run the
   interrupter-aware solver, not the keyskip beam.**

---

## 1. Instrument under test (unchanged from the repo; adjudicator extended)

| part | what |
|---|---|
| decoder | `skipdecode.beam_decode(beam_w=400, max_skip=3)`; `rigid_decode` for the rigid cell only (doctrine 4.3: never rigid-decode LP2 — here rigid is a measured ground-truth cell, not an LP2 decode) |
| adjudicator A (continuity) | `lp.score.Quadgram.score_norm` — the repo default, English, the bar every prior null used |
| adjudicator B (matched EN) | round16 English-via-runes matched quadgram |
| adjudicator C (matched register) | per-register rune-space **trigram** LM, `detectors.build_trigram`, trained on the FIRST HALF of each register corpus; plants drawn from the SECOND HALF so no cell is scored on its own training text |
| recovery | measured on **rune indices** (doctrine mechanics 5) |
| null | wrong key `[(i·7+13) mod 29]`, **same construction**, per replicate |
| bar | `benchmark/null.threshold_for(1, segment_len=L)` — reported per cell, never a fixed −5.5 |
| key family | `sha256_ctr(seed=CICADA3301)` (the B-04/D3 live derived-key class); running/vigenere/prng as secondary controls |
| seeds | 7 per cell; lengths L ∈ {31, 120, 240, 400} |

Power definitions (R2):
- **power_en_quadgram** = fraction of correct-key replicates whose English-quad score clears
  the scale-corrected bar AND beats its own wrong-key null. (The continuity axis.)
- **power_matched_lm** = fraction of correct-key replicates whose matched-register-LM score
  beats the wrong-key matched-LM null. (The R2 power number.)

---

## 2. Power table — register × construction, L=240, key = sha256_ctr

### 2a. Median rune recovery (the DECODER's achievement, scorer-independent)

| register | rigid | keyskip | skip_by_two | rewrite | free_drift | drift_at |
|---|--:|--:|--:|--:|--:|--:|
| EN        | 100% | 100% | **11%** | 97% | 94% | 96% |
| LP1       | 100% | 100% | **22%** | 97% | 93% | 98% |
| LA        | 100% | 100% | **15%** | 97% | 98% | 93% |
| OE        | 100% | 100% | **35%** | 97% | 95% | 88% |
| DE        | 100% | 100% | **34%** | 97% | 96% | 94% |
| CY        | 100% | 100% | **13%** | 97% | 90% | 90% |
| EN_NOVOWEL| 100% |  83% | **41%** | 78% | 56% | 75% |
| RAND      | 100% |  34% | **11%** | 42% | 20% | 38% |

Reading: recovery is a property of the **decoder × construction**, essentially flat across
language registers (the three right-hand "soft" constructions recover ~90–98 % everywhere;
`skip_by_two` fails everywhere). RAND is the control: rigid recovers it trivially (no filter
to desync), but every doublet-filtered construction mangles it — as it must, since RAND has no
structure for the beam to lock onto.

### 2b. Power on the ENGLISH-QUADGRAM adjudicator (repo default — the continuity axis)

| register | rigid | keyskip | skip_by_two | rewrite | free_drift | drift_at |
|---|--:|--:|--:|--:|--:|--:|
| EN        | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| LP1       | 1.00 | 1.00 | 0.00 | 1.00 | 0.86 | 1.00 |
| LA        | 0.29 | 0.29 | 0.00 | 0.14 | 0.29 | 0.14 |
| OE        | 0.71 | 0.71 | 0.00 | 0.71 | 0.43 | 0.43 |
| DE        | 0.71 | 0.71 | 0.00 | 0.43 | 0.43 | 0.29 |
| CY        | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| EN_NOVOWEL| 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| RAND      | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

This is the table that indicts every prior null. **At 100 % rune recovery** (rigid/keyskip),
the English scorer gives Latin 0.29, Welsh **0.00**, vowel-dropped English **0.00**. A sweep
that found the correct Welsh or abbrev-English key under the pinned keyskip construction would
have **thrown it away**. The English quadgram scorer is powered ONLY for the EN/LP1 registers.

### 2c. Power on the MATCHED per-register-LM adjudicator (the R2 power number)

| register | rigid | keyskip | skip_by_two | rewrite | free_drift | drift_at |
|---|--:|--:|--:|--:|--:|--:|
| EN        | 1.00 | 1.00 | 0.71 | 1.00 | 1.00 | 1.00 |
| LA        | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| OE        | 1.00 | 1.00 | 0.71 | 1.00 | 1.00 | 1.00 |
| DE        | 1.00 | 1.00 | 0.86 | 1.00 | 1.00 | 1.00 |
| CY        | 1.00 | 1.00 | 0.71 | 1.00 | 0.86 | 1.00 |
| EN_NOVOWEL| 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| LP1 / RAND| n/a — LP1 reuses the EN-matched scorer; RAND has no language LM (control) |

The matched LM **restores full power on every foreign register** for the recoverable
constructions. Its correct-vs-wrong-key separation at keyskip/L=240 is unambiguous:

| register | recovery | matched-LM (correct) | matched-LM (wrong key) | margin |
|---|--:|--:|--:|--:|
| EN         | 100% | −0.975 | −1.769 | **+0.794** |
| LA         | 100% | −0.969 | −1.793 | **+0.825** |
| OE         | 100% | −1.101 | −1.732 | **+0.631** |
| DE         | 100% | −0.943 | −1.707 | **+0.763** |
| CY         | 100% | −1.134 | −1.715 | **+0.582** |
| EN_NOVOWEL |  83% | −1.163 | −1.659 | **+0.496** |

Note the one place the matched LM **cannot** rescue: `skip_by_two`, where power dips (EN 0.71,
OE 0.71, CY 0.71) because the decoder recovered only 10–35 % of runes — there is nothing for
the LM to score. **A matched adjudicator fixes the register axis; it does nothing for the
construction axis. Both must be covered (R2).**

---

## 3. Length sensitivity of the construction hole

`skip_by_two` median recovery (keyskip beam, sha256_ctr):

| register | L=31 | L=120 | L=240 | L=400 |
|---|--:|--:|--:|--:|
| EN | 52% | 52% | 11% | 10% |
| LA | 32% | 43% | 15% | 30% |
| OE | 77% | 45% | 35% | 10% |

The miss **worsens with length**: a single unrepresentable key-advance event desynchronises
the beam for the entire remainder of the segment, so longer segments accumulate more
post-desync noise. Short pages can accidentally survive; full pages cannot. This is consistent
with R18-L7-B's −6.90 miss and extends it with the length dependence.

---

## 4. AN-END ground-truth row (FOUND-ERROR, R6)

AN-END (page 56 / 73.jpg): known method φ(prime) totient keystream (p−1 mod 29, shift-down)
+ F-interrupters. Built forward over a known English plaintext of the AN-END voice, then
decoded three ways (`anend_row.py`, median of 7 seeds):

| decoder | recovery | note |
|---|--:|---|
| keyskip BEAM (the live LP2 decoder) | **14.4 %** | score −7.04 = noise |
| rigid (totient key, interrupters not removed) | 14.9 % | — |
| interrupter-aware oracle (correct interrupter set) | **100 %** | plant is sound and recoverable |

The plant is provably recoverable (oracle = 100 %), yet the repo's live decoder reads it as
noise, because the keyskip beam's transition relation admits only doublet-driven key skips —
it has **no representation for an interrupter that removes a rune and does not advance the
key.** The interrupter-aware solver `src/lp/solve.py` exists and recovers it perfectly, but it
is **not** the decoder any derived-key sweep in this repo has used.

**This is the AN-END holdout result for the instrument lane: RECOVERED, but only by the
interrupter-aware solver, NOT by the keyskip beam that every sweep relies on.** (This lane does
not claim to blind-rediscover the keystream — that gate belongs to lanes that decode unsolved
pages; this lane measures whether the instrument can SEE the construction, and the answer is:
only if the interrupter-aware solver is in the pipeline.)

---

## 5. Secondary key families (the effect is a scorer/decoder property, not a key property)

EN, L=240, keyskip and rigid, across key families — all identical to the sha256_ctr cell:

| key family | rigid recovery | keyskip recovery | EN-quad | matched-LM |
|---|--:|--:|--:|--:|
| sha256_ctr | 100% | 100% | −4.32 / pow 1.00 | pow 1.00 |
| running (agrippa) | 100% | 100% | −4.32 / pow 1.00 | pow 1.00 |
| vigenere (DIVINITY) | 100% | 100% | −4.32 / pow 1.00 | pow 1.00 |
| prng (3301) | 100% | 100% | −4.32 / pow 1.00 | pow 1.00 |

Confirms R18's flagged not-covered: the register/construction power numbers above are
properties of the **scorer and the decoder**, independent of the key family. Lane 2 may cite
any key family's cell interchangeably for the derived-key class.

---

## 6. R3 columns (CI-ENFORCED) — persisted per row

Every one of the 1,386 rows in `power_table.json` carries, measured on the **correct-key
decode**: `r3_ioc_times_n`, `r3_min_distinct_32`, `r3_best_nonenglish_lm` (+ which register),
`r3_compressibility` (gzip ratio). Cell-level medians are in `power_summary.json`. These let a
later reader re-adjudicate any cell under a different register panel without re-running the
decode — the thing Round 10b failed to do (0/15 compliance) that made 10^10 decodes
permanently un-reinterpretable.

---

## 7. What this covers, what it does NOT, and what reopens each cell (R7 — bounds, not verdicts)

**Covered.** The (register × construction) power of the project's beam+adjudicator for the
derived-key hypothesis class, as a finite 8×6×4 grid × 7 seeds, with a matched-LM adjudicator
added to the register axis. Positive control (EN/keyskip = −4.32, 100 %, power 1.00) reproduces
R18-L7-A, so the harness is sound (Q5 kill-check passed).

**NOT covered (explicit):**
- **Constructions outside the six measured.** `skip_by_two` is covered as ONE transition hole;
  the general class of key-advance events the beam cannot represent is infinite. free_drift at
  q>0.02, multi-interrupter pages, and page-boundary key resets are not in this grid.
  *Reopens if:* a construction is proposed whose beam recovery at L≥240 is < 0.85 — it needs
  its own decoder before any sweep under it means anything.
- **Registers outside the eight measured.** Hebrew, Greek, enumerable abbreviation schemes,
  and mixed-register pages are not covered. The matched-LM method is shown to work; it has not
  been built for these. *Reopens if:* a register is hypothesised — train its trigram LM
  (minutes) and add the column before trusting a null over it.
- **The matched-LM adjudicator is a trigram, not the final word.** It cleanly separates
  correct from wrong key at these lengths, but its absolute power at L=31 and at < 85 %
  recovery is weaker (margins compress). *Reopens if:* a lane needs sub-120-rune adjudication —
  measure the matched-LM null at that L first.
- **AN-END keystream blind-rediscovery** is NOT attempted here (not this lane's job); only the
  instrument's ability to *see* the interrupter construction is measured.

**The one-line mandate this table hands to Lane 2:** a null is informative only inside the
cells where this table shows power ≥ ~0.8. For the derived-key class that means: **use a
matched register LM (not the English quadgram scorer) whenever the plaintext register is in
doubt, and do NOT trust any null under a construction whose recovery here is < 0.85 — build
its decoder first.**
