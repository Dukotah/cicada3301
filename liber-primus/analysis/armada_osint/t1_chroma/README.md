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

## 2026-07-28 re-attack (external lane) — broadened key sweep, CLOSED
- Confirmed the ~328KB "5x5 rune" target is dl_1033.jpg (1327x1427, 328KB), NOT dl_onion3.jpg (175KB, grayscale). dl_1033 carries the visible chroma (21% red-ink pixels).
- No-key OutGuess on dl_1033 reproduces the KNOWN 2013 RSA message ("Welcome. Good luck. 3301. e=65537, n=755791..."). The payload needs NO password.
- Ran 40 NEW OutGuess keys (PARABLE/KOAN/INSTAR case-variants, 3.30.1/3.3.0.1, epiphany/path-lies-empty/welcome/good-luck, magic-square word-grid concatenations in row/col/diag orders, gematria-prime words) NOT in the prior 60-key list. All -> high-entropy (>7.9) capacity-length garbage = OutGuess default-key keystream artifact. NULL.
- steghide across all 7 images x ~100 keys incl empty passphrase -> zero extraction. NULL.
- LSB(R/G/B) of dl_1033 -> ent 7.99, no ASCII structure -> no independent spatial payload.
- VERDICT: the "provable hidden data, key never found" claim is DEBUNKED. The visible RGB modification is the OutGuess embedding of the already-known keyless 2013 message. No external key, no new payload. Lead fully closed.
