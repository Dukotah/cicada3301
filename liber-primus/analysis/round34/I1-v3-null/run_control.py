"""Round 34 / I1 positive-control plants (correct key, offset 0). Streams to control_plants.jsonl. python run_control.py"""
import sys
from common34 import *
REGS9 = list(PAN.registers)
CELLS = [(L, rel, enc, adv) for L in (31, 120, 240, 400) for (rel, enc, adv) in (("keyskip1", "keyskip1", 1), ("keyskip2", "skip_by_two", 2))] + [(120, "free", "free_q05", "free")]
F = open(OUT("control_plants.jsonl"), "a")
T0 = time.time()
for (L, rel, enc, adv) in CELLS:
    K = B2.sha_ctr_key(L * 12 + 2048)
    for reg in REGS9:
        a = TEST[reg].astype(np.int64)
        for s in range(20):
            r = random.Random(9000 + s)
            st = r.randrange(0, len(a) - L - 1)
            P = a[st:st + L].tolist()
            C, info = B2.ENCIPHER[enc](P, K, 0.83, 3301 + s)
            d = V.beam_decode_v3(C, K, adv, "panel_max", tau=0.0, lam_u=4.0)
            x = d["plain_idx"]
            pm = float(AD.adjudicate_batch(np.asarray([x], dtype=np.int64))["pmax"][0])
            F.write(json.dumps({"L": L, "rel": rel, "register": reg, "seed": s, "pmax": round(pm, 4), "rec": round(float(B2.recovery(x, P)), 4)}) + "\n")
        F.flush()
    print("%.0fs" % (time.time() - T0), L, rel, flush=True)
