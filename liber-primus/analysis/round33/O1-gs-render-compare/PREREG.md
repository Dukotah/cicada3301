# O1 — Ghostscript 9.04–9.14 render byte-compare (PREREG only; no compute spent in Round 33)

_Written 2026-10-29 by the Round 33 coordinator. Status: **queued, PREREG-only.** No build box was available for
this round, so this file is the lane's complete Round 33 output. It exists so that whoever picks the lane up on a
Linux box does not have to re-derive the aim._

## Aiming Test

**Q1 — What would a hit look like, and would this instrument recognise it?**
A hit is a Ghostscript release + ImageMagick version + render parameters that reproduce one of the 58 archived LP2
JPEGs **byte-for-byte in the decoded luma/chroma planes** at the measured quality factor (R18-L1 §3 pinned the
pipeline as ImageMagick-over-Ghostscript and the ICC profile as byte-identical across gs 9.04–9.21). Recognizer: a
planted control — render a known PS page through gs 9.04 + the same IM, re-encode at the measured DQT, decode, and
prove the comparator reports an exact plane match on the control and a non-match when the gs minor version is
changed by one. If the comparator cannot distinguish 9.04 from 9.05 on the control, the lane is INVALID.

**Q2 — What measured fact raises the prior?**
`analysis/round18/L1-toolchain/RESULTS.md` §4 and line 201: the embedded ICC profile (2576 B, md5
`e409cef1…`) is byte-identical across ghostpdl tags 9.04–9.21 and non-matching for 9.00–9.02 (9.03 unmeasured);
Round 32 X1 corrected the nav docs to 9.04–9.14. The toolchain is a held artifact, not lore (R4).

**Q3 — Bounded?**
Enumerable: 9 measured gs releases in band (9.04, 9.05, 9.06, 9.07, 9.09, 9.10, 9.12, 9.14, plus 9.03 which was never
measured) × the IM versions contemporaneous with each (≤4 per release) × the DQT/quality factors already measured in
R18-L1 (one per image) = well under 500 renders per page, 58 pages. Each gs build is ~2 GB RAM and ~20 min; this is a
build-box job, not a laptop job.

**Q4 — The three conditionals.**
Not a decode lane. Its negative is conditional on (1) the gs/IM version grid above, (2) the source being PS/PDF
rendered by that chain (R18-L1's finding), (3) the comparator's measured sensitivity on the control.

**Q5 — Kill at 10 %.**
Build 9.04 and 9.14 only; render page 0 through both. If the two renders are byte-identical to each other at the
measured quality factor, the channel cannot pin a minor version and the lane stops with "band not resolvable at
render level" — a bounded negative that costs two builds.

## Deliverable when it runs
`round33/O1-gs-render-compare/` — `build_matrix.json`, `compare.py`, per-page match table, `RESULTS.md`, `ledger.json`.
Any exact match is a toolchain pin, not a solve; it feeds the off-repo source-PDF hunt named in `PICKUP-HERE.md`.
