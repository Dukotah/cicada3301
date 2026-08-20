#!/usr/bin/env python3
"""Hard gates on corpus/B-liber-primus/PAGES.json. Exits non-zero on any failure.

Run:  PYTHONIOENCODING=utf-8 python corpus/B-liber-primus/validate_pages.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PIN = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"

fails = []


def gate(name, got, want):
    ok = got == want
    print("  %-58s %-12s %s" % (name, "OK" if ok else "FAIL", got if ok else "%r != %r" % (got, want)))
    if not ok:
        fails.append(name)


d = json.load(open(os.path.join(HERE, "PAGES.json"), encoding="utf-8"))
P = d["pages"]
print("PAGES.json gates")
gate("page records", len(P), 58)
gate("total LP2 runes", sum(p["n_runes"] for p in P), 13136)

# The 12,956 unsolved figure is stated in SEGMENT coordinates (krisyotam segments
# 0-54). In LP2 PAGE coordinates that is pages 0-55, because page 50 carries no
# runes at all and so consumes no segment. Both forms are gated.
seg = [p for p in P if p.get("segment_index") is not None and p["segment_index"] <= 54]
gate("unsolved runes, segments 0-54", sum(p["n_runes"] for p in seg), 12956)
gate("unsolved runes, pages 0-55", sum(p["n_runes"] for p in P if p["page_index"] <= 55), 12956)
gate("page 50 is runeless", P[50]["n_runes"], 0)
gate("krisyotam segments used", len({p["segment_index"] for p in P
                                     if p.get("segment_index") is not None}), 57)

idx = []
for p in seg:
    idx.extend(p["rune_indices"])
gate("SHA-256 of comma-joined unsolved indices == PROBLEM.json pin",
     hashlib.sha256(",".join(map(str, idx)).encode()).hexdigest(), PIN)

gate("solved LP2 pages", sorted(p["page_index"] for p in P if p.get("status") == "solved"), [56, 57])
gate("LP1 solved page records", len(d["lp1_solved_pages"]), 5)

nimg = [p for p in P if p.get("image_file")]
gate("images attached", len(nimg), 56)
bad = []
for p in nimg:
    b = open(os.path.join(ROOT, p["image_file"]), "rb").read()
    if hashlib.sha1(b).hexdigest() != p["image_sha1"]:
        bad.append(p["page_index"])
gate("image SHA-1 re-verified on disk", bad, [])
gate("images flagged as matching archived onion7 dump",
     sum(1 for p in nimg if p["image_sha1_matches_archived_onion7_dump"]), 56)

bad = [p["page_index"] for p in P
       if p["runes"] and hashlib.sha256(p["runes"].encode("utf-8")).hexdigest()
       != p["sha256_of_rune_string"]]
gate("per-page rune-string SHA-256 self-consistent", bad, [])
gate("every runic page rune-identical to its krisyotam segment",
     [p["page_index"] for p in P if p["n_runes"] and not p["matches_krisyotam_segment"]], [])

print("")
if fails:
    print("FAILED: %s" % ", ".join(fails))
    sys.exit(1)
print("ALL GATES PASS")
