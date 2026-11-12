# Round 44 / WAVE-2 CELL C2 — ALL-PAIRS PAGE XOR / PAGE-AS-KEY-FOR-PAGE — RESULTS

_Run 2026-11-09. PREREG.md hash-stamped into run.log (sha256 2d980e5d…85d5d5b) before first
execution. Thresholds fixed in advance from the committed bars_v3 fit. No LEDGER.json edits._

## Verdict

**NEGATIVE, both lanes. Zero bar-crossers, zero near-misses.** The never-run
`not_covered` clause of R40-C1-R47-F01-LP2-AS-PAD ("all-pairs page XOR and canon-as-key
parts of the reading") is now measured ground under panel-R36 + bars_v3.

| lane | cells (verdict family) | best non-degenerate pmax | fixed bar | margin |
|---|---:|---:|---:|---:|
| pairs (55×54 directed, page_i as key over page_j) | 1,927,476 (+146,772 short-skipped) | **5.925** (key=44→ct=52, rev, add, s=28, o=13, L=179) | 16.7816 (L<240) / 22.6382 (L≥240) | −10.86 z |
| canon-as-key (13,136-rune canon over each page, all offsets) | 6,155,874 (+230,337 self-overlap, reported separately) | **6.141** (ct=20, add, s=28, o=1570, L=269) | 22.6382 (L≥240) | −16.50 z |

- Degenerate rows in the top-100: 0 (pairs), 0 (canon verdict family). The self-overlap
  family's top row (13.31, ct=29, sub, s=0, key window over its own canon interval) is
  **degenerate** — the expected self-key constant diagonal, matching F-01's T6 self-key note.
- **The p27/p54 7-gram pairs, run first and reported individually** (R44-R1-SEVENGRAM
  context): best cell key=27→ct=54 is 4.16 (add, rev, s=0, o=9); best key=54→ct=27 is 3.81
  (negadd, rev, s=1, o=14). Nothing above noise: the unique repeated 7-gram is **not**
  explained by either page keying the other under the F-01 variant closure at any swept
  alignment.

## Positive control (plants, through the identical runner, before any real target)

3/3 passed, each recovered at EXACTLY its planted coordinates as the argmax of its ct page's
cells, non-degenerate, over bar, with the best non-neighbour cell at ~5.0–5.2 (far below bar):

| plant | construction | pmax | bar |
|---|---|---:|---:|
| A | EN_KJV 200, sub, key page 13 **fwd at line-start o=45**, s=0 | 24.65 | 16.78 |
| B | LATIN 150, add, key page 40 **reversed**, o=17, **s=1** | 19.69 | 16.78 |
| C | EN_KJV 180, sub, **canon stream o=7001**, s=0 | 26.38 | 16.78 |

`plant_pair.json`, `plant_canon.json`. Both real runners gate on these files.

## Numbers vs bar

Bars (fixed in PREREG §4 before any run): `bar_v3(16e6, L, "free")` = 16.7816 (120-node,
cells L<240) / 22.6382 (240-node, L≥240); actual total N = 8,083,350 verdict cells
(+230,337 self-overlap + 187,801 plant cells) ≤ N_bar = 16e6, so the bars are conservative.
Sanity checkpoints (PREREG Q5 iii) passed in both lanes (top-100 medians 4.17 / 4.44).
Doctrine-R3 language-agnostic stats (ioc·N, mds, h2, zl) persisted for all full-adjudicated
rows (top-100 per lane + the self-overlap top-20): `pair_results.json`, `canon_results.json`.

## Coverage

- **Pair lane**: unsolved pages 0..54, all 2,970 directed pairs; key direction {fwd, rev};
  sign patterns {sub, add, negadd} × shifts {0, +1, +28} — by the order-swap/shift closure
  (PREREG Q3) this spans the full F-01 variant set {fwd, rev, atbash, neg} × {vigenère,
  beaufort, add}, including ct-side line-start alignments; offsets {0..29} ∪ key-page line
  starts >29; window L = min(len_j, len_i − o), cells L<60 skipped (146,772, counted).
- **Canon lane**: full canon (13,136 runes, fwd) over each unsolved page at **every** offset
  0..13136−len_j, same 9 relation×shift cells; self-overlap cells computed and reported
  separately (0 non-degenerate crossers there either).

## not_covered

Reversed/atbash **canon-stream** lane (the pair lane covers rev keys, the canon lane is fwd
only); shifts outside {0,1,28} (a full Caesar layer on top of the pair relation); key-stream
interrupter / null-F / skip models (exact position-wise group operation only — no beam);
autokey and multi-page composite keys; solved pages (55,56) as keys in the pair lane (present
inside the canon stream, so their fwd segments ARE covered at canon offsets); ct windows other
than page start beyond what the order-swap closure implies; languages/orthographies outside
the 12-register panel; cells with usable window <60 runes.

## three_conditionals

1. **key_space** — as in Coverage above (pages-as-keys F-01-closure + fwd canon-as-key, all
   offsets listed there).
2. **transition_model** — exact position-wise mod-29 group decode (no skips, no interrupters,
   no beam, no autokey).
3. **adjudicator_register** — panel-R36 (12 registers), pmax vs bars_v3 free bars at
   N_bar=16e6; 120-node bar applied to cells L∈[60,240) (slightly lenient for L<120 — can
   only over-flag, never under-report; zero flags occurred).

## Files

`PREREG.md` (hash-stamped), `c2lib.py`, `plant_run.py`, `run_pairs.py`, `run_canon.py`,
`plant_pair.json`, `plant_canon.json`, `pair_results.json`, `canon_results.json`,
`ledger_rows.json`, `run.log`. Reproduce: `python3 plant_run.py && python3 run_pairs.py &&
python3 run_canon.py` (pure python3+numpy, no network; ~2 min total).

## Reopens if

A construction with interrupters/skips over a page-pair key is specified with a validated
skip-tolerant instrument (the pf_v4 / beam_v3 lineage applied to page-keys); or a register
outside panel-R36 is added with a measured power envelope; or the reversed/atbash canon lane
or the full shift layer is argued above flat prior.
