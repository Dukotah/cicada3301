# T1 chroma follow-up — the LP "RGB modification" resolved

The armada's T1 lead ("visible RGB modification in the runes, key never found") is
resolved here. The signal is **genuine saturated red ink** (~#C80000, RGB ≈ 187,2,3),
not a JPEG artifact: it sits on the ink strokes (not high-gradient edges), and only the
red channel is offset (G≈B) — a deliberate Cr-only mark.

It is a **known LP feature** (present in 24 local relikd pages), selectively marking the
drop-cap + section-opening word(s) + dot ornaments. Correction to the armada note: the
three files are full 2400×3600 **LP2 pages** (not magic-square cells), and 167 also
carries red (a central ornament) — so it is **not** a clean control.

- `chroma_analysis.py` — reproduces the red detection + `marked_*.png` evidence.
- `marked_{107,167,229}.png` — red-only glyphs (kept as evidence).
- Source JPEGs are gitignored (re-download from scream314 stage10).

The genuinely-untested angle — the red runes as a **selection** — is extracted and
cryptanalytically tested in `../redrune/`. **Verdict: decorative rubrication (the red
re-states each page's own opening words), cryptographically null.**
