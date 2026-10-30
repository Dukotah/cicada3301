import sys, json, math
sys.dont_write_bytecode = True
import sweep as S
from c1lib import *
import itertools
jobs = []
for it in S.u1_items():
    if it["stratum"] != "R": continue
    for rel, sign, off in itertools.product(RELS, (-1, 1), range(8)):
        jobs.append({"sub": "U1", "cell": "sha256ctr|%s|UP" % it["cid"], "route": "sha256ctr", "cid": it["cid"], "form": "UP", "text": it["forms"][0][1], "rel": rel, "sign": sign, "o": off, "page": None})
assert len(jobs) == 1312, len(jobs)
S.wait_mem()
Nnew = {r: 4416 + 656 for r in RELS}
trig = {r: bar_v3(Nnew[r], 120, r) for r in RELS}
out = open(S.ROWS, "a"); gate = open(S.GATEF, "a"); best = {}; gates = 0
for j in jobs:
    plain, a = S.run_job(j, 120); out.write(json.dumps(AD.to_row(a, S.kid(j))) + "\n")
    pm = float(a["pmax"]); b = best.get(j["rel"])
    if b is None or pm > b["pmax"]: best[j["rel"]] = {"pmax": round(pm, 3), "kid": S.kid(j), "preg": PAN.registers[a["preg"]]}
    if pm >= trig[j["rel"]]:
        pl, a2 = S.run_job(j, 240); gates += 1
        gate.write(json.dumps({"kid": S.kid(j), "pmax120": pm, "pmax240": float(a2["pmax"]), "bar240": bar_v3(Nnew[j["rel"]], 240, j["rel"])}) + "\n")
out.close(); gate.close()
res = {"decodes": len(jobs), "gate_runs": gates, "best": best, "bar_v3_actualN_5072": {r: round(trig[r], 3) for r in RELS},
       "bar_v3_N1e6": {r: round(bar_v3(1e6, 120, r), 3) for r in RELS}, "bar12_actualN": {r: round(S.bar12(5072, 120, r), 3) for r in RELS}}
try: AD.validate_store(S.ROWS); res["validate_store"] = "ok"
except Exception as ex: res["validate_store"] = "FAIL %s" % ex
sys.path.insert(0, AN("handoff")); import validate_ledger as VL
res["check_r3_store"] = VL.check_r3_store(S.ROWS)
res["rows_total"] = sum(1 for _ in open(S.ROWS)) - 1
json.dump(res, open("addendum_summary.json", "w"), indent=1); print(json.dumps(res, indent=1))
