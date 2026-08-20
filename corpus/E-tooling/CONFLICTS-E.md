# CONFLICTS-E — transcription divergences found in vendored third-party tooling

Method. Our canonical transcription is `liber-primus/data/krisyotam_runes.txt`:
**13,136 runes in 57 `%`-delimited segments**, SHA-256 of the comma-joined
Gematria-Primus indices = `74cebdb074898f4c2742733a421e6d1717068a4f4cf2802d2b50923285aad329`.
(The `023312066df4…` hash pinned in `PROBLEM.json` is a *different, smaller* object —
the 12,956-rune **unsolved** subset. Do not compare the two.)

Third-party transcriptions almost always ship the **whole** Liber Primus
(~15,857–15,938 runes: LP1 solved pages plus LP2), so a raw count or whole-file
hash mismatch against our 13,136 is expected and carries no information. The test
that does carry information is per-segment:

> does each of our 57 canonical segments appear **verbatim, contiguous**, inside the
> other file's rune stream?

Tooling: `diff_transcriptions.py` (bulk test) and `locate_divergence.py`
(binary-search the longest matching prefix, then print the exact rune where the two
part company). Full machine output: `transcription_diff.json`.

---

## Headline

**No divergence was found in the rtkd → mainstream lineage.** Every file that
descends from `rtkd/idkfa` / `iddqd` / Taiiwo reproduces all 57 of our segments
rune-for-rune. One independent lineage (a 15,938-rune file) carries **two
single-rune substitutions**, one of which is demonstrably an error on *their* side.

| Vendored file | n runes | 57 canon segments verbatim? |
|---|---:|---|
| `rtkd__idkfa/data/liber` | 15,857 | **57 / 57** |
| `Taiiwo__TaiiwoBot/lib/cicada/cicada/liber_primus.txt` | 15,933 | **57 / 57** |
| `cicada-solvers__lp-decrypter/lp_data/liber-primus__transcription--master.txt` | 15,933 | **57 / 57** |
| `ctvrty-rozmer__bruh/cicada-master/cicada/liber_primus.txt` | 15,933 | **57 / 57** |
| `r4nd0mD3v3l0p3r__LiberPrimusSolver/data/unsolved.txt` | **13,136** | **57 / 57 — and byte-for-byte identical index hash `74cebdb0…`** |
| `Skyro7777777__LiberPrimusDecoded/…/raw/primary/primary_how_solved.*` | 16,009 | 57 / 57 |
| `Skyro7777777__LiberPrimusDecoded/…/raw/wiki_how_solved.*` | 16,005 | 57 / 57 |
| `jens-wedin__liber-primus/data/liber_primus.md` | 15,938 | **55 / 57 — segments 24 and 56 diverge** |
| `Skyro7777777__LiberPrimusDecoded/…/raw/liber_primus.txt` and `…/raw/liber_primus_raw.json` | 15,938 | **55 / 57 — same two segments** |

The three 15,938-rune files share **one identical rune-index SHA-256**
(`67a41c67b6a8e867…`) despite different file wrappers (`.md`, `.txt`, `.json`) and
different owners — so this is **one lineage sampled twice**, not two independent
disagreements. Treat it as a single conflicting witness.

---

## C-E-01 — segment 24, rune 172: `ᚫ` (AE, 25) in ours vs `ᚪ` (A, 24) in the 15,938 lineage

*This one is in unsolved ciphertext, so it is the one that could matter.*

```
canon ctx:  …ᚣᛟᚹᛞᚠᚣᛄᛁᛏᛉᛚᚩᚦᛝᚠᚪᛋᛡᛁᚻᛒᚱᚪᚢᚣ >>ᚫ<< ᚢᛟᛠᚪᚣᛖᛟᚫᛖᛈᚠᛒᛈᛄᛁᛋᛝᛒᚱᚦᚳᛇᛚᛁᚢ…
file  ctx:  …ᚣᛟᚹᛞᚠᚣᛄᛁᛏᛉᛚᚩᚦᛝᚠᚪᛋᛡᛁᚻᛒᚱᚪᚢᚣ >>ᚪ<< ᚢᛟᛠᚪᚣᛖᛟᚫᛖᛈᚠᛒᛈᛄᛁᛋᛝᛒᚱᚦᚳᛇᛚᛁᚢ…
```

- Longest matching prefix 172/270; the following 40 runes re-align at **delta 0**, so it
  is a clean **substitution**, not an insertion or deletion. Exactly one rune differs.
- `ᚪ` (A, index 24) and `ᚫ` (AE, index 25) are **adjacent** in Gematria Primus and are
  the classic confusable pair in this alphabet (`ᚪ` vs `ᚫ` differ by one small stroke).
  A single-rune index-24/25 swap is the exact signature of an OCR or hand-transcription
  slip, not of a different underlying source image.
- **Severity: low-to-moderate, and it does not move our verdict.** One rune out of
  12,956 changes no aggregate statistic reported by this project (doublet count, IoC,
  entropy). It would matter only to a crib or a positional argument that lands on that
  rune. It is logged here so a future solver who lands on segment 24 knows two readings
  exist.
- **Not resolved from pixels.** Neither side of this conflict was checked against the
  original scan in this lane. That is the correct next step and it is recorded in
  `GAPS-E.md`.

## C-E-02 — segment 56, rune 80: `ᚣ` (Y) in ours vs `ᛖ` (E) in the 15,938 lineage

*This one is decidable from the text alone, and we are right.*

```
canon:  …ᚱᚳᚢᛗᚠᛖᚱᛖᚾᚳᛖᛋᚠᛁᚾᛞᚦᛖᛞᛁᚢᛁᚾᛁᛏ >>ᚣ<< ᚹᛁᚦᛁᚾᚪᚾᛞᛖᛗᛖᚱᚷᛖ
file:   …ᚱᚳᚢᛗᚠᛖᚱᛖᚾᚳᛖᛋᚠᛁᚾᛞᚦᛖᛞᛁᚢᛁᚾᛁᛏ >>ᛖ<< ᚹᛁᚦᛁᚾᚪᚾᛞᛖᛗᛖᚱᚷᛖ
```

Transliterated, ours reads `…RCUMFERENCES FIND THE DIVINIT-Y- WITHIN AND EMERGE`; theirs
reads `…DIVINIT-E- WITHIN`. This segment is **plaintext** (a solved page carried in runes),
so the correct reading is fixed by English: **`ᚣ`/Y is right and the 15,938 lineage has a
typo.** Again a clean substitution, tail re-aligns at delta 0.

This second error is what downgrades the first: the same file already contains one
provable transcription mistake, which is evidence that C-E-01 is also that file's mistake
rather than ours.

---

## Non-conflicts (recorded so nobody re-raises them)

- `Skyro7777777__LiberPrimusDecoded/…/decoder/all_pages.json` (21,272) and
  `unsolved_pages.json` (16,378) miss 4–5 segments, and `translit_pages_*` (12,878) misses
  segment 0. These are **derived/re-chunked artefacts of that repo's own pipeline**
  (duplicated pages, re-paginated boundaries), not independent transcriptions — the same
  repo's `raw/` files reproduce 57/57. Not a conflict with the source.
- `cicada-solvers__lp-decrypter/lp_data/lp_section_data.py` (25,948) misses 56 segments:
  it is a Python source that stores each section as a separate string literal
  interleaved with translations, so contiguity is broken by construction. Its sibling
  `liber-primus__transcription--master.txt` is 57/57.
- Anything under 5,000 runes was not segment-tested; those are alphabet tables, single
  pages, key lists and README samples.
