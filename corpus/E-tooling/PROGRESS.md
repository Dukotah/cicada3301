# LANE E — Tooling & Third-Party Corpus — PROGRESS

Started 2026-08-19. Working dir: `corpus/E-tooling/`.

## Baseline hashes established (verified locally, not asserted)
Extractor: `corpus/E-tooling/hash_runes.py` (futhorc glyph -> Gematria Primus index 0..28, comma-joined, SHA-256).

| Object | n runes | SHA-256 |
|---|---|---|
| Full transcription `liber-primus/data/krisyotam_runes.txt` | 13,136 | `74cebdb074898f4c2742733a421e6d1717068a4f4cf2802d2b50923285aad329` |
| Unsolved subset (LP2 pages 0-54), per `liber-primus/PROBLEM.json` | 12,956 | `023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585` |

NOTE: the lane brief paired "13,136 runes" with the `0233120…` hash. Those are two
different objects. `0233120…` is the **12,956-rune unsolved subset**. Vendored
third-party transcriptions are diffed against the **13,136 / `74cebdb0…`** baseline.

## Log
- [x] dir scaffold, hasher built + baseline verified

## 2026-08-19 — root-transcription history resolved (the headline item)
`rtkd/iddqd` cloned WITH FULL HISTORY (59 commits, single branch `master`,
HEAD `f2267b0c2f1e1d2662806b90b9c3a2953b3a7023`, last commit 2019-06-17).
`liber-primus__transcription--master.txt` has been edited exactly THREE times:

| commit | date | message | n runes | index SHA-256 |
|---|---|---|---:|---|
| `218ed88` | 2017-03-01 | Clean up. | 15,935 | `d73e79bba056734dfc7f04f894b567c24680d928767d48c0edf632f91e9412ec` |
| `ed95eb7` | 2017-05-21 | Fix error in segment 2 "A Koan". | 15,933 | `c3eb607844a190915ef3436c148603973ae6bb07e98b3569164d9b7c3e9214e5` |
| `3089b65` | 2019-06-17 | Fix segment offsets and transcription errors. | 15,933 | `c3eb607844a190915ef3436c148603973ae6bb07e98b3569164d9b7c3e9214e5` |

- The 2017-05-21 edit is the ONLY change to the rune sequence: two occurrences of
  `ᚹᛋ` (W,S) replaced by the single ligature `ᛠ` (EA), at rune offsets 998 and 1135,
  both inside segment 2 ("A Koan", a SOLVED LP1 page).
- The 2019-06-17 edit, despite its message, changed **no runes at all** — identical
  index hash. It moved segment offsets/structure only.
- ALL THREE versions contain all 57 of our canonical segments verbatim.
  **Our 13,136 never sat downstream of a root correction.**

## 2026-08-19 — decoder-type reads so far (code-backed)
- `rtkd/idkfa` `lib/shift.js` `mutate()`: `arrKeyData[i][keyOffset++]` advances the key
  pointer for EVERY futhark char, unconditionally -> **RIGID**. Interrupters are handled
  only by a hard-coded `Config.patch` lookup table of literal positions in `config.js`
  (a post-hoc list for pages already solved), never searched. It cannot discover an
  unknown skip pattern.
- `relikd/LiberPrayground` `LP/InterruptSearch.py`: real **SKIP-AWARE** search --
  `all()` enumerates every subset of interrupter positions; `sequential()` is a
  bounded hill-climb over the first `maxdepth=9` interrupts per step, scored by a
  supplied `score_fn`. Bounded to periodic/Vigenere key lengths, not running keys.
- `jens-wedin/liber-primus` `attack_keyskip.py`: **SKIP-AWARE beam search**, self-tested
  to 96-98% recovery on planted key-skip text. Reaches independently almost exactly this
  project's conclusions (86 doublets / 0.66% / lag-1 no-repeat / differencing restores
  3.37%). Its running-key test is declared UNDERPOWERED by its own calibration.

---

## 2026-08-20 — RESUMED after network outage

Repair pass re-cloned the targets that the outage had left as empty directories
(`repair2.sh`, log in `clone.log`, `R2-TRY` / `R2-OK` / `R2-FAIL` lines).
Note: the pre-outage `repair.sh` had a path bug that cloned into
`vendor/c/Users/.../vendor/<name>`; those clones were harvested into `vendor/`
and the stray tree deleted.

### Rune-codepoint alias discovered — this was corrupting the diff
Some transcriptions encode Gematria Primus index 11 (**J**) as **U+16C2 `ᛂ`**
(RUNIC LETTER E) instead of the standard **U+16C4 `ᛄ`** (RUNIC LETTER GER).
Seen in `cicada-solvers/lp-decrypter` (`lp_data/lp_section_data.py`, 933 occurrences,
zero `ᛄ`), `Skyro7777777/LiberPrimusDecoded`, and `resvolver/c1cada`.
It is an ENCODING variant, not a reading difference. All extractors in this lane
(`hash_runes.py`, `scan_vendor.py`, `diff_transcriptions.py`, `classify_divergence.py`,
`locate_divergence.py`) now map `ᛂ` -> 11. Before the fix the classifier reported
55 spurious INDELs and 11 spurious CONTRADICTIONs; after it, 0 and 2.
**Practical consequence for third parties:** any tool that reads one of those files
with a plain 29-rune map silently DROPS every J, shifting every later index.

### THE HEADLINE — our 13,136-rune transcription is attested in JANUARY 2015
`resvolver/c1cada` (GitHub, first commit 2015-01-05) carries a full LP2 rune
transcription in `perl/page.{0-2,3-7,8-14,15-22,23-26,27-32,33-39,40-53,54-55,56,57}.txt`.
Concatenated in page order it is **13,136 runes** with index SHA-256
**`74cebdb074898f4c2742733a421e6d1717068a4f4cf2802d2b50923285aad329`** —
**bit-for-bit identical to `liber-primus/data/krisyotam_runes.txt`.**

Provenance walked commit by commit:

| commit | date (author tz) | n runes | index SHA-256 |
|---|---|---:|---|
| `f75c1de0` | 2015-01-20T22:36:59+01:00 | 13,377 | `ec3d102ac6d4e03aa2d10ab15565b043f89f49a66faaed4345a909b7ba1d7d36` |
| `61c1dbb5` | 2015-01-20T22:43:06+01:00 | 13,377 | `ec3d102a…` |
| `2bd22d12` | 2015-01-20T22:47:23+01:00 | 13,377 | `ec3d102a…` |
| `62b2e189` | 2015-01-21T00:32:45+01:00 | 13,377 | `ec3d102a…` |
| **`fe9b2255`** | **2015-01-21T16:34:18+01:00** ("error", WetSand) | **13,136** | **`74cebdb0…`** |
| `a990e0bc` | 2015-01-21T16:34:35+01:00 ("error fixed") | 13,136 | `74cebdb0…` |

The 2015-01-20 first draft had a garbled `page.27-32.txt` (1,674 runes vs 1,433);
the 2015-01-21 pair of commits fixed it, and from that moment the file set has been
our exact stream. No `perl/page.*.txt` has been touched since 2015-01-21.

This puts an identical witness **25.5 months before** the `rtkd/iddqd` root
(`218ed88`, 2017-03-01) and settles the provenance question this lane was opened on:
our canon does not sit downstream of iddqd — the same 13,136 runes existed in
January 2015, days after the Liber Primus was published.

### Transcription conflicts — final position
Only ONE lineage disagrees with canon, and it is one witness sampled four times:
the 15,938-rune **`scream314/cicada3301` `liber_primus.md`**
(index SHA-256 `67a41c67b6a8e8678944d26e9c6af547ef0a07a21eb47e3fd483790ba48e81d7`),
vendored verbatim by `jens-wedin/liber-primus` and `Skyro7777777/LiberPrimusDecoded`
(and by this repo as `liber-primus/data/scream314_lp.md`). Two single-rune
substitutions; see `CONFLICTS-E.md` C-E-01 and C-E-02. Both are contradicted by the
2015 resvolver witness AND by all four iddqd revisions, so canon is 3-lineages-to-1.

### Provenance warning — `jens-wedin/liber-primus` is NOT independent
Every one of its 8 commits is authored `Claude <noreply@anthropic.com>`, first commit
**2026-08-18T16:51:25Z** — the day before this operation. My earlier PROGRESS note
called it an independent replication of this project's doublet / lag-1 / running-key
conclusions. **That was wrong and is retracted.** It is a same-week AI-authored repo
and must not be counted as third-party corroboration.

## 2026-08-20 — LANE COMPLETE

All five deliverables written: `TOOLS.json` (108 rows), `CONFLICTS-E.md`, `GAPS-E.md`,
`REPORT-E.md`, this file.

Final decoder tiering over the 32 repositories whose decode loop was actually read:
**10 rigid, 13 skip-capable-but-no-search, 9 skip-aware-search.**
Null trustworthiness: **10 false, 19 partial, 3 true.** 34 rows are `unknown` — meaning
the decisive loop was not read, NOT that the tool is rigid.

Transcription: `164 omissions, 4 genuine contradictions`, across two dissenting
lineages that do not corroborate each other. The provenance question is closed —
see `CONFLICTS-E.md` C-E-03b for the commit-by-commit chain from 2015-01-09 to
2017-05-10. Headline: our reading is the CORRECTION of the community's first
transcription, made 12 days after it, by the same people, and adopted by them.

Two retractions recorded in this session:
1. `jens-wedin/liber-primus` is Claude-authored, 2026-08-18 — not an independent
   replication of this project's conclusions.
2. The earlier "lp-decrypter contradicts canon in 56 segments" and "Skyro all_pages.json
   contradicts at segments 6 and 39" reports were extraction artefacts (a U+16C2 J
   codepoint alias, and a JSON that stores runes twice). Both withdrawn.
