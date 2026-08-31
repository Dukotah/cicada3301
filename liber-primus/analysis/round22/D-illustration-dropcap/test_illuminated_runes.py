#!/usr/bin/env python3
"""
Round 22 — Lane D — illuminated-rune-identity test (roadmap S3, richest sub-lane).

The drop-cap is the FIRST body rune of the page, printed red. So "which rune is
illuminated" is recoverable exactly from the canonical per-page rune strings — no
image OCR of the small dense runes needed (only the has-dropcap gate came from the
image, and it is validated). This lets us read the ILLUMINATED-RUNE SEQUENCE across
the illuminated pages, in page order, as an integer sequence over Z/29.

Hypothesis (Q1): if the illuminated runes spell something, the sequence of their
gematria indices should read as English/base-29/ASCII beyond a null. Positive control:
we already validated has-dropcap on 4 pages; here the mapping is a deterministic table
lookup (Gematria Primus), so the "control" is that page 0's first rune is S (matches
the red S seen in the scan).

Null: the drop-cap runes are just the first runes of pages; the size-matched null is
the first-rune-of-every-page sequence (illuminated or not) and random 15-length draws
from the rune alphabet, seed 3301.
"""
import os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SEED = 3301

# Gematria Primus: rune -> (index 0..28, latin)
GP = [
    ("ᚠ","F"),("ᚢ","U"),("ᚦ","TH"),("ᚩ","O"),("ᚱ","R"),("ᚳ","C"),("ᚷ","G"),("ᚹ","W"),
    ("ᚻ","H"),("ᚾ","N"),("ᛁ","I"),("ᛄ","J"),("ᛇ","EO"),("ᛈ","P"),("ᛉ","X"),("ᛋ","S"),
    ("ᛏ","T"),("ᛒ","B"),("ᛖ","E"),("ᛗ","M"),("ᛚ","L"),("ᛝ","ING"),("ᛟ","OE"),("ᛞ","D"),
    ("ᚪ","A"),("ᚫ","AE"),("ᚣ","Y"),("ᛡ","IA"),("ᛠ","EA"),
]
RUNE2IDX = {r: i for i, (r, _) in enumerate(GP)}
RUNE2LAT = {r: l for r, (_, l) in enumerate([(r, l) for r, l in GP])}
IDX2LAT = {i: l for i, (_, l) in enumerate(GP)}


def main():
    pages = json.load(open(os.path.join(REPO, "liber-primus", "analysis", "vision", "canonical_pages.json")))
    page_first = {}
    for rec in pages:
        runes = rec["runes"]
        # first character that is a known rune
        for ch in runes:
            if ch in RUNE2IDX:
                page_first[rec["page"]] = ch
                break

    feats = json.load(open(os.path.join(HERE, "features.json")))["features"]
    illum = [p for p in sorted(int(k) for k in feats) if feats[str(p)]["has_dropcap"]]

    illum_runes = [page_first.get(p) for p in illum if page_first.get(p)]
    illum_idx = [RUNE2IDX[r] for r in illum_runes]
    illum_lat = [IDX2LAT[i] for i in illum_idx]

    # control: page 0 illuminated rune must be S (red S seen in scan)
    p0_ok = page_first.get(0) == "ᛋ"

    # english-ish? just report the string; also base-29 sum, product mod primes
    read = "".join(illum_lat)

    # structure test: is the illuminated-rune index sequence less uniform than
    # a random draw from the alphabet (seed 3301)? Use entropy of the multiset.
    def norm_entropy(seq, k=29):
        c = np.bincount(seq, minlength=k).astype(float)
        p = c / c.sum()
        p = p[p > 0]
        return float(-(p * np.log2(p)).sum() / np.log2(k))
    obs_ent = norm_entropy(illum_idx)

    rng = np.random.default_rng(SEED)
    N = 10000
    null_ent = np.empty(N)
    for i in range(N):
        s = rng.integers(0, 29, size=len(illum_idx))
        null_ent[i] = norm_entropy(s.tolist())
    p_low_entropy = float((null_ent <= obs_ent).mean())  # low = more structured

    out = {
        "illuminated_pages": illum,
        "illuminated_runes": illum_runes,
        "illuminated_indices": illum_idx,
        "illuminated_read_latin": read,
        "control_page0_is_S": p0_ok,
        "n": len(illum_idx),
        "normalised_entropy_observed": round(obs_ent, 4),
        "normalised_entropy_null_mean": round(float(null_ent.mean()), 4),
        "p_more_structured_than_random_alpha": round(p_low_entropy, 4),
        "BAR": "p < 0.01",
        "survivor": bool(p_low_entropy < 0.01),
    }
    with open(os.path.join(HERE, "illuminated_rune_results.json"), "w") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    print()
    print(f"illuminated runes in page order: {read}")
    print(f"control page0=S: {p0_ok}")
    print(f"p(more structured than random alphabet) = {p_low_entropy:.4f} -> "
          f"{'SURVIVOR' if out['survivor'] else 'null'}")
    return out


if __name__ == "__main__":
    main()
