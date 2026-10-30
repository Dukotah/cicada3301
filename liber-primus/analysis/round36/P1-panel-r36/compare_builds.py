import hashlib, json, os
L = os.path.dirname(os.path.abspath(__file__))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
res = {"protocol": "python build_r36.py build1 (PYTHONHASHSEED=1) and python build_r36.py build2 (PYTHONHASHSEED=2): separate processes, same parameters, same disk; hash seeds differ on purpose",
       "files": {}}
for f in sorted(os.listdir(os.path.join(L, "build1"))):
    a, b = sha(os.path.join(L, "build1", f)), sha(os.path.join(L, "build2", f))
    res["files"][f] = {"build1_sha256": a, "build2_sha256": b, "identical": a == b}
def norm(p):
    d = json.load(open(p)); d.pop("built"); d.pop("elapsed_s"); return d
res["out_build12_identical_except_wallclock_fields(built,elapsed_s)"] = norm(os.path.join(L, "build1/out_build12.json")) == norm(os.path.join(L, "build2/out_build12.json"))
res["arrays_identical"] = all(v["identical"] for k, v in res["files"].items() if k.endswith(".npz"))
res["panel_R36_sha256"] = res["files"]["panel12.npz"]["build1_sha256"]
res["testhalves_sha256"] = res["files"]["testhalves12.npz"]["build1_sha256"]
res["byte_identical"] = res["arrays_identical"] and res["out_build12_identical_except_wallclock_fields(built,elapsed_s)"]
res["first_attempt_note"] = ("The first pair of builds (default hash randomisation) was NOT identical: HEBREW test half and the LM/mu/sd/corr arrays differed. Root cause: I1 mappings_r36.hebrew_to_ascii iterates python sets of "
    "combining marks (PYTHONHASHSEED-dependent order) - 15 of 384,147 Hebrew clusters carry two vowel marks. Fixed in build_r36.py by sorting the marks (code-point order) at import time; I1's file is unmodified.")
json.dump(res, open(os.path.join(L, "build_twice.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "first_attempt_note"}, indent=1))
