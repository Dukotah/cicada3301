# Round 28 · Lane L2 — contested-bytes: independent blind read + variant-enumerated keytest · RESULTS

_2026-09-08. Pre-registration: [`PREREG.md`](PREREG.md) incl. **Amendment 1** (anti-repeat
re-scope, dated and written BEFORE any run). Mode: run-now-light, nice 15, single-threaded._

Trust anchor before work: `python3 liber-primus/tests/validate.py` → **ALL VALIDATIONS
PASSED (5/5)**. S2 (round27 grind27, PID 494140) untouched throughout.

---

## 0. Anti-repeat audit — the lane premise was partly wrong, and the lane was re-scoped

The planner's charter said "no ledger row adjudicates their values and P-7's cheap
Cartesian enumeration was never executed". The ledger audit (coverage/not_covered fields)
falsified the first half: **`A-04`** (Round 19 C1) adjudicated ALL 11 witness-conflict
cells with a validated pixel instrument (blind 40/40 gate, 100 % case-ambiguous;
single-template regime 100 % case-ambiguous; 29,161-pair separation licence), resolving
the 6 pre-registered cells to their canon majority values and flipping 3 token-split
cells (45→107, 50→47, 246→198 = `round19/C1/payload_resolved.bin`). What remained
genuinely un-run (Amendment 1, verified against A-04/B-05 `not_covered`/`reopens_if`):

1. an **independent BLIND transcription** of the conflict cells — A-04 `not_covered(e)`,
   and the exact condition its `reopens_if` names;
2. cells **186 / 209 / 210 / 211** — never verified by any pixel instrument
   (A-04 `not_covered(a),(b)`: L5's splitter failed on 186/210/211, mis-segmented 209);
3. the **direct-key battery** (`pp49_51/keytest.py`: additive/Beaufort/atbash, per-page,
   offset sweeps) over the contested-cell Cartesian product and over
   `payload_resolved.bin` — keytest had only ever seen `maj`/`decpref`; B-05's 64
   combination masks ran only through its PRF-expansion grid; C1's propagation re-ran
   only the B-05 PRF grid.

Both deliverables below are those gaps, not a re-run of measured ground.

---

## 1. Read half — independent blind read (`reader.py` → `reader_out.json`)

### 1.1 Instrument (independent of round18/L5 + round19/C1 by construction)

- **Own segmentation**: 4-connected components in the central table band, dot-merge,
  line clustering, deterministic (0,1)(2,3)…(14,15) glyph pairing — no reuse of L5
  `grid.py`/`grid.json`. Hard-stops on row-count mismatch. Result: **80/104/72 = 256
  cells, all pages**, including the 4 cells L5's column-gap splitter could not segment.
- **Own matcher**: normalized cross-correlation over ±3 px shifts (L5/C1 used IoU),
  plus two geometry features NCC alone would waste — height ratio and cap-line offset
  (the physically discriminative axes for I/l/i and W/w per C1 §1.6).
- **Labels**: templates drawn ONLY from the 245 witness-unanimous cells
  (relikd tok = scream tok = scream decimal), lowest-index exemplar per class —
  never from canon at a conflict cell.

### 1.2 Positive control (gate) — passed at the pre-registered bar

Blind seeded sample (seed 3301) of **100** witness-unanimous non-exemplar cells,
single-template regime: **100/100 exact-token** (both glyphs correct);
minimum margin among correct reads **0.0833**. Gate bar was 100/100 → reader trusted.
(First gate attempt scored 78/100 due to a control-design bug — sampled cells that were
themselves the single exemplar of their class had their class deleted by `skip_self`;
fixed by drawing the sample from non-exemplar cells, the same regime as A-04 Control 3.
The bug was in the control harness, not the classifier; recorded here per doctrine.)

### 1.3 Blind verdicts — 15 cells, 3 passes each (pad 0/1/2 px), then unblinded

| idx | class | blind read | canon | A-04 resolved | agree A-04 | 3-pass margin |
|---|---|---|---|---|---|---|
| 25 | contested-6 | `3I` = 198 | 198 | 198 | YES | 0.203–0.214 |
| 175 | contested-6 | `0I` = 18 | 18 | 18 | YES | 0.203–0.214 |
| 182 | contested-6 | `2l` = 167 | 167 | 167 | YES | 0.238–0.257 |
| 199 | contested-6 | `0l` = 47 | 47 | 47 | YES | 0.238–0.257 |
| 215 | contested-6 | `1O` = 84 | 84 | 84 | YES | 0.082–0.085 † |
| 237 | contested-6 | `0W` = 32 | 32 | 32 | YES | 0.440–0.445 |
| 45 | token-split | `1l` = **107** | 81 | **107** | YES | 0.238–0.257 |
| 50 | token-split | `0l` = **47** | 21 | **47** | YES | 0.238–0.257 |
| 165 | token-split | `0I` = 18 | 18 | 18 | YES | 0.203–0.214 |
| 172 | token-split | `2S` = 148 | 148 | 148 | YES | 0.241–0.253 |
| 246 | token-split | `3I` = **198** | 224 | **198** | YES | 0.203–0.214 |
| 186 | unverified | `0J` = 19 | 19 | 19 | YES | 0.380–0.402 |
| 209 | unverified | `2t` = 175 | 175 | 175 | YES | 0.458–0.476 |
| 210 | unverified | `06` = 6 | 6 | 6 | YES | 0.383–0.399 |
| 211 | unverified | `11` = 61 | 61 | 61 | YES | 0.350–0.361 |

† idx 215 (`1O` vs decimal's `05`): margins 0.0818–0.0850 straddle the control minimum
0.0833 — below the pre-registered **change** bar. Since the verdict KEEPS canon, no
change is proposed and the bar is not invoked; noted because 215 was also A-04's
weakest cell (IoU 0.9993 vs 1.0000 elsewhere). Two independent instruments now read it
`1O` unanimously.

### 1.4 What this means

- **All 11 conflict cells: the independent blind read agrees with A-04 100 %**,
  including all 3 byte flips. A-04's `reopens_if` condition ("an independent BLIND
  transcription … disagrees") is **NOT triggered**; its `not_covered(e)` is closed as
  far as a second independent instrument on the same 400-DPI masters can close it.
- **Cells 186/209/210/211 verified for the first time** (A-04 `not_covered(a),(b)`
  closed): all four match canon. Every one of the 256 payload cells has now been
  pixel-verified by at least one validated instrument, 252 by two.
- The 6 pre-registered contested cells are **confirmed at their canon values** —
  the correct payload remains `payload_resolved.bin` (canon + 45→107, 50→47, 246→198).
  `C-CANON-PAYLOAD-3BYTES` stays a coordinator decision; this lane adds a second
  independent instrument's agreement to its evidence file, nothing else.

---

## 2. Decode half — variant-enumerated direct-key battery (`keysweep.py`)

### 2.1 Family

2 bases (canon majority; `payload_resolved`) × 2⁶ contested-cell masks
(cells 25/175/182/199/215/237 ∈ {token, decimal} readings) = **128 payload variants**,
verified corners: `b0m00` = `canon_256.bin`, `b0m63` = `canon_256_decpref.bin`,
`b1m00` = `payload_resolved.bin`. All 128 distinct mod 29 (asserted at runtime).
Battery identical to `pp49_51/keytest.py`: forward + reversed stream × sign ±1 ×
atbash × Beaufort (deduped) × offsets (0–255 on pages ≤ 400 runes, 0 otherwise) over
55 unsolved pages + whole corpus = 56 targets, ≈168,972 configs/variant,
**≈21.6 M decodes** total.

### 2.2 Plant control — passed (and it caught a real aiming flaw first)

English plaintext (131 runes) enciphered with variant `b0m37` at offset 160, pushed
through the REAL pipeline (all 128 variants × full battery on the plant target):
**top-1 = b0m37, config `f sign-1 off160`, recovery 1.000 (≥ 0.90 bar), HIT=True**,
runner-up strictly below (−4.333 vs −4.317).
First plant attempt used offset 42, whose 131-rune key window touches NONE of the six
contested cells — all 64 masks tie and the control failed. That failure is the control
doing its job (a hit at such an offset could not identify the variant); the plant was
moved to offset 160, whose window covers all 6 contested cells + cell 246
(`plant_control.json` records the passing run; the off-42 lesson is recorded here).

### 2.3 Null calibration and family-wise bar

12 shuffled-payload keys (histogram-preserving, order-destroying) through the identical
battery; Gumbel fitted from order statistics per `benchmark/null.py` doctrine
(never bulk sd). `null_calibration.json` (run, PASSED): per-run E[max] ≈ −6.3726
(mean of 12), pooled max@2,027,664 = −6.2101 → μ = −7.1975, β = 0.0654;
**family-wise bar (N = 21,628,416, α = 0.01) = −5.7923** (historical single-battery bar
−5.2 carried report-only, not used).

### 2.4 Sweep result — NEGATIVE, complete (2026-09-15)

Execution note: the first `keysweep.py` process died mid-sweep at 74/128 variants when
the host slept; the sweep was resumed with `resume_sweep.py` (deterministic battery,
identical row format; the 74 complete variants' rows were kept, the partial variant
re-run in full; `sweep_summary.json` records `resumed: true, kept_variants: 74`).
Final state verified: **7,168 rows = 128 variants × 56 targets, no gaps** (asserted at
summary time).

| | |
|---|---|
| decodes evaluated | **21,628,416** (128 × 168,972) |
| family-wise bar (α = 0.01) | **−5.7923** |
| rows ≥ bar | **0** |
| near-bar (within 0.15) | **0** |
| best score anywhere | **−6.350** — `b0m16…23`, page54(len76), `r sign-1 beaufort off237` |
| historical −5.2 bar | nothing within 1.1 of it either |

The global best (−6.350) is **below the pooled null maximum (−6.2101)** from the
12-run calibration — the sweep's extreme value sits inside the null's, which is the
cleanest possible NULL: no near-miss to agonize over, nothing dropped silently. The
8-way tie across masks 16–23 is expected mechanics, not signal: at that page/offset the
131-byte key window misses the cells those masks differ in, so the streams coincide.
R3 stats (IoC·N, min-distinct-32, panel-EN, best non-English z + register, zlib ratio)
are persisted on every one of the 7,168 rows (`sweep_rows.jsonl`), so this negative
remains reinterpretable under future registers.

---

## 3. Coverage × power

**Read half (complete).** Coverage: 15 previously-unverified-by-a-second-instrument
cells (11 witness-conflict cells + 4 never-pixel-verified cells 186/209/210/211) read
blind by an instrument built independent of L5/C1 by construction. Power: the reader
passed a 100/100 exact-token gate on witnessed non-exemplar cells (min correct-read
margin 0.0833) before any conflict cell was unblinded.

**Decode half (complete).** Coverage: 128 payload variants (2 bases × 2⁶ contested-cell
masks, all distinct mod 29) × 56 targets (55 unsolved pages + whole corpus) ×
the full keytest construction set = 21,628,416 decodes, adjudicated against the
family-wise bar −5.7923. Power: the plant control recovered the planted variant top-1
at recovery 1.000 through the real pipeline (§2.2), and the planted-English score
(−4.317) clears the bar by 1.48 — a real additive-family key inside this variant space
could not have been missed.

**Not covered (decode):** (a) the full 2¹¹ joint product over all 11 conflict cells —
only the 2 bases × 2⁶ contested masks ran (the 5 token-split cells vary only jointly,
canon-corner vs image-corner, never independently; ≈1,920 joint variants unrun at
~32 s each ≈ 17 h, deprioritized because two independent 100 %-gated instruments now
agree on those 5 cells); (b) constructions outside the battery (PRF expansion is B-05's
axis, re-run on payload_resolved by C1's propagation; skip/drift relations are the S2
axis); (c) non-English-register hits are only as visible as the I2 panel makes them —
persisted z-scores allow re-adjudication. Reopens if: a new witness reading outside
the recorded ones, a higher-DPI master, or a battery-family extension.

## 4. The three conditionals of the negative

1. **Key space:** the additive/Beaufort/atbash direct-key battery (`pp49_51/keytest.py`
   construction set) over the 128 contested-cell payload variants + reversed streams +
   offset sweeps; NOT the PRF-expansion / hash-derived key families (B-04/B-05 axis) nor
   keys outside this battery.
2. **Transition model:** direct additive substitution mod 29 (+ Beaufort/atbash), no
   rejection-loop / skip relation.
3. **Register:** the round19/I2 panel adjudicator + English quadgram score of record.

(Read-half conditional: same 400-DPI page masters; a third instrument or higher-DPI scan
could in principle still differ — see idx 215's straddling margin, §1.3 †.)

## 5. Verdict

**Read half — FINAL: canon stands.** An independent blind transcription agrees with A-04
on **all 11 witness-conflict cells at 100 %**, including all three byte flips
(45→107, 50→47, 246→198); A-04's `reopens_if` ("an independent BLIND transcription …
disagrees") is **NOT triggered**. Cells 186/209/210/211 are pixel-verified for the first
time and match canon — every one of the 256 payload cells is now verified by ≥1 validated
instrument, 252 by two. The correct payload remains **`round19/C1/payload_resolved.bin`**;
`C-CANON-PAYLOAD-3BYTES` stays a coordinator decision, now carrying a second independent
instrument's agreement.

**Decode half — NEGATIVE.** 21,628,416 decodes over the complete 128-variant family,
0 above the family-wise bar, 0 near-bar, best score inside the null's own extreme range.
Under this battery's construction set and register panel (§4), **no contested-cell
reading variant of the pp49-51 payload keys the runes as a direct additive/Beaufort/
atbash stream** — the conditional "a contested byte hides the key" is now closed for
this construction axis in both directions: the bytes are read (twice, independently)
AND the reading-variant space is swept. Nothing was FLAGGED-FOR-ORACLE because nothing
crossed or approached the bar.

Per doctrine R7: this is a measured bound, not a terminal verdict — the reopening
conditions are listed in §3.
