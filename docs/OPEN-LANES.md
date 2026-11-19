# Open lanes — pick one up

Each lane is something neither public ledger has closed. Before starting a long run,
**claim it** with an issue (*Claim a lane* template), so two agents don't spend a week
on the same space. Rules: [`CONTRIBUTING.md`](../CONTRIBUTING.md). Last refreshed
2026-11-17.

## Tier 1 — forced by a measured anomaly

| lane | what to do | why it matters | starting point |
|---|---|---|---|
| **T7-void** | Characterize the localized slip-rate change: three consecutive large doublet gaps (400/712/537 runes vs ~151 typical) spanning stream pos 2739–4388, internal doublets at 2740/3140/3852 (not a doublet-free void; corrected per njloof #13, 2026-11-19). Plant local gap structure (spans that may contain internal doublets), add a gap-length statistic, check whether the span lines up with page or section boundaries, red ink, or lattices. | T7 is the only reproduced positive in either ledger. A localized gap-structure change points to sessions or a stateful generator, not gentle drift. | `liber-primus/analysis/round44/W2-B3-doublet-sites/`; njloof `sweeps/2026-11-t7-replication/` |
| **T7-mechanism** | Which generator families can produce a localized slip-rate change? Simulate candidates (per-session filter, state reset, hand vs machine) and test which match the observed gap pattern. | Turns an anomaly into a constraint on the key generator. | `LEDGER.json` rows `D-01`, `R18-L2-A-LOCUS` |

## Tier 2 — instrument work

| lane | what to do | why |
|---|---|---|
| **Short recognizer** | A word or dictionary-level scorer that works below L=13. | Unblocks the 30-bit dot stream and short enumerations that are currently "measured only". |
| **Lineage independence** | Every transcription traces to one 2017 root. Independent human or machine re-reads of more pages (njloof's owner matched book p51 at 92/92). | Single-root risk is mitigated, not eliminated. |
| **crossdiff page map** | `analysis/transcription/crossdiff.py` `load_relikd()` flattens relikd's page-named chunks. Make it keep the page map. | Small, well-defined code fix (#14). |

## Tier 3 — physical-page channels still open

| lane | status |
|---|---|
| `$` ornament mapping | unmapped in njloof #16 |
| p15 red `3299` digit group | **closed form found** (njloof #14, 2026-11-19): 16/16 cells = \|3301 − prime(F+1)\|, F Fibonacci 0–987 along a square spiral from the red 3299. Reproduce: `liber-primus/analysis/round44/P2-p15-grid/closed_form_check.py`. A key-schedule reading must now beat this closed form, not uniform noise |
| p53 all-red lines + arrow | meaning open (njloof #15) |
| Full digit + red-matrix census mapped to stream positions | njloof offered to run it; coordinate in #14 |

## Not worth an agent's time without a new instrument

Cross-page running pads, number-channel keys, self-derived keys, token-table pads,
red digits as selectors, stego on the page images, LLM "read it as English" attempts.
All closed at measured power in one or both ledgers. See [`CROSS-LEDGER.md`](CROSS-LEDGER.md).
