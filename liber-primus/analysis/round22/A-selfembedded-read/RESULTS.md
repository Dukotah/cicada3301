# RESULTS — Round 22 Lane A: Self-embedded read (roadmap X2)

_Ran 2026-08-29. Binding: `../../../ARMADA-DOCTRINE.md`. Pre-registration frozen in
[`PREREG.md`](PREREG.md) before any candidate was scored._

## Verdict — NULL (control-validated, bounded, not closed)

**No selection of the already-solved plaintext is more English than chance at the
pre-registered bar.** Across both representations of the concatenated solved-page plaintext
(letter stream and rune-index stream), **0 candidates cleared the family-wise bar** out of
**3,508 selection functions swept**. The handful of per-cell "survivors" (6 total) match the
expected false-positive count almost exactly and are all unreadable gibberish.

This is a real, novel result: **the roadmap X2 lens — "seek within / test the knowledge" read
as a self-embedded acrostic of the solved pages — has now been executed literally and returns
clean-negative, control-validated.** It was never run before (Round 11 worked the *ciphertext /
number channel*, N1–N5 / S1–S2, not the decrypted plaintext).

## Trust anchor

`python3 tests/validate.py` → **ALL VALIDATIONS PASSED (5/5)**, before this lane ran. The
solved-plaintext search space is exactly the 5 rig-reproduced pages that validate.py verifies.

## Coverage × power (doctrine R2 — reported together)

| axis | value |
|---|---|
| **Coverage** (selection functions swept) | **3,508** = 1,754 per representation × 2 representations |
| ↳ every-k | k ∈ [2,40], all offsets o ∈ [0,k−1] → ~780 |
| ↳ reversed every-k | same → ~780 |
| ↳ diagonal / anti-diagonal folds | w ∈ [2,60] → ~118 (diag_w == every-(w+1) offset 0; subsumption noted) |
| **Search space** | concat of 5 solved pages, book order: **1,887 letters / 1,769 rune indices** |
| **Measured power (Phase 0)** | **recovery = 1.000** (2/2 planted acrostics recovered as top-by-excess) |
| **Recognizer** | `src/lp/score.py::score_norm` (KJV-weighted quadgram; ~−2.2 English, < −4 noise) |
| **Null** | per-length size-matched, order-shuffled source, seed 3301, 1,000 shuffles, FPR 1e-3 |

**Power is 1.000 on a planted hit of this exact shape** — the instrument provably sees a
self-embedded acrostic when one is present (`PHASE0-GATE.py`), so the null is a real bound, not
an artifact of a blind recognizer (doctrine mechanics R2).

## Phase 0 — positive control (ran FIRST, gated the sweep)

`PHASE0-GATE.py`: planted a known English message at (a) every-7th and (b) width-13-diagonal
positions inside an i.i.d. length-matched control (1,887 letters, seed 3301), then ran the full
sweep. Both plants were **RECOVERED as the top selection ranked by excess over their own
size-matched null bar**:

| plant | recovered as | score | null bar (1e-3) | excess |
|---|---|---|---|---|
| every-k, k=7 o=0 | `everyk_k7_o0` | −4.089 | −6.177 | **+2.088** |
| diagonal, w=13 | `everyk_k14_o0` (≡ diag_w13) | −4.073 | −6.178 | **+2.105** |

Measured recovery / power = **2/2 = 1.000 → GATE PASS.** (A planted signal clears its bar by
~2.1; a real English selection would look like this. The real data does not.)

Instrument note surfaced by the control: **the width-w main diagonal is identical to every-(w+1)
at offset 0** — it selects positions r·w+r = r·(w+1). Diagonals are therefore *subsumed* by the
every-k family; both labels are accepted as the same recovery. This is why the diagonal plant was
recovered under its every-k alias, not a miss.

## The sweep on the real solved plaintext

| stream | selections | distinct lengths | family bar | per-cell survivors (FPR 1e-3) | **family survivors** |
|---|---|---|---|---|---|
| letters | 1,754 | 113 | −2.562 | 4 (expected 1.75) | **0** |
| runes | 1,754 | 111 | −2.711 | 2 (expected 1.75) | **0** |

- **Family-wise bar** = max score over the entire order-shuffled null across all lengths — what
  the single best selection must beat if the book were pure noise. **Nothing cleared it.**
- **Per-cell survivors** (score > its own length's 1e-3 null bar): 4 + 2 = 6, versus **3.5
  expected** by chance at FPR 1e-3 over 3,508 tests — statistically indistinguishable from zero.
  Every one clears its bar by a trivial margin (excess 0.01–0.21) and every one is gibberish:

  - top letters candidate (`everyk_k39_o22`, +0.210): `OTDANSTTUATTTISRAANMEASAHECLEELDATNNEEN…`
  - top runes candidate (`everyk_k39_o19`, +0.056): `OEDILOYNTHIYUAOTHATHEEIDTHYINGEDOONGMYAH…`

  Best score overall is **−5.37** (letters) / **−5.25** (runes) — solidly in the noise band
  (real English is ~−2.2). No survivor is FLAGGED-FOR-ORACLE because none clears the bar.

Full per-candidate records (English score + IoC·N + min-distinct-32 + base32-fraction + gzip
ratio, doctrine R3) persisted in [`sweep_results.json`](sweep_results.json).

## The three conditionals this negative carries (doctrine Q4)

1. **Selection space swept:** every-k (k≤40, all offsets) + reversed + diagonal folds (w≤60),
   both representations. **NOT covered** below.
2. **Transform:** identity on already-decrypted runes (the selection *is* the transform), so the
   decoder-transition conditional collapses here — the swept axis is the selection function.
3. **Adjudicator register:** English quadgram (KJV-weighted). A selection spelling Latin/Welsh/a
   base32 pointer could be missed by the English score; the persisted `base32_frac`, `ioc_n`,
   `min_distinct_32`, and `gzip_ratio` secondary stats show **no structured outlier** either
   (no candidate has anomalous compressibility or a high base32 fraction with low entropy).

## What is NOT covered (reopeners)

- **Word/line acrostics with true physical structure.** We have only the *concatenated
  transliteration*; the real per-page line breaks and word spacing of the printed book are not
  reconstructed here. A first-rune-of-each-printed-line acrostic is **unenumerated** (needs the
  page-image line geometry — a P0.2/P0.3-style transcription). This is the sharpest reopener.
- **The wider community-solved corpus.** This repo trusts only the 5 pages `validate.py`
  reproduces (A WARNING, SOME WISDOM, two KOANs, WELCOME). The community has solved a few more LP
  pages (e.g. the "AN END" / parable material) that are not in `SOLVED-PAGES.json`; a self-embedded
  read over the *full* community-solved set is unenumerated here.
- **Keyword-cued / two-stage selections** (take every rune after each occurrence of a cue word;
  read the acrostic of the KOAN answers only). Unbounded-ish; not swept.
- **Non-English target registers** beyond the secondary-stat screen (a selection that is Latin
  prose would need a Latin LM to score, not just the base32/IoC screen).

## Reproduce

```bash
cd liber-primus && python3 tests/validate.py            # 5/5, the trust anchor
cd analysis/round22/A-selfembedded-read
python3 PHASE0-GATE.py                                   # positive control: recovery 1.000, PASS
python3 run_sweep.py                                     # the sweep: 0 family survivors -> NULL
```

## Seal note (R21 L1)

Moot here — there is no survivor to certify. Had one cleared the bar it would be
**FLAGGED-FOR-ORACLE, not auto-certified**, per the Round 21 L1 leaky-seal finding.
