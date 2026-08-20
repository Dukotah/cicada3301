#!/usr/bin/env python3
"""Lane A: find data that lives past the real end of a JPEG or PNG.

Motivated by CONFLICTS-A.md C-02, where 61 bytes after a JPEG's EOI marker were
the entire first step of the 2012 puzzle. A naive rfind(b'\xff\xd9') is wrong -
the last FFD9 in a file can sit inside appended data - so the JPEG marker stream
is walked properly, including FF00 byte-stuffing and RST markers inside the
entropy-coded scan.

Writes TRAILING-DATA.json. Measures only; interprets nothing.
"""
import hashlib
import json
import os
import struct
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "TRAILING-DATA.json"


def jpeg_end(d):
    if d[:2] != b"\xff\xd8":
        return None
    i = 2
    while i < len(d) - 1:
        if d[i] != 0xFF:
            return None
        m = d[i + 1]
        if m == 0xFF:
            i += 1
            continue
        if m == 0xD9:
            return i + 2
        if m == 0x01 or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        if i + 4 > len(d):
            return None
        ln = struct.unpack(">H", d[i + 2:i + 4])[0]
        if m == 0xDA:                      # start of scan
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
                    return j + 2
                break                      # another real marker: resume outer walk
            i = j
            continue
        i += 2 + ln
    return None


def png_end(d):
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    i = 8
    while i + 8 <= len(d):
        ln = struct.unpack(">I", d[i:i + 4])[0]
        typ = d[i + 4:i + 8]
        i = i + 8 + ln + 4
        if typ == b"IEND":
            return i
    return None


def main():
    res, bad, scanned = [], [], 0
    for root, dirs, files in os.walk(ROOT):
        if ".gnupg-lane-a" in root:
            continue
        for f in files:
            low = f.lower()
            if not low.endswith((".jpg", ".jpeg", ".png")):
                continue
            p = Path(root) / f
            try:
                d = p.read_bytes()
            except OSError:
                continue
            scanned += 1
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            end = jpeg_end(d) if low.endswith((".jpg", ".jpeg")) else png_end(d)
            if end is None:
                bad.append(rel)
                continue
            n = len(d) - end
            if n <= 0:
                continue
            t = d[end:]
            res.append({
                "path": rel,
                "file_bytes": len(d),
                "image_ends_at": end,
                "trailing_bytes": n,
                "sha256": hashlib.sha256(d).hexdigest(),
                "trailing_sha256": hashlib.sha256(t).hexdigest(),
                "trailing_magic_hex": t[:16].hex(),
                "trailing_printable_ratio": round(
                    sum(1 for c in t if 32 <= c < 127 or c in (9, 10, 13)) / n, 3),
                "trailing_preview": t[:200].decode("utf-8", "backslashreplace"),
            })
    res.sort(key=lambda r: -r["trailing_bytes"])
    OUT.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "what_this_is": (
            "Bytes that sit after the real end of a JPEG (EOI) or PNG (IEND), found by "
            "walking the marker/chunk stream rather than searching for the last EOI. "
            "Motivated by CONFLICTS-A.md C-02. Measurement only - no claim is made about "
            "what any trailer means."),
        "counts": {"images_scanned": scanned,
                   "with_trailing_data": len(res),
                   "unparseable": len(bad)},
        "trailing": res,
        "unparseable": bad,
    }, indent=2), encoding="utf-8")
    print(f"scanned {scanned}; trailing {len(res)}; unparseable {len(bad)}")
    for r in res[:20]:
        print(f"{r['trailing_bytes']:>9}  {r['path']}")


if __name__ == "__main__":
    main()
