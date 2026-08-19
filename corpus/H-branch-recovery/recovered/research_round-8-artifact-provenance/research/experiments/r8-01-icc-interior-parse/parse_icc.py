#!/usr/bin/env python3
"""R8-S1: Structured parse of the embedded ICC profile. Deterministic, no RNG.
Executes the pre-registered procedure exactly. Writes results.json."""
import json, struct, hashlib, glob, os, re

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RELIKD = os.path.join(REPO, "liber-primus", "data", "relikd")

def extract_icc(path):
    """Concatenate ICC_PROFILE APP2 chunks from a JPEG."""
    with open(path, "rb") as f:
        data = f.read()
    i = 2  # skip SOI
    chunks = {}
    while i < len(data) - 1:
        if data[i] != 0xFF:
            i += 1; continue
        marker = data[i+1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2; continue
        if marker == 0xDA:  # SOS -> compressed data begins
            break
        seglen = struct.unpack(">H", data[i+2:i+4])[0]
        seg = data[i+4:i+2+seglen]
        if marker == 0xE2 and seg[:12] == b"ICC_PROFILE\x00":
            seqno = seg[12]; total = seg[13]
            chunks[seqno] = seg[14:]
        i += 2 + seglen
    if not chunks:
        return None
    return b"".join(chunks[k] for k in sorted(chunks))

def read_dt(b):  # ICC dateTimeNumber: 6x uint16 BE
    y,mo,d,h,mi,s = struct.unpack(">6H", b[:12])
    return dict(year=y, month=mo, day=d, hour=h, minute=mi, second=s)

def parse_header(icc):
    h = {}
    h["profile_size"] = struct.unpack(">I", icc[0:4])[0]
    h["cmm_type"] = icc[4:8].decode("latin1").strip("\x00")
    h["version"] = "%d.%d.%d" % (icc[8], icc[9] >> 4, icc[9] & 0xF)
    h["device_class"] = icc[12:16].decode("latin1").strip()
    h["color_space"] = icc[16:20].decode("latin1").strip()
    h["pcs"] = icc[20:24].decode("latin1").strip()
    h["creation_datetime"] = read_dt(icc[24:36])
    h["magic_acsp"] = icc[36:40].decode("latin1")  # must be 'acsp'
    h["platform"] = icc[40:44].decode("latin1").strip("\x00").strip()
    h["manufacturer"] = icc[48:52].decode("latin1").strip("\x00").strip()
    h["model"] = icc[52:56].decode("latin1").strip("\x00").strip()
    h["creator"] = icc[80:84].decode("latin1").strip("\x00").strip()
    h["profile_id_md5"] = icc[84:100].hex()
    return h

def parse_tags(icc):
    count = struct.unpack(">I", icc[128:132])[0]
    tags = {}
    text = {}
    for k in range(count):
        off = 132 + 12*k
        sig = icc[off:off+4].decode("latin1")
        toff, tsize = struct.unpack(">II", icc[off+4:off+12])
        tags[sig] = (toff, tsize)
        if toff + tsize <= len(icc):
            blob = icc[toff:toff+tsize]
            ttype = blob[:4].decode("latin1", "replace")
            if ttype == "desc":  # textDescriptionType (ICC v2)
                n = struct.unpack(">I", blob[8:12])[0]
                text[sig] = blob[12:12+n].decode("latin1", "replace").strip("\x00")
            elif ttype in ("text",):
                text[sig] = blob[8:].decode("latin1", "replace").strip("\x00")
            elif ttype == "mluc":
                nrec = struct.unpack(">I", blob[8:12])[0]
                if nrec:
                    rsize = struct.unpack(">I", blob[12:16])[0]
                    slen = struct.unpack(">I", blob[16:20])[0]
                    soff = struct.unpack(">I", blob[20:24])[0]
                    text[sig] = blob[soff:soff+slen].decode("utf-16-be", "replace").strip("\x00")
    return count, tags, text

def main():
    paths = sorted(glob.glob(os.path.join(RELIKD, "p*.jpg")),
                   key=lambda p: int(re.search(r"p(\d+)\.jpg", p).group(1)))
    # 1-2: extract ICC per page, hash for identity check
    icc_hashes = {}
    ref_icc = None
    for p in paths:
        icc = extract_icc(p)
        if icc is None:
            icc_hashes[os.path.basename(p)] = None; continue
        icc_hashes[os.path.basename(p)] = hashlib.sha256(icc).hexdigest()
        if ref_icc is None:
            ref_icc = icc
    uniq = set(h for h in icc_hashes.values() if h)
    identical = len(uniq) == 1
    # 3-5: parse the reference ICC
    header = parse_header(ref_icc)
    count, tags, text = parse_tags(ref_icc)
    # any printable version/date-ish tokens anywhere in the blob
    strings = re.findall(rb"[\x20-\x7e]{4,}", ref_icc)
    strings = [s.decode("latin1") for s in strings]
    version_tokens = [s for s in strings
                      if re.search(r"ghostscript|artifex|gpl|afpl|\bgs\b|\d\.\d\d?\b", s, re.I)]
    cdt = header["creation_datetime"]
    creation_nonzero = any(cdt[k] for k in cdt)
    # decision token: version/date beyond static 2011 copyright?
    cprt = text.get("cprt", "")
    has_version_token = bool([s for s in version_tokens
                              if re.search(r"ghostscript|artifex|gpl|afpl", s, re.I)
                              and re.search(r"\d", s)])
    datable = creation_nonzero or has_version_token
    verdict = "POSITIVE-DATABLE" if datable else "NULL"

    out = {
        "experiment": "r8-01-icc-interior-parse",
        "n_pages": len(paths),
        "icc_identical_across_all_pages": identical,
        "n_unique_icc_hashes": len(uniq),
        "ref_icc_sha256": hashlib.sha256(ref_icc).hexdigest(),
        "ref_icc_len": len(ref_icc),
        "header": header,
        "acsp_magic_ok": header["magic_acsp"] == "acsp",
        "tag_count": count,
        "tag_signatures": sorted(tags.keys()),
        "text_tags": text,
        "creation_datetime_nonzero": creation_nonzero,
        "version_like_strings": version_tokens,
        "has_tooling_version_token": has_version_token,
        "decision_token_datable": datable,
        "VERDICT": verdict,
    }
    outpath = os.path.join(os.path.dirname(__file__), "results.json")
    with open(outpath, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
