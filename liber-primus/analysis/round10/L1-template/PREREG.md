# L1-TEMPLATE — PRE-REGISTRATION

Written **before** any test was run. Round 10, lane L1.

## Context (not re-derived)

Every cryptanalytic result in this repo assumes the canonical rune stream
(`liber-primus/data/krisyotam_runes.txt`, 13,136 runes / 604 lines / 57 segments) is
correct. The three "independent" transcriptions all descend from one 2017 root
(rtkd/iddqd), so their agreement proves consensus, not correctness. Round 9 built the
first genuinely label-free instrument (`analysis/retranscribe/`) and stopped one stage
short: `templates.py` (1,067 exact bitmaps → 32 shape classes ≥100 members) and
`read.py` (`read_lines.json`, 16,245 glyphs / 646 line bands / 56 page images) both ran;
`diff.py` was never run and no output exists.

This is **not** the eliminated AI-vision re-transcription (mean alignment 0.145). That
asked a generative model to *recognise* a rune. This asks: does this ink match that ink,
exactly, in pixels, on a digital font render whose median glyph has a pixel-identical
twin (Round 8 GEOMETRY, median NN Hamming 0.0000). Different instrument, different error
model.

## Hypotheses

**H1 (instrument).** Deterministic pixel-template DP decoding of the page images
reproduces the canonical rune stream.

**H2 (count).** The 16,245-vs-13,136 surplus (3,109 glyphs) is fully explained by
non-canonical image content (table/Latin pages, headers, ornament bands) plus DP
over-segmentation, and not by canon *omitting* runes that are on the page.

**H3 (doublet).** The canonical doublet deficit (0.66% adjacent-equal vs 3.45% random),
on which the entire OTP-class verdict rests, is present in the label-free image read.
This test is **mapping-free**: adjacent-equal template *classes* are invariant under any
injective class→rune labelling, so it cannot be laundered through the fitted permutation.

## Tests and pre-registered thresholds

### G0 — SELF-CONTROL GATE (mandatory, decided first)
Fit the class→rune assignment by maximum agreement with canon on rune-count-exact lines
(29 labels fitted against ~13,000 glyph identities — canon cannot be laundered through a
channel that narrow). Then:

- **G0a**: overall agreement on count-exact lines must be **≥ 99.5%**.
- **G0b**: on the two **solved** segments (known plaintext = ground truth that leaks
  nothing about 0–54), agreement must be **≥ 99.5%** and the pipeline must reproduce
  their runes.

If G0 fails, the instrument cannot reproduce pages whose runes are known, and **its
disagreements on unsolved pages mean nothing** → verdict INCONCLUSIVE for the
instrument; report the failure mode and do NOT report a transcription finding.

### T1 — DIVERGENCE (only interpretable if G0 passes)
- **PASS / clean**: per-glyph disagreement rate **≤ 0.5%** of compared glyphs AND no
  single (image→canon) confusion pair **≥ 1%** of compared glyphs. → the last
  transcription doubt is retired by measurement.
- **FAIL / dirty**: any systematic confusion class **≥ 1%** of compared glyphs
  concentrated on one rune pair. → escalate to T3.

### T2 — COUNT RECONCILIATION
Per-class and per-page, attribute the surplus. **PASS** = ≥ 95% of the 3,109 surplus
attributed to identified causes (non-canon bands/pages, DP splits/inserts) with the
residue named. **FAIL** = > 5% unexplained, or any page where the image read finds runes
in a region canon has no line for.

### T3 — DOUBLET (mapping-free; the falsifier of the OTP verdict)
On rune-count-exact lines, count adjacent-equal **class** pairs in the image read vs
adjacent-equal **rune** pairs in canon.
- **PASS**: image-read doublet rate within **±0.3%** of canon's rate on the same lines.
  → the deficit is count-verified, the OTP verdict hardens.
- **FAIL**: image-read doublet rate **≥ 2.0%** → the deficit is partly an artifact;
  Campaign X must be re-run and ciphertext autokey returns to the table.
Control: the same statistic on the solved segments, whose doublet rates are known-normal
(2.38% / 3.56%) and must be reproduced within ±1.0% (small-n).

### T4 — IoC (only if T1 or T3 fails)
Re-measure IoC and doublet rate on the corrected stream for segments 0–54.

## NULL CONTROLS (all mandatory)
- **N1 (label null)**: score the diff under 200 random class→rune permutations. Expected
  agreement ≈ 1/29 = 3.4%. The fitted mapping must sit far outside this.
- **N2 (content null)**: diff the image read against a canon whose lines have been
  shuffled (same lengths, wrong content). Expected agreement ≈ 3.4%.
- **N3 (doublet null)**: adjacent-equal rate of a random permutation of the image-read
  class stream — expected ≈ 3.4% — to confirm the statistic can *see* a normal doublet
  rate on this data and is not structurally suppressed by the reader.
- **N4 (reader-blindness null)**: plant known doublets — take a count-exact line, force
  an adjacent duplicate in the *class* stream, confirm T3 detects it. (Sanity that the DP
  is not itself incapable of emitting adjacent equal classes.)

## Scope declared in advance
This tests the *rune identity and count* channel only. It does not test word separators
(dots are below the full-height selection), the Latin table pages 49–51, or ornament
bands. Failure of G0 is a statement about the reader, not about canon.

## Write scope
All output into `liber-primus/analysis/round10/L1-template/` only. No existing file is
modified; no git command is run. `diff.py` is copied into this folder with its output
path retargeted rather than executed in place.
