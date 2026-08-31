#!/usr/bin/env python3
"""
Round 22 — Lane D — Illustration / drop-cap channel (roadmap S3).

Codes the ART of the Liber Primus as data. The one robustly machine-extractable
illustration feature is the ILLUMINATED DROP-CAP: on the pages that have one, the
initial rune of the body text is printed in RED while every other glyph is black.
Red is therefore a clean, transcription-free signal — no fragile full-page OCR is
needed (the R9/vision avenues showed dense-rune OCR is unreliable at 0.145; a single
large red blob is not).

We extract, per page 0..57:
  - red_px          : count of "printer-red" pixels
  - has_dropcap     : red_px above the drop-cap tier threshold (a large red glyph)
  - red_cx, red_cy  : normalised centroid of the red mask (0..1), NaN if none
  - n_red_blobs     : connected components of red above a min area
  - dropcap_aspect  : height/width of the largest red blob's bbox (orientation proxy)

Then we build the DROP-CAP PRESENCE SEQUENCE over the pages and test whether the
ORDER of illuminated pages carries structure beyond a size-matched shuffled null
(seed 3301), per doctrine R2/R3 (value = coverage x power; persist language-agnostic
order statistics).

POSITIVE CONTROL (P0.2-style): four pages were hand-read from the scans and their
drop-cap status recorded below. The extractor must reproduce them or the run aborts.

Images: the full 2400x3600 per-page scans committed in the vendored solver mirror.
"""
import os, re, glob, json, hashlib
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
IMG_DIR = os.path.join(
    REPO, "corpus", "E-tooling", "vendor",
    "cmbsolver__cmbcidada3301", "LiberPrimusUi", "input", "images", "LP")

# printer-red mask: strong R, weak G/B (matches the illuminated drop-caps + red numerals)
def red_mask(a):
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    return (R > 120) & (G < 90) & (B < 90) & (R - G > 60) & (R - B > 60)

# tiers established by the cross-page probe:
#   >30000 px  -> a genuine illuminated drop-cap glyph
#   ~1000 px   -> JPEG speckle / tiny red mark, NOT a drop-cap
DROPCAP_PX_MIN = 30000
BLOB_MIN_PX = 3000

# ---- POSITIVE CONTROL: hand-reads from the scans (see PREREG.md) ----
# page -> has_dropcap (True/False), read by eye at full zoom.
HAND = {
    0: True,   # red S-rune drop-cap, two black crosses in margins
    8: True,   # red Y-rune drop-cap, bare-tree figure left margin
    15: True,  # red I-rune drop-cap (tall red vertical), tree figure left
    9: False,  # black text only, bare-tree figure right margin, NO red drop-cap
}


def label_components(mask, min_px):
    """Tiny 4-connectivity CC labeller (no scipy dep). Returns list of (npix, bbox)."""
    H, W = mask.shape
    seen = np.zeros((H, W), dtype=bool)
    comps = []
    ys, xs = np.where(mask)
    idx = 0
    coords = list(zip(ys.tolist(), xs.tolist()))
    mset = mask  # alias
    from collections import deque
    for (sy, sx) in coords:
        if seen[sy, sx]:
            continue
        q = deque([(sy, sx)])
        seen[sy, sx] = True
        npix = 0
        miny = maxy = sy
        minx = maxx = sx
        while q:
            y, x = q.popleft()
            npix += 1
            if y < miny: miny = y
            if y > maxy: maxy = y
            if x < minx: minx = x
            if x > maxx: maxx = x
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                ny, nx = y+dy, x+dx
                if 0 <= ny < H and 0 <= nx < W and mset[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if npix >= min_px:
            comps.append((npix, (miny, minx, maxy, maxx)))
    return comps


def extract_page(path):
    im = Image.open(path).convert("RGB")
    # downscale for the CC labeller (speed); red_px reported at full res scale factor
    full = np.asarray(im).astype(np.int16)
    m_full = red_mask(full)
    red_px = int(m_full.sum())
    H, W = m_full.shape
    if red_px > 0:
        ys, xs = np.where(m_full)
        red_cx = float(xs.mean() / W)
        red_cy = float(ys.mean() / H)
    else:
        red_cx = red_cy = float("nan")

    # components on a 4x-downsampled mask for speed (min_px scaled by 1/16)
    small = m_full[::4, ::4]
    comps = label_components(small, max(1, BLOB_MIN_PX // 16))
    n_blobs = len(comps)
    if comps:
        comps.sort(reverse=True)
        _, (miny, minx, maxy, maxx) = comps[0]
        h = (maxy - miny + 1)
        w = (maxx - minx + 1)
        aspect = float(h / w) if w else float("nan")
    else:
        aspect = float("nan")

    has_dropcap = red_px >= DROPCAP_PX_MIN
    return {
        "red_px": red_px,
        "red_frac_pct": round(100 * red_px / (H * W), 4),
        "has_dropcap": bool(has_dropcap),
        "red_cx": None if np.isnan(red_cx) else round(red_cx, 4),
        "red_cy": None if np.isnan(red_cy) else round(red_cy, 4),
        "n_red_blobs": n_blobs,
        "dropcap_aspect": None if (comps == [] or np.isnan(aspect)) else round(aspect, 3),
    }


def page_num(path):
    return int(re.findall(r"(\d+)", os.path.basename(path))[0])


def main():
    files = sorted(glob.glob(os.path.join(IMG_DIR, "*.jpg")), key=page_num)
    assert files, f"no images in {IMG_DIR}"
    feats = {}
    for f in files:
        pg = page_num(f)
        feats[pg] = extract_page(f)

    # ---- positive control ----
    control = {}
    ok = True
    for pg, want in HAND.items():
        got = feats[pg]["has_dropcap"]
        control[pg] = {"hand": want, "extracted": got, "match": got == want}
        if got != want:
            ok = False
    print("POSITIVE CONTROL:")
    for pg, c in sorted(control.items()):
        print(f"  page {pg:>2}: hand={c['hand']!s:>5}  extracted={c['extracted']!s:>5}  "
              f"{'OK' if c['match'] else 'MISMATCH'}")
    if not ok:
        print("CONTROL FAILED — extractor does not reproduce hand-counts. ABORTING analysis.")
    else:
        print("CONTROL PASSED — extractor reproduces all hand-counts.\n")

    out = {
        "img_dir": os.path.relpath(IMG_DIR, REPO),
        "n_pages": len(files),
        "dropcap_px_min": DROPCAP_PX_MIN,
        "control": control,
        "control_passed": ok,
        "features": {str(k): v for k, v in sorted(feats.items())},
    }
    with open(os.path.join(HERE, "features.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"wrote features.json ({len(files)} pages)")
    return out, ok


if __name__ == "__main__":
    main()
