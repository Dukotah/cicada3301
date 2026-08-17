# PREREG ADDENDUM D — adjudicating the G1 line-initial hit

Written **after** G1 fired and **before** any diagnostic was run. G1's result is
recorded unchanged in `results.json`; nothing below edits it.

## What G1 found

| position | n | χ² vs uniform (28 df) | p | χ² vs the corpus's own unigram | p | z vs NULL-A |
|---|---|---|---|---|---|---|
| word-initial | 2928 | 23.50 | 0.71 | 18.23 | 0.92 | −0.84 |
| word-final | 2928 | 31.56 | 0.29 | 26.00 | 0.57 | +0.52 |
| **line-initial** | **594** | **81.40** | **4.1e−07** | **78.66** | **1.1e−06** | **+6.35** |
| line-final | 594 | 26.62 | 0.54 | 24.22 | 0.67 | −0.19 |
| page-initial | 55 | 28.84 | 0.42 | 29.25 | 0.40 | +0.48 |

The pre-registered gate was p < 1e−4. Line-initial clears it by three orders of
magnitude. Every other boundary position is dead flat.

## The competing explanations

**H-force** — an acrostic or layout constraint was imposed at line starts (what G1
was built to detect).

**H-type** — greedy width-based line breaking. These pages are typeset to a fixed
measure; runes have different widths; a line breaks when the *next* rune will not
fit, so the rune pushed onto the following line is selected **for being wide**. The
rune that ends a line is not selected on its width at all. H-type therefore predicts
a strong bias at line-**initial** and *none* at line-**final** — which is exactly the
asymmetry observed.

## Diagnostics and their thresholds (fixed before running)

**D1 — width regression, canon-only.** Fit relative rune widths w (29 unknowns) from
line composition alone: for each of the 594 lines, Σ counts·w ≈ 1 (constant measure),
least squares. Then correlate w with the standardised line-initial residual r.
- **H-type CONFIRMED** if Pearson r(w, resid) ≥ **+0.50** with p < **0.01**.
- **H-type REJECTED** if |r| < 0.30.

**D2 — positional confinement.** Same χ² at line positions 1 and 2 (second and third
rune of a line) and at line positions −2, −3.
- **H-type CONFIRMED** if all four are non-significant (p > 0.01) — a width-selection
  effect touches only the overflowing rune.
- **H-force** predicts a designed pattern would not have to be so confined, but this
  test alone cannot refute H-force; D1 is the discriminating one.

**D3 — is anything readable there anyway?** Read the 594-rune line-initial stream
under 29 shifts × {id, atbash} × {fwd, rev} with the rune-4-gram model against
NULL-A. Threshold as M1: ≥ −13.5 and z ≥ +5. (Campaign XVII already read
first-of-line as plaintext and as a key; this is the shift/atbash extension.)

**D4 — independent-corpus control.** The same line-initial χ² on the two solved LP2
pages (55, 56 = 180 runes, 9 lines) is too small to be decisive and is reported only
as a descriptive number, not as a test. Recorded so that nobody mistakes it for one.

## Verdict rule

- D1 confirmed **and** D3 null → the line-initial deviation is a **typesetting
  artifact**, the acrostic family stays closed, and the number is logged so no future
  researcher re-discovers it as a lead.
- D1 rejected → the deviation is **unexplained** and must be reported as an open
  residue with a falsifiable follow-up, whatever D3 says.
