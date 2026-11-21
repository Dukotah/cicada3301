# RESULTS — R44 WAVE-2 CELL B4: p32 blurred tree / p55 ghost tree

Cell dir `analysis/round44/W2-B4-trees/`. PREREG hash-stamped before first run (runlog.txt);
two control-phase instrument addenda (T1 reference population; T2 model-comparison classifier),
both appended and re-stamped BEFORE the corresponding real target was ever scored.

**VERDICT: measured / negative on every pre-registered channel, with ONE pre-registered bar
crossing (T4, p55) that is flagged-for-oracle and characterized by this cell as a null-model
artifact of a two-tone grey line drawing — see `ORACLE-T4-p55-ghost/ORACLE-PENDING.md`. No
legible artifact, no text readout of any length emerged anywhere (so the bars_v3/adjudicate.py
leg was never triggered; N_adjudicated = 0).**

## S1 — byte/pixel diff across every held mirror copy (results/mirror_diff.json)

Positive control PC1: planted +10Y 40x40 block in the tree region, q85 re-encode — T1 fired
(tree p99.9 = 10.0 vs smooth-ref 1.0, bar max(8, 2x1)); clean q85 round-trip did NOT fire (4.0).

Byte identity (sha256, runlog.txt):
- p32: relikd master == Hadyn `ky2khlqdf7qdznac.onion/32.jpg` == cijhho123 `2014onion7/32.jpg`
  == cijhho123 `liber primus images full/49.jpg` (that set's numbering is offset; its
  `32.jpg`/`55.jpg` are DIFFERENT pages — found by hash search, not assumed).
- p55: relikd == `2014onion7/55.jpg` == `images full/72.jpg`. Hadyn mirror holds no p55
  (0–54 only) — held-copy gap, noted.
- wiki-uncovering-cicada `32.jpg`/`55.jpg`: different BYTES, pixel-identical after decode
  (metadata-level re-save; max |dY| = 0.0 on both pages).

**Real result: zero pixel variance exists across every held copy of both pages. The
cross-mirror channel is EMPTY — there is nothing to difference.** T1 fired on no real pair.

## S2 — frequency-domain blur characterization, p32 tree (results/blur_freq.json)

Positive control PC2 (plants through the same classifier): gauss sigma=8 -> gaussian sigma=8;
disk r=8 -> disk r=8; motion L=20 theta=30 -> motion L=20 theta=30.0. All three classes AND
parameters recovered exactly (PREREG tolerance +/-25%, +/-15 deg).

**Real result: the p32 tree blur is GAUSSIAN-like, isotropic, sigma ~= 26 px** (SSE 2.63 vs
motion 2.93 vs disk 3.15 under the P = A f^-alpha |H|^2 + floor model). No motion streak, no
defocus rings. Consistent with a deliberate soft-airbrush/Gaussian render of the art asset,
i.e. "content blur", not camera/process blur. (Conditional: LSI model; a spatially varying
blur is represented only approximately.)

## S3 — deconvolution of the p32 tree (results/deconv.json)

Grid: 62 PSFs (Gaussian sigma 2-30, disk r 2-30, motion L {5,10,20,40} x 8 angles) x
2 deconvolvers (Wiener K=0.01, RL-30) = 124 outputs per target, run identically over
three targets {sharp-rune control, blank-paper control, real p32 tree}.

**Power plants PC3a/PC3b both FELL SHORT of the registered 0.5 edge-energy recovery bar**
(0.326 and 0.402): a known rune-text crop blurred at the real tree's estimated sigma~26 and
RL-30-restored does NOT come back legible, at either glyph scale (crops/PC3a_runes_orig_blur_rl30.png,
crops/PC3b_runes3x_orig_blur_rl30.png). This is a measured instrument limit, not a target
result: at sigma~26 the deconvolver is underpowered to resolve text — so S3's negative is
explicitly power-conditioned.

**Hallucination control (T3 leg): the controls separate cleanly from noise.** Sharp-rune
control max_novel = 566 (deconvolving already-sharp text manufactures hundreds of spurious
stroke-components — the expected ringing); blank-paper control max_novel = 8. The real p32
tree max_novel = 8 (mean 1.9) sits at the blank-paper floor and far below the sharp control.
Because the controls do not satisfy the registered `< 1 novel component each` clean-leg
requirement, T3 cannot fire by construction; and independently the real tree produces no
stroke-structure that is absent from its own dilated dark mask beyond that control floor.

**Real result: T3 did NOT fire (T3_flag_for_oracle = False). Deconvolution of the p32 tree
over the full PSF grid returns only a sharper bare-branch tree silhouette — no glyphs, no
letterforms, no sub-tree structure** (the max-novel example, motion40/22.5 Wiener, is a
cleaner tree outline with scattered ringing fragments; crops/real_tree_maxnovel_motion40_22.5_wiener.png,
plus crops/real_tree_gauss26/gauss14/disk14 at-sigma crops). No text readout of length >= 30
emerged, so the adjudicate.py / bar_v3 leg was never triggered (N_adjudicated = 0).
Consistent with S2's reading of the blur as deliberate content-blur over line art, not a
recoverable concealment of text.

## S4 — p55 ghost tree grey-level / alpha analysis (results/p55_ghost.json)

Positive control PC4: flat alpha=0.18 composite recovered at 0.1803 with residual 1.04 (below
the 6.95 bar); planted 16-px alpha modulation detected loudly (RMS 20.5, spectral peak 1410).

**Real result: T4 FIRED** — interior RMS 16.79 > bar 6.95 (3x black-ink control 2.32) and
spectral peak 65 > 10. Chroma leg clean (0.000 — pure greyscale; no chroma channel).
Post-hoc characterization (runlog.txt): the ghost is a TWO-TONE outline drawing — outline
mode Y~192 (alpha 0.247), fill mode Y~236-244 (alpha 0.059), fill interior RMS 3.06 (only
1.3x the black-ink control, internally flat), bimodal histogram with AA ramp between modes;
all spectral peaks at period >= 86 px (the drawing's own macro structure — nothing like the
plant's sharp 16-px peak). No content inside the fill (crops/p55_ghost_fillband_236_250.png).
**Flagged-for-oracle per doctrine 4.9 (never auto-dismissed): `ORACLE-T4-p55-ghost/`.**

Side observation (characterization, not a preregistered channel): the p32 and p55 trees are
NOT the same art asset — scale-normalized silhouette IoU 0.38 (0.32 mirrored)
(crops/silhouette_p32_vs_p55.png).

## Coverage

- Mirror diff: all 5 held copies of p32 and 4 of p55 in corpus/A-primary-artifacts +
  data/relikd (byte-hash + full-page pixel diff; T1 with validated plant). onions_ibotpeaches
  (analysis/armada_osint/onions_ibotpeaches) holds no LP page images — checked by ls/find.
- Blur: model comparison over Gaussian sigma 1-30 / disk r 1-30 / motion L 3-40 x angles
  (7.5 deg coarse + 2.5 deg refined), LSI assumption.
- Deconvolution: full PREREG grid — 62 PSFs (Gaussian sigma 2-30, disk r 2-30, motion
  L {5,10,20,40} x 8 angles) x {Wiener, RL-30} = 124 outputs, over the real tree plus two
  hallucination controls (sharp rune crop + blank paper); power-conditioned by PC3 (restore
  of a known plant at sigma~26 recovers only 0.33-0.40 of edge energy — below the 0.5 bar).
- p55: single-alpha compositing model + chroma + spectral modulation check, interior erode 3.

## not_covered

- copies of these pages NOT held in this repo (no network in this cell);
- spatially varying or nonlinear blur models (LSI deconvolution only);
- semantic/steganographic channels already measured elsewhere (LSB/append/carve: R8, R29-L1,
  R30-A1/A2) — deliberately not re-run;
- the Hadyn mirror's missing p55 (no copy to diff);
- art-historical identification of the tree assets (R30-C1's open not_covered stands).

## reopens_if

A new mirror copy of p32/p55 with different pixels surfaces; or a validated spatially-varying
deconvolution instrument is brought; or the oracle overrules the T4 characterization.
