# ORACLE BUNDLE — W2-C1 battery statistics S1 + S3 crossed their registered bar

_Per `HUMAN-ORACLE.md`: a survivor that clears a pre-registered bar is flagged-for-oracle,
never auto-certified — and never auto-dismissed. This bundle contains the registered pass
AND the added control that (in this lane's judgment) explains it. The oracle decides._

## 1. What crossed

Pre-registered battery (PREREG.md §5a): 6 order/identity statistics over the figural-motif
catalog streams, seed-3301 nulls, 10,000 draws, survivor iff any p < 0.01/6 = 1.667e-3.

| statistic | p | bar | crossed |
|---|---|---|---|
| S1 presence-gap variance (38 motif pages of 56) | **2.0e-4** | 1.667e-3 | YES |
| S3 zlib compressibility of the 95-token type sequence | **1.0e-4** | 1.667e-3 | YES |
| S2 spearman(V1, page) | 0.93 | — | no |
| S4 zlib orientation stream | 0.013 | — | no |
| S5 prime counts | 0.98 | — | no |
| S6 centroid-y drift | 0.43 | — | no |

Evidence: `../results/reads.json` (battery block), streams in `../results/streams.json`,
catalog in `../results/catalog.json` (95 motifs, every entry citing its crop).

## 2. The added specificity control (R22-D H7/H8 precedent; registered result unaltered)

The S1/S3 null is page-exchangeability. But ANY codex whose illustration plates change per
chapter violates exchangeability with no hidden signal. Control
(`../scripts/control_specificity.py`, `../results/control_specificity.json`): 300 synthetic
"boring sectioned books" built on the canon's own §-structure (`&`/`$` markers,
independent of the catalog), one random plate per section, artless-section fraction
matched:

- **70% of boring control books score S1 ≤ the real book's S1; 79.7% cross the registered bar.**
- **99% score S3 ≤ the real S3; 99% cross the registered bar.**
- Median control p equals the observed p for both (both sit at the resolution floor).

Supporting observation: the motif-plate change pages (0, 3, 8, 15/16, 22/23, 27, 32/33,
40, 53) coincide with the canon's own section boundaries (0,3,8,15,16,23,27,33,40,51,54).

## 3. This lane's reading (for the oracle, not a certification)

S1/S3 measure the overt fact that Liber Primus illustrates by chapter — same plate run
within a section, plate changes at section boundaries. They fire on any such book. No
content-bearing residue: with sectioning granted, the per-section plate identities carry
~a handful of symbols, and every content read over them (counts as rune stream, counts as
cipher keys, orientations, type tokens) came back NEGATIVE or measured-only (see
`../RESULTS.md` §4–5).

## 4. Status

Lane STOPPED further sweeps over this space. Ledger row drafted with
`flagged-for-oracle` note (`../ledger_rows.json`); no `positive` status claimed.
Adjudicator: repo owner, via a GitHub issue titled `ORACLE: W2-C1 S1S3` labelled `oracle`
(this environment cannot open issues — ORACLE-PENDING per HUMAN-ORACLE §2).
