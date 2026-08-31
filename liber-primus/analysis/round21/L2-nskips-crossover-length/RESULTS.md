# RESULTS — Round 21 / L2 — `n_skips` power-crossover length

_Instrument lane. Seed 3301, order-preserving. Reuses the Round 20 P2 machinery verbatim
(`analysis/round20/P2/nskips_lib.py`: plant + the two admitted I1 relations `keyskip1`/`drift` +
the exact discrete-tail null). Trust anchor `python3 tests/validate.py` →
**ALL VALIDATIONS PASSED (5/5)** before this lane ran. Pre-registered in `PREREG.md` before any
sweep; no threshold edited after seeing a result._

## Headline

**On the exact `keyskip1` relation, the `n_skips` statistic crosses over from non-separating to
separating between L=3600 and L=6000. The crossover length is L\* = 6000** (the smallest ladder
point at which the correct-key `n_skips` clears the pre-registered two-sided FPR=0.01 bar against
a size-matched wrong-key null, and it stays separated at every larger L measured: 9000, 12956).

This is the one number PICKUP-HERE item #4 asked for: any future concatenated-page / whole-book
`n_skips` adjudication must respect a window of **≥ ~6000 runes** (about **11–12 pages**) before
`n_skips` alone is a valid discriminator under the exact decoder. Below that it is not.

## Q1-gate (Q5 kill checkpoint) — PASSED

The sweep re-derived the two Round 20 endpoints from the same machinery before trusting any
intermediate L:

| L | correct `n_skips` | null mean | null q99 | two-sided p | recovery | separates? |
|---:|---:|---:|---:|---:|---:|:--|
| 400 (page window) | 6 | 8.87 | 19 | 0.520 | 1.000 | **No** (reproduces R20 ≈0.21-class no-sep) |
| 12956 (full book) | 418 | 296.99 | 350 | 0.000 | 0.999 | **Yes** (reproduces R20 418-vs-~300 right-tail) |

Both endpoints reproduce (L=400 no-sep, L=12956 clean right-tail sep at recovery 0.999). The
null build is the one P2 measured; the kill condition did **not** fire; the ladder is trusted.

## The crossover curve — exact channel (`keyskip1`, `keyskip` mechanism, LP1_REAL)

| L | correct | null mean | null q99 | two-sided p | recovery | separates (FPR 0.01)? |
|---:|---:|---:|---:|---:|---:|:--|
| 400 | 6 | 8.87 | 19 | 0.520 | 1.000 | No |
| 600 | 13 | 13.53 | 25 | 1.040 | 1.000 | No |
| 900 | 16 | 20.80 | 37 | 0.453 | 1.000 | No |
| 1200 | 34 | 27.56 | 46 | 0.400 | 1.000 | No |
| 1600 | 45 | 36.08 | 52 | 0.193 | 1.000 | No |
| 2400 | 68 | 55.62 | 80 | 0.187 | 1.000 | No |
| 3600 | 94 | 82.12 | 107 | 0.267 | 0.999 | No |
| **6000** | **198** | **139.36** | **176** | **0.000** | **0.999** | **Yes ← crossover** |
| 9000 | 290 | 207.63 | 250 | 0.000 | 0.998 | Yes |
| 12956 | 418 | 296.99 | 350 | 0.000 | 0.999 | Yes |

Reading the curve: the correct-key footprint grows ~linearly in L (6→418) while the wrong-key
fabrication grows sublinearly (8.9→297), so the correct key first *overtakes the null mean*
around L≈1000–1200, but does not clear the *1% right tail* (q99) until L=6000. The gap between
"beats the mean" (~L1000) and "clears the 1% tail" (L6000) is the width of the discrete null's
right tail — exactly why P2 warned a Gumbel bar is the wrong tool and this lane used the exact
empirical tail. **Crossover bracket: (3600, 6000]. First separating ladder point: 6000.**

## Positive control (instrument validation) — PASSED at every L

Plant recovery is **≥ 0.998 at every L** on the `keyskip1`-exact cells (1.000 through L=2400,
0.999–0.998 at L=3600–12956). The instrument recovers its own planted footprint everywhere, so
the non-separation at L<6000 is a **real bound on the statistic's power**, not an unvalidated
silence. The R's A-iv decoupling hazard is respected: separation is gated on recovery ≥0.90 AND
p ≤ FPR, never on score.

## Coverage × power (the doctrine's mandated single statement)

- **Coverage:** a 10-point geometric ladder L ∈ {400, 600, 900, 1200, 1600, 2400, 3600, 6000,
  9000, 12956}, seed 3301, size-matched wrong-key null M=300 per L (exact discrete histogram
  persisted, not a fit), brackets the full R20 gap (400, 12956) that was UNMEASURED before this
  lane. Coverage is over LENGTH, not key space — no keys were swept (this is an instrument lane).
- **Power:** plant recovery ≥ 0.998 at every L (instrument validated end-to-end); the exact-channel
  correct-key/wrong-key `n_skips` separation crosses FPR=0.01 at **L\* = 6000**, and holds for all
  larger L. So the statistic has **power 0 at page scale (L ≤ 3600) and power 1 (p=0.000) at
  L ≥ 6000** under the exact decoder — the crossover is sharp.

**One line:** *coverage = the length ladder (400…12956) bracketing R20's unmeasured gap; power =
recovery ≥0.998 throughout, with exact-channel n_skips separation crossing FPR 0.01 at L\*=6000.*

## The three conditionals this negative-below-6000 carries (doctrine Q4)

1. **Key space:** none swept. Plant uses the correct key; null uses uniform wrong keys. The
   "no power below L=6000" statement is a property of the *statistic at that length*, not of any
   key search.
2. **Decoder's transition model — this is where the result splits, and it must be read carefully:**
   - **`keyskip1` (exact relation):** crossover at **L\*=6000**, as above. This is the honest,
     right-tail-footprint crossover — the correct key genuinely leaves more skips than a wrong key,
     and that surplus clears the 1% tail only at ≥6000 runes.
   - **`drift` (permissive lam=12 max_free=2):** the permissive beam **fabricates** huge skip
     counts on random wrong keys (wrong-key null mean 32 → 897 as L grows), so the correct key's
     genuine small footprint sits in the extreme **LEFT** tail at every L (p_left=0.000, p2=0.000
     from L=400 up). Under the two-sided test this "separates everywhere," but it is a **left-tailed
     artifact of the permissive beam's wrong-key inflation, NOT the right-tail footprint signal**
     P2/T3 measured. **Do not read the drift channel as a page-scale n_skips discriminator.** It
     detects "the correct key produces implausibly FEW skips for how permissive the beam is," which
     is a different (and register-blind) fact, useful only if the sieve's beam is the permissive one.
   - **`skip_by_two` (second mechanism, R18 L7-B) — NO valid crossover, and the reason is the
     pre-registered recovery gate doing its job:** the beam **cannot represent** this relation, so
     the plant is **not recovered** — recovery falls from **0.28 at L=400 to 0.04 at L=6000** (vs
     ≥0.998 for `keyskip1`). Because `separates` is gated on recovery ≥0.90 AND p ≤ FPR, skip_by_two
     **never separates at any L** — the `n_skips` values it does emit (0, 6, 5, 7, 27, 54, 84, 167
     at L=400…6000) are meaningless because the underlying decode is wrong. This is the honest L7-B
     result: `n_skips` gives no crossover for a rejection loop the decoder is blind to, and the
     recovery floor correctly refuses to call it a hit. Reported as a **separate curve**, explicitly
     **not merged** with the keyskip crossover. [The skip_by_two L=12956 point and the 5-register
     invariance panel at L=6000 are the sweep's final stages; `nskips_crossover.json` carries every
     completed row. The keyskip1 crossover L\*=6000 and the drift-artifact finding are final and
     independent of those columns.]
3. **Adjudicator's register — the crossover is register-APPROXIMATE, not exactly invariant, and
   the panel measured how much it drifts.** `n_skips` is language-agnostic in that it is a property
   of the rejection loop and keystream, not a plaintext *language model* — no English scorer gated
   anything. But the *magnitude* of the planted footprint at a given L depends on the plaintext's
   doublet density (how often the soft anti-repeat rule fires), so the crossover length drifts
   mildly across registers. Full 5-register panel at L=6000 (all recover ≥0.9995 — instrument
   validated, so this is a real footprint-size effect):

   | register | correct `n_skips` | null mean | p2 | recovery | separates at 6000? | crossover |
   |---|---:|---:|---:|---:|:--|:--|
   | LP1_REAL | 198 | 139.4 | 0.000 | 0.9995 | **Yes** | **6000** |
   | OE | 188 | 139.4 | 0.007 | 1.000 | **Yes** | **6000** |
   | EN_HALFVOWEL | 179 | 139.4 | 0.013 | 0.9998 | No (just above 0.01) | just > 6000 |
   | LATIN | 175 | 139.4 | 0.020 | 1.000 | No | just > 6000 |
   | EN_MODERN | 144 | 139.4 | 0.740 | 1.000 | No | ≫ 6000 |

   Reading: **the two LP-relevant registers (LP1_REAL, OE) cross at exactly 6000**; LATIN and
   half-vowel English cross just past 6000 (footprints ~10–12% smaller); modern high-vowel English
   has far fewer doublets to suppress, a much smaller footprint (144), and a crossover well above
   6000. So the headline **L\*=6000 is the crossover for the LP-relevant registers**; a
   conservative universal gate would round up (e.g. ~7000–8000) to cover the vowel-heavy registers.
   `crossover_by_register` in the JSON records {LP1_REAL:6000, OE:6000, LATIN:None, EN_HALFVOWEL:None,
   EN_MODERN:None} (None = does not separate at any measured L ≤ 6000; the panel was run only at the
   6000 neighbourhood, so a "None" here means "> 6000," not "never").

## What this does and does not license (doctrine R7 — bounds, not verdicts)

- **Licensed:** a future whole-book or long-concatenated-page adjudication may use `n_skips` under
  the **exact `keyskip1`** decoder as a real discriminator **only at window length ≥ ~6000 runes**.
  At page-window lengths (≤ ~3600) `n_skips` alone carries no power under the exact decoder and must
  be combined with the P3a panel-max score (per PICKUP-HERE #4), or the window enlarged.
- **Not licensed:** treating the `drift`-channel or `skip_by_two`-channel left-tail "separation" as
  a footprint discriminator. Those separate for instrument-artifact reasons (wrong-key inflation;
  L7-B blindness), not because the correct key left a recoverable rejection-loop footprint.
- **Reopens if:** a cheaper statistic, a longer-per-decode decoder, or a mixed n_skips+panel-max
  combination lowers the effective crossover below 6000; or the encipherer's true rejection loop is
  neither `keyskip` nor `skip_by_two` (then its own crossover curve must be measured).

## Aiming Test — honestly answerable? YES

All five questions are answered in `PREREG.md` with the recognizer written before the search, the
positive control planted and shown to recover (≥0.998), a size-matched null built per L before
each comparison, an enumerable bounded space (10-point ladder), and coverage×power reported over
the length axis and both decoder channels. The lane was allowed to run and did.

## Files

- `PREREG.md` — the five Aiming-Test answers, threshold (FPR 0.01 two-sided), Q1-gate, kill cond.
- `crossover.py` — the driver (reuses `round20/P2/nskips_lib.py`; Q1-gate first, then ladder).
- `nskips_crossover.json` — persisted language-agnostic statistics: per (L, channel, mechanism,
  register) the full wrong-key discrete histogram, correct/gt `n_skips`, recovery, two-sided p;
  plus `crossover` (keyskip1|keyskip = 6000) and the reproduced R20 endpoints.
- `ledger.json` — coverage × power in the LEDGER.json entry schema.
