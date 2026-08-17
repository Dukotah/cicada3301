# PICKUP-HERE — where the work left off

_Updated **2026-08-17**. Repo: https://github.com/Dukotah/cicada3301 (default branch `master`)._

## 👉 Start with the canonical docs
| Doc | What it holds |
|---|---|
| [`liber-primus/FINAL-SYNTHESIS.md`](liber-primus/FINAL-SYNTHESIS.md) | The terminal verdict on both goals — solve and attribution |
| [`liber-primus/ELIMINATION-LEDGER.md`](liber-primus/ELIMINATION-LEDGER.md) | Everything tried and why it's eliminated — supersedes every scattered "ruled-out" table |
| [`liber-primus/analysis/README.md`](liber-primus/analysis/README.md) | Map of all 183 analysis scripts → campaign → finding |
| [`research/LEDGER.md`](research/LEDGER.md) + [`research/DEAD_ENDS.md`](research/DEAD_ENDS.md) | The 2026-08 pre-registered attack loop — Rounds 1–8, each with its kill reason |

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

**Since then (2026-08), an eight-round pre-registered attack loop closed the last lanes** —
including the two threads this doc previously listed as open. The OTP characterisation is now
backed by a direct measurement of key **entropy**, not just by the absence of key structure.

## The 2026-08 attack loop — Rounds 1–8

Each round was **pre-registered** (hypothesis + pass/fail threshold written before the run) so a
negative result means something. Full detail: [`research/LEDGER.md`](research/LEDGER.md),
kill reasons in [`research/DEAD_ENDS.md`](research/DEAD_ENDS.md).

| Round | Hypothesis tested | Verdict |
|---|---|---|
| 1 | The doublet deficit is an interrupter artifact | **NEGATIVE** — it is intrinsic |
| 2 | A period-locked fractionation signature exists | **NEGATIVE** |
| 3 | Differencing/DP decode can be anchored | **KILL at Gate #1** — un-anchorable; ciphertext-only program COMPLETE |
| 4 | An external key/seed or a verifiable author identity exists | **NEGATIVE** — cold |
| 5 | Residual doublets carry digraphic/autokey/interleave structure | **NEGATIVE** |
| 6 | Misfiled plaintext windows / transition-lattice structure | **NEGATIVE** — the no-repeat rule is a *pure lag-1 identity*, no second-order structure |
| 7 | Some untried public keytext is the key | **KILL, 0/15 unanimous** — any keytext dies both rigidly (doublet-excluded) and skip-aware (un-anchorable), *independent of which text* |
| 8 | Five never-tested axes (below) | **NEGATIVE ×5** |

**Round 8 in detail** ([`research/ROUND-8-RESULTS.md`](research/ROUND-8-RESULTS.md)) — these were
the axes that were never ciphertext-only attacks at all, so "ciphertext-only complete" had never
actually covered them:

- **SEED** — is the pad a seeded PRNG? 10 validated generators (glibc/MSVC/MT19937/CPython/Java,
  each reproduced exactly against the real library) × both directions × every unix-second seed
  2011–2015 = **2.52 × 10⁹ decodes, 0 hits**, best −13.13 (= the null max); plus 15,408
  lore/string/date-seed decodes, 0 hits. → `analysis/seed_sweep/`
- **GEOMETRY** — these are 400-DPI renders of a *typeset* document and only FILE-level stego had
  ever been swept. Glyph-shape substitution is dead (median nearest-neighbour Hamming distance
  **0.0000** — the median glyph has a pixel-identical twin); micro-spacing is 1.86σ unimodal;
  baseline jitter fails BIC. → `analysis/geometry/`
- **PAYLOAD** — "flat IoC" is blind to a compressed/binary plaintext. 166 representations scanned
  for magics/armor/inflate: nothing; byte histogram exactly uniform (χ² 246.7 / 255 df).
- **SKELETON** — word length is a cleartext invariant no pad touches, so a known text could be
  identified as the *plaintext* without a key. FFT scan of every offset across 51 texts / 8.2M
  words: best 20.0% vs a shuffled control's 19.8%. Negative **for that corpus**; the tool is built
  to extend. → `analysis/skeleton/`
- **POINTERS** — the 86 residual doublets read as a book-cipher index: every reading sits inside
  the random null.

**AN-END hunt CLOSED (2026-08)** ([`liber-primus/analysis/anend_hunt/FINDINGS.md`](liber-primus/analysis/anend_hunt/FINDINGS.md)) —
the lost deep-web page is **unreachable by construction**: its address is gated behind solving
OTP-class LP2 0–54 (the 2014 chain grammar is "each onion's solved content yields the next
address"), `gy3hoy2…onion` is a debunked hallucination, no genuinely-retrievable in-scope Tor-v2
corpus exists, the held corpus hashes null across representations (2,706 tests), and the 2026
community status is a sourced negative. **The only remaining door is solving LP2 0–54 —
cryptanalysis, not OSINT.**

## Round 9/10 — multi-lens armada (2026-08-11 → 17)

A fresh, wide 22-lens re-attack (distinct from the `research/round-1…8` sequence), run
across the plaintext/word, keystream/pad, and external/provenance fronts — each lens
pre-registered with a positive control and a size-matched null. The window crashed
mid-run; it was recovered, finished, and synthesized on 2026-08-17.
Full detail: [`liber-primus/analysis/round10/SYNTHESIS.md`](liber-primus/analysis/round10/SYNTHESIS.md).

**Zero hits across all lenses — the OTP / unsolvable-by-design verdict holds and is
hardened.** The value is three things, not another null:

1. **Two prior claims corrected** (marked as superseding in the synthesis):
   - *"Flat IoC forces a full-length key"* is **false** — the smallest IoC-invisible period at
     N=12,956 is **p\*≈400**, not 12,956. The OTP conclusion rests on the **doublet** argument,
     not IoC.
   - *"OTP"* is really **one member of a ciphertext-indistinguishability class**: a SHA-256
     counter-mode derived key + filter, and ciphertext-autokey over flat non-English plaintext,
     both pass the full statistics battery inside the external-pad model's band (no statistic
     separates them at |z|>2.93). State it as OTP-*class*, not a unique external pad.
2. **The transcription got a 4th, genuinely-independent audit** (label-free glyph clustering,
   not canon-trained): 96.93% agreement, clean 29→29 bijection, **no reopener** — every
   disagreement is a DP artifact or a misread on an already-*solved* page. Bounded: only 38.4%
   of lines were glyph-diffable, and the OTP pages are where the read is weakest.
3. **The doublet-deficit argument was stress-tested from both sides** (B4/G3 hardens it — the
   plaintext-independent floor is 1.50% > observed 0.664%; RECON-B/B-16 objects that the soft
   anti-repeat filter, not the key, sets the rate) and **reconciled**: the deficit excludes
   *rigid* plaintext-independent keys; the anti-repeat-aware decoders exclude the rest to the
   audited limit of their power.

**One genuinely-new untested input surfaced (PA-3):** the author's own ~4 MB binary pads from
the 2013 CicadaOS (`DATA/_560.*`, `761.mp3`⊕`twitter.txt`) — period-correct key material she
demonstrably used — have **never been fed under the skip-aware decoder**. Not held in-repo;
would need fetching. It is the highest-prior remaining input, though still low absolute prior.

## What the 2026-07 sessions did

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

_Superseded 2026-08. The two threads this section used to list — "an untried public keytext" and
"the AN END page" — were **both closed by mechanism** in Rounds 7–8. A new keytext is no longer a
lead on its own (any keytext is dead independent of which text it is), and the AN END page is
unreachable by construction._

What is left is **external and low-prior**. Nothing in the ciphertext can close any of it:

1. **A signed or archival pointer** that a specific text *is* the key — i.e. evidence from outside
   the ciphertext, not another text to try.
2. **A correctly-targeted, locally-held archive** that could contain the lost AN END page.
   (Residual activity here = passive monitoring only; the active hunt is closed.)
3. **The author's own binary pads (PA-3, 2026-08)** — the 2013 CicadaOS `DATA/_560.*` files and
   the `761.mp3`⊕`twitter.txt` pair, period-correct key material Cicada demonstrably used, never
   fed under the skip-aware decoder. Not held in-repo; needs fetching. Highest-prior *input*
   remaining (still low absolute prior). → `analysis/round10b/PA-3/ARTIFACT-INVENTORY.md`
4. **RECON-C** — a pre-registered, resumable community-archive fetch (cijhho insider tree, Reddit)
   deliberately deferred, not a crash. Cheap to run. → `analysis/round10/RECON-C/`

_Superseded by Round 9/10:_ the **32-bit seed sweep** (Round 8 loose end) is now **parked with
cause** — L5-seed32 proved the pre-registered threshold is statistically invalid at full-32 scale,
so completing it is a "completeness ritual" (do not resume without a scale-corrected threshold from
`nullcurve.py`). The **SKELETON corpus extension** ran as L4 against 224 texts / 22.6M words:
**negative** (best 22.7% match, z=−1.03, inside the null band).

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
| 4 | OSINT for the lost deep-web hash page | ✅ **closed 2026-08** — unreachable-by-construction; `analysis/anend_hunt/FINDINGS.md` |

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
