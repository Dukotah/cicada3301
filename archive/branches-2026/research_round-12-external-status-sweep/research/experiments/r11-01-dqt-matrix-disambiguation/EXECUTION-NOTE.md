# EXECUTION NOTE — R11 (mechanism clarification; integrity)

The raw numbers in `results.json` are correct, but two derived labels are imprecise and are corrected here
with direct evidence (raw data untouched — no goalpost move).

## The real mechanism: grayscale vs color encoding (SOF component count)
The two DQT fingerprints do NOT differ in luma quality — **both groups have byte-identical luma tables
(Annex-K Q=92, rms 0.00).** Confirmed by direct segment parsing of representative pages:

| Group | Pages | SOF components | DQT tables | Luma Q |
|---|---|---|---|---|
| `32386501afff` | 33 | **3 (color / YCbCr)** | 2 (luma + chroma) | 92 |
| `a3a96add050f` | 23 | **1 (grayscale)** | 1 (luma only) | 92 |

(p0,p1,p49 → 3 components / 2 DQT; p16,p24 → 1 component / 1 DQT.)

So the split is: **23 pages were emitted as single-component GRAYSCALE JPEGs, 33 as 3-component COLOR JPEGs**,
at the same luma quality. For black-on-white rune pages, both are visually equivalent; the difference is an
encoder/rendering-configuration choice, page by page.

## Two label corrections
1. `partA...relationship = "two_quality_settings_of_annexK_base"` is **imprecise**: luma quality is identical
   (Q=92 both). The true difference is component count (color vs grayscale), i.e. presence/absence of a
   distinct chroma quantization table — NOT a luma quality ladder.
2. `annexK_bestfit_quality[a3a96add050f].chroma_Q = 95, rms 4.345` is a **script fallback artifact**: group
   `a3a96add050f` has NO table id 1 (grayscale); the code fell back to fitting its luma table against the
   chroma base. There is no real chroma table in that group. Ignore that field.

## Bearing on the decision
Part B is unaffected: content complexity (ink coverage) is indistinguishable between groups (MW p=0.338),
so the split is NOT content-driven → the pre-registered rule yields SURVIVES. The clarified mechanism
(grayscale-vs-color encode at constant luma Q=92) reinforces "not content-driven": for near-grayscale rune
images the color/grayscale choice is an encoder setting, essentially content-independent. This is a genuine,
positional PRODUCTION-PIPELINE signal — some pages rendered through a grayscale path, others through a color
path — but it has **ZERO ciphertext bearing** (it is the image container's component mode, downstream of all
glyph content). Gate #2 to rule SURVIVES vs NEGATIVE given the identified mundane mechanism.
