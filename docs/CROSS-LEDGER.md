# Cross-ledger: this repo ↔ other public LP2 ledgers

Two groups are running preregistered LP2 campaigns in public. This page maps them onto
each other, so an idea is ruled out once, not twice, and a positive gets replicated
instead of rediscovered.

| ledger | where | unit | rows (2026-11-17) |
|---|---|---|---|
| **Dukotah/cicada3301** | [`liber-primus/LEDGER.json`](../liber-primus/LEDGER.json) | one row per lane/cell, `id` like `R44-W2B3-D01-FALSIFIER` | 350 |
| **njloof/cicada-lp2-sweeps** | [`docs/LEDGER.md`](https://github.com/njloof/cicada-lp2-sweeps/blob/main/docs/LEDGER.md) | one row per campaign `#N`, with per-family verdicts | 17 campaigns |
| **RiskAverseTech/cicada-ioc** | [`README.md`](https://github.com/RiskAverseTech/cicada-ioc) (numbered §§), [`results/`](https://github.com/RiskAverseTech/cicada-ioc/tree/main/results) | one numbered section per study | paused 2026-11-01 |
| **micheloosterhof/aldegonde** | [`hypotheses/`](https://github.com/micheloosterhof/aldegonde/tree/master/hypotheses) ([`INDEX.md`](https://github.com/micheloosterhof/aldegonde/blob/master/hypotheses/INDEX.md)) | one file per hypothesis, from `TEMPLATE.md` | active 2026-11 |

Individual contributors whose corrections landed here: **RETSAM3301** (page numbering and the seg 8 / seg 40
separators, #12), **njloof** (#13, #14), **mariostabile1** (#11).

Want your ledger listed? Open an issue or PR. The bar is the five rules in
[`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Page numbering

Both ledgers now use **book page numbers** when they name pages at or above 50. Older
rows in either ledger may use segment indices; see
[`PAGE-NUMBERING.md`](../liber-primus/data/PAGE-NUMBERING.md). njloof campaigns #1–#8
were run before the relabel; their ids 50–54 are book pages 51–55.

## Replications and corrections across ledgers

| item | first filed | confirmed / corrected by | status |
|---|---|---|---|
| **T7: doublet slip rate is non-stationary** | here, R44 `R44-W2B3-D01-FALSIFIER` (p=0.0010; X1 p=0.00025) | njloof #10 (p=0.0006, independent nulls), localized to three consecutive large doublet gaps (400/712/537 runes vs ~151 typical) spanning stream pos 2739–4388, internal doublets at 2740/3140/3852 (njloof #13 correction, 2026-11-19: not doublet-free) | **reproduced** (same 86 published sites, independent nulls: validates both null calibrations, not an independent observation), **measured, not certified**. Live lane for R45 |
| Page numbering from 50 on (segment = book − 1) | RETSAM3301, #12 (mapping); njloof, #14 (root cause + proof) | adopted here 2026-11-17 | fixed in `PROBLEM.json`; old round docs read through the table |
| Payload byte idx 246 = `0xc6` (`3I`) | here, R19 C1 (image) → promoted R34 | njloof #14 (pixel measurement + human read) | agreed. Campaign VII doc now marked superseded at 45/50/246 |
| Payload bytes idx 165 = `0x12`, 172 = `0x94` | here, Campaign VII | njloof #14 (pixels) | agreed |
| Separator corrections seg 8 / seg 40 | RETSAM3301, #12 | here, R33 B2 (`9b36692`) | landed |
| **Independent blind re-read of the unsolved pages** | RiskAverseTech/cicada-ioc §38 (machine read of the page images, no access to the transcription) | agrees with the canonical transcription at 12,807/12,807 aligned glyphs (98.8 % of 12,956 positions) | cited 2026-11-20 in `TRANSCRIPTION-VERDICT.md` (supersedes its "no independent read exists") |
| pp49–51 stale tokens in rtkd/iddqd master (`1L 0L 0l 2s 3i`) | tz18 (rtkd PR #8), Inky (PR #7); still open upstream | merged in cicada-solvers/iddqd 2024-10-12; matches our `canon_256.hex`; `fetch_sources.py` now pins the PR #8 head | open upstream, reviewed 2026-11-20 |
| p15 4×4 grid: 14/16 = 3301−prime | here, R44 P2 (`R44-P2-P15GRID-TRANSCRIPTION`) | njloof #14 (2026-11-19): **16/16 cells = \|3301 − prime(F+1)\|, F Fibonacci 0–987 along a square spiral from the red 3299**; the two R44 "breakers" are sign flips | **adopted** 2026-11-19 as `R45-COMM-P15GRID-CLOSEDFORM`; reproduced by `closed_form_check.py` |
| T7 span "doublet-free void" | njloof #10, copied here at `6b94529` | njloof #13 (2026-11-19, their LEDGER C1) | corrected: internal doublets at 2740/3140/3852; three large gaps 400/712/537 |
| English-only-negative failure mode | here, R18 L7-A | njloof adopted language-agnostic χ² as design rule | shared method |
| `skip_by_two` stride pads | flagged uncovered here | njloof #3 (negative), #5 (products, negative) | closed in their ledger |
| 32-bit seed sweeps: Perl, POSIX, Xorshift32 | mariostabile1, PR #11 | merged here 2026-10-28 | 0 hits |

## Where the two ledgers cover the same ground

These are closed in **both**. Don't re-run them without a new instrument.

- Cross-page running pads: theirs #1–#6 (≈329M alignments, all algebra families) ↔ ours R44 C2 all-pairs page-keying (6.4M decodes).
- Number channels as keys: theirs #7 ↔ ours R37 C1 (LP1 numbers as key schedules).
- Self-derived keys / word sums: theirs #8, #11 ↔ ours R10 L2, R37 C3 (word sums as cleartext).
- Token table / pp49–51 payload as pad or target: theirs #12, #14 ↔ ours Campaign VII/IX, R30 B1/B2, R44 P4.
- Red ink: theirs #15 (red digits as selectors) is related to, not identical with, ours R44 P1 (red-ink census) and P2 (p15 grid).

## Things one ledger has that the other doesn't

**In njloof's, not yet reflected here:**
- #13: dot-lattices co-locate with red section openings (p=0.00065, structural only).
- #16: the black 4-dot diamond is the rendered sentence separator `.` (126/127); `&` = 13-dot lattice; `$` still unmapped.
- #17: all 6 apostrophes are word-medial, which fits English and rules out Latin.
- p15 printed digit group `3299` is red.

**In ours, open for anyone:** see [`OPEN-LANES.md`](OPEN-LANES.md).

## Method lessons worth copying (from njloof's campaigns)

- **Nulls are family-specific.** Their sum-statistic null sits ~46 χ² above the difference-statistic null. A threshold borrowed from another family crowned four false hits on real data.
- **≤20-draw flags are provisional.** Their #3 page-12 flag (p≤0.048 at 20 draws) dissolved at 1000 draws (p=0.099). Any flag from a coarse null needs its own confirmation campaign before it circulates. Their escalation rule: a family reaching its 20-draw null median goes to ≥200 draws before a verdict ships.
- **The gcd trap in self-pair permutation scans.** A 195.2 flag came entirely from self-pair cyclic reads where gcd(a±1, L) fixed points manufacture ᚠ pile-ups arithmetically. Target-shuffle nulls cannot see that channel. Exclude self-pairs or use a pad-side null.
- **Derive-from-shuffled nulls for self-derived keys.** When the key is computed from the text, re-derive it on every null draw.
- **Page-marginal χ² can be structurally blind** under value-dependent self-keys or many-to-one output maps (their #11, #12: 0/10 plants). Check power before reading a negative.

## Proposed interchange row

If you want your results merged into `LEDGER.json`, send these fields (JSON or a table
row, either is fine):

```json
{
  "id": "<your-prefix>-<campaign>-<family>",
  "hypothesis": "one sentence, falsifiable",
  "status": "negative | measured | inconclusive | open",
  "date": "YYYY-MM-DD",
  "threshold": "what counted as a hit, fixed before output",
  "threshold_fixed_in_advance": true,
  "null": "how the null of the max was built, draws, seed",
  "positive_control": "passed | failed | none",
  "control_detail": "planted signal and recovery rate",
  "coverage": "what space was actually covered",
  "not_covered": "what was not",
  "evidence": "URL to the report",
  "reproduce": "commands"
}
```
