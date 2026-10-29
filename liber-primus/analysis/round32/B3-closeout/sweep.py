#!/usr/bin/env python3
"""R32-B3 glibc gen=0 (random()%29) PRIOR-DENSE FIRST-FIRE. NOT the 2^32 space.
Keystream: round19/G1 gen_glibc.random_seq (TYPE_3, deg31 sep3) % 29 == seed_sweep/sweep.c gen=0.
Decoder: round19/I1 driftbeam presets pair|exact (sign -1, o=0, beam_w=64, L=120 screen).
Adjudicator: round19/I2 adjudicate -> SWEEPROW/1 rows; hitfn20 3-clause gate for escalation.
Usage: python sweep.py control | python sweep.py sweep [budget_s]
"""
import os, sys, json, time, random, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis/round19/G1", "analysis/round19/I1", "analysis/round19/I2", "analysis/round20/P3",
          "analysis/round20/HITFN", "analysis/round11", "analysis/campaign18_skip", "analysis/round13/B04", "src"):
    q = os.path.join(LP, p)
    if q not in sys.path: sys.path.insert(0, q)
import gen_glibc as GG, driftbeam as DB, adjudicate as AD, hitfn20 as H, skipdecode as sk
import lib_numchannel as nc

L_SCREEN, L_HIT, SCREEN_BAR, N_ADJ = 120, 240, 5.0, 10**6
AD._PANEL = AD.Panel(os.path.join(HERE, 'models', 'panel.npz'))  # lane-local REBUILD (see RESULTS: not byte-identical to the I2 build)
U = list(nc.unsolved()); C_SCREEN, C_HIT = U[:L_SCREEN], U[:L_HIT]
NEED = L_HIT * 6 + 64

def ks(seed, n=NEED):
    return [x % 29 for x in GG.random_seq(int(seed) & 0xFFFFFFFF, n)]

def seeds():
    out, seen = [], set()
    def add(x, lab):
        x = int(x) & 0xFFFFFFFF
        if x not in seen: seen.add(x); out.append((x, lab))
    import seeds as B04
    for x in B04.NUM_INTS: add(x, "B04 NUM_INTS")
    for x in B04.FIRST_PRIMES: add(x, "B04 prime")
    for t in B04.NUM_STRINGS:
        try: add(int(t), "B04 NUM_STRINGS")
        except ValueError: pass
    for x in (3301, 1033, 761, 845145127, 1595277641, 1325734783, 1325635200, 1357257600, 1388880000, 2012, 2013, 2014, 29): add(x, "3301 family")
    for e in json.load(open(os.path.join(LP, "analysis", "round20", "P3", "seedprior20.json")))["order"]: add(int(e["seed"]), "seedprior20")
    d0 = datetime.date(2011, 1, 1)
    for i in range((datetime.date(2015, 12, 31) - d0).days + 1):
        d = d0 + datetime.timedelta(days=i)
        ts = int(datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc).timestamp())
        add(ts, "unix-midnight-UTC " + d.isoformat())
        add(d.year * 10000 + d.month * 100 + d.day, "YYYYMMDD " + d.isoformat())
    for x in range(0, 2048): add(x, "small-int")
    t0 = int(datetime.datetime(2011, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
    t1 = int(datetime.datetime(2016, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
    for ts in range(t0, t1, 3600): add(ts, "unix-top-of-hour-UTC")
    return out

def screen(K, preset, C=C_SCREEN):
    d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=64, **DB.PRESETS[preset])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return float(a["pmax"]), a, d

def enc_pair(P, K, supp=0.83, seed=777):
    rng = random.Random(seed); C, j, cp = [], 0, None
    for p in P:
        while True:
            c = (p + K[j]) % 29
            if cp is not None and c == cp and rng.random() < supp: j += 2; continue
            break
        C.append(c); j += 1; cp = c
    return C

def control():
    eng = sk.eng_to_idx(open(os.path.join(LP, "data", "keys", "self_reliance.txt"), encoding="utf-8", errors="ignore").read())[5000:5000+L_HIT]
    assert GG.random_seq(1, 3) == [1804289383, 846930886, 1681692777], "glibc port mismatch vs known srandom(1) outputs"
    res = []
    for seed in (1325734783, 3301, 20120105):
        K = ks(seed)
        for preset in ("pair", "exact"):
            if preset == "pair": C = enc_pair(eng, K)
            else: C = list(sk.encipher_keyskip(eng, K, sign=-1, supp=0.83, seed=777)[0])[:L_HIT]
            pm, _, _ = screen(K, preset, C[:L_SCREEN])
            v = H.evaluate(H.HitDecode(C=C[:L_HIT], K=K, o=0, preset=preset, n_round_adjudicated=N_ADJ, truth_idx=eng[:len(C[:L_HIT])]))
            ok = pm >= SCREEN_BAR and bool(v.hit) and v.recovery >= 0.90
            res.append({"seed": seed, "preset": preset, "screen_pmax": round(pm, 3), "stage_b_pmax": round(v.pmax, 3), "bar": round(v.bar, 4),
                        "recovery": round(v.recovery, 4), "heldout": round(v.heldout_recovery, 4), "hit": bool(v.hit), "pass": ok})
            print(res[-1], flush=True)
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "generator": "glibc random()%29 (gen=0)", "plants": res,
           "all_pass": all(r["pass"] for r in res), "min_recovery": min(r["recovery"] for r in res)}
    json.dump(out, open(os.path.join(HERE, "control.json"), "w"), indent=1)
    return 0 if out["all_pass"] else 1

def sweep(budget):
    c = json.load(open(os.path.join(HERE, "control.json")))
    if not c["all_pass"]: print("REFUSE: control failed"); return 2
    S = seeds(); t0 = time.time(); n = 0; best = {}; hist = {"pair": {}, "exact": {}}; flagged = []; sb = 0
    hdr = AD.header("round32/B3/glibc-gen0-priordense", key_space="glibc srandom(seed);random() mod 29, seed in prior-dense list (%d seeds), offset 0" % len(S),
                    decoder="driftbeam pair|exact keyskip, sign -1, beam_w 64, L120", register_panel="I2 nine-register panel")
    out = open(os.path.join(HERE, "sweep_rows.jsonl"), "w"); out.write(json.dumps(hdr) + "\n")
    done_seeds = 0
    for seed, lab in S:
        if time.time() - t0 > budget: break
        K = ks(seed)
        for preset in ("pair", "exact"):
            pm, a, d = screen(K, preset)
            n += 1; b = "%.1f" % (int(pm * 10) / 10.0); hist[preset][b] = hist[preset].get(b, 0) + 1
            if pm > best.get(preset, (-1e9,))[0]: best[preset] = (round(pm, 3), seed, lab)
            out.write(json.dumps(AD.to_row(a, "glibc0:%d:%s" % (seed, preset))) + "\n")
            if pm >= SCREEN_BAR:
                sb += 1
                v = H.evaluate(H.HitDecode(C=C_HIT, K=K, o=0, preset=preset, n_round_adjudicated=N_ADJ))
                if v.hit or v.pmax >= v.bar:
                    flagged.append({"seed": seed, "label": lab, "preset": preset, "pmax": round(v.pmax, 3), "bar": round(v.bar, 4), "recovery": round(v.recovery, 4), "FLAGGED_FOR_ORACLE": True})
        done_seeds += 1
    out.close()
    summ = {"seeds_in_list": len(S), "seeds_completed_both_presets": done_seeds, "decodes": n, "stage_b": sb, "best": best, "hist": hist,
            "flagged": flagged, "elapsed_s": round(time.time() - t0, 1), "complete": done_seeds == len(S)}
    json.dump(summ, open(os.path.join(HERE, "sweep_summary.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "hist"}))
    return 0

if __name__ == "__main__":
    sys.exit(control() if sys.argv[1] == "control" else sweep(float(sys.argv[2]) if len(sys.argv) > 2 else 1200))
