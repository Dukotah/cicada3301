# Round 44 / WAVE-2 CELL C6 — SHORT-PAGE SPECIFICITY AT HONEST POWER — PREREG

_Dated 2026-11-09, written BEFORE any execution. Doctrine binds (ARMADA-DOCTRINE.md). This
file is hash-stamped into `run.log` before the first run (R44 X1 hygiene fix), and
re-stamped after the dated Addendum 1 (numeric bars + powers) BEFORE any real read._

## 0. What this cell is

B-24 records that the project's short-page specificity anchor ("AN END", 85 runes) was
"disclosed underpowered"; B-19/B-20 record that the Round-9 LENGTH/DIRECTION closures were
disclosed weak. R43 X0 adjudication item 24 (3 blind agents: A1-H8, A2-H10, A5-H9) REOPENED
"short/end pages (p49, seg54, 49–55) as key pages or lighter cipher; exhaust classical
ciphers there", citing exactly these rows: "whole-book sweeps cover these pages, but the
ledger itself records that short-page-specific adjudication is underpowered at these
lengths."

Verified premise (this cell, measured from the artifacts before writing this file):

- Canon `data/krisyotam_runes.txt` = 57 pages / 13,136 runes; pages 0–54 are the unsolved
  stream (12,956 runes); **p55 = 85 runes ("AN END") and p56 = 95 runes are SOLVED
  plaintext** held in canon as futhorc plaintext (R44 W2-A1 RESULTS footnote (b) confirms:
  canon windows over them score as true plaintext).
- Shortest unsolved pages: **p49 = 66**, **p54 = 76**, **p50 = 92** runes.
- The four standing per-page sweeps with stored per-page bests all adjudicated these pages
  against an **L=120 bar node** (no shorter node existed):
  `P2-p15-grid/p2_results.json` (bar 12.956, 12,184 decodes/page, lane total 670,120),
  `P4-blob-pads/p4_results.json` (bar 14.034, 92,160/page, lane total 5,068,800),
  `R1-key-resets/r1_results.json` (bar 15.674, n_bar 2,000,000),
  `W2-A4-chained-pres/results.json` (bar 13.708, n_bar 50,000).
- W2-A1 built the short-STREAM instrument at L ∈ {13, 26, 30, 40, 120} (red channels). No
  node exists at the short-PAGE lengths 66/76/85/92/95. No wave-2 cell runs classical
  ciphers on p49 (W2-C2 uses Vigenère variants for PAGE-PAIR keys, different object).

This cell (a) builds the bespoke matched-null instrument at L ∈ {66, 76, 85, 92, 95}
(bars_v3-style POT fit over the standing 116-map config grid, exactly W2-A1's refit code
path), (b) measures planted-key POWER at those lengths — both at this cell's own N and at
the four standing sweeps' N — **expecting low power at sweep-scale N and saying so: if
measured EN power < 0.5 at a cell, that cell's verdict is instrument-bound (recorded
measured, never negative)**, (c) RE-ADJUDICATES the four sweeps' stored per-page bests for
p49/p50/p54 under the bespoke bars (reuse, no re-sweep), and (d) runs the classical-cipher
exhaust the blind agents asked for on p49 alone (shift / atbash / Vigenère k ≤ 8 at 66
runes — tiny, enumerated below).

## 1. Cited ledger rows (verified open before writing this)

- **B-24** (status open, raw declared-closed-but-thin): "Round 2 specificity anchor (AN END,
  85 runes) disclosed underpowered". coverage/not_covered: null (never instrumented). This
  cell measures specificity/power AT L=85 with the actual solved AN END page as the in-situ
  control.
- **B-19** (open, declared-closed-but-thin): "Round 9 LENGTH closed on the lower bound, not
  the point estimate". coverage/not_covered: null.
- **B-20** (open, scope-limited): "Round 9 DIRECTION: 400-rune reads, ≤64 starts → 'do not
  revive'". coverage/not_covered: null. This cell's direct reads include {fwd, rev} at the
  exact short-page lengths, with measured power — the honest fragment of what B-19/B-20
  disclose as weak. (Full LENGTH/DIRECTION re-closure is NOT claimed; see §7 not_covered.)
- Context: R43 `X0-firewall/ADJUDICATION.md` item 24 (REOPEN) names this cell's ground.
- Reused, not re-run: `R44-P2-*`, `R44-P4-*`, `R44-R1-*`, W2-A4's row (their stored
  per-page bests are inputs; their LEDGER rows and sweeps are untouched).

## 2. The Aiming Test

**Q1 — What would a hit look like, and would THIS instrument recognise it?**
A hit = one of the three shortest unsolved pages is (i) a direct/affine-dressed or (ii) a
classically-enciphered (periodic shift k ≤ 8, optionally atbash-composed, either direction)
natural-language fragment in a panel-R36 register. Recognizer = panel-R36 pmax against
family-wise bars calibrated on matched-LENGTH surrogates through the SAME glue. Plants:
(1) GLUE plants that are not analogues but the real thing — the two SOLVED canon pages p55
(L=85) and p56 (L=95) read through this cell's own 116-map grid; the identity cell MUST
cross the node bar, else INSTRUMENT-INCOMPLETE and stop. (2) CLASSICAL glue plant — one
held-out English window at L=66 enciphered with a known k=3 key and pushed through the full
attack pipeline; must be exactly recovered and cross the classical bar. (3) POWER plants at
every node and every bar this cell issues verdicts against (details in §4). If the attack
cannot recover its own plant at some k, that k is reported at its measured (low) power and
no negative is claimed there.

**Q2 — What measured fact raises the prior above flat?**
(i) The ledger's own self-disclosure: B-24/B-19/B-20 record the short-page closures as
underpowered/weak — the reopening condition is the instrument this cell builds (same logic
that discharged W2-A1's rows). (ii) R43 X0 item 24: 3 of 6 blind agents independently
converged on short/end pages as the place a lighter cipher would hide (blind convergence is
this round's ranking currency). (iii) Measured: every standing per-page sweep adjudicated
L=66–92 pages against an L=120 bar — a documented instrument gap at exactly these pages.

**Q3 — Is the space bounded?**
Enumerable and small, all counts fixed here:
- Direct reads: 3 pages × 116 maps = 348 ≤ **N_direct = 600** (bars fixed at 600).
- Classical p49: dir {fwd,rev} × a {1,28} × [k ≤ 3 FULL exhaust: 29+841+24,389 = 25,259;
  k = 4..6 per-column beam B=4: 256+1,024+4,096; k = 7..8 beam B=3: 2,187+6,561] =
  4 × 39,383 = **157,532 ≤ N_cl = 160,000** (bar fixed at 160,000).
- Re-adjudication: 12 stored cells (4 lanes × 3 pages), **0 new decodes**.
- Null build: (SEL + WIN-U) × 5 nodes × 1,000 surrogates × 116 maps = 1.16 M; VIGK (L=66)
  1,000 × 116; ATTSEL (L=66) = the full attack on 20 surrogates ≈ 3.15 M.

**Q4 — The three conditionals any negative here carries:**
1. *key space:* direct/affine (116 maps) on p49/p50/p54; periodic polyalphabetic shift
   (Vigenère) k ≤ 8 × a ∈ {1,28} × both directions on p49 only — with k ≥ 4 covered only
   through the per-column beam (B=4 for k=4..6, B=3 for k=7..8) guided by an ENGLISH rune
   unigram; a key whose columns fall outside the top-B unigram shifts is NOT covered, and
   the per-k power measurement quantifies exactly that.
2. *transition model:* memoryless monoalphabetic / periodic substitution. No chained,
   output-aware, autokey, transposition, or running-key constructions.
3. *adjudicator register:* panel-R36's 12 registers at the MEASURED power per (L, N) cell
   (Addendum 1). The panel length-calibration covers these L natively (≥ 32, no clamp).
   The beam guidance unigram is English-trained: classical power is measured separately
   for EN and LATIN plants, and the LATIN number is the honest ceiling for non-English.
   Re-adjudication additionally carries: the bespoke null population is affine-grid decodes
   of canon surrogates, not each lane's own decode population; `bars_v3` keyskip bars at
   the same (N, L) are reported alongside as the beam-population cross-check.

**Q5 — Kill condition at 10% of budget:**
(i) Either solved-page glue plant (p55/p56 identity) fails its node bar →
INSTRUMENT-INCOMPLETE, stop, no verdicts. (ii) Any POT fit with < 50 tail exceedances or
non-finite beta → that node uncalibrated, its cells measured-only. (iii) The classical k=3
glue plant is not recovered at full-exhaust → the classical component is
INSTRUMENT-INCOMPLETE (direct + re-adjudication components may still proceed; said
loudly). Checkpoint: after `null_bars.py` + `plant_power.py` + the classical plant gate,
before Addendum 1 and before any real read.

## 3. Instrument definition (FIXED)

- **Canon:** `data/krisyotam_runes.txt`, 13,136 runes, 57 pages; unsolved prefix =
  canon[0:12956] (pages 0–54). Page starts asserted in code from per-page counts.
- **Reading grid** (identical for null, plants, real direct reads): {fwd, rev} × affine
  a ∈ {1, 28}, s ∈ 0..28 = 116 decodes — the standing W2-A1 grid, same code path.
- **Adjudicator:** standing panel-R36 (`round19/I2/adjudicate.py` +
  `data/panels/panel-r36.npz`), `adjudicate_batch` pmax; standing R38 degenerate guard
  (mds ≤ 6 or IoC·N ≥ 4.24) applied to any would-be crosser via full `adjudicate()`.
- **Null families, seed 3301**, matched length, L-nodes {66, 76, 85, 92, 95}:
  - `SEL`: L sorted canon positions, uniform without replacement (whole canon — as W2-A1);
  - `WIN-U`: contiguous L-windows at uniform start **within the unsolved prefix**
    (deviation from W2-A1's whole-canon WIN, reason stated: at these L the solved pages
    p55/p56 are THIS cell's plants; leaving them in the null would put the plant inside
    the null tail. Deviation disclosed here, before execution.);
  1,000 surrogates each × the 116-map grid → 116,000 null pmax per (family, node).
  - `VIGK` (L=66 only): 1,000 WIN-U surrogates × 116 random classical configs each
    (k ~ U{2..8}, dir ~ U{fwd,rev}, a ~ U{1,28}, s-vector uniform) — the classical decode
    population under H0.
  - `ATTSEL` (L=66 only): the FULL classical attack pipeline (identical code path to the
    real read, including the unigram-guided beam selection) run on 20 fresh WIN-U
    surrogates, every generated candidate adjudicated (~157,532 each, ≈ 3.15 M pooled) —
    the selection-biased null the beam actually produces.
- **Bar model:** bars_v3's refit exactly as W2-A1 (`pot_fit`/`pot_bar` code path):
  exponential peaks-over-threshold above the empirical 90th percentile;
  bar(N) = u + β·ln(p_u) + β·ln(N / −ln(1−α)), α = 0.01.
  - **Direct-read bar of record per node** = max(SEL, WIN-U) at N = 600.
  - **Classical bar of record (L=66)** = max(SEL, WIN-U, VIGK, ATTSEL) at N = 160,000.
  - **Re-adjudication bars** = max(SEL, WIN-U) at each lane's N, computed at BOTH the
    lane's per-page N and the lane's family-wise N: P2 (12,184; 670,120), P4 (92,160;
    5,068,800), R1 (2,000,000; 2,000,000 — its own n_bar), A4 (50,000; 50,000). Cross-check
    (reported, not bar of record): `bar_v3(N, L, "keyskip1"|"keyskip2", family="lp2")` —
    bars_v3's keyskip series HAS an L=31 node, so interpolation at 66–92 is in-range.
- **Classical attack (p49, FIXED):** decode_i = (a·c_i + s_{i mod k}) mod 29 over
  dir ∈ {fwd, rev} (rev = reversed page), a ∈ {1, 28} (a=28 = atbash-composed), k ∈ 1..8.
  k ≤ 3: full exhaust of s ∈ Z29^k. k ≥ 4: per column j, rank the 29 shifts by column
  log-likelihood under the EN rune unigram (trained on the FIRST half of
  `data/keys/self_reliance.txt` — the panel-build half, disjoint from the held-out plant
  half; add-0.5 smoothing); enumerate the product of the top-B shifts per column
  (B = 4 for k = 4..6, B = 3 for k = 7..8). All candidates panel-adjudicated.
- **Power floor for any verdict: measured EN power ≥ 0.5 at that cell's (L, N) bar.**
  Below floor → measured / instrument-bound, by design, stated per cell.
- Any bar-crosser (non-degenerate) is **FLAGGED-FOR-ORACLE** per HUMAN-ORACLE.md, never
  certified. Degenerate crossers are recorded and killed per the standing R38 rule.
- Numeric bars + powers appended as **Addendum 1 (dated) BEFORE any real read**; PREREG
  re-hash-stamped into `run.log`.

## 4. Power measurement (FIXED)

- Per node L: 300 held-out EN windows (second half `data/keys/self_reliance.txt`, encoded
  via `lp.gematria.keyword_to_indices`) + 300 held-out LATIN windows (second half
  `analysis/latin/latin_28233.txt`), each through the 116-map grid; power(bar) = fraction
  of window grid-maxes ≥ bar — evaluated against (i) the node's N=600 direct bar and
  (ii) every re-adjudication bar at that node's L. RNG seed 3301.
- Classical, per k ∈ 1..8: 30 EN + 30 LATIN held-out windows at L=66, each enciphered
  c = a·(p − s) mod 29 (a self-inverse) with random a, random s-vector of length k;
  power = fraction where [the true key is generated by the attack: k ≤ 3 always (full
  exhaust); k ≥ 4 iff every true column shift is in that column's top-B] AND
  [pmax(true decode) ≥ classical bar]. This is exact recovery power through the real glue,
  not an analogue.
- EXPECTATION, stated in advance: power at sweep-scale N (especially R1's 2 M and P4's
  5.07 M) and at k ≥ 6 (columns of 8–9 runes under a top-B unigram beam) will be low.
  Wherever it is < 0.5 the corresponding cell is reported as instrument-bound/measured —
  that honest statement IS a deliverable of this cell, per the X0 item-24 reopen.

## 5. Real targets (FIXED; run only after Addendum 1)

| read | object | L | N (bar) |
|---|---|---|---|
| direct 116-grid | p49 (canon 12048–12113) | 66 | 600 |
| direct 116-grid | p54 (canon 12880–12955) | 76 | 600 |
| direct 116-grid | p50 (canon 12114–12205) | 92 | 600 |
| classical exhaust+beam | p49 only | 66 | 160,000 |
| re-adjudication (no new decodes) | stored bests: P2/P4/R1/A4 × p49/p50/p54 | 66/92/76 | each lane's N |

Stored bests being re-adjudicated (copied verbatim from the lanes' results JSON before
execution): P2: 4.794/4.471/4.389; P4: 4.964/4.783/5.748; R1: 4.890/4.678/4.791;
A4: 4.433/3.585/3.301 (order p49/p50/p54).

## 6. Budget / N accounting

Real adjudicated decodes: 348 (direct) + 157,532 (classical) = 157,880; bars fixed at 600
and 160,000 respectively. Null: ≈ 1.16 M (SEL/WIN-U) + 116 k (VIGK) + ≈ 3.15 M (ATTSEL).
Plants: 348 k (node power) + ≤ 500 classical plants (membership check + 1 adjudication
each). Pure python3 + numpy, no network, no image work.

## 7. Coverage / not_covered (declared in advance)

Covers: the short-page instrument (bars + EN/LA power at L 66/76/85/92/95, incl. at the
four standing sweeps' N); p49/p50/p54 direct/affine reads at measured power;
p49 classical (shift/atbash/Vigenère ≤ 8) at measured per-k power; re-adjudication of the
12 stored per-page bests. Does NOT cover: k > 8, transposition, autokey, running-key,
chained/output-aware ciphers on these pages; non-EN-unigram beam guidance for k ≥ 4;
p50/p54 classical (p49 only, per the X0 item); any re-closure of B-19/B-20's full
LENGTH/DIRECTION ground (only the short-page fragment at these L); sub-page segments.

## 8. Outputs

`glue.py`, `null_bars.py` → `nulls.json`, `plant_power.py` → `power.json`,
`classical.py` → `classical.json`, `readjud.py` → `readjud.json`, `RESULTS.md`,
`ledger_rows.json`, `run.log` (hash-stamped). LEDGER.json NOT modified.

---

## Addendum 1 — 2026-11-09, at the Q5 checkpoint, BEFORE any real read

**No threshold is edited. Two disclosures and the numeric instrument follow.**

**Disclosure A — the §0/§2 premise about p55 was WRONG, measured at the checkpoint.**
p55 (L=85) is NOT solved plaintext: its identity transliteration is ciphertext
(`AEJOESRMYLO…`), identity pmax 1.0317, grid max 3.4255 — while p56 is the solved Parable
(`PARABLELICETHEINSTAR…`, identity pmax 16.9518 = grid argmax, PASSED its node bar
5.8395). Consistency check: W2-A1's WIN-null plaintext outliers appear at L=26–40 (fits
inside p56's 95 runes) and vanish at L=120 — consistent with p56 being the ONLY solved
canon page. Consequences, dated here before any further execution: (i) the glue gate
Q5(i) is judged on p56 alone, which PASSED — the 116-map grid + panel + bar code path
demonstrably recognises a real solved canon page through this cell's own glue; (ii) p55
is promoted from "plant" to REAL TARGET — it is exactly B-24's "AN END, 85 runes" object,
and it was verified ABSENT from all four standing per-page sweeps (pages 0–54 only), so
it has never had ANY per-page adjudication; (iii) the p55 grid read already executed
(as a believed plant, 116 decodes ≤ the 600 budget) is hereby re-classified as a real
read executed before this addendum under the wrong premise — numbers frozen as measured
(identity 1.0317, grid max 3.4255), disclosed for the X1 critic; its verdict is issued
against the pre-registered N=600 bar and the measured L=85 power, unchanged by the
reclassification.

**Disclosure B — classical k=3 glue plant.** Q5(iii) as pre-registered requires RECOVERY
through the full-exhaust path: recovered = True, so Q5(iii) did NOT fire. The plant's
true-decode pmax 11.4876 fell 0.37 under the bar 11.8542 on its single draw; that is the
measured k=3 EN power (0.90) manifesting once, and the `passed` flag computed in code was
stricter than the pre-registered gate. The bar is NOT lowered; the single-draw miss is
recorded. Note the classical bar of record is dominated by the ATTSEL selection-biased
family (POT extrapolation 11.8542 vs pooled null empirical max 8.3785 over 3.15 M) — a
conservative bar, per bars_v3's documented property.

**Bars of record** (nulls.json; all POT fits ≥ 11,600 exceedances, Q5(ii) never fired):

| L | direct bar (N=600) | classical bar (N=160,000) |
|---|---|---|
| 66 | 5.8403 | 11.8542 (= max SEL 8.1025 / WIN-U 8.1546 / VIGK 8.2292 / ATTSEL 11.8542) |
| 76 | 5.8545 | — |
| 85 | 5.8330 | — |
| 92 | 5.8589 | — |
| 95 | 5.8395 | — |

Re-adjudication bars (max SEL/WIN-U at each lane N), L=66/76/85/92 ≈ (per nulls.json):
P2 page-N 7.09 / lane-N 8.75; P4 92k 7.93 / 5.07M 9.59; R1 2M 9.20; A4 50k 7.67.

**Measured power** (power.json): EN and LA power = **1.0000 at every node L ∈
{66,76,85,92,95} against EVERY bar issued** — the N=600 direct bars and all re-adjudication
bars up to N=5,068,800 (EN median grid-max 13.38–16.40 ≫ all bars ≤ 9.62). The §4
expectation of low power at sweep-scale N was WRONG for direct-dressed plants — said
loudly: at these lengths the panel has full direct-dress power even at 5 M decodes.
Classical per-k power (EN/LA): k=1 0.83/0.80, k=2 0.90/0.83, k=3 0.90/0.83, k=4 0.83/0.93,
k=5 0.87/0.80, k=6 0.77/0.77, k=7 0.60/0.63, k=8 0.60/**0.37**. All k are EN
verdict-capable (≥ 0.5); LA at k=8 is below floor — any classical negative carries that
LA k=8 hole explicitly. Power declines with k exactly as §4 predicted (beam-membership
loss), just less steeply than feared.

Real reads now proceed per §5, plus p55 direct (disclosed above).
