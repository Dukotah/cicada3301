"""Save one batch of blind strip reads.
Usage: python save_batch.py NN "T2-s01=A:H,AE|A:M,?:L" "T2-s02=..."
Each strip read = comma-separated tokens rune:conf, left to right. Writes reads_batchNN.json, appends its sha256 to
reads_frozen.sha256, rewrites heartbeat.txt. Opens no label file (reads manifest.json only)."""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OK = set("F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA ?".split())
nn = int(sys.argv[1])
man = [m["id"] for m in json.load(open(os.path.join(HERE, "manifest.json"))) if m["batch"] == nn]
nb = max(m["batch"] for m in json.load(open(os.path.join(HERE, "manifest.json"))))
reads = {}
for arg in sys.argv[2:]:
    cid, v = arg.split("=")
    toks = []
    for t in v.split(","):
        r, c = t.split(":")
        assert all(a in OK for a in r.split("|")), t
        assert c in ("H", "M", "L"), t
        toks.append({"read": r, "conf": c})
    reads[cid] = toks
assert sorted(reads) == sorted(man), (set(man) ^ set(reads))
p = os.path.join(HERE, f"reads_batch{nn:02d}.json")
assert not os.path.exists(p), "batch already frozen"
ts = time.strftime("%Y-%m-%d %H:%M:%S")
json.dump({"batch": nn, "saved": ts, "reads": reads}, open(p, "w"), indent=1)
h = hashlib.sha256(open(p, "rb").read()).hexdigest()
open(os.path.join(HERE, "reads_frozen.sha256"), "a").write(f"{h}  reads_batch{nn:02d}.json  {ts}\n")
open(os.path.join(HERE, "heartbeat.txt"), "w").write(
    f"{ts} batch {nn:02d}/{nb:02d} saved ({len(reads)} strips, {sum(map(len, reads.values()))} tokens) sha {h[:12]}\n")
print("saved", p, len(reads), h[:12])
