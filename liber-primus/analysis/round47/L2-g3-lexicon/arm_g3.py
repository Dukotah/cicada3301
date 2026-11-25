"""R47-L2 arm G3: R38-C2-G3 lagged cw/dw pointers through words.py with the lane's OWN encipherers/decoders/judge.
  python -I arm_g3.py faith   C0 re-run of all 576 original jobs; must reproduce ks1 4.911 / ks2 4.700 / direct 4.038
  python -I arm_g3.py real    CS + CE on pages 1,2,4,5 (768 decodes), SWEEPROW store, combined-N bars, gate
  python -I arm_g3.py plants  matched arm (a/b/bp x pages 0,1,2,4,5 x C0/CS/CE x 2 reps) + mismatch arm (a)
Writes only in this folder."""
import os, sys, json, time, math, random, itertools
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import l2lib as L
C2 = os.path.join(L.LP, "analysis", "round38", "C2-never-cells")
sys.path.insert(0, C2)
RG = L.G._load("r38_run_gaps", os.path.join(C2, "gaps", "run_gaps.py"))
lib = sys.modules["lib"]
F = lambda n: os.path.join(HERE, n)
U = list(lib.U)
REAL = L.real_words()
CELLS = RG.g3_cells()
ORIG_N = {"keyskip1": 96, "keyskip2": 96, "direct": 384}
NEW_N = {"keyskip1": 128, "keyskip2": 128, "direct": 512}
COMB_N = {k: ORIG_N[k] + NEW_N[k] for k in ORIG_N}
RECORDED = {"keyskip1": 4.911, "keyskip2": 4.700, "direct": 4.038}
MID = (1, 2, 4, 5)


def jobs(pages):
    out = []
    for cell in CELLS:
        for p in pages:
            for sigma in (-1, 1):
                for rel in (lib.RELS if cell[4] == "A3" else ("direct",)):
                    out.append({"c": cell, "page": p, "sigma": sigma, "rel": rel})
    return out


def decode_unit(j, Cfull, lens, L_):
    return RG.g3_run(j["c"], j["page"], j["sigma"], j["rel"], L_, C=Cfull[:L_], Cfull=Cfull, lens=lens)


def faith():
    """C0 on pages 0-5: lens must equal the lane's LENSP; best per relation must reproduce the record."""
    eq = {}
    for p in range(6):
        u0, lens, ue = L.unit(REAL, p, "C0")
        eq[p] = (u0 == lib.page_start(p)) and lens == RG.LENSP[p]
    best = {}
    t0 = time.time()
    for j in jobs(range(6)):
        p = j["page"]; Cf = RG.HEADFULL[p]
        _, a = decode_unit(j, Cf, RG.LENSP[p], 120); pm = float(a["pmax"])
        if pm > best.get(j["rel"], -9): best[j["rel"]] = pm
    best = {k: round(v, 3) for k, v in best.items()}
    ok = all(eq.values()) and all(abs(best[k] - RECORDED[k]) < 0.0015 for k in RECORDED)
    out = {"c0_lens_equal_LENSP": eq, "best": best, "recorded": RECORDED, "reproduced": ok, "n": len(jobs(range(6))), "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(F("g3_faith.json"), "w"), indent=1); print(json.dumps(out)); return ok


def real():
    js = jobs(MID); rows = lib.Rows(F("g3_sweep_rows.jsonl"), lib.header(
        "round47/L2/g3", "R38-C2-G3 40 cells x pages 1,2,4,5 x sigma x (ks1,ks2 for A3) under fragment conventions CS and CE (words.py)",
        "as R38-C2-G3: A1/A2 beam-free direct (judged vs keyskip1 bar), A3 beam_v3 keyskip1/keyskip2", "g3:conv:src|ch|M|dk|mode:page:sigma:rel",
        {"CS": len(js), "CE": len(js)}))
    best = {}; gates = []; t0 = time.time(); n = 0
    for conv in ("CS", "CE"):
        for j in js:
            p = j["page"]; u0, lens, ue = L.unit(REAL, p, conv); Cf = U[u0:u0 + L.NKEY]
            _, a = decode_unit(j, Cf, lens, 120); kid = "g3:%s:%s:p%d:sg%d:%s" % (conv, RG.cname(j["c"]), p, j["sigma"], j["rel"])
            pm = rows.add(a, kid, "G3-" + conv, j["rel"], RG.cname(j["c"])); n += 1
            k = (conv, j["rel"])
            if pm > best.get(k, (-9,))[0]: best[k] = (round(pm, 3), kid, lib.REGS[a["preg"]])
            bar = lib.bv3(COMB_N[j["rel"]], 120, j["rel"])
            if pm >= bar:
                Lg = min(240, ue - u0); _, a2 = decode_unit(j, Cf, lens, Lg)
                g = {"kid": kid, "pmax120": round(pm, 3), "pmax_gate": round(float(a2["pmax"]), 3), "L_gate": Lg, "bar_gate": round(lib.bv3(COMB_N[j["rel"]], Lg, j["rel"]), 3)}
                g["FLAGGED_FOR_ORACLE"] = g["pmax_gate"] >= g["bar_gate"]; gates.append(g)
    rows.close()
    AD = lib.AD
    try: AD.validate_store(F("g3_sweep_rows.jsonl")); vs = "ok"
    except Exception as ex: vs = "FAIL %s" % ex
    sys.path.insert(0, os.path.join(L.LP, "analysis", "handoff")); import validate_ledger as VL
    out = {"n_decodes": n, "N_orig": ORIG_N, "N_new": NEW_N, "N_combined": COMB_N,
           "best": {"%s|%s" % k: {"pmax120": v[0], "kid": v[1], "preg": v[2]} for k, v in best.items()},
           "bar120_combinedN": {r: round(lib.bv3(COMB_N[r], 120, r), 3) for r in COMB_N},
           "bar120_origN": {r: round(lib.bv3(ORIG_N[r], 120, r), 3) for r in ORIG_N},
           "gate_runs": gates, "flagged_for_oracle": [g for g in gates if g["FLAGGED_FOR_ORACLE"]],
           "validate_store": vs, "check_r3_store": VL.check_r3_store(F("g3_sweep_rows.jsonl")), "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(F("g3_real.json"), "w"), indent=1); print(json.dumps({k: v for k, v in out.items()}, indent=0)[:3000])


def plant_one(cell, Ptrue_unit, tl, dl, rng):
    sigma = rng.choice((-1, 1)); rel = lib.RELS[rng.randrange(2)] if cell[4] == "A3" else "direct"; seed = rng.randrange(1, 10 ** 9)
    if cell[4] == "A3": Cc, _ = RG.g3_enc_a3(Ptrue_unit, tl, cell, sigma, rel, seed)
    else: Cc = RG.g3_enc_direct(Ptrue_unit, tl, cell, sigma)
    Cc = Cc[:240]
    j = {"c": cell, "page": 0, "sigma": sigma, "rel": rel}
    p1, a1 = decode_unit(j, Cc, dl, 120); p2, a2 = decode_unit(j, Cc, dl, 240)
    e = {"rel": rel, "sigma": sigma}
    e.update(lib.judge(float(a1["pmax"]), float(a2["pmax"]), lib.rec_of(p2, Ptrue_unit[:len(p2)]), rel)); return e


def plants():
    rows = []; t0 = time.time()
    for regime in ("a", "b", "bp"):
        for page in (0,) + MID:
            for conv in (("C0",) if page == 0 else L.CONVS):
                for rep in (0, 1):
                    rng = L.plant_rng("g3", regime, page, conv, rep); P = L.G.make_plant(regime, rng)
                    tw, pw = L.plant_words_true(P), L.plant_words_printed(P)
                    dec_convs = [conv] + ([c for c in L.CONVS if c != conv] if (regime == "a" and page != 0 and rep == 0) else [])
                    for dconv in dec_convs:
                        u0, tl, _ = L.unit(tw, page, conv); d0, dl, _ = L.unit(pw, page, dconv)
                        if dconv == conv and regime != "bp": assert (u0, tl[:40]) == (d0, dl[:40])
                        Pu = P.flat[u0:u0 + 240]
                        for cell in CELLS:
                            if dconv != conv:
                                # mismatch: ciphertext enciphered from u0 under conv; decoder reads from its own unit start d0
                                sigma = rng.choice((-1, 1)); rel = lib.RELS[rng.randrange(2)] if cell[4] == "A3" else "direct"; seed = rng.randrange(1, 10 ** 9)
                                lo = min(u0, d0); full = P.flat[lo:lo + 300]
                                # encipher the stream from lo: runes before u0 (CE vs CS only) are left as plaintext-shifted 0 (unknown to decoder)
                                if cell[4] == "A3": Cu, _ = RG.g3_enc_a3(P.flat[u0:u0 + 300], tl, cell, sigma, rel, seed)
                                else: Cu = RG.g3_enc_direct(P.flat[u0:u0 + 300], tl, cell, sigma)
                                Cs = P.flat[lo:u0] + Cu        # pre-unit runes: page p-1's schedule unknown; plaintext stands in
                                Cd = Cs[d0 - lo:d0 - lo + 240]; Pd = P.flat[d0:d0 + 240]
                                j = {"c": cell, "page": 0, "sigma": sigma, "rel": rel}
                                p1, a1 = decode_unit(j, Cd, dl, 120); p2, a2 = decode_unit(j, Cd, dl, 240)
                                e = {"rel": rel, "sigma": sigma}; e.update(lib.judge(float(a1["pmax"]), float(a2["pmax"]), lib.rec_of(p2, Pd[:len(p2)]), rel))
                            else:
                                e = plant_one(cell, Pu, tl, dl, rng)
                            e.update({"regime": regime, "page": page, "conv": conv, "dconv": dconv, "rep": rep, "cell": RG.cname(cell),
                                      "src": cell[0], "mode": cell[4], "arm": "matched" if dconv == conv else "mismatch"})
                            rows.append(e)
                    L.heartbeat("g3", "plants %s p%d %s rep%d %.0fs n=%d" % (regime, page, conv, rep, time.time() - t0, len(rows)))
    M = [r for r in rows if r["arm"] == "matched"]
    for r in M: r["pagecls"] = "p0" if r["page"] == 0 else "mid"
    out = {"rule": "R38 lib.judge(): pmax120>=bar_v3(1e6,120) & pmax240>=bar_v3(1e6,240) & rec240>=0.90",
           "summary_regime_conv": L.summarize([r for r in M if r["page"] != 0], ("regime", "conv")),
           "summary_regime_p0": L.summarize([r for r in M if r["page"] == 0], ("regime",)),
           "summary_regime_all": L.summarize(M, ("regime",)),
           "summary_regime_mode": L.summarize(M, ("regime", "src", "mode")),
           "summary_regime_conv_page": L.summarize([r for r in M if r["page"] != 0], ("regime", "conv", "page")),
           "summary_cell_a": L.summarize([r for r in M if r["regime"] == "a"], ("cell",)),
           "mismatch_a": L.summarize([r for r in rows if r["arm"] == "mismatch"], ("conv", "dconv")),
           "rows": rows, "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(F("g3_plants.json"), "w"), indent=1)
    for k in ("summary_regime_p0", "summary_regime_conv", "mismatch_a"):
        print(k, json.dumps(out[k]))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "faith": sys.exit(0 if faith() else 3)
    {"real": real, "plants": plants}[cmd]()
