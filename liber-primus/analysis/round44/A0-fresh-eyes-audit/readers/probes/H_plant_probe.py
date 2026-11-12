# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork H probe: feed the instrument of record (verify_solution.judge_register = beam_v3 panel_max + panel-R36 + bars_v3)
ciphertexts made by an INDEPENDENT encipherer under house-style variants the sweeps never represent.
Correct key is handed over.  Read-only use of the repo (no bytecode written)."""
import sys, os, random, json, time
sys.dont_write_bytecode = True
LP = _ROOT+"/liber-primus"
sys.path.insert(0, LP)
import numpy as np
import verify_solution as VS
VS.load_instruments(quiet=True)
N = 29
t = np.load(VS.PANEL_R36_TEST)
EN = [int(v) for v in t["EN_MODERN"]]
L = 120

def key(n, seed):
    r = random.Random(seed); return [r.randrange(N) for _ in range(n)]

def enc(P, K, mode="plain", a=0, supp=0.83, seed=5, hold_first_F_after=None, hold_all_F=False, burn_at=None, coin_from_key=False):
    """Independent forward encipherer. Returns (C, info)."""
    rng = random.Random(seed); C = []; j = 0; prev = None; holds = []; burns = 0
    for i, p in enumerate(P):
        if burn_at and i in burn_at:
            j += 1; burns += 1
        if p == 0 and (hold_all_F or (hold_first_F_after is not None and i >= hold_first_F_after and not holds)):
            C.append(0); holds.append(i); prev = 0            # literal F: no key consumed
            continue
        while True:
            k = K[j]
            if mode == "plain":     c = (p + k + a) % N
            elif mode == "beaufort": c = (k - p + a) % N
            elif mode == "atbash_add": c = ((N - 1 - p) + k + a) % N
            else: raise ValueError(mode)
            if prev is not None and c == prev:
                if coin_from_key:
                    coin_reject = (K[j + 1] % 6) != 0          # RANDOM % 6 style coin from the same stream
                    if coin_reject: j += 2; continue
                    j += 1                                      # coin consumed, doublet kept
                elif rng.random() < supp:
                    j += 1; continue
            break
        C.append(c); j += 1; prev = c
    return C, {"holds": holds, "burns": burns}

def rec(dec, P):
    return sum(1 for x, y in zip(dec, P) if x == y) / len(P)

def run(name, **kw):
    pages, truth, infos = [], [], []
    for s in range(3):                                           # 3 independent windows
        P = EN[20000 + 997 * s: 20000 + 997 * s + L]
        K = key(8 * L, 1000 + s)
        C, info = enc(P, K, seed=50 + s, **kw)
        pages.append((C, K, P)); infos.append(info)
    out = {}
    for rel in ("keyskip1", "keyskip2", "free"):
        pm, rc, cl = [], [], []
        for (C, K, P) in pages:
            rows = VS.judge_register(K, [C], relations=(rel,))
            r = rows[0]
            pm.append(round(r["pmax"], 2)); rc.append(round(rec(r["plain_idx"], P), 2)); cl.append(bool(r["clears"]))
        out[rel] = {"pmax": pm, "recovery": rc, "clears_bar": cl, "bar": round(rows[0]["bar"], 2)}
    print(json.dumps({"construction": name, "info": infos, **out}))
    sys.stdout.flush()

t0 = time.time()
run("baseline keyskip1 (control)")
run("constant offset a=+1 (C=P+K+1)", a=1)
run("beaufort (C=K-P)", mode="beaufort")
run("atbash then add (C=(28-P)+K)", mode="atbash_add")
run("one literal-F key hold (first plaintext F at index>=5)", hold_first_F_after=5)
run("all plaintext F literal (solved-page convention)", hold_all_F=True)
import random as _r
g = _r.Random(7); pos = set(); i = 0
while i < L:
    i += max(1, int(g.expovariate(1 / 4.3))); pos.add(i)
run("key burned at every word boundary (~1 per 4.3 runes)", burn_at=pos)
run("coin_from_key RANDOM%6 (reject burns 2; kept doublet burns 1)", coin_from_key=True)
print("elapsed %.0fs" % (time.time() - t0))
