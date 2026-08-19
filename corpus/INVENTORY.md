# corpus/INVENTORY.md — what this repository already holds

_Phase 0 of the corpus sweep. Compiled 2026-08-19 by direct enumeration of the working
tree, the git object store, all remote branches, and both stashes. No fetches were
performed. Nothing below is estimated; every count is measured._

---

## 0. Headline findings, before the detail

Three things a corpus operation needs to know immediately:

1. **27 commits of research exist on branches that were never merged into `master`**, across
   two *separate* research programmes. Eight artifacts are on branches and absent from the
   working tree. See §4 — this is unrecovered material we already own.
2. **A round-numbering collision.** `master` has Rounds 8–12 (SEED/GEOMETRY/PAYLOAD/…). The
   `research/round-*` branches have a *different* Rounds 8–12 (ICC parse / DQT matrix /
   stylometry / external sweep). Same numbers, different work. Any corpus that merges these
   naively will silently conflate them.
3. **The primary-artifact collection barely exists.** `puzzles/` contains **2 files**: one
   MP3 and a README. The 2012 chain, the 2014 chain, the posters, the onion drops and the
   signed messages are not held as artifacts — only described in prose. This is the single
   largest gap and it is Lane A's entire mandate.

---

## 1. Scale

| | files | size |
|---|---|---|
| Tracked in git | **1,099** | 75.5 MB |
| Untracked / gitignored, present on disk | **2,478** | **693.7 MB** |
| Total working tree | 3,577 | 792 MB |
| Git history | 110 commits | |

Tracked composition: 342 `.py`, 236 `.txt` (64 MB — mostly key corpora), 213 `.json`,
182 `.md`, 84 `.log`, 13 `.sh`, 5 `.bin`, 4 `.pdf`.

Untracked composition: 905 `.png` (72 MB), 680 `.bin` (45 MB), 301 `.txt` (137 MB),
146 `.jpg` (87 MB), 128 `.pdf` (112 MB), 105 `.html`, 42 `.asc` (14 MB), 6 `.jsonl` (54 MB).

**Read that second row carefully: 90% of the corpus by volume is untracked.** It is
reproducible-by-script in principle, but it is not versioned, and its provenance lives in
`handoff/capsule/MANIFEST.json` rather than in git.

---

## 2. What we hold, by lane

### Lane A — primary artifacts: **almost nothing**

| holding | state |
|---|---|
| `puzzles/2013/artifacts/761_The-Instar-Emergence.mp3` | 4.01 MB, present |
| `puzzles/` everything else | **absent** — 1 README |
| 2012 chain artifacts (images, posters, dead-drop photos) | **absent** |
| 2014 chain artifacts | **absent as originals** |
| Onion page HTML | 23 files, 4.55 MB, `analysis/armada_osint/onions_ibotpeaches/` |
| Onion-derived blobs (T1–T4) | 380 files, 81.7 MB, `analysis/armada_osint/artifacts/` |
| PGP-signed messages | text quoted in `research/`; **corpus of `.asc` originals: partial**, 42 `.asc` files (14 MB) under `round10/L6-archives/fetched/jaxonkuipers/corpus/` |
| Signature verification status per message | **NOT RECORDED ANYWHERE** |

### Lane B — Liber Primus: **strong, with one real weakness**

| holding | state |
|---|---|
| Page images | **56 present** (`data/relikd/p0..p55.jpg`), 0.36–0.80 MB each, 400-DPI Ghostscript renders |
| Image provenance | **56/56 SHA-1 verified** against the archived onion7 dump (`analysis/stego/provenance.json`), extended to SHA-256 in the capsule |
| Transcription | 57 segments, **13,136 runes total; 12,956 unsolved (pages 0–54)**, SHA-256 `023312066df4…` pinned in `PROBLEM.json` |
| Transcription lineages | 3 compared (krisyotam / relikd / rtkd) — **rune-for-rune identical, 13,136/13,136, 0 divergences** |
| Competing transcriptions where they *disagree* | **none exist** — this is the weakness. All lineages descend from one 2017 root (rtkd/iddqd), so unanimity ≠ independence |
| Solved pages | **5**, reproducible end-to-end by `tests/validate.py`; texts in `SOLVED-PAGES.json`, derived by running the cipher |
| Gematria Primus mapping | machine-readable in `KNOWLEDGE.json` and `src/lp/gematria.py` |
| Page crops | 429 files in `data/relikd/` incl. `crops/` (69) and `_crop13/` (64) |

### Lane C — community record: **substantial but narrow**

| holding | size |
|---|---|
| Reddit `Cicada_comments.jsonl` | **35.41 MB** |
| Reddit `Cicada_posts.jsonl` | **17.66 MB** |
| Discord `solving-lp-general.txt` | 6.51 MB |
| Discord `solved-pages.txt` | 24,335 lines |
| Other L6-archives fetched | 77 files, 91.09 MB total |
| IRC logs (any era) | **absent** |
| Forum threads (cicada3301.boards.net) | **absent** |
| Wikis (uncovering-cicada) | **absent as captures** |
| Non-English communities | **absent** |
| YouTube transcripts/comments | **absent** |

### Lane D — archives: **thin**

| holding | state |
|---|---|
| `analysis/anend_hunt/fetched/` | 3 files, 5.01 MB |
| Wayback snapshot walks | **absent** — no chronological capture series held |
| archive.today captures | **absent** |
| 4chan/8chan archive dumps | partial: `_x_ - Paranormal » Thread #18491379.pdf` (7.69 MB) |
| Onion mirrors beyond iBotPeaches | **absent** |

### Lane E — tooling and prior art: **absent as vendored code**

No third-party solver repos are vendored. `rtkd/iddqd`, `relikd/LiberPrayground`,
`krisyotam`, `cadrypt`, `LiberPrimusSolver`, `cicada-library`, `JBO` are all *referenced* in
prose; none is cloned. What exists is this repo's own 342 `.py` files.

### Lane F — press/academic: **the best-stocked lane**

`analysis/attribution/papers-archive/`: **140 files, 110.52 MB**, including the Rolling Stone
feature (9.06 MB PDF), the "Meet The Man Who Solved…" piece, and UnresolvedMysteries threads.
Academic cryptanalysis literature on the *cipher families*: **absent**.

### Lane G — steganography/forensics: **run, and logged**

`analysis/armada20/og_out/`: **431 files, 14.35 MB** of OutGuess extraction attempts.
`analysis/stego/STEGO-VERDICT.md` records the battery and its negatives. `analysis/geometry/`
holds `glyphs2.npz` (8.25 MB). Known residual: the OutGuess **blank-control** experiment
(item G-02) was deferred for want of a Linux box and has not been run.

### Key corpora (for running-key attacks)

`data/keys/` — 103 files / 45.6 MB (campaign13), 15 files / 5.6 MB (campaign12),
`analysis/skeleton/corpus/` 39 files / 35.9 MB, `analysis/bookcipher/books/` 27 files.
Roughly **224 texts / 22.6 M words** were swept in the SKELETON lane.

---

## 3. Analysis threads and the state each was left in

Authoritative machine-readable record: **`liber-primus/LEDGER.json`, 57 entries.**

| status | count |
|---|---|
| `never-run` | **21** |
| `open` | 18 |
| `partially-run` | 10 |
| `negative` | 3 |
| `eliminated` | 2 |
| `superseded` | 1 |
| `in-flight` | 1 |
| `inconclusive` | 1 |

**In flight right now:** Round 13 B-04 Stage D (full-stream escalation) — a shell has been
running 2h05m at the time of writing. Stages A/B/C complete and NEGATIVE.

**Completed this session:** B-04 A/B/C (6.2 M decodes, negative), B-05 (70,680 decodes,
negative), Round 12 A1 closed with both pads recovered and swept (negative).

**Built and gated, not yet run at width:** Round 15 KDF lane (both controls PASS).

---

## 4. ⚠️ Unmerged work — 27 commits across 7 branches

**This is material we already own and cannot currently see from `master`.**

| branch | commits ahead | files differing | contains |
|---|---|---|---|
| `claude/master-roadmap-libra-qk527u` | **11** | 49 | Campaign VII: `PAGE-MAP.md`, `HINT-DERIVED-METHODS.md`, `NEGATIVE-RESULTS.md`, `MASTER-ROADMAP.md`, `ARTICLE-DRAFT.md`, reading-direction probe, image adjudications |
| `research/round-12-external-status-sweep` | 5 | 25 | `EXTERNAL-STATUS-2026-08.md`, `OPEN_QUESTIONS.md`, the r8–r12 experiment tree |
| `research/round-11-dqt-matrix-disambiguation` | 4 | 24 | DQT split resolved as grayscale-vs-colour encode (resolves R8-S2) |
| `research/round-10-exclusion-power-corrected` | 3 | 20 | corrected stylometry exclusion |
| `research/round-9-stylometry-exclusion` | 2 | 17 | Burrows-Delta gate — marked **INVALID**, tested the wrong quantity |
| `research/round-8-artifact-provenance` | 1 | 11 | ICC interior parse, pre-registered |
| `claude/cicada-3301-scope-cigxzi` | 1 | 26 | **Campaign XV** frontier armada, `campaign15/` P1–P3 scripts |

**Absent from the working tree entirely:**
`liber-primus/analysis/campaign15/` · `liber-primus/analysis/campaign7/` ·
`research/experiments/` · `liber-primus/PAGE-MAP.md` · `NEGATIVE-RESULTS.md` ·
`MASTER-ROADMAP.md` · `research/OPEN_QUESTIONS.md` · `research/EXTERNAL-STATUS-2026-08.md`

**Stashes:** 2, both **pure CRLF noise** (18,574/18,574 and 80,493/80,493 insert/delete).
No content. Safe to drop.

---

## 5. Provenance state

`liber-primus/handoff/capsule/MANIFEST.json` — **103 items** with measured SHA-256:
23 in-repo · 78 gitignored-but-fetchable · 1 RECOVERED (`DATA/560.13`) · 1 derived.

**Provenance we can establish:** the 56 page images (SHA-1 against the archived onion7 dump,
the strongest available chain), the 6 CicadaOS pads (byte-verified, one against its own
Git-LFS pointer digest after both mirrors 404'd), the rune stream (SHA-256 pinned).

**Provenance we cannot establish** — must be re-collected per the standing order:
the Reddit/Discord dumps (no capture date or method recorded), the 140-file papers archive
(no retrieval metadata), the onion HTML (mirror-of-a-mirror, iBotPeaches), the T1–T4 blobs
(derivation not fully documented), and every key corpus text (fetched by script, but no
per-file hash recorded at fetch time).

**One provenance failure already found the hard way:** `_560.00` was a silently truncated
download — 2,412,544 bytes where the real file is 3,992,970, an exact byte prefix. It went
unnoticed for two days because nothing checked digests against an independent source. That
is why the row above matters.

---

## 6. What NOT to re-collect

Do not re-fetch at equal or lower fidelity:

- **The 56 LP page images.** SHA-1-verified against onion7. Any re-fetch must beat 400-DPI
  originals or it is a downgrade.
- **The rune transcription.** Pinned by SHA-256, three lineages diffed to zero divergence.
  *Do* pursue a genuinely independent re-read (see GAPS) — but that is new material, not a
  re-collection.
- **The 6 CicadaOS pads.** All byte-verified.
- **`761_The-Instar-Emergence.mp3`.** Present at 4.01 MB.

Everything else in §5's "cannot establish" list **should** be re-collected with provenance.

---

## 7. Method inheritance for every lane

Whatever the lanes collect, these are already true here and should not be relitigated:

- Nulls require a **passing plant-and-recover control** (`liber-primus/benchmark/`, 8 gates).
- **Beam, not rigid** decoding: rigid scores the *correct* key as noise (−6.835 vs −4.170).
- Thresholds are **not scale-free**; use `benchmark/null.py: threshold_for(n_trials, len)`.
- Read `LEDGER.json`'s `coverage`/`not_covered`, **not** its `status` — three live lanes were
  found hiding inside closures that were labelled shut.
