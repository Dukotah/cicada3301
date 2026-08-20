#!/usr/bin/env python3
"""Mechanical facts for TOOLS.json: clone sha, dates, licence, language, rune files."""
import os, re, json, hashlib, subprocess, datetime, collections

E = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(E, "vendor")
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
IDX = {r: i for i, r in enumerate(GP)}
IDX["ᛂ"] = 11  # codepoint alias for J seen in the wild
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "target",
             "dist", "build", ".idea", ".mypy_cache", ".pytest_cache"}
LANG_EXT = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".go": "Go",
            ".java": "Java", ".c": "C", ".cc": "C++", ".cpp": "C++", ".cu": "CUDA",
            ".rs": "Rust", ".cs": "C#", ".rb": "Ruby", ".zig": "Zig", ".jl": "Julia",
            ".php": "PHP", ".kt": "Kotlin", ".hs": "Haskell", ".pl": "Perl",
            ".lua": "Lua", ".m": "MATLAB/ObjC", ".R": "R", ".r": "R", ".sh": "Shell",
            ".html": "HTML", ".ipynb": "Jupyter"}
LIC_PAT = [
    ("MIT", re.compile(r"\bMIT License\b|Permission is hereby granted, free of charge", re.I)),
    ("Apache-2.0", re.compile(r"Apache License\s*\n?\s*Version 2\.0", re.I)),
    ("GPL-3.0", re.compile(r"GNU GENERAL PUBLIC LICENSE\s*\n?\s*Version 3", re.I)),
    ("GPL-2.0", re.compile(r"GNU GENERAL PUBLIC LICENSE\s*\n?\s*Version 2", re.I)),
    ("AGPL-3.0", re.compile(r"GNU AFFERO GENERAL PUBLIC LICENSE\s*\n?\s*Version 3", re.I)),
    ("LGPL", re.compile(r"GNU LESSER GENERAL PUBLIC LICENSE", re.I)),
    ("BSD-3-Clause", re.compile(r"Redistributions of source code must retain.*Neither the name", re.S | re.I)),
    ("BSD-2-Clause", re.compile(r"Redistributions of source code must retain", re.I)),
    ("Unlicense", re.compile(r"This is free and unencumbered software released into the public domain", re.I)),
    ("MPL-2.0", re.compile(r"Mozilla Public License Version 2\.0", re.I)),
    ("CC0-1.0", re.compile(r"CC0 1\.0 Universal", re.I)),
    ("WTFPL", re.compile(r"DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE", re.I)),
    ("ISC", re.compile(r"ISC License", re.I)),
]

def git(g, *a):
    try:
        return subprocess.run(["git", "--git-dir", g] + list(a), capture_output=True,
                              text=True, encoding="utf-8", timeout=40).stdout.strip()
    except Exception:
        return ""

def main():
    out = {}
    for d in sorted(os.listdir(V)):
        p = os.path.join(V, d)
        if not os.path.isdir(p) or d == "c":
            continue
        g = os.path.join(p, ".git")
        rec = {"dir": d, "clone_sha": None, "remote": None, "first_commit_date": None,
               "last_commit_date": None, "n_commits": None, "authors": [],
               "license": "NOT-STATED", "license_files": [], "language": None,
               "ext_counts": {}, "n_files": 0, "bytes": 0, "readme_head": None,
               "rune_files": []}
        if os.path.isdir(g):
            rec["clone_sha"] = git(g, "rev-parse", "HEAD") or None
            rec["remote"] = git(g, "config", "--get", "remote.origin.url") or None
            rec["last_commit_date"] = git(g, "log", "-1", "--format=%cI") or None
            fl = git(g, "log", "--reverse", "--format=%cI")
            rec["first_commit_date"] = fl.split("\n")[0] if fl else None
            n = git(g, "rev-list", "--count", "HEAD")
            rec["n_commits"] = int(n) if n.isdigit() else None
            rec["shallow"] = os.path.exists(os.path.join(g, "shallow"))
            au = git(g, "log", "--format=%ae")
            rec["authors"] = sorted(set(x for x in au.split("\n") if x))[:12]
        ext = collections.Counter()
        for dp, dns, fns in os.walk(p):
            dns[:] = [x for x in dns if x not in SKIP_DIRS]
            for fn in fns:
                f = os.path.join(dp, fn)
                rel = os.path.relpath(f, p).replace("\\", "/")
                try:
                    sz = os.path.getsize(f)
                except OSError:
                    continue
                rec["n_files"] += 1
                rec["bytes"] += sz
                e = os.path.splitext(fn)[1]
                ext[e] += 1
                low = fn.lower()
                if low.startswith(("licence", "license", "copying", "unlicense")) and sz < 200000:
                    try:
                        t = open(f, encoding="utf-8", errors="ignore").read()
                    except Exception:
                        continue
                    name = "UNRECOGNISED"
                    for nm, pat in LIC_PAT:
                        if pat.search(t):
                            name = nm
                            break
                    rec["license_files"].append({"path": rel, "detected": name})
                    if rec["license"] == "NOT-STATED":
                        rec["license"] = name
                if low.startswith("readme") and rec["readme_head"] is None and sz < 400000:
                    try:
                        rec["readme_head"] = open(f, encoding="utf-8", errors="ignore"
                                                  ).read()[:700]
                    except Exception:
                        pass
                if sz > 40_000_000 or e in (".png", ".jpg", ".jpeg", ".gif", ".zip",
                                            ".pdf", ".bmp", ".pgp", ".gz", ".exe"):
                    continue
                try:
                    t = open(f, encoding="utf-8", errors="ignore").read()
                except Exception:
                    continue
                r = [IDX[c] for c in t if c in IDX]
                if len(r) >= 1000:
                    rec["rune_files"].append({
                        "path": rel, "bytes": sz, "n_runes": len(r),
                        "file_sha256": hashlib.sha256(open(f, "rb").read()).hexdigest(),
                        "sha256_indices": hashlib.sha256(
                            ",".join(map(str, r)).encode()).hexdigest()})
        rec["ext_counts"] = dict(ext.most_common(12))
        langs = collections.Counter()
        for e, n in ext.items():
            if e in LANG_EXT:
                langs[LANG_EXT[e]] += n
        rec["language"] = langs.most_common(1)[0][0] if langs else None
        rec["languages"] = dict(langs.most_common(4))
        rec["rune_files"].sort(key=lambda x: -x["n_runes"])
        rec["rune_files"] = rec["rune_files"][:12]
        out[d] = rec
        print(f"{d[:50]:50s} sha={(rec['clone_sha'] or '')[:8]:8s} "
              f"lic={rec['license'][:12]:12s} lang={str(rec['language'])[:10]:10s} "
              f"runefiles={len(rec['rune_files'])}")
    json.dump({"generated_utc": datetime.datetime.now(datetime.timezone.utc)
               .strftime("%Y-%m-%dT%H:%M:%SZ"), "repos": out},
              open(os.path.join(E, "tools_facts.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
