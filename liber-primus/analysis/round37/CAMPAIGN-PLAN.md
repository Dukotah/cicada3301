# Round 37 — THE UNTRIED READINGS (pre-registration / plan of record)

_Drafted 2026-10-30 as Round 36 closed. Binding doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Seeded
by Round 36 O4's clue-coverage matrix ([`../round36/O4-clue-coverage/untried.md`](../round36/O4-clue-coverage/untried.md)),
Round 36 X1's critic list, and the owner's stated theory (2026-10-30): "the clues given were never used well, not that
information is missing." Each lane's `PREREG.md` is authoritative once written and is dated before its first output;
addenda go in a separate dated file._

## 0. Thesis — the clues have been read, but not under the instrument that could hear them

Round 36 O4 built the first complete matrix of every signed or in-book clue sentence (154 entries) against every reading
family the repo has applied. The result is not "overlooked text" — every sentence has been considered by some round —
but **66 clue × reading cells that were never run, and 55 that were run only with the English-only scorer or the
single-relation legacy beam.** Among the never-run cells are the ones the clue text most literally supports: the three
clauses of the 2016 signed message ("its words are the map, their meaning is the road, their numbers are the direction")
applied *in composition* rather than one at a time; the solved first part's own numbers used as a key schedule over the
unsolved pages; and the signed clauses and remaining LP1 imperatives used as seeds or keys. None of these has a ledger
row. All are bounded (thousands of decodes, not billions), and the instrument that can adjudicate them — the
register-aware beam, the skip-tolerant screen, the twelve-register panel-R36 and the observed null — exists as of this
week. Under doctrine R5 these are rank-1 objects (finite, human-checkable, clue-derived), and under R4 their prior is
the clue text itself, cited.

The round also carries the tooling debt Round 36 X1 ranked first: nothing above can persist rows or screen heads under
twelve registers until `beam_v3`, the SWEEPROW writer and the hit predicates stop assuming nine.

**Not a target:** new generator families; the PHP tails; the Py2.7-MT S2 windows (parked until the exact-relation
control is independently validated and the sandbox lists are exported — recorded in §5).

## 1. Doctrine budget allocation

| share | goes to | lanes |
|---|---|---|
| **≈20%** | instrument debt — 12-register tooling; L-matched `free` null | T1, I1 |
| **≈45%** | bounded clue readings never run (R5 rank 1) | C1, C2 |
| **≈20%** | re-score the English-only / legacy clue readings under the repaired instrument | C3 |
| **≈15%** | red-team + closeout | X1 |

## 2. Lane roster

| ID | Type | Title | Compute | Gates on |
|---|---|---|---|---|
| **T1** | tooling | 12-register plumbing: `beam_v3` `PANEL_PATH`/`CLUSTERS` parameterised; SWEEPROW rows sized from the panel (both `adjudicate.py` copies, `check_r3_store`); `hitfn20`/`panelmax20` take `panel=`/`decoder=` and refuse a bar from a mismatched panel; tests | light | — |
| **I2** | instrument | pf_v4 recalibrated on twelve registers (lse over 12 LMs; thresholds re-frozen at FPR 1e-3; natural-rate power per register incl. GREEK/HEBREW/NORSE) and the bash orbit re-screened + survivors through v3 under panel-R36 (R36 B1 measured reach 0.91/0.68/0.64 with the nine-register screen) | ~60 min | T1 |
| **I1** | instrument | L-matched `free`-relation null at L ∈ {240, 400, 729} (O3: `free` pmax grows with L for every seed) + the O3 ILP32 `free` cell re-judged | medium | — |
| **C1** | bounded (flagship) | O4 U1+U2+U3 as one lane: the 2016 clauses and LP1 imperatives as seeds/keys; LP1's own numbers as a key schedule; map→road→direction composed at word boundaries | ~10k decodes | T1 |
| **C2** | bounded | O4 U4+U7+U8: "prime line sums" as a language-free recognizer clause (measure separation on solved pages first); signed numeric strings as book-code indices; per-page geometry readings of "numbers are the direction" beyond R22-B | light–medium | T1 |
| **C3** | re-score | O4 U5+U6: the Round 10 map/road cleartext streams (incl. the English-gated z=6.94 stream), Round 11 N1–N5/S1/S2, R22-C's 185 operations, under panel-R36 + beam_v3 + pf_v4 | medium | T1 |
| **X1** | red-team | this round + carry-overs (B1 R36 if the coordinator's audit left anything; I1 doc corrections; O4 reclassification) | light | last |

## 3. Lanes in detail

All decode lanes use `beam_v3` (panel_max) under keyskip1 + keyskip2 (+ `free` only where I1 has delivered an L-matched
bar), panel-R36 (`data/panels/panel-r36.npz`, sha a0682f0c…), bars from `round34/I1-v3-null/bars_v3.py` (and I1's
`free` extension), SWEEPROW rows persisted 12-wide (after T1), PREREG before the first output, planted controls before
nulls, no `git`.

---

### T1 — 12-register plumbing  _(tooling; everything else needs it)_

- **Q1.** Failing-then-passing tests: a 12-register store round-trips through `adjudicate.validate_store` and
  `validate_ledger.check_r3_store` (both must read the register count from the store HEADER, not default to 9 — R36 B1's
  276,242-row store currently fails them and sits undeclared as `sweep_store`; declare it once they pass); `beam_v3.panel_max` and `register_cond` run against panel-R36 with
  `PANEL_PATH`/`CLUSTERS` supplied (clusters derived from the panel's register list, not hard-coded 7); `hitfn20` /
  `panelmax20` called with `panel=panel-R36` refuse the Round 19 bar constants and require a bar computed for the
  supplied panel; the Round 35 B1 9-wide store still validates (backward compatibility). CI runs the new tests.
- **Q2–Q5.** Not a discovery lane; it is the debt Round 36 X1 ranked #1. Kill: none; scope creep is the risk — touch
  only the listed call sites and keep every existing test green.
- **Deliverable.** `round37/T1-12reg-plumbing/` — patches in place (listed with diffs in `RESULTS.md`),
  `tests/test_12reg_plumbing.py`, `ledger.json`.

---

### I1 — L-matched `free` null  _(instrument)_

- **Q1.** Planted correct keys under `free` at L ∈ {240, 400, 729} clear the fitted bar at N=1e6 in ≥19/20 seeds per
  register (recall Round 34 I1's control FAILED for `free` at L=120 on OE/CY/HALFVOWEL — measure, do not assume).
- **Q2.** O3 §"Decisions": `free` null median 5.2 / 7.5 / 11.2 at L=120 / 262 / 729; `bars_v3` has `free` only at
  L=120; the O3 ILP32 `free` cell at L=729 scored 15.15 vs a 100-draw null max of 14.33 and is unresolved.
- **Q3.** Bounded: ≥2,000 shuffled-LP2 wrong-key draws per L (free runs ~1–4 decodes/s at L≥400 → cap 90 min total;
  if L=729 does not fit, fit it from the other cells and say so). Then re-judge the O3 cell.
- **Q5.** If the planted control fails at any L, record that `free` has no usable bar there and B/C lanes claim no
  `free` reach at that L.
- **Deliverable.** `round37/I1-free-null/` — `null_free.json`, extension to `bars_v3.py` (family `free`, L grid),
  `control.json`, `o3_cell_rejudged.json`, `RESULTS.md`, `ledger.json`.

---

### C1 — The composed clue readings  _(flagship bounded lane; O4 U1 + U2 + U3)_

- **Q1 (recognizer).** Plant each construction before searching it: (U1) a known plaintext enciphered with one of the
  candidate seed/key strings under the repo's three key-derivation routes (direct key text → rune key; SHA-256-CTR of
  the string as in B-04; PBKDF2 as in R16-KDF) must rank #1 among the candidate list; (U2) a known plaintext enciphered
  with an additive schedule built from LP1's own word/line/sentence gematria sums (state every variant: per-word sum,
  per-line sum, running sum, mod 29 / mod 28) must be recovered ≥0.90 by the matching decoder; (U3) a known plaintext
  enciphered by the composed map→road→direction rule (word boundaries from the cleartext interrupters are unkeyed;
  "map" = the LP1 word list as a codebook, "road" = the semantic/positional index of each word, "direction" = that
  index applied as the key advance at each boundary — write the exact rule in PREREG, with the two or three most
  literal alternatives) must be recovered ≥0.90.
- **Q2 (prior).** The clue text itself, verbatim and signed (`round36/O4-clue-coverage/clues.json`: the 2016-01 message,
  VALID signature); `untried.md` U1–U3 show no ledger row for any of these; the nearest prior attempts (`round10b`
  legacy Vigenère keywords; campaign7 `wordsum_selfkey`, English-only, no row) are English-only/legacy-beam.
- **Q3 (bounded).** U1 ≈3–6k rows (all candidate strings × 3 routes × 2 relations × offsets 0..7); U2 ≈1–3k; U3 ≈2.8k.
  Total ≈10k decodes at L=120 ≈ 2 hours single-process; stream rows; cap 2.5 h.
- **Q4.** key space = the enumerated clue-derived candidates (listed in `candidates.json` with provenance);
  transition model = keyskip1 + keyskip2 (+ the composed U3 rule itself, which is a new relation and is planted);
  register = panel-R36, with pf_v4 power stated where a head screen is used (U1 only).
- **Q5 (kill).** Any planted construction not recovered → that sub-family is INVALID, not negative; stop it and say so.
- **Deliverable.** `round37/C1-composed-clue-readings/` — `candidates.json`, `enciphers_u2_u3.py`, `sweep.py`,
  `control.json`, `sweep_rows.jsonl`, `RESULTS.md` (per sub-family: control, decodes, best vs bar at actual N and
  N=1e6, flagged/near-miss, the three conditionals, not_covered), `ledger.json`, `ledger_patches.json` (F-02 and the
  Round 10 L2/L3 rows O4 flagged as missing).

---

### C2 — Recognizer and index readings  _(O4 U4 + U7 + U8)_

- **U4 prime line sums.** Measure first: on the six solved pages, what fraction of lines have a prime gematria sum
  (WARNING 9/9; WELCOME 3/5; SOME WISDOM 4/5 per O4) vs the same statistic on shuffled nulls. If separation at
  p<0.01 exists, add it as an *informational* SWEEPROW column (not a bar) and re-score the top-1,024 rows of R35-B1 and
  R36-B2 with it; if not, record the measured non-separation and stop (kill at ≤30 min).
- **U7 book-code indices.** The signed numeric strings (`clues.json` H7, H12 and the location numbers) as indices into
  LP1 (word / rune / line) and into the unsolved pages; planted control = a known index list recovering a known phrase;
  bounded (≤500 decodes).
- **U8 geometry.** "Numbers are the direction" as per-page turtle/coordinate renders with LP1 numbers as input and
  interrupter-gated pen-up, beyond R22-B (which used the unsolved pages' numbers): the recognizer is a planted glyph
  render; bounded (≤58 pages × ≤4 variants).
- **Deliverable.** `round37/C2-recognizer-index-readings/` — per-sub-family outputs, `RESULTS.md`, `ledger.json`.

---

### C3 — Re-score under the repaired instrument  _(O4 U5 + U6; the "Reopen" list)_

- **Q1.** For each reopened family, the original lane's planted control re-run under panel-R36 + beam_v3 (+ pf_v4 where
  the family screens heads) must pass before any re-score counts.
- **Q2.** Each family has a ledger row with an English-only / legacy-beam conditional (`R11-*`, `R22-C`, the Round 10
  L2/L3 streams via C1's patch) — the reopen condition the Round 36 audit wrote into `ELIMINATION-LEDGER.md`.
- **Q3.** Bounded: Round 10 L2/L3 cleartext streams (re-score only, no decode); R11 N1–N5/S1/S2 (re-run their top-N
  under v3, ≈2–5k decodes); R22-C 185 operations × keyskip1/2 (≈370 decodes at page length).
- **Q5.** Any row clearing its bar → L=240 → flagged-for-oracle per `HUMAN-ORACLE.md`.
- **Deliverable.** `round37/C3-rescore-reopened/` — per-family outputs, `RESULTS.md` (each family: control, N, best vs
  bar, conditionals now carried), `ledger_patches.json` (restate each reopened row with its 12-register conditional).

---

### X1 — Red-team  _(last)_

Targets: C1's planted constructions (are the composed rules the literal ones the clue supports, or convenient ones?);
C1's candidate list completeness against `clues.json`; C2's separation statistic (shuffle-null done right); C3's
controls; T1's backward compatibility on every existing store; I1's `free` control; Round 36 B1 if the coordinator's
audit left anything; the I1-R36 doc corrections and O4 reclassification applied; ledger patches; gate; Round 38 list.

## 4. Verification and hit protocol
As Rounds 32–36, now with `HUMAN-ORACLE.md` as the written path: any crosser produces the bundle (key/seed, relation,
offset, decoded text for ≥2 pages, the three verifier outputs, the panel argmax trace) and waits for the owner to read
two independent pages as language before any ledger status moves.

## 5. Recorded, not blocking
- S2 windows resume only after: the planted exact-relation control is independently validated; the sandbox top list /
  histogram are exported (snapshot `snap_fWma12lA…` expires ~2026-11-06); `top_S2.json` is re-scored under panel-R36.
- The PHP tier remainder (blocks 200–318 of the R32 stream, then a fresh stream) is low value per hour.
- Round 36 lane docs corrected by the coordinator for X1's findings (I1 reproducibility; O4 counts); B2/S1 ledger
  patches marked superseded.

## 6. Orchestration
- **Wave A (parallel):** T1, I1, and C2's U4 measurement; **I2 after T1** (it needs 12-wide rows) (no 12-register store needed for a measurement).
- **Wave B (after T1):** C1 (laptop, one process), C3 (after C1 or interleaved if RAM allows), C2's U7/U8.
- **Wave C:** X1; coordinator closeout (SYNTHESIS, ledger, nav docs, gate, commit to master, push).
Discipline unchanged: Sonnet; no `git` in lanes; own `round37/<lane>/` dir; nproc=1; stream to disk in append mode;
no `find /`; PREREG dated before first output; RESULTS.md + ledger.json written before replying; RAM check before heavy
runs.

## 7. Guardrails — do NOT re-run
Everything in Rounds 32–36 §6/§7; the bash orbit (R35-B1 / R36-B1); the PHP tiers as swept; the Round 36 O3 autopsy
(the near-miss is NOISE on three verifiers).

## 8. Definition of a good Round 37
The clue-derived readings the matrix found never-run are run, planted-control-gated, under the twelve-register
instrument, and each gets a ledger row with coverage × power and three conditionals; the English-only clue readings
are re-scored and restated; the tooling stops assuming nine registers; `free` has a bar at page length. A survivor would
be extraordinary; the round succeeds without one.
