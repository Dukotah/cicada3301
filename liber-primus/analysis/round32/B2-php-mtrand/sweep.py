#!/usr/bin/env python3
"""R32-B2 PHP mt_rand first-fire: {canonical MT19937, PHP<=7.0 broken twist} x {RAND_RANGE scale29, mod29} x {keyskip1 exact, keyskip2 pair}.
Tier (a) prior-dense seeds; tier (b) uniform random 3301-seeded sample of the 2^32 seed space, prefilter->decode, wall-capped.
Usage: python sweep.py control | python sweep.py sweep [budget_s]
"""
import time
from common import *
import numpy as np, pf_tri as pf
import php_mt as P

M_PF, FPR_TARGET = 16, 6e-4
SCREEN_BAR, N_ADJ = 5.0, 10 ** 6
BLK = 1 << 17
PAN = AD.panel(); LMT = PAN.LMT.astype(np.float32)
CALF, ROWS, SUMF = [os.path.join(HERE, f) for f in ("control.json", "sweep_rows.jsonl", "sweep_summary.json")]
RELS = (("keyskip2", "pair"), ("keyskip1", "exact"))
CN = [cname(c) for c in CELLS]


def tier_a_seeds():
    """(core, dense): core = lore/literature/PGP-second seeds (decoded unfiltered); dense = dates/unix/hours/small ints (prefiltered)."""
    import datetime; sys.path.append(os.path.join(LP, "analysis", "round13", "B04")); import seeds as B04
    core, dense, seen = [], [], set()

    def add(lst, x, lab):
        x = int(x) & 0xFFFFFFFF
        if x not in seen: seen.add(x); lst.append((x, lab))
    for x in B04.NUM_INTS: add(core, x, "B04 NUM_INTS")
    for x in B04.FIRST_PRIMES: add(core, x, "B04 prime")
    for t in B04.NUM_STRINGS:
        try: add(core, int(t), "B04 NUM_STRINGS")
        except ValueError: pass
    for x in (3301, 1033, 761, 845145127, 1595277641, 1325734783, 1325635200, 1357257600, 1388880000, 2012, 2013, 2014, 29): add(core, x, "3301 family")
    for e in json.load(open(os.path.join(LP, "analysis", "round20", "P3", "seedprior20.json")))["order"]: add(core, e["seed"], "seedprior20")
    d0 = datetime.date(2011, 1, 1)
    for i in range((datetime.date(2015, 12, 31) - d0).days + 1):
        d = d0 + datetime.timedelta(days=i)
        add(dense, int(datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc).timestamp()), "unix-midnight-UTC")
        add(dense, d.year * 10000 + d.month * 100 + d.day, "YYYYMMDD")
    for x in range(0, 2048): add(dense, x, "small-int")
    t0 = int(datetime.datetime(2011, 1, 1, tzinfo=datetime.timezone.utc).timestamp()); t1 = int(datetime.datetime(2016, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
    for ts in range(t0, t1, 3600): add(dense, ts, "unix-top-of-hour-UTC")
    return core, dense


def norm_of(cal, cn): return (np.array(cal[cn]["mu"], dtype=np.float32), np.array(cal[cn]["sd"], dtype=np.float32))


def cell_scores(H31, cell, C16, norm):
    K = P.reduce_heads(H31[cell[0]], cell[1])
    return pf.tri_stat((C16[:, None] - K) % 29, LMT, *norm).max(1)


def calibrate(C16):
    rng = np.random.default_rng(3301); sd = rng.integers(0, 1 << 32, size=1 << 19, dtype=np.uint64); out = {}
    Hs = [P.heads_all(sd[i:i + BLK], M_PF) for i in range(0, len(sd), BLK)]
    for cell in CELLS:
        S = np.concatenate([pf.tri_stat((C16[:, None] - P.reduce_heads(h[cell[0]], cell[1])) % 29, LMT) for h in Hs])
        mu, sdv = S.mean(0), S.std(0); mx = ((S - mu) / sdv).max(1); thr = float(np.quantile(mx, 1 - FPR_TARGET))
        out[cname(cell)] = {"mu": mu.tolist(), "sd": sdv.tolist(), "thr": thr, "null_n": len(sd), "null_exceed": float((mx > thr).mean())}
    return out


def screen(K, preset, C):
    d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=64, **DB.PRESETS[preset])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return float(a["pmax"]), a, d


def stage2(seed, cell, C, CH, out=None, N=N_ADJ, truth=None, label=""):
    K = ks(seed, cell); res = []
    for rel, preset in RELS:
        pm, a, d = screen(K, preset, C[:L_SCREEN])
        if out is not None: out.write(json.dumps(AD.to_row(a, "php:%s:%d:%s" % (cname(cell), seed, rel))) + "\n")
        r = {"seed": int(seed), "cell": cname(cell), "rel": rel, "preset": preset, "pmax": pm}
        if label: r["label"] = label
        if pm >= SCREEN_BAR:
            ver = H.evaluate(H.HitDecode(C=CH, K=K, o=0, preset=preset, n_round_adjudicated=N, truth_idx=truth))
            r.update(stage_b_pmax=float(ver.pmax), bar=float(ver.bar), recovery=float(ver.recovery), heldout=float(ver.heldout_recovery), hit=bool(ver.hit))
        res.append(r)
    return res


def chunk(seeds, cal, C, CH, out=None, truth=None, cells=CELLS):
    """Real chunk path: shared MT head, per-cell prefilter, decode survivors. Returns {cell: (n_surv, rows)}."""
    C16 = np.array(C[:M_PF], dtype=np.int8); H31 = P.heads_all(seeds, M_PF); res = {}
    for cell in cells:
        S = cell_scores(H31, cell, C16, norm_of(cal, cname(cell)))
        surv = seeds[S > cal[cname(cell)]["thr"]]; rows = []
        for s in surv: rows += stage2(int(s), cell, C, CH, out, truth=truth)
        res[cell] = (len(surv), rows)
    return res


def rand_seed_arr(rng, n): return rng.integers(0, 1 << 32, size=n, dtype=np.uint64)


def control():
    cal = calibrate(np.array(U[:M_PF], dtype=np.int8))
    st = P.selftest(); print(st, flush=True)
    rng = random.Random(3301); nrng = np.random.default_rng(33011); cor = corpora(); prefpow = []
    for cell in CELLS:                                   # (1) prefilter power
        for rel, enc in (("keyskip2", enc_pair), ("keyskip1", enc_exact)):
            for reg, txt in cor.items():
                seeds = rand_seed_arr(nrng, 250); Cs = []
                for i, s in enumerate(seeds):
                    stt = rng.randrange(0, len(txt) - 130); Cs.append(enc(txt[stt:stt + 120], ks(int(s), cell, 400), seed=i + 1)[:M_PF])
                Cs = np.array(Cs, dtype=np.int8).T
                Kp = P.reduce_heads(P.heads_all(seeds, M_PF)[cell[0]], cell[1])
                S = pf.tri_stat((Cs - Kp) % 29, LMT, *norm_of(cal, cname(cell))).max(1)
                prefpow.append({"cell": cname(cell), "rel": rel, "register": reg, "n": 250, "power": round(float((S > cal[cname(cell)]["thr"]).mean()), 3)})
                print(prefpow[-1], flush=True)
    e2e = []                                             # (2) end-to-end plants through chunk()
    NP = 8
    for cell in CELLS:
        for rel, enc in (("keyskip2", enc_pair), ("keyskip1", enc_exact)):
            npass = nrec = 0
            for ntry in range(NP):
                ps = rng.randrange(1 << 32); reg = "EN_MODERN" if ntry % 2 == 0 else "LATIN"; txt = cor[reg]
                s0 = rng.randrange(0, len(txt) - 300); Ptxt = txt[s0:s0 + L_HIT]
                Cp = enc(Ptxt, ks(ps, cell), seed=ntry + 1)[:L_HIT]
                base = ps & ~0xFFFF
                seeds = np.arange(base, base + (1 << 16), dtype=np.uint64)
                n_s, rr = chunk(seeds, cal, Cp, Cp, truth=Ptxt[:len(Cp)], cells=[cell])[cell]
                hit = [r for r in rr if r["seed"] == ps and r["rel"] == rel]
                pfp = any(r["seed"] == ps for r in rr)
                ok = bool(hit and hit[0].get("hit") and hit[0]["recovery"] >= 0.90)
                npass += pfp; nrec += ok
                e2e.append({"cell": cname(cell), "rel": rel, "seed": int(ps), "register": reg, "prefilter_pass": bool(pfp), "recovered_hit": ok,
                            "survivors_in_chunk": n_s, "pmax": hit[0]["pmax"] if hit else None, "stage_b_pmax": hit[0].get("stage_b_pmax") if hit else None,
                            "bar": hit[0].get("bar") if hit else None, "recovery": hit[0].get("recovery") if hit else None})
                print(e2e[-1], flush=True)
            e2e.append({"summary": True, "cell": cname(cell), "rel": rel, "tries": NP, "prefilter_pass": npass, "recovered_hit": nrec})
    sums = [r for r in e2e if r.get("summary")]
    selfok = (st["canonical_seed1_first_u32_is_1791095845"] and st["canonical_vs_numpy_MT19937_raw"] is True and st["vectorised_heads_equal_scalar"]
              and st.get("matches_round28_L4_gen28_(validated_vs_real_php_8.5.4)") is True)
    allpass = bool(all(s["recovered_hit"] >= 3 and s["recovered_hit"] >= s["prefilter_pass"] - 1 for s in sums) and selfok)
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "construction": "PHP mt_rand, canonical MT19937 + pre-7.1 broken twist; scale29 (RAND_RANGE) + mod29; sign -1, offset 0",
           "m_prefilter": M_PF, "fpr_target": FPR_TARGET, "prefilter_calibration": cal, "selftest": st, "prefilter_power": prefpow, "e2e_plants": e2e, "all_pass": allpass}
    json.dump(out, open(CALF, "w"), indent=1); print("ALL_PASS", allpass)
    return 0 if allpass else 1


def sweep(budget):
    c = json.load(open(CALF))
    if not c["all_pass"]: print("REFUSE: control failed"); return 2
    cal = c["prefilter_calibration"]; t0 = time.time()
    core, dense = tier_a_seeds()
    hdr = AD.header("round32/B2/php-mt_rand",
                    key_space="PHP mt_rand seeds: tier(a) prior-dense %d core (unfiltered) + %d dense (prefiltered); tier(b) uniform random sample of 2^32 (np default_rng(3301)); twists mt+php(<=7.0); reductions scale29+mod29; offset 0, sign -1" % (len(core), len(dense)),
                    decoder="driftbeam pair(keyskip2)|exact(keyskip1), sign -1, beam_w 64, L120 screen / L240 gate",
                    register_panel="round32/I2-multiregister-readjudication nine-register panel (models/panel.npz)",
                    prefilter={"m": M_PF, "stat": "max over 9 registers of z(sum trigram log10)", "fpr_target": FPR_TARGET,
                               "thr": {k: cal[k]["thr"] for k in CN}, "rows_only_for": "prefilter survivors (tier a core: all seeds)"},
                    n_round_adjudicated_reference=N_ADJ, seed_sample="tier b: numpy default_rng(3301).integers(0,2^32), blocks of 2^17")
    out = open(ROWS, "w"); out.write(json.dumps(hdr) + "\n")
    st = {"tier_a_core": len(core), "tier_a_dense": len(dense), "decodes": 0, "stage_b": 0, "flagged": [], "gate3_crossers": [], "best": {}, "hist": {},
          "tier": {"a_core": {"seeds": 0}, "a_dense": {"seeds": 0, "survivors": {k: 0 for k in CN}}, "b": {"seeds": 0, "survivors": {k: 0 for k in CN}}},
          "top": {k + ":" + r[0]: [] for k in CN for r in RELS}}

    def note(rows):
        for r in rows:
            st["decodes"] += 1; key = r["cell"] + ":" + r["rel"]
            b = "%.1f" % (int(r["pmax"] * 10) / 10.0); h = st["hist"].setdefault(r["preset"], {}); h[b] = h.get(b, 0) + 1
            if r["pmax"] > st["best"].get(key, {"pmax": -1e9})["pmax"]: st["best"][key] = {"pmax": round(r["pmax"], 3), "seed": r["seed"]}
            t = st["top"][key]; t.append((round(r["pmax"], 3), r["seed"])); t.sort(reverse=True); del t[5:]
            if "stage_b_pmax" in r:
                st["stage_b"] += 1
                if r["stage_b_pmax"] >= r["bar"]: st["gate3_crossers"].append(r)
                if r["hit"]: st["flagged"].append(dict(r, FLAGGED_FOR_ORACLE=True))

    def save(done):
        st.update(elapsed_s=round(time.time() - t0, 1), complete=done, budget_s=budget, n_round_adjudicated_reference=N_ADJ,
                  coverage_fraction_of_2p32_tier_b=st["tier"]["b"]["seeds"] / 2.0 ** 32)
        json.dump(st, open(SUMF, "w"), indent=1)
    for s, lab in core:                                  # tier a core: decode everything, 4 cells x 2 relations
        for cell in CELLS: note(stage2(s, cell, C_SCREEN, C_HIT, out, label=lab))
        st["tier"]["a_core"]["seeds"] += 1
    out.flush(); save(False); print("core done t=%.0fs decodes=%d best=%s" % (time.time() - t0, st["decodes"], st["best"]), flush=True)
    dseeds = np.array([s for s, _ in dense], dtype=np.uint64)
    for i in range(0, len(dseeds), BLK):
        blk = dseeds[i:i + BLK]; res = chunk(blk, cal, C_SCREEN, C_HIT, out)
        for cell, (ns, rows) in res.items(): st["tier"]["a_dense"]["survivors"][cname(cell)] += ns; note(rows)
        st["tier"]["a_dense"]["seeds"] += len(blk)
    out.flush(); save(False); print("dense done t=%.0fs decodes=%d" % (time.time() - t0, st["decodes"]), flush=True)
    rng = np.random.default_rng(3301); stopped = False
    while True:
        if time.time() - t0 > budget: stopped = True; break
        blk = rand_seed_arr(rng, BLK); res = chunk(blk, cal, C_SCREEN, C_HIT, out)
        for cell, (ns, rows) in res.items(): st["tier"]["b"]["survivors"][cname(cell)] += ns; note(rows)
        st["tier"]["b"]["seeds"] += BLK; out.flush(); save(False)
        if (st["tier"]["b"]["seeds"] // BLK) % 10 == 0:
            print("b seeds=%d t=%.0fs decodes=%d best=%s" % (st["tier"]["b"]["seeds"], time.time() - t0, st["decodes"], {k: v["pmax"] for k, v in st["best"].items()}), flush=True)
    out.close(); save(True)
    print(json.dumps({k: v for k, v in st.items() if k != "hist"}))
    return 0


if __name__ == "__main__":
    sys.exit(control() if sys.argv[1] == "control" else sweep(float(sys.argv[2]) if len(sys.argv) > 2 else 2400))
