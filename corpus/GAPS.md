# corpus/GAPS.md — what we demonstrably do NOT have

_Phase 0 companion to `INVENTORY.md`. Compiled 2026-08-19 by enumeration, not estimation._
_Rule: a gap is only listed here if its absence was **verified**, and it is stated specifically
enough to be actionable. "Need better images" is not a gap; "pages 40–49 held only as 400-DPI
renders, no source PDF with a text layer" is._

Ordered by how much new surface area closing it would open.

---

## G-01 — Primary puzzle artifacts: the collection does not exist ★★★★★

**Verified state:** `puzzles/` contains **2 files** — `2013/artifacts/761_The-Instar-Emergence.mp3`
(4.01 MB) and a README. Nothing else.

Missing, specifically:

| era | artifact | held? |
|---|---|---|
| 2012 | The original 4chan image (2012-01-04) | ✗ |
| 2012 | `845145127.com` countdown page captures | ✗ |
| 2012 | The 14 physical poster photos (GPS-located, multi-country) | ✗ |
| 2012 | QR codes from the posters | ✗ |
| 2012 | Every intermediate image in the chain | ✗ |
| 2013 | The 2013 entry image | ✗ |
| 2013 | `761_The-Instar-Emergence.mp3` | ✓ only |
| 2014 | The 2014 entry image | ✗ |
| 2014 | The oak-tree/runes image (2016-01-05) | ✗ |
| all | Original file **bytes** rather than re-encodes | ✗ |

**Why it matters:** every steganographic and forensic conclusion in this repo about the
*puzzle chain* rests on other people's write-ups, not on artifacts we hold. Lane G cannot
re-run a battery on files that are not here.

---

## G-02 — PGP signature verification status is recorded nowhere ★★★★★

**Verified state:** the signed message *texts* are quoted in `research/03-*.md` and 42 `.asc`
files sit under `round10/L6-archives/fetched/jaxonkuipers/corpus/`. But **no file in this
repository records which signatures verify against key `7A35090F` and which do not.**

This is the repo's own stated authenticity test (`KNOWLEDGE.json: authenticity_test`), and we
have never machine-verified it. Needed: every claimed Cicada message as an `.asc`, a
`gpg --verify` run against the canonical public key, and a table of PASS/FAIL/NO-SIG with the
signature timestamp — which is itself a dataset (see G-09).

---

## G-03 — No independent transcription; all lineages share one 2017 root ★★★★☆

**Verified state:** krisyotam, relikd and rtkd are **rune-for-rune identical, 13,136/13,136,
0 divergences** — and `analysis/transcription/TRANSCRIPTION-VERDICT.md` establishes they all
descend from **rtkd/iddqd (2017)**. Unanimity is not independence.

**What is missing:** a from-scratch re-read that does not consult canon. Whole-page AI vision
failed (mean alignment 0.145 = noise). Per-rune high-zoom reading (~13,000 crops) is specified
in `handoff/PARKED.md` P-1 with a testable unpark threshold (≥99% per-rune accuracy on the
solved control pages) and has never been executed.

**Also missing:** any source PDF **with a text layer**. Only 400-DPI raster renders are held.
A text layer would settle the transcription question outright.

---

## G-04 — Third-party tooling is referenced but not vendored ★★★★☆

**Verified state:** zero third-party repos are cloned into this tree.

Named in prose, absent on disk: `rtkd/iddqd` · `relikd/LiberPrayground` · `krisyotam` ·
`cadrypt` · `LiberPrimusSolver` · `cicada-library` · `JBO` · `tweqx/dwh-check` ·
CyberChef recipes · `opensource.exposed` gematria tools.

We therefore cannot say what each tried, what it concluded, or whether its negatives were
produced by instruments that could actually detect a signal — the failure mode this repo has
documented in its own history.

---

## G-05 — Community record is two sources deep ★★★★☆

**Held:** Reddit `Cicada_comments.jsonl` (35.41 MB) + `Cicada_posts.jsonl` (17.66 MB), and
two Discord channel exports (`solving-lp-general.txt` 6.51 MB, `solved-pages.txt` 24,335 lines).

**Missing entirely:**
- **IRC logs** — `#cicadasolvers` and predecessors, every era. The April-2017 message was
  *found* in IRC; the logs are primary record.
- **Forum**: `cicada3301.boards.net` threads.
- **Wikis**: `uncovering-cicada.wikia.com` as captures (the live site is dead).
- **Discord**: every channel except the two above.
- **Non-English communities** — Russian, German, Japanese, Chinese, Portuguese. Named in the
  brief as parallel research bodies; we hold nothing from any of them.
- **YouTube** — transcripts and comment threads.
- **Twitter** — the 3301 accounts and the 2014/2016 announcement tweets.
- **Deleted content** — reveddit-style mirrors, deleted-comment archives, RSS caches.
- **Mailing lists** — cypherpunks / metzdowd 2011–2013 (RECON-A item I-03, `never-run`).

**Provenance problem on what we do hold:** no capture date, tool, or method is recorded for
either the Reddit or the Discord dumps. Per the standing order these must be re-collected.

---

## G-06 — Archive/dead-web sweep barely started ★★★★☆

**Held:** `analysis/anend_hunt/fetched/` (3 files, 5.01 MB) and one 4chan `/x/` thread PDF.

**Missing:**
- **Chronological Wayback walks.** No snapshot *series* is held for any domain. The brief is
  right that diffs between captures are themselves evidence; we have no diffs because we have
  no series.
- **Wayback captures of the image files themselves** — different capture dates can hold
  different bytes for the same filename. Never checked.
- **archive.today**, **Google cache remnants**, **defunct hosts**.
- **Onion mirrors** beyond the single iBotPeaches copy — every current holding is a
  mirror-of-a-mirror.
- **Internet Archive item metadata and derivative files** (only `3301.iso` was touched, and
  only for one inner file).
- **Torrent / IPFS** archives.

---

## G-07 — Metadata layers nobody has read ★★★☆☆

Explicitly enumerated in the brief and verified absent here:

- **TLS certificate-transparency logs** for every domain the puzzle touched.
- **DNS / WHOIS history** for `845145127.com` and successors.
- **HTTP headers in archived responses** — held HTML is body-only.
- **PDF producer strings** across the 128 untracked PDFs.
- **EXIF across the full artifact set** — run on LP pages only.
- **Hosting IP neighbours** for the leaked `li676-224.members.linode.com` / `106.186.123.224`
  (RECON-A item H-01, `never-run`).

---

## G-08 — Cipher-space literature ★★★☆☆

`analysis/attribution/papers-archive/` is 140 files of **journalism about the puzzle**. There
is **no** academic cryptanalysis literature on the *cipher families*: runic Vigenère variants,
totient-based shifts, autokey, book ciphers, or extreme-value thresholds for keyspace search.

This is the gap most likely to change method rather than add data.

---

## G-09 — Timestamps as a dataset ★★★☆☆

Post times, commit times, file mtimes and PGP signature timestamps exist scattered across
sources. **No timeline dataset has ever been assembled**, and the signature timestamps
specifically (2016-01-01 00:01:07 UTC; 2017-04-04 ~23:23 GMT) are recorded in prose only.

---

## G-10 — Physical layer ★★☆☆☆

No poster photographs, no sticker locations, no geotagged uploads. The 2012 dead-drop
coordinates are described in `research/01-origins-2012.md` but no imagery is held.

---

## G-11 — Our own unmerged work ★★★★★ (cheapest to close)

Not an external gap — **we already own this and cannot see it from `master`.** 27 commits,
7 branches, 8 artifacts absent from the working tree. Full table in `INVENTORY.md` §4.

Includes an entire **Campaign XV**, an entire **Campaign VII** with a `PAGE-MAP.md`, a
`NEGATIVE-RESULTS.md` archive, `OPEN_QUESTIONS.md`, and a pre-registered r8–r12 experiment
tree on ICC/DQT/stylometry that `master` knows nothing about.

⚠️ **Merge hazard:** the branch rounds 8–12 are *different work* from master's rounds 8–12.
Merging without renaming will conflate two research programmes.

---

## G-12 — Provenance we cannot currently establish ★★★☆☆

Per the standing order ("re-collect anything whose provenance we can't establish"), these
must be re-acquired with capture metadata even though bytes are on disk:

| holding | size | missing |
|---|---|---|
| Reddit dumps | 53 MB | capture date, tool, API/dump source |
| Discord exports | 6.5 MB+ | export date, tool, channel IDs |
| papers-archive | 110 MB, 140 files | retrieval date, source URL per file |
| onion HTML | 4.55 MB | which mirror, when, vs. which original |
| T1–T4 blobs | 81.7 MB | derivation chain not fully documented |
| key corpora | 45+ MB | no per-file hash recorded at fetch time |

**Precedent for why this is not pedantry:** `_560.00` was a silently truncated download
(2,412,544 B vs 3,992,970 B, an exact prefix) and went unnoticed for two days, costing a 40%
coverage gap in a completed lane.

---

## Blocked / manual-retrieval required

Nothing yet — no fetches have been attempted in Phase 0. This section will be populated by the
lanes with anything that rate-limits, paywalls, or robots-excludes us, together with a note of
what sits behind it.
