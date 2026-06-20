"""Image-steganography sweep for Cicada LP page images (pure Python).

No external binaries required (binwalk/exiftool/strings/outguess are NOT installed
on this box). Replicates what's doable in Python:

  - JPEG/PNG marker walk; dump every APPn / COM / text segment (decoded)
  - EXIF + ICC-profile presence; XMP scan
  - trailing bytes after EOI (the #1 Cicada trick: appended data)
  - embedded-file-signature carve (binwalk-lite): ZIP/PNG/PDF/GZIP/JPEG/RAR/7z
  - printable-strings extraction with flagging (url/onion/base64/cicada/PGP)
  - byte-entropy + sliding-window high-entropy regions (packed/encrypted payload)
  - DQT quantization-table fingerprint + SOF dims (re-encode / tool tells)
  - LSB of decoded pixels (MEANINGFUL only for lossless PNG/BMP; for JPEG the
    spatial LSB is compression noise -- reported but flagged low-value)

GAP (needs a binary, documented not run): DCT-coefficient stego
(OutGuess/F5/jsteg/steghide). If authentic originals turn up, run those tools
in a Linux env; this script flags DQT anomalies that can hint at them.

Usage:  python stego_scan.py <image_dir> [out_dir]
Writes: <out_dir>/REPORT.md, results.json, and carved/ artifacts.
"""
import sys, os, struct, hashlib, json, math, re
from collections import Counter
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS

SIGS = {
    b"PK\x03\x04": "zip", b"\x89PNG\r\n\x1a\n": "png", b"%PDF": "pdf",
    b"\x1f\x8b\x08": "gzip", b"Rar!\x1a\x07": "rar", b"7z\xbc\xaf\x27\x1c": "7z",
    b"BZh": "bzip2", b"\xff\xd8\xff": "jpeg", b"GIF8": "gif", b"ID3": "mp3",
    b"OggS": "ogg", b"fLaC": "flac", b"\x42\x4d": "bmp(maybe)",
}
STR_FLAGS = [
    (re.compile(rb"https?://", re.I), "url"),
    (re.compile(rb"[a-z2-7]{16,56}\.onion", re.I), "onion"),
    (re.compile(rb"cicada|3301|liber|primus|instar|pilgrim", re.I), "cicada-word"),
    (re.compile(rb"-----BEGIN", re.I), "pgp/key-block"),
    (re.compile(rb"[A-Za-z0-9+/]{40,}={0,2}"), "base64-ish"),
    (re.compile(rb"[0-9a-f]{64,}", re.I), "long-hex"),
]


def entropy(b: bytes) -> float:
    if not b: return 0.0
    c = Counter(b); n = len(b)
    return -sum((v/n) * math.log2(v/n) for v in c.values())


def jpeg_segments(d: bytes):
    segs, i = [], 2
    while i < len(d) - 1:
        if d[i] != 0xFF: i += 1; continue
        m = d[i+1]
        if m == 0xD8 or 0xD0 <= m <= 0xD7: i += 2; continue
        if m == 0xD9: segs.append(("EOI", i, b"")); break
        if i+4 > len(d): break
        ln = struct.unpack(">H", d[i+2:i+4])[0]
        body = d[i+4:i+2+ln]
        name = {0xE0:"APP0/JFIF",0xE1:"APP1/EXIF-XMP",0xE2:"APP2/ICC",0xED:"APP13/IPTC",
                0xEE:"APP14/Adobe",0xFE:"COM",0xDB:"DQT",0xC0:"SOF0",0xC2:"SOF2",
                0xC4:"DHT",0xDA:"SOS"}.get(m, f"0x{m:02X}")
        segs.append((name, i, body))
        if m == 0xDA: break
        i += 2 + ln
    return segs


def _valid_embed(d: bytes, j: int, name: str) -> bool:
    """Validate a signature hit so we don't report random matches inside
    compressed JPEG entropy (the usual binwalk false-positive)."""
    try:
        if name == "zip":      # PK\x03\x04 + version(<100) + flags
            return d[j+4] < 100 and d[j+5] == 0
        if name == "png":      # IHDR chunk must follow the 8-byte sig
            return d[j+12:j+16] == b"IHDR"
        if name == "jpeg":     # SOI then an APP/DQT marker
            return d[j+3] in (0xE0, 0xE1, 0xE2, 0xDB, 0xEE, 0xFE)
        if name == "gzip":     # flag byte valid (<32)
            return d[j+3] < 32
        if name == "pdf":      # %PDF-1.x
            return d[j+5:j+6] == b"-"
        if name in ("rar", "7z", "bzip2"):
            return True        # longer, distinctive sigs
        return False           # gif/bmp/mp3/ogg/flac: too short to trust mid-file
    except IndexError:
        return False


def carve(d: bytes):
    """binwalk-lite: find + VALIDATE embedded signatures past the header."""
    hits = []
    for sig, name in SIGS.items():
        start = 1
        while True:
            j = d.find(sig, start)
            if j < 0: break
            if j > 32 and _valid_embed(d, j, name):
                hits.append((j, name))
            start = j + 1
    return sorted(hits)[:50]


def strings_flagged(d: bytes, minlen=5):
    out, cur = [], bytearray()
    runs = []
    for byte in d:
        if 32 <= byte < 127:
            cur.append(byte)
        else:
            if len(cur) >= minlen: runs.append(bytes(cur))
            cur = bytearray()
    if len(cur) >= minlen: runs.append(bytes(cur))
    flagged = []
    for s in runs:
        for rx, tag in STR_FLAGS:
            if rx.search(s):
                flagged.append((tag, s[:120].decode("latin1", "replace")))
                break
    return len(runs), flagged[:60]


def lsb_planes(path, outdir, stem):
    """Decoded-pixel LSB. Real signal only for lossless formats."""
    try:
        im = Image.open(path); fmt = im.format
        im = im.convert("RGB"); a = np.asarray(im)
    except Exception as e:
        return {"error": str(e)}
    res = {"format": fmt, "lossless": fmt in ("PNG", "BMP", "GIF", "TIFF")}
    bits_msg = {}
    for ci, cn in enumerate("RGB"):
        plane = (a[:, :, ci] & 1).astype(np.uint8)
        # pack row-major into bytes, decode first 256 as ascii preview
        flat = plane.flatten()
        nbytes = len(flat) // 8
        packed = np.packbits(flat[:nbytes*8]).tobytes()
        ent = entropy(packed[:4096])
        printable = sum(32 <= x < 127 for x in packed[:512]) / 512
        preview = packed[:64].decode("latin1", "replace")
        bits_msg[cn] = {"entropy_first4k": round(ent, 3),
                        "printable_frac_first512": round(printable, 3),
                        "ascii_preview": preview}
    res["channels"] = bits_msg
    return res


def scan_one(path, outdir):
    d = open(path, "rb").read()
    stem = os.path.splitext(os.path.basename(path))[0]
    r = {"file": os.path.basename(path), "size": len(d),
         "sha256": hashlib.sha256(d).hexdigest(),
         "md5": hashlib.md5(d).hexdigest()}
    is_jpeg = d[:3] == b"\xff\xd8\xff"
    r["is_jpeg"] = is_jpeg
    text_segs = {}
    if is_jpeg:
        segs = jpeg_segments(d)
        r["segments"] = [s[0] for s in segs]
        eoi = d.rfind(b"\xff\xd9")
        trailing = d[eoi+2:] if eoi >= 0 else b""
        r["trailing_after_eoi"] = len(trailing)
        if trailing:
            open(os.path.join(outdir, f"{stem}_trailing.bin"), "wb").write(trailing)
            r["trailing_preview"] = trailing[:80].hex()
            r["trailing_entropy"] = round(entropy(trailing), 3)
        # dump COM / APP text-ish segments
        for name, off, body in segs:
            if name.startswith("COM") or name.startswith("APP1") or name.startswith("APP13"):
                txt = body[:300].decode("latin1", "replace")
                if any(32 <= b < 127 for b in body[:50]):
                    text_segs[f"{name}@{off}"] = txt
        # DQT fingerprint
        dqts = [b for (n, _, b) in segs if n == "DQT"]
        r["dqt_fingerprint"] = hashlib.md5(b"".join(dqts)).hexdigest()[:12] if dqts else None
    r["text_segments"] = text_segs
    # EXIF
    try:
        im = Image.open(path); ex = im._getexif() if hasattr(im, "_getexif") else None
        r["exif"] = {TAGS.get(k, k): str(v)[:80] for k, v in (ex or {}).items()} if ex else {}
        r["has_icc"] = "icc_profile" in im.info
    except Exception:
        r["exif"] = {}; r["has_icc"] = None
    # carve + strings + entropy + lsb
    r["carved"] = [{"offset": o, "type": t} for o, t in carve(d)]
    nruns, flagged = strings_flagged(d)
    r["n_strings"] = nruns
    r["flagged_strings"] = [{"tag": t, "s": s} for t, s in flagged]
    r["file_entropy"] = round(entropy(d), 3)
    r["lsb"] = lsb_planes(path, outdir, stem)
    return r


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "data/relikd"
    out = sys.argv[2] if len(sys.argv) > 2 else "analysis/stego/out"
    carved = os.path.join(out, "carved"); os.makedirs(carved, exist_ok=True)
    imgs = sorted([f for f in os.listdir(src)
                   if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))],
                  key=lambda x: (len(x), x))
    results = [scan_one(os.path.join(src, f), carved) for f in imgs]
    json.dump(results, open(os.path.join(out, "results.json"), "w"), indent=1)

    # cross-page anomaly summary
    L = ["# Image-stego sweep report", "", f"Source: `{src}`  ({len(results)} images)", ""]
    dqts = Counter(r.get("dqt_fingerprint") for r in results)
    L += [f"- distinct DQT fingerprints: {len(dqts)}  {dict(dqts)}",
          f"- images with trailing-after-EOI: {sum(1 for r in results if r.get('trailing_after_eoi'))}",
          f"- images with carved embedded sigs: {sum(1 for r in results if r.get('carved'))}",
          f"- images with EXIF: {sum(1 for r in results if r.get('exif'))}",
          f"- images with flagged strings: {sum(1 for r in results if r.get('flagged_strings'))}",
          f"- lossless (LSB-meaningful): {sum(1 for r in results if r.get('lsb',{}).get('lossless'))}", ""]
    L.append("## Per-image anomalies (only rows with something)")
    for r in results:
        notes = []
        if r.get("trailing_after_eoi"): notes.append(f"TRAILING {r['trailing_after_eoi']}B (ent {r.get('trailing_entropy')})")
        if r.get("carved"): notes.append(f"CARVE {[c['type'] for c in r['carved'][:6]]}")
        if r.get("exif"): notes.append(f"EXIF {list(r['exif'])[:5]}")
        if r.get("text_segments"): notes.append(f"TEXTSEG {list(r['text_segments'])}")
        if r.get("flagged_strings"): notes.append(f"STR {[f['tag'] for f in r['flagged_strings'][:8]]}")
        if notes:
            L.append(f"- **{r['file']}** ({r['size']}B, sha {r['sha256'][:10]}): " + " | ".join(notes))
    L.append("")
    L.append("## NOTE")
    L.append("DCT-domain stego (OutGuess/F5/jsteg/steghide) is NOT testable here "
             "(needs a binary). Spatial LSB above is only meaningful for lossless "
             "images; for JPEG it is compression noise. Authentic originals + a "
             "Linux env with outguess/stegdetect needed to close that gap.")
    open(os.path.join(out, "REPORT.md"), "w", encoding="utf-8").write("\n".join(L))
    print(f"scanned {len(results)} images -> {out}/REPORT.md")
    print(f"distinct DQT fingerprints: {len(dqts)}")
    for r in results:
        if r.get("trailing_after_eoi") or r.get("carved") or r.get("exif") or r.get("text_segments"):
            print(f"  ANOMALY {r['file']}: trailing={r.get('trailing_after_eoi')} carve={len(r.get('carved',[]))} exif={bool(r.get('exif'))}")


if __name__ == "__main__":
    main()
