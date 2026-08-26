"""C2 — INDEPENDENT re-verification of the Marsaglia CDROM bytes on disk.

Deliberately does NOT read data/MANIFEST.json.  Round 12 was burned twice by a file that
was not what it claimed (a 60.4% prefix of `_560.00`; a 134-byte Git-LFS pointer standing
in for DATA/560.13), and handoff/capsule/verify_capsule.py exists precisely because a
manifest written by the fetching process is not independent evidence about the fetched
bytes.  So: recompute from the bytes, compare against the two PUBLISHED sources
(archive.org item metadata for the ISO, the CDROM's own checksums.sha256.txt for the 110
inner files), and report PASS / DRIFT / ABSENT per file, DRIFT separately from ABSENT.
"""
import os, sys, json, hashlib, time

LANE = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round18/L6-offset-marsaglia"
OUT = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round19/C2"
DATA = os.path.join(LANE, "data")

# published on archive.org/details/marsaglia-cdrom (marsaglia-cdrom_files.xml, re-read here)
PUB_ISO = {"size": 634124288,
           "md5": "f127d50c2bd80e7c23f28184423a2d94",
           "sha1": "ca116df4940eb4b7538942ea6fbe454556b1bac2"}
PUB_CHECKSUMS_TXT = {"size": 11247,
                     "md5": "cc8cf878d7688dc0f2eaad42da444e85",
                     "sha1": "9b3b921a2068b9ed93690746ac003f9dbbcecf3f"}


def digests(path, algos=("md5", "sha1", "sha256")):
    h = {a: hashlib.new(a) for a in algos}
    n = 0
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            n += len(b)
            for x in h.values():
                x.update(b)
    return n, {a: h[a].hexdigest() for a in algos}


def main():
    t0 = time.time()
    rep = {"lane": "round19/C2", "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
           "independent_of": "round18/L6-offset-marsaglia/data/MANIFEST.json (not read)",
           "published_sources": {
               "iso": "archive.org/details/marsaglia-cdrom -> marsaglia-cdrom_files.xml",
               "inner": "checksums.sha256.txt, published on the same item (110 lines)"},
           "files": [], "counts": {}}

    # ---- gate 0: the checksums manifest itself is the published object we trust for the
    # inner files, so it is verified against archive.org's md5/sha1 for it FIRST.
    p = os.path.join(DATA, "checksums.sha256.txt")
    if not os.path.exists(p):
        rep["files"].append({"file": "checksums.sha256.txt", "verdict": "ABSENT"})
    else:
        n, d = digests(p)
        ok = (n == PUB_CHECKSUMS_TXT["size"] and d["md5"] == PUB_CHECKSUMS_TXT["md5"]
              and d["sha1"] == PUB_CHECKSUMS_TXT["sha1"])
        rep["files"].append({"file": "checksums.sha256.txt", "bytes": n, **d,
                             "published": PUB_CHECKSUMS_TXT,
                             "verdict": "PASS" if ok else "DRIFT"})

    # ---- gate 1: the ISO against archive.org's published md5/sha1/size
    p = os.path.join(DATA, "MARSAGLIA_CDROM.iso")
    if not os.path.exists(p):
        rep["files"].append({"file": "MARSAGLIA_CDROM.iso", "verdict": "ABSENT"})
    else:
        n, d = digests(p)
        ok = (n == PUB_ISO["size"] and d["md5"] == PUB_ISO["md5"]
              and d["sha1"] == PUB_ISO["sha1"])
        rep["files"].append({"file": "MARSAGLIA_CDROM.iso", "bytes": n, **d,
                             "published": PUB_ISO, "verdict": "PASS" if ok else "DRIFT",
                             "note": "sha256 is recorded, not compared: archive.org "
                                     "publishes md5/sha1/crc32 for the item file, not sha256"})

    # ---- gate 2: every one of the 110 published inner files, by its own published sha256
    lines = [l.split() for l in open(os.path.join(DATA, "checksums.sha256.txt"))
             if l.strip()]
    for want, pub_path in lines:
        base = pub_path.split("/")[-1]
        # the extractor flattened the ISO tree; look for the basename, then the full tail
        cands = [os.path.join(DATA, "iso", base),
                 os.path.join(DATA, "iso", *pub_path.split("/")[3:])]
        got = next((c for c in cands if os.path.isfile(c)), None)
        if got is None:
            rep["files"].append({"file": pub_path, "verdict": "ABSENT",
                                 "published_sha256": want})
            continue
        n, d = digests(got, ("sha256",))
        rep["files"].append({"file": pub_path, "local": os.path.relpath(got, DATA),
                             "bytes": n, "sha256": d["sha256"],
                             "published_sha256": want,
                             "verdict": "PASS" if d["sha256"] == want else "DRIFT"})

    c = {}
    for f in rep["files"]:
        c[f["verdict"]] = c.get(f["verdict"], 0) + 1
    rep["counts"] = c
    rep["all_gates_pass"] = (c.get("DRIFT", 0) == 0 and c.get("ABSENT", 0) == 0)
    rep["random_data_pads"] = sorted(
        os.path.basename(f["file"]) for f in rep["files"]
        if f["verdict"] == "PASS" and f.get("bytes") == 10_000_000)
    rep["random_data_bytes"] = 10_000_000 * len(rep["random_data_pads"])
    rep["wall_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT, "out_verify.json"), "w") as f:
        json.dump(rep, f, indent=1)
    print(json.dumps(c), "all_gates_pass", rep["all_gates_pass"],
          "pads", len(rep["random_data_pads"]), f"{rep['wall_s']}s")


if __name__ == "__main__":
    main()
