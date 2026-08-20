#!/usr/bin/env python3
"""Lane A fetcher. Downloads a URL to a path under A-primary-artifacts/ and
appends a provenance row to MANIFEST.json. Hashes are always computed, never copied.

usage: python _tools/grab.py <dest-relative-path> <url> [note]
       python _tools/grab.py --batch <tsv file: dest<TAB>url<TAB>note>
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import os
MANIFEST = ROOT / os.environ.get("LANE_A_MANIFEST", "MANIFEST.json")
TIMEOUT = "150"


def load():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"generated_utc": None, "items": []}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def grab(dest, url, note=""):
    out = ROOT / dest
    out.parent.mkdir(parents=True, exist_ok=True)
    hdr = out.parent / (out.name + ".headers")
    r = subprocess.run(
        ["curl", "-sSL", "--max-time", TIMEOUT, "-D", str(hdr), "-o", str(out),
         "-A", "Mozilla/5.0 (corpus-recovery; research archival)",
         "-w", "%{http_code}\t%{content_type}\t%{size_download}\t%{url_effective}", url],
        capture_output=True, text=True,
    )
    parts = (r.stdout.strip().split("\t") + ["", "", "", ""])[:4]
    code, ctype, size, eff = parts
    row = {
        "path": str(dest).replace("\\", "/"),
        "source_url": url,
        "effective_url": eff or None,
        "http_status": code,
        "content_type": ctype or None,
        "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": note,
    }
    if out.exists():
        row["bytes"] = out.stat().st_size
        row["sha256"] = sha256_file(out)
        body = out.read_bytes()[:400]
        if code != "200" or b"<!DOCTYPE html" in body[:120] and not str(dest).endswith((".html", ".htm")):
            row["suspect"] = True
    else:
        row["bytes"] = 0
        row["sha256"] = None
        row["failed"] = True
    if hdr.exists():
        try:
            row["response_headers"] = hdr.read_text(errors="replace").strip().splitlines()[:25]
        except Exception:
            pass
        hdr.unlink()
    return row


def main():
    data = load()
    seen = {i["path"] for i in data["items"]}
    jobs = []
    if sys.argv[1] == "--batch":
        for line in Path(sys.argv[2]).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            f = line.split("\t")
            jobs.append((f[0], f[1], f[2] if len(f) > 2 else ""))
    else:
        jobs.append((sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ""))

    for dest, url, note in jobs:
        if dest in seen:
            print(f"SKIP(dup) {dest}")
            continue
        row = grab(dest, url, note)
        data["items"] = [i for i in data["items"] if i["path"] != dest]
        data["items"].append(row)
        flag = "!!" if row.get("failed") or row.get("suspect") else "ok"
        print(f"{flag} {row['http_status']} {row['bytes']:>10} {dest}")
        data["generated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        MANIFEST.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"manifest: {len(data['items'])} items")


if __name__ == "__main__":
    main()
