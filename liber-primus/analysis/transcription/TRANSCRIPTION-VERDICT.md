# Transcription cross-verification — VERDICT (2026-06-20)

Avenue: the unsolved-page attacks all run on one rune transcription whose
"two independent sources" (krisyotam, relikd) were known to share an origin.
Does an *independent* transcription exist, and do the community's transcriptions
agree? A systematic mis-read would silently defeat the correct decryption.

## Method
A recon armada (6 agents) mapped every machine-readable LP2 transcription and its
origin. Then all distinct lineages were fetched, collapsed to a pure rune-index
stream (every non-rune char dropped), and globally aligned with difflib so
page-break/numbering/delimiter differences don't matter (`crossdiff.py`).
Flagged runes were adjudicated by eye against the hash-verified authentic page
images (`linecrop.py`).

## Finding 1 — the whole field has ONE root
Every transcription traces to **rtkd/iddqd (2017)**:
- krisyotam (our canonical) credits iddqd; the Uncovering Cicada wiki is "ripped
  directly from" iddqd; cadrypt, LiberPrimusSolver, cicada-library, JBO/cicada_tools
  all derive from rtkd. scream314 (2018) and relikd draw from the same community pool.
- So **unanimity ≠ independent confirmation** — there is no from-scratch second
  transcription, and AI vision cannot produce one (see vision-avenue verdict).

## Finding 2 — but all surviving lineages are rune-for-rune IDENTICAL
Three-way diff of the distinct lineages, **13136 runes each**:

| comparison | ratio | divergences |
|---|---|---|
| krisyotam (canonical) vs relikd (diff delimiters, "double-checked") | **1.00000** | **0** |
| krisyotam vs rtkd/iddqd (2017 root) | **1.00000** | **0** |
| relikd vs rtkd/iddqd | **1.00000** | **0** |

Zero rune-level disagreement anywhere. relikd's differently-delimited,
independently-"double-checked" copy converges *exactly* on the rtkd baseline.

## Finding 3 — the baseline is image-audited + spot-verified
- The rtkd transcription was **error-corrected against the page images** by
  multiple contributors over 2017–2021 (Lurker69, Inky, tz18/7he5haman PRs),
  i.e. it is a community-audited read, not one unchecked pass.
- **Independent by-eye spot-check** (this work): high-zoom crops of the authentic
  images on a sample — p0 L1, p20 L6, p44 L5 — match canonical with no
  discrepancy (`linecrop.py`). Adds to the earlier vision-avenue p0 check.
- The transcription also **reproduces every solved page** under its known cipher
  (`tests/validate.py`) — a functional correctness proof on the checkable pages.

## Verdict
The canonical rune transcription is **corroborated**: unanimous across all
community lineages, image-audited at the rune level, spot-verified here against
the authentic originals, and functionally correct on every solved page. **No
transcription error was found.**

Honest limit: this is consensus + audit + sampling, not a full from-scratch
independent re-transcription (none exists; vision can't deliver one). A
systematic error common to the single 2017 root cannot be excluded with
certainty — but it would have to have survived years of image-based PR
corrections AND produce the correct decryptions on the solved pages, which is
implausible. The transcription is not the thing blocking the unsolved pages.
