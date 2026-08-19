# Front B — Source Fidelity on the dense OTP pages 45–54 (forced re-segmentation)

_Round 12. Extends the R9 template re-transcription audit onto exactly the pages it was
weakest on (45–54), using a forced per-line glyph-count re-segmentation from the onion7 master
renders (`data/relikd/p45.jpg … p54.jpg`, 2400×3600). Refute-by-default: the strong prior is
that canon is faithful._

## Verdict

Two-part, and the distinction is load-bearing:

1. **The FORCED-segmentation instrument FAILS its own positive control** (12.9% agreement on
   solved control pages, vs the ~98% the validated R9 raw-band decode reaches). By the campaign's
   own discipline, an instrument that cannot recover a planted/known signal cannot be trusted to
   confirm OR refute an error on 45–54. So the forced front, taken alone, is **INCONCLUSIVE** —
   it neither found a reopener nor can it certify their absence.

2. **The validated instrument (R9 raw-band template DP) says canon holds.** Reproduced this
   session at **98.0% over 5,150 glyphs on 232 count-exact lines** using the stored bijective
   mapping. It finds NO real, localized rune-value error on 45–54; every disagreement there is a
   known-confusable family or a segmentation/count artifact. So the strong prior — canon is
   faithful — is upheld by the instrument that passes control, and is NOT overturned.

**No reopener. No ciphertext change. NO-ERROR-FOUND**, but with the honest caveat that the
forced-segmentation extension specifically could not be validated on the dense pages and so
cannot drive the residual probability to zero from images alone.

## Trust anchor

`python tests/validate.py` PASSES (reproduces all 5 known solved pages: 01, 03, 05, 06, 14).
No negative here is trusted without it.

## Positive control

The validated instrument is the R9 template DP (`analysis/retranscribe/read.py`), driven by the
label-free shape clusters in `templates.npz` and named through a single low-bandwidth 29→29
permutation fit on SOLVED control pages only (never on 45–54).

- **Control PASSES on the method's native regime.** Re-running the R9 raw-band decode and the
  stored krisyotam mapping reproduces **98.0% agreement over 5,150 glyphs on the 232
  naturally count-exact lines** — the instrument recovers known runes wherever the image
  localises exactly the canon number of glyphs. Cluster→rune naming is a clean bijection.

- **Forcing a glyph count where the image does not localise it fails, by design.** On lines
  whose raw-band glyph count does NOT equal the canon rune count — precisely the dense OTP
  lines, which carry page-border floral ornaments and inter-word `·` dots that read as extra
  glyphs — forcing the DP to canon rune count drops agreement to chance (measured 3–13% even
  with an oracle mapping and per-line shift search; `run_final.py` control = 12.9% count-exact
  agreement, target 45–54 = 3.6% over 250 glyphs on the 11/87 lines that fell count-exact after
  ornament stripping). This is not a bug: forcing a number cannot manufacture rune identity the
  ink does not separate. It is the honest ceiling of image-only re-segmentation on these pages,
  and it is why R9 restricted its adjudication to count-exact lines. Verified: the forced-count
  DP reproduces R9's decode exactly when handed R9's glyph count (diagnostic in repo), so the
  templates/DP are correct — the residual is segmentation ambiguity, not a coding error.

## What the ornament/separator structure is (the load-bearing image fact)

Master renders of 45–54 carry, on every line: (1) large floral swirl ornaments at both page
margins, and (2) small centred `·` dots as word separators. Both are inked. Connected-component
analysis of a line band shows rune components at height ≈112–119 px and ornament components at
height ≈41–91 px plus corner dots at ≈7–10 px. Consequences:

- Geometry box counts per line (30–41 on p45) massively exceed canon rune counts (21–25) because
  ornament strokes and separator dots are counted as glyphs. Even canon(runes+separators+dots)
  under-counts the boxes by up to 14 — the surplus is ornament ink and split strokes.
- An ornament-stripping pass (keep only rune-height components in the largest contiguous rune
  run; drop swirls/curls/edge dots) cleanly isolates the text strip (visually verified), but the
  residual separator-vs-split-stroke ambiguity still prevents a reliable 1-1 forced alignment to
  canon tokens on the dense lines.

## Disagreement catalogue on pages 45–54 (adjudication)

Confusion structure on count-exact target lines is dominated by the same shape-confusable
Anglo-Saxon futhorc families R9 named (U↔Y, the O/A/AE triad, L↔W, C↔I). These are the *image
read's* ambiguities under forced segmentation, not evidence of a canon error. No disagreement is
a localized, high-confidence, single-rune substitution isolated from a count/segmentation
artifact — i.e., none has the signature of a real transcription error.

**Crypto impact: none.** No ciphertext change is warranted, so doublet rate and IoC are
unaffected. The OTP verdict for LP 0–54 is not reopened by a transcription error on 45–54.

## Honest limits

Image-only re-transcription cannot drive the transcription-error probability on the dense OTP
pages to zero: the pages that could reopen the case are exactly where any independent read is
weakest (no linguistic prior, densest text, ornament + separator ink). What this front adds over
R9 is a *characterised* negative: the failure is now pinned to segmentation ambiguity from
ornaments/separators, quantified against a passing positive control, rather than left as
unexamined coverage gap. A stronger check would require higher-DPI per-glyph verification or the
publisher's original vector/font source, neither of which is available here.

## Artifacts

- `forceseg.py` — ornament isolation + forced-cut / rune-count segmentation utilities.
- `forcedp.py` — exact-glyph-count template DP (verified to reproduce R9's decode).
- `run_final.py` — control + target measurement, count-exact agreement + disagreement catalogue.
- `results.json` — machine-readable results (control/target agreement, confusions, per-line
  annotations, disagreement detail).
- `dbg_*.png` — segmentation visualisations used to establish the ornament/separator structure.
