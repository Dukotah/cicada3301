#!/usr/bin/env python3
"""R32-B1 bash-4.2 $RANDOM auto-seeded orbit (74 x 2^20 = 77,594,624 seeds) x {LP64, ILP32} x {keyskip1, keyskip2}.
Stage 1: vectorised relation-agnostic panel-trigram prefilter on the first M_PF decoded runes (before any skip).
Stage 2: driftbeam pair|exact (sign -1, o=0, beam_w 64, L120) + round32/I2 nine-register panel -> SWEEPROW rows.
Stage 3: hitfn20 3-clause gate at L240 for pmax >= SCREEN_BAR.
Usage: python sweep.py control | python sweep.py sweep [budget_s]
"""
import time
from common import *
import numpy as np, pf

M_PF, FPR_TARGET = 16, 6e-4
SCREEN_BAR, N_ADJ = 5.0, 10 ** 6
SEC0, SEC1 = 1325376000, 1401580800           # 2012-01-01 .. 2014-06-01 (G1 section 3.3)
PREF = list(range(SEC0 >> 20, (SEC1 >> 20) + 1)); assert len(PREF) == 74
SUB = 1 << 18
PAN = AD.panel(); LMT = PAN.LMT.astype(np.float32)
CALF, ROWS, SUMF = [os.path.join(HERE, f) for f in ("control.json", "sweep_rows.jsonl", "sweep_summary.json")]


def rand_seeds(rng, n):
    return np.array([(rng.choice(PREF) << 20) | rng.randrange(1 << 20) for _ in range(n)], dtype=np.uint64)


def norm_of(cal, v):
    return (np.array(cal[v]["mu"], dtype=np.float32), np.array(cal[v]["sd"], dtype=np.float32))


def prefilter_scores(seeds, v, C16, norm):
    K = pf.heads(seeds, M_PF, v)
    S = pf.tri_stat((C16[:, None] - K) % 29, LMT, *norm)
    return S.max(1)


def calibrate(C16):
    rng = random.Random(3301); out = {}
    for v in VARIANTS:
        sd = rand_seeds(rng, 1 << 19)
        K = pf.heads(sd, M_PF, v); S = pf.tri_stat((C16[:, None] - K) % 29, LMT)
        mu, sdv = S.mean(0), S.std(0); mx = ((S - mu) / sdv).max(1)
        thr = float(np.quantile(mx, 1 - FPR_TARGET))
        out[v] = {"mu": mu.tolist(), "sd": sdv.tolist(), "thr": thr, "null_n": len(sd),
                  "null_exceed": float((mx > thr).mean())}
    return out


def screen(K, preset, C):
    d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=64, **DB.PRESETS[preset])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return float(a["pmax"]), a, d


RELS = (("keyskip2", "pair"), ("keyskip1", "exact"))


def stage2(seed, v, C, CH, out=None, N=N_ADJ, truth=None):
    K = ks(seed, v); res = []
    for rel, preset in RELS:
        pm, a, d = screen(K, preset, C[:L_SCREEN])
        if out is not None:
            out.write(json.dumps(AD.to_row(a, "bash:%s:%d:%s" % (v, seed, rel))) + "\n")
        r = {"seed": int(seed), "variant": v, "rel": rel, "preset": preset, "pmax": pm}
        if pm >= SCREEN_BAR:
            ver = H.evaluate(H.HitDecode(C=CH, K=K, o=0, preset=preset, n_round_adjudicated=N, truth_idx=truth))
            r.update(stage_b_pmax=float(ver.pmax), bar=float(ver.bar), recovery=float(ver.recovery),
                     heldout=float(ver.heldout_recovery), hit=bool(ver.hit))
        res.append(r)
    return res


def chunk(seeds, v, C, CH, cal, out=None, truth=None):
    C16 = np.array(C[:M_PF], dtype=np.int8)
    S = prefilter_scores(seeds, v, C16, norm_of(cal, v))
    surv = seeds[S > cal[v]["thr"]]
    res = []
    for s in surv:
        res += stage2(int(s), v, C, CH, out, truth=truth)
    return len(surv), res


def control():
    cal = calibrate(np.array(U[:M_PF], dtype=np.int8))
    rng = random.Random(3301); chk = {}
    for v in VARIANTS:                       # (0) vectorised head == exact generator
        sd = rand_seeds(rng, 2000); H16 = pf.heads(sd, 16, v)
        bad = sum(1 for i, s in enumerate(sd) if [int(x) for x in H16[:, i]] != ks(int(s), v, 16))
        chk[v] = {"seeds": 2000, "head_mismatch": bad}   # mismatches can only be anti-repeat collisions (p ~ 16/32768)
    cor = corpora(); prefpow = []
    for v in VARIANTS:                       # (1) prefilter power at the chosen threshold
        for rel, enc in (("keyskip2", enc_pair), ("keyskip1", enc_exact)):
            for reg, txt in cor.items():
                seeds = rand_seeds(rng, 250); Cs = []
                for i, s in enumerate(seeds):
                    st = rng.randrange(0, len(txt) - 130); Cs.append(enc(txt[st:st + 120], ks(int(s), v), seed=i + 1)[:M_PF])
                Cs = np.array(Cs, dtype=np.int8).T; Kp = pf.heads(seeds, M_PF, v)
                S = pf.tri_stat((Cs - Kp) % 29, LMT, *norm_of(cal, v)).max(1)
                prefpow.append({"variant": v, "rel": rel, "register": reg, "n": 250,
                                "power": round(float((S > cal[v]["thr"]).mean()), 3)})
                print(prefpow[-1], flush=True)
    e2e = []                                 # (2) end-to-end: planted seed in a 2^16-seed chunk through the real chunk path
    for v in VARIANTS:
        for rel, enc in (("keyskip2", enc_pair), ("keyskip1", enc_exact)):
            npass = nrec = 0
            for ntry in range(10):
                ps = (rng.choice(PREF) << 20) | rng.randrange(1 << 20)
                reg = "EN_MODERN" if ntry % 2 == 0 else "LATIN"; txt = cor[reg]
                s0 = rng.randrange(0, len(txt) - 300); P = txt[s0:s0 + L_HIT]
                Cp = enc(P, ks(ps, v), seed=ntry + 1)[:L_HIT]
                base = ps & ~0xFFFF
                seeds = np.arange(base, base + (1 << 16), dtype=np.uint64)
                n_s, rr = chunk(seeds, v, Cp, Cp, cal, truth=P[:len(Cp)])
                hit = [r for r in rr if r["seed"] == ps and r["rel"] == rel]
                pfp = any(r["seed"] == ps for r in rr)
                ok = bool(hit and hit[0].get("hit") and hit[0]["recovery"] >= 0.90)
                npass += pfp; nrec += ok
                e2e.append({"variant": v, "rel": rel, "seed": int(ps), "register": reg, "prefilter_pass": bool(pfp),
                            "recovered_hit": ok, "survivors_in_chunk": n_s,
                            "pmax": hit[0]["pmax"] if hit else None, "stage_b_pmax": hit[0].get("stage_b_pmax") if hit else None,
                            "bar": hit[0].get("bar") if hit else None, "recovery": hit[0].get("recovery") if hit else None})
                print(e2e[-1], flush=True)
            e2e.append({"summary": True, "variant": v, "rel": rel, "tries": 10, "prefilter_pass": npass, "recovered_hit": nrec})
    sums = [r for r in e2e if r.get("summary")]
    # pass: >=3 recovered end-to-end in every cell, and every plant that survived the prefilter was recovered at the gate
    allpass = (all(s["recovered_hit"] >= 3 and s["recovered_hit"] >= s["prefilter_pass"] - 1 for s in sums)
               and all(c["head_mismatch"] <= 8 for c in chk.values()))
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "construction": "bash 4.2 $RANDOM, RANDOM%29, sign -1, offset 0, seed=tv_sec^tv_usec^pid; LP64 and ILP32",
           "m_prefilter": M_PF, "fpr_target": FPR_TARGET, "prefilter_calibration": cal, "head_vs_exact": chk,
           "prefilter_power": prefpow, "e2e_plants": e2e, "all_pass": bool(allpass)}
    json.dump(out, open(CALF, "w"), indent=1)
    print("ALL_PASS", allpass)
    return 0 if allpass else 1


def sweep(budget):
    c = json.load(open(CALF))
    if not c["all_pass"]:
        print("REFUSE: control failed"); return 2
    cal = c["prefilter_calibration"]; t0 = time.time()
    order = PREF[:]; random.Random(3301).shuffle(order)
    hdr = AD.header("round32/B1/bash42-auto-seeded-orbit",
                    key_space="bash 4.2 $RANDOM%29, seed=(tv_sec>>20<<20)|v, 74 prefixes x 2^20 = 77,594,624 seeds, variants bash4.2 LP64 + bash4.2_i32, offset 0, sign -1",
                    decoder="driftbeam pair(keyskip2)|exact(keyskip1), sign -1, beam_w 64, L120 screen / L240 gate",
                    register_panel="round32/I2-multiregister-readjudication nine-register panel (models/panel.npz)",
                    prefilter={"m": M_PF, "stat": "max over 9 registers of z(sum trigram log10)", "fpr_target": FPR_TARGET,
                               "thr": {v: cal[v]["thr"] for v in VARIANTS}, "rows_only_for": "prefilter survivors"},
                    n_round_adjudicated_reference=N_ADJ, seed_sample="prefix order shuffled with Random(3301)")
    out = open(ROWS, "w"); out.write(json.dumps(hdr) + "\n")
    st = {"prefix_done": 0, "seeds_prefiltered": {v: 0 for v in VARIANTS}, "survivors": {v: 0 for v in VARIANTS},
          "decodes": 0, "best": {}, "stage_b": 0, "flagged": [], "hist": {"pair": {}, "exact": {}}, "gate3_crossers": []}

    def save(done):
        st.update(elapsed_s=round(time.time() - t0, 1), complete=done, prefix_order=order, prefixes_total=74,
                  coverage_fraction_seeds=st["prefix_done"] / 74.0, budget_s=budget, n_round_adjudicated_reference=N_ADJ)
        json.dump(st, open(SUMF, "w"), indent=1)
    stopped = False
    for pi, pre in enumerate(order):
        if time.time() - t0 > budget:
            stopped = True; break
        for sub in range(0, 1 << 20, SUB):
            seeds = np.arange((pre << 20) | sub, ((pre << 20) | sub) + SUB, dtype=np.uint64)
            for v in VARIANTS:
                n_s, rr = chunk(seeds, v, C_SCREEN, C_HIT, cal, out)
                st["seeds_prefiltered"][v] += SUB; st["survivors"][v] += n_s
                for r in rr:
                    st["decodes"] += 1
                    b = "%.1f" % (int(r["pmax"] * 10) / 10.0); h = st["hist"][r["preset"]]; h[b] = h.get(b, 0) + 1
                    key = r["rel"] + ":" + v
                    if r["pmax"] > st["best"].get(key, {"pmax": -1e9})["pmax"]:
                        st["best"][key] = {"pmax": round(r["pmax"], 3), "seed": r["seed"]}
                    if "stage_b_pmax" in r:
                        st["stage_b"] += 1
                        if r["stage_b_pmax"] >= r["bar"]: st["gate3_crossers"].append(r)
                        if r["hit"]: st["flagged"].append(dict(r, FLAGGED_FOR_ORACLE=True))
        st["prefix_done"] += 1; out.flush(); save(False)
        print("prefix %d/74 t=%.0fs decodes=%d surv=%s best=%s" % (pi + 1, time.time() - t0, st["decodes"], st["survivors"], st["best"]), flush=True)
    out.close(); save(not stopped)
    print(json.dumps({k: v for k, v in st.items() if k not in ("hist", "prefix_order")}))
    return 0


if __name__ == "__main__":
    sys.exit(control() if sys.argv[1] == "control" else sweep(float(sys.argv[2]) if len(sys.argv) > 2 else 2500))
