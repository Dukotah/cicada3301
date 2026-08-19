# Lane H — branch recovery. **101 files recovered, and four armadas were already overlapping.**

_Run by the lead, 2026-08-19, concurrently with Lanes A–G. Extraction, not merge — see §4._

## 1. What was recovered

**101 unique files, 1.53 MB**, present on unmerged branches and **absent from the `master`
working tree**, extracted with full provenance to `corpus/H-branch-recovery/recovered/` and
manifested in `RECOVERED.json` (per file: original path, sha256, bytes, source branch, branch
tip commit, and any other branch carrying identical content).

| source branch | files |
|---|---|
| `claude/master-roadmap-libra-qk527u` | 46 |
| `claude/cicada-3301-scope-cigxzi` | 24 |
| `research/round-8-artifact-provenance` | 9 |
| `research/round-9-stylometry-exclusion` | 8 |
| `research/round-11-dqt-matrix-disambiguation` | 6 |
| `research/round-10-exclusion-power-corrected` | 5 |
| `research/round-12-external-status-sweep` | 3 |

Highlights: **Campaign XV** (`campaign15/`, 23 files) · **Campaign VII** (`campaign7/`, 32
files) · `research/experiments/` (the pre-registered r8–r12 tree) · `PAGE-MAP.md` ·
`NEGATIVE-RESULTS.md` · `MASTER-ROADMAP.md` · `OPEN_QUESTIONS.md` ·
`EXTERNAL-STATUS-2026-08.md` · `ARTICLE-DRAFT.md` · `sources/community/` (10 files).

## 2. ⚠️ THE FINDING: four lanes were run twice, or were about to be

**Campaign XV** (dated 2026-07-23, stranded on `claude/cicada-3301-scope-cigxzi` ever since)
executed a 9-probe armada — each probe pre-registered, gated on synthetic ground truth, with a
reproducible script. Several of those probes are items the **current `LEDGER.json` still marks
`never-run`**, because the ledger was built from `master`, which cannot see this branch.

| Campaign XV probe | verdict | RECON-A item | ledger status **today** | consequence |
|---|---|---|---|---|
| **P5** generator-fingerprint | soundness-confirmed, null-closed, max \|z\| = 1.51 | **D-01** | `never-run` | Round 15 CAMPAIGN-PLAN Lane 5 proposed running D-01. **Already done.** |
| **P7** LP2-as-pad inversion | null-closed | **F-01** | `never-run` | Round 15 CAMPAIGN-PLAN **Lane 4 was entirely this**. **Already done.** |
| **P9** RSA re-score | null-closed — 0 RSA-structure matches in 12 `pow(s,e,n)` tests vs 2 authentic 4096-bit Cicada moduli | **E-01** | `never-run` | Round 15 Lane 5 proposed it. **Already done.** |
| **P2** payload-as-PRF-seed | null-closed, best −7.44 over 480 configs | **B-05** | `negative` (Round 13) | **We ran it twice.** Round 13 B-05 (70,680 decodes, best −6.745) independently redid Campaign XV P2. |

**So the overlap concern raised earlier was not hypothetical — it had already happened four
times, and the cause was branch-stranded work, not bad planning.** The ledger was accurate
about `master`; `master` was not accurate about the project.

Note the two independent runs of the payload-as-PRF hypothesis **agree** (both null-closed,
both far below their gates). That is a genuine, if expensive, replication — and it is the only
silver lining here.

## 3. Also recovered: a research programme `master` knows nothing about

`research/experiments/` holds a pre-registered r8–r12 chain on **artifact provenance**, wholly
distinct from master's Rounds 8–12:

- **r8-01** ICC-profile interior parse — NEGATIVE: ICC is stock Ghostscript sRGB, no operator data
- **r8-02** DQT page-membership — INCONCLUSIVE
- **r9-01** Burrows-Delta stylometry exclusion — **marked INVALID by its own authors: "tested the wrong quantity"**
- **r10-01** corrected stylometry exclusion — NEGATIVE, lane closed (measured, not cited)
- **r11-01** DQT matrix disambiguation — **SURVIVES (benign)**: the DQT split is a grayscale-vs-colour encode artifact, not content. This *resolves* r8-02.
- **r12-01** external status sweep — NEGATIVE

The r9 → r10 sequence is worth preserving on its own merits: a lane that caught its own
invalid gate and re-ran it corrected. That is the discipline this repo claims, evidenced.

## 4. Why this is an EXTRACTION and not a merge

**A round-numbering collision makes a naive merge unsafe.** `master` has Rounds 8–12 =
SEED / GEOMETRY / PAYLOAD / SKELETON / POINTERS. The branches have Rounds 8–12 = ICC parse /
DQT / stylometry / external sweep. Same numbers, different programmes. Merging would silently
conflate them and corrupt every cross-reference in `LEDGER.json` and `DEAD_ENDS.md`.

Recommended before any merge:
1. **Renumber** the branch programme — it is chronologically earlier; `provenance-r1..r6` or
   similar, with a mapping table.
2. **Verify before trusting.** These results are recovered, not re-run. Campaign XV's probes
   should be re-executed against the current benchmark gates before their verdicts are
   promoted into `LEDGER.json` — several predate the discovery that **rigid decoding scores
   the correct key as noise**, and P1's own headline is a *skip-aware* DP decode, so the
   suite may well be sound. That needs checking, not assuming.
3. **Then** add ledger entries with `source_branch` provenance, and flip D-01, F-01 and E-01
   off `never-run`.

## 5. Immediate consequence for the live plan

`liber-primus/analysis/round15/CAMPAIGN-PLAN.md` should be revised: **Lane 4 (F-01) and two
of Lane 5's five items (D-01, E-01) are already executed.** Round 15's remaining genuinely
un-run content is the KDF lane (Lane 1, gated and ready), A-03 haplography (Lane 2), the
matched scorer (Lane 3), and the rest of Lane 5 — A-06 ornament bands, C-02 forcing detector,
G-02 OutGuess blank control, H-01/H-03 micro-crosses — plus Lane 6 PHP `mt_rand`.

## 6. Method note for the corpus operation

This is the single strongest argument for Phase 0. Seven branches sat in plain sight in
`git branch -r` for weeks. Nothing was corrupted or lost — but the work was **invisible from
where everyone was standing**, and the project spent real compute rediscovering it.

`CLAUDE.md` already forbids branches for exactly this reason, and documents an earlier
instance where a split made 100 Python sources look permanently lost. **The rule was right and
was not being followed.** The `corpus-sweep` branch this operation runs on should be merged
back promptly rather than becoming the eighth exhibit.
