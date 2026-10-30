# PREREG - R37 C2-U8 per-page geometry (written 2026-10-30, BEFORE any page render is scored)

Binding: ARMADA-DOCTRINE.md. No git. One Python process. Only this directory is written.

## What R22-B already covered (from its PREREG/RESULTS; NOT repeated here)
R22-B (analysis/round22/B-turtle-spatial-render): LP2 pages 0-54 as ONE BOOK-CONCATENATED stream (12,956 runes), streams
{prime value, prime index, totient} x turn moduli {4,6,8,12,29,360} x {absolute, relative} x step {unit, value} = 72 renders,
geometry statistics (closure, self-intersections, bbox fill, caging, symmetry, components) vs 200-shuffle null, + G3 base32/lat-long
decode. Interrupters (F) left IN as ordinary runes. Its own not_covered: per-page renders, interrupter-gated pen-up, LP1 numbers as
input, L-systems, 3D, other step functions. Its recognizer was global shape statistics, not glyph template matching.
Here: PER PAGE, PEN-UP at interrupters, LP1 pages included, recognizer = glyph template match. No overlap with R22-B's 72 cells.

## Pages (58)
LP2 pages 0-54 (55, ciphertext runes as printed, mapcommon.parse); page 55 = AN END and page 56 = PARABLE as printed in the
same file (LP1 solved pages' printed numbers); page 57 = LP1 known-plaintext (cicada_koans_and_lp_sections.txt through
gematria.keyword_to_indices; word boundaries, no F interrupters exist in plaintext). Total 58.

## Variants (4; "numbers" = Gematria Primus prime of the rune; F = rune index 0 = interrupter)
- V1 `prime_mod8_rel`: heading += (prime mod 8)*45 deg, unit step.   (sign/mod variant A)
- V2 `idx_rel_29`: heading += idx*360/29 deg, unit step.            (mod-29 group)
- V3 `idx_abs_card`: heading = (idx mod 4)*90 deg absolute, unit step. (cardinal / Manhattan)
- V4 `wordsum_rel12`: per WORD: heading += (sum of word primes mod 12)*30 deg, step = word length in runes. (word GP sums)
Pen-up rule: V1-V3: a step taken on an F rune is made with the pen up (turn rule still applied); V4: a word containing F is pen-up.
Page 57 (plaintext) has no F: V1-V3 never lift the pen; V4 never lifts. Stated as a limitation, not hidden.

## Recognizer
Glyph candidates = each maximal pen-down STROKE with >=6 steps (V4: >=5) and each adjacent PAIR of strokes (both drawn, gap not drawn).
Each candidate: bbox-fit (aspect preserved) 64x64 raster, line width 3, gaussian blur sigma 2, 32x32, mean-centred, unit-normalised.
Template bank: Latin A-Z + digits 0-9 (Arial) + the 29 Gematria Primus runes (Segoe UI Historic), same pipeline, x 4 rotations (0/90/180/270)
= 260 + 4x... templates. Page-variant score = max over candidates x templates of NCC. Null: 200 sequence shuffles per page-variant
(non-F values permuted, F positions held; V4: word order permuted) through the identical pipeline; null max per page-variant.
Verdict per page-variant: real > null max -> "above null" -> refined with 25,000 shuffles; FLAG iff refined p <= 0.01/232 = 4.3e-5.
Every above-null page-variant PNG goes in the oracle bundle regardless of refined p (a human looks); only refined-p flags are called hits.

## Controls (run BEFORE the pages; kill = any control fails -> INCONCLUSIVE)
A planted glyph drawn by a planted rune sequence inside 100 runes of LP2 page-0 noise on each side of an F-delimited block:
V1 octagon (8 runes with prime mod 8 = 1, 'O'); V2 29-gon (idx 1 x 29, 'O'); V3 'T' and 'L' (cardinal runs); V4 12-gon (12 length-3 words
with sum mod 12 = 1, flanked by F-words). Each must score above its own 200-shuffle null max AND its best template must be a ring/letter
consistent with the plant (reported). 

## Three conditionals the negative carries
1. Rule space: exactly 4 turtle rules x 58 pages = 232 renders; not covered: other moduli/step rules, value-scaled steps, 55-page layout grid, L-systems, 3D, multi-glyph text along a line beyond stroke pairs, glyphs >2 strokes, glyphs at non-90-degree rotation, plaintext-side numbers on LP2 (there is none), line-sum streams.
2. Decoder: deterministic turtle with the pen-up conventions above; a different interrupter semantics (e.g. F = turn marker, or pen-up after not at) is missed.
3. Adjudicator: template NCC on 32x32 rasters over Latin/digit/rune glyphs; power is the planted-control margin, long wandering strokes are ink-dense and mostly match nothing; a non-glyph picture (map, QR, symbol) is not a template here.
Hits would be flagged-for-oracle (HUMAN-ORACLE.md), never self-certified.

## ADDENDUM 1 (2026-10-30, appended during control development, before any page render was scored)
The first control runs (raw NCC score, 6-step minimum) FAILED: shuffled strokes scored 0.87-0.99 (line-like strokes matching I/1/rune-I,
short zigzags matching simple glyphs) above every planted glyph. Instrument changes made on CONTROL data only, before pages:
(1) drop line-like templates (I, 1, rune I) and line-like candidates (bbox aspect > 2.5); (2) candidates 12..40 steps (V4 10..40), ink fraction <= 0.18;
(3) blur sigma 3 on the 64-grid; (4) plants enlarged to >= 24 steps (octagon x3, 29-gon, T/L scaled x3, 12-gon); (5) score = per-candidate
distinctiveness z = (best NCC - mean over bank)/sd over bank. The control STILL FAILED on all five plants (see RESULTS). Per the kill rule the page
sweep below is run as DIAGNOSTIC ONLY (contact sheets for the human eye; template scores not interpretable as a negative). The page-sweep nulls and
flag logic are unchanged.
