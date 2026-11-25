"""R47-L2 arm LEX: the lexicon -> key glue of R38-C1 (WORDNET A-*, FREQRANK B-*) and R39-C1 (SENSE D/L-*) through
the rows' OWN enciphers.enc / sweep.dec_shift / sweep.dec_a3 / judge(), on LP2's real layout via words.py.
  python -I arm_lex.py r38|r39 faith    C0 re-run of the full original job list; must reproduce recorded bests
  python -I arm_lex.py r38|r39 real     CS + CE on pages 1,2 (SWEEPROW store, combined-N bars, gate)
  python -I arm_lex.py r38|r39 plants   matched arm a/b/bp x pages 0,1,2 x C0/CS/CE x 2 reps + mismatch arm (a)
One row per process (the two lanes' modules share file names).  Writes only in this folder."""
import os, sys, json, time, math, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import l2lib as L
ROW = sys.argv[1]
LANE = {"r38": ("round38", "C1-semantic-road"), "r39": ("round39", "C1-sense-similarity")}[ROW]
LDIR = os.path.join(L.LP, "analysis", *LANE)
sys.path.insert(0, LDIR)
SW = L.G._load("%s_sweep" % ROW, os.path.join(LDIR, "sweep.py"))
S, EN, AD, PAN, bar_v3 = SW.S, SW.EN, SW.AD, SW.PAN, SW.bar_v3
REL = SW.REL
F = lambda n: os.path.join(HERE, n)
REAL = L.real_words()
CTRL = json.load(open(os.path.join(LDIR, "control.json")))
CELLS = [k for k, ok in CTRL["valid"].items() if ok]
ORIG = {"r38": {"shift": 2088, "A3": 26136}, "r39": {"shift": 1044, "A3": 13068}}[ROW]
NEW = {k: v * 4 // 3 for k, v in ORIG.items()}          # pages 1,2 (2/3 of the family) x 2 conventions
COMB = {k: ORIG[k] + NEW[k] for k in ORIG}
RECORDED = {"r38": {"shift": 4.62, "A3": 5.296}, "r39": {"shift": 4.004, "A3": 5.351}}[ROW]
ROWNAME = {"A": "R38-C1-SEMANTIC-WORDNET", "B": "R38-C1-SEMANTIC-FREQRANK", "D": "R39-C1-SENSE-SIMILARITY", "L": "R39-C1-SENSE-SIMILARITY"}
U = S.U


def grp(mode): return "A3" if mode == "A3" else "shift"


def decode(var, mode, s, sigma, C, lens):
    saved = S.LENS[0]; S.LENS[0] = lens
    try:
        if mode == "A3": return SW.dec_a3(0, len(C), var, s, sigma, C=C)
        return SW.dec_shift(0, len(C), var, s, sigma, mode, C=C)
    finally:
        S.LENS[0] = saved


def jobs(pages):
    out = []
    for k in CELLS:
        var, mode = k.split("|")
        for p in pages:
            for sg in (-1, 1):
                for s in (range(29) if mode != "A3" else range(726)):
                    out.append((var, mode, p, s, sg))
    return out


def faith():
    eq = {p: L.unit(REAL, p, "C0")[1] == S.LENS[p] and L.unit(REAL, p, "C0")[0] == S.page_start(p) for p in (0, 1, 2)}
    best = {}; t0 = time.time(); js = jobs((0, 1, 2))
    for var, mode, p, s, sg in js:
        _, a = decode(var, mode, s, sg, S.Cpage(p, 120), S.LENS[p]); g = grp(mode)
        best[g] = max(best.get(g, -9), float(a["pmax"]))
    best = {k: round(v, 3) for k, v in best.items()}
    ok = all(eq.values()) and all(abs(best[k] - RECORDED[k]) < 0.0015 for k in RECORDED) and len(js) == sum(ORIG.values())
    out = {"c0_lens_equal_LENS": eq, "n": len(js), "best": best, "recorded": RECORDED, "reproduced": ok, "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(F("%s_faith.json" % ROW), "w"), indent=1); print(json.dumps(out)); return ok


def real():
    js = jobs((1, 2)); store = F("%s_sweep_rows.jsonl" % ROW)
    hdr = AD.header("round47/L2/%s" % ROW, pan=PAN, key_space="%s original job list (vars x A1/A2/A3 x s x sigma) on pages 1,2 under fragment conventions CS and CE (words.py)" % ROW,
                    decoder="as the row: A1/A2 beam-free direct judged vs keyskip1 bar; A3 beam_v3 keyskip1", register_panel="panel-R36 data/panels/panel-r36.npz",
                    panel_sha256=SW.PANEL_SHA, v3_version="round33/I1 beam_v3.py via set_panel", bars="round34/I1 bars_v3", kid_format="%s:conv:var:mode:page:s:sigma" % ROW,
                    n_planned={"CS": len(js), "CE": len(js)})
    f = open(store, "w"); f.write(json.dumps(hdr) + "\n")
    best = {}; gates = []; t0 = time.time(); n = 0
    units = {(p, c): L.unit(REAL, p, c) for p in (1, 2) for c in ("CS", "CE")}
    for conv in ("CS", "CE"):
        for var, mode, p, s, sg in js:
            u0, lens, ue = units[(p, conv)]
            _, a = decode(var, mode, s, sg, U[u0:u0 + 120], lens); pm = float(a["pmax"]); n += 1
            kid = "%s:%s:%s:%s:p%d:s%d:sg%d" % (ROW, conv, var, mode, p, s, sg); f.write(json.dumps(AD.to_row(a, kid)) + "\n")
            g = grp(mode); k = (conv, g, var[0])
            if pm > best.get(k, (-9,))[0]: best[k] = (round(pm, 3), kid, PAN.registers[a["preg"]])
            if pm >= bar_v3(COMB[g], 120, REL):
                Lg = min(240, ue - u0); _, a2 = decode(var, mode, s, sg, U[u0:u0 + Lg], lens)
                e = {"kid": kid, "pmax120": round(pm, 3), "pmax_gate": round(float(a2["pmax"]), 3), "L_gate": Lg, "bar_gate": round(bar_v3(COMB[g], Lg, REL), 3)}
                e["FLAGGED_FOR_ORACLE"] = e["pmax_gate"] >= e["bar_gate"]; gates.append(e)
            if n % 5000 == 0:
                f.flush(); L.heartbeat(ROW + "_real", "%d/%d %.0fs" % (n, 2 * len(js), time.time() - t0))
    f.close()
    try: AD.validate_store(store); vs = "ok"
    except Exception as ex: vs = "FAIL %s" % ex
    sys.path.insert(0, os.path.join(L.LP, "analysis", "handoff")); import validate_ledger as VL
    out = {"n_decodes": n, "N_orig": ORIG, "N_new": NEW, "N_combined": COMB,
           "best": {"%s|%s|%s" % k: {"pmax120": v[0], "kid": v[1], "preg": v[2], "row": ROWNAME[k[2]]} for k, v in sorted(best.items())},
           "bar120_combinedN": {g: round(bar_v3(COMB[g], 120, REL), 3) for g in COMB}, "bar120_origN": {g: round(bar_v3(ORIG[g], 120, REL), 3) for g in ORIG},
           "gate_runs": gates, "flagged_for_oracle": [g for g in gates if g["FLAGGED_FOR_ORACLE"]], "validate_store": vs,
           "check_r3_store": VL.check_r3_store(store), "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(F("%s_real.json" % ROW), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "best"}), json.dumps({k: v["pmax120"] for k, v in out["best"].items()}))


def plant_cell(cell, P, u0, tl, d0, dl, rng):
    var, mode = cell.split("|"); s = rng.randrange(29) if mode != "A3" else rng.randrange(726); sigma = rng.choice((-1, 1)); seed = rng.randrange(1, 10 ** 9)
    lo = min(u0, d0)
    Cu = EN.enc(P.flat[u0:u0 + 300], tl, var, s, sigma, mode, REL if mode == "A3" else None, seed)
    Cs = P.flat[lo:u0] + Cu                     # mismatch only: pre-unit runes (page p-1 schedule) stand in as plaintext
    Cd = Cs[d0 - lo:d0 - lo + 240]; Pd = P.flat[d0:d0 + 240]
    p1, a1 = decode(var, mode, s, sigma, Cd[:120], dl); p2, a2 = decode(var, mode, s, sigma, Cd, dl)
    e = {"cell": cell, "var": var, "mode": mode, "row": ROWNAME[var[0]], "s": s, "sigma": sigma}
    e.update(S.judge(float(a1["pmax"]), float(a2["pmax"]), S.rec_of(p2, Pd[:len(p2)]), REL)); return e


def plants():
    rows = []; t0 = time.time()
    for regime in ("a", "b", "bp"):
        for page in (0, 1, 2):
            for conv in (("C0",) if page == 0 else L.CONVS):
                for rep in (0, 1):
                    rng = L.plant_rng(ROW, regime, page, conv, rep); P = L.G.make_plant(regime, rng)
                    tw, pw = L.plant_words_true(P), L.plant_words_printed(P)
                    dcs = [conv] + ([c for c in L.CONVS if c != conv] if (regime == "a" and page != 0 and rep == 0) else [])
                    for dconv in dcs:
                        u0, tl, _ = L.unit(tw, page, conv); d0, dl, _ = L.unit(pw, page, dconv)
                        if dconv == conv and regime != "bp": assert (u0, tl[:40]) == (d0, dl[:40])
                        for cell in CELLS:
                            e = plant_cell(cell, P, u0, tl, d0, dl, rng)
                            e.update({"regime": regime, "page": page, "conv": conv, "dconv": dconv, "rep": rep, "arm": "matched" if dconv == conv else "mismatch"})
                            rows.append(e)
                    L.heartbeat(ROW + "_plants", "%s p%d %s rep%d %.0fs n=%d" % (regime, page, conv, rep, time.time() - t0, len(rows)))
    M = [r for r in rows if r["arm"] == "matched"]
    out = {"rule": "row's judge(): pmax120>=bar_v3(1e6,120,ks1) & pmax240>=bar_v3(1e6,240,ks1) & rec240>=0.90",
           "summary_row_regime_p0": L.summarize([r for r in M if r["page"] == 0], ("row", "regime")),
           "summary_row_regime_conv": L.summarize([r for r in M if r["page"] != 0], ("row", "regime", "conv")),
           "summary_row_regime_all": L.summarize(M, ("row", "regime")),
           "summary_row_regime_mode": L.summarize(M, ("row", "regime", "mode")),
           "summary_cell_a": L.summarize([r for r in M if r["regime"] == "a"], ("cell",)),
           "mismatch_a": L.summarize([r for r in rows if r["arm"] == "mismatch"], ("row", "conv", "dconv")),
           "rows": rows, "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(F("%s_plants.json" % ROW), "w"), indent=1)
    for k in ("summary_row_regime_p0", "summary_row_regime_conv", "mismatch_a"): print(k, json.dumps(out[k]))


if __name__ == "__main__":
    cmd = sys.argv[2]
    if cmd == "faith": sys.exit(0 if faith() else 3)
    {"real": real, "plants": plants}[cmd]()
