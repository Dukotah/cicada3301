# CONFLICTS-B — Lane B, Liber Primus corpus

Every disagreement Lane B found between sources, and its disposition.
Branch `corpus-sweep`, 2026-08-19.

Rule followed throughout: **record conflicts, do not silently resolve them.**
Where a conflict *is* decidable against ground truth — a solved page's plaintext, or the
SHA-1-pinned page image — it is decided here and the evidence is written down. Where it
is not decidable, it stays open.

| id | subject | status |
|---|---|---|
| C-01 | LP2 page numbering: segment index vs onion7 page number | RESOLVED (reconciled) |
| C-02 | `scream314_lp.md` reads `ᚹᛋ` where `rtkd_master.txt` reads `ᛠ` (LP1 page 06) | RESOLVED against scream314 — **an error in this repo's own data** |
| C-03 | GER/J codepoint: `U+16C2 ᛂ` vs `U+16C4 ᛄ` | RESOLVED as a convention, not a reading |
| C-04 | henkman/liberprimus divergences (9 pages, 13 blocks) | RESOLVED — see C-04a…d and C-08 |
| C-04a | LP2 page 56 rune 19 — canon `ᛉ X` vs henkman `ᛚ L` | **DECIDED for canon** (plaintext) |
| C-04b | LP2 page 33 rune 100 — canon `ᛒ B` vs henkman `ᚹ W` | **DECIDED for canon** (image) |
| C-04c | LP2 page 33 rune 117 — canon `ᛒ B` vs henkman `ᚹ W` | **DECIDED for canon** (image) |
| C-04d | LP2 page 35 — a `ᛒ B` transposed 5 runes | **DECIDED for canon** (image) |
| C-05 | `tests/validate.py` asserts only a prefix of AN END, never sees the truncated tail | OPEN — a gap in the trust anchor |
| C-06 | `aautcsh/idkfa` PARABLE reads `DIUINITE`, canon `DIUINITY` | DECIDED for canon (plaintext) |
| C-07 | `dude123124144` transcription is 0-divergence from canon over 13,136 runes | Not a conflict — evidence of copying |
| C-08 | **"The 2017 rtkd/iddqd root" is not the root** | **OVERTURNED — canon is attested 2015-01-23** |

---

## C-01 — page numbering

`run_stats.load_pages()` splits `liber-primus/data/krisyotam_runes.txt` on `%` into
**57 non-empty segments, 13,136 runes**. `liber-primus/data/sources/relikd_*.txt`
re-splits the *same* runes into **58 onion7 page slots 0–57**, of which **page 50 carries
no runes at all** (p50.jpg is a 13×8 grid of two-character tokens; no runic text).

Reconciliation, corroborated in-repo at `liber-primus/analysis/seed_sweep/prep.py:11`:

```
seg 0..49 -> page 0..49 · page 50 = runeless · seg 50..54 -> page 51..55
seg 55 -> page 56 (AN END) · seg 56 -> page 57 (PARABLE)
```

Consequence worth flagging because it trips people up: **"12,956 unsolved runes across
pages 0–54" is a statement in SEGMENT coordinates.** In LP2 page coordinates the unsolved
corpus is pages **0–55**. Both forms are gated in `validate_pages.py`; both pass.

## C-02 — an error in this repository's own data

`liber-primus/data/scream314_lp.md`, LP1 page 06.jpg, reads **ᚹᛋ (`W`,`S`)** at rune
offsets 142 and 279 where `liber-primus/data/sources/rtkd_master.txt` reads a single
**ᛠ (`EA`)**.

Decidable, because LP1 page 06 is solved (atbash then shift 3):

- `ᛠ` → *"THAT IS NOT **WHO** YOU ARE"* / *"THAT IS WHAT YOU DO NOT **WHO** YOU ARE"* — the
  koan's actual refrain.
- `ᚹᛋ` → *"NOT **WHAT** YOU ARE"* — self-contradictory in context.

**`rtkd_master.txt` is right; `scream314_lp.md` is wrong.** The error propagates into
`SOLVED-PAGES.json` and `liber-primus/tests/validate.py`. LP1 only — the 12,956-rune
unsolved stream is untouched.

## C-03 — the GER/J codepoint

Three external sources write the GER/J rune as **U+16C2 ᛂ**; canon uses **U+16C4 ᛄ**.
453 runes affected. This is a keyboard/typeface convention, not a reading: both map to
Gematria Primus index 11. It is a **join trap** — any tool that compares rune strings
without normalising will report thousands of spurious differences. Normalisation map used
by every Lane B script:

```
ᛂ (U+16C2) -> ᛄ (U+16C4)     ᛣ -> ᛞ     ᚡ -> ᚠ
```

## C-04 — the henkman divergences, and their disposition

`henkman/liberprimus` (repo created 2016-08-14) holds 13,072 runes against canon's 13,136.
It agrees with canon on 49 of 58 pages exactly and diverges on 9 (pages 0, 3, 6, 19, 26,
33, 35, 39, 56) across 13 edit blocks. Full edit script: `CONFLICT-henkman-2016.json`.

**Ten of the thirteen blocks are bulk `delete`s** — canon has runs of runes henkman lacks
(4, 22, 1, 5, 1, 2, 1, 1 runes). That is the signature of *dropped lines*, i.e. an
incomplete transcription, not a competing reading. Only four blocks are substantive glyph
disputes, and all four are now decided:

| id | position | canon | henkman | how decided |
|---|---|---|---|---|
| C-04a | page 56, rune 19 | `ᛉ X` | `ᛚ L` | plaintext — `ADJUDICATION-page56.md` |
| C-04b | page 33, rune 100 | `ᛒ B` | `ᚹ W` | image — `ADJUDICATION-pages33-35-images.md` |
| C-04c | page 33, rune 117 | `ᛒ B` | `ᚹ W` | image — same |
| C-04d | page 35, runes 155/160 | `ᚣ…ᛒ` | `ᛒᚣ…` | image — same |

**henkman is 0-for-4.**

### C-04a in one line
Page 56 is solved. Decoded with the totient keystream `(p_i − 1) mod 29` and one recovered
F-null, canon's `ᛉ` gives *"…THE DEEP WEB **THERE** EXISTS A PAGE…"* — the published
plaintext, attested outside this repo. henkman's `ᛚ` gives *"…**HERE** EXISTS…"*.
Reproduce: `python corpus/B-liber-primus/adjudicate/adjudicate_page56.py`.

### C-04b–d in one line
Pages 33 and 35 are unsolved, so the artifact is the only ground truth. On the
SHA-1-pinned 400-DPI onion7 renders, `ᚹ` (one small triangle, upper third) and `ᛒ` (two
stacked triangles, full height) are plainly different glyphs — page 33 line 7 contains a
genuine `ᚹ` two runes from the disputed glyph, at identical scale, for direct comparison.
Reproduce: `python corpus/B-liber-primus/make_crops.py`.

## C-05 — a gap in the trust anchor (OPEN)

`liber-primus/tests/validate.py` asserts only a *prefix* of the AN END plaintext. A full
decode of page 56 needs **one interrupter** (an F rune treated as a null that does not
advance the keystream); without it the tail truncates. The in-repo gate never sees this
because it stops before the tail. The gate passes today and the page is genuinely solved —
but the assertion is weaker than it looks and should be tightened to the full plaintext.
`analysis/reproduce/reproduce_page_56_an_end.py` does assert the full string.

## C-06 — `aautcsh/idkfa`

`assets/liber-primus-translation.txt` (repo created 2016-01-17), 15,938 runes covering
LP1+LP2, 9 edit blocks against `rtkd_master.txt`. One is decidable: the PARABLE page reads
**DIUINITY** in canon and **DIUINITE** in the candidate. Canon is right.

## C-07 — `dude123124144/Liber-Primus-Runes-OCR`

`misc_scripts/transcriptions.rne` (2017-03), 13,136 runes, **zero** divergences after
normalising `U+16C2 → U+16C4`. Rune-string SHA-256
`ee1b43cf7534842a87618b7f6f5a83799a8973f7936ab6bf2ae6c6b250c91ade` — identical to canon.
Perfect agreement over 13,136 glyphs is not corroboration; it is evidence of **copying**.
Despite the repo name, this is not independent OCR output.

## C-08 — the "2017 root" is overturned

Lane B's working assumption, inherited from the repo's own notes, was that
`rtkd/iddqd` (created 2017-01-04) is the root all canonical transcriptions descend from,
and that henkman (2016-08) was therefore a rare pre-root witness.

**Both halves of that are wrong.** See `REPORT-B.md` §3 and `LINEAGE-2015.json`:

- `resvolver/c1cada` → `translation/liber_primus.rne`, committed **2015-01-23**
  (commit `420a2f4d`), is **13,136 runes, rune-for-rune identical to canon**
  (SHA-256 `ee1b43cf…c91ade`). Canon is attested **two years before** rtkd/iddqd.
- The same repo's `transcriptions.rne`, committed the same day, is the superseded
  **13,072**-rune draft. It carries **all 14** divergences from canon — including every
  one of C-04a…d.
- `henkman/liberprimus` is that draft **with exactly one rune changed** (index 8643).
  It is a copy, not a transcription.

So the four conflicts C-04a–d are not a 2016 reader disagreeing with a 2017 reader. They
are **one 2015 author's first-pass errors, which that same author corrected on the same
day**, resurfacing eighteen months later in someone else's copy of the abandoned draft.
The independent adjudications (plaintext for page 56, images for 33/35) agree with the
correction in every case.
