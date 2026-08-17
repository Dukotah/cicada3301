# RECON-C — PRE-REGISTRATION (Round 10, external register)

Written BEFORE any search or fetch. Lane: enumerate Cicada/LP external sources and archives
that this repo has **never ingested**, with live retrievability judgments.

## Hypothesis

H1: There exist community/archival/code corpora relevant to LP2 that (a) are not referenced
anywhere in this repo and (b) are actually retrievable in 2026.

H0 (null): every candidate source is either already held/known-dead in this repo, or is
unretrievable in 2026 (404 / login-walled / never publicly released).

This is a **recon/register** lane. It produces a source register, not a cryptanalytic result.
No decode is attempted. Nothing here can, on its own, overturn the OTP verdict; the most it can
do is name a retrievable corpus that a later lane could ingest.

## Exact test, per candidate source

Each candidate gets THREE independent gates. A source is logged as `NEW+RETRIEVABLE` only if it
passes all three:

- **G1 NOVELTY (falsifiable):** case-insensitive grep of the candidate's distinctive token
  (domain, repo name, handle) across the whole repo `*.md`/`*.txt`/`*.py`/`*.json`, excluding
  `analysis/bookcipher/books/`, `analysis/skeleton/corpus/`, `analysis/foundation/`,
  `data/keys/` (plaintext book corpora — they produce spurious word hits, e.g. "discord",
  "torrent"). **G1 fails if hit count > 0.** This gate is the falsifier: any claim of "never
  pulled" dies on a single grep hit.
- **G2 RETRIEVABILITY:** a live 2026 fetch (WebFetch/WebSearch) must return actual in-scope
  content, not a landing page, a login wall, or a placeholder. A 200 that serves
  "temporarily not available" counts as **DEAD** (this is exactly the Wayback-tor2web failure
  mode the repo already documented; re-classifying it as live would be a false positive).
- **G3 IN-SCOPE:** the content must plausibly bear on LP2 pages 0–54, the external key, the
  2012–2017 primary corpus, or attribution. Generic dark-web crawls and unrelated
  name-squats (2024 "Cicada3301" ransomware) fail G3.

## Numeric pass/fail thresholds (fixed in advance)

- **Lane PASS (H1 supported):** >= 1 source passing G1+G2+G3 **and** carrying primary
  content not derivable from what the repo already holds.
- **Lane WEAK PASS:** >= 1 source passing G1+G2 but only redundant/derived content
  (mirror of held material) — logged as low priority.
- **Lane NULL (H0 retained):** 0 sources pass all three gates.
- **Per-source honesty rule:** anything that fails G1 is reported as "already held" with the
  repo file:line proving it. Anything failing G2 is reported as a sourced dead link with the
  URL and the observed failure. Both are register entries, not omissions.

## NULL CONTROL (pre-declared)

Recon lanes fail by confirmation bias — the pipeline "finds" novelty because nothing checks it.
Two controls:

1. **Decoy set (negative control), declared now, checked with the same pipeline:** these MUST
   come back as already-held or dead. If any is scored NEW+RETRIEVABLE, the pipeline is
   producing false positives and the whole register is void:
   - Wayback tor2web `*.onion.to` CDX (repo: dead, placeholder only)
   - `gy3hoy2zizvuzvdb.onion` as the AN-END destination (repo: refuted hallucination)
   - `scream314/cicada3301`, `iBotPeaches/cicada_3301`, `relikd/LiberPrayground`,
     `krisyotam` onion7 (repo: already held)
   - Zenodo 18199474 "complete translation" (repo: rejected hoax)
   - `Cicada-DWH-HashcatAttempts`, `tweqx/3301-hash-alarm` (repo: already tracked)
   Expected: 6/6 rejected by the pipeline.
2. **Grep-baseline (false-novelty rate):** before trusting any G1 pass, run G1 on the decoy
   tokens. If G1 does not flag the known-held ones, G1's exclude-list is wrong and must be
   fixed before any novelty claim is made.

## What a finding would and would not prove

- A retrievable never-ingested corpus proves only that an **untested haystack exists**. It does
  NOT constitute a key, and the repo's mechanism-level kills (doublet deficit vs. natural-English
  running keys; OTP characterization) still apply to anything linguistic found in it.
- The single class that could matter is **non-linguistic external data of pad length**
  (>= ~13k symbols) published by 3301, or a **primary-source statement about key material** from
  a 2014-era insider. Everything else is register hygiene.

## Budget / scope limits

- No downloads of bulk corpora in this lane (Discord dumps, Common Crawl segments). Retrievability
  is judged by live metadata + a sample fetch; the ingest itself is handed off in open_residue.
- Write only under `analysis/round10/RECON-C/`. No git. No edits to existing files.
