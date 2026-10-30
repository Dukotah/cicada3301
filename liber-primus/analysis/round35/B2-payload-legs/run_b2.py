#!/usr/bin/env python3
"""R35-B2 leg R30-B2 FULL (folly + 2.jpg + canon). Original b2_rsa_gpg.py exec'd; substitutions only: paths, shim CTR line,
result write suppressed. Controls live at the end of the original script (inside each run)."""
import os, sys, json, shutil
LANE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(LANE, "..", "..", ".."))
OUT = os.path.join(LANE, "R30-B2"); os.makedirs(OUT, exist_ok=True); os.chdir(OUT)
sys.path.insert(0, os.path.join(LANE, "shim"))
os.makedirs("gh", exist_ok=True); os.environ["GNUPGHOME"] = "gh"
src = open(os.path.join(LP, "analysis", "round30", "B2-rsa-gpg", "b2_rsa_gpg.py"), encoding="utf-8").read()
subs = [
 ('ROOT = Path("/mnt/c/Users/dukot/projects/cicada3301/liber-primus")', 'ROOT = Path(r"%s")' % LP),
 ('WORK.mkdir(parents=True, exist_ok=True)', 'pass'),
 ('CANON = ROOT / "analysis/pp49_51/canon_256.bin"', 'CANON = Path(CANON_PATH)'),
 ('FOLLY = ROOT / "analysis/armada_osint/artifacts/folly.bin"', 'FOLLY = Path(r"%s")' % os.path.join(LANE, "inputs", "folly", "folly.bin")),
 ('JPG   = ROOT / "analysis/armada_osint/artifacts/2.jpg"', 'JPG = Path(r"%s")' % os.path.join(LANE, "inputs", "jpg", "2.jpg")),
 ('                from Crypto.Util import Counter\n                ctr = Counter.new(128, initial_value=0)\n                c = AES.new(key, AES.MODE_CTR, counter=ctr)', '                c = AES.new(key, AES.MODE_CTR)'),
 ('(LANE / "b2_results.json").write_text(json.dumps(results, indent=2))\nprint(json.dumps(results, indent=2))', 'pass'),
]
for a, b in subs:
    assert a in src, a[:60]; src = src.replace(a, b)
out = {}
for tag in ("superseded", "promoted"):
    ns = {"__name__": "b2", "CANON_PATH": os.path.join(LANE, "inputs", tag, "canon_256.bin")}
    exec(compile(src, "b2_rsa_gpg.py[%s]" % tag, "exec"), ns)
    out[tag] = ns["results"]; os.makedirs(tag, exist_ok=True)
    json.dump(ns["results"], open(os.path.join(tag, "results.json"), "w"), indent=1, default=str); print(tag, "done", flush=True)
shutil.rmtree("gh", ignore_errors=True)
st = json.load(open(os.path.join(LP, "analysis", "round30", "B2-rsa-gpg", "b2_results.json")))
def eq(a, b): return json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
T = lambda r: r["tests"]
legs = ["jpg_trailer_len", "canon_as_modulus", "gcd_canon_cicadaN", "canon_as_residue_mod_cicadaN", "openpgp_scan", "gpg_raw", "gpg_header_prepend", "canon_as_aes256_key"]
cmp = {"comparator_vs_stored": {k: eq(T(st)[k], T(out["superseded"])[k]) for k in legs},
       "promoted_vs_comparator": {k: eq(T(out["superseded"])[k], T(out["promoted"])[k]) for k in legs},
       "controls": {k: out["superseded"]["controls"][k] for k in out["superseded"]["controls"]},
       "controls_equal_promoted": eq(out["superseded"]["controls"], out["promoted"]["controls"]),
       "controls_equal_stored": eq(st["controls"], out["superseded"]["controls"])}
json.dump(cmp, open("compare.json", "w"), indent=1, default=str); print(json.dumps(cmp, indent=1, default=str)[:3500])
