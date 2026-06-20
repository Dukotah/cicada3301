# Avenue #1 — Vision re-transcription: VERDICT (closed 2026-06-20)

**Goal of the avenue:** independently re-read the runes off each of the 56 LP2
page images via AI vision and diff against the canonical transcription
(`data/krisyotam_runes.txt`). The canonical is "unverified" in the weak sense
that its two supposedly-independent sources share one origin, so a *systematic*
mis-read could in principle have propagated into every attack the rig has run.

**Method:** a 56-agent armada (one Sonnet vision agent per page p0–p55). Each
agent read its page image **blind** — no canonical text shown — matching glyph
shapes against the Gematria Primus chart, transcribing every rune in reading
order, and self-flagging uncertain glyphs. Outputs in `vision_results.json`;
alignment vs canonical computed by `diff_vision.py` (difflib) in `DIFF-REPORT.md`.

## Result: vision cannot transcribe these pages (canonical stands)

- **Mean alignment ratio vision-vs-canonical across 56 pages = 0.145.** The
  vision reads bear almost no resemblance to canonical on *any* page — this is
  noise, not a near-miss with a few correctable errors.
- The 51 "high-confidence candidates" flagged by `diff_vision.py` are an
  **artifact**: the diff heuristic assumed vision would be mostly-correct with a
  few isolated errors. At 14.5% agreement the pages are globally misaligned, so
  per-position "high-confidence disagreement" is meaningless. None are real.

## Why this means *vision* is wrong, not canonical

Three independent lines of evidence, all pointing the same way:

1. **The rig reproduces every solved page from the canonical runes.**
   `tests/validate.py` PASSES: A WARNING (atbash), SOME WISDOM (plaintext),
   A KOAN (atbash+3), WELCOME (Vigenère DIVINITY), CIRCUMFERENCE (Vigenère
   FIRFUMFERENFE). If the transcription were ~85% wrong (as a 0.145 ratio would
   require if vision were right), these decryptions could not validate. They do.
2. **Manual high-zoom re-read.** Cropping p0 line 1 and reading it by hand, the
   black runes after the title-mark are unmistakably `ᚦ ᛄ ᚷ ᚫ` (TH J G AE),
   exactly matching canonical p0 (`…SYENGC.THJGAE…`). The vision agent had
   claimed p0 begins `ᚾᛗᛈᚢᛗᚢᛈ…` (N M P U M U P…) — fabricated.
3. **Internal implausibility.** Two careful transcriptions of the same image
   should agree with *each other* far above 14.5% even if both were imperfect.
   A 0.145 ratio is the signature of one side confabulating.

## Root cause

A page holds ~250 dense runes with several near-identical glyph pairs
(ᚦ/ᚩ/ᚹ, ᛒ/ᛖ, ᚾ/ᛁ, ᛗ/ᛞ) and no positional anchors. Reading a whole page in one
vision pass, the model loses its place and generates plausible-but-invented runs.
The original avenue note had only ever calibrated vision on the short phrase
"SOME WISDOM" — that does not survive scaling to full pages.

## Disposition

- **Avenue #1 is closed.** Page-scale AI-vision re-transcription is **not
  viable** at current fidelity. It neither refutes nor can verify the canonical.
- The canonical transcription remains **verified-correct on every checkable
  page** (all solved pages reproduce). No transcription error was found, and
  none of the avenue's flags are credible.
- **Only conceivable revival:** per-rune cropping (crop each of the ~13,000
  runes individually and read at high zoom, with positional ground truth). That
  is ~13k vision reads — cost-prohibitive on the current budget and with no
  guarantee of beating the glyph-ambiguity floor. Documented, not executed.

## Net effect on the project

All four "move-the-needle" avenues are now closed. The unsolved LP2 pages
(0–55) remain one-time-pad-class with no recoverable key, consistent with
`FINDINGS-FOR-SOLVERS.md`. The honest verdict is unchanged: unsolvable from
ciphertext alone without the unpublished key.
