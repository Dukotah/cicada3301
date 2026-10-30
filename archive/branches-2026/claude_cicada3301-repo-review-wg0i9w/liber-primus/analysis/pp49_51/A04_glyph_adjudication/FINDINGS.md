# A-04 — the 6 contested pp49–51 bytes, adjudicated by image

_2026-08-31. Closes RECON register item **A-04** (`never-run` since Campaign VII,
2026-07-06). Reproduce: `python analysis/pp49_51/A04_glyph_adjudication/adjudicate.py`._

## The open item

Campaign VII characterized pp49–51 as a 256-byte high-entropy payload and built two
canonical variants that differ in exactly **6 of 256 bytes**:

- `canon_256.bin` — majority vote of three witnesses (relikd tokens, scream314 tokens,
  scream314 decimal column).
- `canon_256_decpref.bin` — prefers scream314's decimal column on any disagreement.

The 6 differing cells were the ones where **both token witnesses agree** but scream314's
own decimal column decodes the token to a different value. Campaign VII flagged them as
needing the master image (the project's glyph classifier is rune-trained and cannot read
Latin/digit table characters) and left A-04 open. It is the last honest open item on the
one object in the corpus that is *not* OTP-class runic ciphertext.

## Method

The tables on pp49–51 are Latin-letter/digit two-character base-60 tokens, not runes, and
each disputed cell is a single glyph. Avenue-1 vision failed on dense ~250-rune *runic*
pages, but reading 6 specific Latin cells at high zoom is a different, tractable task. I
re-fetched the three 400-DPI master JPGs (2400×3600) from the relikd mirror and cropped
each contested cell at native resolution (≈260×260 px, upscaled 4×) for a direct read,
using the neighbouring cells in each row as an in-image case reference.

## Result — all 6 confirm the majority stream

| idx | page/cell | token | majority | decimal-pref | image read | verdict |
|---|---|---|---|---|---|---|
| 25  | p49 r3 c1  | `3I` | **198** | 224 | plain full-height bar, **no dot** → capital `I` (18), not dotted `i` (44) | majority |
| 175 | p50 r11 c7 | `0I` | **18**  | 44  | plain full-height bar, **no dot** → capital `I` (18) | majority |
| 182 | p50 r12 c6 | `2l` | **167** | 141 | **footless** bar; adjacent `1L` shows the capital-L foot this glyph lacks → lowercase `l` (47), not `L` (21) | majority |
| 199 | p51 r1 c7  | `0l` | **47**  | 21  | footless bar (adjacent `1j` proves the font draws dots/descenders) → lowercase `l` (47), not `L` (21) | majority |
| 215 | p51 r3 c7  | `1O` | **84**  | 5   | big round letter `O` (24); decimal `5` is impossible from `1O` — a data-entry typo | majority |
| 237 | p51 r6 c5  | `0W` | **32**  | 58  | full-cap-height `W` (32); adjacent `3w` is a shorter lowercase `w` → capital `W`, not `w` (58) | majority |

Every scream314 **decimal-column** value is refuted by the source glyph. Five are the
classic footless-bar / height confusions (`I` vs dotted `i`, lowercase `l` vs capital `L`,
capital `W` vs lowercase `w`); one (idx 215) is a plain typo. The token witnesses — which
both read these correctly — win in all six.

`adjudicate.py` re-checks its six adjudicated values against `canon_256.bin` on every run
and reports `OK: all 6 adjudicated values match canon_256.bin`.

## Consequence

- **`canon_256.bin` is image-verified** as the canonical pp49–51 payload.
- **`canon_256_decpref.bin` is retired** — it encodes six scream314 decimal-entry errors,
  not a real reading ambiguity. Keep the file for provenance but do not use it as an input.
- Any downstream use of pp49–51 as key/seed/PRF material (e.g. **B-05**, pp49–51 expanded
  as a PRF seed) should use `canon_256.bin` exclusively. This removes a 6-byte fork from
  the highest-prior internal seed input.

This does not solve or reopen anything on its own — pp49–51 remains the external-key-class
payload Campaign VII proved it to be — but it closes the last flagged reading ambiguity on
that payload and pins its canonical bytes.
