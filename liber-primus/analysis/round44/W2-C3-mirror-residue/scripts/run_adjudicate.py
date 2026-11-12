"""W2-C3 step 5 — direct symbol-mapped reads of the remaining opaque streams,
adjudicated under panel-R36 against bar_v3(400, L, "free")  (PREREG §3-Q4, §5).

Streams: T2_2jpg, T3_folly, canon_256 (direct read-as-plaintext — in no ledger row;
pad/keystream legs R12-A1/R28/R44-P4 are different constructions and stay closed).
The Outt carrier is pure 15-byte-periodic -> degenerate by construction (mds<=6), and its
13-byte terminal residue is below the 120-symbol floor: both excluded, listed not_covered.
Maps: {mod29, 5bit-skip(>=29 dropped), pair-mod29} x {id, rev, xff} = 9 per stream.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.dirname(HERE)
LP = os.path.abspath(os.path.join(CELL, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))
sys.path.insert(0, os.path.join(LP, "analysis", "round34", "I1-v3-null"))
import residue_lib as R
from adjudicate import adjudicate, is_degenerate
from bars_v3 import bar_v3

N_CAP = 400
BARS = {120: bar_v3(N_CAP, 120, "free"), 240: bar_v3(N_CAP, 240, "free"),
        400: bar_v3(N_CAP, 400, "free"), 729: bar_v3(N_CAP, 729, "free")}
def node(n):
    return max((L for L in BARS if L <= n), default=None)

def m_mod29(b):   return [x % 29 for x in b]
def m_5bit(b):
    bits = "".join(f"{x:08b}" for x in b)
    out = []
    for i in range(0, len(bits) - 4, 5):
        v = int(bits[i:i + 5], 2)
        if v < 29:
            out.append(v)
    return out
def m_pair29(b):  return [(b[i] * 256 + b[i + 1]) % 29 for i in range(0, len(b) - 1, 2)]

MAPS = {"mod29": m_mod29, "5bit_skip": m_5bit, "pair_mod29": m_pair29}
PRE = {"id": R.t_id, "rev": R.t_rev, "xff": R.t_xff}

BLOBS = {
    "T2_2jpg": open(os.path.join(LP, "analysis/armada_osint/extracts/T2.bin"), "rb").read(),
    "T3_folly": open(os.path.join(LP, "analysis/armada_osint/artifacts/folly.bin"), "rb").read(),
    "canon_256": open(os.path.join(LP, "analysis/pp49_51/canon_256.bin"), "rb").read(),
}

rows, best = [], None
for bname, blob in BLOBS.items():
    for pname, pf in PRE.items():
        tb = pf(blob)
        for mname, mf in MAPS.items():
            idx = mf(tb)
            L = node(len(idx))
            if L is None:
                rows.append({"kid": f"{bname}|{pname}|{mname}", "n_symbols": len(idx),
                             "skipped": "below 120-symbol floor"})
                continue
            res = adjudicate(idx[:L])
            deg = is_degenerate(res["mds"], res["ioc"])
            row = {"kid": f"{bname}|{pname}|{mname}", "L": L, "n_symbols": len(idx),
                   "pmax": round(res["pmax"], 3), "preg": res["preg"],
                   "pmax_ne": round(res["pmax_ne"], 3), "en": round(res["en"], 4),
                   "ioc": round(res["ioc"], 4), "mds": res["mds"],
                   "h2": round(res["h2"], 4), "zl": round(res["zl"], 4),
                   "degenerate": bool(deg), "bar": round(BARS[L], 3),
                   "crosses": bool((not deg) and res["pmax"] >= BARS[L])}
            rows.append(row)
            if not deg and (best is None or row["pmax"] - row["bar"] > best["pmax"] - best["bar"]):
                best = row
            print(row["kid"], "L", L, "pmax", row["pmax"], "bar", row["bar"],
                  "deg", deg, "crosses", row["crosses"], flush=True)

n_dec = sum(1 for r in rows if "pmax" in r)
out = {"N_decodes": n_dec, "N_CAP": N_CAP, "bars": {k: round(v, 3) for k, v in BARS.items()},
       "best_non_degenerate": best, "crossers": [r for r in rows if r.get("crosses")],
       "rows": rows}
json.dump(out, open(os.path.join(CELL, "results", "adjudication.json"), "w"), indent=1)
print("N =", n_dec, "crossers:", len(out["crossers"]), "best:", best)
