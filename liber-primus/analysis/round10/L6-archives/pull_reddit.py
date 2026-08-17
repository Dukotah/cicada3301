#!/usr/bin/env python3
"""L6-archives — resumable Reddit-archive puller (arctic-shift / Pushshift mirror).

Fixes the bug in analysis/round10/RECON-C/fetch_recon_c.sh, which paginated with
`after=0`; the API rejects that ("'after' must be a valid date"), so that script
recorded 0 rows and the corpus was mis-scored as empty. Start at after=1 instead.

Writes ONLY into this lane's folder. Re-run safe (skips complete files).
    python3 pull_reddit.py
"""
import json, os, sys, time, urllib.request, urllib.error

API = "https://arctic-shift.photon-reddit.com/api"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetched", "reddit")
os.makedirs(OUT, exist_ok=True)

SUBS = ["a2e7j6ic78h0j", "Cicada", "cicada3301"]
KINDS = ["posts", "comments"]


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            if i == tries - 1:
                print("   ERR", e, file=sys.stderr)
                return None
            time.sleep(2 * (i + 1))
    return None


for sub in SUBS:
    for kind in KINDS:
        path = os.path.join(OUT, f"{sub}_{kind}.jsonl")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print("skip ", os.path.basename(path))
            continue
        after, total, seen = 1000000000, 0, set()
        with open(path, "w", encoding="utf-8") as fh:
            while True:
                d = get(f"{API}/{kind}/search?subreddit={sub}&limit=100&sort=asc&after={after}")
                rows = (d or {}).get("data") or []
                fresh = [r for r in rows if r.get("id") not in seen]
                if not fresh:
                    break
                for r in fresh:
                    seen.add(r.get("id"))
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                total += len(fresh)
                nxt = int(rows[-1]["created_utc"])
                after = nxt + 1 if nxt <= after else nxt
                if len(rows) < 100:
                    break
        print(f"ok    {os.path.basename(path)}  ({total} rows)")
print("done ->", OUT)
