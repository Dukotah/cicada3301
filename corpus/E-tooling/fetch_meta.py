#!/usr/bin/env python3
"""Fetch GitHub metadata (stars, license, language, dates, forks, archived) for every
vendored repo, via `gh api`. Writes repo_meta.json. Logs 403/429 rate-limit hits.
Idempotent: keeps already-fetched entries unless --force.
"""
import os, json, subprocess, datetime, sys

E = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(E, "vendor")
OUT = os.path.join(E, "repo_meta.json")

def remote_of(d):
    p = os.path.join(V, d)
    if not os.path.isdir(os.path.join(p, ".git")):
        return None
    try:
        r = subprocess.run(["git", "--git-dir", os.path.join(p, ".git"),
                            "config", "--get", "remote.origin.url"],
                           capture_output=True, text=True, timeout=20).stdout.strip()
        return r or None
    except Exception:
        return None

def slug(url):
    if not url: return None
    u = url.rstrip("/")
    if u.endswith(".git"): u = u[:-4]
    if "github.com" not in u: return None
    return "/".join(u.split("github.com")[-1].lstrip(":/").split("/")[:2])

def main():
    force = "--force" in sys.argv
    meta = {}
    if os.path.exists(OUT):
        meta = json.load(open(OUT, encoding="utf-8"))
    rate_hits = meta.get("_rate_limit_events", [])
    for d in sorted(os.listdir(V)):
        if not os.path.isdir(os.path.join(V, d)):
            continue
        if d in meta and not force:
            continue
        url = remote_of(d)
        s = slug(url)
        rec = {"dir": d, "remote": url, "slug": s}
        if s:
            r = subprocess.run(["gh", "api", f"repos/{s}"], capture_output=True,
                               text=True, timeout=60)
            if r.returncode == 0:
                try:
                    j = json.loads(r.stdout)
                    rec.update({
                        "stars": j.get("stargazers_count"),
                        "forks": j.get("forks_count"),
                        "language": j.get("language"),
                        "license": (j.get("license") or {}).get("spdx_id"),
                        "license_name": (j.get("license") or {}).get("name"),
                        "created_at": j.get("created_at"),
                        "pushed_at": j.get("pushed_at"),
                        "archived": j.get("archived"),
                        "fork": j.get("fork"),
                        "parent": ((j.get("parent") or {}).get("full_name")),
                        "description": j.get("description"),
                        "size_kb": j.get("size"),
                        "open_issues": j.get("open_issues_count"),
                        "topics": j.get("topics"),
                    })
                except Exception as e:
                    rec["api_error"] = str(e)
            else:
                err = (r.stderr or "")[:300]
                rec["api_error"] = err
                if "429" in err or "rate limit" in err.lower() or "403" in err:
                    rate_hits.append({"slug": s, "when":
                        datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "err": err})
        meta[d] = rec
        meta["_rate_limit_events"] = rate_hits
        json.dump(meta, open(OUT, "w", encoding="utf-8"), indent=1)
    n = sum(1 for k, v in meta.items() if not k.startswith("_"))
    ok = sum(1 for k, v in meta.items() if not k.startswith("_") and v.get("stars") is not None)
    print(f"meta entries={n} with_api={ok} rate_limit_events={len(rate_hits)}")

if __name__ == "__main__":
    main()
