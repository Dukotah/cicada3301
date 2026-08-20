#!/usr/bin/env python3
"""Bulk-pull the uncovering-cicada.fandom.com image set with provenance.

Resumable: skips any file already present with the recorded byte size.
Writes provenance rows to _logs/fandom_manifest.json continuously so a kill
loses at most one file. Verifies each download against the wiki's own SHA-1.
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIST = ROOT / "_logs" / "fandom_allimages.json"
OUT = ROOT / "wiki-uncovering-cicada" / "images"
MAN = ROOT / "_logs" / "fandom_manifest.json"


def sha_both(p):
    h1, h2 = hashlib.sha1(), hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h1.update(c)
            h2.update(c)
    return h1.hexdigest(), h2.hexdigest()


def orig_url(u):
    """Fandom serves a WebP re-encode unless format=original is requested.
    Verified: 0bwc.png is 888 B image/webp without it, 26862 B image/png with it."""
    return u + ("&" if "?" in u else "?") + "format=original"


def safe(name):
    out = "".join(c if (c.isalnum() or c in "._-") else "_" for c in name)
    return out[:150] or "unnamed"


def main():
    imgs = json.loads(LIST.read_text(encoding="utf-8"))
    rows = {}
    if MAN.exists():
        rows = {r["path"]: r for r in json.loads(MAN.read_text(encoding="utf-8"))}
    OUT.mkdir(parents=True, exist_ok=True)

    for n, im in enumerate(imgs):
        fn = safe(im["name"])
        dest = OUT / fn
        rel = str(dest.relative_to(ROOT)).replace("\\", "/")
        if rel in rows and not rows[rel].get("failed"):
            continue
        if dest.exists() and dest.stat().st_size == im.get("size"):
            pass
        else:
            r = subprocess.run(
                ["curl", "-sSL", "--max-time", "90", "-o", str(dest),
                 "-A", "Mozilla/5.0 (corpus-recovery; research archival)",
                 "-w", "%{http_code}\t%{content_type}", orig_url(im["url"])],
                capture_output=True, text=True,
            )
            code, ctype = (r.stdout.strip().split("\t") + ["", ""])[:2]
        if not dest.exists():
            rows[rel] = {"path": rel, "source_url": im["url"], "failed": True,
                         "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        else:
            s1, s256 = sha_both(dest)
            rows[rel] = {
                "path": rel,
                "sha256": s256,
                "sha1": s1,
                "bytes": dest.stat().st_size,
                "source_url": im["url"],
                "http_status": locals().get("code", "cached"),
                "content_type": locals().get("ctype", im.get("mime")),
                "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "wiki_declared_sha1": im.get("sha1"),
                "sha1_matches_wiki": (s1 == im.get("sha1")),
                "wiki_declared_bytes": im.get("size"),
                "wiki_upload_timestamp_utc": im.get("timestamp"),
                "wiki_uploader": im.get("user"),
                "wiki_name": im["name"],
                "fetched_url": orig_url(im["url"]),
                "notes": "uncovering-cicada.fandom.com allimages API dump, fetched with format=original (without it Fandom returns a WebP re-encode); wiki is a community compilation, "
                         "not an original 3301 host. SHA-1 checked against the wiki's own declared digest.",
            }
        if n % 5 == 0 or n == len(imgs) - 1:
            MAN.write_text(json.dumps(list(rows.values()), indent=1), encoding="utf-8")
        # stdout on this box is cp1252; a non-ASCII wiki filename raises
        # UnicodeEncodeError and kills the whole run. Never print raw names.
        line = (f"{n+1}/{len(imgs)} {rows[rel].get('bytes',0):>9} "
                f"{'OK ' if rows[rel].get('sha1_matches_wiki') else 'CHK'} {fn}")
        print(line.encode("ascii", "backslashreplace").decode("ascii"), flush=True)

    MAN.write_text(json.dumps(list(rows.values()), indent=1), encoding="utf-8")
    ok = sum(1 for r in rows.values() if r.get("sha1_matches_wiki"))
    tot = sum(r.get("bytes", 0) for r in rows.values())
    print(f"DONE {len(rows)} files, {ok} sha1-verified, {tot} bytes")


if __name__ == "__main__":
    main()
