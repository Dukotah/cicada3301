# PICKUP-HERE — where we left off (updated 2026-06-20)

Resume point for the Cicada 3301 / Liber Primus work. Repo is public at
https://github.com/Dukotah/cicada3301 (default branch `master`).

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
