# Round 22 — Lane C — THE FOUR LITERAL IMPERATIVES (X1 + X3 + X4)

_Pre-registered 2026-08-29, BEFORE any scoring on LP2. Binding doctrine:
[`../../../ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md). This file is frozen: thresholds are
not edited after a result is seen; corrections are appended as dated addenda._

## The thesis (roadmap Phase 4, ELIMINATION-LEDGER "X1–X4 remain OPEN")

The book issues signed imperatives. Round 11 read the *number channel* under seven lenses and
closed them (control-validated NEGATIVE), but it never **executed the koans as operations**. Lane
C does exactly that, for three signed imperatives, each as a *small enumerable operation set*:

- **X1 — "Do FOUR unreasonable things."** Enumerate the literal "four" readings and run each:
  (a) every 4th rune (the 4 phase-offset decimations); (b) apply the solved-page cipher ladder
  **4 times** (iterated shift/atbash re-application); (c) **4-way interleave / de-interleave**
  (read the stream as 4 braided columns, and its inverse).
- **X3 — "Question all things" / "test the knowledge."** Invert every assumption as an operation:
  (a) read the book **back-to-front as the ENCRYPTION order** — decrypt = re-encipher forwards on
  the reversed stream; (b) treat the **solved** pages as the CIPHER and the **unsolved** as the
  KEY (the deliberately-upside-down keying).
- **X4 — "the words OR their numbers."** Run each Phase-1 number lens (prime-value, prime-index,
  totient) **jointly with its letter twin** as a COMBINE instruction — the keystream is the number
  transform, applied to the letter stream, scored on the resulting letters. The "or" as "combine".

None of these is a Round-11 lens re-run: Round 11 read the *number streams as text / as autokey
feedback*; Lane C uses the number transforms as **keystreams over the letter stream** (X4) and
executes **structural** operations (decimation, iteration, interleave, reversal, role-inversion)
that no prior round performed. Red-team clause below checks this non-overlap explicitly.

---

## THE RECOGNIZER (built and validated before the search — doctrine Q1)

We reuse, unchanged and by citation, the Round-19/20 instrument stack — never the retired −5.5 bar:

- **Decoder:** `round19/I1/driftbeam.py` `beam_decode` (rune-index recovery, `PRESETS`).
- **Adjudicator:** `round19/I2/adjudicate.py` `adjudicate()` — the 9-register panel-max (`pmax`),
  power ≥0.90 in 27/27 registers (round19 I2 RESULTS). Registers:
  `EN_MODERN EN_KJV LP1_REAL LATIN OE DE CY EN_HALFVOWEL EN_NOVOWEL`.
- **Bar:** `round20/P3/panelmax20.py` `panelmax_bar(preset, n_round_adjudicated, alpha=0.01)` —
  the calibrated panel-max family-wise null. **Never −5.5, never a per-register `en` bar.**
- **HIT predicate:** `round20/HITFN/hitfn20.py` `is_hit(HitDecode(...))` / `evaluate(...)` — the
  recovery-gated three-clause decision: (1) `pmax ≥ panelmax_bar`; (2) rune-index recovery ≥ 0.90
  from the DECODE PATH not score; (3) held-out ¾ reproduces under the same key. This is THE
  recognizer. Verified LIVE at lane build time: its guard REJECTS the EN_NOVOWEL hallucinating
  decode (recovery 0.44/0.83) and ACCEPTS the genuine decode (recovery 1.00, pmax 26.4). Score
  alone is never a hit.

For the **structural / non-keyed** operations of X1 and X3 that produce a candidate *rune stream*
(not a key), the recognizer is the same adjudicator run directly on the produced stream:
`adjudicate(stream)` and require `pmax ≥ panelmax_bar` PLUS a language-agnostic corroborator
(IoC·N, min-distinct-32, compressibility), since there is no key to run the held-out clause on.
For those, a bar-clear is FLAGGED-FOR-ORACLE (roadmap seal note), never auto-certified.

## FROZEN THRESHOLDS

| gate | bar | source |
|---|---|---|
| keyed HIT (X4, X3-keyed) | `is_hit` == True (all 3 clauses) | `hitfn20.py` |
| panel-max clear | `pmax ≥ panelmax_bar(preset, N_adj, α=0.01)` | `panelmax20.py` |
| recovery clause | rune-index recovery ≥ **0.90** | `hitfn20.RECOVERY_BAR` |
| structural stream flag | `pmax ≥ panelmax_bar` at that lane's N_adj | `adjudicate` + `panelmax20` |
| **N_adj per sub-lane** | the actual count of decodes THAT sub-lane adjudicates | recorded at run time |

α = 0.01 (claim). Panel-max preset = `exact` for keyskip1 decodes, `drift` where the operation
demands drift tolerance; the preset used is recorded per row. **No fixed −5.5 anywhere.**

---

## The five Aiming-Test answers (doctrine §1)

**Q1 — What would a hit look like, would THIS instrument recognise it?**
A hit is a decode that clears the panel-max null AND recovers ≥0.90 of its rune indices from the
decode path AND reproduces on the held-out ¾ (keyed lanes), or a structural stream that clears the
panel-max null with a corroborating language-agnostic statistic (unkeyed lanes). The instrument is
proven to recognise it: **Phase 0 plants and recovers each operation's own hit shape** — a
4-interleaved known English text must be recovered by the X1 de-interleave; a back-to-front planted
cipher must be recovered by X3; a number-keystream-enciphered known text must be recovered by X4 —
and the HITFN guard already demonstrates the recognizer accepts a genuine decode and rejects a
hallucination. If a plant is NOT recovered, that operation is reported as an unvalidated instrument
(a null from it is not a negative), per doctrine mechanic 2.

**Q2 — What measured fact raises this family's prior above the flat rate?**
Each operation is a **direct, signed instruction in the book's own decrypted plaintext**: "do four
unreasonable things" (X1), "test the knowledge / question all things" (X3), and atbash page 01's
"either the words OR their numbers, for all is sacred" (X4). These are evidence — the author's own
signed text — not lore. Round 11's SYNTHESIS + the ELIMINATION-LEDGER explicitly record X1–X4 as
**OPEN** and never executed literally (`ELIMINATION-LEDGER.md`: "the roadmap's un-run lenses …
**X1–X4** the literal-imperative operations … are NOT covered by Round 11 and remain OPEN").

**Q3 — Is the space bounded, and by what?**
**Enumerable, small.** X1: 4 decimation phases + a bounded iterate-count ladder {2,3,4} × the
solved cipher families {shift 0..28, atbash} + 4-way interleave/de-interleave × {read-order,
column-order} ≈ low hundreds of operations. X3: 2 reversal readings × the solved cipher ladder
(≈60) + the solved-as-cipher / unsolved-as-key inversion over the solved-page keystream family
(≈ tens). X4: 3 number transforms × {+,−} sign × {atbash pre/post} × {value, index, totient} ×
offset 0 ≈ ~36 keystream configs over the 12,956-rune stream. Total ≲ few hundred decode/adjudicate
calls — enumerable in minutes, not a fog.

**Q4 — The three conditionals the negative will carry.**
Every row records (1) the **operation** enumerated (its bounded parameter tuple) = the "key space";
(2) the **decoder preset** (`exact`/`drift`, beam width, max_skip) = the transition model; (3) the
**argmax register `preg`** and the full 9-register panel = the adjudicator register. A negative is
"NEGATIVE over these enumerated operations, this decoder preset, across the 9-register panel."

**Q5 — What single observation kills the sub-lane at 10% of budget?**
If a sub-lane's Phase-0 **positive control does not recover** its own planted hit through the
enumerated operation (e.g. the X1 de-interleave fails to recover a 4-braided known text at ≥0.90),
that operation is declared an **unvalidated instrument** and its null is discarded, not reported as
a negative — and the sub-lane is not scored on LP2 until the control passes. That is the checkpoint.

---

## Per-sub-lane: hypothesis · positive control · size-matched null

### X1 — the FOUR readings
- **Hypothesis:** one literal "four" operation on the LP2 letter stream produces a panel-max-clearing
  register decode.
- **Operations enumerated:**
  - **X1a decimation:** every 4th rune, phases 0..3 → 4 substreams; adjudicate each, and each under
    the solved cipher ladder (shift 0..28 + atbash) as a keystreamless transform.
  - **X1b iterate ×N:** apply the solved-page cipher (atbash, shift-k) N∈{2,3,4} times to the stream;
    adjudicate the result.
  - **X1c 4-way interleave/de-interleave:** split into 4 columns (positions ≡ r mod 4), read
    column-major (de-interleave); and the inverse braid; adjudicate both orderings.
- **Positive control:** take a known English rune stream, 4-way INTERLEAVE it, then confirm the X1c
  de-interleave RECOVERS it (recovery = 1.0 on the reconstructed stream, pmax clears at that N).
- **Null:** the seed-3301 order-destroying shuffle (`lib_numchannel.shuffled`) of the LP2 stream,
  run through the SAME operations, size-matched — the panel-max bar's N_adj is the sub-lane's own
  adjudication count.

### X3 — question all things
- **Hypothesis:** reading the book back-to-front as the encryption order (decrypt = re-encipher on
  the reversed stream), OR keying unsolved-by-solved, clears the bar.
- **Operations enumerated:**
  - **X3a reversal:** reverse the 12,956-rune stream; apply the solved cipher ladder (atbash,
    shift 0..28) forwards as *encryption*; adjudicate. Also the plain reversed stream.
  - **X3b role-inversion:** solved-page plaintext (AN END + PARABLE, in-repo, and the LP1 solved
    English via validate.py) as the RUNNING KEY over the unsolved stream, and the deliberately
    inverted direction (unsolved as key over the solved cipher) — skip-aware decode, is_hit gated.
- **Positive control:** plant — take a known English stream, reverse it and re-encipher forwards with
  a known shift; confirm X3a recovers it by decrypting the reversal. For X3b: plant the solved
  plaintext as a genuine running key over a known target and confirm is_hit accepts it.
- **Null:** seed-3301 shuffle through the same reversal/keying operations; size-matched.

### X4 — the words OR their numbers (COMBINE)
- **Hypothesis:** the number transform of the stream, used as a KEYSTREAM over the letter stream,
  clears the recovery-gated hit bar (the "or" as "combine the channels").
- **Operations enumerated:** keystream ks ∈ {v_prime, v_prime_index, v_totient}(stream), each
  reduced mod 29, applied as `apply_keystream(letters, ks, sign∈{−1,+1})`, with atbash pre/post ∈
  {none, pre, post}, offset 0. ≈ 3 × 2 × 3 = 18 base configs; the letter twin = the raw stream
  adjudicated jointly (report both channels' pmax per row).
- **Positive control:** plant — encipher a known English stream WITH a number-derived keystream,
  then confirm the matching X4 config recovers it via `is_hit` (recovery ≥ 0.90).
- **Null:** seed-3301 shuffle of the stream → its number transform → same keystream application;
  size-matched, so the null keystream has the same value histogram, order destroyed.

## Language-agnostic statistics persisted at run time (doctrine R3, non-negotiable)

Every scored row stores, via `adjudicate()`'s record: `en`, full 9-register `z[]`, `pmax`, `preg`,
`pmax_ne`, `pcon`, **`ioc`** (decrypt IoC·N), **`mds`** (min distinct symbols / 32-window),
`h2`/`zl` (compressibility). Keyed rows additionally store `recovery`, `heldout_recovery`,
`clears_null`, `hit` via `hitfn20.adjudicate_hit_row` (SWEEPROW/3). Persisted to `ledger.json`.

## Red-team / non-overlap clause (doctrine R6)

Before scoring, assert each operation is NOT a Round-11 lens: X4 uses number transforms as
**keystreams over letters** (Round 11 N1/N2 read number streams **as text** or **as autokey
feedback on themselves** — different object); X1/X3 are **structural** (decimation, iteration,
interleave, reversal, role-inversion) which Round 11 never performed. Any bar-clearing survivor is
**FLAGGED-FOR-ORACLE, not auto-certified** (roadmap R21-L1 seal note), pending a non-fold gate.

## Kill condition recap
A sub-lane whose Phase-0 control does not recover is reported as an unvalidated instrument and NOT
scored as a negative. A sub-lane whose control passes and whose LP2 sweep produces no `is_hit` (or
no bar-clearing structural stream with a language-agnostic corroborator) is a NEGATIVE carrying its
three conditionals. Any `is_hit` survivor is FLAGGED-FOR-ORACLE.
