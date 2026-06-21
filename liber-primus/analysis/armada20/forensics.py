#!/usr/bin/env python3
import os, sys, struct, glob, json, re

ROOTS = [
    "/mnt/c/Users/dukot/projects/cicada3301/puzzles/2012",
    "/mnt/c/Users/dukot/projects/cicada3301/puzzles/2013",
    "/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014",
    "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd",
]

MAGICS = {
    b"PK\x03\x04": "ZIP",
    b"PK\x05\x06": "ZIP-empty",
    b"PK\x07\x08": "ZIP-spanned",
    b"\x1f\x8b": "GZIP",
    b"Rar!\x1a\x07": "RAR",
    b"7z\xbc\xaf\x27\x1c": "7Z",
    b"BZh": "BZIP2",
    b"\xfd7zXZ\x00": "XZ",
    b"-----BEGIN": "PGP/PEM",
    b"\x89PNG": "PNG-embedded",
    b"%PDF": "PDF-embedded",
    b"OggS": "OGG",
    b"ID3": "MP3-ID3",
}

def find_eoi(data):
    # find LAST FFD9 (JPEG end marker)
    idx = data.rfind(b"\xff\xd9")
    return idx

def find_png_iend(data):
    # PNG: IEND chunk = 49 45 4E 44 AE 42 60 82 (last 8 bytes of valid PNG)
    idx = data.rfind(b"IEND\xae\x42\x60\x82")
    if idx < 0:
        return -1
    return idx + 8

def scan_archive_magics(data):
    hits = []
    for magic, name in MAGICS.items():
        start = 0
        while True:
            i = data.find(magic, start)
            if i < 0:
                break
            hits.append((i, name))
            start = i + 1
            if len(hits) > 50:
                break
    return hits

def printable_ratio(b):
    if not b:
        return 0.0
    p = sum(1 for c in b if 32 <= c < 127 or c in (9,10,13))
    return p / len(b)

def analyze(path):
    with open(path, "rb") as f:
        data = f.read()
    size = len(data)
    ext = path.lower().rsplit(".",1)[-1]
    res = {"path": path, "size": size, "ext": ext}

    trailing = b""
    if ext in ("jpg","jpeg") or data[:2] == b"\xff\xd8":
        eoi = find_eoi(data)
        if eoi >= 0:
            end = eoi + 2
            trailing = data[end:]
            res["eoi_at"] = eoi
            res["trailing_len"] = len(trailing)
    elif ext == "png" or data[:4] == b"\x89PNG":
        iend = find_png_iend(data)
        if iend >= 0:
            trailing = data[iend:]
            res["iend_at"] = iend
            res["trailing_len"] = len(trailing)

    if trailing:
        res["trailing_hex"] = trailing[:64].hex()
        res["trailing_printable_ratio"] = round(printable_ratio(trailing),3)
        # capture printable text in trailing
        txt = re.findall(rb"[\x20-\x7e]{5,}", trailing)
        if txt:
            res["trailing_strings"] = [t.decode('latin1') for t in txt[:20]]

    mh = scan_archive_magics(data)
    # filter out magics that are just the file's own header
    filtered = []
    for i, name in mh:
        if i < 4:  # own header
            continue
        filtered.append({"off": i, "magic": name})
    if filtered:
        res["embedded_magics"] = filtered[:30]

    return res

def main():
    out = []
    flagged = []
    for root in ROOTS:
        for p in sorted(glob.glob(os.path.join(root, "**", "*"), recursive=True)):
            if not os.path.isfile(p):
                continue
            ext = p.lower().rsplit(".",1)[-1]
            if ext not in ("jpg","jpeg","png","gif","bmp"):
                continue
            try:
                r = analyze(p)
            except Exception as e:
                r = {"path": p, "error": str(e)}
            out.append(r)
            if r.get("trailing_len",0) > 2 or r.get("embedded_magics"):
                flagged.append(r)
    with open("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20/forensics_full.json","w") as f:
        json.dump(out, f, indent=1)
    print(f"Scanned {len(out)} image files")
    print(f"FLAGGED (trailing data or embedded magic): {len(flagged)}")
    for r in flagged:
        print("\n---", r["path"])
        print("  size", r["size"], "trailing_len", r.get("trailing_len"))
        if r.get("trailing_hex"):
            print("  trailing_hex", r["trailing_hex"])
        if r.get("trailing_strings"):
            print("  strings", r["trailing_strings"])
        if r.get("embedded_magics"):
            print("  magics", r["embedded_magics"])

if __name__ == "__main__":
    main()
