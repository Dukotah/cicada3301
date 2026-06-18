# PICKUP-HERE — where we left off (paused 2026-06-17)

Resume point for the Cicada 3301 / Liber Primus work. Repo is public at
https://github.com/Dukotah/cicada3301 (default branch `master`).

## TL;DR state
- The **solvable** Cicada puzzles (2012, 2013, early Liber Primus pages) are
  reconstructed and the cryptanalysis rig is validated (`liber-primus/tests/validate.py`).
- The **unsolved** LP2 pages (0–55) are proven one-time-pad-class: exhaustively
  attacked and ruled out (see `liber-primus/FINDINGS-FOR-SOLVERS.md`).
- We were running **4 "move-the-needle" avenues**. Three are DONE. One is PAUSED.

## The 4 avenues
| # | Avenue | Status |
|---|---|---|
| 1 | Independent **vision re-transcription** of the 56 page images | ⏸ **PAUSED mid-run — resume here** |
| 2 | Doublet-avoidant / fractionation attacks | ✅ closed (ruled out) — `analysis/OPEN-AVENUES.md` |
| 3 | Contribute findings to community | ✅ shipped — `FINDINGS-FOR-SOLVERS.md`, repo public |
| 4 | OSINT for the lost deep-web hash page | ✅ done — `analysis/DEEPWEB-HASH-OSINT.md` (trail cold) |

## ▶ HOW TO RESUME AVENUE #1 (the only unfinished work)

**Goal:** independently re-read the runes off each page image via AI vision and
diff against the canonical text. The canonical transcription is *unverified*
(two "independent" sources are actually one shared origin), so a systematic
mis-read would silently break every attack. This is the one avenue with real
upside.

**Steps next session (needs more tokens — 56 vision agents is heavy):**

1. Re-download the page images (gitignored — not in the repo):
   ```bash
   cd liber-primus/data/relikd
   for i in $(seq 0 55); do curl -sL -o p$i.jpg \
     "https://raw.githubusercontent.com/relikd/LiberPrayground/main/pages/p$i.jpg"; done
   ```
2. Re-launch the vision workflow. The script is saved on disk:
   `C:\Users\dukot\.claude\projects\C--Users-dukot-projects-cicada3301-liber-primus-data-relikd\8aab5c46-ac39-4968-8bef-1b278089e169\workflows\scripts\lp-vision-retranscribe-wf_4a77277f-8e6.js`
   - Same session only: resume with `resumeFromRunId: "wf_4a77277f-8e6"` (cached agents return instantly).
   - New session: just re-run the saved script fresh (it re-does all 56 pages).
3. Diff each agent's transliteration against the canonical per-page runes from
   `liber-primus/data/krisyotam_runes.txt` (split on `%`; map runes→letters with
   `src/lp/gematria.py`). Use `difflib.SequenceMatcher` and flag disagreements.
4. **Critical:** AI vision has its own error rate. Do NOT trust a flagged
   disagreement — re-read that specific rune at high zoom (crop the image with
   PIL and Read the crop). Only a high-confidence, repeatable disagreement is a
   real candidate transcription error.
5. If a real error is found → re-run `liber-primus/attack.py` on the corrected
   page (the rig is ready). If all pages match → canonical is verified; that
   itself is a publishable first.

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
