"""W2-C3 mirror-byte-residue toolkit.  Pure stdlib + PIL/numpy (decode/compare only).

Transform family (attested in-corpus, R43-F6 + 2012 trailer):
    id, rev (byte reversal), xff (bytewise complement), revxff (reverse of complement)
Extension transforms (T2/T3/canon battery only — NOT in R29-L2/R30-B1 coverage):
    rot5, rot6 (bit-rotate per byte), nib (nibble swap), bitrev (per-byte bit reversal),
    delta (b[i]-b[i-1] mod 256), cumsum (running sum mod 256), xoridx (b[i]^ (i & 0xFF))
"""
import bz2
import gzip
import hashlib
import io
import lzma
import math
import struct
import zlib

# ---------------------------------------------------------------- transforms
def t_id(b):      return b
def t_rev(b):     return b[::-1]
def t_xff(b):     return bytes(x ^ 0xFF for x in b)
def t_revxff(b):  return bytes(x ^ 0xFF for x in b)[::-1]
def t_rot(b, k):  return bytes(((x << k) | (x >> (8 - k))) & 0xFF for x in b)
def t_nib(b):     return bytes(((x << 4) | (x >> 4)) & 0xFF for x in b)
def t_bitrev(b):  return bytes(int(f"{x:08b}"[::-1], 2) for x in b)
def t_delta(b):   return bytes((b[i] - b[i - 1]) % 256 for i in range(1, len(b)))
def t_cumsum(b):
    s, out = 0, bytearray()
    for x in b:
        s = (s + x) % 256
        out.append(s)
    return bytes(out)
def t_xoridx(b):  return bytes(b[i] ^ (i & 0xFF) for i in range(len(b)))

CORE = {"id": t_id, "rev": t_rev, "xff": t_xff, "revxff": t_revxff}
EXT = {"rot5": lambda b: t_rot(b, 5), "rot6": lambda b: t_rot(b, 6), "nib": t_nib,
       "bitrev": t_bitrev, "delta": t_delta, "cumsum": t_cumsum, "xoridx": t_xoridx}

# ---------------------------------------------------------------- magics
MAGICS = [
    ("jpeg", b"\xff\xd8\xff"), ("png", b"\x89PNG\r\n\x1a\n"), ("gif", b"GIF8"),
    ("gzip", b"\x1f\x8b\x08"), ("zlib78", b"\x78\x9c"), ("zlib78da", b"\x78\xda"),
    ("zlib7801", b"\x78\x01"), ("bzip2", b"BZh"), ("xz", b"\xfd7zXZ\x00"),
    ("zip", b"PK\x03\x04"), ("rar", b"Rar!\x1a"), ("7z", b"7z\xbc\xaf\x27\x1c"),
    ("pdf", b"%PDF"), ("elf", b"\x7fELF"), ("pgp_armor", b"-----BEGIN PGP"),
    ("pem", b"-----BEGIN "), ("ogg", b"OggS"), ("tar_ustar", b"ustar"),
    ("png_ihdr", b"IHDR"), ("outguess_jpeg_eoi_rev", b"\xd9\xff"),
]

def entropy(b):
    if not b:
        return 0.0
    c = [0] * 256
    for x in b:
        c[x] += 1
    n = len(b)
    return -sum(v / n * math.log2(v / n) for v in c if v)

def chi2(b):
    if not b:
        return 0.0
    c = [0] * 256
    for x in b:
        c[x] += 1
    e = len(b) / 256
    return sum((v - e) ** 2 / e for v in c)

def windowed_entropy(b, win=4096, step=1024):
    if len(b) < win:
        return [entropy(b)]
    return [entropy(b[i:i + win]) for i in range(0, len(b) - win + 1, step)]

def printable_ratio(b):
    return sum(1 for x in b if 32 <= x < 127 or x in (9, 10, 13)) / max(1, len(b))

def sha(b):
    return hashlib.sha256(b).hexdigest()

# ---------------------------------------------------------------- structure
def smallest_period(b, max_p=4096, tol=0.0):
    """Smallest p with b[i]==b[i+p] for all i (tol = allowed mismatch fraction)."""
    n = len(b)
    for p in range(1, min(max_p, n // 2) + 1):
        mism = sum(1 for i in range(n - p) if b[i] != b[i + p])
        if mism <= tol * (n - p):
            return p, mism
    return None, None

def is_byte_palindrome(b):
    return b == b[::-1]

def palindrome_core(b):
    """Longest symmetric prefix/suffix: max k with b[:k] == reverse(b[-k:])."""
    lo, hi = 0, len(b) // 2
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if b[:mid] == b[-mid:][::-1]:
            lo = mid
        else:
            hi = mid - 1
    return lo

# ---------------------------------------------------------------- image walks
def jpeg_end_scan(d):
    """Same as trailing_scan.py's walker (with the scan inner loop verbatim)."""
    if d[:2] != b"\xff\xd8":
        return None, "no SOI"
    i = 2
    while i < len(d) - 1:
        if d[i] != 0xFF:
            return None, f"lost marker sync at offset {i} (byte {d[i]:#04x})"
        m = d[i + 1]
        if m == 0xFF:
            i += 1
            continue
        if m == 0xD9:
            return i + 2, None
        if m == 0x01 or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        if i + 4 > len(d):
            return None, f"truncated marker segment header at {i}"
        ln = struct.unpack(">H", d[i + 2:i + 4])[0]
        if m == 0xDA:
            j = i + 2 + ln
            while j < len(d) - 1:
                if d[j] != 0xFF:
                    j += 1
                    continue
                n = d[j + 1]
                if n == 0x00 or 0xD0 <= n <= 0xD7 or n == 0xFF:
                    j += 2
                    continue
                if n == 0xD9:
                    return j + 2, None
                break
            else:
                return None, f"entropy scan ran past EOF (scan started {i})"
            i = j
            continue
        i += 2 + ln
    return None, "walk ended before EOI"

def png_end(d):
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        return None, "no PNG signature"
    i = 8
    while i + 8 <= len(d):
        ln = struct.unpack(">I", d[i:i + 4])[0]
        typ = d[i + 4:i + 8]
        i = i + 8 + ln + 4
        if typ == b"IEND":
            return i, None
    return None, "no IEND chunk before EOF"

def walk_chain(d, max_depth=12):
    """Repeatedly parse JPEG/PNG from offset 0 and recurse into the remainder.
    Returns list of segments: (kind, start, end, sha256) + final residue."""
    segs, off, depth = [], 0, 0
    while off < len(d) and depth < max_depth:
        rest = d[off:]
        end = why = None
        kind = None
        if rest[:2] == b"\xff\xd8":
            kind = "jpeg"
            end, why = jpeg_end_scan(rest)
        elif rest[:8] == b"\x89PNG\r\n\x1a\n":
            kind = "png"
            end, why = png_end(rest)
        if kind is None or end is None:
            segs.append(("residue", off, len(d), sha(rest), why))
            return segs
        segs.append((kind, off, off + end, sha(rest[:end]), None))
        off += end
        depth += 1
    if off < len(d):
        segs.append(("residue", off, len(d), sha(d[off:]), "max_depth"))
    return segs

# ---------------------------------------------------------------- decompression
def try_decompress(b, off):
    out = {}
    seg = b[off:]
    for name, fn in [
        ("gzip", lambda s: gzip.decompress(s)),
        ("zlib", lambda s: zlib.decompress(s)),
        ("zlib_raw", lambda s: zlib.decompressobj(-15).decompress(s)),
        ("bz2", lambda s: bz2.decompress(s)),
        ("xz", lambda s: lzma.decompress(s)),
    ]:
        try:
            d = fn(seg)
            if len(d) >= 16:
                out[name] = d
        except Exception:
            pass
    return out

def magic_scan(b, magics=MAGICS, max_hits=50):
    hits = []
    for name, sig in magics:
        start = 0
        while len(hits) < 10_000:
            i = b.find(sig, start)
            if i < 0:
                break
            hits.append((name, i))
            start = i + 1
            if sum(1 for h in hits if h[0] == name) >= max_hits:
                break
    return hits

def identify(blob, transforms=None, decomp_headers_only=True, brute_zlib_limit=65536):
    """Run the full identification battery.  Returns a dict report."""
    if transforms is None:
        transforms = CORE
    rep = {"bytes": len(blob), "sha256": sha(blob), "entropy": round(entropy(blob), 4),
           "chi2": round(chi2(blob), 1), "printable": round(printable_ratio(blob), 3),
           "transforms": {}}
    we = windowed_entropy(blob)
    rep["win_entropy_min"] = round(min(we), 4)
    rep["win_entropy_max"] = round(max(we), 4)
    p, mism = smallest_period(blob[:16384])
    rep["smallest_period_16k"] = p
    rep["byte_palindrome"] = is_byte_palindrome(blob)
    rep["palindrome_core"] = palindrome_core(blob)
    for tname, tf in transforms.items():
        tb = tf(blob)
        hits = magic_scan(tb)
        found = []
        payloads = []
        seen_off = set()
        for name, off in hits:
            found.append([name, off])
            if name in ("gzip", "zlib78", "zlib78da", "zlib7801", "bzip2", "xz") and off not in seen_off:
                seen_off.add(off)
                dec = try_decompress(tb, off)
                for how, d in dec.items():
                    payloads.append({"at": off, "how": how, "out_bytes": len(d),
                                     "out_sha": sha(d), "out_entropy": round(entropy(d), 3),
                                     "out_head_hex": d[:16].hex()})
        # brute raw-deflate for small blobs
        if not decomp_headers_only and len(tb) <= brute_zlib_limit:
            for off in range(len(tb)):
                try:
                    d = zlib.decompressobj(-15).decompress(tb[off:])
                    if len(d) >= 64 and entropy(d) < 7.5:
                        payloads.append({"at": off, "how": "raw_deflate_brute",
                                         "out_bytes": len(d), "out_sha": sha(d),
                                         "out_entropy": round(entropy(d), 3),
                                         "out_head_hex": d[:16].hex()})
                except Exception:
                    pass
        rep["transforms"][tname] = {"magic_hits": found[:60], "n_magic_hits": len(found),
                                    "decompressed": payloads}
    return rep
