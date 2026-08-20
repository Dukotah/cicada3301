#!/usr/bin/env python3
"""Scan corpus/E-tooling/vendor/* and emit:
  - vendor_scan.json : per-repo git identity, size, languages, license text guess,
                       readme excerpt, and every file containing >=200 futhorc runes
                       with its rune count + canonical index SHA-256.
Run repeatedly; it is idempotent and cheap.
"""
import os, sys, json, hashlib, subprocess, datetime

E = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(E, "vendor")

GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
IDX = {r: i for i, r in enumerate(GP)}
# Codepoint aliases seen in the wild: some transcriptions encode GP index 11 (J)
# as U+16C2 RUNIC LETTER E rather than U+16C4 RUNIC LETTER GER. Same glyph slot,
# different codepoint -- an ENCODING variant, not a reading difference.
IDX["ᛂ"] = 11
RUNE_LO, RUNE_HI = 0x16A0, 0x16F8

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "target", "build", "dist", ".idea"}
TEXT_EXT = {".txt", ".md", ".json", ".py", ".js", ".ts", ".go", ".c", ".h", ".cpp", ".cs",
            ".dart", ".rs", ".java", ".php", ".rb", ".pl", ".zig", ".html", ".csv", ".yml",
            ".yaml", ".toml", ".ipynb", ".tsv", ".jsx", ".sh", ".lp", ".dat", ""}


def git(repo, *args):
    try:
        return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                              text=True, timeout=25).stdout.strip()
    except Exception:
        return ""


def rune_digest(text):
    idx = [IDX[c] for c in text if c in IDX]
    if not idx:
        return 0, None
    s = ",".join(str(i) for i in idx)
    return len(idx), hashlib.sha256(s.encode()).hexdigest()


def raw_rune_count(text):
    return sum(1 for c in text if RUNE_LO <= ord(c) <= RUNE_HI)


def scan_repo(path):
    name = os.path.basename(path)
    head = git(path, "rev-parse", "HEAD")
    rec = {
        "dir": name,
        "clone_sha": head or None,
        "valid_clone": bool(head),
        "remote": git(path, "config", "--get", "remote.origin.url") or None,
        "last_commit_date": git(path, "log", "-1", "--format=%cI") or None,
        "first_commit_date": git(path, "log", "--reverse", "--format=%cI", "--max-count=1") or None,
        "n_commits": None,
        "shallow": os.path.exists(os.path.join(path, ".git", "shallow")),
        "license_files": [],
        "readme_files": [],
        "rune_files": [],
        "n_files": 0,
        "bytes": 0,
        "ext_counts": {},
    }
    c = git(path, "rev-list", "--count", "HEAD")
    if c.isdigit():
        rec["n_commits"] = int(c)

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, path).replace("\\", "/")
            try:
                sz = os.path.getsize(fp)
            except OSError:
                continue
            rec["n_files"] += 1
            rec["bytes"] += sz
            ext = os.path.splitext(f)[1].lower()
            rec["ext_counts"][ext] = rec["ext_counts"].get(ext, 0) + 1
            lf = f.lower()
            if lf.startswith("licen") or lf.startswith("copying") or lf.startswith("unlicen"):
                rec["license_files"].append(rel)
            if lf.startswith("readme"):
                rec["readme_files"].append(rel)
            # rune scan
            if ext not in TEXT_EXT or sz > 8_000_000:
                continue
            try:
                t = open(fp, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            n_raw = raw_rune_count(t)
            if n_raw < 200:
                continue
            n, h = rune_digest(t)
            rec["rune_files"].append({
                "path": rel, "bytes": sz,
                "n_runes_gp29": n, "n_runes_raw_block": n_raw,
                "sha256_indices": h,
                "file_sha256": hashlib.sha256(open(fp, "rb").read()).hexdigest(),
            })
    rec["rune_files"].sort(key=lambda r: -r["n_runes_gp29"])
    return rec


def main():
    out = {"generated_utc": datetime.datetime.now(datetime.timezone.utc)
           .strftime("%Y-%m-%dT%H:%M:%SZ"), "repos": []}
    if not os.path.isdir(V):
        print("no vendor dir"); return
    for d in sorted(os.listdir(V)):
        p = os.path.join(V, d)
        if not os.path.isdir(p):
            continue
        try:
            out["repos"].append(scan_repo(p))
        except Exception as e:
            out["repos"].append({"dir": d, "error": str(e), "valid_clone": False})
    with open(os.path.join(E, "vendor_scan.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    ok = sum(1 for r in out["repos"] if r.get("valid_clone"))
    bad = [r["dir"] for r in out["repos"] if not r.get("valid_clone")]
    withr = sum(1 for r in out["repos"] if r.get("rune_files"))
    print(f"repos={len(out['repos'])} valid={ok} with_rune_files={withr}")
    if bad:
        print("BROKEN:", " ".join(bad))


if __name__ == "__main__":
    main()
