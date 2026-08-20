#!/usr/bin/env python3
"""Build corpus/B-liber-primus/MANIFEST.json.

Every file this lane fetched gets one row: path, sha256, bytes, source_url,
retrieved_utc. URLs come from hunt_results.json (which recorded them at fetch
time) plus an explicit table for the files fetched by hand with curl. A file
whose URL cannot be established is emitted with source_url=null and listed in
the `unattributed` block rather than being given an invented URL.

Run: PYTHONUTF8=1 python corpus/B-liber-primus/build_manifest.py
"""
import os
import json
import hashlib
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FETCHED = os.path.join(HERE, "fetched")
OUT = os.path.join(HERE, "MANIFEST.json")

# Files fetched directly with curl, outside the hunt tool.
EXPLICIT = {
    "transcriptions.rne":
        "https://raw.githubusercontent.com/dude123124144/Liber-Primus-Runes-OCR/master/misc_scripts/transcriptions.rne",
    "ia_liber-primus_metadata.json": "https://archive.org/metadata/liber-primus",
    "ia_search.json": "https://archive.org/advancedsearch.php?q=liber+primus+OR+cicada3301&output=json&rows=60",
    "ghrepo.json": "https://api.github.com/repos/dude123124144/Liber-Primus-Runes-OCR",
    "ghtree.json": "https://api.github.com/repos/dude123124144/Liber-Primus-Runes-OCR/git/trees/master?recursive=1",
    "zenodo_18199474/record.json": "https://zenodo.org/api/records/18199474",
    "zenodo_18199474/liber-primus__transcription--master.txt":
        "https://zenodo.org/api/records/18199474/files/liber-primus__transcription--master.txt/content",
    "zenodo_18199474/liber-primus__translation.txt":
        "https://zenodo.org/api/records/18199474/files/liber-primus__translation.txt/content",
    "zenodo_18199474/liber-primus__keys.txt":
        "https://zenodo.org/api/records/18199474/files/liber-primus__keys.txt/content",
    "zenodo_18199474/metodo.txt":
        "https://zenodo.org/api/records/18199474/files/metodo.txt/content",
}

# Derived deliverables of this lane (in-repo, not fetched).
DERIVED = [
    ("corpus/B-liber-primus/PAGES.json", "built by corpus/B-liber-primus/build_pages.py"),
    ("corpus/B-liber-primus/hunt_results.json", "built by corpus/B-liber-primus/hunt_transcriptions.py"),
    ("corpus/B-liber-primus/CONFLICT-henkman-2016.json", "built by corpus/B-liber-primus/align_henkman.py"),
]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    urls = {}
    hr = os.path.join(HERE, "hunt_results.json")
    if os.path.exists(hr):
        for repo in json.load(open(hr, encoding="utf-8"))["repos"]:
            for f in repo.get("files", []):
                urls[os.path.normpath(os.path.join(ROOT, f["local"]))] = f["source_url"]

    rows, unattributed = [], []
    for dirpath, _dirs, files in os.walk(FETCHED):
        for fn in sorted(files):
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, FETCHED).replace("\\", "/")
            url = urls.get(os.path.normpath(p)) or EXPLICIT.get(rel)
            st = os.stat(p)
            row = {
                "path": "corpus/B-liber-primus/fetched/" + rel,
                "sha256": sha256(p),
                "bytes": st.st_size,
                "source_url": url,
                "retrieved_utc": datetime.datetime.fromtimestamp(
                    st.st_mtime, datetime.timezone.utc).isoformat(timespec="seconds"),
            }
            rows.append(row)
            if url is None:
                unattributed.append(row["path"])

    der = []
    for rel, how in DERIVED:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        st = os.stat(p)
        der.append({"path": rel, "sha256": sha256(p), "bytes": st.st_size,
                    "source_url": None, "derived_by": how,
                    "retrieved_utc": datetime.datetime.fromtimestamp(
                        st.st_mtime, datetime.timezone.utc).isoformat(timespec="seconds")})

    data = {
        "$comment": ("Provenance for everything Lane B fetched. Hashes are measured, "
                     "URLs are recorded at fetch time. Nothing here is invented."),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "generator": "corpus/B-liber-primus/build_manifest.py",
        "n_fetched": len(rows),
        "n_bytes_fetched": sum(r["bytes"] for r in rows),
        "unattributed": unattributed,
        "fetched": sorted(rows, key=lambda r: r["path"]),
        "derived_in_repo": der,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("wrote %s  (%d fetched files, %d bytes, %d unattributed)"
          % (OUT, len(rows), data["n_bytes_fetched"], len(unattributed)))
    for u in unattributed:
        print("  UNATTRIBUTED: %s" % u)


if __name__ == "__main__":
    main()
