"""L3 step 1 — isolate the CONFIRMED interior chroma anomaly as a mask.

Prior armada (armada_osint) confirmed a genuine interior chromatic modification in
107 & 229: interior |R-G| > edge |R-G| (ratios 0.36 / 0.62), while control 167 was
clean of *that specific* effect. This script rebuilds that interior-vs-edge |R-G|
signal, quantifies it for 107/229/167, and writes a per-image anomaly mask + the
diff planes used downstream by bitstream.py.

The distinction from redrune/: redrune tested the SATURATED RED rubrication
(R~187,G~2) as a rune SELECTION. Here we characterize the low-amplitude interior
|R-G| deviation of the ink INTERIOR (not saturated red, not edges) and read it as a
raw payload plane.
"""
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage

ART = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/artifacts"
OUT = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round29/L3-chroma-bitstream"

def load(name):
    im = Image.open(os.path.join(ART, name)).convert("RGB")
    return np.asarray(im).astype(np.int16)

def characterize(name):
    a = load(name)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    L = (0.299 * R + 0.587 * G + 0.114 * B)
    RmG = (R - G).astype(np.float32)
    absRmG = np.abs(RmG)

    # ink = dark strokes
    ink = L < (L.mean() - 1.0 * L.std())
    # edges = high luminance gradient (JPEG ringing lives here)
    gy, gx = np.gradient(L)
    grad = np.hypot(gx, gy)
    edge = grad > np.percentile(grad, 99)
    # interior of ink = ink pixels NOT on a strong luminance edge (erode ink, remove edge)
    ink_er = ndimage.binary_erosion(ink, iterations=2)
    interior = ink_er & (~edge)
    flat = (L > (L.mean() - 0.5 * L.std())) & (~edge)  # background paper

    stats = {
        "image": name,
        "shape": list(a.shape),
        "abs_RmG_interior_mean": float(absRmG[interior].mean()) if interior.sum() else None,
        "abs_RmG_edge_mean": float(absRmG[edge].mean()) if edge.sum() else None,
        "abs_RmG_flat_bg_mean": float(absRmG[flat].mean()) if flat.sum() else None,
        "interior_over_edge_ratio": None,
        "interior_px": int(interior.sum()),
        "edge_px": int(edge.sum()),
        # signed skew: is R systematically > G (positive chroma push) in interior?
        "RmG_interior_signed_mean": float(RmG[interior].mean()) if interior.sum() else None,
        "RmG_edge_signed_mean": float(RmG[edge].mean()) if edge.sum() else None,
        "RmG_interior_pos_frac": float((RmG[interior] > 0).mean()) if interior.sum() else None,
    }
    if stats["abs_RmG_edge_mean"]:
        stats["interior_over_edge_ratio"] = stats["abs_RmG_interior_mean"] / stats["abs_RmG_edge_mean"]

    # anomaly mask: interior ink pixels where |R-G| exceeds a modest threshold
    # (the actual "modified" pixels we will read as a bitstream plane)
    for thr in (3, 5, 8, 12):
        m = interior & (absRmG > thr)
        stats[f"mask_px_thr{thr}"] = int(m.sum())

    # persist the chosen mask (thr=5) + the raw RmG plane restricted to interior
    mask = interior & (absRmG > 5)
    np.save(os.path.join(OUT, f"mask_{name}.npy"), mask)
    np.save(os.path.join(OUT, f"RmG_{name}.npy"), RmG.astype(np.int16))
    np.save(os.path.join(OUT, f"interior_{name}.npy"), interior)
    # also save raw channels for LSB reads
    np.save(os.path.join(OUT, f"rgb_{name}.npy"), a.astype(np.uint8))
    return stats

if __name__ == "__main__":
    names = ["dl_107.jpg", "dl_229.jpg", "dl_167.jpg"]
    out = [characterize(n) for n in names]
    print(json.dumps(out, indent=2))
    with open(os.path.join(OUT, "mask_stats.json"), "w") as f:
        json.dump(out, f, indent=2)
