import sys, os, json, random, time
sys.argv = sys.argv[:1]
import run_null_free as R
np = R.np
def more(L, s0):
    K = R.B2.sha_ctr_key(R.kl(L)); out = open(R.F("control_free_stream.jsonl"), "a"); t0 = time.time()
    for reg in R.PAN.registers:
        a = R.TH[reg].astype(np.int64)
        for s in range(s0, 20):
            if s % 5 == 0: R.memwait()
            r = random.Random(9000 + s); st = r.randrange(0, len(a) - L - 1); P = a[st:st + L].tolist()
            C, _ = R.B2.ENCIPHER["free_q05"](P, K, 0.83, 3301 + s)
            x = R.V.beam_decode_v3(C, K, "free", "panel_max", tau=0.0, lam_u=4.0)["plain_idx"]
            out.write(json.dumps({"L": L, "register": reg, "seed": s, "pmax": R.pm_of([x])[0], "rec": round(float(R.B2.recovery(x, P)), 4), "len": len(x)}) + "\n")
        out.flush(); print(L, reg, "%.0fs" % (time.time() - t0), flush=True)
more(400, 5); more(729, 3)
