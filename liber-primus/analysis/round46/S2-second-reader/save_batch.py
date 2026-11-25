"""Save one batch of blind reads: python save_batch.py NN "S0100=M:H S0101=W:H ..."
Writes reads_batchNN.json, appends its sha256 to reads_frozen.sha256, rewrites heartbeat.txt. Opens no label file."""
import hashlib, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
nn = int(sys.argv[1]); toks = " ".join(sys.argv[2:]).split()
man = [m["id"] for m in json.load(open(os.path.join(HERE, "manifest.json"))) if m["batch"] == nn]
reads = {}
for t in toks:
    cid, v = t.split("="); r, c = v.split(":"); reads[cid] = {"read": r, "conf": c}
assert sorted(reads) == sorted(man), (set(man) ^ set(reads))
p = os.path.join(HERE, f"reads_batch{nn:02d}.json")
assert not os.path.exists(p), "batch already frozen"
ts = time.strftime("%Y-%m-%d %H:%M:%S")
json.dump({"batch": nn, "saved": ts, "reads": reads}, open(p, "w"), indent=1)
h = hashlib.sha256(open(p, "rb").read()).hexdigest()
open(os.path.join(HERE, "reads_frozen.sha256"), "a").write(f"{h}  reads_batch{nn:02d}.json  {ts}\n")
open(os.path.join(HERE, "heartbeat.txt"), "w").write(f"{ts} batch {nn:02d}/13 saved ({len(reads)} reads) sha {h[:12]}\n")
print("saved", p, len(reads), h[:12])
