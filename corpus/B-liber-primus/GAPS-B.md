# GAPS-B — what Lane B could not establish

Branch `corpus-sweep`, 2026-08-19. Companion to `REPORT-B.md` and `CONFLICTS-B.md`.
Everything here is an honest hole, not a to-do list dressed up as one.

| id | gap | severity | why it matters |
|---|---|---|---|
| G-01 | No transcription independent of the 2015 resvolver lineage exists | **high** | the corpus has one witness, not many |
| G-02 | No text layer anywhere in the published artifacts | medium | every rune came from a human eye |
| G-03 | LP2 page 50 is runeless and its content is undecoded | medium | 1 of 58 pages is not in the stream at all |
| G-04 | `tests/validate.py` asserts only a prefix of AN END | medium | the trust anchor is weaker than it reads |
| G-05 | Only 3 of 13,136 runes have been image-verified | medium | no systematic OCR audit exists |
| G-06 | GitHub code search does not see every repo | medium | the hunt is provably incomplete |
| G-07 | Software Heritage / GitLab / Bitbucket / Codeberg not swept | medium | deleted repos are exactly where a 2014 transcription would be |
| G-08 | resvolver's own source for the 2015 transcription is unknown | medium | the chain stops at a person, not an artifact |
| G-09 | The `scream314` LP1 error is still live in repo data | low–medium | wrong runes in `SOLVED-PAGES.json` |

---

## G-01 — the corpus has ONE witness (high)

This is the most important gap Lane B found, and it is worse than it looked at the start.

Every transcription checked resolves to a single 2015 lineage:

```
resvolver/c1cada  transcriptions.rne     2015-01-16  13,053 runes   draft
resvolver/c1cada  transcriptions.rne     2015-01-23  13,072 runes   draft, "fixed error"
resvolver/c1cada  translation/…rne       2015-01-23  13,136 runes   == CANON
Be5haram/CICADA2K16 RuneSolver.py        2016-01-14  canon embedded contiguously
henkman/liberprimus                      2016-08-14  = the 13,072 draft, 1 rune changed
rtkd/iddqd                               2017-01-04  the assumed "root" — two years downstream
dude123124144/…-OCR                      2017-03     13,136, ZERO divergences from canon
krisyotam / relikd / rtkd_master         later       rune-identical to each other and to canon
```

Perfect agreement over 13,136 glyphs across "independent" sources is not corroboration —
it is the fingerprint of copying. **We do not have several transcriptions that agree. We
have one transcription, copied.**

What that costs: the standard argument "N independent readers all read `ᛒ` here" is not
available anywhere in this corpus. Every statistic computed on the 12,956-rune unsolved
index inherits the error profile of one 2015 reader. The index is almost certainly right —
C-04a–d show that reader's known errors were caught and corrected, and three of the
corrections check out against the images — but *almost certainly* is the honest word.

**How to close it:** a genuinely independent re-transcription from the images. Nothing
else will do. That is a bounded task (13,136 glyphs, 56 clean 400-DPI renders, machine-set
type) and it is the single highest-value piece of unglamorous work available on this
project.

## G-02 — no text layer (medium)

Searched and not found:

- archive.org item `liber-primus` is a **9,086,651-byte ZIP of images**. No text layer.
- No PDF, EPUB or SVG release of the Liber Primus with selectable runes was located.
- The onion7 originals are raster (`.jpg`), not vector.

So there is no machine-readable primary source to diff a transcription against. Every rune
in existence was typed by a person looking at a picture. This is the root cause of G-01.

## G-03 — LP2 page 50 (medium)

p50.jpg carries **no runic text at all**: a 13×8 grid of two-character tokens. It is
excluded from the rune stream, which is why segment indices and page numbers diverge above
49 (C-01). Lane B did not attempt to interpret the grid. Whether it is a key, a cipher in
its own right, or decoration is **open**, and it is one of only two pages in the book
(with the runeless art pages) that the whole rig structurally cannot see.

## G-04 — the trust anchor asserts a prefix (medium)

See `CONFLICTS-B.md` C-05. `liber-primus/tests/validate.py` checks a prefix of the AN END
plaintext. A complete decode requires one F-null interrupter; the gate stops before the
point where its absence would show. The gate is not *wrong*, but per `CLAUDE.md`
("`validate.py` is the whole basis for trusting any negative result in this repo") a gate
that cannot see a truncated tail is a real weakness. `analysis/reproduce/` asserts the
full plaintext on all seven pages instead.

## G-05 — 3 runes image-verified out of 13,136 (medium)

`ADJUDICATION-pages33-35-images.md` settles exactly the positions that were disputed. It
is a reading check, not an audit. **No systematic image-vs-transcription verification of
the corpus exists** — not in this repo and, as far as the hunt could tell, not anywhere
public. Combined with G-01 this is the corpus's real exposure.

`make_crops.py` shows the method works and is cheap: line bands from the row ink profile,
glyph columns from the column ink profile, cross-checked against `PAGES.json` line breaks
(the script asserts the image line count equals the transcription line count and fails
loudly otherwise). Scaling it to all 56 pages is straightforward.

## G-06 — the hunt is provably incomplete (medium)

GitHub code search across seven distinct rune substrings returned 109 file hits in 31
repos. **`henkman/liberprimus` was not among them** — despite being a whole-book
transcription that Lane B had already fetched by name. GitHub's code index is not
exhaustive (indexing lag, repo size and popularity thresholds, forks excluded).

So: the two new pre-2017 finds (`resvolver/c1cada`, `Be5haram/CICADA2K16`) came out of
code search, but the absence of further hits is **not** evidence of absence. A
name/description sweep and a code sweep find different things and neither is complete.

## G-07 — non-GitHub forges and deleted repos not swept (medium)

Not attempted, and each is a plausible home for something older than 2015-01:

- **Software Heritage** — archives deleted repositories. The 2014 Liber Primus release is
  eleven years old; the most likely early transcriptions are in repos that no longer exist.
  This is the highest-value unswept source.
- GitLab, Bitbucket, Codeberg, SourceForge.
- Gists (GitHub code search does not cover them).
- Non-English communities: Russian, German, Chinese and Japanese Cicada forums were active
  in 2013–2014 and are not represented in anything Lane B fetched.
- The IRC logs and forum archives in `corpus/C-community/` were not mined for pasted rune
  blocks, which is where a 2014-era transcription would most naturally appear.

## G-08 — resvolver's source is unknown (medium)

`resvolver/c1cada` has no README explaining where its runes came from. The repo was created
2015-01-05, the first transcription committed 2015-01-16, corrected 2015-01-23. The Liber
Primus images were published in January 2014, so there is a **twelve-month window** in
which the transcription could have been made and circulated elsewhere first — forum post,
pastebin, IRC, a now-deleted repo. resvolver may be the transcriber or may be a
re-publisher. **The chain of custody stops at a person, not an artifact.**

## G-09 — a known-wrong rune is still live in repo data (low–medium)

The `scream314_lp.md` `ᚹᛋ`/`ᛠ` error (C-02) propagates into `SOLVED-PAGES.json` and
`liber-primus/tests/validate.py`. LP1 only; the unsolved stream is unaffected; nothing
downstream is invalidated. But it is a known error sitting in the repo's own data and it
has not been corrected. Lane B recorded it rather than editing shared data mid-sweep.

---

## What Lane B deliberately did NOT do

- **Did not edit `liber-primus/data/`, `SOLVED-PAGES.json` or `tests/validate.py`.**
  C-02 and C-05 are real defects in shared data and the trust anchor. Changing either
  mid-sweep would move the ground under every other lane. They are recorded, with the
  evidence, for the owner to action.
- **Did not resolve conflicts that ground truth could not settle.** The ten bulk-delete
  blocks in henkman are almost certainly dropped lines, but "almost certainly" is not a
  verdict and they are left recorded.
- **Did not extrapolate from three verified runes to the corpus.** See G-05.

---

## Addendum — Priority-4 hunt outcome (2026-08-19)

The renewed hunt (GitHub **code** search over seven rune substrings + Software Heritage
origin search) closed one gap and reshaped another.

**Closed:** the "pre-root transcription" question. Two pre-2017 witnesses were found —
`resvolver/c1cada` (2015-01-05, canon exactly, 2015-01-23) and `Be5haram/CICADA2K16`
(2016-01-14, canon embedded contiguously). See `REPORT-B.md` §3.

**Reshaped:** finding them made G-01 *worse*, not better. Both witnesses carry the same
reading; the second is a copy of the first. Going back two more years produced no
independent eye.

**Checked and discarded:**

| candidate | why not |
|---|---|
| `latin-ocr/liberprimus00danagoog`, `…01danagoog` (2016-04-25) | Google Books OCR of an unrelated **Latin** book titled *Liber Primus*. Not Cicada. |
| `aautcsh/liberprimus` (2019), `krypt0x/liberprimus` (2021) | forks of `henkman/liberprimus` |
| `cicada-solvers/LiberPrimusSolver`, `tony-michaelson/LiberPrimusSolver` | forks of `r4nd0mD3v3l0p3r/LiberPrimusSolver` (2019) |
| `sradley/LiberPrimus` | deleted from GitHub; Software Heritage holds only a **partial 2020 visit with no snapshot** — content unrecoverable, and 2020 is post-root anyway |
| `LiberPrimus/*` org, `ing4lipt`, `RabbitTone`, `1van-marx` | all 2018 or later |

**Still unswept** (G-07 stands): gists, GitLab, Bitbucket, Codeberg, SourceForge,
non-English forums, and the IRC/forum archives already sitting in `corpus/C-community/` —
which, given that a transcription existed by January 2015, is now the *most* likely place
for anything earlier to be hiding. A 2014 paste in a forum thread would predate every
repository found here.

Method caveat worth carrying forward (G-06): **`henkman/liberprimus` did not appear in any
of the seven code searches**, despite being a whole-book transcription already fetched by
name. GitHub's code index is not exhaustive. Absence of hits is not absence of repos.
