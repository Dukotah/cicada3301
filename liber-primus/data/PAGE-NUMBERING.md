# LP2 segment index vs book page number

**Short version:** from 50 onward, the segment index in `krisyotam_runes.txt` is the
book page number minus one. Book page 50 has no segment.

| segment index (this repo) | book page (2014 `N.jpg`) | content |
|---|---|---|
| 0–49 | 0–49 | unsolved runes |
| — | **50** | the 13×8 base-60 token table, **no runes** |
| 50–54 | **51–55** | unsolved runes |
| 55 | 56 | AN END (solved, φ(prime) shift) |
| 56 | 57 | PARABLE (solved, direct transliteration) |

## Why

The master transcription (rtkd/iddqd lineage) segments LP2 by book page, with 58 slots.
Slot 50 holds the page-50 token table and zero runes. The runes-only extraction that
produced `krisyotam_runes.txt` filtered to runes, so slot 50 became empty, was dropped,
and every later segment renumbered down by one.

## Consequences

- "LP2 pages 0–54" in older docs here means **segments** 0–54. The 55 unsolved rune
  pages are book pages 0–49 and 51–55.
- "Page 55 was never transcribed" is false. Book page 55 is segment 54.
- When a doc here says "canon p55" it means segment 55, which is book page 56 (AN END).
- No content-based result changes. Only page *names* at 50 and above do. Older round
  docs are left as written, as historical record. Read their page labels ≥ 50 through
  this table.

## Credit and evidence

- [njloof](https://github.com/njloof), [issue #14](https://github.com/Dukotah/cicada3301/issues/14),
  found the root cause and proved it from three sources: the page-50 image, a from-scratch
  human read of book page 51 (92/92 runes match segment 50), and the master transcription's
  58-slot layout. Full evidence pack:
  [STREAM_TAIL_EVIDENCE.md](https://github.com/njloof/cicada-lp2-sweeps/blob/main/docs/STREAM_TAIL_EVIDENCE.md).
- [RETSAM3301](https://github.com/RETSAM3301), [issue #12](https://github.com/Dukotah/cicada3301/issues/12),
  recorded the same image mapping on 2026-10-10.
- Also noted in #14: `analysis/transcription/crossdiff.py` `load_relikd()` concatenates
  relikd's page-named chunk files flat, which throws away the one correct page map in
  the lineage. Not changed yet; anything that needs page labels should use this table.
