# Round 33 / I2 -- Construction axis -- RESULTS (2026-10-29)
Scripts: `enciphers.py`, `priors.py` -> `doublet_priors.json`, `rep.py` -> `representability.json` (driftbeam relations
via round32 beam_v2), `rep_v3.py` -> `representability_v3.json` (I1's beam_v3 `panel_max`; imported cleanly, but I1 had
not validated it, so v3 columns are provisional), `relation_skip_by_k.py` -> `patch_validation.json`. Run as in PREREG.md;
20 plants per cell.

## 1. Doublet-rate priors (30 random key/plaintext draws, L=12,956, EN_MODERN, supp 0.83; LP2 observed 0.66384 %)
| construction | mean % | sd | abs err vs LP2 | err / skip_by_two err | within 2x |
|---|---|---|---|---|---|
| keyskip1 (control) | 0.598 | 0.059 | 0.066 | 0.96 | yes |
| skip_by_two (control) | 0.595 | 0.057 | 0.069 | 1.00 | yes |
| reset_per_page | 0.599 | 0.064 | 0.065 | 0.94 | yes |
| reset_per_line | 0.595 | 0.061 | 0.069 | 1.00 | yes |
| skip_by_3 | 0.603 | 0.068 | 0.061 | 0.88 | yes |
| skip_by_4 | 0.596 | 0.059 | 0.068 | 0.98 | yes |
| skip_by_5 | 0.599 | 0.055 | 0.065 | 0.95 | yes |

At full LP2 length skip_by_two's rate is 0.595 %, not the 0.84 % of the Round 18 L=240 measurement (a small-sample
value; one L=12,956 draw has sd about 0.06 pp). LP2's 0.664 % sits about 1.2 sd above all seven. **The Q5 kill rule did
not fire, but only because the measurement cannot discriminate**: every output-side filter at supp 0.83 gives the same
rate (analytically q(1-s)/(1-qs), q=1/29), plain keyskip1 included. The prior is a non-discriminating necessary
condition (it still excludes key-side and plaintext-side filters, per R18); it is NOT evidence for resets or advance>=3
over keyskip1. Under R4 these constructions have no evidence prior beyond "not excluded".

## 2. Representability (median rune recovery, 20 plants; bar 0.85). Cells read rel1 / rel2 / free
| construction | register | L=120 driftbeam | L=120 v3 | page-length driftbeam | page-length v3 | oracle-segmented rel1 (L120 / page) |
|---|---|---|---|---|---|---|
| keyskip1 ctl | MODERN | 1.00/.44/1.00 | 1.00/.45/1.00 | 1.00/.45/1.00 | 1.00/.45/1.00 | - |
| keyskip1 ctl | NOVOWEL | .83/.38/.40 | 1.00/.53/1.00 | .79/.17/.25 | 1.00/.46/1.00 | - |
| skip_by_two ctl | MODERN | .30/1.00/1.00 | .30/1.00/1.00 | .15/1.00/1.00 | .15/1.00/.99 | - |
| skip_by_two ctl | NOVOWEL | .35/.71/.37 | .58/1.00/1.00 | .16/.74/.18 | .31/1.00/1.00 | - |
| reset_per_page | MODERN | n/a (invisible) | n/a | .51/.27/.51 | .51/.26/.51 | n/a / 1.00 |
| reset_per_page | NOVOWEL | n/a | n/a | .40/.15/.25 | .51/.23/.51 | n/a / .83 |
| reset_per_line | MODERN | .21/.15/.21 | .21/.13/.20 | .08/.06/.08 | .08/.06/.08 | 1.00 / .99 |
| reset_per_line | NOVOWEL | .20/.16/.14 | .21/.17/.21 | .08/.07/.06 | .08/.08/.08 | .80 / .83 |
| skip_by_3 | MODERN | .24/.23/**1.00** | .24/.23/**.99** | .11/.18/**.96** | .10/.18/**.96** | - |
| skip_by_3 | NOVOWEL | .22/.20/.25 | .26/.25/**.97** | .08/.08/.16 | .09/.20/**.91** | - |
| skip_by_4 | MODERN | .19/.33/.79 | .17/.33/.83 | .07/.12/.38 | .07/.13/.56 | - |
| skip_by_4 | NOVOWEL | .10/.23/.16 | .21/.30/.76 | .05/.10/.10 | .08/.13/.33 | - |
| skip_by_5 | MODERN | .19/.15/.73 | .17/.15/.74 | .07/.09/.41 | .07/.08/.47 | - |
| skip_by_5 | NOVOWEL | .17/.13/.19 | .23/.21/.69 | .07/.07/.08 | .09/.08/.21 | - |

reset_per_page at L=120 is invisible by construction and was not run. reset_per_line at page length uses the real
per-page line map of the two planted pages. Recovery is decoder-side only; the panel adjudicator was not run (PREREG).
The oracle NOVOWEL value (.80-.83) equals the keyskip1 control's driftbeam NOVOWEL (.79-.83): that residual is the
legacy-scorer register hole, not the reset construction.

Reading:
- skip_by_3 is REPRESENTED: `free` recovers it in EN_MODERN, v3+free in NOVOWEL. No relation earned.
- skip_by_4 and skip_by_5 are UNREPRESENTED (best cell 0.83 at L=120 MODERN; 0.33-0.56 at page length).
- reset_per_page and reset_per_line are UNREPRESENTED by every relation (<= 0.51), yet recovered (1.00 MODERN) by
  segmenting at the known boundary and running relation 1. That is a segmentation fix, not a transition-relation fix.

## 3. Outcome
Kill rule fired: NO (literal rule; the prior is non-discriminating, see 1). Earned (prior within 2x AND unrepresented
by driftbeam 1/2/free and v3): skip_by_4, skip_by_5 (relation `keyskipk`), reset_per_page and reset_per_line (as
`decode_with_resets` segmentation). Shipped as a patch proposal only: `relation_patch.md`, `relation_skip_by_k.py`
(all planted constructions recover 1.0 on EN_MODERN, L=120 x10; reset_per_page 2-page x6 recovers 1.0).

## 4. Three conditionals
Key space: none opened (SHA-CTR synthetic key, correct key supplied). Transition model: the axis measured; advance k in
1..5, supp 0.83 fixed, reset to offset 0 only. Adjudicator register: EN_MODERN and EN_NOVOWEL, recovery criterion only.

## 5. not_covered
Reset to a nonzero/permuted offset; resets combined with skip_by_k or free drift; supp != 0.83; k > 5; burn patterns
other than "rejected draw plus k-1 more"; other registers; nine-register panel adjudication; page-length plants span
only 2 pages; v3 not yet validated by I1 (columns provisional); patch validated only on EN_MODERN with its own quadgram
scorer (not NOVOWEL, not speed-profiled); the LP2 line map is unreliable, so reset_per_line decoding on real data needs
the segmentation fixed first; the doublet rate cannot rank any of these against keyskip1, so there is no claim that LP2
uses any of them.
