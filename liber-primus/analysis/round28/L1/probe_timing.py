import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis/round11", "analysis/campaign18_skip",
          "analysis/round19/I1", "analysis/round19/I2",
          "analysis/round20/P3", "analysis/round20/HITFN"):
    q = os.path.join(LP, p)
    if q not in sys.path: sys.path.insert(0, q)
import lib_numchannel as nc, driftbeam as DB, adjudicate as AD

PAD = os.path.join(LP, "analysis", "round12", "A1", "pads", "DATA__560.00.iso-authoritative")
b = open(PAD, "rb").read(20000)
K = [x % 29 for x in b]
C = list(nc.unsolved())[:400]

for preset, bw in (("exact", 120), ("pair", 120), ("pair", 64)):
    t0 = time.time()
    n = 4
    for i in range(n):
        d = DB.beam_decode(C, K, sign=-1, o=i * 700, beam_w=bw, **DB.PRESETS[preset])
        a = AD.adjudicate(d["plain_idx"])
    dt = (time.time() - t0) / n
    print(f"{preset} bw={bw}: {dt:.3f}s/decode (incl adjudicate) pmax={a['pmax']:.2f}")
