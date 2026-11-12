# Round 44 / WAVE-2 CELL A1 — SHORT-STREAM NULL + THE L<60 ENUMERATIONS — RESULTS

_Run 2026-11-09. PREREG.md (incl. dated Addendum 1) preceded every output and is hash-stamped
in `run.log` before first execution and again before the real reads. Instrument: panel-R36
(`round19/I2/adjudicate.py` + `data/panels/panel-r36.npz`); bar model = bars_v3's exponential
POT refit on fresh matched-length nulls (bars_v3 itself has no node below L=120 — building the
missing nodes IS this cell). Pure python3, no network._

## Verdict

**INSTRUMENT BUILT — the project now has a short-stream bar of record at L ∈ {13, 26, 30, 40}
(+120 validation node), with measured power.** Headline honesty item first:
**at L=13 the instrument's measured English power is 0.25 (Latin 0.05) — below the
pre-registered 0.5 verdict floor — so the two 13-rune red streams are MEASURED-ONLY: no
negative is claimed for them, by design.** At L=26/30/40 power is 0.97–1.00 and verdicts are
live.

**Real reads: 464 decodes, 0 crossers, nothing FLAGGED-FOR-ORACLE.**
The one power-backed verdict: **grand26 (all 26 short-red runes wave 1 proved were never read:
13 drop-caps + title + URPN, canon order) is NEGATIVE as a direct/affine stream** — best 3.03
vs bar 6.89 at power 0.97. The 30-bit dot stream matched **no pre-registered constant** in any
of 4 bit-variants and is measured-only for the panel by construction (2-symbol alphabet =
degenerate under the standing R38 guard). This discharges `R44-P1-RED-SELECTION` /
`R44-P1-RED-CENSUS` **reopens_if (i)** ("a bar is built for L<60 streams") — partially:
discharged at L∈{26,30,40}, and *measured as not honestly dischargeable* at L=13 with this
recognizer class.

## 1. Positive control + power (plant_power.json)

| gate | result |
|---|---|
| Glue plant, L=120 held-out English window through THIS cell's own 116-map grid + collect path | pmax **15.7133 ≥ bar 5.8323**, identity cell byte-intact → **PASSED** (no verdict was issued before this gate) |
| POT fit stability (Q5 ii) | 11,599–11,600 tail exceedances per node — never fired |

Measured power (fraction of 300 held-out windows — second half of `data/keys/self_reliance.txt`
/ `analysis/latin/latin_28233.txt`, the panel build's reserved plant halves — whose grid-max
clears the bar of record):

| L | bar of record | EN power | LATIN power | verdict-capable (≥0.5 EN)? |
|---|---|---|---|---|
| 13 | 10.5184 | **0.2533** | 0.0533 | **NO** |
| 26 | 6.8897 | 0.9700 | 0.9367 | yes |
| 30 | 6.3350 | 1.0000 | 0.9867 | yes |
| 40 | 6.0856 | 1.0000 | 1.0000 | yes (instrument node; no real stream at 40) |
| 120 | 5.8323 | 1.0000 | 1.0000 | yes (validation node) |

Null families (seed 3301, 1000 surrogates × 116-map grid each): SEL = order-preserving canon
position selections; WIN = contiguous canon windows; bar of record = max of the two POT bars at
N=600, α=0.01. Two honest footnotes: (a) the panel's length-calibration grid floors at 32, so
all L<32 scoring is clamped to the 32-node calibration — null, plants and reals go through the
identical clamp, so the bars are self-consistent, but that clamp is WHY L=13 power is poor
(variance under-modelled → bar forced high); (b) the WIN family's windows include the canon's
solved-page plaintext, so its tail — and hence the bar of record — is conservative (the
emp_max ≈ 10.1–11.0 outliers at L=26–40 are true plaintext windows, incidental proof the
instrument sees real language at those lengths).

## 2. The real reads (results.json; N = 464 ≤ budget 600; grid = {fwd,rev} × affine a∈{1,28}, s∈0..28)

| stream | L | best pmax | bar | crossers | verdict |
|---|---|---|---|---|---|
| dropcaps13 `SLPAXLUMDNGIAFA` | 13 | 4.3678 | 10.5184 | 0 | **measured-only** (power 0.25 < 0.5) |
| titleURPN13 `FULMAEAYOEA`+`URPN` | 13 | 4.7880 | 10.5184 | 0 | **measured-only** (power 0.25 < 0.5) |
| grand26 (all 26, canon order) | 26 | 3.0319 | 6.8897 | 0 | **NEGATIVE** at power 0.97 EN / 0.94 LA |
| dotvals30 (13/10 as mod-29) | 30 | 8.9287 | 6.3350 | 0 | **measured-only by construction** — the raw 8.93 "crossing" is the R38 degenerate-decode artifact (mds = 2 ≤ 6; a 2-symbol stream scores content-independently); killed by the standing guard, exactly as pre-registered |

Doctrine-R3 statistics for each stream's best decode are in `results.json streams.*.best`
(en, ioc, mds, h2, zl, pmax_ne, pcon, degenerate).

## 3. Structural table for the 30-bit stream + numerals (structural.json)

`s = 111111111111111111111001110111` (13-dot→1; 27 ones, 3 zeros; zeros at positions 22, 23,
27 ← the three 10-dot diamonds on imgs 36, 38, 49).

- **Pre-registered constant matches: NONE.** Not 3301/1033/761/509/311/3299/1595277641 in any
  of {fwd, rev, complement, rev-complement}, decimal or binary-containment — except the
  trivial `11101` (=29) substring, unavoidable inside a run of 27 ones (recorded as trivial).
- Decimals: fwd 1,073,741,431 = 7 × 153,391,633 (= 2³⁰ − 393); rev 1,000,341,503 =
  7 × 97 × 1,473,257; comp 392 = 2³·7²; revcomp 73,400,320 = 2²¹·5·7. None prime.
- Groupings (fwd): 5-bit → 31,31,31,31,19,23 (Baconian unbuildable, values ≥26 dominate);
  6-bit → 63,63,63,57,55; 3-bit → 7×7,1,6,7; 10-bit → 1023,1023,311... (all variants verbatim
  in structural.json). ASCII UNBUILDABLE (30 ∤ 8); 0-padded bytes [63,255,249,183] recorded.
- Dot sum 27·13 + 3·10 = 381; 381 mod 29 = 4 (`R`). Values as translit: P×21, I, I, P, P, P,
  I, P, P, P.
- Numerals: margin `1 2 3 4 5` = futhorc `U TH O R C` trivially (they label the five numbered
  list items — P1 census note); red grid cell 3299 is prime, 3301−3299 = 2, 3299 mod 29 = 22
  (`OE`). Grid READINGS remain lane P2's ground (already negative there).
- Gematria-prime sums: dropcaps 834, title 638 (mod 29 = 0), URPN 86, all26 1558 — none prime,
  no 3301 relation.

## 4. Coverage × not_covered

**Covered:** the short-stream instrument itself (2 null families × 5 L-nodes, power measured EN
+ LA); grand26 direct/affine at power 0.97; dropcaps13/titleURPN13 direct/affine *recorded* at
power 0.25; dotvals30 direct/affine recorded (degenerate class); the full pre-registered
structural table (4 bit-variants × 8 constants × 6 groupings + run-lengths + numerals + sums).

**not_covered (the three conditionals, PREREG §2 Q4):**
- *key space:* only identity/affine × fwd/rev. No keyed, derived, transposition, positional-
  selector, or cross-channel-join readings of any short stream; dot stream as key/parameter
  stays inside `R44-P1-RED-KEYPARAM`'s not_covered; constants/bases outside the
  pre-registered structural list.
- *transition model:* memoryless monoalphabetic only; chained/output-aware constructions
  (the pinned LP2 model) are not representable here.
- *adjudicator register:* panel-R36's 12 registers, at the MEASURED powers above — in
  particular every L=13 statement is conditional on a recognizer that misses 75% of true
  English at that length, which is why no L=13 verdict is issued. Non-EN/LA register power
  not separately measured.

**Reopens if:** (i) a higher-power short recognizer is validated at L=13 (word/dictionary-level
scorer — the natural next instrument step; the streams are preserved ready-to-score); (ii) a
keyed reading family consumes these streams with its own refit bar (`null_bars.py` refits a new
node in minutes); (iii) a constant outside the pre-registered list is independently motivated.

## 5. Files

- `PREREG.md` (+ Addendum 1) — hash-stamped twice in `run.log` (pre-execution, pre-real-reads)
- `shortnull.py` — the single shared glue (grid, canon, panel, POT, plant windows)
- `null_bars.py` → `short_null.json` — the null build + bars of record
- `plant_power.py` → `plant_power.json` — glue plant + power curves
- `readings.py` → `results.json` — the 4 real streams vs the fixed bars
- `structural.py` → `structural.json` — the enumerative table
- `ledger_rows.json` — 3 draft rows (instrument/measured, grand26/negative,
  L13+dot/measured); LEDGER.json itself NOT modified

Reproduce: `python3 null_bars.py && python3 plant_power.py && python3 readings.py &&
python3 structural.py` (in this directory; pure python3+numpy, no network).
