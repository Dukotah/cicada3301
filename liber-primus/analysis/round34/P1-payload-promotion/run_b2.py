#!/usr/bin/env python3
"""R34-P1 reader R30-B2 (RSA/GPG structural), canon legs only. Original b2_rsa_gpg.py source exec'd with
path/shim substitutions only. folly.bin and 2.jpg are absent (gitignored): those legs are NOT re-runnable."""
import os, sys, json, tempfile, shutil, time
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "R30-B2")
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "shim"))
GH = os.path.join(OUT, "gh"); os.makedirs(GH, exist_ok=True); os.environ["GNUPGHOME"] = "gh"; os.chdir(OUT)
src = open(os.path.join(LP, "analysis", "round30", "B2-rsa-gpg", "b2_rsa_gpg.py"), encoding="utf-8").read()
subs = [
 ('ROOT = Path("/mnt/c/Users/dukot/projects/cicada3301/liber-primus")', 'ROOT = Path(r"%s")' % LP),
 ('WORK.mkdir(parents=True, exist_ok=True)', 'pass'),
 ('CANON = ROOT / "analysis/pp49_51/canon_256.bin"', 'CANON = Path(CANON_PATH)'),
 ('folly = FOLLY.read_bytes()', 'folly = b""'),
 ('jpg = JPG.read_bytes()', 'jpg = b""'),
 ('                from Crypto.Util import Counter\n                ctr = Counter.new(128, initial_value=0)\n                c = AES.new(key, AES.MODE_CTR, counter=ctr)', '                c = AES.new(key, AES.MODE_CTR)'),
 ('(LANE / "b2_results.json").write_text(json.dumps(results, indent=2))\nprint(json.dumps(results, indent=2))', 'pass'),
]
for a, b in subs:
    assert a in src, a[:60]
    src = src.replace(a, b)
out = {}
for tag in ("canon", "resolved"):
    t0 = time.time()
    ns = {"__name__": "b2", "CANON_PATH": os.path.join(HERE, "inputs", tag, "canon_256.bin")}
    exec(compile(src, "b2_rsa_gpg.py[%s]" % tag, "exec"), ns)
    out[tag] = ns["results"]; print(tag, "done %.0fs" % (time.time() - t0), flush=True)
shutil.rmtree(GH, ignore_errors=True)
json.dump(out, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=str)
st = json.load(open(os.path.join(LP, "analysis", "round30", "B2-rsa-gpg", "b2_results.json")))
def view(r):
    t = r["tests"]
    return {"mod": t["canon_as_modulus"], "gcd": t["gcd_canon_cicadaN"], "res": t["canon_as_residue_mod_cicadaN"], "pgp": t["openpgp_scan"]["canon_256"],
            "gpg_raw": t["gpg_raw"]["canon_256"], "prep": t["gpg_header_prepend"]["canon_256"], "aes": t["canon_as_aes256_key"]["over_canon_self"]}
cmp = {"stored_vs_canon_rerun": {k: view(st)[k] == view(out["canon"])[k] for k in view(st)},
       "canon_vs_resolved": {k: view(out["canon"])[k] == view(out["resolved"])[k] for k in view(st)},
       "controls_canon": out["canon"]["controls"], "controls_resolved_equal": out["canon"]["controls"].get("pos_real_rsa2048_modulus") == out["resolved"]["controls"].get("pos_real_rsa2048_modulus")}
json.dump(cmp, open(os.path.join(OUT, "compare.json"), "w"), indent=1, default=str)
print(json.dumps(cmp, indent=1, default=str)[:3000])
