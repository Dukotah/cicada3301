"""I1 - JPEG encoder fingerprint extractor (Round 18, lane L1).

Parses every marker of a JPEG and derives:
  * DQT tables (raw bytes + sha1) and, by INTERVAL ARITHMETIC over libjpeg's
    quality-scaling rule, the exact set of integer IJG qualities consistent with
    the observed tables.  libjpeg: temp = (base*scale + 50)/100, clipped [1,255],
    scale = 5000/Q (Q<50) else 200-2Q.
  * Huffman table classification: identical to the IJG Annex K "standard" tables
    (i.e. encoder did NOT set optimize_coding) vs custom/optimised.
  * Chroma subsampling, component count, precision, geometry, restart interval.
  * JFIF version/units/density, ICC profile header fields + description/copyright,
    Adobe APP14 transform, COM segments, trailing bytes after EOI.
  * Marker ORDER as a string - encoders differ in emission order.

Usage:  python3 jpeg_fingerprint.py FILE [FILE...]        -> JSON to stdout
        python3 jpeg_fingerprint.py --selftest            -> PC1 quality recovery
"""
import struct, hashlib, json, sys, os

# ---- IJG Annex K base tables, NATURAL (row-major) order -------------------
STD_LUMA = [
    16, 11, 10, 16, 24, 40, 51, 61,
    12, 12, 14, 19, 26, 58, 60, 55,
    14, 13, 16, 24, 40, 57, 69, 56,
    14, 17, 22, 29, 51, 87, 80, 62,
    18, 22, 37, 56, 68, 109, 103, 77,
    24, 35, 55, 64, 81, 104, 113, 92,
    49, 64, 78, 87, 103, 121, 120, 101,
    72, 92, 95, 98, 112, 100, 103, 99]
STD_CHROMA = [
    17, 18, 24, 47, 99, 99, 99, 99,
    18, 21, 26, 66, 99, 99, 99, 99,
    24, 26, 56, 99, 99, 99, 99, 99,
    47, 66, 99, 99, 99, 99, 99, 99,
    99, 99, 99, 99, 99, 99, 99, 99,
    99, 99, 99, 99, 99, 99, 99, 99,
    99, 99, 99, 99, 99, 99, 99, 99,
    99, 99, 99, 99, 99, 99, 99, 99]
ZIGZAG = [
    0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5,
    12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21, 28,
    35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51,
    58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63]


def zz(natural):
    return [natural[i] for i in ZIGZAG]


STD_LUMA_ZZ = zz(STD_LUMA)
STD_CHROMA_ZZ = zz(STD_CHROMA)


def ijg_scale(q):
    q = max(1, min(100, int(q)))
    return 5000 // q if q < 50 else 200 - 2 * q


def ijg_table(base_zz, q, baseline=True):
    s = ijg_scale(q)
    out = []
    for b in base_zz:
        t = (b * s + 50) // 100
        if t < 1:
            t = 1
        if t > 32767:
            t = 32767
        if baseline and t > 255:
            t = 255
        out.append(t)
    return out


def qualities_consistent(vals_zz, base_zz):
    """All integer IJG qualities 1..100 whose scaled table equals vals_zz exactly."""
    return [q for q in range(1, 101) if ijg_table(base_zz, q) == list(vals_zz)]


# ---- IJG standard Huffman tables (Annex K) -------------------------------
STD_DC_LUMA_BITS = [0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
STD_DC_LUMA_VAL = list(range(12))
STD_DC_CHROMA_BITS = [0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
STD_DC_CHROMA_VAL = list(range(12))
STD_AC_LUMA_BITS = [0, 2, 1, 3, 3, 2, 4, 3, 5, 5, 4, 4, 0, 0, 1, 0x7d]
STD_AC_LUMA_VAL = [
    0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
    0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xa1, 0x08,
    0x23, 0x42, 0xb1, 0xc1, 0x15, 0x52, 0xd1, 0xf0, 0x24, 0x33, 0x62, 0x72,
    0x82, 0x09, 0x0a, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x25, 0x26, 0x27, 0x28,
    0x29, 0x2a, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43, 0x44, 0x45,
    0x46, 0x47, 0x48, 0x49, 0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
    0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x73, 0x74, 0x75,
    0x76, 0x77, 0x78, 0x79, 0x7a, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
    0x8a, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0xa2, 0xa3,
    0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6,
    0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9,
    0xca, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xe1, 0xe2,
    0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xf1, 0xf2, 0xf3, 0xf4,
    0xf5, 0xf6, 0xf7, 0xf8, 0xf9, 0xfa]
STD_AC_CHROMA_BITS = [0, 2, 1, 2, 4, 4, 3, 4, 7, 5, 4, 4, 0, 1, 2, 0x77]
STD_AC_CHROMA_VAL = [
    0x00, 0x01, 0x02, 0x03, 0x11, 0x04, 0x05, 0x21, 0x31, 0x06, 0x12, 0x41,
    0x51, 0x07, 0x61, 0x71, 0x13, 0x22, 0x32, 0x81, 0x08, 0x14, 0x42, 0x91,
    0xa1, 0xb1, 0xc1, 0x09, 0x23, 0x33, 0x52, 0xf0, 0x15, 0x62, 0x72, 0xd1,
    0x0a, 0x16, 0x24, 0x34, 0xe1, 0x25, 0xf1, 0x17, 0x18, 0x19, 0x1a, 0x26,
    0x27, 0x28, 0x29, 0x2a, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43, 0x44,
    0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58,
    0x59, 0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x73, 0x74,
    0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87,
    0x88, 0x89, 0x8a, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a,
    0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4,
    0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7,
    0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda,
    0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xf2, 0xf3, 0xf4,
    0xf5, 0xf6, 0xf7, 0xf8, 0xf9, 0xfa]

STD_HUFF = {
    (0, 0): (STD_DC_LUMA_BITS, STD_DC_LUMA_VAL),
    (0, 1): (STD_DC_CHROMA_BITS, STD_DC_CHROMA_VAL),
    (1, 0): (STD_AC_LUMA_BITS, STD_AC_LUMA_VAL),
    (1, 1): (STD_AC_CHROMA_BITS, STD_AC_CHROMA_VAL),
}


def classify_huff(cls, tid, bits, vals):
    ref = STD_HUFF.get((cls, tid))
    if ref is None:
        return "unknown-slot"
    if list(bits) == list(ref[0]) and list(vals) == list(ref[1]):
        return "IJG-standard"
    return "custom-optimised"


# ---- ICC ------------------------------------------------------------------
def parse_icc(blob):
    if len(blob) < 132:
        return {"error": "short", "len": len(blob)}
    o = {"len": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}
    o["size_field"] = struct.unpack('>I', blob[0:4])[0]
    o["cmm"] = blob[4:8].decode('latin-1')
    o["version"] = "%d.%d.%d" % (blob[8], blob[9] >> 4, blob[9] & 0xF)
    o["device_class"] = blob[12:16].decode('latin-1')
    o["colorspace"] = blob[16:20].decode('latin-1')
    o["pcs"] = blob[20:24].decode('latin-1')
    y, m, d, hh, mm, ss = struct.unpack('>6H', blob[24:36])
    o["created"] = "%04d-%02d-%02dT%02d:%02d:%02d" % (y, m, d, hh, mm, ss)
    o["magic"] = blob[36:40].decode('latin-1')
    o["platform"] = blob[40:44].decode('latin-1')
    o["flags"] = struct.unpack('>I', blob[44:48])[0]
    o["manufacturer"] = blob[48:52].decode('latin-1')
    o["model"] = blob[52:56].decode('latin-1')
    o["rendering_intent"] = struct.unpack('>I', blob[64:68])[0]
    o["creator"] = blob[80:84].decode('latin-1')
    o["profile_id"] = blob[84:100].hex()
    n = struct.unpack('>I', blob[128:132])[0]
    tags = {}
    if 0 < n < 200:
        for i in range(n):
            p = 132 + 12 * i
            if p + 12 > len(blob):
                break
            sig = blob[p:p + 4].decode('latin-1')
            off, sz = struct.unpack('>II', blob[p + 4:p + 12])
            tags[sig] = [off, sz]
    o["tags"] = sorted(tags)
    o["ntags"] = n
    for want in ("desc", "cprt", "dmnd", "dmdd"):
        if want in tags:
            off, sz = tags[want]
            if off + sz <= len(blob):
                d0 = blob[off:off + sz]
                typ = d0[:4].decode('latin-1')
                txt = None
                if typ == 'desc' and len(d0) > 12:
                    ln = struct.unpack('>I', d0[8:12])[0]
                    txt = d0[12:12 + max(0, ln - 1)].decode('latin-1', 'replace')
                elif typ == 'mluc' and len(d0) > 28:
                    ln, ofs = struct.unpack('>II', d0[20:28])
                    txt = d0[ofs:ofs + ln].decode('utf-16-be', 'replace')
                elif typ in ('text', 'utf8'):
                    txt = d0[8:].split(b'\x00')[0].decode('latin-1', 'replace')
                o["icc_" + want] = {"type": typ, "text": txt}
    return o


# ---- main parse ------------------------------------------------------------
MARKER_NAMES = {0xC0: "SOF0", 0xC1: "SOF1", 0xC2: "SOF2", 0xC3: "SOF3",
                0xC4: "DHT", 0xC9: "SOF9", 0xCA: "SOF10", 0xCC: "DAC",
                0xD8: "SOI", 0xD9: "EOI", 0xDA: "SOS", 0xDB: "DQT",
                0xDC: "DNL", 0xDD: "DRI", 0xFE: "COM"}


def marker_name(m):
    if m in MARKER_NAMES:
        return MARKER_NAMES[m]
    if 0xE0 <= m <= 0xEF:
        return "APP%d" % (m - 0xE0)
    return "FF%02X" % m


def fingerprint(path):
    d = open(path, 'rb').read()
    o = {"file": os.path.basename(path), "path": path, "size": len(d),
         "sha256": hashlib.sha256(d).hexdigest(),
         "sha1": hashlib.sha1(d).hexdigest(),
         "markers": [], "dqt": [], "dht": [], "appn": [], "com": [],
         "dri": None, "sof": None, "icc": None, "trailing": 0}
    if not d.startswith(b'\xff\xd8'):
        o["error"] = "not a JPEG"
        return o
    i = 2
    icc_chunks = {}
    while i < len(d) - 1:
        if d[i] != 0xFF:
            i += 1
            continue
        m = d[i + 1]
        if m in (0xFF, 0x00):
            i += 1
            continue
        if m == 0xD8 or 0xD0 <= m <= 0xD7 or m == 0x01:
            o["markers"].append(marker_name(m))
            i += 2
            continue
        if m == 0xD9:
            o["markers"].append("EOI")
            o["eoi_offset"] = i
            o["trailing"] = len(d) - (i + 2)
            if o["trailing"] > 0:
                o["trailing_sha256"] = hashlib.sha256(d[i + 2:]).hexdigest()
                o["trailing_head_hex"] = d[i + 2:i + 34].hex()
            i += 2
            break
        if i + 4 > len(d):
            break
        L = struct.unpack('>H', d[i + 2:i + 4])[0]
        seg = d[i + 4:i + 2 + L]
        o["markers"].append(marker_name(m))
        if m == 0xDB:
            p = 0
            while p < len(seg):
                pq = seg[p] >> 4
                tq = seg[p] & 0xF
                p += 1
                n = 64 * (2 if pq else 1)
                raw = seg[p:p + n]
                p += n
                vals = list(struct.unpack('>64H', raw)) if pq else list(raw)
                base = STD_LUMA_ZZ if tq == 0 else STD_CHROMA_ZZ
                cands = qualities_consistent(vals, base)
                o["dqt"].append({"tq": tq, "prec": pq,
                                 "sha1": hashlib.sha1(raw).hexdigest(),
                                 "vals_zigzag": vals,
                                 "ijg_quality_candidates": cands,
                                 "matches_std_family": cands != []})
        elif m == 0xC4:
            p = 0
            while p + 17 <= len(seg):
                tc = seg[p] >> 4
                th = seg[p] & 0xF
                bits = list(seg[p + 1:p + 17])
                nv = sum(bits)
                vals = list(seg[p + 17:p + 17 + nv])
                p += 17 + nv
                o["dht"].append({"class": tc, "id": th, "nvals": nv, "bits": bits,
                                 "sha1": hashlib.sha1(bytes(bits) + bytes(vals)).hexdigest(),
                                 "classification": classify_huff(tc, th, bits, vals)})
        elif m == 0xDD:
            o["dri"] = struct.unpack('>H', seg[:2])[0]
        elif 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            comps = []
            for c in range(seg[5]):
                b = seg[6 + 3 * c: 9 + 3 * c]
                comps.append({"id": b[0], "h": b[1] >> 4, "v": b[1] & 0xF, "tq": b[2]})
            o["sof"] = {"marker": marker_name(m), "prec": seg[0],
                        "h": struct.unpack('>H', seg[1:3])[0],
                        "w": struct.unpack('>H', seg[3:5])[0],
                        "ncomp": seg[5], "components": comps,
                        "subsampling": "x".join("%d%d" % (c["h"], c["v"]) for c in comps),
                        "progressive": m == 0xC2}
        elif m == 0xFE:
            o["com"].append(seg.decode('latin-1', 'replace'))
        elif 0xE0 <= m <= 0xEF:
            ident = seg.split(b'\x00', 1)[0][:32].decode('latin-1', 'replace')
            rec = {"marker": marker_name(m), "ident": ident, "len": L,
                   "sha1": hashlib.sha1(seg).hexdigest()}
            if ident == 'ICC_PROFILE' and len(seg) > 14:
                sn, tot = seg[12], seg[13]
                icc_chunks[sn] = seg[14:]
                rec["icc_chunk"] = [sn, tot]
            elif ident == 'JFIF' and len(seg) >= 14:
                rec["jfif"] = {"ver": "%d.%02d" % (seg[5], seg[6]), "units": seg[7],
                               "xdensity": struct.unpack('>H', seg[8:10])[0],
                               "ydensity": struct.unpack('>H', seg[10:12])[0],
                               "thumb": [seg[12], seg[13]]}
            elif ident == 'Adobe' or seg[:5] == b'Adobe':
                rec["adobe"] = {"ver": struct.unpack('>H', seg[5:7])[0] if len(seg) > 6 else None,
                                "transform": seg[11] if len(seg) > 11 else None}
            elif ident == 'Exif':
                rec["exif_head_hex"] = seg[:64].hex()
            else:
                rec["head_hex"] = seg[:48].hex()
            o["appn"].append(rec)
        if m == 0xDA:
            j = i + 2 + L
            while j < len(d) - 1:
                if d[j] == 0xFF and d[j + 1] == 0xD9:
                    break
                j += 1
            i = j
            continue
        i += 2 + L
    if icc_chunks:
        blob = b"".join(icc_chunks[k] for k in sorted(icc_chunks))
        o["icc"] = parse_icc(blob)
        o["icc"]["nchunks"] = len(icc_chunks)
    o["marker_order"] = ",".join(o["markers"])
    o["fingerprint_vector"] = {
        "ncomp": o["sof"]["ncomp"] if o["sof"] else None,
        "subsampling": o["sof"]["subsampling"] if o["sof"] else None,
        "progressive": o["sof"]["progressive"] if o["sof"] else None,
        "dqt_sha1": [t["sha1"] for t in o["dqt"]],
        "ijg_q": sorted(set(tuple(t["ijg_quality_candidates"]) for t in o["dqt"])),
        "dht_class": sorted(set(t["classification"] for t in o["dht"])),
        "ndht": len(o["dht"]),
        "dri": o["dri"],
        "apps": [a["ident"] for a in o["appn"]],
        "icc_sha256": o["icc"]["sha256"] if o["icc"] else None,
        "marker_order": o["marker_order"],
        "geometry": [o["sof"]["w"], o["sof"]["h"]] if o["sof"] else None,
        "jfif": next((a.get("jfif") for a in o["appn"] if a.get("jfif")), None),
    }
    return o


def selftest():
    """PC1: encode a synthetic image at known qualities, recover each exactly."""
    from PIL import Image
    import numpy as np
    import tempfile
    rng = np.random.default_rng(3301)
    a = (rng.random((256, 256, 3)) * 255).astype('uint8')
    img = Image.fromarray(a)
    ok, rows = 0, []
    QS = [50, 75, 85, 90, 92, 95]
    for q in QS:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            p = f.name
        img.save(p, "JPEG", quality=q, subsampling=0)
        fp = fingerprint(p)
        cands = fp["dqt"][0]["ijg_quality_candidates"]
        hit = cands == [q]
        rows.append({"planted": q, "recovered": cands, "exact": hit,
                     "huff": sorted(set(t["classification"] for t in fp["dht"]))})
        ok += hit
        os.unlink(p)
    print(json.dumps({"control": "PC1 quality recovery", "n": len(QS),
                      "exact": ok, "rows": rows,
                      "PASS": ok == len(QS)}, indent=1))
    return ok == len(QS)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--selftest":
        sys.exit(0 if selftest() else 1)
    out = [fingerprint(p) for p in args]
    print(json.dumps(out if len(out) > 1 else out[0], indent=1))
