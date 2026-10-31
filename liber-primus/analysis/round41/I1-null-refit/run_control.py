"""R41 I1 Q1b: planted correct keys through the REAL chunk path. 20 plants x 12 registers x 2 relations (bash 4.2 ABIs alternating).
Each plant: enc_exact / enc_pair of 240 test-half runes with a random orbit seed; only filter = realised C[:40] doublet-free (as the real LP2 head);
a 4096-seed chunk containing the key -> pf_v4_12 frozen -> v3 L=120 (both rels, all chunk survivors, like chunk_bash) -> v3 L=240 on the plant.
Appends raw rows to control_raw.jsonl (resumable); judging against the refit bars happens in judge_control.py.   python run_control.py"""
from i1lib import *
NPL = 20
OUT = F("control_raw.jsonl")
done = set()
if os.path.exists(OUT):
    for l in open(OUT): r = json.loads(l); done.add((r["register"], r["rel"], r["j"]))
rng = random.Random(4102); out = open(OUT, "a"); t0 = time.time()
BASH = ("bash4.2", "bash4.2_i32")
for reg in REGS:
    arr = TEST[reg].astype(np.int64)
    for rel in RELS:
        enc = C1.enc_exact if rel == "keyskip1" else C1.enc_pair
        for j in range(NPL):
            # draw the plant deterministically (rng advances even when resuming)
            for _ in range(500):
                v = BASH[j % 2]; ps = (rng.choice(PREF) << 20) | rng.randrange(1 << 20); K = C1.ks(ps, v, 1024)
                st = rng.randrange(0, len(arr) - 300); P = arr[st:st + 240].tolist()
                C = enc(P, K, seed=rng.randrange(1, 10 ** 9))[:240]
                if len(C) < 240 or any(C[i] == C[i + 1] for i in range(39)): continue
                break
            else:
                raise RuntimeError("no plant")
            if (reg, rel, j) in done: continue
            naive = [(P[i] + K[i]) % 29 for i in range(240)]; wsk = int(any(C[i] != naive[i] for i in range(24)))
            base = ps & ~0xFFF; seeds = np.arange(base, base + 4096, dtype=np.uint64)
            m = pass_mask(seeds, v, Chead=C); surv = seeds[m]
            e = {"register": reg, "rel": rel, "j": j, "abi": v, "seed": int(ps), "with_skip_head24": wsk, "chunk_survivors": int(m.sum()), "prefilter_pass": bool(ps in set(int(s) for s in surv))}
            if e["prefilter_pass"]:
                d1, a1 = v3dec(C[:120], K, rel); d2, a2 = v3dec(C, K, rel)
                e["pmax120"] = round(float(a1["pmax"]), 4); e["pmax240"] = round(float(a2["pmax"]), 4); e["preg120"] = REGS[a1["preg"]]; e["preg240"] = REGS[a2["preg"]]
                e["recovery240"] = round(float(B2.recovery(d2["plain_idx"], P)), 4); e["recovery120"] = round(float(B2.recovery(d1["plain_idx"], P[:120])), 4)
            out.write(json.dumps(e) + "\n"); out.flush()
        log("control", reg, rel, "%.0fs" % (time.time() - t0))
log("control done")
