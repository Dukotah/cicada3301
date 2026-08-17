#!/usr/bin/env python3
"""L6-archives — rune-novelty comparator + its pre-registered controls.

Builds the held rune corpus (every file in the repo carrying >200 Elder/Anglo-Saxon
futhorc codepoints), then asks of any candidate text: does it contain a run of >=MIN
runes that does NOT appear as a substring of anything already held?

Controls (pre-registered in PREREG.md, both must pass or no novelty claim is admissible):
  C1  held canonical stream  -> MUST report 0 novel runs
  C2  shuffled canonical     -> MUST report >0 novel runs (comparator not saturating)

Usage:
    python3 rune_novelty.py                 # controls only
    python3 rune_novelty.py FILE [FILE...]  # controls + candidates
"""
import os, re, sys, random, hashlib

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
RUNE = re.compile(r"[ᚠ-᛿]+")
MIN = 8
SELF = os.path.abspath(__file__)
LANE = os.path.dirname(SELF)


def load_held():
    streams, files = [], []
    for root, dirs, fs in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
        if os.path.abspath(root).startswith(LANE):
            continue  # never let this lane's own downloads count as "held"
        for f in fs:
            p = os.path.join(root, f)
            try:
                if os.path.getsize(p) > 20_000_000:
                    continue
                t = open(p, "rb").read().decode("utf-8")
            except Exception:
                continue
            runs = RUNE.findall(t)
            n = sum(len(r) for r in runs)
            if n > 200:
                streams.append("|".join(runs))
                files.append((n, os.path.relpath(p, REPO)))
    return streams, files


def novel_runs(text, streams):
    out = []
    for r in RUNE.findall(text):
        if len(r) < MIN:
            continue
        if not any(r in s for s in streams):
            out.append(r)
    return out


def report(label, text, streams):
    nov = novel_runs(text, streams)
    tot = sum(len(r) for r in RUNE.findall(text))
    print(f"  {label:42s} runes={tot:7d}  novel_runs={len(nov):5d}  "
          f"novel_runes={sum(len(r) for r in nov):6d}")
    for r in nov[:5]:
        print(f"      {hashlib.sha256(r.encode()).hexdigest()[:16]}  len={len(r)}  cp={[hex(ord(c)) for c in r[:8]]}")
    return nov


if __name__ == "__main__":
    streams, files = load_held()
    print(f"HELD CORPUS: {len(files)} files, {sum(n for n, _ in files)} runes")
    canon = open(os.path.join(REPO, "liber-primus", "data", "krisyotam_runes.txt"),
                 encoding="utf-8").read()

    print("\nCONTROLS")
    c1 = report("C1 held canonical (must be 0)", canon, streams)
    chars = [c for c in canon if RUNE.match(c)]
    random.seed(3301)
    random.shuffle(chars)
    c2 = report("C2 shuffled canonical (must be >0)", "".join(chars), streams)
    ok = (len(c1) == 0) and (len(c2) > 0)
    print(f"  CONTROLS {'PASS' if ok else 'FAIL'}")
    if not ok:
        sys.exit("comparator broken - no novelty claim admissible")

    if len(sys.argv) > 1:
        print("\nCANDIDATES")
        for p in sys.argv[1:]:
            try:
                t = open(p, "rb").read().decode("utf-8", errors="ignore")
            except Exception as e:
                print(f"  {p}: unreadable ({e})")
                continue
            report(os.path.basename(p), t, streams)
