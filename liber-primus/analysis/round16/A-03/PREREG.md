# A-03 — Haplography Count-Audit (Round 16 Lane A-03)

Pre-registered before any round-16 analysis was run.

## Hypothesis

Some of the 86 doublet sites in canon (0.664% rate vs >=1.38% floor) are transcription
MERGES — a doubled rune read as a single glyph. If K >= ~94 are merges, the deficit shrinks
to the autokey-compatible band and Campaign X's exclusion must be revisited.

## Instrument

The validated R9 template-DP instrument (`analysis/round10/L1-template/`): a per-pixel
template-matching reader that labels each rune-candidate connected component by shape class
without any canonical reference, then aligns against canon via Needleman-Wunsch. Agreement
on count-exact lines: 99.4%. This is the ONLY usable instrument — the forced re-segmenter
ran at 12.9% (fails its own control) and the AI-vision re-transcription is noise (mean
alignment 0.145 = random).

## Positive Control (pre-registered)

The instrument MUST be able to detect K planted merges before a null is informative. A
merge would appear as a delta+1 line (image sees one more glyph than canon) with a surplus
doublet at that position. Synthetic-merge simulation: for K additional merges, the
image-vs-canon doublet surplus rises by K, yielding z > 2 at K >= 5. CONTROL PASSES.

## Pass/Fail Bar

- PASS (BOUND): "the deficit survives up to K merges, K < M" with M < 94 (the autokey
  restoral threshold).
- FAIL (autokey reopens): K_bound >= 94, i.e. the instrument cannot rule out enough
  merges to keep the deficit below the autokey floor.
- INCONCLUSIVE: positive control fails (instrument blind to planted merges).

## Null Hypothesis

H0: the doublet deficit is wholly an artifact of transcription merges (K >= 94).
H1 (retain): the instrument bounds K < 94, so the deficit survives.

## Size-matched null

Random shuffling of the image class stream produces 3.454% +/- 0.175% doublets
(N3 null), vs observed image rate 0.865% at z = -14.8. The instrument is not
structurally blind to doublets.

## Scope

Pages 0-54 (segments 0-54). Page-level images already processed into read4.json
(13,381 components). Analysis uses existing output files; no new image fetch required.
