#!/usr/bin/env python3
"""L6-archives — rescue Liber-Primus repos that are DEAD on GitHub from Software Heritage.

Software Heritage has 0 references anywhere in this repo (G1 novelty pass). It is the only
retrieval channel left for repos whose GitHub origin now 404s. This script walks
origin -> latest snapshot -> HEAD revision -> directory tree and downloads every text-ish
blob so the rune-novelty comparator can be run over them.

Writes ONLY into this lane's folder. Re-run safe.
    python3 pull_swh.py                 # the 7 dead-on-GitHub origins found 2026-08-12
    python3 pull_swh.py <origin-url>    # any other origin
"""
import json, os, subprocess, sys, time, urllib.parse

API = "https://archive.softwareheritage.org/api/1"
UA = {"User-Agent": "Mozilla/5.0 (research; liber-primus archive rescue)"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetched", "swh")
DEAD = [
    "https://github.com/Devenoh/liber-primus",
    "https://github.com/Hadyn/Liber-Primus-Runes-OCR",
    "https://github.com/HelixPiano/Rune-indices-Liber-Primus",
    "https://github.com/christj2/Liber-Primus-Decoder",
    "https://github.com/geraldsandoval/liber-primus",
    "https://github.com/hcbt/Liber-Primus-scripts",
    "https://github.com/lydiasamuel/liber-primus",
]
TEXTY = (".txt", ".md", ".py", ".json", ".csv", ".js", ".java", ".cs", ".c", ".cpp",
         ".rb", ".go", ".rs", ".html", ".yml", ".yaml", ".ipynb", "")


def api(path, tries=3):
    """urllib normalises the '//' inside SWH's origin-in-path URLs, so shell out to curl."""
    url = path if path.startswith("http") else API + path
    for i in range(tries):
        r = subprocess.run(["curl", "-sS", "--max-time", "90", "-A", UA["User-Agent"], url],
                           capture_output=True)
        try:
            return json.loads(r.stdout.decode("utf-8", "ignore"))
        except Exception:
            if i == tries - 1:
                print("   ERR", url[:100], r.stdout[:120])
                return None
            time.sleep(3 * (i + 1))


def raw(url, dest):
    r = subprocess.run(["curl", "-sS", "--max-time", "120", "-A", UA["User-Agent"],
                        "-o", dest, url], capture_output=True)
    return r.returncode == 0 and os.path.getsize(dest) >= 0


def walk(dir_id, prefix, dest, depth=0):
    if depth > 4:
        return
    entries = api(f"/directory/{dir_id}/") or []
    for e in entries:
        name = e["name"]
        if e["type"] == "dir":
            walk(e["target"], prefix + name + "/", dest, depth + 1)
        elif e["type"] == "file":
            ext = os.path.splitext(name)[1].lower()
            if ext not in TEXTY or (e.get("length") or 0) > 8_000_000:
                continue
            p = os.path.join(dest, (prefix + name).replace("/", "__"))
            if os.path.exists(p):
                continue
            if raw(e["target_url"] + "raw/", p):
                print(f"    ok {prefix}{name}")
            else:
                print(f"    FAIL {prefix}{name}")


for origin in (sys.argv[1:] or DEAD):
    slug = origin.rstrip("/").split("/")[-2] + "__" + origin.rstrip("/").split("/")[-1]
    dest = os.path.join(OUT, slug)
    os.makedirs(dest, exist_ok=True)
    print("==", origin)
    v = api("/origin/" + origin + "/visit/latest/")
    if not v or not v.get("snapshot"):
        print("   no snapshot in SWH")
        continue
    snap = api(f"/snapshot/{v['snapshot']}/")
    branches = (snap or {}).get("branches", {})
    rev = None
    for b in ("refs/heads/main", "refs/heads/master", "HEAD"):
        t = branches.get(b)
        while t and t.get("target_type") == "alias":
            t = branches.get(t["target"])
        if t and t.get("target_type") == "revision":
            rev = t["target"]
            break
    if rev is None:
        for t in branches.values():
            if t.get("target_type") == "revision":
                rev = t["target"]
                break
    if rev is None:
        print("   no revision")
        continue
    r = api(f"/revision/{rev}/")
    if not r:
        continue
    walk(r["directory"], "", dest)
print("done ->", OUT)
