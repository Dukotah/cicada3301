"""L3 step 2 — read the confirmed anomaly plane as a raw BITSTREAM, many ways.

For each image (107, 229, and 167 control) and each mask, we walk the modified
pixels in several orders and derive a bit per pixel several ways, then measure the
resulting bit sequence: length, Shannon entropy (bit-level & byte-level), whether
it begins with a known magic header, and whether it decodes to printable ASCII.

Orderings:  raster (row-major), column-major, boustrophedon (serpentine rows).
Bit definitions per modified pixel:
  - lsbR / lsbG / lsbB : LSB of that channel
  - sign               : sign of (R-G) deviation  (1 if R>G else 0)
  - mag                : |R-G| > median(|R-G| over mask)  (magnitude threshold)
Also, for completeness, LSB of ALL interior pixels (not just the >thr mask), which
is the classic stego plane.
"""
import os, sys, json, math, gzip, io
import numpy as np

OUT = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round29/L3-chroma-bitstream"

MAGICS = {
    b"\x1f\x8b": "gzip",
    b"PK\x03\x04": "zip",
    b"\x89PNG": "png",
    b"\xff\xd8\xff": "jpeg",
    b"-----BEGIN": "pgp/pem",
    b"BZh": "bzip2",
    b"\x37\x7a\xbc\xaf": "7z",
    b"Rar!": "rar",
    b"OggS": "ogg",
    b"%PDF": "pdf",
    b"SQLi": "sqlite",
}

def shannon_bits(bits):
    if len(bits) == 0: return 0.0
    p1 = bits.mean(); p0 = 1 - p1
    h = 0.0
    for p in (p0, p1):
        if p > 0: h -= p * math.log2(p)
    return h

def byte_entropy(bs):
    if len(bs) == 0: return 0.0
    counts = np.bincount(np.frombuffer(bs, dtype=np.uint8), minlength=256)
    p = counts / counts.sum()
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())

def bits_to_bytes(bits):
    n = (len(bits) // 8) * 8
    b = bits[:n].reshape(-1, 8)
    vals = (b * (1 << np.arange(7, -1, -1))).sum(axis=1).astype(np.uint8)
    return vals.tobytes()

def check_magic(bs):
    hits = []
    for m, name in MAGICS.items():
        if bs[:len(m)] == m:
            hits.append(name)
    return hits

def printable_ratio(bs):
    if not bs: return 0.0
    arr = np.frombuffer(bs, dtype=np.uint8)
    pr = ((arr >= 32) & (arr < 127)) | (arr == 9) | (arr == 10) | (arr == 13)
    return float(pr.mean())

def try_gunzip(bs):
    try:
        return gzip.decompress(bs)[:64]
    except Exception:
        return None

def order_indices(ys, xs, mode, W):
    """Return a permutation of the mask-pixel list into the requested walk order."""
    if mode == "raster":
        key = ys.astype(np.int64) * W + xs
    elif mode == "column":
        key = xs.astype(np.int64) * 100000 + ys
    elif mode == "boust":
        # serpentine: even rows L->R, odd rows R->L
        xx = np.where(ys % 2 == 0, xs, W - 1 - xs)
        key = ys.astype(np.int64) * W + xx
    else:
        raise ValueError(mode)
    return np.argsort(key, kind="stable")

def analyze_image(name):
    rgb = np.load(os.path.join(OUT, f"rgb_{name}.npy")).astype(np.int16)
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    RmG = np.load(os.path.join(OUT, f"RmG_{name}.npy")).astype(np.int16)
    mask = np.load(os.path.join(OUT, f"mask_{name}.npy"))
    interior = np.load(os.path.join(OUT, f"interior_{name}.npy"))
    H, W = mask.shape
    results = []

    def emit(tag, bits):
        bits = np.asarray(bits, dtype=np.uint8)
        bs = bits_to_bytes(bits)
        rec = {
            "image": name, "reading": tag, "nbits": int(len(bits)),
            "nbytes": len(bs), "bit_entropy": round(shannon_bits(bits), 4),
            "bit_ones_frac": round(float(bits.mean()), 4) if len(bits) else 0.0,
            "byte_entropy": round(byte_entropy(bs), 4),
            "printable_ratio": round(printable_ratio(bs), 4),
            "magic": check_magic(bs),
            "head_hex": bs[:16].hex(),
            "head_ascii": "".join(chr(c) if 32 <= c < 127 else "." for c in bs[:32]),
        }
        gz = try_gunzip(bs)
        if gz is not None:
            rec["gunzip_head"] = gz.hex()
        results.append(rec)
        # dump the bytes for the strong-signal images for downstream crypto
        if name in ("dl_107.jpg", "dl_229.jpg"):
            safe = tag.replace(" ", "_").replace("/", "-")
            with open(os.path.join(OUT, f"bits_{name}_{safe}.bin"), "wb") as f:
                f.write(bs)

    # ---- mask-restricted readings ----
    ys, xs = np.where(mask)
    med = np.median(np.abs(RmG[mask])) if mask.sum() else 0
    for mode in ("raster", "column", "boust"):
        perm = order_indices(ys, xs, mode, W)
        oy, ox = ys[perm], xs[perm]
        emit(f"mask lsbR {mode}", (R[oy, ox] & 1))
        emit(f"mask lsbG {mode}", (G[oy, ox] & 1))
        emit(f"mask lsbB {mode}", (B[oy, ox] & 1))
        emit(f"mask sign {mode}", (RmG[oy, ox] > 0).astype(np.uint8))
        emit(f"mask mag {mode}", (np.abs(RmG[oy, ox]) > med).astype(np.uint8))

    # ---- full-interior LSB planes (classic stego) ----
    iy, ix = np.where(interior)
    for mode in ("raster",):
        perm = order_indices(iy, ix, mode, W)
        oy, ox = iy[perm], ix[perm]
        emit(f"interior lsbR {mode}", (R[oy, ox] & 1))
        emit(f"interior lsbG {mode}", (G[oy, ox] & 1))
        emit(f"interior lsbB {mode}", (B[oy, ox] & 1))
        emit(f"interior sign {mode}", (RmG[oy, ox] > 0).astype(np.uint8))
    return results

if __name__ == "__main__":
    allr = []
    for n in ["dl_107.jpg", "dl_229.jpg", "dl_167.jpg"]:
        allr.extend(analyze_image(n))
    with open(os.path.join(OUT, "bitstream_results.json"), "w") as f:
        json.dump(allr, f, indent=2)
    # print a compact table
    print(f"{'image':12s} {'reading':22s} {'nbits':>7s} {'bitH':>6s} {'ones':>6s} {'byteH':>6s} {'prnt':>5s} {'magic':>8s}")
    for r in allr:
        print(f"{r['image']:12s} {r['reading']:22s} {r['nbits']:7d} {r['bit_entropy']:6.3f} "
              f"{r['bit_ones_frac']:6.3f} {r['byte_entropy']:6.3f} {r['printable_ratio']:5.2f} "
              f"{','.join(r['magic']) if r['magic'] else '-':>8s}")
    # highlight anything interesting
    print("\n--- FLAGS (magic hit / low byte-entropy / high printable) ---")
    for r in allr:
        flag = []
        if r["magic"]: flag.append("MAGIC:" + ",".join(r["magic"]))
        if r["nbytes"] >= 8 and r["byte_entropy"] < 6.5: flag.append(f"lowH={r['byte_entropy']}")
        if r["printable_ratio"] > 0.85 and r["nbytes"] >= 8: flag.append(f"printable={r['printable_ratio']}")
        if r.get("gunzip_head"): flag.append("GUNZIP_OK")
        if flag:
            print(f"  {r['image']} | {r['reading']} | {' '.join(flag)} | ascii='{r['head_ascii']}'")
