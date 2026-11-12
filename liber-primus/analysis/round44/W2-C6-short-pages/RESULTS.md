# Round 44 / WAVE-2 CELL C6 — SHORT-PAGE SPECIFICITY AT HONEST POWER — RESULTS

_Run 2026-11-09/10. PREREG.md (incl. dated Addendum 1, written at the Q5 checkpoint BEFORE
any real read) preceded every output; hash-stamped twice in `run.log`. Instrument:
panel-R36 (`round19/I2/adjudicate.py` + `data/panels/panel-r36.npz`); bar model = bars_v3's
exponential-POT refit on bespoke matched-length nulls at the exact short-page lengths.
Pure python3 + numpy, no network. Cited rows: B-24, B-19, B-20 (+ R43 X0 item 24 REOPEN)._

## Verdict

**INSTRUMENT BUILT + the underpower question is now MEASURED, and the answer inverts the
ledger's fear: at the short-page lengths the panel is at FULL power.** EN and LA plant
power = **1.0000 at every node L ∈ {66, 76, 85, 92, 95} against every bar this cell
issues — including bars at the standing sweeps' own N up to 5,068,800** (EN median
grid-max 13.38–16.40 vs bars ≤ 9.62). B-24's "disclosed underpowered" no longer has to be
taken on (missing) disclosure: it is replaced by a measured power envelope, and the
short-page negatives SURVIVE it.

**Real reads: 157,996 adjudicated decodes + 12 re-adjudicated stored cells. 0 crossers.
Nothing FLAGGED-FOR-ORACLE.**

1. **Direct/affine (116-map grid, bars at N=600, power 1.0 EN+LA):** p49 best 2.8694 vs
   5.8403; p54 3.5251 vs 5.8545; p50 3.6218 vs 5.8589; p55 3.4255 vs 5.8330 →
   **NEGATIVE at power 1.0** for all four.
2. **p49 classical exhaust** (shift/atbash/Vigenère: k ≤ 3 FULL exhaust, k=4–8
   EN-unigram beam; 157,532 candidates, the X0 item-24 ask): best 7.1074 (k=8 beam, rev)
   vs bar of record 11.8542 — and also under every non-selection family bar (8.10–8.23).
   **NEGATIVE at measured per-k EN power 0.60–0.90** (per-k table below; LA k=8 = 0.37 is
   below floor and that hole is carried explicitly).
3. **Re-adjudication of the 12 stored per-page bests** (P2/P4/R1/W2-A4 × p49/p50/p54)
   under bespoke matched-length bars at the lanes' own N: all stay under by ≥ 2.1 (page-N
   bars 7.09–9.23), at measured EN power 1.0. **The standing short-page negatives HOLD
   under honest short-length adjudication.**

**The cell's one discovery is a premise correction with a coverage hole attached (Addendum
1 Disclosure A): canon p55 — the 85-rune "AN END" body, B-24's own object — is NOT solved
plaintext and is ABSENT from all four standing per-page sweeps (they sweep pages 0–54
only).** Its first-ever per-page adjudication is this cell's direct read (negative at
power 1.0); every keyed per-page family the standing sweeps ran on pages 0–54 remains
UNRUN on p55. That gap is named in not_covered and is the concrete reopener this cell
hands forward.

## 1. Positive controls (through this cell's own glue; no verdict preceded them)

| gate | result |
|---|---|
| Glue plant = the real solved canon page p56 (Parable, L=95) through the 116-grid | identity pmax **16.9518 ≥ bar 5.8395**, identity = grid argmax → **PASSED** |
| p55 as intended second glue plant | **premise WRONG, measured at checkpoint**: p55 is ciphertext (identity 1.0317) — reclassified to real target per dated Addendum 1, numbers frozen; disclosed for X1 |
| Classical k=3 glue plant (known key, full pipeline) | **RECOVERED = True** (Q5(iii) did not fire); true-decode pmax 11.4876 vs bar 11.8542 single-draw miss = measured k=3 power 0.90 appearing once; bar NOT lowered; disclosed |
| POT fits (Q5(ii)) | every node ≥ 11,600 exceedances — never fired |

## 2. The instrument (nulls.json, power.json; seed 3301, α=0.01)

Null families per node: SEL (sorted canon position selections) + WIN-U (contiguous windows
over the unsolved prefix canon[:12956]; deviation from W2-A1's whole-canon WIN disclosed in
PREREG §3 — the solved page is this cell's plant, so it cannot sit in the null), 1000
surrogates × 116-map grid each. L=66 adds VIGK (random classical configs) and ATTSEL (the
FULL attack pipeline on 20 surrogates, 3.15 M pooled candidates — the selection-biased
null the beam actually produces; it dominates the classical bar: 11.8542 vs pooled
empirical max 8.3785, conservative by bars_v3's documented POT property).

| L | direct bar (N=600) | EN / LA power | re-adjudication bars (page-N → lane-N) | EN power at ALL of them |
|---|---|---|---|---|
| 66 | 5.8403 | 1.00 / 1.00 | P2 7.088→8.748; P4 7.926→9.586; R1 9.201; A4 7.673 | 1.00 |
| 76 | 5.8545 | 1.00 / 1.00 | 7.094→8.744; 7.927→9.577; 9.194; 7.676 | 1.00 |
| 85 | 5.8330 | 1.00 / 1.00 | 7.072→8.722; 7.905→9.555; 9.172; 7.654 | 1.00 |
| 92 | 5.8589 | 1.00 / 1.00 | 7.111→8.777; 7.952→9.618; 9.232; 7.698 | 1.00 |
| 95 | 5.8395 | 1.00 / 1.00 | (validation node, p56) | 1.00 |

Classical (L=66, bar 11.8542 at N=160,000): per-k power EN/LA = k1 0.83/0.80, k2 0.90/0.83,
k3 0.90/0.83, k4 0.83/0.93, k5 0.87/0.80, k6 0.77/0.77, k7 0.60/0.63, k8 0.60/**0.37**.
All k verdict-capable for EN (≥ 0.5 floor); **LA at k=8 is below floor** — the classical
negative does not cover Latin-register Vigenère k=8, said here and in the row.
bars_v3 keyskip cross-checks at the lanes' N (reported, not bars of record) sit at
9.1–11.6 — same order as the bespoke bars; no stored best approaches either.

## 3. The real reads

**Direct (direct.json; 464 decodes ≤ 600):** best maps and full R3 stats per page are in
the JSON (all non-degenerate; e.g. p49 best = rev/a=28/s=13, en −7.10 noise). 0
crossers.

**Classical p49 (classical.json; 157,532 = exactly the PREREG count):** global best
7.1074 = a k=8 beam candidate (rev, a=1), i.e. the maximally-selected cell of the sweep —
exactly where the null says the max should land (ATTSEL emp max 8.38). Non-degenerate; its
transliteration is noise ("IDIGCLCDNHOFIEWGF…"). Top-10 with full R3 stats persisted. 0
crossers; k ≤ 3 FULL exhaust means: **no shift, atbash, or Vigenère key of period ≤ 3
exists (either direction, plain or atbash-composed) that renders p49 as panel-visible
language — unconditionally within the register panel**; k=4–8 negative at the measured
beam power above.

**Re-adjudication (readjud.json; 0 new decodes):** all 12 cells under both page-N and
lane-N bespoke bars, margins 2.14–4.55. Note the direction of the original error: the
lanes applied L=120 bars from their OWN (beam/key-family) null populations (12.96–15.67),
which were HIGHER than the honest matched-length bars at their N — the standing
adjudications were conservative, not lenient; what was missing was the power measurement,
which is now 1.0.

## 4. Coverage × not_covered

**Covered:** the short-page instrument of record (bars + EN/LA power at L ∈
{66,76,85,92,95}, incl. at N up to 5.07 M); direct/affine reads of p49/p54/p50/p55 at
power 1.0; p49 classical — full exhaust k ≤ 3 × {fwd,rev} × {plain, atbash-composed},
EN-unigram-beam k=4–8 at per-k power 0.60–0.90 EN; re-adjudication of all 12 stored
short-page bests.

**not_covered (the three conditionals, PREREG §2 Q4, plus the gap found):**
- *key space:* k > 8, transposition, autokey, running-key, chained/output-aware ciphers on
  these pages; k=4–8 keys whose columns fall outside the EN-unigram top-B beam (power says
  60–90 % of random such keys ARE caught, the rest are not); p50/p54/p55 classical (p49
  only, per the X0 item); sub-page segments.
- **p55 (AN END body): every keyed per-page family the standing sweeps ran on pages 0–54
  (P2 grid keys, P4 blob pads, R1 reset keys, A4 chained-presentation offsets) was NEVER
  run on p55.** Reopener: any per-page sweep should extend its page loop to 55; this
  cell's direct read is p55's only per-page record.
- *transition model:* memoryless monoalphabetic / periodic substitution only.
- *adjudicator register:* panel-R36's 12 registers; classical beam guidance is
  English-unigram (LA k=8 power 0.37 < floor — Latin Vigenère k=8 NOT excluded); all at
  the measured powers tabulated above.
- B-19/B-20 are cited, not discharged: this cell covers only the short-page fragment of
  the Round-9 LENGTH/DIRECTION ground ({fwd, rev} at L 66–95, power 1.0); the 400-rune
  reads and ≤ 64-start ladders of B-20 remain as disclosed there.

## 5. Files

`glue.py` (single shared code path), `null_bars.py` → `nulls.json`, `plant_power.py` →
`power.json`, `direct.py` → `direct.json`, `classical.py` → `classical.json`,
`readjud.py` → `readjud.json`, `ledger_rows.json` (draft rows; LEDGER.json untouched),
`run.log` (hash-stamped pre-execution and pre-real-reads).
