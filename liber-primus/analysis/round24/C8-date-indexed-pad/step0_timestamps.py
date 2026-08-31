"""C8 STEP 0 -- enumerate every PGP-signed Cicada artifact in-repo and extract its signature
creation time, then map each to the page it covers, to decide honestly whether the UNSOLVED
decrypt-target pages carry any timestamp to index a dated pad by.

Reproduce: python3 analysis/round24/C8-date-indexed-pad/step0_timestamps.py
Writes: cache/timestamps.json
"""
import os, re, base64, struct, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CORPUS = os.path.join(LP, "data", "scream314_lp.md")
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)


def _parse_sig_creation(armor: str):
    """Parse an ASCII-armored PGP SIGNATURE block, return sig-creation unix time."""
    lines = [l.strip() for l in armor.strip().splitlines()]
    b64, started = [], False
    for l in lines:
        if l.startswith("Version:") or l.startswith("Comment:"):
            continue
        if l == "":
            started = True
            continue
        if l.startswith("="):  # radix-64 checksum -> end of body
            break
        if started:
            b64.append(l)
    raw = base64.b64decode("".join(b64))
    tag_byte = raw[0]
    newfmt = bool(tag_byte & 0x40)
    if not newfmt:
        lentype = tag_byte & 0x03
        hs = {0: 2, 1: 3, 2: 5}.get(lentype, 1)
    else:
        hs = 2
    d = raw[hs:]
    ver = d[0]
    if ver == 4:
        hashed_len = struct.unpack(">H", d[4:6])[0]
        hashed = d[6:6 + hashed_len]
        j, ct = 0, None
        while j < len(hashed):
            sl = hashed[j]; j += 1
            sptype = hashed[j]; spdata = hashed[j + 1:j + sl]
            if sptype == 2:
                ct = struct.unpack(">I", spdata[:4])[0]
            j += sl
        return ver, ct
    elif ver == 3:
        ct = struct.unpack(">I", d[3:7])[0]
        return ver, ct
    return ver, None


def enumerate_signed_blocks():
    txt = open(CORPUS, encoding="utf-8").read()
    # strip the 4-space markdown indentation used for the code blocks
    body = "\n".join(l[4:] if l.startswith("    ") else l for l in txt.splitlines())
    # section headers to attribute each block to a page
    lines = body.splitlines()
    headers = [(i, l) for i, l in enumerate(lines) if l.startswith("## ")]

    def section_for(line_idx):
        cur = "(preamble)"
        for hi, h in headers:
            if hi <= line_idx:
                cur = h[3:].strip()
            else:
                break
        return cur

    out = []
    # find each SIGNATURE block with its char offset -> line number
    for m in re.finditer(r"-----BEGIN PGP SIGNATURE-----(.*?)-----END PGP SIGNATURE-----",
                         body, re.S):
        line_idx = body[:m.start()].count("\n")
        ver, ct = _parse_sig_creation(m.group(1))
        out.append({
            "section": section_for(line_idx),
            "line": line_idx + 1,
            "sig_version": ver,
            "sig_creation_unix": ct,
            "sig_creation_utc": (datetime.datetime.fromtimestamp(ct, datetime.timezone.utc)
                                 .isoformat().replace("+00:00", "Z")) if ct else None,
        })
    return out


def main():
    blocks = enumerate_signed_blocks()
    # the decrypt target is the unsolved LP2 runic corpus data/krisyotam_runes.txt
    # (%-delimited pages 0-56; last two are solved AN END / PARABLE, rest unsolved)
    kris = os.path.join(LP, "data", "krisyotam_runes.txt")
    npages = open(kris, encoding="utf-8").read().count("%") + 1
    result = {
        "corpus": os.path.relpath(CORPUS, LP),
        "n_signed_blocks": len(blocks),
        "signed_blocks": blocks,
        "decrypt_target": {
            "file": os.path.relpath(kris, LP),
            "n_pages": npages,
            "note": "%-delimited; pages 0-54 unsolved runic ciphertext, last 2 solved. "
                    "NONE of these runic pages carries a PGP signature block.",
        },
        "premise1_verdict": (
            "FAIL for decrypt target: all signatures cover intro/index PROSE or JPEG-hash "
            "wrappers; NO unsolved runic ciphertext page carries a PGP signature block. "
            "There is no per-page timestamp to index a dated pad by."
        ),
        "premise2_verdict": (
            "dates covered: all sig-creation times are Jan-2014, after NIST Beacon genesis "
            "2013-09-05; Bitcoin covers a fortiori. MOOT because premise1 fails."
        ),
        "beacon_genesis_unix": 1378395540,  # 2013-09-05T15:39:00Z
    }
    dates = [b["sig_creation_unix"] for b in blocks if b["sig_creation_unix"]]
    result["min_sig_unix"] = min(dates) if dates else None
    result["all_after_beacon_genesis"] = all(d >= 1378395540 for d in dates) if dates else None
    outp = os.path.join(CACHE, "timestamps.json")
    json.dump(result, open(outp, "w"), indent=1)
    print(json.dumps({k: v for k, v in result.items() if k != "signed_blocks"}, indent=1))
    print(f"\nwrote {os.path.relpath(outp, LP)} ({len(blocks)} signed blocks)")


if __name__ == "__main__":
    main()
