# Issue #12 data correction -- two separator categories in `data/krisyotam_runes.txt`

Lane B2, Round 33, 2026-10-29. Only file changed outside this lane dir: `liber-primus/data/krisyotam_runes.txt` (2 bytes).

## Provenance line (for the commit / ledger)

> Separator corrections `. -> -` at segment 8 gap 12 and segment 40 gap 8 (indices count the decorative initial as rune 0, first physical line
> of each segment). Adjudicated by **RETSAM3301** (GitHub issue #12, opened 2026-10-10; research initiated and directed by RETSAM3301, with
> verification and technical assistance from OpenAI ChatGPT), cross-checked against relikd, Wulfic, the archived 2014 images and our Round-19
> T2 separator audit. Makes no plaintext claim.

## Diff

Segments split on `%`, lines on `/` (as `analysis/round19/T2/t2lib.py:canon_lines()`); line-local gap k = after k runes.

```
char 2609: ᚢᛉᛗᚳᚦᛈᚩᛒ.ᛡᚾᛏ-ᛠᛉ/  ->  ᚢᛉᛗᚳᚦᛈᚩᛒ-ᛡᚾᛏ-ᛠᛉ/
char 13337: ᚾᛗ-ᚣᚷᛞᚫᚻ.ᚪᛈᛉᚣᚻ-ᛇᛠ  ->  ᚾᛗ-ᚣᚷᛞᚫᚻ-ᚪᛈᛉᚣᚻ-ᛇᛠ
```
(seg 8 line 0 gap 12 = char 2609, `ᛒ|ᛡ`; seg 40 line 0 gap 8 = char 13337, `ᚻ|ᚪ`; offsets in the UTF-8 decoded text, CRLF preserved.)

Counts: `.` 183 -> 181, `-` 2,764 -> 2,766 over the whole file. Length 18,155 chars unchanged. Rune sequence, `%`, `/`, `$`, `&` and newline counts byte-identical (checked by script); all 13,136 rune identities and every word-break position unchanged.

## Verification against our own evidence (pre-edit gate -- both passed, so no STOP)

* Round 19 `T2/out_separators.json` lists exactly `{gline 88, seg 8, gap 12, canon ".", image "-"}` and `{gline 444, seg 40, gap 8, canon ".", image "-"}`. Gap 12/8 are interior (line has 17 and 19 runes), not line-boundary attribution.
* The file's rune pair at each gap is `ᛒ|ᛡ` (seg 8) and `ᚻ|ᚪ` (seg 40), the same as the issue.
* Independent eyeball in this lane on the on-disk page masters `data/relikd/p8.jpg`, `p40.jpg` (crops `gap_p8.png`, `gap_p40.png`): each gap holds a single small square dot, the same size as the neighbouring word-separator dots on the line; no lozenge. Agrees with T2's measured classes (`-` = one 9-10 px dot; `.` = a 24-60 px lozenge).
* Archived-JPEG SHA-256 (`8.jpg c679eb08...0922`, `40.jpg d9c4e3dc...2008`): NOT verifiable here. I hashed every image under `data/`, `analysis/round19/T1`, `analysis/round19/T2` (56 files); neither hash is on disk (the on-disk `data/relikd/p8.jpg`/`p40.jpg` are a different lineage/bytes), and I did not download from the neuroretransmit host. Status: pinned hashes unchecked; evidence rests on the on-disk relikd masters plus T2.
* Issue ZIP not downloaded; nothing from it executed. Its claims were not needed for the edit.

## Validators (before / after)

| check | before | after |
|---|---|---|
| `python tests/validate.py` | ALL VALIDATIONS PASSED, rc 0 | identical output (`_val_before.txt` vs `_val_after.txt`, diff empty), rc 0 |
| `python analysis/handoff/check_consistency.py` | "No document drift detected", rc 0 | identical output, rc 0 |
| `pytest tests/test_rig.py tests/test_validate_ledger_r3.py -q` | -- | 13 passed (after only; the file is not read by those tests except the offline-skipped crossdiff test) |

CI drift steps (`build_index/problem/knowledge/solved_pages` + `git diff --exit-code`) were NOT regenerated: they would rewrite committed files and I may not run git. Inspection: the only generated entry-point script that mentions the file is `build_knowledge.py:199`, a prose string, so its output cannot change; `SOLVED-PAGES.json` is built from the `lp.corpus` page labels (LP1 pages 01/05/06/03/14/73), not from this file. The CI steps that read the file (`run_stats`, `crypto_rigor`, `structure_analysis`, `crossdiff`) were not run (CI-only, fetch third-party sources). Coordinator: run them in CI.

## Does either gap move a segment boundary a solved-page control depends on?

No. Both edits are one-character `.`->`-` inside a line; no `%` (segment), `/` (line), `$`, `&` or newline moved. The rig's controls (`validate.py`: LP1 pages `Runes - 01`, `05`, `06`, `03`, `14`, `73`) do not use segments 8 or 40 (LP2 pages; T2's own control is segments 55/56). Effect limited to punctuation-sensitive statistics: any script counting `.` sees 181 not 183 (the issue's "175 -> 173 in the first 55 segments" is the same change).

## The roadmap's "19 separator disagreements" (S2 lane)

Cheap result, nothing applied:
* The 19 are Round 8's shortlisted lines (glines 75, 83, 93, 123, 127, 130, 133, 153, 158, 466, 475, 495, 515, 526, 536, 538, 545, 550, 554). Round 19 T2 §5.3 / `out_sep19.json` already read all 19: **all reproduce canon exactly, in count and position** (old diffs were line-alignment slips). Neither issue-12 target is in the 19. So the other 17 "disagreements" are already adjudicated as non-disagreements; there is nothing to correct.
* The whole-book T2 audit has 24 positionally-disagreeing lines (the 2 above + 22 others, 28 gap-level rows). Listed for the record, not applied (evidence status: automated image read only; 15 are gap-0 line-boundary attribution, 7 are at the line end; the rest are 2 adjacent-swap pairs on gline 95 and 1 on 579). Full rows: `separator_other_candidates.json`.

| gline | seg | gap | line runes | canon | image | class |
|---|---|---|---|---|---|---|
| 61 | 5 | 0 | 22 | -none- | - | line-boundary (gap 0) |
| 87 | 7 | 0 | 14 | -none- | . | line-boundary (gap 0) |
| 92 | 8 | 0 | 22 | -none- | . | line-boundary (gap 0) |
| 95 | 8 | 0 | 23 | -none- | - | line-boundary (gap 0) |
| 95 | 8 | 2 | 23 | - | -none- | interior |
| 95 | 8 | 13 | 23 | -none- | - | interior |
| 95 | 8 | 14 | 23 | - | -none- | interior |
| 116 | 10 | 0 | 22 | -none- | . | line-boundary (gap 0) |
| 135 | 11 | 0 | 23 | -none- | - | line-boundary (gap 0) |
| 140 | 12 | 0 | 20 | -none- | . | line-boundary (gap 0) |
| 164 | 14 | 0 | 20 | -none- | . | line-boundary (gap 0) |
| 167 | 15 | 0 | 9 | -none- | . | line-boundary (gap 0) |
| 228 | 20 | 23 | 23 | . | - | line-end (<=2 from end) |
| 229 | 20 | 0 | 22 | -none- | . | line-boundary (gap 0) |
| 271 | 24 | 23 | 23 | - | -- | line-end (<=2 from end) |
| 283 | 25 | 21 | 21 | -none- | - | line-end (<=2 from end) |
| 295 | 26 | 19 | 19 | -none- | - | line-end (<=2 from end) |
| 404 | 36 | 0 | 21 | - | -none- | line-boundary (gap 0) |
| 410 | 37 | 0 | 20 | - | -none- | line-boundary (gap 0) |
| 413 | 37 | 24 | 24 | . | -none- | line-end (<=2 from end) |
| 414 | 37 | 0 | 22 | - | -none- | line-boundary (gap 0) |
| 419 | 37 | 0 | 20 | - | -none- | line-boundary (gap 0) |
| 424 | 38 | 0 | 21 | - | -none- | line-boundary (gap 0) |
| 430 | 38 | 0 | 22 | -none- | . | line-boundary (gap 0) |
| 579 | 53 | 0 | 19 | -none- | - | line-boundary (gap 0) |
| 579 | 53 | 1 | 19 | - | -none- | interior |

Only gline 228 (`.` vs image `-`, at the line end) is a `.`-vs-`-` category question like the two corrected here; it sits at a line boundary where T2 itself says attribution is unreliable. `not_covered`: human image adjudication of these rows.
