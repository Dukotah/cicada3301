# Independent Re-Transcription Audit — Stage 2/3 Findings

_Round 9 TEMPLATE track. Stage 1 (label-free glyph clustering) done earlier; Stage 2
(decode + audit vs canonical krisyotam transcription) completed 2026-08-17._

**Bottom line:** No reopener. Agreement **96.93%** (5,047 / 5,207 glyphs) on the 232
rune-count-exact lines. Class→rune mapping is a clean **29→29 bijection** (no collapsed or
uncovered runes). Every disagreement is a line-start segmentation artifact, a high-cost
known-confusable in the *image* read (not canon), or a whole-line read failure on the three
near-identical high-entropy OTP pages. **Zero disagreements are real, localized rune-value
errors in canon.** Stage 2 completed but bounded: glyph-level adjudication reliably covers
232/604 lines (38.4%).

## On the circularity critique (Campaign V was criticized as circular)

Cluster identities are fixed **label-free** in Stages 1–2 (deciding which ink blobs are the
same rune uses zero transcription input). Canon enters only to *name* the pre-formed clusters
via a single 29→29 permutation (`linear_sum_assignment`) — low-bandwidth, bijective, and
falsifiable: a systematic canon error would surface as a non-bijective or high-disagreement
assignment, and it did not. This is materially better than the prior classifier that was
*trained* on canon labels. **Honest residual:** the naming step is not fully canon-blind.

## Confusion structure

Dominated by shape-confusable Anglo-Saxon futhorc families — U↔Y, the O/A/AE triad, L↔W, C↔I.
These are the *read's* ambiguities, not canon's.

## Disagreement loci (103 total, three buckets — none a reopener)

- **A — line-start artifact (15 loci, solved pages):** all pinned at position 0, x=601 — the
  same first-glyph column band, page after page. A mechanical DP edge effect, not a per-rune
  error.
- **B — high-cost confusable mis-read on SOLVED pages (3 loci):** p29:336·9, p34:388·9,
  p35:401·18, all `C→I` at very high match cost (871–955 vs median 124). These pages are
  cryptographically solved, so canon is proven correct *by decryption* — the image read is the
  wrong party.
- **C — whole-line read failure on OTP pages 45–47 (85 loci):** exactly four short lines
  (517/529/541/549) that landed in "count-exact" by coincidence. No offset −4…+4 realigns them
  (best 2/22 = chance for two length-22 high-entropy streams); pages 45/46/47 share
  near-identical per-line cost fingerprints. This is the dense-OTP read failing, not canon being
  wrong (median template cost on OTP lines runs 500–1,100 = garbage).

## Crypto impact

**None.** No ciphertext changes, so no effect on doublet rate or IoC. Refute-by-default holds —
canon is faithful within the audit's resolution.

## Limits (what would strengthen it)

Only 38.4% of lines are glyph-diffable (the template DP over/under-segments dense lines), and
the OTP pages that could actually reopen the case are exactly where the independent read is
weakest (no linguistic prior, densest text). This audit **lowers** the probability of a
transcription reopener but cannot drive it to zero on the OTP pages from images alone. A
stronger OTP check would need connected-component-free segmentation (forced per-line glyph-count
alignment) or higher-DPI per-glyph verification.

Artifacts: `diff.py`, `diff_report.json` (new), `read.py`, `read_lines.json`, `templates.py`,
`templates.npz`.
