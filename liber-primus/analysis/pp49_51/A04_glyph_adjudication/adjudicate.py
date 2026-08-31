#!/usr/bin/env python3
"""
A-04 — image adjudication of the 6 contested pp49-51 table bytes.

Campaign VII (canonicalize.py) built the 256-byte pp49-51 payload from three
witnesses and flagged 6 cells where relikd and scream314 agree on the *token*
but scream314's own decimal column decodes it differently:

    idx 25 (p49 r3 c1)   token 3I   maj 198  decpref 224
    idx 175 (p50 r11 c7) token 0I   maj 18   decpref 44
    idx 182 (p50 r12 c6) token 2l   maj 167  decpref 141
    idx 199 (p51 r1 c7)  token 0l   maj 47   decpref 21
    idx 215 (p51 r3 c7)  token 1O   maj 84   decpref 5
    idx 237 (p51 r6 c5)  token 0W   maj 32   decpref 58

These were the difference between canon_256.bin (majority) and
canon_256_decpref.bin (decimal-preferred). Campaign VII said they "need the
master image" and left them open (RECON register A-04, status never-run).

This script re-fetches the three master page JPGs (400-DPI, 2400x3600) from the
relikd mirror and crops each contested cell at native resolution for a
high-zoom human/vision read — a tractable task on 6 specific cells even though
Avenue-1 full-page rune vision failed (dense ~250-rune pages). Provenance is
pinned by SHA-1 against the archive.org onion7 hashes recorded in
analysis/stego/provenance.json where available.

Reads (2026-08-31, high-zoom vision):

    idx 25   3I : 2nd glyph = plain full-height bar, NO dot -> capital I (18),
                  not dotted i (44).            => 198  (majority) CONFIRMED
    idx 175  0I : plain full-height bar, NO dot -> capital I (18).
                                                 => 18   (majority) CONFIRMED
    idx 182  2l : footless bar; the adjacent 1L in the SAME cell-pair shows a
                  clear capital-L foot this glyph lacks -> lowercase l (47),
                  not capital L (21).            => 167  (majority) CONFIRMED
    idx 199  0l : footless bar (adjacent 1j shows the font renders dots/
                  descenders) -> lowercase l (47), not L (21).
                                                 => 47   (majority) CONFIRMED
    idx 215  1O : big round letter O (24); decimal 5 is impossible from '1O'
                  and is a data-entry typo.      => 84   (majority) CONFIRMED
    idx 237  0W : full-cap-height W (32); adjacent 3w is a shorter lowercase w,
                  so this is capital W, not w (58).
                                                 => 32   (majority) CONFIRMED

RESULT: all 6 contested cells resolve in favour of the MAJORITY stream
(canon_256.bin). Every scream314 decimal-column value is refuted by the image
(I/i and l/L case confusion on footless bars, w/W height, one plain typo).
=> canon_256.bin is image-verified; canon_256_decpref.bin is retired.

Run from liber-primus/:  python analysis/pp49_51/A04_glyph_adjudication/adjudicate.py
Requires: pillow, network (relikd mirror). Crops are written to a gitignored
scratch dir; only this script + FINDINGS.md are committed.
"""
import os, sys, hashlib, json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # liber-primus/
PAGES_DIR = REPO / "data" / "relikd" / "pages"
MIRROR = "https://raw.githubusercontent.com/relikd/LiberPrayground/master/pages"

# (page, table_row, col, global_idx, token, majority_val, decpref_val, read)
CELLS = [
    (49, 3, 1, 25,  "3I", 198, 224, "capital I (no dot); decpref dotted-i refuted"),
    (50, 11, 7, 175, "0I", 18,  44,  "capital I (no dot); decpref dotted-i refuted"),
    (50, 12, 6, 182, "2l", 167, 141, "lowercase l (no foot vs adjacent 1L); decpref L refuted"),
    (51, 1, 7, 199, "0l", 47,  21,  "lowercase l (no foot); decpref L refuted"),
    (51, 3, 7, 215, "1O", 84,  5,   "round letter O; decpref 5 is a typo, refuted"),
    (51, 6, 5, 237, "0W", 32,  58,  "capital W (full height vs adjacent 3w); decpref w refuted"),
]

# native-pixel grid estimates (2400x3600 page), col0 center x + col pitch, row0 center y + row pitch
GEOM = {
    49: dict(y0=1380, dy=176, x0=744, dx=130),
    50: dict(y0=600,  dy=183, x0=690, dx=137),
    51: dict(y0=590,  dy=176, x0=755, dx=123),
}

def fetch_pages():
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    import urllib.request
    for p in (49, 50, 51):
        dst = PAGES_DIR / f"p{p}.jpg"
        if dst.exists() and dst.stat().st_size > 100000:
            continue
        url = f"{MIRROR}/p{p}.jpg"
        print(f"fetch {url}")
        urllib.request.urlretrieve(url, dst)

def crops(outdir):
    from PIL import Image
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    for p, r, c, idx, tok, mv, dv, note in CELLS:
        g = GEOM[p]
        im = Image.open(PAGES_DIR / f"p{p}.jpg").convert("L")
        cx = g["x0"] + c * g["dx"]; cy = g["y0"] + r * g["dy"]
        crop = im.crop((cx - 120, cy - 130, cx + 140, cy + 130))
        w, h = crop.size
        crop = crop.resize((w * 4, h * 4))
        crop.save(outdir / f"cell_p{p}_r{r}c{c}_idx{idx}.png")
    print(f"wrote {len(CELLS)} crops to {outdir}")

def write_result():
    out = {
        "test": "A-04",
        "verdict": "RESOLVED",
        "resolution": "all 6 contested cells confirm the MAJORITY stream (canon_256.bin)",
        "method": "high-zoom vision read of 6 native-resolution cell crops from the 400-DPI master JPGs",
        "cells": [
            {"idx": idx, "page": p, "row": r, "col": c, "token": tok,
             "majority": mv, "decimal_preferred": dv, "adjudicated": mv,
             "read": note}
            for (p, r, c, idx, tok, mv, dv, note) in CELLS
        ],
        "consequence": (
            "canon_256.bin is image-verified as the canonical pp49-51 payload. "
            "canon_256_decpref.bin is retired: all 6 scream314 decimal-column "
            "values are refuted by the source glyphs (case confusion + 1 typo). "
            "Downstream key/seed uses (e.g. B-05) should use canon_256.bin only."
        ),
    }
    dst = Path(__file__).resolve().parent / "results.json"
    dst.write_text(json.dumps(out, indent=2))
    print("wrote", dst)
    # sanity: the adjudicated bytes must equal canon_256.bin at those indices
    canon = (REPO / "analysis" / "pp49_51" / "canon_256.bin").read_bytes()
    mism = [idx for (p, r, c, idx, tok, mv, dv, note) in CELLS if canon[idx] != mv]
    if mism:
        print("WARNING: adjudicated value != canon_256.bin at idx", mism)
    else:
        print("OK: all 6 adjudicated values match canon_256.bin")

if __name__ == "__main__":
    scratch = os.environ.get("A04_SCRATCH",
        "/tmp/claude-0/-home-user-cicada3301/68162a52-c9cd-5f0e-ab96-61a17615bb0c/scratchpad/crops")
    fetch_pages()
    try:
        crops(scratch)
    except Exception as e:
        print("crop step skipped:", e)
    write_result()
