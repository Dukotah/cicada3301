# Round 19 — LANE 1 — INSTRUMENT POWER ENVELOPE — PREREGISTRATION

_Written before any measurement. Binding. Appended-only after first run._
_Doctrine: `liber-primus/ARMADA-DOCTRINE.md`. This lane is the ≈30% instrument share (R1/R2)._

## What this lane is and is not

This lane runs **no key-space sweep**. It measures the power of the project's decoder +
adjudicator across the **full cross-product** of two axes, for the derived-key hypothesis
class, so that every other Round-19 lane's null means something.

- **register axis** (adjudicator): English, Latin, Old English, Welsh, German,
  abbreviated/vowel-dropped English — plus the controls `EN_KJV` (in-corpus upper bound),
  `LP1_REAL` (the solved pages' own lossy orthography), `RAND` (floor), wrong-key.
- **construction axis** (decoder): `rigid`, `beam` (keyskip, the pinned form), `skip_by_two`
  (missed at −6.90 in R18), `soft-anti-repeat` (rewrite). Plus the R18-L7-B stressors
  `free_drift`/`drift_at` as the continuous version of the transition-relation hole.

The method is plant-the-correct-key: take solved pages + the AN-END plaintext as ground
truth, encipher under a known key×construction, decode with the **correct** key, record the
adjudicator score. The deliverable is `POWER-ENVELOPE.md` + a machine-readable
`power_table.json` that Lane 2 can cite cell-by-cell.

### Why this is new, not a re-run of R18-L7

R18 measured the two axes **separately**, never crossed:
- `round18/L7-redteam/a1_scorer_language.py` swept the **register** axis with construction
  held at the pinned `keyskip` beam, adjudicated **English-quadgram-only** (`out_a1.json`).
- `round18/L7-redteam/b1_power_envelope.py` swept the **construction** axis with plaintext
  held **English**, adjudicated English-quadgram-only (`out_b1.json`).

Neither measured (register × construction), and **neither scored any non-English register
under a matched non-English LM** — so L7-A's near-zero non-English powers are confounded:
they measure "English scorer on foreign text," not "can a matched instrument see a foreign
plaintext at all." This lane (a) crosses the axes and (b) **extends the adjudicator with
per-register rune-space LMs** (following the already-built, gate-passing but never-adopted
`analysis/round16/scorer/scorer.py`), then reports power on BOTH axes per R2.

---

## The Five Aiming-Test Questions (Doctrine §1)

### Q1 — What would a hit look like, and would THIS instrument recognise it?

A "hit" for this lane is a **measured power cell**: for a given (register, construction)
pair, the fraction of correct-key replicates whose decode clears `null.threshold_for(N,
segment_len=L)` under the **best-matched register LM**, together with the median
rune-index recovery. The planted shape is the exact object: ground-truth plaintext (solved
page / AN-END / register corpus) → enciphered by the named construction under a known key →
decoded with the correct key.

**Proof the instrument recognises the planted shape (recognizer, pre-run):**
- `benchmark/plant.py` already reproduces the LP2 surface signature (doublet 0.633% vs
  0.664%, IoC·N 0.9996, H 4.8567 — a FAIR proxy; verified this session) and exposes
  `.recovery()` on rune indices.
- R18-L7-A already demonstrated the positive control the recognizer must pass: planting the
  correct key over `LP1_REAL` and `EN_MODERN` under keyskip yields **100% rune recovery and
  score −4.2 to −4.33 at power 1.00** (`out_a1.json`). That is the proof the pipeline emits
  a recognisable hit when one is planted in English/LP1 register.
- The **new** recognizer claim this lane must prove before trusting any non-English cell:
  plant Latin under the keyskip beam, decode with the correct key, score under a **Latin**
  rune-space LM, and show the correct-key score clears the matched null while a wrong key
  does not. If the matched-LM recognizer cannot separate correct from wrong key on a planted
  foreign plaintext, the lane reports that the adjudicator is unfixable for that register
  (an honest negative instrument result), not a cipher result.

### Q2 — What measured fact raises this family's prior above the flat rate?

**Measured prior, with path:** `analysis/round18/L7-redteam/RESULTS.md` §A.1 + §B.1–B.2 and
their JSON (`out_a1.json`, `out_b1.json`). Two measured facts, each a file-backed number:
1. The adjudicator's measured power against a non-English **correct key** is 0.33 (Latin),
   0.00 (Welsh), 0.00 (vowel-dropped English) — and for vowel-dropped English the correct
   key scores **below** a wrong key (−7.60 vs −7.41). (`out_a1.json`, table §A.1.)
2. The decoder misses `skip_by_two` at **−6.90 / 25.8% recovery**, and raising beam width
   50→1000 and max_skip 1→8 changes the score by **exactly 0.000** (`out_b1.json`, §B.1–B.2).

These are not lore; they are measurements on the repo's own instrument. They establish that
**the power of every prior negative is unknown off the English/pinned-keyskip cell**, which
is exactly the quantity this lane measures. This lane is therefore **not** a completeness
ritual: it has a concrete, file-cited measured prior that the instrument's power is
non-uniform and in places zero, and its whole purpose is to turn that into a table.

### Q3 — Is the space bounded, and by what?

**Enumerable and small.** This lane sweeps no keys. The measured space is the finite grid:
~9 registers × ~6 constructions × 4 segment lengths (31/120/240/400) × ≥7 replicate seeds,
≈1,500 correct-key decodes total — plus the adjudicator panel (≤6 register LMs trained
once). This is a **finite, human-checkable object** (Doctrine §R5 rank 1): every cell is
named in advance and listed in `power_table.json`. No fog, no unbounded pad space.

### Q4 — The three conditionals the negative (here: each power cell) will carry

Every cell in `power_table.json` is explicitly tagged with all three (Doctrine §Q4):
1. **key space**: the key family planted (`sha256_ctr(seed=CICADA3301)` as the B-04/D3 live
   derived-key class; running-key and vigenere as secondary families to verify the effect is
   a scorer property, not a key property — R18 flagged this as not-covered).
2. **decoder transition model**: which construction the beam represents — one of
   {rigid, beam/keyskip, skip_by_two, rewrite/soft-anti-repeat, free_drift, drift_at}.
3. **adjudicator register**: which plaintext LM scored the decode — one of
   {EN-quadgram (repo default), LA, OE, DE, CY, abbrev-EN rune-space LMs}, reported as both
   the English-only score (for continuity with prior nulls) AND the best-matched-register
   score (the R2 power number).

R3 columns persisted for every row: **decrypt IoC·N**, **min distinct symbols over a 32-rune
window**, **best non-English LM score over the register panel**, **compressibility** (gzip
ratio of the rune-index byte stream). `validate_ledger.py` enforces their presence.

### Q5 — Kill condition at 10% of budget

**Checkpoint (first ~150 decodes):** run the English/keyskip positive control cell plus the
Latin/keyskip matched-LM recognizer cell.
**Kill condition:** if the English/keyskip positive control does NOT reproduce R18-L7-A's
≈−4.3 / 100%-recovery / power-1.00 cell (i.e. the planted hit is not recognised by the
baseline instrument), the lane is **mis-wired** — stop, fix the harness, do not report any
power table. A null from an unvalidated instrument is not a negative (Doctrine §4.2). This is
the single observation that abandons the run early.

---

## Recognizer, positive control, null, threshold (explicit)

- **Recognizer**: correct-key decode scores above `null.threshold_for(N, segment_len=L)`
  under the matched-register LM; recovery measured on **rune indices**.
- **Positive control**: English/keyskip cell must match R18-L7-A (−4.2..−4.33, 100% rec).
- **Null**: wrong-key decode per cell (same construction), AND a shuffle/register-null per
  `null.py`. Power = fraction of correct-key replicates separable from the null.
- **Threshold**: `benchmark/null.py: threshold_for(n_trials, segment_len=L)` — reported per
  cell, never a fixed −5.5 (Doctrine §4.4). Never rigid-decode LP2 (§4.3).

## AN-END holdout

This lane claims **no decode of any unsolved page**, so the AN-END blind-rediscovery gate
does not gate this lane's deliverable. BUT AN-END (page 56 / 73.jpg; φ(prime) totient
keystream, p−1 mod 29 shift-down, + F-interrupters) is **used as a second ground-truth
plant** in the power table: its known plaintext and known keystream give a non-synthetic
positive-control row whose construction (totient keystream + interrupters) is a real,
non-keyskip transition model. Reported outcome: whether the current beam + any matched LM
recognises AN-END's correct-key decode, i.e. whether the instrument can even see a page the
project has already solved. If it cannot, that is a FOUND-ERROR about the instrument.
Artifacts available: `analysis/anend_hunt/`, `SOLVED-PAGES.json`.

## Deliverables

- `analysis/round19/instrument/POWER-ENVELOPE.md` — narrative, both-axis power tables,
  what reopens each cell (R7 bounds not verdicts).
- `analysis/round19/instrument/power_table.json` — machine-readable, one row per
  (register, construction, L, key_family) with all R3 columns + both-axis scores, for Lane 2.
- Per-register rune-space LMs (trained once, committed as scripts; corpora gitignored).

## Pass/fail

This is a measurement lane; it does not "pass" or "fail" a hypothesis. It succeeds if it
emits a complete, R3-compliant power table whose English/keyskip cell matches the known
positive control. It reports FOUND-ERROR (R6) if any cell reveals the adjudicator cannot
recognise a correct-key decode of a register/construction the project has treated as covered.
