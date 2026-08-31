# N1 — PDF text-layer / embedded font-subset hunt — PRE-REGISTRATION

_Round 20, Lane N1. Written BEFORE any measurement. Binding: `ARMADA-DOCTRINE.md`._
_Depends on Round 18 L1's NC-6: "No off-repo web/archive search was completed inside this
lane, so the outside world is unsearched, not searched-and-empty."_

## Objective

Find any surviving Liber Primus (or 3301) PDF / PostScript document that carries a **text
layer** (extractable runes) or an **embedded font subset**. A subset `/BaseFont` name plus its
six-letter subset tag would NAME the typesetting program and the rune face outright, converting
L1's *inference* about the toolchain (gs 9.04-9.14, ImageMagick q92, 6x9in page) into a
*measurement*, and promoting the S-TEX generator family from rank 5 to rank 1.

This lane is ARCHIVAL. It scores nothing on LP2 ciphertext, runs no decoder, and blocks no
other lane. It is not a key-space sweep, so the Aiming Test is answered in the archival register.

## The five Aiming-Test answers

**Q1 (recogniser — what would a hit look like, and would this instrument recognise it?)**
A hit = a PDF where `pdffonts` reports at least one font with `emb=yes` AND `sub=yes` whose
`/BaseFont` after the `+` is a runic face (allrunes / Junicode / Everson / Noto Sans Runic /
BabelStone / a custom name), OR any PDF whose `pdftotext` output contains U+16A0..U+16FF
Unicode Runic glyphs (a text layer) for a document that is a genuine LP source (not a
derivative save of a Wikipedia page / puzzle write-up / academic paper).
POSITIVE CONTROL: synthesise a PDF that embeds a subset of a runic TrueType face and typeset
runic text into it; prove `pdffonts` reports `emb=yes sub=yes` with a `TAG+FaceName` BaseFont,
and `pdftotext` recovers the runic codepoints. If the instrument cannot surface a planted
subset tag, the null is worthless. Report the control's recovered tag verbatim.

**Q2 (prior — what measured fact raises this above the flat rate?)**
L1 `RESULTS.md` §3-4: the 58 LP2 JPEGs are byte-exact a Ghostscript(9.04-9.14)->ImageMagick(q92)
render of a typeset 6.00x9.00-inch page. A source PDF/PS *provably existed*. L1 scanned 493
LOCAL PDFs and found none, but explicitly did NOT search off-repo. So a surviving copy on a
known mirror is a live, evidence-motivated target, not lore.

**Q3 (bounded — is the space enumerable?)**
Bounded and enumerable at the mirror level: the KNOWN mirrors already referenced in-repo are a
fixed, finite set — iBotPeaches, micheloosterhof, krisyotam, Internet Archive. The lane
enumerates the PDFs reachable in those four sources plus the full local corpus, runs each
through `pdffonts`/`pdftotext`/`strings`, and reports coverage as (# PDFs inspected) / (# PDFs
reachable). It does NOT attempt an unbounded web crawl.

**Q4 (three conditionals the negative carries)**
1. KEY SPACE: the set of PDFs reachable in {local corpus + the 4 named mirrors}, at the date
   reached. NOT "all PDFs that ever existed."
2. DECODER RELATION: n/a — this is an artifact hunt, not a decode. The relevant analogue is the
   extraction path: `pdffonts` (embedded-font objects) + `pdftotext` (text layer) +
   `strings|grep` (raw FontFile / BaseFont / subset-tag residue). A negative is conditional on
   these three extractors; a PDF that hides a font in an unusual object stream could be missed.
3. ADJUDICATOR REGISTER: "is this a runic face / a genuine LP source" — a subset tag naming a
   non-runic face (Times/Arial/etc.) is a NEGATIVE for this lane even though it is an embedded
   subset.

**Q5 (kill condition at <=10% budget)**
KILL: if after (a) re-scanning the full local PDF corpus and (b) fetching the LP-bearing PDFs
reachable from the four named mirrors, NO PDF surfaces that embeds a runic font subset OR
carries a genuine (non-derivative) LP runic text layer, then LOG THE ARCHIVAL BOUND and STOP.
Do NOT drift into AN-END onion OSINT / preimage retrieval (foreclosed, ELIMINATION-LEDGER
:328-384). Time-box the whole lane to <=15 min wall clock; if the mirror fetch exceeds that,
report the exact coverage fraction reached and stop.

## Positive control (must pass before trusting any null)

`control.py` builds a real PDF with an embedded, subsetted runic font using reportlab (or a
minimal hand-rolled PDF if reportlab absent), typesets a runic string, and verifies:
- `pdffonts` shows a line with `emb=yes`, `sub=yes`, and a `XXXXXX+FaceName` BaseFont, AND
- the six-char subset tag is recovered verbatim.
PASS = subset tag surfaced verbatim by the same `pdffonts` command used on real targets.

## Surrogate null (seed 3301, order-preserving)

Not applicable in the decode sense (no scoring statistic). The archival analogue of a null:
a re-wrap of the published JPEGs into a PDF has NO fonts and NO text layer. `control.py` also
builds this negative-control (image-only PDF) and confirms `pdffonts` reports zero fonts, so
the instrument distinguishes "source document" from "re-wrap of the images."

## Pass / fail threshold (set in advance, never edited)

- **HIT (lane-level FOUND)**: >=1 reachable PDF with `emb=yes sub=yes` runic `/BaseFont`, OR a
  genuine-LP runic text layer. Report the `/BaseFont` subset tag(s) verbatim.
- **NEGATIVE / archival bound**: local corpus re-scan reproduces L1's NC-6 (only derivative
  runic text-layer PDFs, no runic subset) AND the reachable mirror PDFs add no such artifact.
  Log the coverage fraction and the exact mirror URLs reached.
- This lane cannot clear the Round-20 panel-max null (it runs no decode), so `hit` in the
  structured output is reported as the artifact-level find, and the decode-`hit` schema field
  is FALSE by construction (no decode was performed).
