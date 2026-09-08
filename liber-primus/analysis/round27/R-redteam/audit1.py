#!/usr/bin/env python3
"""R-lane audit part 1: artifact recomputation (no C engine yet)."""
import json, math, os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
R27 = os.path.abspath(os.path.join(HERE, ".."))
LP  = os.path.abspath(os.path.join(R27, "..", ".."))
sys.path.insert(0, os.path.join(R27, "P2-harness"))

V = json.load(open(os.path.join(R27, "P0-spec", "vectors.json")))
c = V["constants"]

# 1. claim bar formula
mu = float(c["panelmax_cell"]["mu"]); beta = float(c["panelmax_cell"]["beta"])
bar = mu + beta*(math.log(1e6) - math.log(-math.log(0.99)))
print("claim_bar recomputed: %.15f  vs frozen %s  match=%s" % (bar, c["claim_bar_pair_1e6"], abs(bar-float(c["claim_bar_pair_1e6"]))<1e-12))
print("cand margin: claim-1.5 = %.6f ; CAND_BAR=%s (SCREEN_BAR) ; extra headroom %.4f" % (bar-1.5, c["SCREEN_BAR"], bar-1.5-float(c["SCREEN_BAR"])))

# 2. py_scores.jsonl stats (false-reject python side)
rows = []
with open(os.path.join(R27, "P2-harness", "py_scores.jsonl")) as f:
    for ln in f:
        o = json.loads(ln); rows.append((int(o["seed"]), float(o["pmax"])))
rng = random.Random(27002)
want_seeds = [rng.randrange(0, 2**32) for _ in range(100000)]
got_seeds = [s for s,_ in rows]
print("py_scores rows=%d ; seed set == frozen RNG27002 sample: %s" % (len(rows), got_seeds == want_seeds))
mx = max(rows, key=lambda t: t[1])
hg = [t for t in rows if t[1] >= 5.883520294328688]
cb = [t for t in rows if t[1] >= 5.0]
print("py max pmax %.6f @ seed %d ; >=hard_gate: %d ; >=cand_bar: %d -> %s" % (mx[1], mx[0], len(hg), len(cb), sorted(cb)))

# 3. engine.dat constants vs vectors.json
dat = open(os.path.join(R27, "P1-engine", "engine.dat")).read().split("\n")
def datline(k):
    return [l for l in dat if l.startswith(k)][0]
mu_v = [float(x) for x in c["panel_mu_n120"]]
sd_v = [float(x) for x in c["panel_sd_n120"]]
mu_d = [float(x) for x in datline("MU ").split()[1:]]
sd_d = [float(x) for x in datline("SD ").split()[1:]]
print("engine.dat MU==vectors: %s  SD==vectors: %s" % (mu_d==mu_v, sd_d==sd_v))
cs_d = [int(x) for x in dat[dat.index(datline("CSCREEN 120"))+1].split()]
print("engine.dat CSCREEN==vectors C_SCREEN: %s" % (cs_d == V["ciphertext"]["C_SCREEN"]))
pc_d = [int(x) for x in dat[dat.index(datline("PLANT_CIPHER 120"))+1].split()]
print("engine.dat PLANT_CIPHER==vectors planted_stage_a.cipher_idx_120: %s" % (pc_d == V["planted_stage_a"]["cipher_idx_120"]))
print("vectors planted_stage_a pmax:", V["planted_stage_a"]["pmax"])
print("vectors planted_selftest verdict:", json.dumps(V["planted_selftest"]["verdict"])[:300])

# 4. STATUS.json arithmetic
S = json.load(open(os.path.join(R27, "P1-engine", "run", "STATUS.json")))
W = S["workers"]
cov = sum(w["cursor"]-w["band_start"] for w in W)
done = sum(w["seeds_done"] for w in W)
cands = sum(w["n_candidates"] for w in W)
print("bands contiguous:", all(W[i]["band_end"]==W[i+1]["band_start"] for i in range(5)), "start", W[0]["band_start"], "end", W[-1]["band_end"], "== 2^32:", W[-1]["band_end"]==2**32)
print("agg seeds_done %d (file %d) cov %d (file %d) lag(done-cov) %d (max 255*6=1530)" % (done, S["aggregate"]["seeds_done"], cov, S["aggregate"]["lane_words_covered"], done-cov))
print("coverage_fraction file %.9f recomputed %.9f" % (S["aggregate"]["lane_coverage_fraction"], cov/2**32))
print("n_candidates file %d sum %d ; cand rate %.3e /seed ; ratio vs gumbel 6.95e-5: %.2fx" % (S["aggregate"]["n_candidates"], cands, cands/done, (cands/done)/6.95e-5))
print("n_claim_bar_hits:", S["aggregate"]["n_claim_bar_hits"], "best", S["aggregate"]["best_pmax"], "@", S["aggregate"]["best_word"])

# 5. candidates.jsonl consistency
import collections
n=0; mxc=(-1,0); lanes=collections.Counter(); below=0
seen=set(); dups=0
with open(os.path.join(R27, "P1-engine", "run", "candidates.jsonl")) as f:
    for ln in f:
        ln=ln.strip()
        if not ln: continue
        o=json.loads(ln); n+=1; lanes[o.get("lane")]+=1
        p=float(o["pmax"])
        if p < 5.0: below+=1
        if p > mxc[1]: mxc=(o["seed"],p)
        if o["seed"] in seen: dups+=1
        seen.add(o["seed"])
print("candidates.jsonl: %d rows, lanes %s, below-bar rows %d, dup seeds %d, max pmax %.6f @ %d" % (n, dict(lanes), below, dups, mxc[1], mxc[0]))

# 6. histogram consistency
import struct
h = open(os.path.join(R27, "P1-engine", "run", "hist_S1.u64"), "rb").read()
nbins = len(h)//8//6
hist = struct.unpack("<%dQ" % (len(h)//8), h)
tot = sum(hist)
above5 = sum(hist[w*nbins+b] for w in range(6) for b in range(500, nbins))
above_claim = sum(hist[w*nbins+b] for w in range(6) for b in range(739, nbins))
print("hist: bins/worker %d, total count %d (vs seeds_done %d), >=bin500(5.00) %d, >=bin739 %d" % (nbins, tot, done, above5, above_claim))

# 7. top_S1.json vs best
T = json.load(open(os.path.join(R27, "P1-engine", "run", "top_S1.json")))
print("top_S1: %d entries, top %.6f @ %d (STATUS best %.6f @ %d)" % (len(T), T[0]["pmax"], T[0]["seed"], S["aggregate"]["best_pmax"], S["aggregate"]["best_word"]))
