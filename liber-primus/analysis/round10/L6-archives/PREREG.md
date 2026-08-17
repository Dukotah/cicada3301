# L6-archives — PRE-REGISTRATION

_Written BEFORE any search, fetch or hash. Round 10 armada, lane **L6 — UNPULLED ARCHIVES**._
_Repo: `cicada3301`, branch master. Write-scope: `liber-primus/analysis/round10/L6-archives/` only._

## What this lane is NOT

It is **not** a re-run of the AN-END hunt. `liber-primus/analysis/anend_hunt/FINDINGS.md`
(2026-08) closed that page as **unreachable-by-construction**: its address is produced only by
solving OTP-class LP2 0–54, `gy3hoy2zizvuzvdb.onion` is a refuted hallucination, and the held
corpus hashes null across 2,706 representation tests. That verdict is **accepted as given** and
is not re-derived here. Any candidate source whose only value would be "maybe the AN END page is
in it" is scored against the same bar the AN-END hunt used, not re-litigated.

It is also not a keytext hunt. Round 7 killed *any* natural-language keytext by mechanism
(0/15 unanimous, doublet-exclusion + un-anchorability), so "a new book to try" is not a lead.

## Hypothesis

**H1:** There exist corpora bearing on LP2 / the 2012–2017 Cicada primary record that this repo
has **never pulled**, that are **retrievable in 2026**, and that contain at least one of:
(a) rune/page material not in the held corpus, (b) a key/pad claim, or (c) a primary statement
about key delivery.

**H0 (null):** every candidate is already held, already killed with a reason in this repo, or
unretrievable in 2026 (404 / login-walled / never publicly released / placeholder-only).

## Target classes (fixed in advance, in priority order)

1. **CicadaSolvers community data** — Discord export dumps, the wiki + its full revision history,
   IRC/forum archives, r/Cicada + r/a2e7j6ic78h0j + 4chan/8chan archives 2012–2015.
2. **Code hosts** — GitHub / GitLab / Software Heritage for LP repos, transcriptions, solver
   tools, or pad-shaped data published **after this repo's last sweep (2026-07-27)**.
3. **Web archives** — archive.org, archive.today, Common Crawl for onion7-era mirrors; Tor-v2
   mirror collections; any dataset/torrent of the original onion.
4. **The RECON-C handoff** — `analysis/round10/RECON-C/` pre-registered this exact register lane,
   wrote `fetch_recon_c.sh`, and then **never ran it and never wrote its REGISTER**. Executing
   that fetcher is in-scope and is the cheapest retrievable target on the board.

## Gates (each source scored independently, all three required for NEW+RETRIEVABLE)

- **G1 NOVELTY.** Case-insensitive grep of the source's distinctive token (domain / repo / handle
  / file path) across the whole repo, excluding the plaintext key corpora that produce spurious
  word hits (`analysis/bookcipher/books/`, `analysis/skeleton/corpus/`, `analysis/foundation/`,
  `data/keys/`, `data/*.txt`). **G1 fails on any hit.** Novelty is judged at FILE level, not repo
  level: a named repo already cited for one file can still be novel for a file never fetched.
- **G2 RETRIEVABILITY (2026).** A live fetch must return actual in-scope bytes. HTTP 200 serving
  a placeholder / login wall / "temporarily not available" scores **DEAD**, per the documented
  Wayback-tor2web failure mode.
- **G3 IN-SCOPE.** Must bear on LP2 0–54, the external key, the 2012–2017 primary corpus, or
  attribution. Generic dark-web crawls and the 2024 "Cicada3301" ransomware name-squat fail G3.

## Numeric pass / fail thresholds (fixed NOW)

| Outcome | Bar |
|---|---|
| **HIT (lane POSITIVE)** | ≥1 source passing G1+G2+G3 that yields **(a)** ≥1 rune whose SHA-256 line/page hash is absent from the held canonical corpus, **or (b)** an explicit key/pad claim with a retrievable artifact, **or (c)** a first-person primary statement that 3301 distributed cipher material or keys. |
| **WEAK / register-only** | ≥1 source passing G1+G2+G3 but content is redundant with, or derivable from, held material. Logged, not a finding. |
| **NULL (H0 retained)** | 0 sources clear the HIT bar. |

Two thresholds that must be stated as numbers so a negative means something:

- **Rune-novelty test:** any rune text pulled is normalised to the 29-rune Gematria Primus
  alphabet, and each ≥8-rune line is SHA-256'd and set-compared against the held canonical LP
  line hashes (`data/krisyotam_runes.txt`, `data/scream314_lp.md`, `data/campaign14/`,
  `analysis/**/*runes*`). **HIT = ≥1 novel line hash** that is not a substring/re-segmentation of
  held text. **NULL = 0 novel lines.**
- **Key-claim test:** a text is a key/pad claim only if it contains a first-person or
  primary-source assertion about key or pad delivery. Third-party speculation, "they gave us
  access to a wiki/git/forum", or a solver's hypothesis **does not meet the bar** (this is the
  exact bar `RECON-C/fetch_recon_c.sh` pre-registered for the IRC winners leak, and it is
  inherited verbatim).

## NULL CONTROL (pre-declared — the register is void without it)

Recon lanes fail by confirmation bias. Two controls, both run through the identical pipeline:

1. **Decoy set — MUST come back already-held or dead.** If any scores NEW+RETRIEVABLE the
   pipeline is producing false positives and the whole register is void:
   `scream314/cicada3301`, `iBotPeaches/cicada_3301`, `relikd/LiberPrayground`,
   `krisyotam` onion7, Wayback tor2web `*.onion.to` CDX, `gy3hoy2zizvuzvdb.onion`,
   Zenodo 18199474 "complete translation", `Cicada-DWH-HashcatAttempts`,
   `tweqx/3301-hash-alarm`. **Expected: 9/9 rejected.**
2. **Rune-hash control.** Before comparing any pulled rune text, feed the held canonical rune
   stream itself through the novelty comparator. It **must** report 0 novel lines. If the
   comparator reports novelty on the corpus it was built from, the comparator is broken and no
   novelty claim from it is admissible. Second control: feed a shuffled/rotated copy of the same
   stream; it **must** report novel lines (i.e. the comparator is not trivially saturating).

## What a HIT would and would not prove

- A retrievable never-ingested corpus proves an **untested haystack exists**. It is not a key.
  The mechanism-level kills (Round 7 keytext kill, the OTP characterisation) still apply to
  anything linguistic found in it.
- The only classes that could move the case: **non-linguistic external data of pad length**
  (≥ ~13k symbols) published by 3301; a **primary statement about key material** from a 2014-era
  insider; or **rune material not in the canonical stream** (which would be the first new
  ciphertext since 2014 and would reopen transcription).

## Budget / scope limits

- ≤20 min per run. No bulk-corpus downloads (full Discord exports, Common Crawl segments) —
  retrievability judged by live metadata + a sample fetch; the ingest is handed off in
  `open_residue` with a resumable script.
- Write only under `analysis/round10/L6-archives/`. No git. No edits to any existing file.
