# REPORT-B — Liber Primus corpus sweep

Lane B, branch `corpus-sweep`, 2026-08-19.

---

## 0. Headline

**The canonical Liber Primus rune stream is attested on GitHub on 2015-01-23 — two years
earlier than this project believed — and every "independent" transcription in existence
traces back to it.** The corpus does not have several witnesses that agree. It has **one
witness, copied**.

Secondary, and the reason the first result is safe to state: **all four decidable reading
conflicts were adjudicated, and all four went to canon** — one against a solved page's
plaintext, three against the SHA-1-pinned page images.

## 1. Deliverables

| file | what it is | gate |
|---|---|---|
| `PAGES.json` | 58 LP2 page records (0–57) + 5 LP1 solved-page records | `validate_pages.py` — **14/14 PASS** |
| `validate_pages.py` | hard gates on the above | run it |
| `LINEAGE-2015.json` | the 2015 origin, with every witness diffed | `lineage_2015.py` |
| `CONFLICT-henkman-2016.json` | full rune-level edit script, henkman vs canon | `align_henkman.py` |
| `ADJUDICATION-page56.md` | page 56 decided against plaintext | `adjudicate/adjudicate_page56.py` |
| `ADJUDICATION-pages33-35-images.md` | pages 33/35 decided against the images | `make_crops.py` |
| `crops/` | the glyph crops (rendered PNG — derived, gitignore) | `make_crops.py` |
| `CONFLICTS-B.md` | every disagreement found, and its disposition | — |
| `GAPS-B.md` | what could not be established | — |
| `MANIFEST.json` | every artifact fetched, with hashes and provenance | `build_manifest.py` |
| `hunt_results.json` | the external transcription hunt | `hunt_transcriptions.py` |
| `analysis/reproduce/` | 7 standalone scripts + runner | **7/7 PASS**, 0.8 s |

### PAGES.json validation

```
$ PYTHONIOENCODING=utf-8 python corpus/B-liber-primus/validate_pages.py
  page records                                               OK  58
  total LP2 runes                                            OK  13136
  unsolved runes, segments 0-54                              OK  12956
  unsolved runes, pages 0-55                                 OK  12956
  page 50 is runeless                                        OK  0
  krisyotam segments used                                    OK  57
  SHA-256 of comma-joined unsolved indices == PROBLEM.json pin OK 023312066df4...23af1585
  solved LP2 pages                                           OK  [56, 57]
  LP1 solved page records                                    OK  5
  images attached                                            OK  56
  image SHA-1 re-verified on disk                            OK  []
  images flagged as matching archived onion7 dump            OK  56
  per-page rune-string SHA-256 self-consistent               OK  []
  every runic page rune-identical to its krisyotam segment   OK  []
ALL GATES PASS
```

Note on the headline numbers: **13,136 total and 12,956 unsolved are both confirmed.**
"12,956 across pages 0–54" is a statement in *segment* coordinates; in LP2 *page*
coordinates the unsolved corpus is pages 0–**55**, because page 50 carries no runes.
Both forms are gated. See `CONFLICTS-B.md` C-01.

### analysis/reproduce/

```
$ python analysis/reproduce/run_all.py
reproduce_page_runes_01.py     PASS   A WARNING                      Atbash
reproduce_page_03.py           PASS   WELCOME                        Vigenere + interrupters
reproduce_page_05.py           PASS   SOME WISDOM                    transliteration
reproduce_page_06.py           PASS   A KOAN (master and student)    Atbash + shift 3
reproduce_page_14.py           PASS   A KOAN (the circumference)     Vigenere + interrupters
reproduce_page_56_an_end.py    PASS   AN END                         prime-totient keystream
reproduce_page_57_parable.py   PASS   PARABLE                        transliteration
7/7 passed
```

Each script goes from a raw data file to the plaintext with no manual steps, and is a
**standalone re-implementation** — it inlines its own Gematria Primus table, ciphers,
quadgram scorer and interrupter beam search and imports nothing from `liber-primus/src`.
That matters: `tests/validate.py` reproduces the LP1 solves *by calling the rig*, so
agreement there only proves the rig agrees with itself. Two independent implementations
landing on the same plaintext is evidence.

## 2. The four adjudications

| conflict | canon | henkman | decided by | winner |
|---|---|---|---|---|
| page 56, rune 19 | `ᛉ X` | `ᛚ L` | plaintext (solved page) | **canon** |
| page 33, rune 100 | `ᛒ B` | `ᚹ W` | page image | **canon** |
| page 33, rune 117 | `ᛒ B` | `ᚹ W` | page image | **canon** |
| page 35, runes 155/160 | `ᚣ…ᛒ` | `ᛒᚣ…` | page image | **canon** |

**Page 56** is solved, so it is decidable. Method — established from
`liber-primus/ELIMINATION-LEDGER.md:479,525`, not guessed: keystream `key[i] = (p_i − 1)
mod 29` over consecutive primes from the first prime (no offset), decrypt `P = (C − K) mod
29`, with F runes optionally null (a null is dropped and does **not** advance the
keystream). Page 56 has 5 literal F runes; a beam search over skip/keep recovers exactly
one null, at F-occurrence 3.

```
canon   X : ANENDWITHINTHEDEEPWEB THEREEXISTS APAGETHATHASHESTO...   10/10 cribs, -4.5727/char
henkman L : ANENDWITHINTHEDEEPWEB  HEREEXISTS APAGETHATHASHESTO...    9/10 cribs, -4.6001/char
```

The published plaintext — attested in `corpus/C-community/`, in the `cicada-solvers`
org description, and by Boxentriq — is *"WITHIN THE DEEP WEB THERE EXISTS A PAGE…"*.
Canon. Note the failure mode is subtle: `THERE` → `HERE` still reads, and quadgram scoring
alone separates them by only 0.027/char. **External ground truth decided this, not the
score.**

**Pages 33 and 35** are unsolved, so the artifact is the only ground truth. The onion7
renders are machine-set type at 400 DPI (2400×3600), SHA-1 pinned against the archived
dump, and `ᚹ` (one small triangle, upper third) versus `ᛒ` (two stacked triangles, full
height) is a one-whole-triangle difference. All three positions read canon unambiguously.
The strongest crop is `crops/p33_rune115W_vs_rune117B.png`: canon puts a genuine `ᚹ` two
runes from the disputed glyph on the same line, at identical scale — they are visibly
different objects in one image.

Page 35 turned out not to be an insertion at all: both transcriptions carry 271 runes, so
it is a **transposition** — a `ᛒ` five positions early. The image line reads
`ᚣ ᛏ ᛝ ᛡ ᚩ ᛒ · ᛏ ᚦ ᚳ · …`, 23 glyphs matching canon exactly, word breaks included. The
line-initial glyph is `ᚣ` and carries no triangles at all.

## 3. The 2015 origin — the main finding

The hunt was pointed at "pre-root transcriptions", where *root* meant `rtkd/iddqd`
(2017-01-04). GitHub **code** search (rune substrings, not repo names) over seven
distinct probes returned 31 repos; two predate 2017:

### `resvolver/c1cada` — created 2015-01-05

| commit | date | file | runes | vs canon |
|---|---|---|---|---|
| `42d33941` | 2015-01-16 | `transcriptions.rne` | 13,053 | draft |
| `420a2f4d` | 2015-01-23 | `transcriptions.rne` | 13,072 | draft, "fixed error" |
| `420a2f4d` | 2015-01-23 | `translation/liber_primus.rne` | **13,136** | **IDENTICAL** |

`translation/liber_primus.rne` has rune-string SHA-256
`ee1b43cf7534842a87618b7f6f5a83799a8973f7936ab6bf2ae6c6b250c91ade` — the same as
`liber-primus/data/krisyotam_runes.txt` today. The repo's *last* push is 2016-01-15, so
all of its content predates rtkd/iddqd by a clear year even at the latest possible date.

The superseded 13,072-rune draft from the same day carries **14** divergences from canon:

```
delete  page 0  rune 117  EO-TH-J-I
delete  page 0  rune 134  W-B-C-X-D-B-F-M-T-N-E-EA-J-N-L-G-B-X-G-TH-Y-I   (22 runes, a dropped line)
delete  page 0  rune 188  AE
delete  page 3  rune 55   B-W-N-H-M
delete  page 6  rune 2    T
delete  page 19 rune 82   A-IA
delete  page 26 rune 262  NG
replace page 33 rune 100  B -> W          <-- C-04b
replace page 33 rune 117  B -> W          <-- C-04c
insert  page 35 rune 155       -> B       <-- C-04d
delete  page 35 rune 160  B               <-- C-04d
replace page 36 rune 0    Y -> E
delete  page 39 rune 36   N
replace page 56 rune 19   X -> L          <-- C-04a
```

**Every one of the four adjudicated conflicts is in that list.** They are not a 2016
reader disagreeing with a 2017 reader. They are one 2015 author's first-pass errors — and
that same author corrected them, on the same day, in the file that became canon. Three
independent adjudications (one plaintext, two image) agree with his correction every time.

### `henkman/liberprimus` — demoted

Diffed against resvolver's 2015-01-23 draft: **13,072 vs 13,072 runes, one edit block, one
rune** (index 8643, `ᛖ` → `ᚣ` — henkman happens to correct that one toward canon).

`henkman/liberprimus` is a copy of the abandoned 2015 draft. It is **not** an independent
transcription, its four glyph conflicts are 0-for-4 against ground truth, and its 64-rune
shortfall is that draft's dropped lines. Historically interesting; not a source of
corrections. Nothing downstream of canon needs re-examining.

### `Be5haram/CICADA2K16` — 2016-01-14

`RuneSolver.py` (committed 2016-01-14, 20,315 runes) contains the full canonical
13,136-rune stream as a **contiguous substring**. A second pre-2017 attestation of canon,
independent of resvolver's repo but not of his reading.

### The corrected timeline

```
2014-01     Liber Primus images published (onion7)
2015-01-05  resvolver/c1cada created
2015-01-16  first transcription committed             13,053 runes
2015-01-23  "fixed error" -> draft 13,072  AND  translation/liber_primus.rne = CANON
2016-01-14  Be5haram/CICADA2K16 embeds canon contiguously
2016-08-14  henkman/liberprimus = the abandoned draft, 1 rune changed
2017-01-04  rtkd/iddqd "Init."  <- what this project called "the root"
2017-03     dude123124144/...-OCR  13,136 runes, ZERO divergences from canon
later       krisyotam, relikd, rtkd_master - all rune-identical
```

## 4. Other conflicts found

- **An error in this repository's own data.** `liber-primus/data/scream314_lp.md` reads
  `ᚹᛋ` (`W`,`S`) at LP1 page 06 offsets 142 and 279 where `rtkd_master.txt` reads a single
  `ᛠ` (`EA`). Decidable: `ᛠ` gives the koan's actual refrain *"THAT IS NOT **WHO** YOU
  ARE"*; `ᚹᛋ` gives the self-contradictory *"NOT **WHAT** YOU ARE"*. **`rtkd_master` is
  right.** The error propagates into `SOLVED-PAGES.json` and `tests/validate.py`. LP1 only;
  the 12,956-rune unsolved stream is unaffected. Recorded, not edited — see `GAPS-B.md`.
- **The trust anchor asserts a prefix.** `tests/validate.py` checks only the beginning of
  the AN END plaintext, so it never sees that a full decode needs one interrupter. It
  passes today and the page is genuinely solved, but per `CLAUDE.md` this is the file the
  whole repo's credibility rests on and the assertion should be tightened.
- **A codepoint join trap.** Three external sources write GER/J as `U+16C2 ᛂ`; canon uses
  `U+16C4 ᛄ`. 453 runes. Any comparison that skips normalisation reports thousands of
  spurious differences.
- **`aautcsh/idkfa`** (2016-01-17): PARABLE reads `DIUINITE`, canon `DIUINITY`. Canon.
- **`dude123124144/Liber-Primus-Runes-OCR`**: 13,136 runes, zero divergences. Despite the
  name, that is a copy, not OCR output.

## 5. What this changes, and what it does not

**Unchanged.** The 12,956-rune unsolved index, its pin
`023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585`, and every statistic
downstream of it. Canon survived every check that could be made. No re-run is required.

**Changed.** Two beliefs:

1. *"rtkd/iddqd (2017) is the root."* It is not. The root is at least 2015-01-23, and the
   2017 repo is two years downstream.
2. *"Several independent transcriptions agree, so the corpus is solid."* They are not
   independent. The agreement is copying. The corpus rests on one reader — a careful one,
   whose known errors were caught and whose corrections check out, but one.

The practical consequence is in `GAPS-B.md` G-01 and G-05: **there is no independent
re-transcription and no systematic image audit of the 13,136 runes.** Three runes are now
image-verified because three were disputed. `make_crops.py` shows the method is cheap and
that the artifact is good enough to settle any such dispute glyph by glyph. Scaling it to
all 56 pages is the highest-value unglamorous work available here.

## 6. Reproducing everything

```bash
cd /c/Users/dukot/projects/cicada3301
export PYTHONIOENCODING=utf-8

python corpus/B-liber-primus/validate_pages.py                  # 14 gates on PAGES.json
python analysis/reproduce/run_all.py                            # 7/7 solved pages
python corpus/B-liber-primus/adjudicate/adjudicate_page56.py    # the page-56 verdict
python corpus/B-liber-primus/make_crops.py                      # the page-33/35 crops
python corpus/B-liber-primus/lineage_2015.py                    # the 2015 origin
```

Network-touching (re-fetches, needs `gh` auth):

```bash
python corpus/B-liber-primus/hunt_transcriptions.py resvolver/c1cada Be5haram/CICADA2K16
```
