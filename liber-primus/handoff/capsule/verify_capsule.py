"""verify_capsule.py — re-check every item in MANIFEST.json and report drift or death.

This is the capsule's watchdog. Run it whenever you arrive at this repo cold, and run it
again before you trust any number in it. It answers three questions per item:

  ALIVE?    for a gitignored/LOST item, is at least one recorded mirror still serving bytes?
  INTACT?   for a local file, does its SHA-256 still equal the manifest's?
  DRIFTED?  did a mirror serve DIFFERENT bytes than the manifest recorded?

DRIFTED is the dangerous one and the reason this file exists. A dead link is obvious;
a link that quietly starts serving a re-issued Gutenberg text or a re-rendered JPEG is
not, and it silently invalidates comparisons against every number in this repo.

Usage
-----
  python3 handoff/capsule/verify_capsule.py                 # local files only (fast, offline)
  python3 handoff/capsule/verify_capsule.py --net           # also probe mirrors (HEAD only)
  python3 handoff/capsule/verify_capsule.py --net --fetch   # download + hash fetchable items
  python3 handoff/capsule/verify_capsule.py --only images    # substring filter on item id
  python3 handoff/capsule/verify_capsule.py --limit 5 --net  # test a few, not all 101
  python3 handoff/capsule/verify_capsule.py --json report.json

Exit code 0 = no INTACT failures and no DRIFT. Non-zero = something changed; read the report.
Missing gitignored files are NOT a failure (they are expected absent in a fresh clone);
they are reported as ABSENT.

Stdlib only, so a bare Python 3 in 2027 can run it.
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MANIFEST = os.path.join(HERE, "MANIFEST.json")
UA = {"User-Agent": "cicada3301-capsule-verify/1.0"}
CHUNK = 1 << 20

OK, ABSENT, INTACT_FAIL, DRIFT, DEAD, SKIP = "OK", "ABSENT", "INTACT-FAIL", "DRIFT", "DEAD", "SKIP"


def sha256_file(path):
    h, n = hashlib.sha256(), 0
    with open(path, "rb") as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            n += len(b)
            h.update(b)
    return h.hexdigest(), n


def head(url, timeout):
    """Probe a URL without downloading. Returns (alive, detail)."""
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return True, f"HTTP {r.status} len={r.headers.get('Content-Length', '?')}"
    except urllib.error.HTTPError as e:
        # Some hosts (archive.org's in-ISO extractor, GitHub raw) reject HEAD but serve GET.
        if e.code in (403, 405, 501):
            try:
                req = urllib.request.Request(url, headers=dict(UA, Range="bytes=0-0"))
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return True, f"HTTP {r.status} (GET-range fallback)"
            except Exception as e2:
                return False, f"HEAD {e.code}, range-GET failed: {e2}"
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, repr(e)


def fetch_hash(url, timeout, cap):
    """Download and hash. cap = max bytes before giving up (0 = unlimited)."""
    h, n = hashlib.sha256(), 0
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        while True:
            b = r.read(CHUNK)
            if not b:
                break
            n += len(b)
            h.update(b)
            if cap and n > cap:
                raise RuntimeError(f"exceeded --max-bytes cap at {n} B")
    return h.hexdigest(), n


def check(it, args):
    """Return (status, detail) for one manifest item."""
    path, want = it.get("path"), it.get("sha256")

    # ---- pure-derived items: recompute is out of scope here; the manifest records how.
    if it.get("status") == "derived":
        return SKIP, "derived item — recompute via the 'derivation' field in the manifest"

    # ---- local file present: the INTACT check
    if path:
        ap = os.path.join(REPO, path)
        if os.path.exists(ap):
            got, n = sha256_file(ap)
            if want is None:
                return SKIP, f"no recorded sha256 to compare ({n} B on disk)"
            if got == want:
                return OK, f"sha256 intact ({n} B)"
            return INTACT_FAIL, f"sha256 CHANGED\n      manifest {want}\n      on disk  {got}"

    # ---- not on disk. Offline run: absence of a gitignored file is expected, not a failure.
    if not args.net:
        if it.get("status") == "LOST":
            return DEAD, "recorded LOST; re-run with --net to retry its mirrors"
        return ABSENT, "not on disk (expected for gitignored items; use --net to probe mirrors)"

    mirrors = it.get("mirrors") or []
    if not mirrors:
        return DEAD, "not on disk and NO mirror recorded — this item is unrecoverable"

    # ---- network: probe, and optionally fetch+hash
    notes = []
    for url in mirrors:
        if " " in url:                       # manifest annotates some URLs after a space
            url = url.split(" ", 1)[0]
        if not url.startswith("http"):
            continue
        alive, detail = head(url, args.timeout)
        if not alive:
            notes.append(f"dead: {url} — {detail}")
            continue
        if not args.fetch:
            return OK, f"mirror alive: {url} — {detail}"
        try:
            got, n = fetch_hash(url, args.timeout, args.max_bytes)
        except Exception as e:
            notes.append(f"fetch failed: {url} — {e}")
            continue
        if want is None:
            return SKIP, f"fetched {n} B from {url}; manifest has no sha256 to compare"
        if got == want:
            return OK, f"refetch byte-identical ({n} B) from {url}"
        notes.append(f"DRIFT: {url} served {n} B sha256 {got}")
    if any(s.startswith("DRIFT") for s in notes):
        return DRIFT, "\n      ".join(notes)
    return DEAD, "\n      ".join(notes) if notes else "no reachable mirror"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--net", action="store_true", help="probe mirrors for absent items")
    ap.add_argument("--fetch", action="store_true",
                    help="with --net, download and hash instead of just probing")
    ap.add_argument("--only", default="", help="substring filter on item id")
    ap.add_argument("--limit", type=int, default=0, help="check at most N items")
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--max-bytes", type=int, default=200 * 1024 * 1024,
                    help="abort a --fetch that exceeds this (default 200 MB; 0 = unlimited)")
    ap.add_argument("--json", default="", help="write the full report to this path")
    args = ap.parse_args()

    if not os.path.exists(MANIFEST):
        sys.exit(f"MANIFEST.json not found at {MANIFEST}\n"
                 f"Build it: python3 {os.path.join(HERE, 'build_manifest.py')}")
    man = json.load(open(MANIFEST, encoding="utf-8"))
    items = [it for it in man["items"] if args.only in it["id"]]
    if args.limit:
        items = items[:args.limit]

    print(f"capsule: {MANIFEST}")
    print(f"generated {man.get('generated_utc')}  schema {man.get('schema_version')}")
    print(f"checking {len(items)} of {len(man['items'])} items"
          f"{'  [--net]' if args.net else '  [offline]'}"
          f"{'  [--fetch]' if args.fetch else ''}\n")

    rows, tally = [], {}
    for it in items:
        st, detail = check(it, args)
        tally[st] = tally.get(st, 0) + 1
        rows.append({"id": it["id"], "status_manifest": it.get("status"),
                     "result": st, "detail": detail})
        if st != OK or args.only or args.limit:
            print(f"  [{st:11s}] {it['id']}\n      {detail}")

    print("\n" + "=" * 72)
    for k in sorted(tally):
        print(f"  {k:12s}: {tally[k]}")
    bad = tally.get(INTACT_FAIL, 0) + tally.get(DRIFT, 0)
    dead = tally.get(DEAD, 0)
    print("=" * 72)
    if bad:
        print(f"FAIL — {bad} item(s) changed bytes. Do NOT compare new results against this "
              f"repo's numbers until reconciled.")
    elif dead:
        print(f"WARNING — {dead} item(s) have no live source. The capsule is degrading; "
              f"mirror them somewhere durable now.")
    else:
        print("PASS — every checked item is intact / reachable.")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"manifest": MANIFEST, "tally": tally, "rows": rows}, f, indent=1)
        print(f"report -> {args.json}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
