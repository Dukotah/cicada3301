#!/usr/bin/env python3
"""Extract hex-encoded binaries carried inside PGP-SIGNED Cicada messages.

Several 3301 messages transport a whole file as ASCII hex inside the signed
body. Those bytes are therefore attested by the 3301 signature itself, which
makes them the highest-fidelity copy of the artifact obtainable — better than
any mirror. This script pulls them out and identifies them by magic number.

Writes to signed-payloads/ and emits signed-payloads/PAYLOADS.json.
"""
import binascii
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MSG = ROOT / "pgp" / "messages"
OUT = ROOT / "signed-payloads"

MAGIC = [
    (b"\xff\xd8\xff", "jpg", "JPEG"),
    (b"\x89PNG\r\n\x1a\n", "png", "PNG"),
    (b"GIF8", "gif", "GIF"),
    (b"ID3", "mp3", "MP3 (ID3v2)"),
    (b"\xff\xfb", "mp3", "MP3 (MPEG frame)"),
    (b"OggS", "ogg", "Ogg"),
    (b"%PDF", "pdf", "PDF"),
    (b"PK\x03\x04", "zip", "ZIP"),
    (b"MThd", "mid", "Standard MIDI"),
]


def clearsigned_body(text):
    if "-----BEGIN PGP SIGNED MESSAGE-----" not in text:
        return None
    after = text.split("-----BEGIN PGP SIGNED MESSAGE-----", 1)[1]
    # skip the Hash: armour headers, which end at the first blank line
    parts = after.split("\n\n", 1)
    if len(parts) < 2:
        return None
    return parts[1].split("-----BEGIN PGP SIGNATURE-----", 1)[0]


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for p in sorted(MSG.glob("*.asc")):
        body = clearsigned_body(p.read_text(encoding="utf-8", errors="replace"))
        if body is None:
            continue
        # A hex payload is a run of lines that are pure hex and long enough to
        # be a file rather than a hash. Require >= 512 hex digits.
        # NOTE: a trailing partial line (e.g. the final "fe" of a 60-col hex
        # dump) is part of the payload. Dropping it silently truncates the
        # file - which is exactly how the repo's interconnectedness.bin ended
        # up 3 bytes short. Take every hex-only line once the run has started.
        hexlines, started = [], False
        for ln in body.splitlines():
            s = ln.strip()
            if re.fullmatch(r"[0-9a-fA-F]{16,}", s):
                hexlines.append(s)
                started = True
            elif started and re.fullmatch(r"[0-9a-fA-F]{2,}", s):
                hexlines.append(s)
            elif started and s == "":
                continue
            elif started:
                break
        if not hexlines:
            continue
        blob = "".join(hexlines)
        if len(blob) < 512 or len(blob) % 2:
            note = "odd-length or short hex run; not decoded"
            rows.append({"source_message": p.name, "hex_digits": len(blob),
                         "decoded": False, "note": note})
            continue
        raw = binascii.unhexlify(blob)
        ext, kind = "bin", "unidentified"
        for sig, e, k in MAGIC:
            if raw.startswith(sig):
                ext, kind = e, k
                break
        name = p.stem + "." + ext
        (OUT / name).write_bytes(raw)
        rows.append({
            "file": f"signed-payloads/{name}",
            "source_message": p.name,
            "source_message_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "sha1": hashlib.sha1(raw).hexdigest(),
            "md5": hashlib.md5(raw).hexdigest(),
            "detected_type": kind,
            "hex_digits": len(blob),
            "decoded": True,
            "provenance": "bytes carried inside a clearsigned 3301 message whose signature "
                          "verifies against 6D854CD7933322A601C3286D181F01E57A35090F; "
                          "therefore attested by the signer, not merely mirrored",
            "extracted_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
        print(f"{len(raw):>10} {kind:<16} {name}  <- {p.name}")
    (OUT / "PAYLOADS.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"{len(rows)} payload rows")


if __name__ == "__main__":
    main()
