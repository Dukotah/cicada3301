# S-G3 — RESULTS: Python 2.7 `random.seed(str)` sweep — NEGATIVE at 0.057% coverage, instrument validated

_Run 2026-08-28. Trust anchor `tests/validate.py` PASSES before and after. No git commit._

## Verdict: NEGATIVE (validated instrument, stated-fraction coverage) — no HIT

The recovery-gated hit function (`round20/HITFN`) cleared the red-team HALT, so S-G3 — the one lane
P1's frozen kill releases (enumerable end-to-end **without a sieve**) — ran. The positive control
recovered a planted Py2.7 key **rank-1** through the full pipeline; the sweep then screened
**2,458,000** words of the 2³² space and **`is_hit()` fired on nothing**. This is a real negative
from a validated instrument, not silence.

## Positive control — PASS (mandatory, ran FIRST)

`poscontrol.py` (→ `out_poscontrol.json`). Planted the top P3b prior seed **1325734783 as the 32-bit
word `w`**, built its `init_by_array([w])` `random29` keystream, enciphered a real EN_MODERN
plaintext via `keyskip` (supp 0.83, L=240), and recovered it through I1 keyskip1 → I2 panel → P3a
bar → HITFN `is_hit`:

| mode | is_hit | pmax | bar | recovery | held-out | preg |
|---|:---:|---:|---:|---:|---:|---|
| strict (truth_idx) | **True** | 28.27 | 7.634 | 1.000 | 1.000 | LP1_REAL |
| real (held-out, no oracle) | **True** | 28.27 | 7.634 | 1.000 | 1.000 | LP1_REAL |

**Rank-1 recovery:** true word pmax **28.27** vs wrong-neighborhood (±500, n=199) max pmax **4.18**;
rank **1/200**; **0/199 wrong neighbors clear the 7.634 bar**. The instrument recovers its own
planted key from this exact generator, so the null below is trustworthy.

## The sweep — `sweep.py` (two-stage, prior-ordered, time-boxed)

- **Stage A** (every word): keyskip1 beam (`exact`, reduced width 64) on L=120 canonical unsolved
  ciphertext → `pmax`. Frozen screen bar **5.0** (≪ 7.634 claim bar; the plant clears at ~28, wrong
  words ≤4.2 — no true positive is screened out).
- **Stage B** (survivors, pmax≥5.0): full L=240 adjudication + `hitfn20.is_hit` (real-candidate mode,
  no oracle) → SWEEPROW/3 rows carrying `recovery, heldout_recovery, clears_null, hit`.
- **Seed order** (P3b prior-weighted, doctrine R4): all 433 prior words + ±512 neighborhoods of the
  top 64 prior seeds = **45,975 prior words screened FIRST** (all covered), then a dense contiguous
  block from `w=0`.

### Key numbers

| quantity | value |
|---|---|
| words screened | **2,458,000** |
| fraction of 2³² | **0.0005723 = 0.05723 %** |
| Stage-B survivors (pmax≥5.0) | 230 |
| **HITS (`is_hit`==True)** | **0** |
| top survivor pmax | 6.27 (`w=594211`, LATIN, rec 1.0) — **below the 7.634 bar, hit=false** |
| wall time / procs | 2089 s / 6 cores |
| throughput | 1176 words/s (6 cores) |
| prior words all screened | **yes** (45,975) |
| **extrapolated full 2³² cost** | **≈ 7 core-days** (6 cores → ~1.2 wall-days) |

The gate discriminated correctly: several survivors reach recovery/held-out **1.0** but sit at
pmax 5.9–6.3 **below** the null bar (`clears=false`), and one (`w=1415259`, pmax 6.23) clears neither
— all correctly `hit=false`. No word cleared pmax≥7.634 AND recovery≥0.90 AND held-out≥0.90.

## Measured power per register (P3a, exact preset, N=1e6, claim bar 7.634)

| register | pmax power (correct key) | wrong-key power | median recovery | note |
|---|---:|---:|---:|---|
| LP1_REAL | 1.00 | 0.00 | 1.00 | |
| LATIN | 1.00 | 0.00 | 1.00 | |
| OE | 1.00 | 0.00 | 1.00 | (threshold OK here; drift-OE still ranks via n_skips) |
| EN_HALFVOWEL | 1.00 | 0.00 | 1.00 | |
| EN_MODERN / EN_KJV | 1.00 | 0.00 | 1.00 | |
| DE / CY | 1.00 | 0.00 | 1.00 | |
| EN_NOVOWEL | **0.70** | 0.00 | **0.84** | detection-only; recovery<0.90 → HITFN rejects (defect d) |
| RAND (neg control) | 0.00 | 0.00 | 0.29 | no leak |

The sweep therefore carries **power 1.00 across LP1_REAL / Latin / OE / half-vowel English** (the four
registers the win-condition names) and 0.00 false-positive power on wrong keys — so the negative is a
**power-≥0.90 negative on those registers**, limited only by coverage.

## The three conditionals of this negative (doctrine R2)

This negative holds for: **(key space)** Python 2.7 32-bit `init_by_array([w])` `random29` streams,
0.057 % of 2³² enumerated (prior words fully covered) × **(decoder relation)** I1 keyskip1 (`exact`)
Stage-A screen + full L=240 gate, drift_rec available as the transcription-robust channel ×
**(adjudicator register)** the I2 9-panel at P3a power 1.00 on LP1_REAL/Latin/OE/half-vowel English,
0.70 on EN_NOVOWEL (detection-only). It does **not** touch the CSPRNG / `/dev/urandom` branch, does
not enumerate the remaining 99.94 % of the word space, and does not test `grb5_mod`/`grb5_rej`/
`shuffle29` reducers or the 64-bit ABI (those remain unswept — reopening conditions below).

## Reopening conditions

- **Full 2³² enumeration** (`random29`, exact preset): ~**7 core-days** — the family-collapse run,
  affordable but beyond this 40-min box. Its negative at power 1.00 on the four registers would
  collapse Py2.7 `random.seed(str)` as the LP2 key source.
- The other **three reducers** (`grb5_mod`, `grb5_rej`, `shuffle29`) and the **64-bit ABI** word map
  (2 key words) are unswept; each is a separate ~7-core-day + variant run.
- Any word `w` that later clears pmax≥7.634 AND recovery≥0.90 AND held-out≥0.90 is a HIT by
  construction (the predicate is deployed and proven on the plant).

## Files

`PREREG.md` · `poscontrol.py` + `out_poscontrol.json` · `sweep.py` + `out_sweep.json` +
`sweep.jsonl` (survivor SWEEPROW/3 rows) · `test_sg3.py` (all pass) · `RESULTS.md`.

`tests/validate.py` → ALL VALIDATIONS PASSED (5/5), before and after. No git commit.
