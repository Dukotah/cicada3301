"""Minimal ISO9660 extractor — stdlib only, no pycdlib / 7z / bsdtar required.

Written for the capsule's `DATA/560.13` recovery (see RECOVERY-560.13.md): the machine that
needed it had no ISO tooling at all, and a future reader may be in the same position. Handles
plain ISO9660 (which is all the 2013 CicadaOS `3301.iso` uses).

Usage:
    python3 iso_extract.py 3301.iso --list
    python3 iso_extract.py 3301.iso --extract DATA/560.13 --out DATA_560.13
"""
import argparse
import os
import struct
import sys

SECTOR = 2048


def _both_le(b, off):
    """Read the little-endian half of an ISO 'both-endian' 32-bit field."""
    return struct.unpack_from("<I", b, off)[0]


def _records(f, lba, size):
    """Yield (name, lba, length, is_dir) for every record in a directory extent."""
    f.seek(lba * SECTOR)
    data = f.read(size)
    pos = 0
    while pos < len(data):
        rec_len = data[pos]
        if rec_len == 0:
            # padding to the end of the sector; jump to the next one
            nxt = ((pos // SECTOR) + 1) * SECTOR
            if nxt >= len(data):
                break
            pos = nxt
            continue
        ext_lba = _both_le(data, pos + 2)
        ext_len = _both_le(data, pos + 10)
        flags = data[pos + 25]
        name_len = data[pos + 32]
        name = data[pos + 33: pos + 33 + name_len]
        # strip the ';1' version suffix ISO9660 appends to file identifiers
        nm = name.decode("latin-1")
        if ";" in nm:
            nm = nm.split(";", 1)[0]
        yield nm, ext_lba, ext_len, bool(flags & 0x02)
        pos += rec_len


def _root(f):
    """Return (lba, size) of the root directory from the Primary Volume Descriptor."""
    f.seek(16 * SECTOR)
    pvd = f.read(SECTOR)
    if pvd[1:6] != b"CD001":
        raise SystemExit("not an ISO9660 image (no CD001 at sector 16)")
    rr = pvd[156:156 + 34]          # root directory record, embedded in the PVD
    return _both_le(rr, 2), _both_le(rr, 10)


def walk(f, lba, size, prefix=""):
    for nm, l, n, is_dir in _records(f, lba, size):
        if nm in ("\x00", "\x01", ""):      # '.' and '..'
            continue
        path = f"{prefix}{nm}"
        if is_dir:
            yield from walk(f, l, n, path + "/")
        else:
            yield path, l, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iso")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--extract", help="path inside the ISO, e.g. DATA/560.13")
    ap.add_argument("--out", help="output file (default: basename of --extract)")
    a = ap.parse_args()

    with open(a.iso, "rb") as f:
        lba, size = _root(f)
        entries = list(walk(f, lba, size))
        if a.list or not a.extract:
            for p, l, n in entries:
                print(f"{n:>12}  {p}")
            return
        want = a.extract.upper().lstrip("/")
        for p, l, n in entries:
            if p.upper() == want:
                out = a.out or os.path.basename(p)
                f.seek(l * SECTOR)
                left = n
                with open(out, "wb") as o:
                    while left:
                        b = f.read(min(1 << 20, left))
                        if not b:
                            break
                        o.write(b)
                        left -= len(b)
                print(f"extracted {p} -> {out} ({n} bytes)")
                return
        sys.exit(f"{a.extract} not found in {a.iso}")


if __name__ == "__main__":
    main()
