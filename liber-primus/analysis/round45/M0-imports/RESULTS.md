# Round 45 M0: import fold-in (FlareZ123 + Fable52)

_2026-11-23, lane M0 (closeout). Plan of record: [`../CAMPAIGN-PLAN.md`](../CAMPAIGN-PLAN.md).
Rows: [`ledger_rows.json`](ledger_rows.json), merged into `liber-primus/LEDGER.json` (351 → 365)._

## Sources

- **FlareZ123/liber-primus**, read-only clone at commit `65b9c444de106b2f0a77f42097728308596e4795`
  (2026-11-23). Treated as untrusted data: M0 read each study's header, method and result sections
  but ran none of its scripts. **Its rune corpus is derived from our `dataset/liber_primus.json`**
  (fable52 `reconcile.py`), so it is not an independent transcription. Agreement on ciphertext-side
  counts is not replication of the input.
- **Fable 5.2 fresh-eyes pass**, [`../../fable52/`](../../fable52/) (scripts + `OUTPUTS.txt`). Known
  defects: the per-page line from `t1_doublet_structure.py` is wrong (page counter not wired);
  `t8_wordlen_scope.py`'s control failed, so it is **uninformative** and gets no row. The scripts
  read word/line structure from the external clone's `lp2-transcription.txt` (path hard-coded in
  `fable52/load.py`). That file is rune-identical to our dataset.

## Local spot-check of the imported ciphertext-side numbers

`python -I verify_imports.py` → [`verify_output.txt`](verify_output.txt). Each number the imported
exclusions rest on on the ciphertext side matches: same-phase pair count M(840)=3277,
M(3301)=634; 2,896 printed words; 0 equal last-4 pairs among words ≥ 8 runes; 4 equal last-3 pairs
among words ≥ 7 runes; largest 3-gap sum 1,649 = 400+712+537, with the four sites (first rune,
0-based) at 2739/3139/3851/4388, and the longest single gap is 712. The English donor controls were
**not** re-run, so the imported exclusions are filed `measured` with their register conditional.
They are not filed as our own `negative`s.

## Rows

| id | status | effect |
|---|---|---|
| R45-IMPORT-WORDLEN-GRAMMAR | measured | Printed word-length order has no grammar (LP2 z=+0.4/+0.5 vs solved-LP z=+7.4 at 875 words). This is a premise flag on every row that reads printed words as plaintext words in order. Notes added to C-01, R10-L2-MAP, R37-C1-U3, R37-C3-U5-L2-MAP, R38-C2-G3, R40-C1-R04-M4-LP1-POINTER. |
| R45-IMPORT-D03-PHASEMAP-ALLPERIOD | measured | Bounded closure of D-03's periodic-map corner. Any deterministic per-phase map (many-to-one included) is excluded at q=1..3301 global, 1..1033 for chapter and 13-dot resets, 1..130 for page resets and 1..22 for line resets, against 5 native-English donors (Crowley, Blake). Homophonic emission (D-03's core) stays open. |
| R45-IMPORT-D04-PREDECESSOR-SBOX | measured | Narrows D-04. A previous-ciphertext-keyed secret table is excluded per chapter with 0–3 extra page rekeys, and so is the GP28 word-reset variant. Per-page private tables and schedules with ≥ 4 rekeys stay open. |
| R45-IMPORT-R12C1-PLAINHIST-M4-7 | measured | Key-independent bound on the plaintext-source corner of R12-C1 for memory 4–7 with one global table (384/384 controls violate). Memory 1–3 rests on a companion study that M0 did not import. The bound **requires the printed spaces to be real.** |
| R45-IMPORT-DOUBLET-MARKER-GATES | measured | Strengthens R44-W2B3-DOUBLET-CHANNEL: "doublet = fixed plaintext-rune marker" is excluded for all 29 runes and for periodic keys ≤ 256. The word-position parts inherit the spaces caveat. |
| R45-IMPORT-P0-RED13-AGREEMENT | measured | **Agreement** with R44-P1. The p0 red run is the same 13 GP indices (8+5), with the 13-dot block at x1405–1444 and the red word-dot at x1123–1133 (same pixels). Book-wide red totals (their 225 and 30 marks vs our 213 and 27+3) are **not** reconciled. |
| R45-IMPORT-T7-CONDITIONED-NULLS | measured | T7 survives chapter (p=5e-5), page (0.0046), page×13-dot (0.002), word/line class and exact word length (0.0077) conditioning. Their line-occupancy null (p=0.23) is **saturated** (Fable52: null 0.367±0.009 vs 0.380, power 0.04). The word-identity null (p=0.26) is of the same class and its power is unmeasured. **T7 stays live.** |
| R45-IMPORT-DOUBLET-ALLOGRAPH | measured | All 86 doublets are the same glyph on the JPEGs (Jaccard ≥ 0.90). This supports A-03 from the identity side. There was no planted-allograph control. |
| R45-IMPORT-PP49-51-P27-AGREEMENT | measured | Agreement on the pp49–51 table: 256/256 cells, cells 45/50/246 = 107/47/198. Also agreement that p27:93 = U. |
| R45-IMPORT-REJECTED-P50-LEADZERO | measured | **Reviewed and rejected as signal.** The p50 leading-zero doublet enrichment fails phase look-elsewhere under a clustering-preserving null (family p=0.54, Fable52 t2). |
| R45-FABLE52-D01-STREAM-FILTER | measured | The doublet rate is the same in-word, cross-word and across line breaks, lags 2–7 are at expectation, and the difference histogram is flat. This confirms D-01's stream-level single-lag filter. |
| R45-FABLE52-T7-DISTRIBUTED | measured | T7 is distributed rate heterogeneity: r1 ≈ 0.21 on each side of the large-gap run, the longest gap is ordinary (p=0.52), and rank r1 has p=0.003. It is not one void. |
| R45-FABLE52-T5-PT-MARKER | measured | Plaintext-coupled rare events in English reach r1 ≥ 0.38 in ≤ 0.8% of windows, so a plaintext marker is not favoured as T7's mechanism. |
| R45-FABLE52-T6-WORDCOLUMNAR | negative | Weak negative on a whole-book word-level columnar transposition (power ~1 on English at 2–56 columns, 0 at partial f ≤ 0.5). There is **low power against the solved-LP register** (lag-1 z = −1.17). |

## Declined / not imported

- **p50 leading-zero / doublet enrichment** (`lp2-p50-raw-tableau-allsecret-gate.md`,
  `lp2-doublet-gap-nonstationarity-ordering.md`): rejected as signal (row above). The same file's
  five stationary tableau-selector exclusions were outside M0's import list and were not imported.
- **"T7 is explained by printed-line occupancy / event-bearing word identity"** (FlareZ's own
  reading): not imported as an explanation. Both nulls condition on nearly the observed positions.
  The line null's power is 0.04.
- **Fable52 t8** (word-length scope): its control failed, so it is uninformative. No row. R45 W1 owns
  the fix.
- **FlareZ plain-history memory 1–3** (`lp2-plainprev-shortmemory-suffix-collision-gate.md`): only
  referenced, not read or imported.
