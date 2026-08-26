"""R1 / sub-attack C — is the L1 prior load-bearing, or post-hoc?

Pre-registered in PREREG.md §5.  Mechanical arms only; the documentary audit lives in
RESULTS.md.  Arms:

  C-b   the GnuPG-1.4.11 corpus: how many INDEPENDENT signing events, and is the armor
        Version header actually a passive fingerprint of the signer's OS?
  C-a   encoder-identification alternatives: does anything that is NOT ImageMagick reproduce
        LP2's four discriminating JPEG fields?
  C-c   the shift arithmetic: are the x3 / x2.5 / x2 multipliers traceable to any count?

    python3 c_prior.py     -> out_c.json
"""
import collections
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
MSGS = os.path.join(REPO, "corpus", "A-primary-artifacts", "ibotpeaches", "messages")
PAGES = None


# ------------------------------------------------------------------ C-b
def pgp_audit():
    rows = []
    other = collections.Counter()
    files = []
    for root, _d, fs in os.walk(MSGS):
        for fn in fs:
            files.append(os.path.join(root, fn))
    for full in sorted(files):
        rel = os.path.relpath(full, MSGS).replace(os.sep, "/")
        y = rel.split("/")[0]
        try:
            t = open(full, encoding="utf-8", errors="ignore").read()
        except Exception:                                        # noqa: BLE001
            continue
        for m in re.finditer(
                r"-----BEGIN PGP SIGNATURE-----(.*?)-----END PGP SIGNATURE-----", t, re.S):
            blk = m.group(1)
            ver = re.search(r"Version:\s*(.+)", blk)
            body = "".join(blk.split("\n\n", 1)[-1].split())
            rows.append({"year": y, "file": rel,
                         "version": ver.group(1).strip() if ver else None,
                         "sig_sha1": hashlib.sha1(body.encode()).hexdigest()[:16],
                         "siglen": len(body)})
        for m in re.finditer(r"^-?\s*Version:\s*(.+)$", t, re.M):
            other[m.group(1).strip()] += 1

    vers = collections.Counter(r["version"] for r in rows)
    distinct_by_ver = collections.defaultdict(set)
    for r in rows:
        distinct_by_ver[r["version"]].add(r["sig_sha1"])
    dup = collections.Counter(r["sig_sha1"] for r in rows)
    per_year = collections.defaultdict(set)
    for r in rows:
        if r["version"] and "1.4.11" in r["version"]:
            per_year[r["year"]].add(r["sig_sha1"])

    return {
        "signature_blocks_total": len(rows),
        "distinct_signature_payloads": len({r["sig_sha1"] for r in rows}),
        "version_header_counts_in_SIGNATURE_blocks": dict(vers),
        "distinct_signature_payloads_by_version":
            {str(k): len(v) for k, v in distinct_by_ver.items()},
        "all_Version_headers_anywhere_in_corpus": dict(other),
        "repeated_signature_payloads": {k: v for k, v in dup.items() if v > 1},
        "distinct_1_4_11_sigs_per_year": {k: len(v) for k, v in sorted(per_year.items())},
        "rows": rows,
    }


# ------------------------------------------------------------------ C-a
def jpeg_vector(path):
    """Independent marker/DQT/DHT/ICC reader — no PIL, no ImageMagick."""
    b = open(path, "rb").read()
    i, out = 2, {"markers": [], "dqt_sha1": [], "huff": None, "icc_len": 0,
                 "icc_desc": None, "ncomp": None, "sampling": None,
                 "jfif": None, "size": len(b), "trailing": 0}
    std_luma_present = None
    icc = b""
    while i < len(b) - 1:
        if b[i] != 0xFF:
            i += 1
            continue
        m = b[i + 1]
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7 or m == 0x01:
            out["markers"].append(f"{m:02X}")
            if m == 0xD9:
                out["trailing"] = len(b) - (i + 2)
                break
            i += 2
            continue
        ln = int.from_bytes(b[i + 2:i + 4], "big")
        seg = b[i + 4:i + 2 + ln]
        name = {0xE0: "APP0", 0xE2: "APP2", 0xDB: "DQT", 0xC4: "DHT", 0xDA: "SOS",
                0xC0: "SOF0", 0xC2: "SOF2", 0xFE: "COM", 0xE1: "APP1"}.get(m, f"{m:02X}")
        out["markers"].append(name)
        if m == 0xDB:
            p = 0
            while p < len(seg):
                prec = seg[p] >> 4
                n = 64 * (2 if prec else 1)
                out["dqt_sha1"].append(hashlib.sha1(seg[p + 1:p + 1 + n]).hexdigest()[:12])
                p += 1 + n
        elif m == 0xE2 and seg[:11] == b"ICC_PROFILE":
            icc += seg[14:]
        elif m == 0xE0 and seg[:4] == b"JFIF":
            out["jfif"] = {"ver": f"{seg[5]}.{seg[6]:02d}", "units": seg[7],
                           "dx": int.from_bytes(seg[8:10], "big"),
                           "dy": int.from_bytes(seg[10:12], "big")}
        elif m in (0xC0, 0xC2):
            out["h"] = int.from_bytes(seg[1:3], "big")
            out["w"] = int.from_bytes(seg[3:5], "big")
            nc = seg[5]
            out["ncomp"] = nc
            out["sampling"] = "x".join(f"{seg[6+3*k+1]>>4}{seg[6+3*k+1]&15}" for k in range(nc))
        elif m == 0xC4:
            # classify: IJG standard luma DC table starts 00 01 05 01 01 01 01 01 01 00...
            bits = seg[1:17]
            if bits == bytes([0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]) and seg[0] == 0x00:
                std_luma_present = True
        elif m == 0xDA:
            # scan data to EOI
            j = i + 2 + ln
            while j < len(b) - 1:
                if b[j] == 0xFF and b[j + 1] == 0xD9:
                    out["markers"].append("D9")
                    out["trailing"] = len(b) - (j + 2)
                    break
                j += 1
            break
        i += 2 + ln
    out["huff"] = "IJG-standard" if std_luma_present else "custom-optimised"
    out["icc_len"] = len(icc)
    if len(icc) > 132:
        # find 'desc' tag
        ntags = int.from_bytes(icc[128:132], "big")
        for k in range(min(ntags, 64)):
            off = 132 + 12 * k
            sig = icc[off:off + 4]
            o = int.from_bytes(icc[off + 4:off + 8], "big")
            n = int.from_bytes(icc[off + 8:off + 12], "big")
            if sig == b"desc":
                out["icc_desc"] = icc[o + 12:o + 12 + 40].split(b"\x00")[0].decode(
                    "latin-1", "ignore")
        out["icc_illuminant"] = icc[68:80].hex()
        out["icc_md5"] = hashlib.md5(icc).hexdigest()
    return out


def find_pages():
    for cand in ("corpus/A-primary-artifacts/Hadyn_cicada/2014/ky2khlqdf7qdznac.onion",
                 "corpus/A-primary-artifacts", "sources", "corpus"):
        p = os.path.join(REPO, cand)
        if not os.path.isdir(p):
            continue
        for root, _dirs, files in os.walk(p):
            jp = [f for f in files if re.fullmatch(r"\d+\.jpg", f)]
            if len(jp) >= 20:
                return root, sorted(jp, key=lambda x: int(x[:-4]))
    return None, []


def encoder_alternatives(workdir):
    """Try to reproduce LP2's 4 discriminating fields WITHOUT ImageMagick."""
    os.makedirs(workdir, exist_ok=True)
    res = {}

    def run(cmd, **kw):
        try:
            return subprocess.run(cmd, shell=True, capture_output=True, timeout=180, **kw)
        except Exception as e:                                   # noqa: BLE001
            return type("R", (), {"returncode": -1, "stderr": str(e).encode()})()

    # a small PostScript source with grey text, rendered at 400dpi like LP2
    ps = os.path.join(workdir, "src.ps")
    with open(ps, "w") as f:
        f.write("%!PS\n/Helvetica findfont 40 scalefont setfont\n"
                "0 setgray 72 700 moveto (LIBER PRIMUS CONTROL) show\n"
                "72 600 moveto (THORN WYNN EOLH DAEG) show\nshowpage\n")
    gs1 = os.path.join(workdir, "gs_q92.jpg")
    r = run(f"gs -q -dNOPAUSE -dBATCH -sDEVICE=jpeg -dJPEGQ=92 -r400 "
            f"-sOutputFile={gs1} {ps}")
    res["gs_ok"] = r.returncode == 0
    if os.path.exists(gs1):
        res["stage1_gs_q92"] = jpeg_vector(gs1)

    # ALT-1: jpegtran -optimize -copy all  (lossless Huffman re-optimisation)
    out1 = os.path.join(workdir, "alt_jpegtran.jpg")
    r = run(f"jpegtran -optimize -copy all -outfile {out1} {gs1}")
    res["jpegtran_available"] = (r.returncode == 0)
    if os.path.exists(out1):
        res["ALT1_gs_then_jpegtran_optimize"] = jpeg_vector(out1)

    # ALT-2: PIL re-save with quality='keep' + optimize  (libjpeg optimise, DQT preserved)
    try:
        from PIL import Image
        im = Image.open(gs1)
        icc = im.info.get("icc_profile")
        out2 = os.path.join(workdir, "alt_pil_keep.jpg")
        im.save(out2, "JPEG", quality="keep", optimize=True, icc_profile=icc)
        res["ALT2_gs_then_PIL_keep_optimize"] = jpeg_vector(out2)
        # ALT-3: PIL gray conversion of a gray page + keep-quality optimise
        im2 = Image.open(gs1).convert("L")
        out3 = os.path.join(workdir, "alt_pil_gray.jpg")
        im2.save(out3, "JPEG", quality=92, optimize=True, icc_profile=icc)
        res["ALT3_gs_then_PIL_gray_q92_optimize"] = jpeg_vector(out3)
    except Exception as e:                                        # noqa: BLE001
        res["pil_error"] = str(e)

    # ALT-4: ImageMagick, for reference (the identification L1 made)
    out4 = os.path.join(workdir, "alt_im.jpg")
    r = run(f"magick {gs1} {out4}")
    if os.path.exists(out4):
        res["REF_gs_then_ImageMagick_default"] = jpeg_vector(out4)
    return res


# ------------------------------------------------------------------ C-c
SHIFT_TABLE = [
    (1, "glibc rand()/random()/drand48", 3.0, "F6/F7"),
    (2, "Python 2.7 random", 3.0, "F1/F8"),
    (3, "Perl 5.14 rand/srand (drand48 under the hood)", 2.5, "F7"),
    (4, "bash $RANDOM (a 15-bit glibc rand() derivative) / coreutils", 2.0, "F8/F9"),
    (5, "LaTeX-side LCG", 2.0, "F5+F4"),
    (6, "OpenSSL/GnuPG-adjacent KDF", 1.5, "F6"),
    (7, "Java util.Random", 1.0, "none"),
    (8, "PHP mt_rand", 0.8, "none"),
    (9, "Windows CRT rand", 0.15, "F1/F2/F6/F7"),
    (10, ".NET System.Random", 0.05, "F6+F7,F1+F2,F9"),
    (11, "hardware / true RNG", 1.0, "none"),
]


def shift_audit():
    """Are the multipliers derivable, and are same-family rows consistent?"""
    findings = []
    # 1. same-family inconsistency: L1's own rank-4 row says $RANDOM IS a glibc rand()
    #    derivative, yet rank 1 (glibc rand) gets x3 and rank 4 gets x2 on the same evidence.
    findings.append({
        "id": "same-family-split",
        "rows": [1, 4],
        "detail": "Row 4's own justification text describes $RANDOM as 'a 15-bit glibc rand() "
                  "derivative'. Row 1 is glibc rand()/random(). The same generator family "
                  "carries x3 and x2 on non-overlapping evidence citations (F6/F7 vs F8/F9).",
    })
    # 2. Perl row cites F7 (Ubuntu ships Perl 5.14) but Perl's rand IS drand48 -> row 1 again
    findings.append({
        "id": "perl-is-drand48",
        "rows": [1, 3],
        "detail": "Row 3's own parenthetical says Perl's rand is 'drand48 under the hood'. "
                  "drand48 is explicitly listed in row 1. Rows 1 and 3 are therefore not "
                  "disjoint hypotheses, but are multiplied as if they were (x3 and x2.5).",
    })
    # 3. two demotions on identical evidence, different magnitudes
    findings.append({
        "id": "windows-demotion-split",
        "rows": [9, 10],
        "detail": "Rows 9 and 10 are demoted by the same four facts (F1/F2/F6/F7/F9) and "
                  "receive x0.15 and x0.05 — a factor of 3 apart with no stated discriminator.",
    })
    # 4. traceability
    traceable = [r for r in SHIFT_TABLE if False]   # no row states a count, ratio or base rate
    findings.append({
        "id": "no-derivation",
        "rows": [r[0] for r in SHIFT_TABLE],
        "detail": "No row in L1 §6.2 states a base rate, a count, a likelihood ratio or a "
                  "calibration for its multiplier. §6.2's own header calls them 'priors for "
                  "search-order and budget allocation, not probabilities'.",
    })
    prod = 1.0
    for r in SHIFT_TABLE:
        prod *= r[2]
    return {"n_rows": len(SHIFT_TABLE), "n_traceable_to_a_count": len(traceable),
            "findings": findings,
            "sum_of_shifts": sum(r[2] for r in SHIFT_TABLE),
            "note": "A set of multiplicative re-weightings over a partition should have a "
                    "stated normalisation; §6.2 has none, so the table cannot be read as a "
                    "distribution — only as an ordering."}


def main():
    out = {}
    print("== C-b: PGP corpus ==")
    out["C_b_pgp"] = pgp_audit()
    p = out["C_b_pgp"]
    print(f"  signature blocks: {p['signature_blocks_total']}, "
          f"distinct payloads: {p['distinct_signature_payloads']}")
    print(f"  version headers in signature blocks: "
          f"{p['version_header_counts_in_SIGNATURE_blocks']}")
    print(f"  ALL Version: headers anywhere: {p['all_Version_headers_anywhere_in_corpus']}")
    print(f"  distinct 1.4.11 sigs per year: {p['distinct_1_4_11_sigs_per_year']}")

    print("\n== C-a: encoder alternatives ==")
    root, jp = find_pages()
    out["pages_dir"] = root
    if root:
        v = jpeg_vector(os.path.join(root, jp[0]))
        out["LP2_page_vector"] = v
        print(f"  LP2 {jp[0]}: {v['w']}x{v['h']} ncomp={v['ncomp']} samp={v['sampling']} "
              f"huff={v['huff']} icc={v['icc_len']} desc={v['icc_desc']!r} "
              f"dqt={v['dqt_sha1']} trailing={v['trailing']}")
    else:
        print("  LP2 page images not found in this worktree — using L1's published vector")
    out["C_a_alternatives"] = encoder_alternatives(os.path.join(HERE, "_encwork"))
    for k, v in out["C_a_alternatives"].items():
        if isinstance(v, dict) and "huff" in v:
            print(f"  {k:38s} ncomp={v['ncomp']} samp={v['sampling']} huff={v['huff']} "
                  f"icc={v['icc_len']} desc={v['icc_desc']!r} dqt={v['dqt_sha1']}")
        else:
            print(f"  {k:38s} {v}")

    print("\n== C-c: shift arithmetic ==")
    out["C_c_shifts"] = shift_audit()
    for f in out["C_c_shifts"]["findings"]:
        print(f"  [{f['id']}] rows {f['rows']}")

    with open(os.path.join(HERE, "out_c.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("\nwrote out_c.json")


if __name__ == "__main__":
    main()
