# PICKUP-HERE — where the work left off

_Updated **2026-07-29**. Repo: https://github.com/Dukotah/cicada3301 (default branch `master`)._

## 👉 Start with the three canonical docs
| Doc | What it holds |
|---|---|
| [`liber-primus/FINAL-SYNTHESIS.md`](liber-primus/FINAL-SYNTHESIS.md) | The terminal verdict on both goals — solve and attribution |
| [`liber-primus/ELIMINATION-LEDGER.md`](liber-primus/ELIMINATION-LEDGER.md) | Everything tried and why it's eliminated — supersedes every scattered "ruled-out" table |
| [`liber-primus/analysis/README.md`](liber-primus/analysis/README.md) | Map of all 183 analysis scripts → campaign → finding |

## State in one paragraph

LP2 (unsolved segments 0–54) is **OTP-class**: a full-length keystream filtered to avoid
consecutive-equal runes (soft, ~83% suppression) against an external one-time pad →
information-theoretically unsolvable **without the pad**. The transcription is verified three
independent ways and is **not** the blocker. As of the 2026-07-28/29 auditor loop the internal
attack surface is **closed**, and the verdict has hardened from *unsolved-by-effort* to
**unsolvable-by-design**: the pad appears unpublished by design, since pages 0–54 were the
terminal onion7 deliverable with no accompanying key. On attribution, there is **no falsifiable
name** — stylometry is *provably* impossible at 359 words of authentic connected prose — but the
loop produced the tightest honest **profile** yet, anchored on a technique fingerprint
(Smirnov/Carlitz anti-repeat hardening = a combinatorialist's reflex, applied by hand).

## What the last three sessions did

- **2026-07-27 — OSINT / external-artifact sweep.** Pulled the onion images and HTML never held
  locally from community mirrors (iBotPeaches, archive.org, scream314, krisyotam) and re-extracted.
  **No new key**: T1 and T5 decode to already-known 2013/2016 messages; a 60-key OutGuess sweep was
  null; T2/T3 remain unidentified high-entropy blobs (low prior).
  → `liber-primus/analysis/OSINT-SWEEP-2026-07-27.md`, `analysis/armada_osint/`
- **2026-07-28 — LP1/LP2 recon + Campaign XIX.** Method dossier for the solved section (key
  selection is **semantic, not numeric**), structure dossier for the unsolved one (editorial
  sections exist; the cipher does **not** reset at them), and the full winner/insider roster —
  none of whom holds LP or key material.
  → `analysis/recon/RECON-SUMMARY-2026-07-28.md`, `analysis/attribution/CAMPAIGN-XIX-WITNESSES.md`
- **2026-07-29 — the 11-iteration auditor loop.** A rotating-critic loop (contrarian → naïve
  outsider → author-empathy → historian → data-provenance → lateral-field → game-theorist →
  devil's-advocate believer) that sealed the remaining lanes, **positively refuted autokey**, and
  self-corrected three of its own false positives.
  → `liber-primus/FINAL-SYNTHESIS.md`, `analysis/recon/`, `analysis/attribution/TECHNIQUE-FINGERPRINT-2026-07-29.md`

## If you're picking this up cold

```bash
cd liber-primus
python tests/validate.py     # trust anchor — reproduces every known solved page
pytest -m "not network"      # fast regression gate
```

Then read the ledger. **Do not re-run** anything in its "Do NOT re-run" list — more keywords,
short/periodic keys, number-theoretic keystreams, autokey, differencing/integration, page-on-page
keying, transposition-only, fractionation, substitution/homophonic, image stego, AI-vision
re-transcription, or pp49–51 as a runic key. Every one is eliminated with a reason and a
reproduce pointer.

## What is actually still open

Two things, both **external** — nothing in the ciphertext can close either:
1. **An untried already-public keytext** Cicada expected solvers to recognize. Falsifiable, and
   therefore the one productive avenue left (~200 named texts already eliminated, skip-aware).
   Extend by adding a slug to `analysis/campaign12/fetch_keytexts.py` and re-running `run_sweep.py`.
2. **The "AN END" deep-web page** — the only place the pad might physically exist. Cold trail
   (Tor v2 dead); what remains un-examined is narrow and low-prior.

**What would reopen the case:** a new 7A35090F-signed Cicada release, a CicadaSolvers-accepted
reproducible page solve, or the private pad surfacing.

---

# Historical detail

_Kept for provenance. The avenue log below is from the 2026-06-20 snapshot; where it disagrees
with the ledger, the ledger wins._

## The 4 avenues
| # | Avenue | Status |
|---|---|---|
| 1 | Independent **vision re-transcription** of the 56 page images | ✅ **closed 2026-06-20** — not viable; canonical verified — `liber-primus/analysis/vision/AVENUE-1-VISION-VERDICT.md` |
| 2 | Doublet-avoidant / fractionation attacks | ✅ closed (ruled out) — `analysis/OPEN-AVENUES.md` |
| 3 | Contribute findings to community | ✅ shipped — `liber-primus/docs/FINDINGS-FOR-SOLVERS.md`, repo public |
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
- `liber-primus/docs/FINDINGS-FOR-SOLVERS.md` — what's eliminated + why (start here)
- `liber-primus/analysis/OPEN-AVENUES.md` — ranked remaining avenues
- `liber-primus/attack.py` — validated attack CLI (`selftest` re-finds DIVINITY)
- `liber-primus/tests/validate.py` — proves the rig on all solved pages

## Do NOT re-run (proven dead)
More key texts, keywords, keystreams, autokey, differencing, page-keying,
fractionation, transposition-only. All eliminated with reasons recorded.
