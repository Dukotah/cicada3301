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
