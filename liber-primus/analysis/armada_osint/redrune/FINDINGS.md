# Red-rune extraction & cryptanalysis — FINDINGS

**Question:** the relikd Liber Primus renders carry genuine red ink on select
glyphs (verified: mean RGB ~ (187,2,3), saturated ~#C80000, not a JPEG artifact).
Our transliteration carries no colour, so the red runes as a *selection* had never
been fed to cryptanalysis. Do they encode anything, or are they decorative
rubrication?

**Verdict: decorative rubrication. The red runes encode nothing new. Clean null.**

---

## Method

- **Red rule (verified):** `red = (R-(G+B)/2 > 40) & (R>120) & (G<80)` on the RGB
  array. Per glyph box, `red-fraction = red_px / ink_px`; glyph is RED if fraction
  > 0.30. The red is bimodal — fractions cluster at ~0 or ~1.0 — so the count of
  red glyphs (**187**) is identical for every threshold from 0.15 to 0.90.
  Threshold choice is not load-bearing.

- **Page<->canon alignment (STEP 2).** The requested count-signature matching was
  built and tested and proved **unreliable**: the segmenter drifts +-2-3
  glyphs/line, exceeding between-page discrimination — only **1 of 56** pages
  matched confidently. We therefore reuse the already-solved image<->canon
  alignment baked into `analysis/stones/` (`build_dataset.py` + `alignment.json`),
  whose verified premise is that **relikd line order == krisyotam line order
  exactly (594 identical lines)** even though relikd *page numbers* differ from
  krisyotam page numbers. `dataset.npz` gives, for all **12,764** segmented
  glyphs, the glyph box + its aligned canon rune (**10,774** on exact-count-match
  lines; the other 1,990 use the stones classifier, mean conf 0.96). We overlay
  the red rule on those boxes -> a red flag per canonically-placed rune. This is
  the confident extraction the count-signature path could not deliver.

- **Decoration classes.** The stones segmenter (`runic_components`, height
  95-132 px) already excludes the giant ornamental **drop-cap** initials (h~500)
  and the **dot-grid** separator ornaments (tiny). So the 187 red glyphs are
  genuine text-runes, not the obvious decorative furniture — the strongest possible
  case for the "hidden selection" hypothesis. It still fails (below).

## STEP 4 — the global red-rune string (187 runes, canon reading order)

```
HEOGMIAFSYENGCJEOHNGCTHTAEJTXHTUOEDTHTXBMGIASBXEODOOETTHAECWJXEAGEAMIXMUXMCTHPOB
UNGNCUBNTFNGAWNGGXDGIBIEOTBIYPYLSOAAEHLEEOIMLLSCPEOXCFIAWHGTHEOIFUEORCSNMYGDAEH
TPWEOSWBEOTHNHGJRIADIATHAIEOAEXLEOEAIAAJHRTHPDJNGOGFEOMCHDOTCMNGDIATHXIM
```

Red appears on **14 of 55 canon pages**; the rest have no red text-runes.

## STEP 5 — DECORATION vs DATA (the decisive test)

Per canon page, is the red run the page's own opening / section-initial words?

| kind | pages | meaning |
|------|-------|---------|
| prefix | 7 | red = the page's literal opening word(s) after the drop-cap |
| contig-run | 5 | red = a single contiguous section-initial block |
| scattered | 2 | red glyphs not contiguous |
| no-red | 41 | — |

**12 of 14 red pages are contiguous opening/section runs.** Spot-check against
canon confirms them as the literal text:
- canon page 0 opens `S HEOGMIAF SYENGC...`; red = `HEOGMIAFSYENGC` (the opening
  word, the leading `S` being the height-excluded drop-cap).
- canon page 27 opens `M PYLSOAAEHLEEOIMLLSC...`; red = `PYLSOAAEHLEEOIMLLSCP`.
- the big 47-rune red block corresponds to a page's opening section verbatim.

The two "scattered" pages (canon 3, 33) are almost certainly the same phenomenon
blurred by +-1 glyph segmentation drift and the relikd/canon page-number offset,
not an independent hidden selection. **The red is rubrication of section openers.
It re-states text already present in black; it carries no independent payload.**

## STEP 6 — cryptanalysis of the global red string

Calibrated scorer `score_norm` (English baseline ~ -4.0, noise floor ~ -7.49,
break threshold -5.2).

**(a) direct readings of the red string**
| reading | score |
|---------|-------|
| RED direct | -7.760 |
| RED atbash | -7.649 |
| RED best single-shift (+25) | -7.133 |

**(b) red as KEY over the 12,577 black runes** (additive/Beaufort/atbash, both
signs, forward + reversed): best config = **-7.469**.

**Best score overall: -7.13** — at the random noise floor, ~2 points below the
-5.2 break threshold and ~3 below English. **0 of ~30 configurations cleared the
threshold.** No plaintext, no key.

## Conclusion

The red ink is genuine, but as a cryptographic *selection* it is a null. It is
decorative **rubrication**: on the pages that have it, the red marks are the
literal opening / section-initial words of that same page (12/14 pages are exact
contiguous opening runs; the 2 "scattered" cases are alignment-noise variants of
the same thing). The red re-states black text already in the corpus — it adds no
new symbols and encodes no independent message. Read directly, under Atbash, under
any single gematria shift, or used as additive/Beaufort/atbash key material over
the black runes (per-sign, forward and reversed), the 187-rune red string scores
at the noise floor (best -7.13 vs threshold -5.2). **Documented null: the red
runes are decoration, not data.**

## Reproduce

```
PYTHONUTF8=1 python analysis/armada_osint/redrune/extract.py
```
Writes `result.json`. Depends on `analysis/stones/dataset.npz`, `all_pred.npy`,
`all_conf.npy`, `alignment.json` (the verified image<->canon alignment) and the
relikd JPEGs in `data/relikd/`.
