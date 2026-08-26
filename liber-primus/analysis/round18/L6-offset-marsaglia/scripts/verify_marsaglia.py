"""L6 / sub-lane B, step 1 — VERIFY BEFORE SWEEPING.  PREREG s5.2.

This repository has twice swept the wrong bytes: `_560.00` arrived as a silent 60.4%
prefix, and `DATA/560.13` arrived as a 134-byte Git-LFS pointer.  So nothing here is fed
to the decoder until its hash is checked against a published value.

Three independent published fingerprints are used:
  1. archive.org item metadata for `marsaglia-cdrom`  (md5 + sha1 + exact size)
  2. the CDROM's own `checksums.sha256.txt` (110 lines) for the inner files
  3. our own recomputation of all of the above

Writes data/MANIFEST.json in the shape of handoff/capsule/MANIFEST.json.
"""
import os, sys, json, hashlib, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_l6 as X

ISO = os.path.join(X.DATA, "MARSAGLIA_CDROM.iso")
CHK = os.path.join(X.DATA, "checksums.sha256.txt")
EXT = os.path.join(X.DATA, "iso")

# archive.org published item metadata, https://archive.org/metadata/marsaglia-cdrom
PUB = {"size": 634124288,
       "md5": "f127d50c2bd80e7c23f28184423a2d94",
       "sha1": "ca116df4940eb4b7538942ea6fbe454556b1bac2"}


def hashes(path, algos=("md5", "sha1", "sha256")):
    hs = {a: hashlib.new(a) for a in algos}
    n = 0
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            n += len(b)
            for h in hs.values():
                h.update(b)
    return n, {a: h.hexdigest() for a, h in hs.items()}


def main():
    man = {"lane": "round18/L6-offset-marsaglia", "generated": time.strftime("%Y-%m-%d"),
           "source_item": "https://archive.org/details/marsaglia-cdrom",
           "published_metadata": PUB, "gates": [], "iso": {}, "inner_files": [],
           "verified_pads": [], "unverified": []}

    # ---- gate 1: the ISO itself ------------------------------------------------
    size, h = hashes(ISO)
    ok = (size == PUB["size"] and h["md5"] == PUB["md5"] and h["sha1"] == PUB["sha1"])
    man["iso"] = {"path": "data/MARSAGLIA_CDROM.iso", "bytes": size, **h}
    man["gates"].append({"gate": "ISO size+md5+sha1 == archive.org published metadata",
                         "PASS": ok,
                         "detail": f"size {size} (want {PUB['size']}), md5 {h['md5']}, "
                                   f"sha1 {h['sha1']}"})
    print(("PASS " if ok else "FAIL ") + f"ISO {size:,} B  md5={h['md5']} sha1={h['sha1']}")
    print(f"      sha256={h['sha256']}  (recorded; archive.org publishes md5+sha1 only)")
    if not ok:
        X.jdump(man, os.path.join(X.DATA, "MANIFEST.json"))
        print("ISO does not match the published fingerprints — NOT SWEEPING.")
        return 1

    # ---- gate 2: checksums.sha256.txt ------------------------------------------
    pub_lines = []
    for ln in open(CHK):
        ln = ln.strip()
        if not ln:
            continue
        d, _, p = ln.partition("  ")
        pub_lines.append((d.strip().lower(), p.strip()))
    _, ch = hashes(CHK, ("sha256",))
    man["checksums_file"] = {"path": "data/checksums.sha256.txt", "lines": len(pub_lines),
                             "sha256": ch["sha256"]}
    print(f"      checksums.sha256.txt: {len(pub_lines)} published SHA-256 lines, "
          f"self sha256={ch['sha256']}")

    # ---- extract ---------------------------------------------------------------
    if not os.path.isdir(EXT) or not os.listdir(EXT):
        os.makedirs(EXT, exist_ok=True)
        print("      extracting with 7z ...", flush=True)
        r = subprocess.run(["7z", "x", "-y", f"-o{EXT}", ISO],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print("      7z exit", r.returncode)

    got = {}
    for root, _, files in os.walk(EXT):
        for fn in files:
            p = os.path.join(root, fn)
            n, hh = hashes(p, ("sha256",))
            got.setdefault(hh["sha256"], []).append((os.path.relpath(p, EXT), n))

    matched, missing = [], []
    for d, name in pub_lines:
        if d in got:
            rel, n = got[d][0]
            matched.append({"published_path": name, "extracted": rel, "bytes": n,
                            "sha256": d})
        else:
            missing.append({"published_path": name, "sha256": d})
    man["inner_files"] = matched
    man["unverified"] = missing
    man["gates"].append({"gate": "inner files verified against published SHA-256",
                         "PASS": len(missing) == 0,
                         "detail": f"{len(matched)}/{len(pub_lines)} published SHA-256 "
                                   f"lines matched an extracted file"})
    print(f"      inner files: {len(matched)}/{len(pub_lines)} published SHA-256s matched"
          + (f"; UNMATCHED: {[m['published_path'] for m in missing]}" if missing else ""))

    # ---- which of them are the RANDOM DATA (the pads) ---------------------------
    # BITS.01..BITS.60 are the 60 blocks of random bits; CALIF/CANADA/GERMANY.BIT are the
    # physically-sourced bit files.  Everything else on the disc is code, docs or
    # PostScript and is NOT random data - it is swept only as part of the whole-ISO pad.
    pads, seen = [], set()
    for m in matched:
        base = os.path.basename(m["published_path"]).upper()
        if base.startswith("BITS.") or base.endswith(".BIT"):
            if m["sha256"] in seen:
                continue
            seen.add(m["sha256"])
            pads.append({"name": base, "extracted": m["extracted"], "bytes": m["bytes"],
                         "sha256": m["sha256"],
                         "verified_against": "checksums.sha256.txt (published on the CDROM "
                                             "item, archive.org/details/marsaglia-cdrom)"})
    pads.sort(key=lambda r: r["name"])
    man["verified_pads"] = pads
    tot = sum(p["bytes"] for p in pads)
    print(f"      random-data pads: {len(pads)} files, {tot:,} bytes, ALL hash-verified")
    man["random_data_bytes"] = tot
    man["all_gates_pass"] = all(g["PASS"] for g in man["gates"])
    X.jdump(man, os.path.join(X.DATA, "MANIFEST.json"))
    print("MANIFEST:", os.path.join(X.DATA, "MANIFEST.json"),
          "  gates:", "PASS" if man["all_gates_pass"] else "FAIL")
    return 0 if man["all_gates_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
