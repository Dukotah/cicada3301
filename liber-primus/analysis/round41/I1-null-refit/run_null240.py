"""R41 I1 L=240 phase: decode the FIRST survivors (draw order) lacking an L=240 row at U[:240], both relations.  python run_null240.py [wall_cap_s] [target_total]"""
from i1lib import *
CAP = float(sys.argv[1]) if len(sys.argv) > 1 else 1500; TARGET = int(sys.argv[2]) if len(sys.argv) > 2 else 5200
OUT = F("null_stream240.jsonl")
have = {(r["fam"], r["seed"]) for r in map(json.loads, open(F("null_stream.jsonl"))) if "keyskip1_240" in r}
if os.path.exists(OUT): have |= {(r["fam"], r["seed"]) for r in map(json.loads, open(OUT))}
todo = [(r["fam"], r["seed"]) for r in map(json.loads, open(F("null_stream.jsonl"))) if (r["fam"], r["seed"]) not in have]
log("L240 phase: have", len(have), "todo", len(todo)); wait_mem(); t0 = time.time(); out = open(OUT, "a"); n = 0
for fam, seed in todo:
    if len(have) + n >= TARGET or time.time() - t0 > CAP: break
    K = ks_full(fam, seed); row = {"fam": fam, "seed": seed}
    for r in RELS:
        d, a = v3dec(U[:240], K, r); row[r + "_240"] = [round(float(a["pmax"]), 4), int(a["preg"]), int(a["mds"]), round(float(a["ioc"]), 4)]
    out.write(json.dumps(row) + "\n"); n += 1
    if n % 200 == 0: out.flush(); log("L240", len(have) + n, "%.0fs" % (time.time() - t0))
out.flush(); log("L240 done", len(have) + n)
