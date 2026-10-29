# B2 PREREG -- p27:93, LP1 transcription audit, GitHub issue #12 (Round 33)

Dated 2026-10-29, written before any LP1 or p27 measurement in this lane. Binding: `ARMADA-DOCTRINE.md`.
Operational note: the first action in the lane was a single read-only `git log` (a rule slip, no state touched); no git command is used after that.

## Part A -- issue #12 (data correction, no plaintext claim)
- Apply exactly two single-character edits to `data/krisyotam_runes.txt`: segment 8 first line gap 12 and segment 40 first line gap 8, `.` -> `-`. Segments split on `%`, lines on `/`, matching `analysis/round19/T2/t2lib.py:canon_lines()`.
- Precondition: our own Round 19 `out_separators.json` must list exactly `{gline 88, gap 12, canon '.', image '-'}` and `{gline 444, gap 8, canon '.', image '-'}` and the file's rune pair at each gap must match the issue (`ᛒ|ᛡ`, `ᚻ|ᚪ`). Any mismatch: STOP that edit and report.
- Before/after: `tests/validate.py`, `analysis/handoff/check_consistency.py`, `pytest tests/test_rig.py tests/test_validate_ledger_r3.py`. Pass criterion: byte-identical validator output, byte diff = exactly 2 characters, `%`, `/`, `$`, `&`, newline counts and rune sequence unchanged.
- The other "19 separator disagreements": report from T2 artefacts only if they fall out without new image work; apply none.
- JPEG SHA-256: check only files on disk under `data/` and the T1/T2 dirs; no downloads.

## Part B -- p27:93
- Render the glyph at the highest resolution on disk, context +-5 runes, the T1 margin. Do NOT overwrite canon. Resolve only if the evidence is unambiguous; otherwise record what a human must look at.

## Part C -- LP1 audit
- Reproduce T1's G-READ-LP1 (1,699/1,796 = 94.5991 %; pooled 1,879/1,976 = 95.0911 %) from committed code by re-running `analysis/round19/T1/g_read_lp1.py` logic. Q5 kill: if it does not reproduce to the digit, stop Part C and file it.
- Bucket misses by section/page/glyph into `lp1_misses.json`; list the 20 lowest-margin cells.
- Re-fit LP1_REAL and re-run the I2 `power.py` gate (L=120) only if any LP1 cell is changed. Changing a cell requires unambiguous evidence; a recall-bucket finding alone is not a cell change.
