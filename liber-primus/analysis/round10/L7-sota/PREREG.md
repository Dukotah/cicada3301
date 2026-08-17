# L7-sota — PRE-REGISTRATION

Written **before** any web query was issued. Round 10, lane L7 (community state of the art,
current as of 2026-08-12).

## Hypothesis

H1: Something exists **outside this repo** — published between the last in-repo status check
(anend_hunt FINDINGS, 2026-08; FRESHNESS-2026-07-29; Campaign XIII 2026-07) and today
(2026-08-12) — that the repo does not have, and that materially changes the LP2 verdict.

H1 decomposes into four independent sub-hypotheses, each with its own gate:

- **H1a (release):** a new Cicada 3301 message exists that verifies against PGP key
  **0x181F01E57A35090F**.
- **H1b (solve):** a claimed LP2 (segments 0–54) solve exists that CicadaSolvers or an
  equivalent body accepts as **reproducible**, i.e. published METHOD + plaintext, not an
  announcement.
- **H1c (statistic):** a published, sourced statistic on the unsolved corpus **contradicts**
  this repo's measurements: IoC·N = 1.000 (raw IoC 0.0345 on 29 symbols), doublet rate
  0.66% observed vs 3.45% random, soft anti-repeat p_keep ≈ 0.18.
- **H1d (tool):** a public tool/harness has a **capability this repo's rig lacks** (not merely
  a reimplementation in another language, not merely faster).

H2 (the question nobody asks): has **anyone independently reached the OTP / external-pad
conclusion** for LP2? If yes, cite them and record priority. If no, record that the repo's
central finding is, so far as public sources show, unique.

## Exact test

WebSearch + WebFetch sweep, minimum 20 distinct queries, over:
(a) 3301 signed-release channels and signature-verification trackers;
(b) CicadaSolvers (site, Discord-adjacent public pages, GitHub org `cicada-solvers`),
    r/cicada, uncovering-cicada wiki, Boxentriq, Tumbleson's blog;
(c) arXiv / Zenodo / OSF / Semantic Scholar / Google Scholar / ResearchGate / thesis
    repositories, for formal treatment of LP2 or its cipher class;
(d) GitHub/GitLab for LP tooling with commits in 2025–2026;
(e) explicit searches for the OTP / one-time-pad / unbreakable-by-design framing, and for
    the anti-repeat / doublet-suppression statistic, by anyone other than this repo.

Every candidate is graded against the gate below. Every dismissed item is logged with a
one-line reason so the next cycle does not re-check it.

## Pass / fail thresholds (fixed in advance)

**HIT** requires **at least one** of:
1. A message with a **verifiable 7A35090F signature** dated after 2017-04, reported by a
   source that states the signature was checked. (Note the standing downgrade from
   FRESHNESS-2026-07-29: post-SHAttered, a valid signature is *necessary but not sufficient*
   — corroboration required. A signed message still counts as a HIT for this lane, flagged.)
2. A solve claim where (i) a method is published in enough detail to re-implement, AND
   (ii) a named community body or ≥2 independent third parties report reproducing it.
3. A published numeric statistic on the same corpus that falls **outside** these tolerances:
   IoC·N 1.000 ± 0.05 (raw 0.0345 ± 0.0017), doublet rate 0.66% ± 0.30pp. A number outside
   tolerance from a source that states its corpus and method = contradiction = HIT.
   (A number outside tolerance whose corpus is unstated or clearly different — e.g. includes
   solved pages, or LP1 — is NOT a contradiction; it is a scope difference, logged as null.)
4. A tool that performs an operation the repo's rig cannot perform at all — enumerated
   candidate capabilities: joint interrupt-mask × key optimisation at scale, neural/LLM
   plaintext scoring integrated into search, a from-images OCR pipeline, a public keytext
   corpus larger than this repo's, or any attack on a cipher class the ledger has not
   modelled.

**NULL** (explicitly): YouTube videos, Medium/Substack posts, unsigned "I solved it" claims,
AI-generated "translations" (Zenodo/OFELLIA class), ransomware/name-squat "Cicada3301",
Schoenberger self-attribution (unsigned, contested, litigated — do not launder), reposts of
already-known 2013–2017 material, and any tool that is a port/rewrite of an existing solver.

**NEGATIVE verdict** = ≥20 queries executed across all five source classes with zero HITs.

## Null control

Two, since this is a search lane and the failure mode is "any search returns *something*":

- **NC1 — decoy-query control.** Issue queries for events that certainly did NOT happen
  ("Liber Primus page 42 solved 2026", "Cicada 3301 signed message August 2026", "Liber
  Primus one-time pad proof published"). If these return the *same class* of confident-looking
  results as the real queries, the search channel is producing noise and no positive from it
  is trustworthy. Expectation: decoys return SEO chaff / unrelated pages only.
- **NC2 — known-negative recall.** Re-issue the queries that produced the repo's already-known
  items (Zenodo 18199474 / OFELLIA, the Katayama SHA-1 forgery paper, Cicada-DWH-HashcatAttempts).
  If the sweep fails to re-find things known to exist, the sweep has insufficient recall and a
  null is uninformative. Expectation: all three re-found.

A NEGATIVE is only reportable if NC1 comes back clean AND NC2 recalls ≥2 of 3.

## Known-scope warning recorded in advance

The last in-repo external check is dated 2026-08 (anend_hunt) — **days** before this run. A
window that short cannot, by construction, contain much novelty. This lane's value is therefore
weighted toward (c) literature, (d) tooling capability comparison, and H2 (independent-OTP
priority) — the three things prior checks did *not* do systematically — rather than toward
"is there news since last week."

## Artifacts to be produced

- `PREREG.md` (this file)
- `FINDINGS.md` — verdict, the graded table, sources with dates
- `NULLS.md` — every dismissed item, one line each, so nobody re-checks it
- `queries.log` — the query list actually executed
