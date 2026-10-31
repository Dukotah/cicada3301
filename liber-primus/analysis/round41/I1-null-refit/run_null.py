"""R41 I1 population draw: python run_null.py [wall_cap_s].  Appends survivor rows to null_stream.jsonl (resumable by block)."""
from i1lib import *
TARGET_S, TARGET_240 = 41000, int(os.environ.get("T240", "5200"))
CAP = float(sys.argv[1]) if len(sys.argv) > 1 else 6000
STATE, STREAM = F("run_state.json"), F("null_stream.jsonl")
st = json.load(open(STATE)) if os.path.exists(STATE) else {"blk": 0, "screened": {f: 0 for f in FAMILIES}, "surv": {f: 0 for f in FAMILIES}, "n_surv": 0, "n240": 0}
BLK = 1 << 16
t0 = time.time(); out = open(STREAM, "a")
log("start", json.dumps({k: v for k, v in st.items()}))
wait_mem()
while st["n_surv"] < TARGET_S and time.time() - t0 < CAP:
    b = st["blk"]
    for fi, fam in enumerate(FAMILIES):
        rng = np.random.default_rng([4101, b, fi])
        seeds = seeds_for(fam, rng, BLK); m = pass_mask(seeds, fam); sv = seeds[m]
        st["screened"][fam] += BLK
        for s in sv:
            K = ks_full(fam, s); row = {"fam": fam, "seed": int(s), "blk": b}
            for r in RELS:
                d, a = v3dec(U[:120], K, r)
                row[r] = [round(float(a["pmax"]), 4), int(a["preg"]), int(a["mds"]), round(float(a["ioc"]), 4)]
            if st["n240"] < TARGET_240:
                for r in RELS:
                    d, a = v3dec(U[:240], K, r)
                    row[r + "_240"] = [round(float(a["pmax"]), 4), int(a["preg"]), int(a["mds"]), round(float(a["ioc"]), 4)]
                st["n240"] += 1
            out.write(json.dumps(row) + "\n"); st["surv"][fam] += 1; st["n_surv"] += 1
    st["blk"] = b + 1; out.flush(); json.dump(st, open(STATE, "w"))
    if b % 5 == 0:
        log("blk", b, "surv", st["n_surv"], "n240", st["n240"], "%.0f s" % (time.time() - t0))
    if b % 20 == 19: wait_mem()
log("done", json.dumps(st))
