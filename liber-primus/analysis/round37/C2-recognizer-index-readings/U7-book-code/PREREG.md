# PREREG - R37 C2-U7 book-code indices (written 2026-10-30, BEFORE any selection is scored)

Binding: ARMADA-DOCTRINE.md. No git. One Python process. Only this directory is written.

## Hypothesis
The signed numeric strings are book-code INDICES into text ("Liber Primus is the way", the 2012-14 chain used
page:line:char / word-index book codes). NOT keys: X1 correction - H7/H12 as numeric keys already ran (R10b B1,
campaign18 numeric2_skip). Direction here = number -> position in a text -> retrieved letters.

## Signed numeric strings (verbatim; provenance = clues.json O4 / corpus/A-primary-artifacts/pgp/messages/)
- S1  2012-01-end-of-puzzle P.S. integer (three lines joined, backslash continuations removed):
  `1041279065891998535982789873959431895640` `442510695567564373922695237268242385295908173` `9834390370374475764863415203423499357108713631`
- S2  2013-cicada-os-message `@1231507051321` (digits `1231507051321`)
- LOC 2012-01-location-numbers, ten 12-digit blocks verbatim, in order:
  162667212858 414974253863 598852142735 876873892385 935691396441 316744223127 427566844663 644169769482 889296759263 963846244281
  (LOC = digits concatenated; LOCW = each block as one whole number)
Not used (different shape, already book codes with explicit page:line): the colon-list messages (book-code-poem, mabinogion, second-chance, opening-book-code) and 2012-01-coordinates (decimals).

## Index schemes (digit string D, optionally reversed; index v -> element v mod size)
- pair (non-overlapping 2-digit), triple (non-overlapping 3-digit), single (each digit), whole (LOCW only: each 12-digit block is one number, mod size).
- base: 0-based (v mod size) or 1-based ((v-1) mod size). Reversal: digit string reversed (for whole: each block reversed).
- Targets (units): LP1 = solved plaintext `data/keys/armada18/cicada_koans_and_lp_sections.txt` (words / non-blank lines / flat runes via gematria.keyword_to_indices, greedy digraphs - lossy K->C,V->U); UNS = LP2 pages 0-54 ciphertext rune stream from round10/L2-map mapcommon.parse(max_page=54) (words / lines / flat runes), read as-is.
- Readouts: R = the rune at the index (flat rune stream); F = first rune of the indexed word/line; W = the whole indexed word concatenated.
- Selection count: (S1,S2,LOC) x (pair,triple,single) x {LP1,UNS} x {R,F-word,F-line} x 2 bases x 2 rev = 216; LOCW x 6 x 2 x 2 = 24; W readout: 9 x 2 x 2 x 2 = 72 + LOCW 2x2x2 = 8. Total 320 (<=500).

## Recognizer
Panel-R36 (`data/panels/panel-r36.npz`, 12 registers, sha a0682f0c...), statistic `pmax_ne` (best non-English-modern/KJV
register z) on the retrieved rune string, via round19/I2 `Panel` raw trigram score + panel calibration at the selection length
(clamped at the panel grid ends - for n<32 absolute z is inflated, but p-values come from the null draws at the SAME n, so this does not matter).
Two nulls per selection, M=2000 each: (b) random-index null = same readout from uniformly random indices of the same count;
(a) order-shuffle of the selected units. p = (1+#null>=real)/(M+1); p_gate = max(p_a, p_b).
Any p_gate<=0.005 is refined with M=100,000 (b) and 20,000 (a). FLAG = refined p_gate <= 0.01/320 = 3.1e-5
(family-wise Bonferroni over the 320). Per-scheme-group bar = 0.01/N_group reported as well.

## Kill / controls (run BEFORE the scheme sweep)
Three planted controls: A) 60-rune LP1 phrase hidden by a triple-digit list into LP1 flat runes (R); B) the LP1 sentence
"THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED" located by word indices (W readout, triple); C) 60-rune phrase hidden
by first-rune-of-UNS-word indices (triple, UNS F-word). Each must give p_gate <= 0.002 (floor 5e-4 at M=2000). A random digit
string of the same length must NOT. If any control fails the sweep result is INCONCLUSIVE, not negative.

## Three conditionals the negative carries
1. Rule space: only the 320 enumerated selections; not covered: page:line:char addressing (no LP page/line metadata for LP1 text), non-LP texts (Mabinogion, KJV - the reverse direction campaign XVII did), sliding/overlapping digit windows, base-N conversions of the integers, per-block short strings, colon-list messages.
2. Decoder: index -> letters is a verbatim retrieval with a mod wrap; a book code with a different skip/offset convention or a different edition is missed.
3. Adjudicator: trigram-panel pmax_ne has power only for strings long enough to carry language (n>=~30); S2 selections (n=4..13) are essentially unpowered and are stated as such. Hits would be flagged for oracle (HUMAN-ORACLE.md), never self-certified.

## ADDENDUM 1 (2026-10-30, after the first run of u7.py)
Run 1 used a random-index null drawn over the WHOLE target; that is mis-specified for single/pair schemes (digits 0-9 only address the first 10 units).
The null was corrected to draw index VALUES uniformly over the scheme's own alphabet (0-9, 0-99, 0-999, 0..10^12 for whole) with the same base/mod map, and the
sweep re-run (31 s). Both runs: 0 flagged. Control B (LP1 word-W readout) failed in both runs (see RESULTS); W-readout cells are therefore reported as UNPOWERED,
not as negatives. The family-wise bar stays 0.01/320 (conservative).
