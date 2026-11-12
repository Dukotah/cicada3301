# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork H probe 4: same-stream coin idiom (coin_from_key, RANDOM%6) shaped like real page 0: no kept doublet in
[0,120), at least one kept doublet in [120,240).  Does keyskip2 clear the L=120 screen AND the L=240 gate bars
(sweep-scale bars of record ~10.5 at L=120, ~10.35 at L=240)?  Correct key handed over."""
import sys, random
sys.dont_write_bytecode = True
sys.path.insert(0, _ROOT+"/liber-primus")
import numpy as np
import verify_solution as VS
V, BR, pan = VS.load_instruments(quiet=True)
t = np.load(VS.PANEL_R36_TEST); EN = [int(v) for v in t["EN_MODERN"]]
N = 29
def enc(P, K):
    C = []; j = 0; prev = None; kept = []
    for i, p in enumerate(P):
        while True:
            c = (p + K[j]) % N
            if prev is not None and c == prev:
                if (K[j + 1] % 6) != 0: j += 2; continue
                j += 1; kept.append(i)
            break
        C.append(c); j += 1; prev = c
    return C, kept
got = []; s = 0; n = 0
while len(got) < 20 and n < 4000:
    n += 1
    P = EN[50000 + 257 * n: 50000 + 257 * n + 240]
    r = random.Random(900 + n); K = [r.randrange(N) for _ in range(2000)]
    C, kept = enc(P, K)
    if not kept or kept[0] < 120: continue
    row = {}
    for L in (120, 240):
        for rel, adv in (("keyskip2", 2), ("free", "free")):
            if rel == "free" and L == 240: continue
            d = V.beam_decode_v3(C[:L], K, adv, design="panel_max", sign=-1, o=0, beam_w=400)
            res = V.A.adjudicate(d["plain_idx"], pan=pan)
            row[(rel, L)] = (float(res["pmax"]), sum(1 for x, y in zip(d["plain_idx"], P[:L]) if x == y) / L)
    got.append((kept[0], row))
import statistics as st
for key in (("keyskip2", 120), ("keyskip2", 240), ("free", 120)):
    pm = [g[1][key][0] for g in got]; rc = [g[1][key][1] for g in got]
    print(key, "n=%d" % len(pm), "pmax min/median %.1f/%.1f" % (min(pm), st.median(pm)), "recovery median %.2f" % st.median(rc),
          "frac pmax>=10.5: %.2f" % (sum(1 for x in pm if x >= 10.5) / len(pm)))
print("first kept-doublet index in each plant:", [g[0] for g in got])
