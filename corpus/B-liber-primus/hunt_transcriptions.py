#!/usr/bin/env python3
"""Hunt candidate Liber Primus transcriptions in public repos and DIFF them
rune-for-rune against this repository's canonical stream.

For each repo: list the default-branch tree via the GitHub API, download every
blob that plausibly holds runes, keep the ones that actually do, and report
  - how many Gematria Primus runes it holds
  - whether its rune string is a contiguous match, a subsequence match, or
    DIVERGES from canon, and where.

Writes corpus/B-liber-primus/hunt_results.json and saves every fetched file
under corpus/B-liber-primus/fetched/<owner>__<repo>/<path>.

Usage: python corpus/B-liber-primus/hunt_transcriptions.py owner/repo [owner/repo ...]
"""
import os
import sys
import json
import time
import hashlib
import datetime
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "liber-primus", "src"))
from lp import gematria as gp   # noqa: E402

FETCHED = os.path.join(HERE, "fetched")
RESULTS = os.path.join(HERE, "hunt_results.json")
MAX_BLOBS = int(os.environ.get("HUNT_MAX_BLOBS", "45"))

# Codepoint variants seen in the wild for the same Gematria Primus glyph.
CODEPOINT_ALIASES = {
    "ᛂ": "ᛄ",   # RUNIC LETTER E used where canon uses GER (J, index 11)
    "ᛣ": "ᛞ",   # RUNIC LETTER DAEG variant -> D
    "ᚡ": "ᚠ",   # RUNIC LETTER V/F variant  -> F
}
SKIP_EXT = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".zip", ".pdf", ".pyc",
            ".ttf", ".otf", ".woff", ".woff2", ".ico", ".mp3", ".wav", ".exe")


def canon_stream():
    txt = open(os.path.join(ROOT, "liber-primus", "data", "krisyotam_runes.txt"),
               encoding="utf-8").read()
    return "".join(c for c in txt if c in gp.RUNE_TO_IDX)


def normalise(text):
    return "".join(CODEPOINT_ALIASES.get(c, c) for c in text)


def runes_of(text):
    return "".join(c for c in normalise(text) if c in gp.RUNE_TO_IDX)


def get(url, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": "cicada3301-corpus-sweep"})
    with urllib.request.urlopen(req, timeout=60) as r:
        b = r.read()
    return b if raw else json.loads(b.decode("utf-8"))


def compare(cand, canon):
    """Classify a candidate rune string against canon."""
    if not cand:
        return {"relation": "no-runes"}
    if cand == canon:
        return {"relation": "identical-to-canon", "n": len(cand)}
    at = canon.find(cand)
    if at >= 0:
        return {"relation": "exact-substring-of-canon", "n": len(cand), "offset": at}
    at = cand.find(canon)
    if at >= 0:
        return {"relation": "canon-is-substring-of-candidate", "n": len(cand), "offset": at}
    # aligned prefix diff
    diffs = [(i, a, b) for i, (a, b) in enumerate(zip(cand, canon)) if a != b]
    return {
        "relation": "DIVERGES",
        "n": len(cand),
        "n_canon": len(canon),
        "first_divergence_index": diffs[0][0] if diffs else None,
        "n_aligned_divergences": len(diffs),
        "sample": [{"index": i, "candidate": a, "candidate_cp": "U+%04X" % ord(a),
                    "canon": b, "canon_cp": "U+%04X" % ord(b)} for i, a, b in diffs[:20]],
    }


def scan_repo(full_name, canon):
    owner, repo = full_name.split("/")
    out = {"repo": full_name, "files": []}
    try:
        meta = get("https://api.github.com/repos/%s" % full_name)
    except Exception as e:
        out["error"] = "repo meta: %s" % e
        return out
    out["created_at"] = meta.get("created_at")
    out["pushed_at"] = meta.get("pushed_at")
    out["description"] = meta.get("description")
    out["fork"] = meta.get("fork")
    out["default_branch"] = meta.get("default_branch")
    try:
        tree = get("https://api.github.com/repos/%s/git/trees/%s?recursive=1"
                   % (full_name, meta.get("default_branch", "master")))
    except Exception as e:
        out["error"] = "tree: %s" % e
        return out
    blobs = [t for t in tree.get("tree", [])
             if t["type"] == "blob"
             and not t["path"].lower().endswith(SKIP_EXT)
             and t.get("size", 0) > 200
             and t.get("size", 0) < 6_000_000]
    # cheap prefilter: text-ish extensions only, biggest first (transcriptions
    # are large text blobs), capped so one sprawling repo cannot eat the budget
    TEXTY = (".txt", ".rne", ".md", ".json", ".csv", ".dat", ".text", ".rst",
             ".py", ".js", ".ts", ".go", ".rs", ".java", ".cs", ".c", ".cpp",
             ".html", ".htm", ".xml", ".yml", ".yaml", ".lp", ".utf8", "")
    blobs = [t for t in blobs if os.path.splitext(t["path"])[1].lower() in TEXTY]
    blobs.sort(key=lambda t: -t.get("size", 0))
    blobs = blobs[:MAX_BLOBS]
    out["n_blobs_considered"] = len(blobs)
    for t in blobs:
        url = "https://raw.githubusercontent.com/%s/%s/%s" % (full_name, out["default_branch"], t["path"])
        try:
            raw = get(url, raw=True)
        except Exception:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        r = runes_of(text)
        if len(r) < 100:
            continue
        d = os.path.join(FETCHED, "%s__%s" % (owner, repo), os.path.dirname(t["path"]))
        os.makedirs(d, exist_ok=True)
        local = os.path.join(d, os.path.basename(t["path"]))
        with open(local, "wb") as f:
            f.write(raw)
        rec = {
            "path": t["path"],
            "source_url": url,
            "local": os.path.relpath(local, ROOT).replace("\\", "/"),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "n_runes": len(r),
            "sha256_of_normalised_rune_string": hashlib.sha256(r.encode("utf-8")).hexdigest(),
            "used_codepoint_aliases": sorted({c for c in text if c in CODEPOINT_ALIASES}),
        }
        rec.update(compare(r, canon))
        out["files"].append(rec)
        print("     + %s (%d runes)" % (t["path"], len(r)), flush=True)
        time.sleep(0.1)
    return out


def main():
    os.makedirs(FETCHED, exist_ok=True)
    canon = canon_stream()
    repos = sys.argv[1:]
    prev = {}
    if os.path.exists(RESULTS):
        prev = {r["repo"]: r for r in json.load(open(RESULTS, encoding="utf-8"))["repos"]}
    for name in repos:
        print("scanning %s ..." % name, flush=True)
        res = scan_repo(name, canon)
        prev[name] = res
        for f in res.get("files", []):
            print("   %-52s %6d runes  %s" % (f["path"][:52], f["n_runes"], f["relation"]))
        if res.get("error"):
            print("   ERROR %s" % res["error"])
        # checkpoint after every repo so a kill never loses work
        with open(RESULTS, "w", encoding="utf-8") as fh:
            json.dump({"generated_utc": datetime.datetime.now(datetime.timezone.utc)
                       .isoformat(timespec="seconds"),
                       "canon_n_runes": len(canon),
                       "canon_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
                       "codepoint_aliases_normalised": CODEPOINT_ALIASES,
                       "repos": list(prev.values())}, fh, ensure_ascii=False, indent=1)
    print("wrote %s" % RESULTS)


if __name__ == "__main__":
    main()
