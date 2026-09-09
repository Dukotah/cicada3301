#!/usr/bin/env python3
"""R28-R T3: empirical test of L3's i386-subsumption claim.

Claim under test (L3 PREREG "pinned semantics"): every i386 Py2.7 string seed
collapses to ONE word w in [0,2^32) and its keystream == the integer-seed
keystream for w — hence the i386 string image is subsumed by R27-S1/S2's
[0,2^32) sweeps for {random29, offset 0}.

Parts:
  CONTROL  wrong-word plant (w+1) must produce a DIFFERENT stream (comparator
           sensitivity), run before anything is trusted.
  A        >=100 dictionary strings + forced negative-hash-32 strings + edges:
           keystream(s, wordsize=32) ==? keystream(int w32) over 2,000 draws.
  B        >=60 strings (>=30 with negative 64-bit hash) vs the REAL amd64
           CPython 2.7.18 binary: hash parity + 2,000-draw stream parity, and
           the abs-vs-unsigned-cast discrimination (if CPython used abs, the
           negative-hash rows would mismatch).
Output: work/t3_results.json; exit 1 on any FOUND-ERROR.
"""
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
G3 = os.path.normpath(os.path.join(HERE, "..", "..", "round19", "G3"))
sys.path.insert(0, G3)
import gen_py27 as G  # noqa: E402

PY27 = "/home/dukotah/py27/root2718/usr/bin/python2.7"
DICT = os.path.normpath(os.path.join(HERE, "..", "L3", "dictionary.jsonl"))
NDRAWS = 2000
MASK32 = (1 << 32) - 1
MASK64 = (1 << 64) - 1

out = {"draws_per_case": NDRAWS, "errors": []}


def ks_str(s, wordsize, n=NDRAWS):
    return G.keystream(s, "random29", n, wordsize=wordsize)


def ks_int(w, n=NDRAWS):
    return G.keystream(w, "random29", n)


# ---------- load sample: first 100 dict strings by tier order + hunt negatives
strings = []
with open(DICT) as f:
    for i, line in enumerate(f):
        r = json.loads(line)
        strings.append(r["s"])
        if i >= 20000:
            break
sample = strings[:100]
neg32 = [s for s in strings if G.py2_str_hash(s.encode("latin-1"), 32) < 0][:30]
neg64 = [s for s in strings if G.py2_str_hash(s.encode("latin-1"), 64) < 0][:30]
pos64 = [s for s in strings if G.py2_str_hash(s.encode("latin-1"), 64) >= 0][:30]
edges = ["", "a", " ", "\x00", "CICADA3301", "3301"]
part_a_set = list(dict.fromkeys(sample + neg32 + edges))  # dedupe, keep order
out["n_part_a"] = len(part_a_set)
out["n_neg32_in_sample"] = sum(
    1 for s in part_a_set if G.py2_str_hash(s.encode("latin-1"), 32) < 0)

# ---------- CONTROL: comparator must catch a planted wrong word
s0 = "THE PRIMES ARE SACRED"
w0 = G.py2_str_hash(s0.encode("latin-1"), 32) & MASK32
ctrl_same = ks_str(s0, 32) == ks_int(w0)
ctrl_diff = ks_str(s0, 32) == ks_int((w0 + 1) & MASK32)
out["control"] = {"string": s0, "w32": w0,
                  "true_word_matches": ctrl_same,
                  "planted_wrong_word_matches": ctrl_diff,
                  "control_ok": ctrl_same and not ctrl_diff}
if not out["control"]["control_ok"]:
    out["errors"].append("CONTROL FAILED: comparator cannot distinguish words")
    print(json.dumps(out, indent=1))
    sys.exit(1)

# ---------- Part A: i386 identity, string path vs integer path
a_fail = []
for s in part_a_set:
    h = G.py2_str_hash(s.encode("latin-1"), 32)
    w = h & MASK32
    if not (0 <= w < 2 ** 32):
        a_fail.append({"s": s, "reason": "word outside [0,2^32)", "w": w})
        continue
    if ks_str(s, 32) != ks_int(w):
        a_fail.append({"s": s, "reason": "keystream mismatch", "h32": h, "w": w})
out["part_a"] = {"n": len(part_a_set), "n_fail": len(a_fail), "fails": a_fail}
if a_fail:
    out["errors"].append("PART A: %d i386 identity failures" % len(a_fail))

# ---------- Part B: vs the real amd64 CPython 2.7.18
b_set = list(dict.fromkeys(neg64 + pos64 + edges))
py2_prog = r'''
import json, random, sys
strings = json.load(sys.stdin)
res = []
for s in strings:
    s2 = s.encode("latin-1")
    h = hash(s2)
    random.seed(s2)
    ks = [int(random.random()*29) for _ in range(%d)]
    res.append({"h": h, "ks": ks})
print json.dumps(res)
''' % NDRAWS
p = subprocess.run([PY27, "-c", py2_prog], input=json.dumps(b_set),
                   capture_output=True, text=True)
if p.returncode != 0:
    out["errors"].append("py2.7 subprocess failed: " + p.stderr[-500:])
    print(json.dumps(out, indent=1))
    sys.exit(1)
real = json.loads(p.stdout)

b_fail, abs_discrim = [], {"n_neg64": 0, "abs_would_differ": 0}
for s, r in zip(b_set, real):
    h_ref = G.py2_str_hash(s.encode("latin-1"), 64)
    if h_ref != r["h"]:
        b_fail.append({"s": s, "reason": "hash mismatch",
                       "ours": h_ref, "real": r["h"]})
        continue
    if ks_str(s, 64) != r["ks"]:
        b_fail.append({"s": s, "reason": "stream mismatch vs real 2.7.18"})
        continue
    if h_ref < 0:
        abs_discrim["n_neg64"] += 1
        # if CPython used abs(hash) the real stream would equal ks_int(abs(h));
        # show it does NOT (i.e. the unsigned cast is the true semantics)
        if ks_int(abs(h_ref)) != r["ks"]:
            abs_discrim["abs_would_differ"] += 1
out["part_b"] = {"n": len(b_set), "n_fail": len(b_fail), "fails": b_fail,
                 "abs_vs_cast": abs_discrim}
if b_fail:
    out["errors"].append("PART B: %d mismatches vs real 2.7.18" % len(b_fail))
if abs_discrim["n_neg64"] and \
        abs_discrim["abs_would_differ"] != abs_discrim["n_neg64"]:
    out["errors"].append(
        "PART B: abs()-hypothesis indistinguishable on some rows "
        "(%(abs_would_differ)d/%(n_neg64)d)" % abs_discrim)

out["verdict"] = "NO-ERROR-FOUND" if not out["errors"] else "FOUND-ERROR"
json.dump(out, open(os.path.join(HERE, "work", "t3_results.json"), "w"),
          indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "part_a"}, indent=1)[:2500])
print("part_a n=%d n_fail=%d" % (out["part_a"]["n"], out["part_a"]["n_fail"]))
print("VERDICT:", out["verdict"])
sys.exit(0 if not out["errors"] else 1)
