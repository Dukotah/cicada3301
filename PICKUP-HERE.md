# PICKUP-HERE — where we left off (updated 2026-07-23)

Resume point for the Cicada 3301 / Liber Primus work. Repo is public at
https://github.com/Dukotah/cicada3301 (default branch `master`).

## 👉 START HERE: `liber-primus/ELIMINATION-LEDGER.md`
The single, complete, reproducible record of **everything tried and why it's
eliminated**, current through **Campaign XV (2026-07-23)**. Read it first — it
supersedes the scattered "ruled-out" tables in the older docs below.

## Latest: Campaign XV — frontier armada (2026-07-23)
A 9-probe armada burned down the standing red-team agenda. **No break (expected for
OTP-class), but the two biggest soundness caveats are now discharged and 5 new families
closed.** See `liber-primus/analysis/CAMPAIGN-XV-FINDINGS.md`; scripts in `analysis/campaign15/`.
- **Rigid-alignment caveat DISCHARGED (P1):** a skip-tolerant filter-aware beam decoder
  (validated: recovers a plant at −4.28/97.4%, and shows the *correct* key decoded rigidly
  through a skip filter collapses to −7.47) ran 2,876 skip-aware decodes over the attested
  generators + 21 cached keytexts → 0 clear −5.2. The ~112 prior keystream/keytext nulls are
  now sound against filter-perturbed alignment.
- **Hand-generated-pad loophole CLOSED (P5):** generator fingerprinting = full conformance to a
  memoryless machine rejection-sampler (max |z|=1.51; the suite catches a shuffle-bag at ≈−23σ).
- **OTP MODEL-CLASS-VERIFIED (P8):** LP2 sits inside a 1,000-member filtered-uniform control band
  on every compression/context predictor; English fires at the 0th percentile. No structure
  survives the two constraints.
- **New named nulls:** payload-as-PRF-seed (P2), payload-as-RSA under Cicada's *real* 4096-bit
  moduli (P9, `analysis/campaign15/cicada_pubkey.asc` now in-repo), surjective 29→k homophonic
  (P6), LP2-as-pad inversion (P7), doublet side-channel (P4), word-length skeleton over the
  on-disk corpus (P3).
- **Frontier now:** essentially ONE external avenue — an untried already-public keytext over the
  **full** 112-text corpus (needs a box with open outbound HTTPS to re-fetch; this session's proxy
  blocks gutenberg/archive/wikisource), then re-run through the P1 skip-beam + P3 skeleton matcher.
  Plus the cold "AN END" deep-web page. Everything ciphertext-internal is closed to model-class.

## What happened since the 2026-06-20 snapshot (Campaigns VII–XI)
The four "avenues" below were the state as of June 20; work then continued:
- **Campaign X (positive result):** simulated the community's decade-old
  autokey/autoclave hypothesis and **excluded it** — all autokey variants sit at
  the ~3.4% random doublet band; the observed 0.66% deficit is reproduced only by an
  OTP with an active no-repeat filter. `liber-primus/analysis/CAMPAIGN-X-FINDINGS.md`
- **Campaign XI:** quantified that filter — **soft, ~83% suppression** (sharpest
  description yet of the one engineered feature); alt-base (59/61/62/64) readings of
  the pp49–51 digits used as key over the runes = null.
  `liber-primus/analysis/CAMPAIGN-XI-FINDINGS.md`
- **Campaigns VII/IX:** fully characterized the non-runic **pp49–51 base-60 payload**
  (2048-bit high-entropy blob — not prime/RSA/key/text; structural leads all null).
- **Campaigns III–VI, VIII:** transcription verified 3 ways (glyph classifier 99.2%);
  no public external key exists; no named author attributable.
- **Net:** still no break (expected for OTP-class), but the mechanism is now described
  to a parameter and appears ahead of the published community state of the art.

## 📄 Community deliverable
**`liber-primus/SOLVERS-DOSSIER.md`** = the consolidated solver-facing contribution
(verified provenance, full ruled-out map, verified-positives, open threads, tools).
Final crypto-rigor probes: `liber-primus/analysis/crypto_rigor.py` + `analysis/CRYPTO-RIGOR.md`
(F-run histogram, transposition-validity, no-repeat decodes — all closed).

## TL;DR state
- The **solvable** Cicada puzzles (2012, 2013, early Liber Primus pages) are
  reconstructed and the cryptanalysis rig is validated (`liber-primus/tests/validate.py`).
- The **unsolved** LP2 pages (0–55) are proven one-time-pad-class: exhaustively
  attacked and ruled out (see `liber-primus/FINDINGS-FOR-SOLVERS.md`).
- All **4 "move-the-needle" avenues are now CLOSED.** (#1 was the last open one;
  closed 2026-06-20 — see below.)

## The 4 avenues
| # | Avenue | Status |
|---|---|---|
| 1 | Independent **vision re-transcription** of the 56 page images | ✅ **closed 2026-06-20** — not viable; canonical verified — `liber-primus/analysis/vision/AVENUE-1-VISION-VERDICT.md` |
| 2 | Doublet-avoidant / fractionation attacks | ✅ closed (ruled out) — `analysis/OPEN-AVENUES.md` |
| 3 | Contribute findings to community | ✅ shipped — `FINDINGS-FOR-SOLVERS.md`, repo public |
| 4 | OSINT for the lost deep-web hash page | ✅ done — `analysis/DEEPWEB-HASH-OSINT.md` (trail cold) |

## ✅ AVENUE #1 — what happened (closed)

Ran the full 56-agent vision armada (one Sonnet agent per page, blind reads).
**Result: vision cannot transcribe these dense ~250-rune pages** — mean
alignment vs canonical was only **0.145** (noise). Confirmed canonical is the
correct one, not vision, via (a) `tests/validate.py` reproducing every solved
page from the canonical runes, and (b) a manual high-zoom re-read of p0 matching
canonical exactly. No transcription error exists to find. Full writeup +
artifacts: `liber-primus/analysis/vision/` (`AVENUE-1-VISION-VERDICT.md`,
`DIFF-REPORT.md`, `vision_results.json`, `build_canonical.py`, `diff_vision.py`).

To reproduce: re-download images (gitignored) then re-run the helpers:
```bash
cd liber-primus/data/relikd
for i in $(seq 0 55); do curl -sL -o p$i.jpg \
  "https://raw.githubusercontent.com/relikd/LiberPrayground/main/pages/p$i.jpg"; done
cd ../.. && python analysis/vision/build_canonical.py   # ground truth
# armada writes analysis/vision/vision_results.json, then:
python analysis/vision/diff_vision.py                   # DIFF-REPORT.md
```
Only conceivable revival = per-rune cropping (~13k individual high-zoom reads) —
cost-prohibitive, documented but not executed.

## ✅ AVENUE #5 — Image steganography (NEW, run + closed 2026-06-20)

Asked: do the LP2 page images carry stego (like Cicada's 2012/2013 images)? Never
examined here before. Result: **no recoverable image stego.** Highlights:
- **Provenance proven:** our circulating images are byte-authentic — **56/56 SHA1
  match** the archive.org `ky2khlqdf7qdznac.onion` onion7 hashes (first published
  verification). They're 400-DPI Ghostscript/Artifex renders ⇒ not OutGuess carriers.
- No appended-data (0 trailing bytes/56), no EXIF/COM, carve = validated-clean,
  LSB = lossy-noise, red/black color = **relikd solver annotation** (dead).
- OutGuess: 30/33 LP2 pages **empty**; 3 give capacity-length (58152 B) entropy-7.997
  false-positives that share a **1417-byte prefix** — most likely OutGuess default-key
  keystream over the pages' shared blank margins (artifact, not payload).
- Full writeup: `liber-primus/analysis/stego/STEGO-VERDICT.md` (+ `stego_scan.py`,
  `provenance.json`). **Not 100% closed:** the decisive control needs OutGuess 0.2 on
  a Linux env (no WSL/Docker/compiler on this box) — see verdict §"decisive next experiment".

## ✅ AVENUE #6 — Transcription cross-verification (NEW, run + closed 2026-06-20)

Re-attacked the "canonical transcription unverified" question the right way (after
AI vision failed). Recon armada mapped every machine-readable LP2 transcription:
**the whole field has ONE root — rtkd/iddqd (2017)** (krisyotam credits it, the
wiki copies it, cadrypt/LiberPrimusSolver/cicada-library/JBO derive from it). So
unanimity ≠ independence. BUT a 3-way rune-stream diff (`analysis/transcription/crossdiff.py`)
shows all distinct lineages — krisyotam (canonical), relikd (diff delimiters,
"double-checked"), rtkd (root) — are **rune-for-rune IDENTICAL: 13136/13136, 0
divergences**. Plus the rtkd baseline was image-audited via PRs (2017–21), I
spot-verified p0/p20/p44 lines by eye against the authentic images (`linecrop.py`),
and it reproduces all solved pages. **Verdict: canonical corroborated; no
transcription error found** (full writeup `analysis/transcription/TRANSCRIPTION-VERDICT.md`).
Limit: not a from-scratch independent re-read (none exists; vision can't deliver one).

## Other live (long-shot) thread, if wanted
- **CT-logs brute force** for the "AN END" deep-web hash (avenue #4 tail): hash
  early-2014 Certificate Transparency log entries against
  `36367763…c2a8b4` across the candidate algorithm set (tweqx/dwh-check).
  Low odds; documented in `analysis/DEEPWEB-HASH-OSINT.md`.

## Key files
- `liber-primus/FINDINGS-FOR-SOLVERS.md` — what's eliminated + why (start here)
- `liber-primus/analysis/OPEN-AVENUES.md` — ranked remaining avenues
- `liber-primus/attack.py` — validated attack CLI (`selftest` re-finds DIVINITY)
- `liber-primus/tests/validate.py` — proves the rig on all solved pages

## Do NOT re-run (proven dead)
More key texts, keywords, keystreams, autokey, differencing, page-keying,
fractionation, transposition-only. All eliminated with reasons recorded.
