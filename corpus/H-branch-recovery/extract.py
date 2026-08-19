"""Extract every file that exists on a branch but not in master, WITH provenance.

Deliberately an EXTRACTION, not a merge. The research/round-8..12 branches carry a
DIFFERENT Rounds 8-12 than master does (ICC parse / DQT / stylometry / external sweep vs
SEED / GEOMETRY / PAYLOAD / SKELETON / POINTERS). Merging naively would conflate two
research programmes under one numbering. So the content is recovered into the corpus with
a record of exactly where each file came from, and the merge decision is left to a human.
"""
import json, os, subprocess, hashlib, collections

BRANCHES = [
    "claude/cicada-3301-scope-cigxzi",
    "claude/master-roadmap-libra-qk527u",
    "research/round-8-artifact-provenance",
    "research/round-9-stylometry-exclusion",
    "research/round-10-exclusion-power-corrected",
    "research/round-11-dqt-matrix-disambiguation",
    "research/round-12-external-status-sweep",
]
OUT = "corpus/H-branch-recovery/recovered"
man = []
seen = {}

def sh(*a):
    return subprocess.run(a, capture_output=True)

for b in BRANCHES:
    ref = f"origin/{b}"
    files = sh("git", "diff", "--name-only", f"master...{ref}").stdout.decode(
        "utf-8", "replace").split("\n")
    tip = sh("git", "rev-parse", ref).stdout.decode().strip()
    for f in files:
        f = f.strip()
        if not f or os.path.exists(f):
            continue                      # already in the working tree
        blob = sh("git", "show", f"{ref}:{f}").stdout
        if not blob:
            continue
        h = hashlib.sha256(blob).hexdigest()
        if h in seen:                     # identical content across branches
            seen[h]["also_on_branches"].append(b)
            continue
        dest = os.path.join(OUT, b.replace("/", "_"), f)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").write(blob)
        rec = {"original_path": f, "recovered_to": dest.replace("\\", "/"),
               "sha256": h, "bytes": len(blob), "source_branch": b,
               "branch_tip_commit": tip, "also_on_branches": []}
        seen[h] = rec
        man.append(rec)

os.makedirs(OUT, exist_ok=True)
json.dump({"$comment": "Files present on unmerged branches and ABSENT from the master "
                       "working tree, extracted with provenance. Extraction, not merge: "
                       "the branch rounds 8-12 are different work from master's rounds "
                       "8-12 and merging naively would conflate two programmes.",
           "extracted_utc": subprocess.run(["date","-u","+%Y-%m-%dT%H:%M:%SZ"],
                                           capture_output=True,text=True).stdout.strip(),
           "n_files": len(man), "total_bytes": sum(r["bytes"] for r in man),
           "files": man},
          open("corpus/H-branch-recovery/RECOVERED.json", "w"), indent=1)
print(f"recovered {len(man)} unique files, {sum(r['bytes'] for r in man)/1e6:.2f} MB")
c = collections.Counter(r["source_branch"] for r in man)
for k, v in c.most_common():
    print(f"   {v:3d}  {k}")
