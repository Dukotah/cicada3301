# Open lanes — pick one up

Each lane is something neither public ledger has closed. Before starting a long run,
**claim it** with an issue (*Claim a lane* template), so two agents don't spend a week
on the same space. Rules: [`CONTRIBUTING.md`](../CONTRIBUTING.md). Last refreshed
2026-11-17.

## Tier 1 — forced by a measured anomaly

| lane | what to do | why it matters | starting point |
|---|---|---|---|
| **T7-void** | Characterize the 1,649-rune doublet-free span (stream pos 2739–4388). Plant local voids, add a void-length statistic, check whether the span lines up with page or section boundaries, red ink, or lattices. | T7 is the only replicated positive in either ledger. A localized void points to sessions or a stateful generator, not gentle drift. | `liber-primus/analysis/round44/W2-B3-doublet-sites/`; njloof `sweeps/2026-11-t7-replication/` |
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
| p15 red `3299` digit group | catalogued (njloof #14), not tested |
| p53 all-red lines + arrow | meaning open (njloof #15) |
| Full digit + red-matrix census mapped to stream positions | njloof offered to run it; coordinate in #14 |

## Not worth an agent's time without a new instrument

Cross-page running pads, number-channel keys, self-derived keys, token-table pads,
red digits as selectors, stego on the page images, LLM "read it as English" attempts.
All closed at measured power in one or both ledgers. See [`CROSS-LEDGER.md`](CROSS-LEDGER.md).
