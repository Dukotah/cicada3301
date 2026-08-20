# CONFLICTS-E — transcription divergences found in vendored third-party tooling

## What is being compared, and to what

Our canonical transcription is `liber-primus/data/krisyotam_runes.txt`:
**13,136 runes in 57 `%`-delimited segments**. SHA-256 of the comma-joined
Gematria-Primus indices (0..28) = `74cebdb074898f4c2742733a421e6d1717068a4f4cf2802d2b50923285aad329`.

> **Two different hashes, two different objects — do not confuse them.**
> `liber-primus/PROBLEM.json` pins `023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585`.
> That is the SHA-256 of the comma-joined indices of the **12,956-rune UNSOLVED
> subset** (canon segments 0–54, i.e. LP2 pages 0–54). `74cebdb0…` is the SHA-256 of
> the comma-joined indices of the **full 13,136-rune canonical file** (all 57
> segments: pages 0–54 plus the two trailing pages). Verified here: segments 0..54
> sum to exactly 12,956 runes. Neither hash is wrong; they cover different objects.
> Everything in this file is diffed against the **13,136 / `74cebdb0…`** object.

Third-party transcriptions usually ship the **whole** Liber Primus (~15,857–15,938
runes: LP1's solved pages plus LP2), so a raw count or whole-file hash mismatch
against 13,136 is expected and carries no information. The test that carries
information is per-segment:

> does each of our 57 canonical segments appear **verbatim and contiguous**
> inside the other file's rune stream — and if not, is the difference an
> **OMISSION** (that page simply is not in their file) or a **CONTRADICTION**
> (a different rune at the same aligned position)?

Tooling in this directory: `diff_transcriptions.py` (segment-presence test) →
`transcription_diff.json`; `classify_divergence.py` (anchors each missing segment by
its longest common run, then runs `difflib.SequenceMatcher` over the aligned window
and labels every opcode) → `divergence_classified.json`; `locate_divergence.py`
(single-case drill-down).

### Methodological correction that had to be made first — a codepoint alias

Some transcriptions encode Gematria Primus index 11 (**J**, normally
**U+16C4 `ᛄ`** RUNIC LETTER GER) as **U+16C2 `ᛂ`** (RUNIC LETTER E). Census over
all rune-bearing vendored files:

| codepoint | glyph | occurrences | repos |
|---|---|---:|---|
| U+16C2 | `ᛂ` | 1,229 | `cicada-solvers/lp-decrypter`, `Skyro7777777/LiberPrimusDecoded`, `resvolver/c1cada` |
| U+16EB | `᛫` | 301 | `crackalamoo/futhorc` (word separator, not a letter) |
| U+16E5 `ᛥ` / U+16E2 `ᛢ` | | 47 / 12 | `crackalamoo/futhorc` (full 33-rune futhorc, not LP) |

`cicada-solvers/lp-decrypter`'s `lp_data/lp_section_data.py` contains **933 `ᛂ` and
zero `ᛄ`** — a 28-symbol stream where every other transcription has 29.
This is an **ENCODING variant, not a reading difference**: with `ᛂ → 11` applied,
that file reproduces all 57 canon segments.

**But it is a real hazard for anyone reusing that file.** A tool that reads it with
a plain 29-rune map silently *drops* every J, shifting every subsequent index by one
and desynchronising any keystream. Before the alias was applied, this lane's own
classifier reported 55 spurious INDELs and 11 spurious CONTRADICTIONs from that one
file. All extractors here now map `ᛂ → 11`.

---

## Headline 1 — our 13,136-rune transcription is attested in **January 2015**

`resvolver/c1cada` (`https://github.com/resvolver/c1cada`, first commit 2015-01-05)
carries a full LP2 rune transcription split across eleven files,
`perl/page.{0-2,3-7,8-14,15-22,23-26,27-32,33-39,40-53,54-55,56,57}.txt`.
Concatenated in page order:

**13,136 runes, index SHA-256
`74cebdb074898f4c2742733a421e6d1717068a4f4cf2802d2b50923285aad329` — bit-for-bit
identical to `liber-primus/data/krisyotam_runes.txt`. All 57 canon segments present
verbatim, zero divergences.**

Walked commit by commit (`git --git-dir=vendor/resvolver__c1cada/.git`):

| commit | date (author tz) | message / author | n runes | index SHA-256 |
|---|---|---|---:|---|
| `f75c1de0235034d2ec8920351f1d396c3e140a0c` | 2015-01-20T22:36:59+01:00 | "Some perl to work out frequencies" (root) | 13,377 | `ec3d102ac6d4e03aa2d10ab15565b043f89f49a66faaed4345a909b7ba1d7d36` |
| `61c1dbb5` | 2015-01-20T22:43:06+01:00 | "Tidy code not in use" (WetSand) | 13,377 | `ec3d102a…` |
| `2bd22d12` | 2015-01-20T22:47:23+01:00 | "x" (WetSand) | 13,377 | `ec3d102a…` |
| `62b2e189` | 2015-01-21T00:32:45+01:00 | "random added" (WetSand) | 13,377 | `ec3d102a…` |
| **`fe9b2255`** | **2015-01-21T16:34:18+01:00** | **"error" (WetSand)** | **13,136** | **`74cebdb0…`** |
| `a990e0bc` | 2015-01-21T16:34:35+01:00 | "error fixed" (WetSand) | 13,136 | `74cebdb0…` |

The 2015-01-20 first draft had a garbled `page.27-32.txt` (1,674 runes where the
corrected file has 1,433); the two 2015-01-21 commits fixed it, and from `fe9b2255`
onward the eleven files have been our exact stream. **No `perl/page.*.txt` has been
modified since 2015-01-21** (repo HEAD is 2016-01-15).

Why this matters. `rtkd/iddqd`'s `liber-primus__transcription--master.txt` — the file
the community treats as the root — was first committed **2017-03-01** (`218ed88`).
The resvolver witness precedes it by **25.5 months** and agrees with us exactly. Our
canon therefore does not sit downstream of iddqd; the same 13,136 runes were on
GitHub within days of the Liber Primus becoming public.

Caveat, stated plainly: an exact match does not prove two *independent* readings —
both could descend from one community transcription posted in January 2015. What it
does establish is that the 13,136-rune stream is the long-standing reading and not an
artefact of the 2017-era tooling.

---

## Headline 2 — exactly one lineage disagrees, and it is one witness sampled four times

| Vendored file | n runes | index SHA-256 | 57 canon segments verbatim? |
|---|---:|---|---|
| `resvolver__c1cada/perl/page.*.txt` (2015) | **13,136** | `74cebdb0…` | **57/57 — identical to canon** |
| `r4nd0mD3v3l0p3r__LiberPrimusSolver/data/unsolved.txt` | **13,136** | `74cebdb0…` | **57/57 — identical to canon** |
| `iddqd_versions/master_218ed88.txt` (2017-03-01) | 15,935 | — | 57/57 |
| `iddqd_versions/master_ed95eb7.txt` (2017-05-21) | 15,933 | — | 57/57 |
| `iddqd_versions/master_3089b65.txt` (2019-06-17) | 15,933 | — | 57/57 |
| `rtkd__idkfa/data/liber` | 15,857 | — | 57/57 |
| `Taiiwo__TaiiwoBot/lib/cicada/cicada/liber_primus.txt` | 15,933 | — | 57/57 |
| `cicada-solvers__lp-decrypter/lp_data/liber-primus__transcription--master.txt` | 15,933 | — | 57/57 |
| `cicada-solvers__lp-decrypter/lp_data/lp_section_data.py` | 25,948 | — | 57/57 *(after `ᛂ→11`)* |
| `ctvrty-rozmer__bruh/cicada-master/cicada/liber_primus.txt` | 15,933 | — | 57/57 |
| `Skyro7777777__LiberPrimusDecoded/…/raw/primary/primary_how_solved.*` | 16,009 | — | 57/57 |
| `Skyro7777777__LiberPrimusDecoded/…/raw/wiki_how_solved.*` | 16,005 | — | 57/57 |
| **`scream314__cicada3301/liber_primus.md`** | **15,938** | **`67a41c67b6a8e8678944d26e9c6af547ef0a07a21eb47e3fd483790ba48e81d7`** | **55/57 — segments 24 and 56 CONTRADICT** |
| `jens-wedin__liber-primus/data/liber_primus.md` | 15,938 | `67a41c67…` (same file) | 55/57 — same two |
| `Skyro7777777__LiberPrimusDecoded/…/raw/liber_primus.txt`, `…/raw/liber_primus_raw.json` | 15,938 | `67a41c67…` (same file) | 55/57 — same two |
| `liber-primus/data/scream314_lp.md` *(already inside this repo)* | 15,938 | `67a41c67…` (same file) | 55/57 — same two |

All four 15,938-rune files carry **one identical rune-index SHA-256**, and
`jens-wedin/liber-primus`'s README states outright that its copy is vendored from
`scream314/cicada3301`. So this is **one witness, `scream314/cicada3301`, counted
once** — not four independent disagreements.

Score on the two contested runes: **canon + resvolver (2015) + all four iddqd
revisions + idkfa + Taiiwo + lp-decrypter ⟶ three or more lineages against
scream314's one.**

---

## C-E-01 — canon segment 24, rune 172 (global rune index 5,891): `ᚫ` (AE, 25) vs `ᚪ` (A, 24)

**Verdict: CONTRADICTION (single-rune substitution). It sits on unsolved ciphertext,
so it is the one that could matter. Canon is supported three lineages to one.**

Canon segment 24 is **LP2 page 24**, one of the 55 unsolved pages (segments 0..54 sum
to the 12,956-rune unsolved stream, so segment index = LP2 page number there).

```
canon:  …ᛝᚠᚪᛋᛡᛁᚻᛒᚱᚪᚢᚣ >>ᚫ<< ᚢᛟᛠᚪᚣᛖᛟᚫᛖᛈᚠᛒ…
file :  …ᛝᚠᚪᛋᛡᛁᚻᛒᚱᚪᚢᚣ >>ᚪ<< ᚢᛟᛠᚪᚣᛖᛟᚫᛖᛈᚠᛒ…
```

- `difflib` over the aligned window returns exactly **one** opcode, a `replace` of
  length 1 ↔ 1. Twelve runes of context on each side are identical. Not an insertion,
  not a deletion, not a re-pagination: a clean substitution.
- `ᚪ` (A, index 24) and `ᚫ` (AE, index 25) are **adjacent in Gematria Primus** and
  differ by one small stroke in the glyph. A 24/25 swap is the exact signature of an
  OCR or hand-transcription slip.
- **Significance: real but bounded.** One rune in 12,956 moves no aggregate this
  project reports (doublet count, IoC, entropy). It matters to a crib, an alignment,
  or a positional argument that lands on that rune, and to nothing else.
- **Not resolved from pixels in this lane.** See `GAPS-E.md`.

## C-E-02 — canon segment 56, rune 80 (global rune index 13,121): `ᚣ` (Y, 26) vs `ᛖ` (E, 18)

**Verdict: CONTRADICTION (single-rune substitution), and it is decidable — we are right.**

Canon segment 56 is the final page, carried in runes but written in **cleartext**:

```
canon:  …ᛁᚾᛞᚦᛖᛞᛁᚢᛁᚾᛁᛏ >>ᚣ<< ᚹᛁᚦᛁᚾᚪᚾᛞᛖᛗᛖᚱᚷᛖ
file :  …ᛁᚾᛞᚦᛖᛞᛁᚢᛁᚾᛁᛏ >>ᛖ<< ᚹᛁᚦᛁᚾᚪᚾᛞᛖᛗᛖᚱᚷᛖ
```

Transliterated, the page reads `PARABLE LICE THE INSTAR TUNNELNG TO THE SURFACE WE
MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIUINIT_ WITHIN AND EMERGE`. Canon gives
**DIUINITY**; scream314 gives **DIUINITE**. English fixes the reading: **`ᚣ`/Y is
correct and scream314 has a typo.** One `replace` opcode; the tail re-aligns at
delta 0.

C-E-02 is what downgrades C-E-01: the same file already contains one provable
transcription error, so the prior that C-E-01 is also scream314's error rather than
ours is strong — and the 2015 resvolver witness confirms it independently.

---

## C-E-03 — `henkman/liberprimus` (2016-08-14): three more contradictions, all in different places

`henkman/liberprimus` was recovered late in this lane
(`2212f631714711a2d51c858c47dfb6f89ae9ee44`, HEAD 2020-06-28). Its `liberprimus.txt`
was added in the **initial commit `8cc9665`, 2016-08-14T18:01:14+02:00**, and
`git log -- liberprimus.txt` shows exactly that one commit — **the file has never been
edited**. It is therefore a clean 2016 witness, seven months before the iddqd root.

It holds **13,072 runes** (canon: 13,136 — it is 64 runes short) and reproduces 48 of
our 57 segments verbatim. The nine divergences classify as:

| canon segment | verdict | detail |
|---|---|---|
| 0, 3, 6, 19, 26, 39 | **OMISSION** | runs of 1–56 runes simply absent (segment 0 alone drops 6 + 56 + 1) |
| 35 | **INDEL** | the rune `ᛒ` (B) sits at position 155 in henkman and at 160 in canon — a five-place displacement of the same rune, not an absence |
| **33** | **CONTRADICTION ×2** | position 100 and position 117: canon `ᛒ` (B, 17) vs henkman `ᚹ` (W, 7), both times, with identical 12-rune context on each side |
| **55** | **CONTRADICTION** | position 19: canon `ᛉ` (X, 14) vs henkman `ᛚ` (L, 20), identical context |

This **independently reproduces Lane B's finding** (`page 33 W vs B twice`,
`page 35 B vs absent`, `page 56 L vs X`) from a separate clone and a separate
classifier. One refinement: the page-35 case is a **displacement**, not an absence —
the `ᛒ` is present five runes early — which is the signature of a dropped-and-
reinserted rune rather than a different reading.

**The decisive observation is that henkman and scream314 disagree with canon in
*different* places.** henkman agrees with canon on segments 24 and 56 (C-E-01,
C-E-02); scream314 agrees with canon on segments 33 and 55 (C-E-03). Neither
dissenting witness corroborates the other. On every one of the four contested runes:

| contested rune | canon | resvolver 2015 | iddqd (all 4 revs) | henkman 2016 | scream314 |
|---|---|---|---|---|---|
| seg 24 @172 | `ᚫ` | `ᚫ` | `ᚫ` | `ᚫ` | **`ᚪ`** |
| seg 33 @100 | `ᛒ` | `ᛒ` | `ᛒ` | **`ᚹ`** | `ᛒ` |
| seg 33 @117 | `ᛒ` | `ᛒ` | `ᛒ` | **`ᚹ`** | `ᛒ` |
| seg 55 @19 | `ᛉ` | `ᛉ` | `ᛉ` | **`ᛚ`** | `ᛉ` |
| seg 56 @80 | `ᚣ` | `ᚣ` | `ᚣ` | `ᚣ` | **`ᛖ`** |

**Canon is the majority reading on every contested rune, and each dissent is a
lone witness.** henkman's dissents are additionally discounted by the fact that the
same file drops 64 runes outright — a transcription with that many omissions is a
noisy witness on substitutions too.

*(Neither `ᛒ`/`ᚹ` nor `ᛉ`/`ᛚ` is a Gematria-Primus-adjacent pair, unlike `ᚪ`/`ᚫ` in
C-E-01. They are, however, visually confusable futhorc glyphs — `ᛒ` vs `ᚹ` differ by
the second bowl, `ᛉ` vs `ᛚ` by the second arm — so the OCR/hand-slip explanation still
fits.)*

---

## Non-conflicts, recorded so nobody re-raises them

- **`Skyro7777777/LiberPrimusDecoded` `decoder/all_pages.json` (21,272 runes) and
  `decoder/unsolved_pages.json` (16,378).** These JSON files store both a `runes`
  field and a `raw_section` field per page, so a *flat* rune extraction reads the same
  text twice, interleaved, and the segment search lands on the wrong copy. Extracting
  only the `runes` field gives **15,934** and **12,956** runes respectively, and the
  divergence collapses to exactly segments 24 and 56 — the same scream314 lineage,
  nothing more. The earlier report of segments 6 and 39 diverging in these files was
  an extraction artefact and is **retracted**.
- **`cicada-solvers/lp-decrypter` `lp_data/lp_section_data.py`.** Earlier reported as
  missing 56 of 57 segments. That was the `ᛂ`/U+16C2 alias, not a transcription
  difference. With the alias applied it is **57/57**. Retracted.
- **`crackalamoo/futhorc`.** Uses the full 33-rune Anglo-Saxon futhorc including `ᛥ`
  (STAN) and `ᛢ` (CWEORTH), plus `᛫` as a separator. It is a general futhorc package,
  not an LP transcription. Not comparable.
- Files under 1,000 runes were not segment-tested: alphabet tables, single pages, key
  lists, README samples.

---

## Provenance warning that belongs with the conflicts

**`jens-wedin/liber-primus` is not an independent third party.** All 8 commits are
authored `Claude <noreply@anthropic.com>`; the first is
`f7d40c225255eea6a19e76e458c6b058babdb668`, **2026-08-18T16:51:25Z** — the day before
this corpus operation. An earlier note in this lane's `PROGRESS.md` described it as
independently reaching this project's doublet / lag-1 / running-key conclusions.
**That is retracted.** It is same-week AI-authored work and must not be counted as
third-party corroboration of anything. It remains a *useful* tool — its
`attack_keyskip.py` is one of the few genuine skip-aware beam searches in the corpus —
but it is a sibling, not a witness.

The same caution, at lower confidence, applies to several other 2026-vintage repos in
this corpus: `Skyro7777777/LiberPrimusDecoded` (first commit 2026-08-11, sole author
`z@container`), `AegisTrustCore/Liber-Primus-HMS-Run-Time` (2026-08-12),
`Pitchfork-and-Torch/instar` and `…/liber-research` (2026-08-14 / 2026-08-18),
`chipper1999/*` (2026-08-07), `hugvig/liber-primus-research` (2026-08-09),
`NoxxGames/LiberPrimus-GPU` (2026-05-15, carries a `.codex/agents` directory).
Their authorship is not verifiable from repo metadata alone; they are flagged in
`TOOLS.json` under `notes` and should not be treated as independent confirmation of
anything without further checking.
