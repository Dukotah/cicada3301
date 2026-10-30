"""P1: inventory every corpus input of panel-R36 -> inputs_r36.json.   `python make_inputs.py --check` re-verifies the disk against it."""
import hashlib, json, os, sys, platform
import numpy as np
LANE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(LANE, "..", "..", ".."))
I1 = os.path.join(LANE, "..", "I1-new-registers")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
J = lambda p: json.load(open(p, encoding="utf-8"))
OUT = os.path.join(LANE, "inputs_r36.json")
if "--check" in sys.argv:
    d = J(OUT); bad = 0
    for e in d["inputs"]:
        p = os.path.join(LP, e["path"])
        ok = os.path.exists(p) and sha(p) == e["sha256"] and os.path.getsize(p) == e["bytes"]
        if not ok: bad += 1; print("MISMATCH", e["path"])
    print(len(d["inputs"]) - bad, "/", len(d["inputs"]), "inputs match"); sys.exit(1 if bad else 0)

b1 = J(os.path.join(LANE, "build1", "out_build12.json"))
r32 = J(os.path.join(LP, "analysis/round32/I2-multiregister-readjudication/out_build.json"))["corpora"]
r19 = J(os.path.join(LP, "analysis/round19/I2/out_build.json"))["corpora"]
flog = {(e["register_dir"], e["file"]): e for e in J(os.path.join(I1, "fetch_log.json"))["files"] if e.get("status") == "ok"}
vf = {i["what"]: i for i in J(os.path.join(LANE, "verify_fetch.json"))["items"]}
norm = lambda p: p.replace("\\", "/")
HOW = {
 "data/kjv.txt": ("python data/fetch_sources.py --r19", "https://www.gutenberg.org/files/10/10-0.txt", "Round 19 original, byte-exact (sha-verified by fetch_sources)"),
 "data/keys/mabinogion.txt": ("python data/fetch_sources.py --r19", "https://www.gutenberg.org/files/5160/5160-0.txt", "Round 19 original, byte-exact (sha-verified by fetch_sources)"),
 "data/keys/welsh/welsh_mabinogion.txt": ("SUBSTITUTE - copy analysis/round36/P1-panel-r36/inputs_frozen/welsh_mabinogion.txt (fetch_sources.py --welsh does NOT reproduce it: re-fetch gives sha da02fef6.., 761,024 B)",
     "gutenberg.org/cache/epub/{3680,57981,56275,67424}/pg*.txt, boilerplate-stripped (Round 32 recipe)", "Round 32 substitute (NOT the Round 19 'diplomatic edition', sha 4b3fd926.., lost)"),
}
inputs = {}
for reg, files in b1["corpora"].items():
    for f in files:
        path = norm(f["path"]); full = os.path.join(LP, path)
        e = inputs.setdefault(path, {"path": path, "sha256": sha(full), "bytes": os.path.getsize(full), "used_by": []})
        assert e["sha256"] == f["sha256"] and e["bytes"] == f["bytes"], path          # same bytes the build hashed
        e["used_by"].append(reg)
for path, e in inputs.items():
    r32m = [x for fs in r32.values() for x in fs if norm(x["path"]) == path]
    r19m = [x for fs in r19.values() for x in fs if norm(x["path"]) == path]
    e["r32_sha256"] = r32m[0]["sha256"] if r32m else None
    e["r19_sha256"] = r19m[0]["sha256"] if r19m else None
    e["matches_round32"] = (r32m[0]["sha256"] == e["sha256"]) if r32m else "n/a (new in Round 36)"
    e["matches_round19"] = (r19m[0]["sha256"] == e["sha256"]) if r19m else "n/a (new in Round 36)"
    if path in HOW:
        e["how_obtained"], e["url"], e["status"] = HOW[path]
    elif path.startswith("analysis/round36/I1-new-registers/corpora/"):
        parts = path.split("/"); rd, fn = parts[-2], parts[-1]
        fl = flog[(rd, fn)]; assert fl["sha256"] == e["sha256"]
        e["how_obtained"] = "python analysis/round36/I1-new-registers/fetch_r36.py (URL below; logged in I1 fetch_log.json)"
        e["url"] = fl["url"]; e["status"] = "new in Round 36 (I1); re-fetched by P1 on 2026-10-30: " + ("identical" if vf[rd + "/" + fn]["match"] else "DIFFERENT")
    else:
        e["how_obtained"] = "in the repo (tracked file)"; e["url"] = None
        e["status"] = "in-repo, hash identical to Round 32/Round 19 record" if e["matches_round32"] is True else "in-repo"
    e["refetch_verified"] = (None if False else None) or (vf.get(rd + "/" + fn, vf.get(path, {})).get("match") if path.startswith("analysis/round36/I1") else
                             vf.get(path, vf.get("CY welsh substitute (fetch_sources --welsh)" if "welsh" in path else path, {})).get("match"))
for e in inputs.values():
    if e["refetch_verified"] is None: e["refetch_verified"] = "n/a (tracked in repo)"
lst = sorted(inputs.values(), key=lambda e: (e["used_by"][0], e["path"]))
code = {}
for rel in ("analysis/round36/I1-new-registers/build_models_r36.py", "analysis/round36/I1-new-registers/mappings_r36.py", "analysis/round10b/B6-non-english-plaintext/detectors.py", "benchmark/plant.py",
            "analysis/campaign18_skip/skipdecode.py", "analysis/round32/I2-multiregister-readjudication/adjudicate.py",
            "analysis/round32/I2-multiregister-readjudication/power.py", "analysis/round36/I1-new-registers/run_gate.py",
            "analysis/round36/P1-panel-r36/build_r36.py", "data/fetch_sources.py"):
    p = os.path.join(LP, rel)
    code[rel] = sha(p) if os.path.exists(p) else "NOT FOUND"
out = {"panel": "panel-R36", "registers": b1["registers"], "inputs": lst,
       "summary": {"n_inputs": len(lst),
                   "n_registers_inputs": {r: len(v) for r, v in b1["corpora"].items()},
                   "match_round32": sorted(e["path"] for e in lst if e["matches_round32"] is True),
                   "differ_from_round32": sorted(e["path"] for e in lst if e["matches_round32"] is False),
                   "new_in_round36": sorted(e["path"] for e in lst if str(e["matches_round32"]).startswith("n/a"))[:3] + ["... (%d files)" % sum(1 for e in lst if str(e["matches_round32"]).startswith("n/a"))]},
       "code_sha256": code, "environment": {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform()},
       "build_params": {"mode": "--nine=rebuild", "lambdas": b1["null"] and [0.70, 0.20, 0.09, 0.01], "null_draws_per_length": b1["null"]["draws_per_length"],
                        "null_seed": b1["null"]["seed"], "len_grid": b1["null"]["len_grid"], "mapping_variant": b1["mapping_variant"]}}
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(out["summary"], indent=1)); print(len(lst), "inputs")
for e in lst:
    if "round36/I1" not in e["path"]: print(e["used_by"], e["path"], e["sha256"][:10], e["bytes"], "R32:", e["matches_round32"], "R19:", e["matches_round19"])
