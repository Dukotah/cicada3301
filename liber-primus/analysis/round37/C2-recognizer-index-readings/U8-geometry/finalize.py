import json
import numpy as np
r = json.load(open('results.json')); P = r['pages']; C = r['controls']
L = ["# RESULTS - R37 C2-U8 per-page geometry (interrupter-gated turtle renders)\n",
     "PREREG.md (+Addendum 1) written first. 58 pages x 4 variants = 232 renders; each vs 200 sequence shuffles (non-F values permuted, F positions held; V4 word order permuted). Runtime 395 s.\n",
     "## What R22-B already covered (not repeated)\nR22-B: LP2 pages 0-54 as one book-concatenated stream; value / prime-index / totient x moduli {4,6,8,12,29,360} x absolute/relative x unit/value step = 72 renders; global shape statistics (closure, self-intersections, bbox fill, caging, symmetry, components) vs 200-shuffle null; F left in as an ordinary rune; no per-page, no pen-up, no LP1 numbers, no template/glyph recognizer. Its own not_covered named exactly those. U8 here is per page, interrupter-gated, includes AN END / PARABLE as printed and LP1 plaintext word sums, and uses a glyph template match.\n",
     "## Planted-glyph controls (before the pages) - **ALL FAILED**\n| plant | variant | plant best score (z of best template) | best template | shuffle null max | verdict |\n|---|---|---|---|---|---|"]
for k, v in C.items():
    L.append(f"| {k} | {k.split('_')[0]} | {v['score']:.2f} | {v['best_template']} | {v['null_max']:.2f} | {'PASS' if v['passed'] else 'FAIL'} |")
L.append("\nThe recognizer could not separate a planted 24-30 step glyph (octagon, 29-gon, T, L, 12-gon) embedded in LP2 page-0 noise from the best accidental match among the shuffled strokes. Raw NCC (first attempt) was worse (null 0.87-0.99 from line-like strokes matching I / 1 / rune-I and short zigzags matching simple glyphs); the z-distinctiveness version in Addendum 1 got closest on V3 (T: 4.09 vs null max 4.21) but still failed. Per the kill rule this lane is **INCONCLUSIVE**: the page results below are diagnostic only.\n")
L.append("## Variant table (diagnostic; control failed)\n| variant | pages | above own null max | max real score | max page-null-max | mean(real - null max) | pages with no candidate |\n|---|---|---|---|---|---|---|")
for v in sorted(set(p['var'] for p in P)):
    s = [p for p in P if p['var'] == v]
    L.append(f"| {v} | {len(s)} | {sum(p['above_null'] for p in s)} | {max(p['score'] for p in s):.2f} | {max(p['null_max'] for p in s):.2f} | {np.mean([p['score'] - p['null_max'] for p in s]):.2f} | {sum(p['template'] is None for p in s)} |")
L.append("\nNo page-variant exceeded its own 200-shuffle null max (0/232), so no refinement ran and **no oracle PNGs were produced**. Because the control failed this is not a clean negative: a real planted-class glyph would also have been missed.\n")
L.append("Human-eye material: `png/contact_V1..V4_*.png` (58 page renders per variant, 96 px thumbnails, 10 columns; black = pen down, pale blue = pen up) and `png/plant_*.png` (the plants with the best candidate in red). Page order: 0-54 LP2, 55 AN END, 56 PARABLE, 57 LP1 plaintext.\n")
L.append("## Three conditionals\n1. **Rule space:** 4 turtle rules x 58 pages = 232 renders. Not covered: other moduli/step rules, value-scaled steps, the 55-page grid layout, L-systems, 3D, glyphs of >2 strokes, line-sum streams, multi-glyph text along a line beyond adjacent stroke pairs.\n2. **Decoder:** deterministic turtle; F = pen-up unit step (V1-V3) / F-containing word pen-up (V4); a different interrupter semantics is missed. LP1 plaintext (page 57) has no F so is never pen-up.\n3. **Adjudicator:** glyph-template NCC (Latin/digits/runes) is UNPOWERED here: planted glyphs of 24-30 steps are not separable from shuffled strokes. Needs a better recognizer (e.g. an OCR-style classifier trained on turtle-drawn strokes, or fewer degrees of freedom) before this family can be called negative.\n")
L.append("## not_covered\nAll of the above conditionals; additionally a power-adequate recognizer. Coordinator decision needed: invest in a stroke-aware recognizer (e.g. require closure/rotation-invariant Hu moments + template) or accept the human-eye contact sheets as the only readout.\n")
L.append("## Files\nPREREG.md, u8.py, finalize.py, results.json, run.log, png/, ledger.json, RESULTS.md\n")
open('RESULTS.md', 'w').write("\n".join(L))
led = {"$comment": "written by R37 C2-U8 lane agent", "entries": [{
    "id": "R37-C2-U8-GEOMETRY", "round": 37, "lane": "C2-U8", "date": "2026-10-30", "status": "inconclusive", "positive_control": "failed",
    "control_detail": "5 planted glyphs (octagon, 29-gon, T, L, 12-gon) in LP2 page-0 noise: none exceeded its 200-shuffle null max (best V3-T 4.09 vs 4.21).",
    "hypothesis": "Numbers are the direction: per-page, interrupter-gated turtle renders of page numbers (and LP1 word sums) draw a glyph.",
    "coverage": "232 renders (58 pages x 4 variants), 200 shuffles each; 0/232 above own null max; no oracle PNGs; diagnostic only.",
    "result": "inconclusive: recognizer has no measured power at 24-30 step glyphs.", "threshold": "refined p <= 0.01/232 after beating the page null max",
    "power": "failed on all 5 plants",
    "conditionals": ["rule space: 4 rules x 58 pages only (R22-B covered 72 book-concatenated combos)", "decoder: unit/word-length steps, F = pen-up", "adjudicator: glyph-template NCC unpowered"],
    "not_covered": ["power-adequate glyph recognizer", "other moduli/steps", "55-page grid", "L-systems", "glyphs >2 strokes"],
    "artifacts": ["PREREG.md", "u8.py", "results.json", "RESULTS.md", "png/contact_V1_prime_mod8_rel.png", "png/contact_V2_idx_rel_29.png", "png/contact_V3_idx_abs_card.png", "png/contact_V4_wordsum_rel12.png"]}]}
json.dump(led, open('ledger.json', 'w'), indent=1)
