# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork H probe 3: does THE ORACLE (verify_solution.judge_register + decide) pass a CORRECT key when the
keystream is CONTINUOUS across pages (the project's own generative model) rather than restarting per page?"""
import sys, random
sys.dont_write_bytecode = True
sys.path.insert(0, _ROOT+"/liber-primus")
import numpy as np
import verify_solution as VS
VS.load_instruments(quiet=True)
t = np.load(VS.PANEL_R36_TEST); EN = [int(v) for v in t["EN_MODERN"]]
N = 29
LENS = [262, 266, 201, 217, 261, 263]          # the real first six LP2 page lengths
P = EN[40000:40000 + sum(LENS)]
r = random.Random(2026); K = [r.randrange(N) for _ in range(13500)]
def enc_stream(P, K, supp=0.83, seed=11, reset_at=()):
    rng = random.Random(seed); C = []; j = 0; prev = None
    for i, p in enumerate(P):
        if i in reset_at: j = 0
        while True:
            c = (p + K[j]) % N
            if prev is not None and c == prev and rng.random() < supp: j += 1; continue
            break
        C.append(c); j += 1; prev = c
    return C
def pages_of(C):
    out = []; s = 0
    for L in LENS: out.append(C[s:s + L]); s += L
    return out
for name, reset in (("CONTINUOUS keystream across pages (project's generative model)", ()),
                    ("key RESTARTS at each page (what the oracle selftest plants)", set(np.cumsum([0] + LENS[:-1]).tolist()))):
    C = enc_stream(P, K, reset_at=reset)
    rows = VS.judge_register(K, pages_of(C))
    ok, rel, per = VS.decide(rows)
    print(name)
    for rr in ("keyskip1", "keyskip2", "free"):
        print("   %-8s pages clearing: %d/%d   pmax by page: %s" % (rr, per[rr]["clearing"], per[rr]["tested"],
              [round(x["pmax"], 1) for x in rows if x["relation"] == rr]))
    print("   ORACLE VERDICT:", "PASS" if ok else "FAIL")
