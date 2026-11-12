# Round 44 / WAVE-2 CELL A1 — SHORT-STREAM NULL + THE L<60 ENUMERATIONS — PREREG

_Dated 2026-11-09, written BEFORE any execution. Doctrine binds (ARMADA-DOCTRINE.md).
This file is hash-stamped into `run.log` before the first run (R44 X1 hygiene fix)._

## 0. What this cell is

R44 wave 1 left three finite red-channel reads with NO bar node (bars_v3's lowest free node is
L=120; the wave-1 lanes treated L<60 as "no adjudicable bar exists"):

1. the 30-symbol red diamond dot-block stream (27× 13-dot, 3× 10-dot; as bits with 13→1:
   `111111111111111111111001110111`) — `round44/P1-red-ink/results.json families.B`,
2. the red margin numerals `1 2 3 4 5` + the red grid cell `3299` (L=6),
3. the 13 red drop-cap initials `SLPAXLUMDNGIAFA` (canon indices from
   `round44/P1-red-ink/channel.json full.dropcaps`) and the red title `FULMAEAYOEA` (canon
   3603–3611, 9 runes) + `URPN` (canon 12644–12647, 4 runes).

This cell (a) builds an honest SHORT-STREAM NULL instrument (matched-length surrogate families,
seed 3301, through panel-R36), (b) measures its POWER with planted held-out English (and Latin)
fragments — if power at L=13 is ~0 that is said loudly and those streams are marked
measured-only, (c) adjudicates the real short streams against the calibrated bars, and
(d) runs enumerative structural checks on the 30-bit stream and the numerals.
It discharges `R44-P1-RED-SELECTION` / `R44-P1-RED-CENSUS` reopens_if (i): "a bar is built for
L < 60 streams". This cell GATES nothing downstream. The bars become the project's short-stream
instrument of record.

## 1. Cited ledger rows (verified open ground)

- `R44-P1-RED-CENSUS` (measured) — cov: "Dot/numeral streams fully enumerated verbatim (L=30
  and L=6, below any adjudicable bar)". The bar is what this cell builds. Open.
- `R44-P1-RED-SELECTION` (negative) — not_covered: "Per-section/per-page substreams with L<60
  (no bar exists; enumerated in channel.json)". The drop-cap/title/URPN short streams as
  STANDALONE L<60 reads are exactly inside that not_covered. Open.
- `R44-P1-RED-KEYPARAM` (negative) — not_covered names "dot-block counts ... untested as keys";
  this cell reads the dot stream as a standalone mod-29 stream, not as a key (key use stays
  not_covered here too).
- `R22-D-ILLUSTRATION-DROPCAP` (negative) — covered presence/position/identity of drop-caps as
  a geometric channel; the 13 initials as a RUNE TEXT STREAM under a 12-register panel were
  never read (P1 RESULTS correction 5: "excluded from every prior red read"). Open.
- `R44-P3-APOSTROPHE-NUMERAL-CENSUS` (measured) — not_covered: "sub-120 adjudication power in
  general". This cell supplies exactly that instrument.

## 2. The Aiming Test

**Q1 — What would a hit look like, would THIS instrument recognise it?**
A hit = one of the short red streams is a direct/affine-dressed natural-language fragment in a
panel-R36 register. Recognizer = panel-R36 pmax over the SAME 116-map reading grid used on the
real streams, against a family-wise bar calibrated on matched-length surrogates. Plants: (i) a
GLUE plant at L=120 (held-out English through the identical grid+collect code path) that MUST
pass its own calibrated bar — no verdict of any kind without it; (ii) POWER plants at each
short node (300 held-out EN windows + 300 held-out LATIN windows per L) whose crossing rate IS
the measured power. If measured EN power at a node is ~0, streams at that node get NO negative
verdict — they are recorded measured-only, which is itself this cell's honest deliverable.

**Q2 — What measured fact raises the prior?**
`round44/P1-red-ink/RESULTS.md` corrections 3–5: the title line and URPN sit on lines the
stones segmentation never held (never extracted, never read before wave 1), and the 13 red
drop-cap initials were height-excluded from every prior red read. The 13-vs-10 dot distinction
is a wave-1 census discovery (`census.json`), convergence-flagged by 4/6 blind agents (R43 F1).
And the rows' own reopens_if (i) names this exact instrument as the reopening condition.

**Q3 — Is the space bounded?**
Enumerable and tiny: 4 real streams × 116 affine maps = 464 decodes (budget cap N=600), plus a
finite structural table over one 30-bit string and 6 numerals. The null build is 2 families ×
5 L-nodes × 1000 surrogates × 116 maps.

**Q4 — The three conditionals of any negative here:**
1. *key space:* identity/affine (a∈{1,28}, s∈0..28) × fwd/rev only. No keyed, derived,
   transposition, or cross-channel-join readings of the short streams.
2. *transition model:* memoryless monoalphabetic maps. Chained/output-aware constructions and
   any use of the short streams AS keys/parameters are not represented.
3. *adjudicator register:* panel-R36's 12 registers, at the MEASURED short-L power (stated per
   node in Addendum 1; expected heavily degraded at L=13). The panel length-calibration grid
   floors at 32: all L<32 scoring is clamped to the 32-node calibration — the null is built
   through the identical clamp, so bars are self-consistent, but register resolution below
   L=32 is whatever the power measurement says, no more.
Additionally: the dot stream has a 2-symbol alphabet → every decode of it is DEGENERATE under
the standing R38 guard (mds≤6); it can never be certified by this panel regardless of score.
Pre-registered as measured-only-by-construction for the panel reading; its real content is
tested by the structural table.

**Q5 — Kill condition at 10% budget:**
(i) The L=120 glue plant fails its bar → INSTRUMENT-INCOMPLETE, stop, no verdicts.
(ii) Any POT fit with < 50 tail exceedances or non-finite beta → that node is not calibrated;
streams at it are measured-only. Checkpoint: after `null_bars.py` + `plant_power.py`, before
any real read.

## 3. Instrument definition (FIXED)

- **Reading grid** (identical for null, plants, real): {fwd, rev} × affine a∈{1,28}, s∈0..28
  = 116 decodes per stream. Same code path (`grid()` in `shortnull.py`).
- **Adjudicator:** standing panel-R36 (`round19/I2/adjudicate.py` + `data/panels/panel-r36.npz`),
  adjudicate_batch pmax, degenerate guard as standing (R38: mds≤6 or IoC·N≥4.24).
- **Null surrogate families, seed 3301** (matched-length, order-preserving):
  - `SEL`: L canon positions drawn uniformly without replacement, SORTED (order-preserving
    selection from `data/krisyotam_runes.txt` canon — exactly how the real selection streams
    arise);
  - `WIN`: contiguous L-windows of canon at uniform random start.
  1000 surrogates per (family, L), each through the full 116-map grid → 116,000 null pmax per
  node. L-nodes: {13, 26, 30, 40, 120} (120 = glue-validation node, cross-checked against
  bars_v3 free).
- **Bar model** (bars_v3's, refit): exponential peaks-over-threshold above the empirical 90th
  percentile u; beta = mean excess (exponential MLE); mu = u + beta·ln(p_u);
  **bar(N, L, fam) = mu + beta·ln(N / −ln(1−alpha))**, alpha = 0.01, **N = 600** (the cell's
  fixed real-decode budget; actual planned 464). **Bar of record at each L = max over the two
  families** (conservative).
- **Power** per node: fraction of 300 held-out English windows (second half of
  `data/keys/self_reliance.txt`, the panel build's reserved plant half, encoded via
  `lp.gematria.keyword_to_indices`) whose grid-max pmax ≥ bar of record; same for 300 Latin
  windows (second half of `analysis/latin/latin_28233.txt`). RNG seed 3301.
- **Power floor for a verdict: 0.5.** A real stream read at node L yields NEGATIVE only if
  EN power(L) ≥ 0.5 AND 0 crossers; otherwise its record is measured-only. Any bar-crosser is
  FLAGGED-FOR-ORACLE per HUMAN-ORACLE.md, never certified.
- Numeric bars + powers are appended as **Addendum 1 (dated) BEFORE any real read** and the
  file re-hash-stamped.

## 4. Real targets (FIXED; run only after Addendum 1)

| stream | L | node | source |
|---|---|---|---|
| dropcaps13 = [15,20,13,24,14,20,1,19,23,21,27,0,24] (`SLPAXLUMDNGIAFA`) | 13 | 13 | channel.json full.dropcaps, canon order |
| titleURPN13 = title[0,1,20,19,24,28,26,22,24] + URPN[1,4,13,9] | 13 | 13 | canon 3603–3611 + 12644–12647 |
| grand26 = all 26 short-red runes in canon position order (dropcaps ∪ title ∪ URPN) | 26 | 26 | channel.json full minus legacy187 |
| dotvals30 = [13×21,10,10,13,13,13,10,13,13,13] as mod-29 symbols | 30 | 30 | P1 results.json families.B block order |

Each × the 116 grid. The L=40 node is calibrated as part of the instrument of record (no real
stream at 40 exists; stated plainly). Red margin numerals (L=6) are below the lowest node:
enumerated in the structural table only.

## 5. Structural table for the 30-bit stream (enumerative; FIXED match criteria)

Stream `s = 111111111111111111111001110111` (13-dot→1), plus rev(s), comp(s), rev(comp(s)).
A reportable MATCH = exact equality / exact containment against the pre-registered constant
list: {3301, 1033, 761, 509, 311, 29, 3299, 1595277641} in binary (and the 30-bit values' own
decimal equal to any of these); primality of the four 30-bit values; factorisations;
zero-position set {22,23,27} (1-based) and its deltas vs the 10-dot image set {36,38,49};
groupings 2×15, 3×10, 5×6, 6×5, 10×3, 15×2 bits fwd/rev (values; 5-bit as Baconian A–Z where
<26); ASCII noted UNBUILDABLE (30 ∤ 8) unless 0-padded (then reported verbatim); run-length
encoding; ones/zeros counts; sum of dot counts and its mod 29. Numerals: 1,2,3,4,5,3299 as
mod-29 translits; gematria-prime sums of dropcaps/title/URPN with primality + 3301-relations.
Everything here is RECORDED (measured), never a verdict; any exact constant match is reported
loudly and goes to the oracle path, not to certification.

## 6. Budget / N accounting

Real adjudicated decodes: 464 ≤ N=600 (bars fixed at 600). Null: 1,160,000 decode-adjudications
(10 nodes × 116k). Plants: (300 EN + 300 LA) × 5 nodes × 116 = 348,000. Pure python3+numpy,
no network, no image work (wave-1 census is the artifact of record; exact crops cited there).

## 7. Outputs

`shortnull.py` (shared glue), `null_bars.py` → `short_null.json`, `plant_power.py` →
`plant_power.json`, `readings.py` → `results.json`, `structural.py` → `structural.json`,
`RESULTS.md`, `ledger_rows.json`, `run.log` (hash-stamped). LEDGER.json NOT modified.

---

## Addendum 1 — 2026-11-09, BEFORE any real read (per §3)

Numeric bars of record (short_null.json; seed 3301, N=600, alpha=0.01, POT fits all with
11,599–11,600 exceedances, every node calibrated — Q5(ii) did not fire):

| L | bar of record | EN power | LA power | verdict-capable (EN ≥ 0.5)? |
|---|---|---|---|---|
| 13 | 10.5184 | **0.2533** | 0.0533 | **NO — measured-only node** |
| 26 | 6.8897 | 0.9700 | 0.9367 | yes |
| 30 | 6.3350 | 1.0000 | 0.9867 | yes |
| 40 | 6.0856 | 1.0000 | 1.0000 | yes |
| 120 | 5.8323 | 1.0000 | 1.0000 | yes (instrument node) |

Glue plant (L=120): pmax 15.7133 ≥ 5.8323, identity cell intact → **PASSED**. Q5(i) did not
fire. Per §3, the L=13 streams (dropcaps13, titleURPN13) therefore CANNOT yield a negative
verdict: their reads run and are persisted measured-only. Power at L=13 is not ~0 (0.25 EN)
but is below the 0.5 floor — said loudly here as §2 Q1 requires. dotvals30 is additionally
measured-only-by-construction (2-symbol alphabet, degenerate). grand26 is the one stream with
a verdict-capable node. Note: the WIN null family's canon windows include the solved-page
plaintext; its tail is therefore conservative (emp_max ~10.1–11.0 at L=26–40 are true
plaintext windows — incidental proof the instrument sees real language at these L). The
bars_v3 free@120,N600 bar is 11.3518 vs this instrument's 5.8323: different null populations
(beam-search wrong-key decodes vs single affine-grid decodes); not interchangeable, reported
for orientation only.
