# ORACLE-PENDING — R44 W2-B4 T4 crossing (p55 ghost tree, image-domain)

**What crossed**: the pre-registered T4 bar for the p55 grey "ghost tree"
(`analysis/round44/W2-B4-trees/PREREG.md`). Interior residual RMS 16.79 vs bar 6.95
(3 x black-ink control RMS 2.32) and spectral peak ratio 65.0 vs bar 10.
Chroma leg did NOT fire (mean chroma 0.000 — the region is pure greyscale).

**This is an image-domain crossing, not a decode survivor** — the HUMAN-ORACLE bundle items
1–5 (key provenance, decoded pages, panel trace) do not apply; no text readout of any length
emerged, so no adjudicate.py / bars_v3 scoring was triggered. Per doctrine 4.9 the crossing is
flagged, not certified, and the lane stopped further p55 channels.

**The cell's own post-hoc characterization (measured, in runlog.txt + results/p55_ghost.json):**
the T4 null model ("ghost = single flat alpha composite") is mis-specified for this object.
The ghost is a TWO-TONE outline drawing:
- outline strokes at Y mode ~192 (alpha ~0.247), fill at Y mode ~236–244 (alpha ~0.059);
- fill interior (erode 2) RMS = 3.06, i.e. only 1.3 x the black-ink control — internally flat;
- the 100–248 histogram is bimodal with an anti-aliasing ramp between modes, which is what
  inflated the single-alpha residual to 16.8;
- all top-10 spectral peaks sit at |f| <= 0.015 cycles/px (period >= 86 px) = the macro
  structure of the drawing itself; the PC4 planted 16-px modulation produced a sharp
  mid-frequency peak (ratio 1410) of a kind absent here;
- no content inside the fill band (crops/p55_ghost_fillband_236_250.png — interiors clean).

**Verdict proposed to the oracle**: the crossing is a null-model artifact of a two-tone grey
line drawing; no code-like channel. The human should eyeball the crops and concur or overrule.

**Crops for the human read** (exact, from relikd master p55.jpg, bbox y1400:2550 x700:1750):
- `../crops/p55_ghost_region.png` — raw luminance, stretched
- `../crops/p55_ghost_stretched_180_250.png` / `p55_ghost_stretched_half.png` — outline band
- `../crops/p55_ghost_fillband_236_250.png` — fill band only
- `../crops/p55_ghost_interior_residual.png` — the residual field that fired T4

**Channel**: no GitHub issue opened from this cell (no network); per HUMAN-ORACLE.md §2 this
file stands in until the next overseer run opens `ORACLE: W2-B4 T4-p55-ghost` with label
`oracle`.
