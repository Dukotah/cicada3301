"""L3 step 4 — cryptanalyze the extracted bitstreams (due diligence, low prior).

The characterization showed the anomaly is a constant DC red offset (rubrication),
so the mask bitstreams are expected to be noise. We still run the standard closing
battery on the mask LSB-R byte streams (the lowest-entropy readings): header-hunt
after transforms (raw / bit-invert / byte-reverse / nibble-swap / XOR 0x00..0xFF)
and, if the byte count is rune-compatible, map to base-29 and score with the LP
scorer. Report the best score vs the break threshold.
"""
import os, sys, glob, gzip, math
import numpy as np

OUT = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round29/L3-chroma-bitstream"
ROOT = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus"
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "analysis"))

MAGICS = [b"\x1f\x8b", b"PK\x03\x04", b"\x89PNG", b"\xff\xd8\xff", b"-----BEGIN",
          b"BZh", b"7z\xbc\xaf", b"Rar!", b"%PDF", b"\x42\x5a\x68"]

def hunt(bs):
    hits = []
    transforms = {
        "raw": bs,
        "invert": bytes(b ^ 0xFF for b in bs),
        "reverse": bs[::-1],
        "nibswap": bytes(((b<<4)|(b>>4))&0xFF for b in bs),
    }
    for x in range(256):
        transforms[f"xor{x:02x}"] = bytes(b ^ x for b in bs)
    for tname, t in transforms.items():
        for m in MAGICS:
            idx = t.find(m)
            if idx != -1 and idx < 4:
                hits.append((tname, m, idx))
        try:
            g = gzip.decompress(t)
            hits.append((tname, "GZIP_OK", len(g)))
        except Exception:
            pass
    return hits

def try_lp_score(bs):
    """If byte count maps to a plausible rune count, score as base-29."""
    try:
        from lp import gematria as gp, score as _score
    except Exception as e:
        return f"(scorer import failed: {e})"
    N = gp.N; SC = _score.default()
    # interpret each byte mod 29 as a rune index
    idxs = [b % N for b in bs]
    if len(idxs) < 10:
        return "(too short)"
    # score first 2000 runes
    seg = idxs[:2000]
    s = SC.score_norm(gp.indices_to_translit(seg))
    return round(float(s), 3)

if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(OUT, "bits_dl_*_mask_lsbR_*.bin")) +
                   glob.glob(os.path.join(OUT, "bits_dl_*_mask_mag_*.bin")))
    print(f"cryptanalyzing {len(files)} mask bitstreams (header-hunt + LP score)\n")
    best = None
    for f in files:
        bs = open(f, "rb").read()
        hits = hunt(bs)
        sc = try_lp_score(bs)
        name = os.path.basename(f)
        print(f"{name:44s} nbytes={len(bs):6d}  hdr_hits={len(hits)}  lp_score={sc}")
        if hits:
            print("     HITS:", hits[:5])
        if isinstance(sc, float) and (best is None or sc > best[0]):
            best = (sc, name)
    print()
    if best:
        print(f"best LP score: {best[0]} ({best[1]})  | LP break threshold = -5.2, English ~ -4.0, noise floor ~ -7.5")
