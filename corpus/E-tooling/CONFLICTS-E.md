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

**And in fact the same repository shows the reading being arrived at.** `c1cada` also
holds an *earlier and different* stream, `transcriptions.rne` (13,053 runes on
2015-01-16, 13,072 on 2015-01-23), which carries the competing reading discussed under
C-E-03b — and the same transcriber's later repository replaces it, under the same
filename, with our 13,136 stream. See C-E-03b for the full commit-by-commit chain.

---

## Headline 2 — two lineages disagree with canon, in different places, and canon wins both

*(This heading previously read "exactly one lineage disagrees". That was written before
`henkman/liberprimus` and the cijhho archive were recovered. There are two dissenting
lineages, they contradict canon at different runes, and they do not corroborate each
other. See C-E-03 and C-E-03b.)*

### Lineage A — `scream314` (15,938 runes): contradicts at segments 24 and 56

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

**Canon is the majority reading on every contested rune.** henkman's dissents are
additionally discounted by the fact that the same file drops 64 runes outright — a
transcription with that many omissions is a noisy witness on substitutions too.

### C-E-03b — both readings are dated to the first three weeks of January 2015, and canon is the corrected one

The full dated chain, assembled from three repositories' git histories:

| date (commit) | repo / file | n runes | index SHA-256 | reading |
|---|---|---:|---|---|
| **2015-01-09T23:39:25Z** `52e5c7e4` | `thomasandfriends/Cicada3301Runes` `data/runes.rune.old` (also `.rune~`, `.rune.old~`) | 13,072 | **`a38c30ca109919b8ec55d28f924e7544307e93422bda8c5ed2b22f2e69180d0f`** | **W / W / L** |
| 2015-01-09 (same commit) | `thomasandfriends/…` `data/runes.rune` | 13,063 | `ae9e6c12…` | **W / W / L** |
| 2015-01-16 `42d3394` | `resvolver/c1cada` `transcriptions.rne` | 13,053 | `3a2a1f8f…` | (same family) |
| 2015-01-20 `f75c1de` | `resvolver/c1cada` `perl/page.*.txt` | 13,377 | `ec3d102a…` | draft, garbled page 27-32 |
| **2015-01-21T16:34:18+01:00** `fe9b2255` | `resvolver/c1cada` `perl/page.*.txt` | **13,136** | **`74cebdb0…`** | **B / B / X — canon** |
| 2015-01-23 `420a2f4` | `resvolver/c1cada` `transcriptions.rne` | 13,072 | `a38c30ca…` (identical to the 2015-01-09 file) | W / W / L |
| **2015-01-23** `420a2f4` | `resvolver/c1cada` `translation/liber_primus.rne` | **13,136** | **`74cebdb0…`** | **canon** |
| 2016-08-14 `8cc9665` | `henkman/liberprimus` `liberprimus.txt` | 13,072 | `e9d9ed39…` | W / W / L |
| 2017-03-01 `218ed88` | `rtkd/iddqd` `…transcription--master.txt` | 15,935 | — | canon-compatible (all 57 segments) |
| **2017-05-10** `9d9faa7` | `dude123124144/Liber-Primus-Runes-OCR` `misc_scripts/transcriptions.rne` | **13,136** | **`74cebdb0…`** | **canon** |

Three things follow, and they should be stated in this order.

**1. The W/W/L reading is the OLDER one.** The earliest dated rune stream anywhere in
this corpus is `thomasandfriends/Cicada3301Runes`, a single commit by Misha Wagner on
**2015-01-09**, six days after the Liber Primus was published — and it reads `ᚹ` at
segment 33 @100 and @117 and `ᛚ` at segment 55 @19. Our reading is not the original; it
is a **correction made twelve days later**.

**2. The correction is the right way round.** The 13,136 stream is not a divergent
branch of the 13,072 one — it is *longer by 64 runes*, and those 64 runes are exactly
the omissions that make segments 0, 3, 6, 19, 26, 35, 36 and 39 fail to match in the
older file. A transcription that gains 64 previously-missed runes and simultaneously
changes three glyphs is a transcription being **re-checked against the images**, which
is the only process that produces that combination. A drifting copy loses runes; it
does not gain them.

**3. The transcriber who produced the older reading adopted the newer one.**
`resvolver/c1cada` carries both side by side on 2015-01-23, and `dude123124144`'s own
later repository re-publishes `transcriptions.rne` — the same filename that held the
13,072 stream — as the **13,136 stream** in 2017. He replaced his own reading.

That is the strongest statement this lane can make about the canon: it is the
corrected successor of the community's first attempt, adopted by the person who made
the first attempt, and it is what every later mainstream lineage carries.

The W/W/L reading survives downstream in `henkman/liberprimus` (2016) and in the
cijhho script archive, which is why it keeps resurfacing as an apparent conflict.

#### The cijhho archive holds both readings too

**The whole provenance question resolves inside one repository.** `resvolver/c1cada`
holds *both* readings, in files whose git history is dated and checkable, and all of
them are committed by the same transcriber, `dude123124144`:

| commit | date | file | n runes | index SHA-256 |
|---|---|---|---:|---|
| `42d3394` | 2015-01-16T03:04:24-05:00 | `transcriptions.rne` | 13,053 | `3a2a1f8f2c6e52f835df487c3ac06478ba3cdfdee697f129b14519b6fd523de9` |
| `f75c1de` | 2015-01-20T22:36:59+01:00 | `perl/page.*.txt` (11 files) | 13,377 | `ec3d102ac6d4e03aa2d10ab15565b043f89f49a66faaed4345a909b7ba1d7d36` |
| **`fe9b2255`** | **2015-01-21T16:34:18+01:00** | `perl/page.*.txt` | **13,136** | **`74cebdb0…` — canon** |
| `420a2f4` | 2015-01-23T12:56:18-05:00 | `transcriptions.rne` | 13,072 | `a38c30ca109919b8ec55d28f924e7544307e93422bda8c5ed2b22f2e69180d0f` |
| **`420a2f4`** | **2015-01-23T12:56:18-05:00** | `translation/liber_primus.rne` | **13,136** | **`74cebdb0…` — canon** |

The 13,072 file at `a38c30ca…` reproduces **exactly the C-E-03 contradictions**:
segment 33 @100 `ᛒ`→`ᚹ`, segment 33 @117 `ᛒ`→`ᚹ`, segment 55 @19 `ᛉ`→`ᛚ`, with the
missing-segment set `[0, 3, 6, 19, 26, 33, 35, 36, 39, 55]` — henkman's set plus 36.
It is 13,072 runes, the same length as henkman's file, though the two index hashes
differ slightly, so they are near neighbours rather than copies.

**And the transcriber corrected himself.** The same author's later repository,
`dude123124144/Liber-Primus-Runes-OCR`, carries a file with the *same name*,
`misc_scripts/transcriptions.rne`, committed `9d9faa7` on **2017-05-10** — and it is
**13,136 runes hashing to `74cebdb0…`**. So does `misc_scripts/liber_primus_words.rne`
in the same directory. The person who produced the 13,072 reading in January 2015
replaced it, under the same filename, with our reading.

That is the strongest statement this lane can make about the canon:

> Both readings existed in January 2015, in one repository, by one transcriber. The
> 13,072 reading is the earlier and lossier of the two; the 13,136 reading is the one
> he corrected to within a week, published again in `translation/liber_primus.rne`,
> and still carried under the same filename two years later. The 13,072 reading
> survives downstream in `henkman/liberprimus` (2016) and in the cijhho script
> archive; the 13,136 reading is what `rtkd/iddqd` (2017), `scream314` (2018),
> `micheloosterhof/aldegonde` (`data/page0-58.txt`),
> `r4nd0mD3v3l0p3r/LiberPrimusSolver` (`data/unsolved.txt`),
> `cicada-solvers/libergo` (`cmd/runesub/runesub.sh`) and this project all carry.

#### The cijhho archive holds both readings too

`krisyotam/cicada3301` (`76d3ee8c762f60025822c8c05edbf31351636469`) carries an archive
attributed to `cijhho`, and inside its `2014/` folder there are **two different rune
streams**:

| file | n runes | index SHA-256 | agrees with |
|---|---:|---|---|
| `archives/cijhho/2014/Liber Primus/runes in text format.txt` | **13,136** | **`74cebdb0…`** | **canon, exactly — a third copy of our stream** |
| `archives/cijhho/2014/additional docs/scripts/runes.py` | 13,092 | `0762d8ff…` | **the henkman lineage** |
| `archives/cijhho/2014/additional docs/scripts/runescript.py.py` | 13,101 | `3d395ee6…` | **the henkman lineage** |

Both script files miss the same segment set as henkman — `[0, 3, 6, 19, 26, 33, 35,
39, 55]` plus 36 — and carry **exactly henkman's three contradictions**: segment 33
@100 `ᛒ`→`ᚹ`, segment 33 @117 `ᛒ`→`ᚹ`, segment 55 @19 `ᛉ`→`ᛚ`. That is not
coincidence; it is one transcription copied twice.

So the corpus holds **two** competing lineages for those three runes, not one witness
and one slip. The count on 33/55 is therefore *three lineages* (canon /
`resvolver` 2015 / `iddqd` 2017 / `scream314` 2018 — the last three agreeing with us)
against *one lineage with at least three members* (the cijhho scripts and
`henkman/liberprimus`). Canon still wins, but by weight of independent lineages rather
than by isolation of the dissenter.

**Dating caveat, stated because it matters.** `krisyotam/cicada3301` was created
**2026-04-11** — the "2014" is a *folder label inside a 2026 archive*, not git evidence.
Nothing here dates the cijhho scripts to 2014. The only hard date evidence for this
lineage is henkman's 2016-08-14 commit. By contrast `resvolver/c1cada`'s
2015-01-21 date is git history and is checkable.

Two further notes on these files:
- `runes.py`'s segment-0 "contradiction" is an **artefact**: the file embeds the
  Gematria Primus alphabet table inline as a rune string, and the classifier's anchor
  lands on it. `runescript.py.py` labels the same segment INDEL. Discount segment 0.
- The presence of *both* readings inside one archive folder is itself the useful fact:
  whoever assembled it had both, and kept both.

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
